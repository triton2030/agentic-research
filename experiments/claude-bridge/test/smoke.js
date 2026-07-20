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
  CLAUDE_WIRE_LIMITS,
  archiveThread,
  auditSkill,
  cleanupRuns,
  doctor,
  killRun,
  listThreads,
  peekRun,
  profiles,
  relayRun,
  reportRun,
  resultRun: resultControl,
  sendThread,
  startRun,
  startThread,
  waitRun: waitControl
} = await import("../src/runner.js");

async function waitRun(runId, options) {
  const control = await waitControl(runId, options);
  const report = reportRun(runId);
  if (control.timed_out) report.timed_out = true;
  return report;
}

function resultRun(runId) {
  return reportRun(runId);
}

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
assert.equal(doctorReport.auth.method, "claude.ai");
assert.equal(doctorReport.auth.subscription_type, "max");
assert.equal(doctorReport.billing.mode, "subscription_oauth");
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
    ["--effort", "xhigh"],
    `${profileName} must use xhigh effort`
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
const authOverrideEnv = [
  "ANTHROPIC_AUTH_TOKEN",
  "ANTHROPIC_API_KEY",
  "ANTHROPIC_BASE_URL",
  "CLAUDE_API_KEY",
  "CLAUDE_CODE_OAUTH_TOKEN",
  "CLAUDE_CODE_USE_BEDROCK",
  "CLAUDE_CODE_USE_VERTEX",
  "CLAUDE_CODE_USE_FOUNDRY"
];
const modelOverrideEnv = [
  "ANTHROPIC_DEFAULT_FABLE_MODEL",
  "ANTHROPIC_DEFAULT_OPUS_MODEL",
  "ANTHROPIC_DEFAULT_SONNET_MODEL",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL",
  "CLAUDE_CODE_SUBAGENT_MODEL"
];
for (const name of [...authOverrideEnv, ...modelOverrideEnv]) process.env[name] = "should-not-leak";
const started = startRun({
  prompt: "Return exactly BRIDGE_OK.",
  profile: "normal",
  cwd: bridgeRoot
});
assert.ok(started.run_id);
assert.ok(fs.existsSync(started.log_dir));

const peek = peekRun(started.run_id);
assert.equal(peek.run_id, started.run_id);
assert.ok(peek.next_cursor >= peek.cursor);
assert.equal(peek._envelope.schema, "claude-bridge.control.v2");

const report = await waitRun(started.run_id, { timeoutMs: 10000 });
const startedCommand = JSON.parse(fs.readFileSync(report.files.command, "utf8"));
assert.equal(startedCommand.args.filter((value) => value === "--model").length, 1);
assert.equal(startedCommand.args.filter((value) => value === "--effort").length, 1);
assert.equal(startedCommand.args.filter((value) => value === "--permission-mode").length, 1);
assert.equal(startedCommand.args.filter((value) => value === "--append-subagent-system-prompt").length, 1);
const fakeEnvCapture = JSON.parse(fs.readFileSync(fakeEnvCaptureFile, "utf8"));
assert.equal(startedCommand.env.subscription_billing_guard.mode, "subscription_oauth");
assert.deepEqual(
  startedCommand.env.subscription_billing_guard.auth_env_overrides_stripped.sort(),
  [...authOverrideEnv].sort()
);
assert.deepEqual(startedCommand.env.model_env_overrides_stripped.sort(), [...modelOverrideEnv].sort());
assert.deepEqual(
  fakeEnvCapture,
  Object.fromEntries([...authOverrideEnv, ...modelOverrideEnv].map((name) => [name, null]))
);
delete process.env.FAKE_CLAUDE_ENV_CAPTURE;
for (const name of [...authOverrideEnv, ...modelOverrideEnv]) delete process.env[name];
assert.equal(report.status, "completed");
assert.equal(report.billing.mode, "subscription_oauth");
assert.equal(report.model, "opus");
assert.equal(report.resolved_model, "claude-opus-4-8");
assert.deepEqual(report.resolved_model_history, ["claude-opus-4-8"]);
assert.equal(report.model_switch_observed, false);
assert.deepEqual(report.model_env_overrides_stripped.sort(), [...modelOverrideEnv].sort());
assert.equal(report.session_id, started.session_id);
assert.equal(report.session_observed, true);
assert.equal(report.managed, false);
assert.equal(report.final_output.full_text_file, report.files.final_output);
assert.match(fs.readFileSync(report.files.final_output, "utf8"), /BRIDGE_OK/);
assert.match(relayRun(started.run_id).text, /BRIDGE_OK/);
assert.ok(fs.existsSync(report.files.state));
assert.ok(report.activity.recent_text.some((event) => /BRIDGE_OK/u.test(event.text)));

