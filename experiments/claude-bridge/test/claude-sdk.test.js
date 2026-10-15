import assert from "node:assert/strict";
import test from "node:test";
import { AsyncMailbox, CLAUDE_SDK_VERSION, claudeRateLimit, claudeRuntimeWarning, startClaudeSdkSession } from "../src/claude-sdk.js";

const SESSION_ID = "11111111-1111-4111-8111-111111111111";

function launch() {
  return {
    cwd: "/workspace",
    env: {},
    executable: "/fake/claude",
    profile: {
      effort: "xhigh",
      model: "claude-opus-5",
      requestedModel: "opus"
    },
    sessionId: null
  };
}

test("streaming engine waits for a confirmed completion signal after result", async () => {
  const output = new AsyncMailbox();
  const capture = {};
  const engine = startClaudeSdkSession(launch(), {
    queryFactory: ({ prompt, options }) => {
      capture.input = prompt;
      capture.options = options;
      return {
        [Symbol.asyncIterator]() {
          return output;
        },
        async initializationResult() {
          return { models: [] };
        },
        async interrupt() {
          return { still_queued: [] };
        },
        close() {
          output.close();
        }
      };
    }
  });

  output.push({
    type: "system",
    subtype: "init",
    apiKeySource: "none",
    model: "claude-opus-5",
    session_id: SESSION_ID
  });
  await engine.ready;
  const turn = engine.send("Inspect.");
  const input = await capture.input.next();
  assert.equal(input.value.uuid, turn.uuid);
  assert.equal(capture.options.maxTurns, 48);

  output.push({
    type: "result",
    subtype: "success",
    is_error: false,
    result: "DONE",
    session_id: SESSION_ID,
    duration_ms: 10,
    num_turns: 1,
    modelUsage: { "claude-opus-5": {} }
  });
  let settled = false;
  void turn.completion.then(() => {
    settled = true;
  });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(settled, false, "result alone must not make a persistent session sendable");

  output.push({ type: "rate_limit_event", rate_limit_info: {
    status: "allowed_warning", rateLimitType: "five_hour", resetsAt: 1800000000
  } });
  output.push({
    type: "system",
    subtype: "session_state_changed",
    state: "idle",
    session_id: SESSION_ID
  });
  const raw = await turn.completion;
  assert.equal(raw.result.result, "DONE");
  assert.equal(raw.rateLimit.resets_at, 1800000000);
  assert.ok(raw.runtimeWarnings.includes("subscription_rate_limit_warning:five_hour"));

  const secondTurn = engine.send("Continue.");
  output.push({
    type: "result",
    subtype: "success",
    is_error: false,
    result: "SECOND_DONE",
    session_id: SESSION_ID,
    duration_ms: 5,
    num_turns: 1,
    modelUsage: { "claude-opus-5": {} }
  });
  output.push({
    type: "command_lifecycle",
    state: "completed",
    command_uuid: "different-command",
    session_id: SESSION_ID
  });
  let secondSettled = false;
  void secondTurn.completion.then(() => {
    secondSettled = true;
  });
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(secondSettled, false, "another command's lifecycle must not settle this turn");
  output.push({
    type: "command_lifecycle",
    state: "completed",
    command_uuid: secondTurn.uuid,
    session_id: SESSION_ID
  });
  assert.equal((await secondTurn.completion).result.result, "SECOND_DONE");
  await engine.stop();
});

