import assert from "node:assert/strict";
import test from "node:test";
import { ClaudeAskError } from "../src/claude-ask.js";
import { createClaudeSessionAdapter } from "../src/claude-session.js";

const OPUS_SESSION = "11111111-1111-4111-8111-111111111111";
const FABLE_SESSION = "22222222-2222-4222-8222-222222222222";
const THIRD_SESSION = "33333333-3333-4333-8333-333333333333";

function deferred() {
  let reject;
  let resolve;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    reject = rejectPromise;
    resolve = resolvePromise;
  });
  return { promise, reject, resolve };
}

function profileFor(name, effort = "xhigh") {
  if (name === "fable_advisor") {
    return {
      effort,
      model: "claude-fable-5",
      requestedModel: "fable"
    };
  }
  return {
    effort,
    model: "claude-opus-5",
    requestedModel: "opus"
  };
}

function launchFor(request) {
  return {
    cwd: request.cwd,
    env: {},
    executable: "/fake/claude",
    profile: request.session_id ? null : profileFor(request.profile, request.effort),
    prompt: request.prompt,
    sessionId: request.session_id || null,
    stripped: []
  };
}

class FakeEngine {
  constructor(launch, callbacks, sessionId) {
    this.actions = [];
    this.callbacks = callbacks;
    this.interruptCompletes = false;
    this.interruptReceipt = { still_queued: [] };
    this.launch = launch;
    this.model = launch.profile?.model || "claude-opus-5";
    this.sessionId = sessionId;
    this.stopReasons = [];
    this.turns = [];
    this.init = {
      type: "system",
      subtype: "init",
      apiKeySource: "none",
      model: this.model,
      session_id: sessionId
    };
    this.completion = Promise.resolve({ error: null, init: this.init, lastRaw: null });
    this.ready = Promise.resolve().then(() => {
      this.emit(this.init);
      return { control: null, init: this.init };
    });
  }

  emit(message) {
    this.callbacks.onMessage?.(message);
  }

  send(prompt, { priority = "now" } = {}) {
    const turn = deferred();
    const entry = { ...turn, priority, prompt, settled: false };
    this.turns.push(entry);
    this.actions.push(`send:${prompt}`);
    return {
      completion: turn.promise,
      uuid: `fake-turn-${this.turns.length}`
    };
  }

  rawResult(text, overrides = {}) {
    return {
      init: this.init,
      iteratorError: null,
      primaryModels: [this.model],
      result: {
        type: "result",
        subtype: "success",
        is_error: false,
        result: text,
        session_id: this.sessionId,
        duration_ms: 25,
        num_turns: 1,
        modelUsage: { [this.model]: {} },
        ...overrides
      },
      usageModels: [this.model]
    };
  }

  finish(text = "DONE", overrides = {}) {
    const entry = this.turns.findLast((turn) => !turn.settled);
    assert.ok(entry, "Expected an unsettled fake turn.");
    entry.settled = true;
    entry.resolve(this.rawResult(text, overrides));
  }

  async interrupt() {
    this.actions.push("interrupt");
    if (this.interruptCompletes) this.finish("INTERRUPTED");
    return this.interruptReceipt;
  }

  async stop(reason) {
    this.actions.push("stop");
    this.stopReasons.push(reason);
    for (const turn of this.turns.filter((entry) => !entry.settled)) {
      turn.settled = true;
      turn.resolve(this.rawResult("STOPPED"));
    }
    return this.completion;
  }

  end(error = null, lastRaw = null) {
    this.callbacks.onTerminal?.({ error, lastRaw });
  }
}

function createHarness({
  maxSessions = 4,
  sessionIds = [OPUS_SESSION, FABLE_SESSION, THIRD_SESSION],
  steerSettleMs = 25
} = {}) {
  const engines = [];
  const prepared = [];
  let freshIndex = 0;
  const adapter = createClaudeSessionAdapter({
    maxSessions,
    prepareRequest: async (request) => {
      prepared.push(request);
      return launchFor(request);
    },
    startSession: (launch, callbacks) => {
      const sessionId = launch.sessionId || sessionIds[freshIndex++];
      const engine = new FakeEngine(launch, callbacks, sessionId);
      engines.push(engine);
      return engine;
    },
    steerSettleMs
  });
  return { adapter, engines, prepared };
}