const compactPollingRun = startRun({
  prompt: "POLL_BRIDGE LONG_OUTPUT_BRIDGE",
  profile: "normal",
  cwd: bridgeRoot
});
let compactPollingBytes = 0;
for (let index = 0; index < 10; index += 1) {
  const timeoutControl = await waitControl(compactPollingRun.run_id, { timeoutMs: 15 });
  assert.equal(timeoutControl.timed_out, true);
  assert.equal(timeoutControl.terminal, false);
  assert.equal(Object.hasOwn(timeoutControl, "activity"), false);
  assert.equal(Object.hasOwn(timeoutControl, "command"), false);
  assert.equal(Object.hasOwn(timeoutControl, "files"), false);
  const timeoutBytes = Buffer.byteLength(JSON.stringify(timeoutControl), "utf8");
  assert.ok(timeoutBytes < 1024, `timeout control used ${timeoutBytes} bytes`);
  compactPollingBytes += timeoutBytes;
}
const compactTerminal = await waitControl(compactPollingRun.run_id, { timeoutMs: 10000 });
const compactTerminalBytes = Buffer.byteLength(JSON.stringify(compactTerminal), "utf8");
assert.ok(compactTerminalBytes < 4096, `terminal control used ${compactTerminalBytes} bytes`);
compactPollingBytes += compactTerminalBytes;
assert.equal(compactTerminal.status, "completed");
assert.equal(compactTerminal.terminal, true);
assert.ok(compactPollingBytes < 7000, `compact polling used ${compactPollingBytes} bytes`);

const compactReport = reportRun(compactPollingRun.run_id);
for (const removedDuplicate of ["events", "milestones", "chat_relay", "final_output_summary", "agent_behavior"]) {
  assert.equal(Object.hasOwn(compactReport, removedDuplicate), false, `${removedDuplicate} must stay off report v2`);
}
const reportFinalText = fs.readFileSync(compactReport.final_output.full_text_file, "utf8");
let relayCursor = 0;
let relayedText = "";
let relayChunks = 0;
while (relayCursor < reportFinalText.length) {
  const relay = relayRun(compactPollingRun.run_id, { cursor: relayCursor, maxChars: 8000 });
  assert.equal(relay.cursor, relayCursor);
  assert.ok(relay.text.length <= 8000);
  relayedText += relay.text;
  relayCursor = relay.next_cursor;
  relayChunks += 1;
}
assert.equal(relayedText, reportFinalText);
assert.equal(relayChunks, 3);
const relayConsumerA = relayRun(compactPollingRun.run_id, { cursor: 0, maxChars: 120 });
const relayConsumerB = relayRun(compactPollingRun.run_id, { cursor: 0, maxChars: 120 });
assert.equal(relayConsumerA.text, relayConsumerB.text);
assert.equal(relayConsumerA.next_cursor, relayConsumerB.next_cursor);
const noDelta = peekRun(compactPollingRun.run_id, { cursor: compactTerminal.event_count });
assert.equal(noDelta.new_events, 0);
assert.equal(Object.hasOwn(noDelta, "updates"), false);

const failedCompactRun = startRun({
  prompt: "FAIL_BRIDGE",
  profile: "normal",
  cwd: bridgeRoot
});
const failedCompactControl = await waitControl(failedCompactRun.run_id, { timeoutMs: 10000 });
assert.equal(failedCompactControl.status, "failed");
assert.equal(failedCompactControl.result.termination.exit_code, 7);
assert.match(failedCompactControl.result.termination.detail, /FAKE_BRIDGE_FAILURE/u);

const legacyUnknownRunId = `legacy-completed-unknown-${Date.now()}`;
const legacyUnknownDir = path.join(runsDir, legacyUnknownRunId);
fs.mkdirSync(legacyUnknownDir, { recursive: true });
const legacyUnknownFiles = {
  prompt: path.join(legacyUnknownDir, "prompt.txt"),
  profile: path.join(legacyUnknownDir, "profile.json"),
  command: path.join(legacyUnknownDir, "command.json"),
  events: path.join(legacyUnknownDir, "events.ndjson"),
  stdout: path.join(legacyUnknownDir, "stdout.log"),
  stderr: path.join(legacyUnknownDir, "stderr.log"),
  debug: path.join(legacyUnknownDir, "debug.log"),
  final_output: path.join(legacyUnknownDir, "final-output.md"),
  report: path.join(legacyUnknownDir, "report.json"),
  state: path.join(legacyUnknownDir, "state.json")
};
fs.writeFileSync(legacyUnknownFiles.events, `${JSON.stringify({ type: "result", text: "LEGACY_BRIDGE_OK" })}\n`);
fs.writeFileSync(
  legacyUnknownFiles.report,
  JSON.stringify({
    run_id: legacyUnknownRunId,
    profile: "normal",
    model: "opus",
    status: "running",
    cwd: bridgeRoot,
    files: legacyUnknownFiles
  })
);
const legacyUnknownControl = resultControl(legacyUnknownRunId);
assert.equal(legacyUnknownControl.status, "completed_unknown");
assert.equal(legacyUnknownControl.terminal, true);
assert.ok(legacyUnknownControl.warnings.kinds.includes("legacy_terminal_status_unknown"));
assert.match(relayRun(legacyUnknownRunId).text, /LEGACY_BRIDGE_OK/u);

const cliAdvisorRun = cliJson([
  "run",
  "--prompt",
  "Return BRIDGE_OK through the CLI advisor path.",
  "--profile",
  "advisor",
  "--cwd",
  bridgeRoot
]);
const cliAdvisorReport = await waitRun(cliAdvisorRun.run_id, { timeoutMs: 10000 });
assert.equal(cliAdvisorReport.status, "completed");
assert.equal(cliAdvisorReport.write_scope.status, "passed");

