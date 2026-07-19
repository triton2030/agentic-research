import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const bridgeRoot = path.resolve(__dirname, "..");
const fakeClaude = path.join(__dirname, "fixtures", "fake-claude.mjs");
const cli = path.join(bridgeRoot, "src", "cli.js");
const smokeStateRoot = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-smoke-state-"));
const runsDir = path.join(smokeStateRoot, "runs");
const smokeTmuxSessions = new Set();
process.env.CLAUDE_BRIDGE_CLAUDE_BIN = fakeClaude;
process.env.CLAUDE_BRIDGE_RUNS_DIR = runsDir;
const {
  archiveThread,
  auditSkill,
  cleanupRuns,
  doctor,
  killRun,
  listThreads,
  peekRun,
  profiles,
  resultRun,
  sendThread,
  startRun,
  startThread,
  waitRun
} = await import("../src/runner.js");

function cleanupSmokeTmuxSessions() {
  for (const session of smokeTmuxSessions) {
    spawnSync("tmux", ["kill-session", "-t", session], { encoding: "utf8" });
  }
}

function trackTmuxSession(payload) {
  if (payload?.tmux_session) smokeTmuxSessions.add(payload.tmux_session);
}

process.once("exit", () => {
  cleanupSmokeTmuxSessions();
  fs.rmSync(smokeStateRoot, { recursive: true, force: true });
});

function cliJson(args) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd: bridgeRoot,
    env: { ...process.env, CLAUDE_BRIDGE_CLAUDE_BIN: fakeClaude },
    encoding: "utf8"
  });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return JSON.parse(result.stdout);
}

function writeSyntheticState(runId, state) {
  const runDir = path.join(runsDir, runId);
  fs.mkdirSync(runDir, { recursive: true });
  const files = {
    prompt: path.join(runDir, "prompt.txt"),
    profile: path.join(runDir, "profile.json"),
    command: path.join(runDir, "command.json"),
    events: path.join(runDir, "events.ndjson"),
    stdout: path.join(runDir, "stdout.log"),
    stderr: path.join(runDir, "stderr.log"),
    debug: path.join(runDir, "debug.log"),
    report: path.join(runDir, "report.json"),
    state: path.join(runDir, "state.json")
  };
  fs.writeFileSync(files.events, "");
  fs.writeFileSync(
    files.state,
    JSON.stringify(
      {
        run_id: runId,
        profile: "normal",
        model: "opus",
        cwd: bridgeRoot,
        pid: process.pid,
        status: "running",
        started_at: new Date().toISOString(),
        command: [process.execPath, "--debug-file", "/tmp/not-this-run/debug.log"],
        log_dir: runDir,
        files,
        ...state
      },
      null,
      2
    )
  );
  return { runDir, files };
}

function readPidFile(file) {
  return Number(fs.readFileSync(file, "utf8").trim());
}

function pidAlive(pid) {
  return spawnSync("ps", ["-p", String(pid)], { encoding: "utf8" }).status === 0;
}

async function waitForFile(file, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (fs.existsSync(file)) return;
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error(`Timed out waiting for ${file}`);
}

async function waitForPidExit(pid, label, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (!pidAlive(pid)) return;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`${label} pid ${pid} is still alive`);
}

const doctorReport = doctor();
assert.equal(doctorReport.ok, true);
assert.equal(doctorReport.ready_for_live_runs, true);
assert.equal(doctorReport.auth.logged_in, true);
assert.equal(doctorReport.stream_json_supported, true);
assert.equal(doctorReport.flags["--effort"], true);
assert.equal(doctorReport.flags["--dangerously-skip-permissions"], true);
assert.equal(doctorReport.flags["--permission-mode"], true);
assert.equal(doctorReport.flags["--json-schema"], true);
assert.equal(doctorReport.flags["--agent"], true);
assert.equal(doctorReport.flags["--agents"], true);
assert.equal(doctorReport.flags["--session-id"], true);
assert.equal(doctorReport.flags["--resume"], true);
assert.equal(doctorReport.flags["--max-turns"], true);
assert.equal(doctorReport.flag_evidence["--max-turns"], "parser_probe");

