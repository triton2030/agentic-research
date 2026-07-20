#!/usr/bin/env node
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { askClaude } from "../src/claude-ask.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const bridgeRoot = path.resolve(testDir, "..");
const repoRoot = path.resolve(bridgeRoot, "..", "..");
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), "claude-sdk-live-"));

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

const directClaudeChildren = (snapshot) => [...snapshot]
  .filter(([, processInfo]) => (
    processInfo.ppid === process.pid &&
    processInfo.command.includes("/Users/triton/.local/bin/claude")
  ))
  .map(([pid]) => pid);

const receipts = {};

try {
  const opusCwd = path.join(scratch, "opus");
  const fableCwd = path.join(scratch, "fable");
  fs.mkdirSync(opusCwd);
  fs.mkdirSync(fableCwd);
  const opusMarker = token("OPUS_SCOPE");
  const fableMarker = token("FABLE_SCOPE");
  fs.writeFileSync(path.join(opusCwd, "scope-marker.txt"), `${opusMarker}\n`);
  fs.writeFileSync(path.join(fableCwd, "scope-marker.txt"), `${fableMarker}\n`);

  const [opus, fable] = await Promise.all([
    askClaude({
      cwd: opusCwd,
      profile: "opus_advisor",
      prompt:
        `Read exactly scope-marker.txt, ${path.join(repoRoot, "README.md")}, and /etc/hosts; ` +
        "do not search or start background tasks. " +
        `Return the marker, the README heading Agentic Research, and one localhost line.`
    }),
    askClaude({
      cwd: fableCwd,
      profile: "fable_advisor",
      prompt: "Read scope-marker.txt and return only its exact contents."
    })
  ]);
  assert.match(opus.text, new RegExp(opusMarker, "u"));
  assert.doesNotMatch(opus.text, new RegExp(fableMarker, "u"));
  assert.match(opus.text, /Agentic Research/u);
  assert.match(opus.text, /localhost/iu);
  assert.match(fable.text, new RegExp(fableMarker, "u"));
  assert.doesNotMatch(fable.text, new RegExp(opusMarker, "u"));
  assert.notEqual(opus.session_id, fable.session_id);
  assert.equal(opus.requested_model, "opus");
  assert.equal(fable.requested_model, "fable");

  const [opusResume, fableResume] = await Promise.all([
    askClaude({
      cwd: opusCwd,
      profile: "fable_advisor",
      session_id: opus.session_id,
      prompt: "Return only the exact scope token from the previous turn."
    }),
    askClaude({
      cwd: fableCwd,
      profile: "opus_advisor",
      session_id: fable.session_id,
      prompt: "Return only the exact scope token from the previous turn."
    })
  ]);
  assert.match(opusResume.text, new RegExp(opusMarker, "u"));
  assert.match(fableResume.text, new RegExp(fableMarker, "u"));
  assert.equal(opusResume.session_id, opus.session_id);
  assert.equal(fableResume.session_id, fable.session_id);
  assert.equal(opusResume.requested_model, null);
  assert.equal(fableResume.requested_model, null);
  assert.equal(opusResume.resolved_model, opus.resolved_model);
  assert.equal(fableResume.resolved_model, fable.resolved_model);
  assert.match(opusResume.warnings.join(" "), /resume_session_owns_model/u);
  assert.match(fableResume.warnings.join(" "), /resume_session_owns_model/u);
  receipts.sessions = { opus, opus_resume: opusResume, fable, fable_resume: fableResume };

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
  fs.rmSync(scratch, { recursive: true, force: true });
}
