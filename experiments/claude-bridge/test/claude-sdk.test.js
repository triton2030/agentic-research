import assert from "node:assert/strict";
import test from "node:test";
import { AsyncMailbox, startClaudeSdkSession } from "../src/claude-sdk.js";

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

  output.push({
    type: "system",
    subtype: "session_state_changed",
    state: "idle",
    session_id: SESSION_ID
  });
  const raw = await turn.completion;
  assert.equal(raw.result.result, "DONE");

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