const profileList = profiles();
assert.ok(profileList.some((profile) => profile.name === "advisor" && profile.flags.includes("plan")));
assert.ok(profileList.some((profile) => profile.name === "fable-advisor" && profile.flags.includes("fable")));
assert.ok(profileList.some((profile) => profile.name === "worker" && profile.flags.includes("auto")));
assert.ok(profileList.some((profile) => profile.name === "unrestricted" && profile.flags.includes("--dangerously-skip-permissions")));
assert.ok(profileList.some((profile) => profile.name === "turbo" && profile.flags.includes("plan")));
assert.ok(profileList.some((profile) => profile.name === "no-skills" && profile.flags.includes("--disable-slash-commands")));
assert.ok(profileList.some((profile) => profile.name === "no-memory"));
assert.equal(profileList.some((profile) => profile.name === "clean"), false);
assert.equal(profileList.some((profile) => profile.name === "subagent"), false);
for (const profileName of ["advisor", "worker", "normal", "no-memory", "no-skills", "read-only", "turbo", "skill-audit", "streaming-observe"]) {
  const profile = profileList.find((candidate) => candidate.name === profileName);
  assert.ok(profile, `${profileName} profile should exist`);
  assert.deepEqual(
    profile.flags.slice(profile.flags.indexOf("--effort"), profile.flags.indexOf("--effort") + 2),
    ["--effort", "max"],
    `${profileName} must use max effort`
  );
}
const fableProfile = profileList.find((profile) => profile.name === "fable-advisor");
assert.deepEqual(
  fableProfile.flags.slice(fableProfile.flags.indexOf("--effort"), fableProfile.flags.indexOf("--effort") + 2),
  ["--effort", "xhigh"]
);
for (const profile of profileList) {
  if (profile.flags.includes("stream-json")) {
    assert.ok(profile.flags.includes("--verbose"), `${profile.name} must include --verbose with stream-json`);
  }
  if (profile.name !== "unrestricted") {
    assert.equal(profile.flags.includes("--dangerously-skip-permissions"), false, `${profile.name} must not bypass permissions`);
  }
}
const hiddenFlagRun = startRun({
  prompt: "Hidden documented flag parser probe.",
  profile: "normal",
  cwd: bridgeRoot,
  maxTurns: 1
});
assert.equal((await waitRun(hiddenFlagRun.run_id, { timeoutMs: 10000 })).status, "completed");
process.env.FAKE_CLAUDE_REJECT_OPTION = "--max-turns";
assert.throws(
  () => startRun({ prompt: "Rejected hidden flag.", profile: "normal", cwd: bridgeRoot, maxTurns: 1 }),
  /does not support required option/
);
delete process.env.FAKE_CLAUDE_REJECT_OPTION;
assert.throws(
  () => startRun({ prompt: "No policy override.", profile: "advisor", cwd: bridgeRoot, permissionMode: "bypassPermissions" }),
  /fixes permissionMode=plan/u
);
assert.throws(
  () => startRun({ prompt: "No model override.", profile: "fable-advisor", cwd: bridgeRoot, model: "opus" }),
  /fixes model=fable/u
);
assert.throws(
  () =>
    startRun({
      prompt: "Reserved flags stay first-class.",
      profile: "unrestricted",
      cwd: bridgeRoot,
      extraArgs: ["--model", "fable"]
    }),
  /cannot override bridge-owned controls/u
);
assert.throws(
  () =>
    startRun({
      prompt: "Equals syntax cannot bypass typed controls.",
      profile: "unrestricted",
      cwd: bridgeRoot,
      extraArgs: ["--model=fable"]
    }),
  /cannot override bridge-owned controls/u
);

const fakeEnvCaptureFile = path.join(runsDir, "_fake-claude-env.json");
fs.rmSync(fakeEnvCaptureFile, { force: true });
process.env.FAKE_CLAUDE_ENV_CAPTURE = fakeEnvCaptureFile;
process.env.ANTHROPIC_API_KEY = "should-not-leak";
process.env.CLAUDE_API_KEY = "should-not-leak";
const started = startRun({
  prompt: "Return exactly BRIDGE_OK.",
  profile: "normal",
  cwd: bridgeRoot
});
assert.ok(started.run_id);
assert.ok(fs.existsSync(started.log_dir));

const peek = peekRun(started.run_id);
assert.equal(peek.run_id, started.run_id);
assert.ok(Array.isArray(peek.milestones));

const report = await waitRun(started.run_id, { timeoutMs: 10000 });
const startedCommand = JSON.parse(fs.readFileSync(report.files.command, "utf8"));
assert.equal(startedCommand.args.filter((value) => value === "--model").length, 1);
assert.equal(startedCommand.args.filter((value) => value === "--effort").length, 1);
assert.equal(startedCommand.args.filter((value) => value === "--permission-mode").length, 1);
const fakeEnvCapture = JSON.parse(fs.readFileSync(fakeEnvCaptureFile, "utf8"));
assert.equal(startedCommand.env.api_key_env_stripped, true);
assert.deepEqual(fakeEnvCapture, { ANTHROPIC_API_KEY: null, CLAUDE_API_KEY: null });
delete process.env.FAKE_CLAUDE_ENV_CAPTURE;
delete process.env.ANTHROPIC_API_KEY;
delete process.env.CLAUDE_API_KEY;
assert.equal(report.status, "completed");
assert.equal(report.model, "opus");
assert.equal(report.resolved_model, "claude-opus-4-8");
assert.equal(report.session_id, started.session_id);
assert.equal(report.session_observed, true);
assert.equal(report.managed, false);
assert.match(report.final_output_summary, /BRIDGE_OK/);
assert.match(report.chat_relay.text, /BRIDGE_OK/);
assert.match(report.chat_relay.markdown, /Claude:\nBRIDGE_OK/);
assert.equal(report.chat_relay.full_text_file, report.files.final_output);
assert.match(fs.readFileSync(report.files.final_output, "utf8"), /BRIDGE_OK/);
assert.equal(report.agent_behavior.role, "controlled_external_claude");
assert.equal(report.agent_behavior.tail.terminal, true);
assert.ok(fs.existsSync(report.files.state));
assert.ok(report.milestones.some((event) => event.kind === "assistant_text" && /BRIDGE_OK/u.test(event.text)));

const syntheticModelRun = startRun({
  prompt: "SYNTHETIC_MODEL_AFTER_INIT",
  profile: "advisor",
  cwd: bridgeRoot
});
const syntheticModelReport = await waitRun(syntheticModelRun.run_id, { timeoutMs: 10000 });
assert.equal(syntheticModelReport.resolved_model, "claude-opus-4-8");

const separateResult = cliJson(["result", "--run-id", started.run_id]);
assert.equal(separateResult.status, "completed");
assert.equal(separateResult.managed, false);
assert.match(separateResult.final_output_summary, /BRIDGE_OK/);
assert.match(separateResult.chat_relay.text, /BRIDGE_OK/);
assert.match(fs.readFileSync(separateResult.files.final_output, "utf8"), /BRIDGE_OK/);
const separatePeek = cliJson(["peek", "--run-id", started.run_id, "--cursor", "0"]);
assert.equal(separatePeek.status, "completed");
assert.equal(separatePeek.managed, false);
assert.ok(separatePeek.next_cursor > 0);
assert.ok(Array.isArray(separatePeek.relay_updates));
assert.match(separatePeek.chat_relay.text, /BRIDGE_OK/);