process.env.FAKE_CLAUDE_AUTH_METHOD = "console";
assert.throws(
  () => startRun({ prompt: "PAYG auth must be rejected.", profile: "advisor", cwd: bridgeRoot }),
  /requires Claude\.ai plan OAuth/u
);
assert.equal(doctor().ready_for_live_runs, false);
delete process.env.FAKE_CLAUDE_AUTH_METHOD;

process.env.FAKE_CLAUDE_API_PROVIDER = "gateway";
assert.throws(
  () => startRun({ prompt: "Gateway auth must be rejected.", profile: "advisor", cwd: bridgeRoot }),
  /claude\.ai\/gateway\/max/u
);
assert.equal(doctor().ready_for_live_runs, false);
delete process.env.FAKE_CLAUDE_API_PROVIDER;

const helperSettingsCwd = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-helper-settings-"));
fs.mkdirSync(path.join(helperSettingsCwd, ".claude"));
fs.writeFileSync(
  path.join(helperSettingsCwd, ".claude", "settings.json"),
  JSON.stringify({ apiKeyHelper: "/tmp/not-executed-helper" })
);
assert.throws(
  () => startRun({ prompt: "apiKeyHelper must be rejected.", profile: "advisor", cwd: helperSettingsCwd }),
  /refuses apiKeyHelper settings/u
);
fs.writeFileSync(
  path.join(helperSettingsCwd, ".claude", "settings.json"),
  JSON.stringify({ env: { ANTHROPIC_API_KEY: "not-used" } })
);
assert.throws(
  () => startRun({ prompt: "Settings API key must be rejected.", profile: "advisor", cwd: helperSettingsCwd }),
  /refuses auth\/provider overrides in settings/u
);
fs.writeFileSync(
  path.join(helperSettingsCwd, ".claude", "settings.json"),
  JSON.stringify({ env: { ANTHROPIC_DEFAULT_OPUS_MODEL: "claude-opus-old" } })
);
assert.throws(
  () => startRun({ prompt: "Settings model pin must be rejected.", profile: "advisor", cwd: helperSettingsCwd }),
  /refuses model alias redirects in settings/u
);
fs.rmSync(helperSettingsCwd, { recursive: true, force: true });

const syntheticModelRun = startRun({
  prompt: "SYNTHETIC_MODEL_AFTER_INIT",
  profile: "advisor",
  cwd: bridgeRoot
});
const syntheticModelReport = await waitRun(syntheticModelRun.run_id, { timeoutMs: 10000 });
assert.equal(syntheticModelReport.resolved_model, "claude-opus-4-8");

const separateResult = cliJson(["result", "--run-id", started.run_id]);
assert.equal(separateResult.status, "completed");
assert.equal(separateResult.terminal, true);
assert.equal(separateResult.result.output.full_text_file, report.files.final_output);
assert.equal(Object.hasOwn(separateResult, "activity"), false);
assert.equal(Object.hasOwn(separateResult, "command"), false);
const separateRelay = cliJson(["relay", "--run-id", started.run_id]);
assert.match(separateRelay.text, /BRIDGE_OK/);
const separateReport = cliJson(["report", "--run-id", started.run_id]);
assert.equal(separateReport.status, "completed");
assert.ok(separateReport.activity);
const separatePeek = cliJson(["peek", "--run-id", started.run_id, "--cursor", "0"]);
assert.equal(separatePeek.status, "completed");
assert.ok(separatePeek.next_cursor > 0);
assert.ok(Array.isArray(separatePeek.updates));
assert.equal(Object.hasOwn(separatePeek, "activity"), false);

const noMemoryRun = startRun({
  prompt: "Return exactly BRIDGE_OK.",
  profile: "no-memory",
  cwd: bridgeRoot
});
const noMemoryReport = await waitRun(noMemoryRun.run_id, { timeoutMs: 10000 });
const noMemoryCommand = JSON.parse(fs.readFileSync(noMemoryReport.files.command, "utf8"));
assert.equal(noMemoryCommand.env.CLAUDE_CODE_DISABLE_AUTO_MEMORY, "1");

const syntheticExternalRoot = path.resolve(bridgeRoot, "../..");
const syntheticExternalTarget = path.join(syntheticExternalRoot, "README.md");
const scopedExternalRun = startRun({
  prompt: `Target path: ${syntheticExternalTarget}`,
  profile: "advisor",
  cwd: bridgeRoot,
  addDir: syntheticExternalRoot
});
await waitRun(scopedExternalRun.run_id, { timeoutMs: 10000 });
const scopedExternalReport = reportRun(scopedExternalRun.run_id);
assert.deepEqual(scopedExternalReport.add_dirs, [syntheticExternalRoot]);
assert.equal(scopedExternalReport.warnings.some((warning) => warning.type === "boundary_suspicion"), false);
const unscopedExternalRun = startRun({
  prompt: `Target path: ${syntheticExternalTarget}`,
  profile: "advisor",
  cwd: bridgeRoot
});
await waitRun(unscopedExternalRun.run_id, { timeoutMs: 10000 });
const unscopedExternalReport = reportRun(unscopedExternalRun.run_id);
assert.equal(unscopedExternalReport.warnings.some((warning) => warning.type === "boundary_suspicion"), true);

