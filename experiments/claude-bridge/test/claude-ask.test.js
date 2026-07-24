import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { askClaude, ClaudeAskError, withClaudeAskTestDependencies } from "../src/claude-ask.js";
import { createClaudeAskServer } from "../src/ask-server.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const bridgeRoot = path.resolve(testDir, "..");
const fakeClaude = path.join(testDir, "fixtures", "fake-claude.mjs");
const OPUS_SESSION = "11111111-1111-4111-8111-111111111111";
const FABLE_SESSION = "22222222-2222-4222-8222-222222222222";

function sdkMessages({
  sessionId = OPUS_SESSION,
  initModel = "claude-opus-5",
  mainModel = initModel,
  auxiliaryModel,
  text = "ADVICE_OK",
  apiKeySource = "none",
  resultSubtype = "success",
  errors
} = {}) {
  return [
    {
      type: "system",
      subtype: "init",
      apiKeySource,
      model: initModel,
      session_id: sessionId,
      claude_code_version: "2.1.219"
    },
    ...(auxiliaryModel ? [{
      type: "assistant",
      parent_tool_use_id: "subagent-tool-use",
      message: { model: auxiliaryModel }
    }] : []),
    { type: "assistant", parent_tool_use_id: null, message: { model: mainModel } },
    {
      type: "result",
      subtype: resultSubtype,
      is_error: resultSubtype !== "success",
      result: text,
      errors,
      session_id: sessionId,
      duration_ms: 123,
      modelUsage: {
        ...(auxiliaryModel ? { [auxiliaryModel]: {} } : {}),
        [mainModel]: {}
      }
    }
  ];
}

function queryFactoryFor(messages, capture = {}) {
  return ({ prompt, options }) => {
    capture.prompt = prompt;
    capture.options = options;
    return {
      async *[Symbol.asyncIterator]() {
        for (const message of typeof messages === "function" ? messages({ prompt, options }) : messages) yield message;
      },
      close() {
        capture.closed = true;
      }
    };
  };
}

function fakeOptions(messages, overrides = {}) {
  return { executable: fakeClaude, queryFactory: queryFactoryFor(messages), ...overrides };
}

function askTest(request, options = {}) {
  const { signal, ...dependencies } = options;
  return withClaudeAskTestDependencies(dependencies, () => askClaude(request, signal));
}

async function expectClaudeError(promise, code) {
  try {
    await promise;
    assert.fail(`Expected ClaudeAskError(${code})`);
  } catch (error) {
    assert.ok(error instanceof ClaudeAskError, error?.stack || String(error));
    assert.equal(error.code, code);
    assert.ok(error.message.length <= 2000);
    return error;
  }
}

function processAlive(pid) {
  try {
    process.kill(Number(pid), 0);
    return true;
  } catch {
    return false;
  }
}

async function waitForFile(file) {
  const deadline = Date.now() + 3000;
  while (!fs.existsSync(file) && Date.now() < deadline) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(fs.existsSync(file), true, `Timed out waiting for ${file}`);
}

test("one-shot uses fixed profile and native SDK authority", async () => {
  const capture = {};
  const result = await askTest(
    { prompt: "Challenge this design.", profile: "opus_advisor", cwd: bridgeRoot },
    fakeOptions(sdkMessages(), { queryFactory: queryFactoryFor(sdkMessages(), capture) })
  );

  assert.deepEqual(result, {
    text: "ADVICE_OK",
    session_id: OPUS_SESSION,
    requested_model: "opus",
    resolved_model: "claude-opus-5",
    duration_ms: 123,
    warnings: []
  });
  assert.match(capture.prompt, /do not modify files/iu);
  assert.match(capture.prompt, /Challenge this design/u);
  assert.equal(capture.options.model, "claude-opus-5");
  assert.equal(capture.options.effort, "xhigh");
  assert.deepEqual(capture.options.additionalDirectories, ["/"]);
  assert.equal(capture.options.persistSession, true);
  for (const absent of ["allowedTools", "disallowedTools", "permissionMode", "settingSources", "strictMcpConfig", "fallbackModel"]) {
    assert.equal(capture.options[absent], undefined, `${absent} must remain native/unset`);
  }
  assert.equal(capture.closed, true);
});