async function expectAdapterError(promise, code, messagePattern) {
  try {
    await promise;
    assert.fail(`Expected ClaudeAskError(${code})`);
  } catch (error) {
    assert.ok(error instanceof ClaudeAskError, error?.stack || String(error));
    assert.equal(error.code, code);
    if (messagePattern) assert.match(error.message, messagePattern);
    return error;
  }
}

async function waitForState(adapter, sessionId, expected) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    const snapshot = await adapter.observe({ session_id: sessionId });
    if (snapshot.state === expected) return snapshot;
    await new Promise((resolve) => setImmediate(resolve));
  }
  const snapshot = await adapter.observe({ session_id: sessionId });
  assert.equal(snapshot.state, expected);
  return snapshot;
}

test("session operation schema stays strict while remaining MCP-visible", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());

  await expectAdapterError(
    adapter.command({
      op: "open_fresh",
      cwd: "/workspace",
      prompt: "Missing profile."
    }),
    "invalid_request",
    /profile/u
  );
  await expectAdapterError(
    adapter.command({
      op: "stop",
      prompt: "Not accepted for stop.",
      session_id: OPUS_SESSION
    }),
    "invalid_request",
    /prompt/u
  );
  assert.equal(engines.length, 0);
});

test("open_fresh returns the native UUID while its first turn is still running", async (t) => {
  const { adapter, engines, prepared } = createHarness();
  t.after(() => adapter.shutdown());

  const opened = await adapter.command({
    op: "open_fresh",
    prompt: "PRIVATE_INITIAL_TASK",
    profile: "opus_advisor",
    effort: "max",
    cwd: "/workspace"
  });

  assert.equal(opened.accepted_op, "open_fresh");
  assert.equal(opened.session_id, OPUS_SESSION);
  assert.equal(opened.state, "thinking");
  assert.equal(opened.requested_model, "opus");
  assert.equal(opened.requested_effort, "max");
  assert.equal(opened.resolved_model, "claude-opus-5");
  assert.deepEqual(prepared, [{
    cwd: "/workspace",
    prompt: "PRIVATE_INITIAL_TASK",
    profile: "opus_advisor",
    effort: "max"
  }]);
  assert.deepEqual(engines[0].actions, ["send:PRIVATE_INITIAL_TASK"]);
  assert.equal(engines[0].turns[0].settled, false);

  const summary = await adapter.observe({ session_id: OPUS_SESSION });
  assert.deepEqual(summary.events, []);
  assert.deepEqual(summary.messages, []);
  assert.ok(JSON.stringify(summary).length < 2_000);
  assert.doesNotMatch(JSON.stringify(summary), /PRIVATE_INITIAL_TASK/u);
});