const threadSuffix = `${process.pid}-${Date.now()}`;
const crossFolderRoot = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-cross-folder-"));
const crossFolderCanonicalRoot = fs.realpathSync.native(crossFolderRoot);
const crossFolderOwner = path.join(crossFolderRoot, "owner.txt");
fs.writeFileSync(crossFolderOwner, "CROSS_FOLDER_OWNER_MARKER\n");
const opusThread = startThread({
  prompt: `Target path: ${crossFolderOwner}`,
  topic: `smoke-opus-${threadSuffix}`,
  profile: "advisor",
  cwd: bridgeRoot,
  addDir: crossFolderRoot
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
assert.deepEqual(opusThread.add_dirs, [crossFolderCanonicalRoot]);
assert.deepEqual(opusThread.add_dir_contexts, [
  {
    root: crossFolderCanonicalRoot,
    workspace: {
      kind: "directory",
      worktree_root: crossFolderCanonicalRoot,
      common_dir: null,
      branch: null,
      head: null,
      ref: null
    }
  }
]);
assert.ok(reportRun(opusThread.run_id).activity.recent_paths.includes(crossFolderOwner));
assert.equal(fableThreadReport.session_id, fableThread.thread_id);
assert.equal(fableThreadReport.session_observed, true);
assert.equal(fableThreadReport.model, "fable");
assert.equal(fableThreadReport.effort, "xhigh");
assert.equal(fableThreadReport.resolved_model, "claude-fable-5");
assert.notEqual(opusThread.thread_id, fableThread.thread_id);

const tunedThread = cliJson([
  "thread-start",
  "--prompt",
  "Return BRIDGE_OK for a tuned persistent advisor.",
  "--topic",
  `tuned-thread-${threadSuffix}-bounded`,
  "--profile",
  "advisor",
  "--model",
  "fable",
  "--effort",
  "high",
  "--add-dir",
  crossFolderRoot,
  "--cwd",
  bridgeRoot
]);
const tunedThreadReport = await waitRun(tunedThread.run_id, { timeoutMs: 10000 });
assert.equal(tunedThreadReport.model, "fable");
assert.equal(tunedThreadReport.effort, "high");
assert.equal(tunedThreadReport.resolved_model, "claude-fable-5");
assert.deepEqual(tunedThread.add_dirs, [crossFolderCanonicalRoot]);
const tunedContinuation = cliJson([
  "thread-send",
  "--thread-id",
  tunedThread.thread_id,
  "--prompt",
  "Return BRIDGE_OK from the same tuned thread.",
  "--cwd",
  bridgeRoot
]);
await waitRun(tunedContinuation.run_id, { timeoutMs: 10000 });
assert.deepEqual(tunedContinuation.add_dirs, [crossFolderCanonicalRoot]);

const switchedModelRun = startRun({
  prompt: "MODEL_SWITCH_BRIDGE",
  profile: "fable-advisor",
  cwd: bridgeRoot
});
const switchedModelReport = await waitRun(switchedModelRun.run_id, { timeoutMs: 10000 });
assert.equal(switchedModelReport.initial_resolved_model, "claude-fable-5");
assert.equal(switchedModelReport.resolved_model, "claude-opus-4-8");
assert.deepEqual(switchedModelReport.resolved_model_history, ["claude-fable-5", "claude-opus-4-8"]);
assert.equal(switchedModelReport.model_switch_observed, true);
assert.ok(switchedModelReport.warnings.some((warning) => warning.kind === "model_switch_observed"));

const workerRepo = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-worker-"));
assert.equal(spawnSync("git", ["init", "-q"], { cwd: workerRepo }).status, 0);
assert.equal(spawnSync("git", ["config", "user.email", "bridge@example.invalid"], { cwd: workerRepo }).status, 0);
assert.equal(spawnSync("git", ["config", "user.name", "Claude Bridge Smoke"], { cwd: workerRepo }).status, 0);
fs.writeFileSync(path.join(workerRepo, "allowed.txt"), "baseline\n");
fs.writeFileSync(path.join(workerRepo, "outside.txt"), "baseline\n");
fs.writeFileSync(path.join(workerRepo, ".gitignore"), "ignored.txt\n");
assert.equal(spawnSync("git", ["add", "."], { cwd: workerRepo }).status, 0);
assert.equal(spawnSync("git", ["commit", "-qm", "baseline"], { cwd: workerRepo }).status, 0);
assert.throws(
  () =>
    startRun({
      prompt: "Guarded workers cannot read an unobserved external root.",
      profile: "worker",
      writeFiles: ["allowed.txt"],
      cwd: workerRepo,
      addDir: crossFolderRoot
    }),
  /guarded worker profile cannot use addDir/u
);

const boundedFableWorker = startRun({
  prompt: "Return BRIDGE_OK without edits.",
  profile: "worker",
  model: "fable",
  effort: "high",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const boundedFableWorkerReport = await waitRun(boundedFableWorker.run_id, { timeoutMs: 10000 });
assert.equal(boundedFableWorkerReport.model, "fable");
assert.equal(boundedFableWorkerReport.effort, "high");
assert.equal(boundedFableWorkerReport.resolved_model, "claude-fable-5");
assert.equal(boundedFableWorkerReport.write_scope.status, "passed");
assert.throws(
  () => startRun({ prompt: "Reject weak alias.", profile: "advisor", model: "sonnet", cwd: bridgeRoot }),
  /allows only moving model aliases opus or fable/u
);

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
const continuedAddDirIndex = continuedCommand.args.indexOf("--add-dir");
assert.ok(continuedAddDirIndex >= 0);
assert.equal(continuedCommand.args[continuedAddDirIndex + 1], crossFolderCanonicalRoot);
assert.equal(continuedOpusReport.session_id, opusThread.thread_id);
assert.deepEqual(continuedOpus.add_dirs, [crossFolderCanonicalRoot]);
assert.throws(
  () =>
    sendThread({
      thread_id: opusThread.thread_id,
      prompt: "Do not widen this thread's context roots.",
      cwd: bridgeRoot,
      addDir: bridgeRoot
    }),
  /owns its immutable addDir manifest/u
);
assert.throws(
  () =>
    sendThread({
      thread_id: opusThread.thread_id,
      prompt: "Do not change this thread's profile.",
      cwd: bridgeRoot,
      profile: "fable-advisor"
    }),
  /bound to profile=advisor/u
);
const retargetRoot = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-retarget-"));
const retargetOriginal = path.join(retargetRoot, "original");
const retargetReplacement = path.join(retargetRoot, "replacement");
const retargetAlias = path.join(retargetRoot, "alias");
fs.mkdirSync(retargetOriginal);
fs.mkdirSync(retargetReplacement);
fs.symlinkSync(retargetOriginal, retargetAlias);
const retargetThread = startThread({
  prompt: "Return BRIDGE_OK for immutable external scope.",
  topic: `scope-retarget-${threadSuffix}-guard`,
  profile: "advisor",
  cwd: bridgeRoot,
  addDir: retargetAlias
});
await waitRun(retargetThread.run_id, { timeoutMs: 10000 });
assert.deepEqual(retargetThread.add_dirs, [fs.realpathSync.native(retargetOriginal)]);
fs.rmSync(retargetOriginal, { recursive: true, force: true });
fs.symlinkSync(retargetReplacement, retargetOriginal);
assert.throws(
  () =>
    sendThread({
      thread_id: retargetThread.thread_id,
      prompt: "A replaced root must not be followed.",
      cwd: bridgeRoot
    }),
  /addDir root moved/u
);
fs.rmSync(retargetRoot, { recursive: true, force: true });
const cliThreadList = cliJson(["threads", "--cwd", bridgeRoot, "--include-archived"]);
assert.ok(cliThreadList.threads.some((thread) => thread.thread_id === opusThread.thread_id));

const smokeThreads = listThreads({ cwd: bridgeRoot, includeArchived: true }).threads.filter((thread) =>
  thread.topic?.endsWith(threadSuffix)
);
assert.equal(smokeThreads.length, 2);
assert.equal(smokeThreads.find((thread) => thread.thread_id === opusThread.thread_id)?.turns, 2);
assert.deepEqual(
  smokeThreads.find((thread) => thread.thread_id === opusThread.thread_id)?.add_dirs,
  [crossFolderCanonicalRoot]
);
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
const staleLeaseFile = path.join(runsDir, "thread-leases", `${opusThread.thread_id}.json`);
fs.mkdirSync(path.dirname(staleLeaseFile), { recursive: true });
fs.writeFileSync(
  staleLeaseFile,
  JSON.stringify({
    thread_id: opusThread.thread_id,
    token: "stale-smoke-lease",
    owner_pid: 999999,
    acquired_at: new Date(Date.now() - 60_000).toISOString()
  })
);
const staleLeaseTime = new Date(Date.now() - 60_000);
fs.utimesSync(staleLeaseFile, staleLeaseTime, staleLeaseTime);
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
assert.equal(fs.existsSync(`${staleLeaseFile}.recovery`), false);

const branchThread = startThread({
  prompt: "Return BRIDGE_OK for branch identity.",
  topic: `branch-identity-${threadSuffix}`,
  profile: "advisor",
  cwd: workerRepo
});
const branchThreadReport = await waitRun(branchThread.run_id, { timeoutMs: 10000 });
assert.equal(branchThreadReport.write_scope.status, "passed");
assert.equal(branchThreadReport.write_scope.enforcement, "read_only_git_footprint_observation");
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
const readOnlyMutationRun = startRun({
  prompt: "WRITE_OUT_OF_SCOPE_BRIDGE",
  profile: "advisor",
  cwd: workerRepo
});
const readOnlyMutationReport = await waitRun(readOnlyMutationRun.run_id, { timeoutMs: 10000 });
assert.equal(readOnlyMutationReport.write_scope.status, "failed");
assert.ok(readOnlyMutationReport.write_scope.changed_files.includes("outside.txt"));
assert.equal(readOnlyMutationReport.write_scope.attribution, "unknown_shared_worktree");
assert.ok(readOnlyMutationReport.warnings.some((warning) => warning.kind === "read_only_footprint_changed"));
assert.equal(spawnSync("git", ["restore", "outside.txt"], { cwd: workerRepo }).status, 0);
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
assert.match(fs.readFileSync(path.join(workerRepo, "allowed.txt"), "utf8"), /changed by fake Claude/u);
assert.equal(spawnSync("git", ["restore", "allowed.txt"], { cwd: workerRepo }).status, 0);
const atomicWorkerRun = startRun({
  prompt: "WRITE_ATOMIC_ALLOWED_BRIDGE",
  profile: "worker",
  writeFiles: ["allowed.txt"],
  cwd: workerRepo
});
const atomicWorkerReport = await waitRun(atomicWorkerRun.run_id, { timeoutMs: 10000 });
assert.equal(atomicWorkerReport.write_scope.status, "passed");
assert.deepEqual(atomicWorkerReport.write_scope.changed_files, ["allowed.txt"]);
assert.deepEqual(atomicWorkerReport.write_scope.out_of_scope_files, []);
assert.match(fs.readFileSync(path.join(workerRepo, "allowed.txt"), "utf8"), /changed atomically by fake Claude/u);
assert.ok(
  atomicWorkerReport.activity.recent_tool_trace.some(
    (event) => event.kind === "tool_use" && event.tool_name === "Write" && event.file_path === "allowed.txt"
  )
);
assert.deepEqual(
  atomicWorkerReport.activity.recent_tool_trace
    .filter((event) => event.kind === "tool_use")
    .map((event) => event.tool_name),
  ["Write", "Read"]
);
assert.equal(
  atomicWorkerReport.activity.recent_tool_trace.filter((event) => event.kind === "tool_result").length,
  2
);
assert.equal(atomicWorkerReport.activity.counts.tool_use, 2);
assert.equal(atomicWorkerReport.activity.counts.tool_result, 2);
fs.writeFileSync(path.join(workerRepo, "outside.txt"), "concurrent change after terminal report\n");
const frozenWorkerPeek = peekRun(atomicWorkerRun.run_id);
assert.ok(!frozenWorkerPeek.warnings?.kinds.includes("write_scope_violation"));
assert.equal(resultRun(atomicWorkerRun.run_id).write_scope.status, "passed");
assert.equal(spawnSync("git", ["restore", "outside.txt"], { cwd: workerRepo }).status, 0);

const lifecycleRepo = fs.mkdtempSync(path.join(os.tmpdir(), "claude-bridge-lifecycle-"));
assert.equal(spawnSync("git", ["init", "-q"], { cwd: lifecycleRepo }).status, 0);
assert.equal(spawnSync("git", ["config", "user.email", "bridge@example.invalid"], { cwd: lifecycleRepo }).status, 0);
assert.equal(spawnSync("git", ["config", "user.name", "Claude Bridge Smoke"], { cwd: lifecycleRepo }).status, 0);
fs.writeFileSync(path.join(lifecycleRepo, "allowed.txt"), "baseline\n");
fs.writeFileSync(path.join(lifecycleRepo, "outside.txt"), "baseline\n");
assert.equal(spawnSync("git", ["add", "."], { cwd: lifecycleRepo }).status, 0);
assert.equal(spawnSync("git", ["commit", "-qm", "baseline"], { cwd: lifecycleRepo }).status, 0);
const lifecycleHead = spawnSync("git", ["rev-parse", "HEAD"], { cwd: lifecycleRepo, encoding: "utf8" }).stdout.trim();
const lifecycleWriteScope = () => ({
  mode: "guarded",
  root: lifecycleRepo,
  allowed_files: ["allowed.txt"],
  baseline: {},
  baseline_head: lifecycleHead,
  observed_files: [],
  observation_complete: true,
  observation_error: null
});

const revivedRunId = `revived-terminal-${Date.now()}`;
const revivedRun = writeSyntheticState(revivedRunId, {
  cwd: lifecycleRepo,
  pid: null,
  process_group_pid: null,
  status: "completed",
  write_scope: {
    ...lifecycleWriteScope(),
    final_evaluation: { status: "passed", enforcement: "prompt_boundary_plus_git_and_filesystem_postflight" }
  }
});
const revivedProcess = spawn(process.execPath, ["-e", "setInterval(() => {}, 1000)", revivedRun.runDir], {
  detached: true,
  stdio: "ignore"
});
revivedProcess.unref();
const revivedState = JSON.parse(fs.readFileSync(revivedRun.files.state, "utf8"));
revivedState.pid = revivedProcess.pid;
revivedState.process_group_pid = revivedProcess.pid;
fs.writeFileSync(revivedRun.files.state, JSON.stringify(revivedState, null, 2));
await new Promise((resolve) => setTimeout(resolve, 100));
const revivedReport = resultRun(revivedRunId);
assert.equal(revivedReport.status, "running_orphaned");
assert.equal(revivedReport.write_scope.status, "pending");
const reopenedState = JSON.parse(fs.readFileSync(revivedRun.files.state, "utf8"));
assert.equal(reopenedState.write_scope.final_evaluation, undefined);
fs.writeFileSync(path.join(lifecycleRepo, "outside.txt"), "mutation after revival\n");
process.kill(-revivedProcess.pid, "SIGKILL");
await waitForPidExit(revivedProcess.pid, "revived terminal fixture");
let refrozenReport;
const refreezeDeadline = Date.now() + 5000;
while (Date.now() < refreezeDeadline) {
  refrozenReport = resultRun(revivedRunId);
  if (refrozenReport.status === "orphaned") break;
  await new Promise((resolve) => setTimeout(resolve, 50));
}
assert.equal(refrozenReport.status, "orphaned");
assert.equal(refrozenReport.write_scope.status, "failed");
assert.ok(refrozenReport.write_scope.out_of_scope_files.includes("outside.txt"));
assert.equal(spawnSync("git", ["restore", "outside.txt"], { cwd: lifecycleRepo }).status, 0);

for (const reportKind of ["missing", "corrupt", "pending"]) {
  const legacyRunId = `legacy-terminal-${reportKind}-${Date.now()}`;
  const legacyRun = writeSyntheticState(legacyRunId, {
    cwd: lifecycleRepo,
    pid: null,
    process_group_pid: null,
    status: "completed",
    write_scope: lifecycleWriteScope()
  });
  if (reportKind === "corrupt") fs.writeFileSync(legacyRun.files.report, "{not-json");
  if (reportKind === "pending") {
    fs.writeFileSync(legacyRun.files.report, JSON.stringify({ write_scope: { status: "pending" } }));
  }
  const legacyReport = resultRun(legacyRunId);
  assert.equal(legacyReport.write_scope.status, "unknown");
  assert.match(legacyReport.write_scope.error, /no frozen write-scope report/u);
}
fs.rmSync(lifecycleRepo, { recursive: true, force: true });
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
  agents: {
    reviewer: {
      description: "Reviews bridge smoke runs",
      prompt: "Review only.",
      tools: ["Read", "Glob", "Grep"],
      permissionMode: "plan",
      model: "inherit",
      effort: "xhigh"
    }
  },
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
assert.ok(newCliControlsCommand.args.includes("--agents"));
assert.ok(newCliControlsCommand.args.includes("--append-subagent-system-prompt"));
assert.ok(newCliControlsCommand.args.includes("--plugin-url"));
assert.equal(newCliControlsCommand.args.includes("--allow-dangerously-skip-permissions"), false);
assert.ok(newCliControlsCommand.args.includes("--brief"));
assert.ok(newCliControlsCommand.args.includes("--file"));
assert.ok(newCliControlsCommand.args.includes("--input-format"));
assert.ok(newCliControlsCommand.args.includes("--replay-user-messages"));

assert.throws(
  () => startRun({ prompt: "Opaque agent.", profile: "advisor", cwd: bridgeRoot, agent: "reviewer" }),
  /cannot load an opaque --agent/u
);
assert.throws(
  () =>
    startRun({
      prompt: "Unsafe subagent.",
      profile: "advisor",
      cwd: bridgeRoot,
      agents: { reviewer: { description: "Unsafe", prompt: "Write.", tools: ["Read", "Write"] } }
    }),
  /cannot enable write-capable tools/u
);
assert.throws(
  () =>
    startRun({
      prompt: "Bypass subagent.",
      profile: "advisor",
      cwd: bridgeRoot,
      agents: { reviewer: { description: "Unsafe", prompt: "Review.", permissionMode: "bypassPermissions" } }
    }),
  /cannot override permissionMode/u
);
assert.throws(
  () =>
    startRun({
      prompt: "Model drift subagent.",
      profile: "advisor",
      cwd: bridgeRoot,
      agents: { reviewer: { description: "Drifts", prompt: "Review.", model: "fable" } }
    }),
  /cannot override model/u
);

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
const restartedWaitStarted = Date.now();
const restartedLongWait = cliJson(["wait", "--run-id", longRun.run_id, "--timeout-ms", "120"]);
assert.equal(restartedLongWait.timed_out, true);
assert.ok(Date.now() - restartedWaitStarted >= 100, "restarted non-tmux wait must honor timeout instead of spinning");
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
  for (const name of [...authOverrideEnv, ...modelOverrideEnv]) process.env[name] = "must-not-leak-via-tmux";
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
  assert.match(relayRun(tmuxRun.run_id).text, /BRIDGE_OK/u);
  assert.ok(tmuxReport.files.tmux_pane);
  assert.match(fs.readFileSync(tmuxReport.files.stdout, "utf8"), /BRIDGE_OK/u);
  assert.match(fs.readFileSync(tmuxReport.files.tmux_pane, "utf8"), /BRIDGE_OK/u);
  assert.deepEqual(
    JSON.parse(fs.readFileSync(tmuxEnvCaptureFile, "utf8")),
    Object.fromEntries([...authOverrideEnv, ...modelOverrideEnv].map((name) => [name, null]))
  );
  assert.equal(tmuxReport.session_id, tmuxRun.session_id);
  delete process.env.FAKE_CLAUDE_ENV_CAPTURE;
  for (const name of [...authOverrideEnv, ...modelOverrideEnv]) delete process.env[name];
  await new Promise((resolve) => setTimeout(resolve, 250));
  assert.notEqual(
    spawnSync("tmux", ["has-session", "-t", tmuxRun.tmux_session], { encoding: "utf8" }).status,
    0
  );

  const concurrentTmuxRun = startRun({
    prompt: "POLL_BRIDGE",
    profile: "normal",
    cwd: bridgeRoot,
    useTmux: true
  });
  trackTmuxSession(concurrentTmuxRun);
  const waitCallStarted = Date.now();
  const concurrentTmuxWait = waitRun(concurrentTmuxRun.run_id, { timeoutMs: 10000 });
  assert.ok(Date.now() - waitCallStarted < 150, "tmux wait must not block the MCP event loop");
  const concurrentTmuxPeek = peekRun(concurrentTmuxRun.run_id, { cursor: 0 });
  assert.equal(concurrentTmuxPeek.terminal, false);
  const concurrentTmuxReport = await concurrentTmuxWait;
  assert.equal(concurrentTmuxReport.status, "completed");

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
  assert.equal(livePeek.tmux_capture_available, true);
  assert.ok(livePeek.updates.some((update) => /Reading context/u.test(update.text || "")));
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
assert.ok(toolNames.includes("claude_relay"));
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
assert.equal(mcpWaitPayload.terminal, true);
assert.equal(Object.hasOwn(mcpWaitPayload, "activity"), false);
assert.equal(Object.hasOwn(mcpWaitPayload, "text"), false);
assert.ok(Buffer.byteLength(mcpWait.content[0].text, "utf8") < 4096);
const mcpResult = await client.callTool({
  name: "claude_result",
  arguments: { run_id: mcpRunPayload.run_id }
});
const mcpResultPayload = JSON.parse(mcpResult.content[0].text);
assert.equal(mcpResultPayload.terminal, true);
assert.equal(Object.hasOwn(mcpResultPayload, "activity"), false);
assert.ok(Buffer.byteLength(mcpResult.content[0].text, "utf8") < 4096);
const mcpRelay = await client.callTool({
  name: "claude_relay",
  arguments: { run_id: mcpRunPayload.run_id }
});
const mcpRelayPayload = JSON.parse(mcpRelay.content[0].text);
assert.match(mcpRelayPayload.text, /BRIDGE_OK/);
const mcpPeek = await client.callTool({
  name: "claude_peek",
  arguments: {
    run_id: mcpRunPayload.run_id,
    cursor: 0
  }
});
const mcpPeekPayload = JSON.parse(mcpPeek.content[0].text);
assert.ok(mcpPeekPayload.next_cursor > 0);
assert.ok(Array.isArray(mcpPeekPayload.updates));
assert.equal(Object.hasOwn(mcpPeekPayload, "activity"), false);
assert.ok(Buffer.byteLength(mcpPeek.content[0].text, "utf8") < 4096);
const mcpObserve = await client.callTool({
  name: "claude_observe",
  arguments: {
    run_id: mcpRunPayload.run_id,
    cursor: 0
  }
});
const mcpObservePayload = JSON.parse(mcpObserve.content[0].text);
assert.equal(mcpObservePayload._envelope.schema, "claude-bridge.control.v2");
assert.equal(Object.hasOwn(mcpObservePayload, "activity"), false);
const mcpThreadStart = await client.callTool({
  name: "claude_thread_start",
  arguments: {
    prompt: "Return exactly BRIDGE_OK from a persistent MCP thread.",
    topic: `mcp-thread-${threadSuffix}`,
    profile: "advisor",
    cwd: bridgeRoot,
    addDir: crossFolderRoot
  }
});
const mcpThreadPayload = JSON.parse(mcpThreadStart.content[0].text);
assert.ok(mcpThreadPayload.thread_id);
assert.deepEqual(mcpThreadPayload.add_dirs, [crossFolderCanonicalRoot]);
const mcpThreadWait = await client.callTool({
  name: "claude_wait",
  arguments: { run_id: mcpThreadPayload.run_id, timeoutMs: 10000 }
});
assert.equal(JSON.parse(mcpThreadWait.content[0].text).status, "completed");
const mcpThreads = await client.callTool({
  name: "claude_threads",
  arguments: { cwd: bridgeRoot, includeArchived: true }
});
const mcpThreadEntry = JSON.parse(mcpThreads.content[0].text).threads.find(
  (thread) => thread.thread_id === mcpThreadPayload.thread_id
);
assert.deepEqual(mcpThreadEntry.add_dirs, [crossFolderCanonicalRoot]);
const mcpCleanup = await client.callTool({
  name: "claude_cleanup_runs",
  arguments: { olderThanDays: 14 }
});
assert.ok(mcpCleanup.content?.[0]?.text?.includes("dry_run"));
await client.close();

const directResult = resultRun(started.run_id);
assert.equal(directResult.status, "completed");
assert.equal(directResult.managed, false);
const directControl = resultControl(started.run_id);
assert.equal(directControl.terminal, true);
assert.equal(Object.hasOwn(directControl, "activity"), false);
assert.ok(Buffer.byteLength(JSON.stringify(directControl), "utf8") < 4096);
const directKill = killRun(started.run_id);
assert.equal(directKill.killed, false);

fs.rmSync(crossFolderRoot, { recursive: true, force: true });

process.stdout.write("claude-bridge smoke ok\n");