test("resume keeps the native session model and omits caller model routing", async () => {
  const capture = {};
  const result = await askTest(
    { prompt: "Continue.", profile: "fable_advisor", cwd: bridgeRoot, session_id: OPUS_SESSION },
    fakeOptions(sdkMessages(), { queryFactory: queryFactoryFor(sdkMessages(), capture) })
  );
  assert.equal(capture.options.resume, OPUS_SESSION);
  assert.equal(capture.options.model, undefined);
  assert.equal(capture.options.effort, undefined);
  assert.equal(result.requested_model, null);
  assert.equal(result.resolved_model, "claude-opus-5");
  assert.match(result.warnings.join(" "), /resume_session_owns_model/u);
});

test("parallel subscription preflights and sessions remain independent", async (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "claude-sdk-parallel-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const env = { FAKE_AUTH_BARRIER_DIR: path.join(root, "barrier") };
  const opusCapture = {};
  const fableCapture = {};
  const [left, right] = await Promise.all([
    askTest(
      { prompt: "LEFT", profile: "opus_advisor", cwd: bridgeRoot },
      fakeOptions(sdkMessages({ text: "LEFT", sessionId: OPUS_SESSION }), {
        env,
        queryFactory: queryFactoryFor(sdkMessages({ text: "LEFT", sessionId: OPUS_SESSION }), opusCapture)
      })
    ),
    askTest(
      { prompt: "RIGHT", profile: "fable_advisor", cwd: bridgeRoot },
      fakeOptions(sdkMessages({ text: "RIGHT", sessionId: FABLE_SESSION, initModel: "claude-fable-5" }), {
        env,
        queryFactory: queryFactoryFor(
          sdkMessages({ text: "RIGHT", sessionId: FABLE_SESSION, initModel: "claude-fable-5" }),
          fableCapture
        )
      })
    )
  ]);
  assert.deepEqual([left.text, right.text], ["LEFT", "RIGHT"]);
  assert.notEqual(left.session_id, right.session_id);
  assert.equal(opusCapture.options.model, "claude-opus-5");
  assert.equal(fableCapture.options.model, "claude-fable-5");
  assert.equal(fs.readdirSync(path.join(root, "barrier")).length, 2);
});

test("minimal guard strips explicit routes while preserving native config", async (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "claude-sdk-env-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const configDir = path.join(root, "native-config");
  const authEnvFile = path.join(root, "auth-env.json");
  fs.mkdirSync(configDir);
  fs.writeFileSync(path.join(configDir, "settings.json"), JSON.stringify({ apiKeyHelper: "native-owner" }));
  const capture = {};
  const result = await askTest(
    { prompt: "Inspect.", profile: "opus_advisor", cwd: bridgeRoot },
    fakeOptions(sdkMessages(), {
      env: {
        ANTHROPIC_API_KEY: "strip-me",
        CLAUDE_CODE_USE_VERTEX: "1",
        CLAUDE_CONFIG_DIR: configDir,
        FAKE_AUTH_ENV_FILE: authEnvFile
      },
      queryFactory: queryFactoryFor(sdkMessages(), capture)
    })
  );
  const authEnv = JSON.parse(fs.readFileSync(authEnvFile, "utf8"));
  assert.deepEqual(authEnv, {
    ANTHROPIC_API_KEY: null,
    CLAUDE_CODE_USE_VERTEX: null,
    CLAUDE_CONFIG_DIR: configDir
  });
  assert.equal(capture.options.env.ANTHROPIC_API_KEY, undefined);
  assert.equal(capture.options.env.CLAUDE_CODE_USE_VERTEX, undefined);
  assert.equal(capture.options.env.CLAUDE_CONFIG_DIR, configDir);
  assert.match(result.warnings.join(" "), /environment_overrides_stripped:ANTHROPIC_API_KEY,CLAUDE_CODE_USE_VERTEX/u);
});