const noMemoryRun = startRun({
  prompt: "Return exactly BRIDGE_OK.",
  profile: "no-memory",
  cwd: bridgeRoot
});
const noMemoryReport = await waitRun(noMemoryRun.run_id, { timeoutMs: 10000 });
const noMemoryCommand = JSON.parse(fs.readFileSync(noMemoryReport.files.command, "utf8"));
assert.equal(noMemoryCommand.env.CLAUDE_CODE_DISABLE_AUTO_MEMORY, "1");

const threadSuffix = `${process.pid}-${Date.now()}`;
const opusThread = startThread({
  prompt: "Return exactly BRIDGE_OK for the persistent Opus thread.",
  topic: `smoke-opus-${threadSuffix}`,
  profile: "advisor",
  cwd: bridgeRoot
});
const fableThread = startThread({
  prompt: "Return exactly BRIDGE_OK for the independent Fable thread.",
  topic: `smoke-fable-${threadSuffix}`,
  profile: "fable-advisor",
  cwd: bridgeRoot
});
const [opusThreadReport, fableThreadReport] = await Promise.all([
  waitRun(opusThread.run_id, { timeoutMs: 10000 }),
  waitRun(fableThread.run_id, { timeoutMs: 10000 })
]);
assert.equal(opusThreadReport.session_id, opusThread.thread_id);
assert.equal(opusThreadReport.session_observed, true);
assert.equal(opusThreadReport.resolved_model, "claude-opus-4-8");
assert.equal(fableThreadReport.session_id, fableThread.thread_id);
assert.equal(fableThreadReport.session_observed, true);
assert.equal(fableThreadReport.model, "fable");
assert.equal(fableThreadReport.effort, "xhigh");
assert.equal(fableThreadReport.resolved_model, "claude-fable-5");
assert.notEqual(opusThread.thread_id, fableThread.thread_id);

const continuedOpus = sendThread({
  thread_id: opusThread.thread_id,
  prompt: "Continue this same conversation and return BRIDGE_OK.",
  cwd: bridgeRoot
});
const continuedOpusReport = await waitRun(continuedOpus.run_id, { timeoutMs: 10000 });
const continuedCommand = JSON.parse(fs.readFileSync(continuedOpusReport.files.command, "utf8"));
const resumeIndex = continuedCommand.args.indexOf("--resume");
assert.ok(resumeIndex >= 0);
assert.equal(continuedCommand.args[resumeIndex + 1], opusThread.thread_id);
assert.equal(continuedOpusReport.session_id, opusThread.thread_id);
const cliThreadList = cliJson(["threads", "--cwd", bridgeRoot, "--include-archived"]);
assert.ok(cliThreadList.threads.some((thread) => thread.thread_id === opusThread.thread_id));

const smokeThreads = listThreads({ cwd: bridgeRoot, includeArchived: true }).threads.filter((thread) =>
  thread.topic?.endsWith(threadSuffix)
);
assert.equal(smokeThreads.length, 2);
assert.equal(smokeThreads.find((thread) => thread.thread_id === opusThread.thread_id)?.turns, 2);
assert.equal(smokeThreads.find((thread) => thread.thread_id === fableThread.thread_id)?.turns, 1);
assert.equal(smokeThreads.every((thread) => thread.last_status === "completed"), true);
assert.equal(smokeThreads.every((thread) => thread.lifecycle === "ready" && thread.resumable), true);
archiveThread({ thread_id: fableThread.thread_id });
assert.equal(
  listThreads({ cwd: bridgeRoot }).threads.some((thread) => thread.thread_id === fableThread.thread_id),
  false
);
assert.throws(
  () => sendThread({ thread_id: fableThread.thread_id, prompt: "Must not resume archived thread." }),
  /archived/u
);
archiveThread({ thread_id: fableThread.thread_id, archived: false });

const busyThread = startThread({
  prompt: "SLEEP_BRIDGE",
  topic: `smoke-busy-${threadSuffix}`,
  profile: "advisor",
  cwd: bridgeRoot
});
const busyThreadStatus = listThreads({ cwd: bridgeRoot, includeArchived: true }).threads.find(
  (thread) => thread.thread_id === busyThread.thread_id
);
assert.equal(busyThreadStatus.lifecycle, "busy");
assert.equal(busyThreadStatus.resumable, false);
assert.throws(
  () => sendThread({ thread_id: busyThread.thread_id, prompt: "Concurrent resume must fail." }),
  /already has a live turn/u
);
killRun(busyThread.run_id);
await waitRun(busyThread.run_id, { timeoutMs: 10000 });
assert.throws(
  () => sendThread({ thread_id: busyThread.thread_id, prompt: "Killed first turn is not resumable." }),
  /no completed, stream-observed session/u
);

const raceTurnsBefore = listThreads({ cwd: bridgeRoot, includeArchived: true }).threads.find(
  (thread) => thread.thread_id === opusThread.thread_id
).turns;
const raceArgs = [
  cli,
  "thread-send",
  "--thread-id",
  opusThread.thread_id,
  "--prompt",
  "SLEEP_BRIDGE"
];
const raceEnv = { ...process.env, CLAUDE_BRIDGE_CLAUDE_BIN: fakeClaude };
const raceOne = spawn(process.execPath, raceArgs, { cwd: bridgeRoot, env: raceEnv, stdio: ["ignore", "pipe", "pipe"] });
const raceTwo = spawn(process.execPath, raceArgs, { cwd: bridgeRoot, env: raceEnv, stdio: ["ignore", "pipe", "pipe"] });
const raceExits = [raceOne, raceTwo].map(
  (child) => new Promise((resolve) => child.once("exit", (code) => resolve(code)))
);
let racedThread;
const raceDeadline = Date.now() + 5000;
while (Date.now() < raceDeadline) {
  racedThread = listThreads({ cwd: bridgeRoot, includeArchived: true }).threads.find(
    (thread) => thread.thread_id === opusThread.thread_id
  );
  if (racedThread?.turns === raceTurnsBefore + 1 && racedThread.lifecycle === "busy") break;
  await new Promise((resolve) => setTimeout(resolve, 50));
}
assert.equal(racedThread.turns, raceTurnsBefore + 1);
assert.equal(racedThread.lifecycle, "busy");
killRun(racedThread.last_run_id);
const raceStopDeadline = Date.now() + 5000;
while (Date.now() < raceStopDeadline && !["killed", "failed"].includes(resultRun(racedThread.last_run_id).status)) {
  await new Promise((resolve) => setTimeout(resolve, 50));
}
const raceExitCodes = (await Promise.all(raceExits)).sort();
assert.deepEqual(raceExitCodes, [0, 1]);