test("SDK credential contradiction stops an already-reserved opening turn", async () => {
  const ready = deferred();
  const actions = [];
  const adapter = createClaudeSessionAdapter({
    prepareRequest: async (request) => launchFor(request),
    startSession: () => ({
      ready: ready.promise,
      completion: Promise.resolve({ error: null, init: null, lastRaw: null }),
      send(prompt) {
        actions.push(`send:${prompt}`);
        return { completion: new Promise(() => {}), uuid: "must-not-send" };
      },
      async stop() {}
    })
  });
  const pending = adapter.command({
    op: "open_fresh",
    prompt: "MUST_NOT_LEAVE",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["send:MUST_NOT_LEAVE"]);
  ready.resolve({
    control: {},
    init: {
      type: "system",
      subtype: "init",
      apiKeySource: "user",
      model: "claude-opus-5",
      session_id: OPUS_SESSION
    }
  });
  await expectAdapterError(pending, "sdk_subscription_required");
  assert.deepEqual(actions, ["send:MUST_NOT_LEAVE"]);
  await adapter.shutdown();
});

test("explicit observations are bounded and omit thinking and raw tool I/O", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  await adapter.command({
    op: "open_fresh",
    prompt: "Review the evidence.",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  const engine = engines[0];

  engine.emit({
    type: "system",
    subtype: "thinking_tokens",
    estimated_tokens: 1234,
    thinking: "HIDDEN_THINKING_BODY"
  });
  for (const toolName of ["Read", "Search", "Inspect"]) {
    engine.emit({
      type: "tool_progress",
      tool_name: toolName,
      input: { secret: "RAW_TOOL_INPUT" },
      output: "RAW_TOOL_OUTPUT"
    });
  }
  engine.emit({
    type: "assistant",
    parent_tool_use_id: null,
    message: {
      model: "claude-opus-5",
      content: [
        { type: "thinking", thinking: "HIDDEN_ASSISTANT_THINKING" },
        {
          type: "tool_use",
          name: "Bash",
          input: { secret: "RAW_ASSISTANT_TOOL_INPUT" }
        }
      ]
    }
  });
  engine.emit({
    type: "rate_limit_event",
    rate_limit_info: { status: "allowed_warning", isUsingOverage: true }
  });
  engine.emit({
    type: "system",
    subtype: "permission_denied",
    tool_name: "Write",
    message: "RAW_PERMISSION_REASON"
  });
  engine.finish(`ANSWER:${"A".repeat(5_000)}`);
  await waitForState(adapter, OPUS_SESSION, "idle");

  const activity = await adapter.observe({
    session_id: OPUS_SESSION,
    detail: "activity",
    limit: 2
  });
  assert.equal(activity.events.length, 2);
  assert.ok(activity.events.every((event) => event.summary.length <= 220));
  assert.ok(activity.events.some((event) => event.type === "permission" && /Write/u.test(event.summary)));
  assert.match(activity.warnings.join(" "), /subscription_overage_in_use/u);
  assert.match(activity.warnings.join(" "), /permission_denied:Write/u);

  const conversation = await adapter.observe({
    session_id: OPUS_SESSION,
    detail: "conversation",
    limit: 1,
    max_chars: 200
  });
  assert.equal(conversation.messages.length, 1);
  assert.equal(conversation.messages[0].role, "assistant");
  assert.ok(conversation.messages[0].text.length <= 200);

  const exposed = JSON.stringify({ activity, conversation });
  for (const secret of [
    "HIDDEN_THINKING_BODY",
    "HIDDEN_ASSISTANT_THINKING",
    "RAW_TOOL_INPUT",
    "RAW_TOOL_OUTPUT",
    "RAW_ASSISTANT_TOOL_INPUT",
    "RAW_PERMISSION_REASON"
  ]) {
    assert.doesNotMatch(exposed, new RegExp(secret, "u"));
  }
});

test("authoritative task levels and requires_action stay internally consistent", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  await adapter.command({
    op: "open_fresh",
    prompt: "Inspect.",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  engines[0].emit({
    type: "system",
    subtype: "background_tasks_changed",
    tasks: [{ task_id: "task-1", task_type: "agent", description: "Inspecting" }]
  });
  let summary = await adapter.observe({ session_id: OPUS_SESSION });
  assert.equal(summary.state, "subagent");
  assert.equal(summary.background_tasks, 1);

  engines[0].emit({
    type: "system",
    subtype: "background_tasks_changed",
    tasks: []
  });
  summary = await adapter.observe({ session_id: OPUS_SESSION });
  assert.equal(summary.state, "thinking");
  assert.equal(summary.background_tasks, 0);
  assert.doesNotMatch(summary.direction, /background task/u);

  engines[0].emit({
    type: "system",
    subtype: "session_state_changed",
    state: "requires_action"
  });
  summary = await adapter.observe({ session_id: OPUS_SESSION });
  assert.equal(summary.state, "requires_action");
  assert.match(summary.direction, /requires/u);
});

test("parallel sessions remain isolated and enforce live-session capacity", async (t) => {
  const { adapter, engines } = createHarness({ maxSessions: 2 });
  t.after(() => adapter.shutdown());

  const [left, right] = await Promise.all([
    adapter.command({
      op: "open_fresh",
      prompt: "LEFT_TASK",
      profile: "opus_advisor",
      cwd: "/left"
    }),
    adapter.command({
      op: "open_fresh",
      prompt: "RIGHT_TASK",
      profile: "fable_advisor",
      cwd: "/right"
    })
  ]);
  assert.deepEqual([left.session_id, right.session_id], [OPUS_SESSION, FABLE_SESSION]);
  assert.deepEqual(engines.map((engine) => engine.actions[0]), ["send:LEFT_TASK", "send:RIGHT_TASK"]);

  await expectAdapterError(
    adapter.command({
      op: "open_fresh",
      prompt: "THIRD_TASK",
      profile: "opus_advisor",
      cwd: "/third"
    }),
    "session_capacity"
  );

  engines[0].finish("LEFT_DONE");
  await waitForState(adapter, OPUS_SESSION, "idle");
  const rightSummary = await adapter.observe({ session_id: FABLE_SESSION });
  assert.equal(rightSummary.state, "thinking");
  const [leftConversation, rightConversation] = await Promise.all([
    adapter.observe({ session_id: OPUS_SESSION, detail: "conversation" }),
    adapter.observe({ session_id: FABLE_SESSION, detail: "conversation" })
  ]);
  assert.match(JSON.stringify(leftConversation.messages), /LEFT_TASK/u);
  assert.doesNotMatch(JSON.stringify(leftConversation.messages), /RIGHT_TASK/u);
  assert.match(JSON.stringify(rightConversation.messages), /RIGHT_TASK/u);
  assert.doesNotMatch(JSON.stringify(rightConversation.messages), /LEFT_TASK/u);
});

test("concurrent open_resume reserves one native session before async preflight", async () => {
  const gate = deferred();
  let prepares = 0;
  const adapter = createClaudeSessionAdapter({
    prepareRequest: async (request) => {
      prepares += 1;
      await gate.promise;
      return launchFor(request);
    },
    startSession: (launch, callbacks) => new FakeEngine(launch, callbacks, launch.sessionId)
  });
  const first = adapter.command({
    op: "open_resume",
    prompt: "FIRST",
    cwd: "/workspace",
    session_id: OPUS_SESSION
  });
  await new Promise((resolve) => setImmediate(resolve));
  await expectAdapterError(
    adapter.command({
      op: "open_resume",
      prompt: "SECOND",
      cwd: "/workspace",
      session_id: OPUS_SESSION
    }),
    "session_already_active"
  );
  assert.equal(prepares, 1);
  gate.resolve();
  await first;
  await adapter.shutdown();
});

test("cancelling an open during preflight never starts a native process", async () => {
  const gate = deferred();
  const controller = new AbortController();
  let starts = 0;
  const adapter = createClaudeSessionAdapter({
    prepareRequest: async (request) => {
      await gate.promise;
      return launchFor(request);
    },
    startSession() {
      starts += 1;
      assert.fail("Cancelled preflight must not start Claude.");
    }
  });
  const pending = adapter.command({
    op: "open_fresh",
    prompt: "MUST_NOT_START",
    profile: "opus_advisor",
    cwd: "/workspace"
  }, controller.signal);
  await new Promise((resolve) => setImmediate(resolve));
  controller.abort();
  gate.resolve();

  await expectAdapterError(pending, "cancelled");
  assert.equal(starts, 0);
  await adapter.shutdown();
});

test("reopening a retained session still obeys live engine capacity", async () => {
  const { adapter, engines } = createHarness({ maxSessions: 1 });
  await adapter.command({
    op: "open_fresh",
    prompt: "FIRST",
    profile: "opus_advisor",
    cwd: "/first"
  });
  engines[0].finish("DONE");
  await waitForState(adapter, OPUS_SESSION, "idle");
  engines[0].end();

  await adapter.command({
    op: "open_fresh",
    prompt: "SECOND",
    profile: "opus_advisor",
    cwd: "/second"
  });
  await expectAdapterError(
    adapter.command({
      op: "send",
      prompt: "REOPEN_FIRST",
      session_id: OPUS_SESSION
    }),
    "session_capacity"
  );
  await adapter.shutdown();
});

test("failed reopen cleanup counts once toward live engine capacity", async () => {
  const cleanup = deferred();
  const keepAlive = setTimeout(() => {}, 1_000);
  const engines = [];
  let starts = 0;
  const adapter = createClaudeSessionAdapter({
    closeTimeoutMs: 5,
    maxSessions: 2,
    prepareRequest: async (request) => launchFor(request),
    startSession: (launch, callbacks) => {
      starts += 1;
      if (starts === 2) {
        const initError = new Error("Synthetic reopen init failure.");
        const engine = {
          ready: Promise.reject(initError),
          completion: cleanup.promise,
          send() {
            return { completion: new Promise(() => {}), uuid: "failed-reopen-turn" };
          },
          stop() {
            return cleanup.promise;
          }
        };
        engines.push(engine);
        return engine;
      }
      const sessionId = launch.sessionId || (starts === 1 ? OPUS_SESSION : FABLE_SESSION);
      const engine = new FakeEngine(launch, callbacks, sessionId);
      engines.push(engine);
      return engine;
    }
  });

  await adapter.command({
    op: "open_fresh",
    prompt: "FIRST",
    profile: "opus_advisor",
    cwd: "/first"
  });
  engines[0].finish("DONE");
  await waitForState(adapter, OPUS_SESSION, "idle");
  engines[0].end();

  await expectAdapterError(
    adapter.command({
      op: "send",
      prompt: "FAIL_REOPEN",
      session_id: OPUS_SESSION
    }),
    "claude_sdk_error"
  );
  assert.equal(adapter.inspect(OPUS_SESSION).closing, true);

  const second = await adapter.command({
    op: "open_fresh",
    prompt: "SECOND",
    profile: "fable_advisor",
    cwd: "/second"
  });
  assert.equal(second.session_id, FABLE_SESSION);
  assert.equal(second.state, "thinking");
  assert.equal(starts, 3);

  cleanup.resolve({ error: null, init: null, lastRaw: null });
  await new Promise((resolve) => setImmediate(resolve));
  clearTimeout(keepAlive);
  await adapter.shutdown();
});

test("send after idle reuses the same native engine", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  await adapter.command({
    op: "open_fresh",
    prompt: "FIRST_TASK",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  engines[0].finish("FIRST_ANSWER");
  const beforeFollowup = await waitForState(adapter, OPUS_SESSION, "idle");

  const sent = await adapter.command({
    op: "send",
    prompt: "SECOND_TASK",
    session_id: OPUS_SESSION
  });
  assert.equal(sent.state, "thinking");
  assert.equal(engines.length, 1);
  assert.deepEqual(engines[0].actions, ["send:FIRST_TASK", "send:SECOND_TASK"]);
  const immediateDelta = await adapter.observe({
    session_id: OPUS_SESSION,
    detail: "conversation",
    cursor: beforeFollowup.cursor
  });
  assert.deepEqual(
    immediateDelta.messages.map(({ role, text }) => ({ role, text })),
    [{ role: "user", text: "SECOND_TASK" }]
  );

  engines[0].finish("SECOND_ANSWER");
  await waitForState(adapter, OPUS_SESSION, "idle");
  const conversation = await adapter.observe({
    session_id: OPUS_SESSION,
    detail: "conversation",
    limit: 4,
    max_chars: 4_000
  });
  assert.deepEqual(
    conversation.messages.map(({ role, text }) => ({ role, text })),
    [
      { role: "user", text: "FIRST_TASK" },
      { role: "assistant", text: "FIRST_ANSWER" },
      { role: "user", text: "SECOND_TASK" },
      { role: "assistant", text: "SECOND_ANSWER" }
    ]
  );
});

test("conversation character budget preserves the newest assistant answer", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  await adapter.command({
    op: "open_fresh",
    prompt: `OLD_PROMPT_${"X".repeat(1_000)}`,
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  engines[0].finish("NEWEST_ANSWER");
  await waitForState(adapter, OPUS_SESSION, "idle");
  const conversation = await adapter.observe({
    session_id: OPUS_SESSION,
    detail: "conversation",
    limit: 4,
    max_chars: 200
  });
  assert.equal(conversation.messages.at(-1).role, "assistant");
  assert.match(conversation.messages.at(-1).text, /NEWEST_ANSWER/u);
});

test("steer interrupts the active turn before sending its correction", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  await adapter.command({
    op: "open_fresh",
    prompt: "ORIGINAL_TASK",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  engines[0].interruptCompletes = true;

  const steered = await adapter.command({
    op: "steer",
    prompt: "CORRECTED_TASK",
    session_id: OPUS_SESSION
  });

  assert.equal(steered.accepted_op, "steer");
  assert.equal(steered.state, "thinking");
  assert.equal(engines.length, 1);
  assert.deepEqual(engines[0].actions, [
    "send:ORIGINAL_TASK",
    "interrupt",
    "send:CORRECTED_TASK"
  ]);
  assert.equal(engines[0].turns[1].settled, false);
});

test("stop closes one engine and shutdown closes every remaining engine", async () => {
  const { adapter, engines } = createHarness();
  await Promise.all([
    adapter.command({
      op: "open_fresh",
      prompt: "LEFT_TASK",
      profile: "opus_advisor",
      cwd: "/left"
    }),
    adapter.command({
      op: "open_fresh",
      prompt: "RIGHT_TASK",
      profile: "fable_advisor",
      cwd: "/right"
    })
  ]);

  const stopped = await adapter.command({
    op: "stop",
    session_id: OPUS_SESSION
  });
  assert.equal(stopped.state, "closed");
  assert.equal(engines[0].stopReasons.length, 1);
  assert.equal(engines[1].stopReasons.length, 0);

  await adapter.shutdown();
  assert.equal(engines[0].stopReasons.length, 1);
  assert.equal(engines[1].stopReasons.length, 1);
  assert.equal((await adapter.observe({ session_id: FABLE_SESSION })).state, "closed");
});

test("delayed cleanup remains closing and reserves capacity until completion", async () => {
  const cleanup = deferred();
  const keepAlive = setTimeout(() => {}, 1_000);
  let callbacks;
  const engine = {
    ready: Promise.resolve({
      control: {},
      init: {
        type: "system",
        subtype: "init",
        apiKeySource: "none",
        model: "claude-opus-5",
        session_id: OPUS_SESSION
      }
    }),
    completion: cleanup.promise,
    send() {
      return { completion: new Promise(() => {}), uuid: "turn-1" };
    },
    stop() {
      return cleanup.promise;
    }
  };
  const adapter = createClaudeSessionAdapter({
    closeTimeoutMs: 5,
    maxSessions: 1,
    prepareRequest: async (request) => launchFor(request),
    startSession: (_launch, handlers) => {
      callbacks = handlers;
      return engine;
    }
  });
  await adapter.command({
    op: "open_fresh",
    prompt: "WAIT",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  const stopped = await adapter.command({ op: "stop", session_id: OPUS_SESSION });
  assert.equal(stopped.state, "closing");
  await expectAdapterError(
    adapter.command({
      op: "open_fresh",
      prompt: "SECOND",
      profile: "opus_advisor",
      cwd: "/second"
    }),
    "session_capacity"
  );
  cleanup.resolve({ error: null, init: null, lastRaw: null });
  callbacks.onTerminal?.({ error: null, lastRaw: null });
  await waitForState(adapter, OPUS_SESSION, "closed");
  clearTimeout(keepAlive);
  await adapter.shutdown();
});

test("session turn timeout is typed while native cleanup retains capacity", async () => {
  const cleanup = deferred();
  let callbacks;
  const engine = {
    ready: Promise.resolve({
      control: {},
      init: {
        type: "system",
        subtype: "init",
        apiKeySource: "none",
        model: "claude-opus-5",
        session_id: OPUS_SESSION
      }
    }),
    completion: cleanup.promise,
    send() {
      return { completion: new Promise(() => {}), uuid: "turn-timeout" };
    },
    stop() {
      return cleanup.promise;
    }
  };
  const adapter = createClaudeSessionAdapter({
    closeTimeoutMs: 5,
    maxSessions: 1,
    turnTimeoutMs: 5,
    prepareRequest: async (request) => launchFor(request),
    startSession: (_launch, handlers) => {
      callbacks = handlers;
      return engine;
    }
  });
  await adapter.command({
    op: "open_fresh",
    prompt: "TIME_OUT",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  await new Promise((resolve) => setTimeout(resolve, 20));

  const closing = await adapter.observe({ session_id: OPUS_SESSION });
  assert.equal(closing.state, "closing");
  assert.deepEqual(closing.terminal, {
    kind: "timeout",
    code: "timeout",
    resumable: true
  });
  await expectAdapterError(
    adapter.command({
      op: "open_fresh",
      prompt: "SECOND",
      profile: "opus_advisor",
      cwd: "/second"
    }),
    "session_capacity"
  );

  cleanup.resolve({ error: null, init: null, lastRaw: null });
  callbacks.onTerminal?.({ error: null, lastRaw: null });
  await waitForState(adapter, OPUS_SESSION, "timed_out");
  await adapter.shutdown();
});

test("cancelled observation and steer do not leak a waiter or send a correction", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  const opened = await adapter.command({
    op: "open_fresh",
    prompt: "ORIGINAL",
    profile: "opus_advisor",
    cwd: "/workspace"
  });

  const observeController = new AbortController();
  const waiting = adapter.observe({
    session_id: OPUS_SESSION,
    cursor: opened.cursor,
    wait_ms: 20_000
  }, observeController.signal);
  observeController.abort();
  await expectAdapterError(waiting, "cancelled");
  assert.equal(adapter.inspect(OPUS_SESSION).waiters.size, 0);

  const steerController = new AbortController();
  const steering = adapter.command({
    op: "steer",
    prompt: "MUST_NOT_SEND",
    session_id: OPUS_SESSION
  }, steerController.signal);
  await new Promise((resolve) => setImmediate(resolve));
  steerController.abort();
  await expectAdapterError(steering, "cancelled");
  assert.deepEqual(engines[0].actions, ["send:ORIGINAL", "interrupt"]);
});

test("an already-cancelled send never reaches an idle engine", async (t) => {
  const { adapter, engines } = createHarness();
  t.after(() => adapter.shutdown());
  await adapter.command({
    op: "open_fresh",
    prompt: "FIRST",
    profile: "opus_advisor",
    cwd: "/workspace"
  });
  engines[0].finish("DONE");
  await waitForState(adapter, OPUS_SESSION, "idle");
  const controller = new AbortController();
  controller.abort();
  await expectAdapterError(
    adapter.command({
      op: "send",
      prompt: "MUST_NOT_SEND",
      session_id: OPUS_SESSION
    }, controller.signal),
    "cancelled"
  );
  assert.deepEqual(engines[0].actions, ["send:FIRST"]);
});

test("restart-like missing state is explicit and open_resume restores native history", async () => {
  const { adapter, engines } = createHarness();
  await expectAdapterError(
    adapter.command({
      op: "send",
      prompt: "Continue.",
      session_id: OPUS_SESSION
    }),
    "session_not_active",
    /open_resume/u
  );
  await expectAdapterError(
    adapter.observe({ session_id: OPUS_SESSION }),
    "session_not_active",
    /open_resume/u
  );
  assert.deepEqual(engines, []);
  const resumed = await adapter.command({
    op: "open_resume",
    prompt: "Continue after restart.",
    cwd: "/workspace",
    session_id: OPUS_SESSION
  });
  assert.equal(resumed.session_id, OPUS_SESSION);
  assert.equal(resumed.state, "thinking");
  assert.equal(engines[0].launch.sessionId, OPUS_SESSION);
  assert.deepEqual(engines[0].actions, ["send:Continue after restart."]);
  await adapter.shutdown();
});
