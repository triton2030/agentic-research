#!/usr/bin/env node
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { askClaude } from "../src/claude-ask.js";
import { createClaudeSessionAdapter } from "../src/claude-session.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const bridgeRoot = path.resolve(testDir, "..");
const repoRoot = path.resolve(bridgeRoot, "..", "..");
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "claude-sdk-live-"));
const activeSessionStates = new Set([
  "starting",
  "thinking",
  "tool",
  "subagent",
  "retrying",
  "steering",
  "requires_action"
]);
const observationKeys = [
  "active_tool",
  "background_tasks",
  "changed",
  "cursor",
  "direction",
  "events",
  "last_activity_age_ms",
  "messages",
  "possibly_stalled",
  "requested_effort",
  "requested_model",
  "resolved_model",
  "session_id",
  "state",
  "terminal",
  "thinking_tokens",
  "warnings"
];

function token(prefix) {
  return `${prefix}_${randomUUID().slice(0, 8).toUpperCase()}`;
}

function alive(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function processSnapshot() {
  const raw = execFileSync("ps", ["-axo", "pid=,ppid=,pgid=,command="], { encoding: "utf8" });
  return new Map(raw.trim().split("\n").map((line) => {
    const match = line.trim().match(/^(\d+)\s+(\d+)\s+(\d+)\s+(.*)$/u);
    return match
      ? [Number(match[1]), { ppid: Number(match[2]), pgid: Number(match[3]), command: match[4] }]
      : null;
  }).filter(Boolean));
}

function descendants(snapshot, rootPid) {
  const found = new Set([rootPid]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const [pid, processInfo] of snapshot) {
      if (found.has(processInfo.ppid) && !found.has(pid)) {
        found.add(pid);
        changed = true;
      }
    }
  }
  return found;
}

async function waitForPid(getPid) {
  const deadline = Date.now() + 10_000;
  while (!getPid() && Date.now() < deadline) await new Promise((resolve) => setTimeout(resolve, 25));
  assert.ok(getPid(), "Agent SDK did not expose its Claude PID");
}

async function waitUntilDead(pid) {
  const deadline = Date.now() + 5000;
  while (alive(pid) && Date.now() < deadline) await new Promise((resolve) => setTimeout(resolve, 25));
  assert.equal(alive(pid), false, `Claude process ${pid} survived cancellation`);
}