const workerRepo = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-worker-"));
assert.equal(spawnSync("git", ["init", "-q"], { cwd: workerRepo }).status, 0);
assert.equal(spawnSync("git", ["config", "user.email", "bridge@example.invalid"], { cwd: workerRepo }).status, 0);
assert.equal(spawnSync("git", ["config", "user.name", "Claude Bridge Smoke"], { cwd: workerRepo }).status, 0);
fs.writeFileSync(path.join(workerRepo, "allowed.txt"), "baseline\n");
fs.writeFileSync(path.join(workerRepo, "outside.txt"), "baseline\n");
fs.writeFileSync(path.join(workerRepo, ".gitignore"), "ignored.txt\n");
assert.equal(spawnSync("git", ["add", "."], { cwd: workerRepo }).status, 0);
assert.equal(spawnSync("git", ["commit", "-qm", "baseline"], { cwd: workerRepo }).status, 0);
const branchThread = startThread({
  prompt: "Return BRIDGE_OK for branch identity.",
  topic: `branch-identity-${threadSuffix}`,
  profile: "advisor",
  cwd: workerRepo
});
await waitRun(branchThread.run_id, { timeoutMs: 10000 });
const branchThreadEntry = listThreads({ cwd: workerRepo, includeArchived: true }).threads.find(
  (thread) => thread.thread_id === branchThread.thread_id
);
assert.equal(branchThreadEntry.workspace.kind, "git");
assert.equal(branchThreadEntry.workspace_match, true);
assert.throws(
  () => sendThread({ thread_id: branchThread.thread_id, prompt: "Wrong worktree.", cwd: bridgeRoot }),
  /belongs to cwd/u
);
assert.equal(spawnSync("git", ["switch", "-q", "-c", "parallel-agent-branch"], { cwd: workerRepo }).status, 0);
const movedBranchEntry = listThreads({ cwd: workerRepo, includeArchived: true }).threads.find(
  (thread) => thread.thread_id === branchThread.thread_id
);
assert.equal(movedBranchEntry.workspace_match, false);
assert.equal(movedBranchEntry.resumable, false);
assert.throws(
  () => sendThread({ thread_id: branchThread.thread_id, prompt: "Wrong branch.", cwd: workerRepo }),
  /belongs to Git ref/u
);
const externalSymlinkDir = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-symlink-"));
const externalSymlinkTarget = path.join(externalSymlinkDir, "target.txt");
fs.symlinkSync(externalSymlinkTarget, path.join(workerRepo, "link.txt"));
assert.throws(
  () => startRun({ prompt: "No symlink escapes.", profile: "worker", writeFiles: ["link.txt"], cwd: workerRepo }),
  /cannot contain symlinks/u
);
fs.rmSync(path.join(workerRepo, "link.txt"));
fs.rmSync(externalSymlinkDir, { recursive: true, force: true });
assert.throws(
  () => startRun({ prompt: "Worker without scope.", profile: "worker", cwd: workerRepo }),
  /requires writeFiles/u
);
const workerRun = startRun({
  prompt: "WRITE_ALLOWED_BRIDGE",
  profile: "worker",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const workerReport = await waitRun(workerRun.run_id, { timeoutMs: 10000 });
assert.equal(workerReport.write_scope.status, "passed");
assert.equal(
  workerReport.write_scope.enforcement,
  "prompt_boundary_plus_git_and_filesystem_postflight"
);
assert.deepEqual(workerReport.write_scope.changed_files, ["allowed.txt"]);
assert.deepEqual(workerReport.write_scope.out_of_scope_files, []);
assert.equal(workerReport.agent_behavior.write_scope_status, "passed");
assert.match(fs.readFileSync(path.join(workerRepo, "allowed.txt"), "utf8"), /changed by fake Claude/u);
assert.throws(
  () =>
    startRun({
      prompt: "Worker must not overlap dirty user edits.",
      profile: "worker",
      writeFiles: ["allowed.txt"],
      cwd: workerRepo
    }),
  /pre-existing dirty files/u
);
assert.equal(spawnSync("git", ["restore", "allowed.txt"], { cwd: workerRepo }).status, 0);
const ignoredWorkerRun = startRun({
  prompt: "WRITE_IGNORED_BRIDGE",
  profile: "worker",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const ignoredWorkerReport = await waitRun(ignoredWorkerRun.run_id, { timeoutMs: 10000 });
assert.equal(ignoredWorkerReport.write_scope.status, "failed");
assert.ok(ignoredWorkerReport.write_scope.out_of_scope_files.includes("ignored.txt"));
fs.rmSync(path.join(workerRepo, "ignored.txt"), { force: true });
const violatingWorkerRun = startRun({
  prompt: "WRITE_OUT_OF_SCOPE_BRIDGE",
  profile: "worker",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const violatingWorkerReport = await waitRun(violatingWorkerRun.run_id, { timeoutMs: 10000 });
assert.equal(violatingWorkerReport.write_scope.status, "failed");
assert.deepEqual(violatingWorkerReport.write_scope.out_of_scope_files, ["outside.txt"]);
assert.ok(violatingWorkerReport.warnings.some((warning) => warning.kind === "write_scope_violation"));
assert.equal(spawnSync("git", ["restore", "outside.txt"], { cwd: workerRepo }).status, 0);
const renameWorkerRun = startRun({
  prompt: "RENAME_OUTSIDE_BRIDGE",
  profile: "worker",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const renameWorkerReport = await waitRun(renameWorkerRun.run_id, { timeoutMs: 10000 });
assert.equal(renameWorkerReport.write_scope.status, "failed");
assert.ok(renameWorkerReport.write_scope.out_of_scope_files.includes("outside.txt"));
assert.equal(spawnSync("git", ["restore", "allowed.txt", "outside.txt"], { cwd: workerRepo }).status, 0);
const committingWorkerRun = startRun({
  prompt: "COMMIT_ALLOWED_BRIDGE",
  profile: "worker",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const committingWorkerReport = await waitRun(committingWorkerRun.run_id, { timeoutMs: 10000 });
assert.equal(committingWorkerReport.write_scope.status, "failed");
assert.equal(committingWorkerReport.write_scope.head_changed, true);
assert.ok(committingWorkerReport.write_scope.violations.includes("git_head_changed"));
fs.writeFileSync(path.join(workerRepo, "allowed.txt"), "pre-existing user edit\n");
const unrestrictedRun = startRun({
  prompt: "WRITE_OUT_OF_SCOPE_BRIDGE",
  profile: "unrestricted",
  cwd: workerRepo
});
const unrestrictedReport = await waitRun(unrestrictedRun.run_id, { timeoutMs: 10000 });
assert.equal(unrestrictedReport.write_scope.status, "observed");
assert.deepEqual(unrestrictedReport.write_scope.changed_files, ["outside.txt"]);
assert.equal(unrestrictedReport.write_scope.out_of_scope_files.length, 0);
fs.rmSync(workerRepo, { recursive: true, force: true });

assert.throws(
  () =>
    startRun({
      prompt: "This permission combination must fail before spawning.",
      profile: "read-only",
      cwd: bridgeRoot,
      allowDangerouslySkipPermissions: true
    }),
  /cannot enable permission bypass/u
);
const newCliControlsRun = startRun({
  prompt: "Return exactly BRIDGE_OK.",
  profile: "read-only",
  cwd: bridgeRoot,
  permissionMode: "plan",
  jsonSchema: { type: "object", properties: { ok: { type: "boolean" } }, required: ["ok"] },
  agent: "reviewer",
  agents: { reviewer: { description: "Reviews bridge smoke runs", prompt: "Review only." } },
  pluginUrl: ["https://example.invalid/plugin.zip"],
  brief: true,
  file: ["file_abc:doc.txt"],
  inputFormat: "text",
  replayUserMessages: true
});
const newCliControlsReport = await waitRun(newCliControlsRun.run_id, { timeoutMs: 10000 });
const newCliControlsCommand = JSON.parse(fs.readFileSync(newCliControlsReport.files.command, "utf8"));
assert.ok(newCliControlsCommand.args.includes("--permission-mode"));
assert.equal(newCliControlsCommand.args.filter((value) => value === "--permission-mode").length, 1);
assert.ok(newCliControlsCommand.args.includes("--json-schema"));
assert.ok(newCliControlsCommand.args.includes("--agent"));
assert.ok(newCliControlsCommand.args.includes("--agents"));
assert.ok(newCliControlsCommand.args.includes("--plugin-url"));
assert.equal(newCliControlsCommand.args.includes("--allow-dangerously-skip-permissions"), false);
assert.ok(newCliControlsCommand.args.includes("--brief"));
assert.ok(newCliControlsCommand.args.includes("--file"));
assert.ok(newCliControlsCommand.args.includes("--input-format"));
assert.ok(newCliControlsCommand.args.includes("--replay-user-messages"));

const orphanId = `orphan-no-fingerprint-${Date.now()}`;
writeSyntheticState(orphanId, { started_at: new Date(Date.now() - 5000).toISOString() });
const orphanReport = cliJson(["result", "--run-id", orphanId]);
assert.equal(orphanReport.status, "orphaned");
assert.match(orphanReport.orphan_reason, /fingerprint/u);
const orphanKill = cliJson(["kill", "--run-id", orphanId]);
assert.equal(orphanKill.killed, false);

const fakeParentPidFile = path.join(runsDir, "_fake-claude-parent.pid");
const fakeChildPidFile = path.join(runsDir, "_fake-claude-child.pid");
fs.rmSync(fakeParentPidFile, { force: true });
fs.rmSync(fakeChildPidFile, { force: true });
process.env.FAKE_CLAUDE_PID_FILE = fakeParentPidFile;
process.env.FAKE_CLAUDE_CHILD_PID_FILE = fakeChildPidFile;
const longRun = startRun({
  prompt: "SLEEP_BRIDGE",
  profile: "normal",
  cwd: bridgeRoot
});
await waitForFile(fakeParentPidFile);
await waitForFile(fakeChildPidFile);
const longState = JSON.parse(fs.readFileSync(path.join(longRun.log_dir, "state.json"), "utf8"));
longState.started_at = new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString();
fs.writeFileSync(path.join(longRun.log_dir, "state.json"), JSON.stringify(longState, null, 2));
const cleanupWhileActive = cleanupRuns({ olderThanDays: 14 });
assert.ok(cleanupWhileActive.skipped_active.some((candidate) => candidate.run_id === longRun.run_id));
const longRunParentPid = readPidFile(fakeParentPidFile);
const longRunChildPid = readPidFile(fakeChildPidFile);
await new Promise((resolve) => setTimeout(resolve, 250));
const restartedLongReport = cliJson(["result", "--run-id", longRun.run_id]);
assert.equal(restartedLongReport.status, "running_orphaned");
assert.equal(restartedLongReport.managed, false);
const restartedLongKill = cliJson(["kill", "--run-id", longRun.run_id]);
assert.equal(restartedLongKill.killed, true);
const localKilledReport = await waitRun(longRun.run_id, { timeoutMs: 10000 });
assert.equal(localKilledReport.status, "killed");
assert.equal(localKilledReport.managed, false);
await waitForPidExit(longRunParentPid, "Claude parent");
await waitForPidExit(longRunChildPid, "Claude child");

fs.rmSync(fakeParentPidFile, { force: true });
fs.rmSync(fakeChildPidFile, { force: true });
const daemonRun = startRun({
  prompt: "DAEMON_BRIDGE",
  profile: "normal",
  cwd: bridgeRoot
});
await waitForFile(fakeChildPidFile);
const daemonChildPid = readPidFile(fakeChildPidFile);
const daemonReport = await waitRun(daemonRun.run_id, { timeoutMs: 10000 });
assert.equal(daemonReport.status, "running_orphaned");
const daemonRestartedReport = cliJson(["result", "--run-id", daemonRun.run_id]);
assert.equal(daemonRestartedReport.status, "running_orphaned");
const daemonKill = cliJson(["kill", "--run-id", daemonRun.run_id]);
assert.equal(daemonKill.killed, true);
await waitForPidExit(daemonChildPid, "Claude daemon child");
const daemonKilledReport = cliJson(["result", "--run-id", daemonRun.run_id]);
assert.equal(daemonKilledReport.status, "killed");

fs.rmSync(fakeParentPidFile, { force: true });
fs.rmSync(fakeChildPidFile, { force: true });
const stubbornRun = startRun({
  prompt: "IGNORE_TERM_BRIDGE",
  profile: "normal",
  cwd: bridgeRoot
});
await waitForFile(fakeParentPidFile);
await waitForFile(fakeChildPidFile);
const stubbornParentPid = readPidFile(fakeParentPidFile);
const stubbornChildPid = readPidFile(fakeChildPidFile);
await new Promise((resolve) => setTimeout(resolve, 250));
const stubbornSoftKill = cliJson(["kill", "--run-id", stubbornRun.run_id]);
assert.equal(stubbornSoftKill.killed, true);
const stubbornStillKilling = cliJson(["result", "--run-id", stubbornRun.run_id]);
assert.equal(stubbornStillKilling.status, "killing");
const stubbornHardKill = cliJson(["kill", "--run-id", stubbornRun.run_id]);
assert.equal(stubbornHardKill.killed, true);
await waitForPidExit(stubbornParentPid, "Claude stubborn parent");
await waitForPidExit(stubbornChildPid, "Claude stubborn child");
const stubbornKilledReport = await waitRun(stubbornRun.run_id, { timeoutMs: 10000 });
assert.equal(stubbornKilledReport.status, "killed");
delete process.env.FAKE_CLAUDE_PID_FILE;
delete process.env.FAKE_CLAUDE_CHILD_PID_FILE;
fs.rmSync(fakeParentPidFile, { force: true });
fs.rmSync(fakeChildPidFile, { force: true });

if (spawnSync("tmux", ["-V"], { encoding: "utf8" }).status === 0) {
  const tmuxEnvCaptureFile = path.join(runsDir, "_fake-claude-tmux-env.json");
  fs.rmSync(tmuxEnvCaptureFile, { force: true });
  process.env.FAKE_CLAUDE_ENV_CAPTURE = tmuxEnvCaptureFile;
  process.env.ANTHROPIC_API_KEY = "must-not-leak-via-tmux";
  process.env.CLAUDE_API_KEY = "must-not-leak-via-tmux";
  const tmuxRun = startRun({
    prompt: "Return exactly BRIDGE_OK via tmux.",
    profile: "normal",
    cwd: bridgeRoot,
    useTmux: true
  });
  trackTmuxSession(tmuxRun);
  assert.equal(tmuxRun.use_tmux, true);
  assert.ok(tmuxRun.tmux_session);
  const tmuxReport = await waitRun(tmuxRun.run_id, { timeoutMs: 10000 });
  assert.equal(tmuxReport.status, "completed");
  assert.equal(tmuxReport.use_tmux, true);
  assert.equal(tmuxReport.managed, false);
  assert.match(tmuxReport.final_output_summary, /BRIDGE_OK/u);
  assert.match(tmuxReport.chat_relay.text, /BRIDGE_OK/u);
  assert.ok(tmuxReport.files.tmux_pane);
  assert.match(fs.readFileSync(tmuxReport.files.stdout, "utf8"), /BRIDGE_OK/u);
  assert.match(fs.readFileSync(tmuxReport.files.tmux_pane, "utf8"), /BRIDGE_OK/u);
  assert.deepEqual(JSON.parse(fs.readFileSync(tmuxEnvCaptureFile, "utf8")), {
    ANTHROPIC_API_KEY: null,
    CLAUDE_API_KEY: null
  });
  assert.equal(tmuxReport.session_id, tmuxRun.session_id);
  delete process.env.FAKE_CLAUDE_ENV_CAPTURE;
  delete process.env.ANTHROPIC_API_KEY;
  delete process.env.CLAUDE_API_KEY;
  await new Promise((resolve) => setTimeout(resolve, 250));
  assert.notEqual(
    spawnSync("tmux", ["has-session", "-t", tmuxRun.tmux_session], { encoding: "utf8" }).status,
    0
  );

  fs.rmSync(fakeParentPidFile, { force: true });
  fs.rmSync(fakeChildPidFile, { force: true });
  process.env.FAKE_CLAUDE_PID_FILE = fakeParentPidFile;
  process.env.FAKE_CLAUDE_CHILD_PID_FILE = fakeChildPidFile;
  const liveTmuxRun = startRun({
    prompt: "SLEEP_BRIDGE",
    profile: "normal",
    cwd: bridgeRoot,
    useTmux: true
  });
  trackTmuxSession(liveTmuxRun);
  await waitForFile(fakeParentPidFile);
  await waitForFile(fakeChildPidFile);
  const liveParentPid = readPidFile(fakeParentPidFile);
  const liveChildPid = readPidFile(fakeChildPidFile);
  await new Promise((resolve) => setTimeout(resolve, 500));
  const livePeek = peekRun(liveTmuxRun.run_id, { cursor: 0 });
  assert.equal(livePeek.tmux_capture.available, true);
  assert.match(livePeek.tmux_capture.text, /Reading context/u);
  assert.equal(livePeek.activity.tmux_capture_available, true);
  const liveKill = killRun(liveTmuxRun.run_id);
  assert.equal(liveKill.killed, true);
  await waitForPidExit(liveParentPid, "Claude tmux parent");
  await waitForPidExit(liveChildPid, "Claude tmux child");
  const liveKilledReport = resultRun(liveTmuxRun.run_id);
  assert.equal(liveKilledReport.status, "killed");
  delete process.env.FAKE_CLAUDE_PID_FILE;
  delete process.env.FAKE_CLAUDE_CHILD_PID_FILE;
  fs.rmSync(fakeParentPidFile, { force: true });
  fs.rmSync(fakeChildPidFile, { force: true });
}

const fixtureDir = path.join(runsDir, "_smoke-fixtures");
fs.mkdirSync(fixtureDir, { recursive: true });
const fixtureSkill = path.join(fixtureDir, "sample-skill.md");
fs.writeFileSync(fixtureSkill, "# Sample Skill\n\nRead marker: SAMPLE_SKILL_MARKER\n");
const audit = await auditSkill({
  skillPath: fixtureSkill,
  cwd: bridgeRoot,
  timeoutMs: 10000
});
assert.equal(audit.evidence, "passed");

const nestedStreamAudit = await auditSkill({
  skillPath: fixtureSkill,
  prompt: "NESTED_TOOL_EVENTS",
  cwd: bridgeRoot,
  timeoutMs: 10000
});
assert.equal(nestedStreamAudit.evidence, "passed");
assert.equal(nestedStreamAudit.read_attempts.length, 1);
assert.equal(nestedStreamAudit.matching_events.length, 1);

const selfReportAudit = await auditSkill({
  skillPath: fixtureSkill,
  prompt: "SELF_REPORT_ONLY",
  cwd: bridgeRoot,
  timeoutMs: 10000
});
assert.equal(selfReportAudit.evidence, "unknown");

const wrongPathAudit = await auditSkill({
  skillPath: fixtureSkill,
  prompt: "WRONG_TOOL_PATH",
  cwd: bridgeRoot,
  timeoutMs: 10000
});
assert.equal(wrongPathAudit.evidence, "failed");

const failedReadAudit = await auditSkill({
  skillPath: fixtureSkill,
  prompt: "READ_ERROR",
  cwd: bridgeRoot,
  timeoutMs: 10000
});
assert.equal(failedReadAudit.evidence, "failed");
assert.equal(failedReadAudit.read_attempts.length, 1);
assert.equal(failedReadAudit.matching_events.length, 0);

const timeoutAudit = await auditSkill({
  skillPath: fixtureSkill,
  prompt: "SLEEP_BRIDGE",
  cwd: bridgeRoot,
  timeoutMs: 50
});
assert.equal(timeoutAudit.evidence, "timed_out");
assert.equal(timeoutAudit.tail_terminal, true);
assert.equal(timeoutAudit.run.status, "killed");

const oldRunId = `old-cleanup-${Date.now()}`;
const old = writeSyntheticState(oldRunId, {
  pid: null,
  status: "completed",
  started_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString()
});
const oldTime = new Date(Date.now() - 20 * 24 * 60 * 60 * 1000);
fs.utimesSync(old.runDir, oldTime, oldTime);
const corruptRunId = `corrupt-cleanup-${Date.now()}`;
const corruptRunDir = path.join(runsDir, corruptRunId);
fs.mkdirSync(corruptRunDir, { recursive: true });
fs.writeFileSync(path.join(corruptRunDir, "state.json"), "{not-json");
fs.utimesSync(corruptRunDir, oldTime, oldTime);
const corruptReportRunId = `corrupt-report-cleanup-${Date.now()}`;
const corruptReportRunDir = path.join(runsDir, corruptReportRunId);
fs.mkdirSync(corruptReportRunDir, { recursive: true });
fs.writeFileSync(path.join(corruptReportRunDir, "report.json"), "{not-json");
fs.utimesSync(corruptReportRunDir, oldTime, oldTime);
const terminalLiveRunId = `terminal-live-cleanup-${Date.now()}`;
const terminalLive = writeSyntheticState(terminalLiveRunId, {
  pid: null,
  status: "completed",
  started_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString()
});
const terminalLiveProcess = spawn(
  process.execPath,
  ["-e", "setInterval(() => {}, 1000)", terminalLive.runDir],
  { detached: true, stdio: "ignore" }
);
terminalLiveProcess.unref();
const terminalLiveState = JSON.parse(fs.readFileSync(terminalLive.files.state, "utf8"));
terminalLiveState.pid = terminalLiveProcess.pid;
terminalLiveState.process_group_pid = terminalLiveProcess.pid;
fs.writeFileSync(terminalLive.files.state, JSON.stringify(terminalLiveState, null, 2));
fs.utimesSync(terminalLive.runDir, oldTime, oldTime);
await new Promise((resolve) => setTimeout(resolve, 100));
const cleanupDryRun = cleanupRuns({ olderThanDays: 14 });
assert.ok(cleanupDryRun.dry_run);
assert.ok(cleanupDryRun.candidates.some((candidate) => candidate.run_id === oldRunId));
assert.ok(cleanupDryRun.skipped_unknown.some((candidate) => candidate.run_id === corruptRunId));
assert.ok(cleanupDryRun.skipped_unknown.some((candidate) => candidate.run_id === corruptReportRunId));
assert.ok(cleanupDryRun.skipped_active.some((candidate) => candidate.run_id === terminalLiveRunId));
assert.ok(fs.existsSync(old.runDir));
const cleanupConfirmed = cliJson(["cleanup", "--days", "14", "--confirm"]);
assert.ok(cleanupConfirmed.candidates.some((candidate) => candidate.run_id === oldRunId));
assert.equal(fs.existsSync(old.runDir), false);
assert.equal(fs.existsSync(corruptRunDir), true);
assert.equal(fs.existsSync(corruptReportRunDir), true);
assert.equal(fs.existsSync(terminalLive.runDir), true);
process.kill(-terminalLiveProcess.pid, "SIGKILL");
await waitForPidExit(terminalLiveProcess.pid, "terminal-state cleanup fixture");
fs.rmSync(corruptRunDir, { recursive: true, force: true });
fs.rmSync(corruptReportRunDir, { recursive: true, force: true });
fs.rmSync(terminalLive.runDir, { recursive: true, force: true });

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [path.join(bridgeRoot, "src", "server.js")],
  env: {
    ...process.env,
    CLAUDE_BRIDGE_CLAUDE_BIN: fakeClaude
  }
});
const client = new Client({ name: "claude-bridge-smoke", version: "0.1.0" });
await client.connect(transport);
const tools = await client.listTools();
const toolNames = tools.tools.map((tool) => tool.name);
assert.ok(toolNames.includes("claude_run"));
assert.ok(toolNames.includes("claude_observe"));
assert.ok(toolNames.includes("claude_cleanup_runs"));
assert.ok(toolNames.includes("claude_thread_start"));
assert.ok(toolNames.includes("claude_thread_send"));
assert.ok(toolNames.includes("claude_threads"));
assert.ok(toolNames.includes("claude_thread_archive"));
assert.equal(toolNames.includes("claude_subagent_run"), false);
assert.equal(toolNames.includes("claude_agents"), false);
const doctorTool = await client.callTool({ name: "claude_doctor", arguments: {} });
assert.ok(doctorTool.content?.[0]?.text?.includes("stream_json_supported"));
const badRunTool = await client.callTool({
  name: "claude_run",
  arguments: {
    prompt: "This should fail inside the handler.",
    profile: "missing-profile",
    cwd: bridgeRoot
  }
});
assert.equal(badRunTool.isError, true);
assert.match(badRunTool.content?.[0]?.text || "", /Unknown Claude bridge profile/u);
const mcpRun = await client.callTool({
  name: "claude_run",
  arguments: {
    prompt: "Return exactly BRIDGE_OK from MCP.",
    profile: "normal",
    cwd: bridgeRoot
  }
});
const mcpRunPayload = JSON.parse(mcpRun.content[0].text);
assert.ok(mcpRunPayload.run_id);
const mcpWait = await client.callTool({
  name: "claude_wait",
  arguments: {
    run_id: mcpRunPayload.run_id,
    timeoutMs: 10000
  }
});
const mcpWaitPayload = JSON.parse(mcpWait.content[0].text);
assert.equal(mcpWaitPayload.status, "completed");
assert.match(mcpWaitPayload.final_output_summary, /BRIDGE_OK/);
assert.match(mcpWaitPayload.chat_relay.text, /BRIDGE_OK/);
const mcpPeek = await client.callTool({
  name: "claude_peek",
  arguments: {
    run_id: mcpRunPayload.run_id,
    cursor: 0
  }
});
const mcpPeekPayload = JSON.parse(mcpPeek.content[0].text);
assert.ok(mcpPeekPayload.next_cursor > 0);
assert.match(mcpPeekPayload.chat_relay.text, /BRIDGE_OK/);
assert.ok(mcpPeekPayload.activity);
assert.ok(Array.isArray(mcpPeekPayload.activity.recent_text));
const mcpObserve = await client.callTool({
  name: "claude_observe",
  arguments: {
    run_id: mcpRunPayload.run_id,
    cursor: 0
  }
});
const mcpObservePayload = JSON.parse(mcpObserve.content[0].text);
assert.ok(mcpObservePayload.activity);
assert.match(mcpObservePayload.activity.note, /Observable trace only/u);
const mcpThreadStart = await client.callTool({
  name: "claude_thread_start",
  arguments: {
    prompt: "Return exactly BRIDGE_OK from a persistent MCP thread.",
    topic: `mcp-thread-${threadSuffix}`,
    profile: "advisor",
    cwd: bridgeRoot
  }
});
const mcpThreadPayload = JSON.parse(mcpThreadStart.content[0].text);
assert.ok(mcpThreadPayload.thread_id);
const mcpThreadWait = await client.callTool({
  name: "claude_wait",
  arguments: { run_id: mcpThreadPayload.run_id, timeoutMs: 10000 }
});
assert.equal(JSON.parse(mcpThreadWait.content[0].text).status, "completed");
const mcpThreads = await client.callTool({
  name: "claude_threads",
  arguments: { cwd: bridgeRoot, includeArchived: true }
});
assert.ok(JSON.parse(mcpThreads.content[0].text).threads.some((thread) => thread.thread_id === mcpThreadPayload.thread_id));
const mcpCleanup = await client.callTool({
  name: "claude_cleanup_runs",
  arguments: { olderThanDays: 14 }
});
assert.ok(mcpCleanup.content?.[0]?.text?.includes("dry_run"));
await client.close();

const directResult = resultRun(started.run_id);
assert.equal(directResult.status, "completed");
assert.equal(directResult.managed, false);
const directKill = killRun(started.run_id);
assert.equal(directKill.killed, false);

process.stdout.write("claude-bridge smoke ok\n");