test("auth mismatch and invalid public requests fail before SDK query", async () => {
  let queried = false;
  const queryFactory = () => {
    queried = true;
    return queryFactoryFor(sdkMessages())({ prompt: "", options: {} });
  };
  await expectClaudeError(
    askTest(
      { prompt: "Never run.", profile: "opus_advisor", cwd: bridgeRoot },
      {
        executable: fakeClaude,
        env: { FAKE_AUTH_JSON: JSON.stringify({ loggedIn: true, authMethod: "apiKey", apiProvider: "firstParty" }) },
        queryFactory
      }
    ),
    "subscription_required"
  );
  await expectClaudeError(
    askTest({ prompt: "Never run.", profile: "future", cwd: bridgeRoot }, fakeOptions(sdkMessages())),
    "unsupported_profile"
  );
  await expectClaudeError(
    askTest({ prompt: "Never run.", profile: "opus_advisor", cwd: path.join(bridgeRoot, "missing") }, fakeOptions(sdkMessages())),
    "invalid_cwd"
  );
  await expectClaudeError(
    askTest({ prompt: "Never run.", profile: "opus_advisor", cwd: bridgeRoot, session_id: "wrong" }, fakeOptions(sdkMessages())),
    "invalid_session_id"
  );
  await expectClaudeError(
    askTest({ prompt: "X".repeat(60_001), profile: "opus_advisor", cwd: bridgeRoot }, fakeOptions(sdkMessages())),
    "invalid_request"
  );
  assert.equal(queried, false);
});

test("cancellation during auth stops the probe before SDK query", async (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "claude-sdk-auth-cancel-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const pidFile = path.join(root, "auth.pid");
  let queried = false;
  const controller = new AbortController();
  const pending = askTest(
    { prompt: "Never run.", profile: "opus_advisor", cwd: bridgeRoot },
    {
      executable: fakeClaude,
      env: { FAKE_AUTH_DELAY_MS: "5000", FAKE_AUTH_PID_FILE: pidFile },
      queryFactory: () => {
        queried = true;
        throw new Error("must not query");
      },
      signal: controller.signal
    }
  );
  await waitForFile(pidFile);
  const pid = fs.readFileSync(pidFile, "utf8");
  assert.equal(processAlive(pid), true);
  controller.abort();
  await expectClaudeError(pending, "cancelled");
  const deadline = Date.now() + 3000;
  while (processAlive(pid) && Date.now() < deadline) await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(processAlive(pid), false);
  assert.equal(queried, false);
});

function blockingQueryFactory(capture) {
  capture.started = new Promise((resolve) => {
    capture.markStarted = resolve;
  });
  return ({ options }) => ({
    async *[Symbol.asyncIterator]() {
      const aborted = new Promise((resolve, reject) => {
        if (options.abortController.signal.aborted) reject(new Error("SDK aborted"));
        else options.abortController.signal.addEventListener("abort", () => reject(new Error("SDK aborted")), { once: true });
      });
      capture.markStarted();
      yield sdkMessages()[0];
      await aborted;
    },
    close() {
      capture.closed = true;
    }
  });
}

test("host cancellation and timeout close the SDK query", async () => {
  const cancelled = {};
  const controller = new AbortController();
  const pending = askTest(
    { prompt: "Wait.", profile: "opus_advisor", cwd: bridgeRoot },
    { executable: fakeClaude, queryFactory: blockingQueryFactory(cancelled), signal: controller.signal }
  );
  await cancelled.started;
  controller.abort();
  await expectClaudeError(pending, "cancelled");
  assert.equal(cancelled.closed, true);

  const timedOut = {};
  await expectClaudeError(
    askTest(
      { prompt: "Wait.", profile: "fable_advisor", cwd: bridgeRoot },
      { executable: fakeClaude, queryFactory: blockingQueryFactory(timedOut), timeoutMs: 500 }
    ),
    "timeout"
  );
  assert.equal(timedOut.closed, true);
});

test("typed SDK failures are bounded and incomplete evidence fails closed", async () => {
  const oauth = await askTest(
    { prompt: "OAuth evidence.", profile: "opus_advisor", cwd: bridgeRoot },
    fakeOptions(sdkMessages({ apiKeySource: "oauth", text: "OAUTH_OK" }))
  );
  assert.equal(oauth.text, "OAUTH_OK");

  const failed = sdkMessages({ resultSubtype: "error_during_execution", errors: ["X".repeat(5000)] });
  await expectClaudeError(
    askTest({ prompt: "Fail.", profile: "opus_advisor", cwd: bridgeRoot }, fakeOptions(failed)),
    "claude_sdk_result"
  );
  await expectClaudeError(
    askTest({ prompt: "No init.", profile: "opus_advisor", cwd: bridgeRoot }, fakeOptions(sdkMessages().slice(1))),
    "sdk_subscription_required"
  );
  await expectClaudeError(
    askTest(
      { prompt: "Wrong credential.", profile: "opus_advisor", cwd: bridgeRoot },
      fakeOptions(sdkMessages({ apiKeySource: "user" }))
    ),
    "sdk_subscription_required"
  );
});

