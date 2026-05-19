import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import {
  auditSkill,
  cleanupRuns,
  doctor,
  killRun,
  peekRun,
  profiles,
  resultRun,
  startRun,
  waitRun
} from "../src/runner.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const bridgeRoot = path.resolve(__dirname, "..");
const fakeClaude = path.join(__dirname, "fixtures", "fake-claude.mjs");
const cli = path.join(bridgeRoot, "src", "cli.js");
const runsDir = path.join(bridgeRoot, "runs");
const smokeTmuxSessions = new Set();
process.env.CLAUDE_BRIDGE_CLAUDE_BIN = fakeClaude;

function cleanupSmokeTmuxSessions() {
  for (const session of smokeTmuxSessions) {
    spawnSync("tmux", ["kill-session", "-t", session], { encoding: "utf8" });
  }
}

function trackTmuxSession(payload) {
  if (payload?.tmux_session) smokeTmuxSessions.add(payload.tmux_session);
}

process.once("exit", cleanupSmokeTmuxSessions);

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
assert.equal(doctorReport.stream_json_supported, true);
assert.equal(doctorReport.flags["--dangerously-skip-permissions"], true);
assert.equal(doctorReport.flags["--permission-mode"], true);
assert.equal(doctorReport.flags["--json-schema"], true);
assert.equal(doctorReport.flags["--agent"], true);
assert.equal(doctorReport.flags["--agents"], true);

const profileList = profiles();
assert.ok(profileList.some((profile) => profile.name === "turbo" && profile.flags.includes("--dangerously-skip-permissions")));
assert.ok(profileList.some((profile) => profile.name === "no-skills" && profile.flags.includes("--disable-slash-commands")));
assert.ok(profileList.some((profile) => profile.name === "no-memory"));
assert.equal(profileList.some((profile) => profile.name === "clean"), false);
assert.equal(profileList.some((profile) => profile.name === "subagent"), false);
for (const profile of profileList) {
  if (profile.flags.includes("stream-json")) {
    assert.ok(profile.flags.includes("--verbose"), `${profile.name} must include --verbose with stream-json`);
  }
}
assert.throws(
  () =>
    startRun({
      prompt: "This should fail before spawning.",
      profile: "normal",
      cwd: bridgeRoot,
      maxTurns: 1
    }),
  /does not advertise/
);

const fakeEnvCaptureFile = path.join(bridgeRoot, "runs", "_fake-claude-env.json");
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
const fakeEnvCapture = JSON.parse(fs.readFileSync(fakeEnvCaptureFile, "utf8"));
assert.equal(startedCommand.env.api_key_env_stripped, true);
assert.deepEqual(fakeEnvCapture, { ANTHROPIC_API_KEY: null, CLAUDE_API_KEY: null });
delete process.env.FAKE_CLAUDE_ENV_CAPTURE;
delete process.env.ANTHROPIC_API_KEY;
delete process.env.CLAUDE_API_KEY;
assert.equal(report.status, "completed");
assert.equal(report.managed, false);
assert.match(report.final_output_summary, /BRIDGE_OK/);
assert.match(report.chat_relay.text, /BRIDGE_OK/);
assert.match(report.chat_relay.markdown, /Claude:\nBRIDGE_OK/);
assert.ok(fs.existsSync(report.files.state));
assert.ok(report.milestones.some((event) => event.kind === "assistant_text" && /BRIDGE_OK/u.test(event.text)));

const separateResult = cliJson(["result", "--run-id", started.run_id]);
assert.equal(separateResult.status, "completed");
assert.equal(separateResult.managed, false);
assert.match(separateResult.final_output_summary, /BRIDGE_OK/);
assert.match(separateResult.chat_relay.text, /BRIDGE_OK/);
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

const newCliControlsRun = startRun({
  prompt: "Return exactly BRIDGE_OK.",
  profile: "read-only",
  cwd: bridgeRoot,
  permissionMode: "plan",
  jsonSchema: { type: "object", properties: { ok: { type: "boolean" } }, required: ["ok"] },
  agent: "reviewer",
  agents: { reviewer: { description: "Reviews bridge smoke runs", prompt: "Review only." } },
  pluginUrl: ["https://example.invalid/plugin.zip"],
  allowDangerouslySkipPermissions: true,
  brief: true,
  file: ["file_abc:doc.txt"],
  inputFormat: "text",
  replayUserMessages: true
});
const newCliControlsReport = await waitRun(newCliControlsRun.run_id, { timeoutMs: 10000 });
const newCliControlsCommand = JSON.parse(fs.readFileSync(newCliControlsReport.files.command, "utf8"));
assert.ok(newCliControlsCommand.args.includes("--permission-mode"));
assert.ok(newCliControlsCommand.args.includes("--json-schema"));
assert.ok(newCliControlsCommand.args.includes("--agent"));
assert.ok(newCliControlsCommand.args.includes("--agents"));
assert.ok(newCliControlsCommand.args.includes("--plugin-url"));
assert.ok(newCliControlsCommand.args.includes("--allow-dangerously-skip-permissions"));
assert.ok(newCliControlsCommand.args.includes("--brief"));
assert.ok(newCliControlsCommand.args.includes("--file"));
assert.ok(newCliControlsCommand.args.includes("--input-format"));
assert.ok(newCliControlsCommand.args.includes("--replay-user-messages"));

const orphanId = `orphan-no-fingerprint-${Date.now()}`;
writeSyntheticState(orphanId, {});
const orphanReport = cliJson(["result", "--run-id", orphanId]);
assert.equal(orphanReport.status, "orphaned");
assert.match(orphanReport.orphan_reason, /fingerprint/u);
const orphanKill = cliJson(["kill", "--run-id", orphanId]);
assert.equal(orphanKill.killed, false);

const fakeParentPidFile = path.join(bridgeRoot, "runs", "_fake-claude-parent.pid");
const fakeChildPidFile = path.join(bridgeRoot, "runs", "_fake-claude-child.pid");
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

const oldRunId = `old-cleanup-${Date.now()}`;
const old = writeSyntheticState(oldRunId, {
  pid: null,
  status: "completed",
  started_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString()
});
const oldTime = new Date(Date.now() - 20 * 24 * 60 * 60 * 1000);
fs.utimesSync(old.runDir, oldTime, oldTime);
const cleanupDryRun = cleanupRuns({ olderThanDays: 14 });
assert.ok(cleanupDryRun.dry_run);
assert.ok(cleanupDryRun.candidates.some((candidate) => candidate.run_id === oldRunId));
assert.ok(fs.existsSync(old.runDir));
const cleanupConfirmed = cliJson(["cleanup", "--days", "14", "--confirm"]);
assert.ok(cleanupConfirmed.candidates.some((candidate) => candidate.run_id === oldRunId));
assert.equal(fs.existsSync(old.runDir), false);

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
