import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { createClaudeSessionsReader } from "../src/claude-sessions.js";
import { ClaudeAskError } from "../src/claude-result.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const bridgeRoot = path.resolve(testDir, "..");
const fakeClaude = path.join(testDir, "fixtures", "fake-claude.mjs");
const ACTIVE_SESSION = "11111111-1111-4111-8111-111111111111";
const OTHER_SESSION = "22222222-2222-4222-8222-222222222222";

function active(sessionId = ACTIVE_SESSION) {
  return {
    sessionId,
    name: "active-claude",
    kind: "interactive",
    cwd: bridgeRoot,
    startedAt: 1234
  };
}

function transcript() {
  return [
    {
      type: "user",
      message: { content: "First visible request" }
    },
    {
      type: "assistant",
      message: {
        content: [
          { type: "thinking", thinking: "PRIVATE_THINKING" },
          { type: "tool_use", name: "Read", input: { path: "PRIVATE_TOOL_INPUT" } },
          { type: "text", text: "First visible response" }
        ]
      }
    },
    {
      type: "user",
      message: {
        content: [
          { type: "tool_result", content: "PRIVATE_TOOL_RESULT" },
          { type: "text", text: "Latest visible request" }
        ]
      }
    },
    {
      type: "system",
      message: { content: "PRIVATE_SYSTEM" }
    },
    {
      type: "assistant",
      message: { content: [{ type: "text", text: "Latest visible response" }] }
    }
  ];
}

function reader(overrides = {}) {
  return createClaudeSessionsReader({
    executable: fakeClaude,
    listActive: async () => [active()],
    getSessionInfo: async () => ({
      sessionId: ACTIVE_SESSION,
      summary: "Active work",
      customTitle: "Visible title",
      gitBranch: "main"
    }),
    getSessionMessages: async () => transcript(),
    ...overrides
  });
}

test("list_active returns metadata without reading conversation text", async () => {
  let messageReads = 0;
  const result = await reader({
    getSessionMessages: async () => {
      messageReads += 1;
      return transcript();
    }
  }).read({ op: "list_active" });

  assert.equal(result.op, "list_active");
  assert.equal(result.sessions.length, 1);
  assert.deepEqual(result.sessions[0], {
    session_id: ACTIVE_SESSION,
    name: "active-claude",
    kind: "interactive",
    cwd: bridgeRoot,
    started_at_ms: 1234,
    title: "Visible title",
    git_branch: "main"
  });
  assert.equal(messageReads, 0);
  assert.equal(result.session, null);
  assert.deepEqual(result.messages, []);
  assert.deepEqual(result.warnings, []);
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE_/u);
});

test("list_active accepts limit and bounds metadata reads", async () => {
  let metadataReads = 0;
  const result = await reader({
    listActive: async () => [active(), active(OTHER_SESSION)],
    getSessionInfo: async (sessionId) => {
      metadataReads += 1;
      return { sessionId, customTitle: "Active work" };
    }
  }).read({ op: "list_active", limit: 1 });

  assert.equal(result.sessions.length, 1);
  assert.equal(result.sessions[0].session_id, ACTIVE_SESSION);
  assert.equal(metadataReads, 1);
});

test("read requires an active native session and returns only the requested tail", async () => {
  const result = await reader().read({ op: "read", session_id: ACTIVE_SESSION, limit: 2 });

  assert.equal(result.op, "read");
  assert.deepEqual(result.sessions, []);
  assert.equal(result.session.session_id, ACTIVE_SESSION);
  assert.deepEqual(result.messages, [
    { role: "user", text: "Latest visible request" },
    { role: "assistant", text: "Latest visible response" }
  ]);
  assert.deepEqual(result.warnings, []);
  assert.doesNotMatch(JSON.stringify(result), /PRIVATE_/u);

  await assert.rejects(
    reader().read({ op: "read", session_id: OTHER_SESSION }),
    (error) => error instanceof ClaudeAskError && error.code === "session_not_active"
  );
});

test("list_active keeps sessions when one metadata record cannot be read", async () => {
  const result = await reader({
    listActive: async () => [active(), active(OTHER_SESSION)],
    getSessionInfo: async (sessionId) => {
      if (sessionId === OTHER_SESSION) throw new Error("broken metadata");
      return { sessionId, customTitle: "Active work" };
    }
  }).read({ op: "list_active" });

  assert.equal(result.sessions.length, 2);
  assert.equal(result.sessions[1].session_id, OTHER_SESSION);
  assert.equal(result.sessions[1].title, "active-claude");
  assert.deepEqual(result.warnings, []);
});

test("cwd scope is canonical and read failures preserve the native session id", async () => {
  let captured;
  const scoped = reader({
    listActive: async (request) => {
      captured = request;
      return [active()];
    },
    getSessionMessages: async () => {
      throw new Error("broken transcript");
    }
  });

  await assert.rejects(
    scoped.read({ op: "read", session_id: ACTIVE_SESSION, cwd: bridgeRoot }),
    (error) => {
      assert.equal(error.code, "session_read_failed");
      assert.equal(error.details.session_id, ACTIVE_SESSION);
      return true;
    }
  );
  assert.equal(captured.cwd, bridgeRoot);
});