test("bounded result reports main-model resolution without auxiliary-model corruption", async () => {
  const result = await askTest(
    { prompt: "Deep review.", profile: "fable_advisor", cwd: bridgeRoot },
    fakeOptions(sdkMessages({
      initModel: "claude-fable-5",
      auxiliaryModel: "claude-haiku-4-5-20251001",
      mainModel: "claude-opus-5",
      text: `BEGIN\n${"0123456789".repeat(2000)}\nEND`
    }))
  );
  assert.ok(result.text.length <= 12000);
  assert.match(result.text, /chars omitted/u);
  assert.equal(result.resolved_model, "claude-opus-5");
  assert.match(result.warnings.join(" "), /model_history:claude-fable-5->claude-opus-5/u);
  assert.match(
    result.warnings.join(" "),
    /model_resolution_mismatch:requested=claude-fable-5,resolved=claude-opus-5/u
  );
  assert.doesNotMatch(result.warnings.join(" "), /haiku/u);
  assert.doesNotMatch(result.warnings.join(" "), /safety/u);
});

test("MCP exposes exactly one honest blocking claude_ask schema", async () => {
  const packet = {
    text: "MCP_OK",
    session_id: OPUS_SESSION,
    requested_model: null,
    resolved_model: "claude-opus-5",
    duration_ms: 5,
    warnings: ["resume_session_owns_model"]
  };
  const instance = createClaudeAskServer(async () => packet);
  const client = new Client({ name: "claude-ask-test", version: "1.0.0" });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await instance.server.connect(serverTransport);
  await client.connect(clientTransport);
  try {
    const tools = await client.listTools();
    assert.deepEqual(tools.tools.map((tool) => tool.name), ["claude_ask"]);
    assert.match(tools.tools[0].description, /Opus 5 or Fable 5/u);
    assert.deepEqual(tools.tools[0].annotations, {
      readOnlyHint: false,
      destructiveHint: true,
      idempotentHint: false,
      openWorldHint: true
    });
    assert.match(JSON.stringify(tools.tools[0].outputSchema.properties.requested_model), /null/u);
    const called = await client.callTool({
      name: "claude_ask",
      arguments: { prompt: "Continue.", profile: "opus_advisor", cwd: bridgeRoot, session_id: OPUS_SESSION }
    });
    assert.deepEqual(called.structuredContent, packet);
    assert.ok(Buffer.byteLength(called.content[0].text, "utf8") < 16000);
  } finally {
    await client.close();
    await instance.shutdown();
  }
});

function blockingMcpAsk(capture) {
  capture.started = new Promise((resolve) => {
    capture.markStarted = resolve;
  });
  return async (request, signal) => {
    capture.signal = signal;
    capture.markStarted();
    await new Promise((resolve, reject) => {
      if (signal.aborted) reject(new ClaudeAskError("cancelled", "cancelled"));
      else signal.addEventListener("abort", () => reject(new ClaudeAskError("cancelled", "cancelled")), { once: true });
    });
  };
}

async function connectMcp(ask) {
  const instance = createClaudeAskServer(ask);
  const client = new Client({ name: "claude-cancel-test", version: "1.0.0" });
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  await instance.server.connect(serverTransport);
  await client.connect(clientTransport);
  return { client, instance };
}

test("MCP host cancellation and shutdown reach the deep request signal", async () => {
  const cancelled = {};
  const first = await connectMcp(blockingMcpAsk(cancelled));
  const controller = new AbortController();
  const cancelledCall = first.client.callTool(
    { name: "claude_ask", arguments: { prompt: "Wait.", profile: "opus_advisor", cwd: bridgeRoot } },
    undefined,
    { signal: controller.signal, timeout: 2000 }
  );
  await cancelled.started;
  controller.abort();
  await assert.rejects(cancelledCall, /abort/iu);
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(cancelled.signal.aborted, true);
  await first.client.close();
  await first.instance.shutdown();

  const stopped = {};
  const second = await connectMcp(blockingMcpAsk(stopped));
  const stoppedCall = second.client.callTool({
    name: "claude_ask",
    arguments: { prompt: "Wait.", profile: "fable_advisor", cwd: bridgeRoot }
  });
  const stoppedOutcome = stoppedCall.catch((error) => error);
  await stopped.started;
  await second.instance.shutdown();
  assert.equal(stopped.signal.aborted, true);
  const stoppedResult = await stoppedOutcome;
  assert.ok(stoppedResult);
  await second.client.close();
});