test("credential init is validated before events even when control initialization hangs", async () => {
  const output = new AsyncMailbox();
  const observed = [];
  let initializationRequested = false;
  const engine = startClaudeSdkSession(launch(), {
    onMessage: (message) => observed.push(message.type),
    validateInit(init) {
      if (init.apiKeySource === "user") {
        const error = new Error("Wrong credential.");
        error.code = "sdk_subscription_required";
        throw error;
      }
    },
    queryFactory: ({ prompt }) => ({
      [Symbol.asyncIterator]() {
        return output;
      },
      initializationResult() {
        initializationRequested = true;
        return new Promise(() => {});
      },
      close() {
        output.close();
      }
    })
  });

  const turn = engine.send("Never execute tools.");
  output.push({
    type: "system",
    subtype: "init",
    apiKeySource: "user",
    model: "claude-opus-5",
    session_id: SESSION_ID
  });
  output.push({
    type: "assistant",
    parent_tool_use_id: null,
    message: {
      model: "claude-opus-5",
      content: [{ type: "tool_use", name: "Bash", input: { command: "MUST_NOT_RUN" } }]
    }
  });

  await assert.rejects(engine.ready, (error) => error?.code === "sdk_subscription_required");
  await assert.rejects(turn.completion, (error) => error?.code === "sdk_subscription_required");
  assert.deepEqual(observed, []);
  assert.equal(initializationRequested, false, "control initialization must not delay credential validation");
  assert.equal(engine.abortController.signal.aborted, true);
  await engine.completion;
});

test("startup failures before init keep their native cause instead of becoming credential errors", async () => {
  const output = new AsyncMailbox();
  const engine = startClaudeSdkSession(launch(), {
    queryFactory: () => ({
      [Symbol.asyncIterator]: () => output,
      close: () => output.close()
    })
  });
  const turn = engine.send("Inspect.");
  output.push({ type: "result", subtype: "error_during_execution", is_error: true,
    startup_failure_reason: "provider_not_allowed", errors: ["Provider denied by managed policy."] });
  await assert.rejects(engine.ready, (error) => {
    assert.equal(error.code, "claude_startup");
    assert.equal(error.details.startup_failure_reason, "provider_not_allowed");
    assert.equal(error.details.resumable, false);
    assert.deepEqual(error.details.runtime, { sdk_version: CLAUDE_SDK_VERSION, claude_code_version: null });
    return true;
  });
  assert.equal((await turn.completion).result.startup_failure_reason, "provider_not_allowed");
  await engine.stop();
});

test("context diagnostics use summary only, share pending requests and omit private breakdowns", async () => {
  const output = new AsyncMailbox();
  let resolveUsage;
  let calls = 0;
  const engine = startClaudeSdkSession(launch(), {
    queryFactory: () => ({
      [Symbol.asyncIterator]: () => output,
      getContextUsage(options) {
        calls += 1;
        assert.deepEqual(options, { detail: "summary" });
        return new Promise((resolve) => { resolveUsage = resolve; });
      },
      close: () => output.close()
    })
  });
  assert.equal(await engine.getContextUsage(), null);
  output.push({ type: "system", subtype: "init", session_id: SESSION_ID });
  await engine.ready;
  const first = engine.getContextUsage();
  const second = engine.getContextUsage();
  assert.equal(first, second);
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(calls, 1);
  resolveUsage({ totalTokens: 1200, maxTokens: 200000, percentage: 0.6,
    memoryFiles: [{ path: "PRIVATE_PATH" }], systemPromptSections: [{ name: "PRIVATE_PROMPT" }] });
  assert.deepEqual(await first, { used_tokens: 1200, max_tokens: 200000, used_percent: 0.6, estimated: true });
  await engine.stop();
  assert.equal(await engine.getContextUsage(), null);
});

test("limit projection preserves recovery time and false account signals without copying payment data", () => {
  const message = { type: "rate_limit_event", rate_limit_info: {
    status: "allowed_warning", rateLimitType: "five_hour", resetsAt: 1800000000,
    utilization: 0.9, overageEnabled: false, isUsingOverage: false,
    overageDisabledReason: "org_level_disabled", hasChargeableSavedPaymentMethod: true,
    raw: "PRIVATE_ACCOUNT", overageResetsAt: Infinity
  } };
  assert.equal(claudeRuntimeWarning(message), "subscription_rate_limit_warning:five_hour");
  assert.deepEqual(claudeRateLimit(message), {
    status: "allowed_warning", rate_limit_type: "five_hour", resets_at: 1800000000,
    utilization: 0.9, overage_enabled: false, is_using_overage: false,
    overage_disabled_reason: "org_level_disabled"
  });
  assert.equal(claudeRateLimit({ type: "rate_limit_event", rate_limit_info: { status: "invalid" } }), null);
});