async function observeTreeUntilSettled(rootPid, observedTree, completion) {
  let settled = false;
  completion.finally(() => { settled = true; });
  const deadline = Date.now() + 5000;
  while (!settled && Date.now() < deadline) {
    for (const pid of descendants(processSnapshot(), rootPid)) observedTree.add(pid);
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  assert.equal(settled, true, "Claude cancellation did not settle within five seconds");
  for (const pid of descendants(processSnapshot(), rootPid)) observedTree.add(pid);
  await completion;
}

function assertBoundedObservation(packet, detail, { limit, maxChars }) {
  assert.deepEqual(Object.keys(packet).sort(), observationKeys);
  assert.ok(packet.events.length <= limit);
  assert.ok(packet.messages.length <= limit);
  assert.ok(Buffer.byteLength(JSON.stringify(packet), "utf8") <= 12_000);
  assert.doesNotMatch(
    JSON.stringify(packet),
    /"(?:content|thinking|thinking_blocks|tool_input|tool_output|tool_result|tool_use|tool_use_result)"\s*:/u
  );
  for (const event of packet.events) {
    assert.deepEqual(Object.keys(event).sort(), ["at_ms", "cursor", "summary", "type"]);
    assert.ok(event.summary.length <= 220);
  }
  for (const message of packet.messages) {
    assert.deepEqual(Object.keys(message).sort(), ["cursor", "role", "text"]);
  }
  if (detail === "summary") {
    assert.deepEqual(packet.events, []);
    assert.deepEqual(packet.messages, []);
  } else if (detail === "activity") {
    assert.deepEqual(packet.messages, []);
  } else {
    assert.deepEqual(packet.events, []);
    assert.ok(packet.messages.reduce((total, message) => total + message.text.length, 0) <= maxChars);
  }
}

async function waitUntilIdle(adapter, sessionId, initialSnapshot, timeoutMs = 90_000) {
  const deadline = Date.now() + timeoutMs;
  let snapshot = initialSnapshot;
  while (snapshot.state !== "idle" || snapshot.terminal?.kind !== "success") {
    assert.doesNotMatch(snapshot.state, /^(?:closed|failed|timed_out)$/u);
    const remainingMs = deadline - Date.now();
    assert.ok(remainingMs > 0, `Claude session ${sessionId} did not become idle`);
    if (snapshot.state === "idle") {
      await new Promise((resolve) => setTimeout(resolve, 25));
    }
    snapshot = await adapter.observe({
      session_id: sessionId,
      detail: "summary",
      cursor: snapshot.cursor,
      wait_ms: Math.min(10_000, remainingMs),
      limit: 1,
      max_chars: 200
    });
  }
  return snapshot;
}

const directClaudeChildren = (snapshot) => [...snapshot]
  .filter(([, processInfo]) => (
    processInfo.ppid === process.pid &&
    processInfo.command.includes("/Users/triton/.local/bin/claude")
  ))
  .map(([pid]) => pid);

const receipts = {};
let sessionAdapter = null;

try {
  const opusCwd = path.join(scratch, "opus");
  const secondCwd = path.join(scratch, "second-opus");
  fs.mkdirSync(opusCwd);
  fs.mkdirSync(secondCwd);
  const opusMarker = token("OPUS_SCOPE");
  const secondMarker = token("SECOND_OPUS_SCOPE");
  fs.writeFileSync(path.join(opusCwd, "scope-marker.txt"), `${opusMarker}\n`);
  fs.writeFileSync(path.join(secondCwd, "scope-marker.txt"), `${secondMarker}\n`);

  const [opus, second] = await Promise.all([
    askClaude({
      cwd: opusCwd,
      profile: "opus_advisor",
      prompt:
        `Read exactly scope-marker.txt, ${path.join(repoRoot, "README.md")}, and /etc/hosts; ` +
        "do not search or start background tasks. " +
        `Return the marker, the README heading Agentic Research, and one localhost line.`
    }),
    askClaude({
      cwd: secondCwd,
      profile: "opus_advisor",
      prompt: "Read scope-marker.txt and return only its exact contents."
    })
  ]);
  assert.match(opus.text, new RegExp(opusMarker, "u"));
  assert.doesNotMatch(opus.text, new RegExp(secondMarker, "u"));
  assert.match(opus.text, /Agentic Research/u);
  assert.match(opus.text, /localhost/iu);
  assert.match(second.text, new RegExp(secondMarker, "u"));
  assert.doesNotMatch(second.text, new RegExp(opusMarker, "u"));
  assert.notEqual(opus.session_id, second.session_id);
  assert.equal(opus.requested_model, "opus");
  assert.equal(second.requested_model, "opus");
  assert.equal(opus.resolved_model, "claude-opus-5");
  assert.equal(second.resolved_model, "claude-opus-5");

  const [opusResume, secondResume] = await Promise.all([
    askClaude({
      cwd: opusCwd,
      session_id: opus.session_id,
      prompt: "Return only the exact scope token from the previous turn."
    }),
    askClaude({
      cwd: secondCwd,
      session_id: second.session_id,
      prompt: "Return only the exact scope token from the previous turn."
    })
  ]);
  assert.match(opusResume.text, new RegExp(opusMarker, "u"));
  assert.match(secondResume.text, new RegExp(secondMarker, "u"));
  assert.equal(opusResume.session_id, opus.session_id);
  assert.equal(secondResume.session_id, second.session_id);
  assert.equal(opusResume.requested_model, null);
  assert.equal(secondResume.requested_model, null);
  assert.equal(opusResume.resolved_model, opus.resolved_model);
  assert.equal(secondResume.resolved_model, second.resolved_model);
  assert.match(opusResume.warnings.join(" "), /resume_session_owns_model/u);
  assert.match(secondResume.warnings.join(" "), /resume_session_owns_model/u);
  receipts.sessions = { opus, opus_resume: opusResume, second_opus: second, second_opus_resume: secondResume };

  sessionAdapter = createClaudeSessionAdapter();
  const sessionMarker = token("SESSION_ADAPTER");
  const steerMarker = token("SESSION_STEER");
  const toolOutputMarker = token("RAW_TOOL_OUTPUT");
  const sessionCwd = path.join(scratch, "session");
  fs.mkdirSync(sessionCwd);
  fs.writeFileSync(path.join(sessionCwd, "tool-output.txt"), `${toolOutputMarker}\n`);
  let controlledSessionId = null;
  let explicitlyStopped = false;
  try {
    const opened = await sessionAdapter.command({
      op: "open_fresh",
      cwd: sessionCwd,
      profile: "opus_advisor",
      prompt:
        "Use the Read tool once to read tool-output.txt. " +
        `After reading it, reply with exactly ${sessionMarker}; do not repeat the file contents.`
    });
    controlledSessionId = opened.session_id;
    assert.equal(opened.accepted_op, "open_fresh");
    assert.ok(activeSessionStates.has(opened.state), `open_fresh returned in unexpected state ${opened.state}`);
    assert.equal(opened.terminal, null, "open_fresh waited for the terminal result");

    const openingSummary = await sessionAdapter.observe({
      session_id: controlledSessionId,
      detail: "summary",
      wait_ms: 0,
      limit: 1,
      max_chars: 200
    });
    assertBoundedObservation(openingSummary, "summary", { limit: 1, maxChars: 200 });

    const firstIdle = await waitUntilIdle(sessionAdapter, controlledSessionId, openingSummary);
    assertBoundedObservation(firstIdle, "summary", { limit: 1, maxChars: 200 });
    assert.equal(firstIdle.terminal?.kind, "success");

    const activity = await sessionAdapter.observe({
      session_id: controlledSessionId,
      detail: "activity",
      wait_ms: 0,
      limit: 8,
      max_chars: 400
    });
    assertBoundedObservation(activity, "activity", { limit: 8, maxChars: 400 });
    assert.ok(activity.events.some((event) => event.type === "tool" && /Read/iu.test(event.summary)));
    assert.doesNotMatch(JSON.stringify(activity), new RegExp(toolOutputMarker, "u"));

    const firstConversation = await sessionAdapter.observe({
      session_id: controlledSessionId,
      detail: "conversation",
      wait_ms: 0,
      limit: 4,
      max_chars: 800
    });
    assertBoundedObservation(firstConversation, "conversation", { limit: 4, maxChars: 800 });
    assert.match(
      firstConversation.messages.filter(({ role }) => role === "assistant").at(-1)?.text || "",
      new RegExp(sessionMarker, "u")
    );
    assert.doesNotMatch(JSON.stringify(firstConversation), new RegExp(toolOutputMarker, "u"));

    const followUp = await sessionAdapter.command({
      op: "send",
      session_id: controlledSessionId,
      prompt: "Return only the exact token from your immediately previous answer. Do not use tools."
    });
    assert.equal(followUp.accepted_op, "send");
    assert.equal(followUp.session_id, controlledSessionId);

    const followUpIdle = await waitUntilIdle(sessionAdapter, controlledSessionId, followUp);
    assert.equal(followUpIdle.session_id, controlledSessionId);
    assert.equal(followUpIdle.terminal?.kind, "success");

    const followUpConversation = await sessionAdapter.observe({
      session_id: controlledSessionId,
      detail: "conversation",
      wait_ms: 0,
      limit: 4,
      max_chars: 800
    });
    assertBoundedObservation(followUpConversation, "conversation", { limit: 4, maxChars: 800 });
    assert.match(
      followUpConversation.messages.filter(({ role }) => role === "assistant").at(-1)?.text || "",
      new RegExp(sessionMarker, "u")
    );

    const longTurn = await sessionAdapter.command({
      op: "send",
      session_id: controlledSessionId,
      prompt:
        "Develop a very long, exhaustive analysis of every possible architecture for this bridge. " +
        "Do not use tools and do not give a short answer."
    });
    assert.ok(activeSessionStates.has(longTurn.state), `long send returned in unexpected state ${longTurn.state}`);
    const steered = await sessionAdapter.command({
      op: "steer",
      session_id: controlledSessionId,
      prompt: `Stop the prior analysis and return only ${steerMarker}. Do not use tools.`
    });
    assert.equal(steered.accepted_op, "steer");
    assert.equal(steered.session_id, controlledSessionId);

    const steerIdle = await waitUntilIdle(sessionAdapter, controlledSessionId, steered);
    assert.equal(steerIdle.terminal?.kind, "success");
    const steerConversation = await sessionAdapter.observe({
      session_id: controlledSessionId,
      detail: "conversation",
      wait_ms: 0,
      limit: 4,
      max_chars: 800
    });
    assertBoundedObservation(steerConversation, "conversation", { limit: 4, maxChars: 800 });
    assert.match(
      steerConversation.messages.filter(({ role }) => role === "assistant").at(-1)?.text || "",
      new RegExp(steerMarker, "u")
    );

    const stopped = await sessionAdapter.command({ op: "stop", session_id: controlledSessionId });
    explicitlyStopped = true;
    assert.equal(stopped.accepted_op, "stop");
    assert.equal(stopped.session_id, controlledSessionId);
    assert.equal(stopped.state, "closed");
    receipts.session_adapter = {
      opened,
      opening_summary: openingSummary,
      first_idle: firstIdle,
      activity,
      first_conversation: firstConversation,
      follow_up: followUp,
      follow_up_idle: followUpIdle,
      follow_up_conversation: followUpConversation,
      long_turn: longTurn,
      steered,
      steer_idle: steerIdle,
      steer_conversation: steerConversation,
      stopped
    };
  } finally {
    if (controlledSessionId && !explicitlyStopped) {
      await sessionAdapter.command({ op: "stop", session_id: controlledSessionId }).catch(() => {});
    }
    await sessionAdapter.shutdown();
    sessionAdapter = null;
  }

  let abortRootPid = null;
  const abortController = new AbortController();
  const abortPromise = askClaude(
    {
      cwd: bridgeRoot,
      profile: "opus_advisor",
      prompt: "Think silently for several minutes before replying. Do not use tools."
    },
    abortController.signal
  );
  await waitForPid(() => {
    abortRootPid ||= directClaudeChildren(processSnapshot())[0] || null;
    return abortRootPid;
  });
  const observedTree = new Set([abortRootPid]);
  for (const delayMs of [250, 500, 750]) {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
    for (const pid of descendants(processSnapshot(), abortRootPid)) observedTree.add(pid);
  }
  const observedBeforeAbort = new Set(observedTree);
  abortController.abort();
  const cancellation = assert.rejects(abortPromise, (error) => error?.code === "cancelled");
  await observeTreeUntilSettled(abortRootPid, observedTree, cancellation);
  for (const pid of observedTree) await waitUntilDead(pid);
  receipts.abort = {
    root_pid: abortRootPid,
    observed_process_tree: [...observedTree].sort((left, right) => left - right),
    observed_after_abort: [...observedTree]
      .filter((pid) => !observedBeforeAbort.has(pid))
      .sort((left, right) => left - right),
    alive_after: [...observedTree].filter(alive)
  };
  process.stdout.write(`${JSON.stringify(receipts, null, 2)}\n`);
} finally {
  await sessionAdapter?.shutdown();
  fs.rmSync(scratch, { recursive: true, force: true });
}
