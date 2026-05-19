import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const serverPath = path.join(root, "src", "server.js");
const runnerUrl = pathToFileURL(path.join(root, "src", "runner.js")).href;
const smokeHome = fs.mkdtempSync(path.join(os.tmpdir(), "gemini-mcp-home-"));

function baseEnv() {
  const env = Object.fromEntries(
    Object.entries(process.env).filter(([, value]) => value !== undefined)
  );
  delete env.GEMINI_API_KEY;
  delete env.GOOGLE_API_KEY;
  delete env.GEMINI_MODEL;
  delete env.GEMINI_THINKING_LEVEL;
  delete env.GEMINI_MCP_BACKEND;
  delete env.GEMINI_CLI_PATH;
  delete env.GEMINI_CLI_TIMEOUT_MS;
  delete env.GOOGLE_GENAI_USE_VERTEXAI;
  delete env.GOOGLE_CLOUD_PROJECT;
  delete env.GOOGLE_CLOUD_LOCATION;
  delete env.GOOGLE_APPLICATION_CREDENTIALS;
  env.HOME = smokeHome;
  return env;
}

async function withClient(env, callback) {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [serverPath],
    env
  });
  const client = new Client({ name: "gemini-mcp-smoke", version: "0.1.0" });
  await client.connect(transport);
  try {
    return await callback(client);
  } finally {
    await client.close();
  }
}

function runnerJson(source) {
  const result = spawnSync(process.execPath, ["--input-type=module", "-e", source], {
    cwd: root,
    env: baseEnv(),
    encoding: "utf8"
  });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return JSON.parse(result.stdout);
}

function runnerCallJson(fn, runId) {
  return runnerJson(`
const runner = await import(${JSON.stringify(runnerUrl)});
const output = await runner.${fn}(${JSON.stringify(runId)});
console.log(JSON.stringify(output));
`);
}

function writeSyntheticState(runId, state) {
  const runDir = path.join(root, "runs", runId);
  fs.mkdirSync(runDir, { recursive: true });
  const files = {
    prompt: path.join(runDir, "prompt.txt"),
    command: path.join(runDir, "command.json"),
    script: path.join(runDir, "run.sh"),
    events: path.join(runDir, "events.ndjson"),
    stdout: path.join(runDir, "stdout.log"),
    stderr: path.join(runDir, "stderr.log"),
    tmux_pane: path.join(runDir, "tmux-pane.log"),
    report: path.join(runDir, "report.json"),
    state: path.join(runDir, "state.json"),
    exit_code: path.join(runDir, "exit-code.txt")
  };
  fs.writeFileSync(files.events, "");
  fs.writeFileSync(files.stdout, "");
  fs.writeFileSync(files.stderr, "");
  fs.writeFileSync(
    files.state,
    JSON.stringify(
      {
        run_id: runId,
        backend: "gemini-cli",
        model: "gemini-3.1-pro-preview",
        thinking_level: "high",
        cwd: root,
        pid: process.pid,
        process_group_pid: process.pid,
        status: "running",
        started_at: new Date().toISOString(),
        command: [process.execPath, "/tmp/not-this-run/run.sh"],
        log_dir: runDir,
        files,
        use_tmux: false,
        ...state
      },
      null,
      2
    )
  );
  return { runDir, files };
}

await withClient({ ...baseEnv(), PATH: "" }, async (client) => {
  const tools = await client.listTools();
  const toolNames = tools.tools.map((tool) => tool.name);
  assert.deepEqual(toolNames.sort(), [
    "gemini_ask",
    "gemini_cleanup_runs",
    "gemini_kill",
    "gemini_peek",
    "gemini_result",
    "gemini_run",
    "gemini_status",
    "gemini_wait"
  ]);

  const status = await client.callTool({ name: "gemini_status", arguments: {} });
  const statusPayload = JSON.parse(status.content[0].text);
  assert.equal(statusPayload.ok, true);
  assert.equal(statusPayload.effective_backend, null);
  assert.equal(statusPayload.available_auth.api_key, false);
  assert.equal(statusPayload.default_model, "gemini-3.1-pro-preview");
  assert.equal(statusPayload.default_thinking_level, "high");
  assert.equal(statusPayload.default_cli_timeout_ms, 50000);

  const ask = await client.callTool({
    name: "gemini_ask",
    arguments: {
      prompt: "Return exactly GEMINI_MCP_OK."
    }
  });
  assert.equal(ask.isError, true);
  assert.match(ask.content[0].text, /Vertex AI|GEMINI_MCP_BACKEND=cli/u);
});

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "gemini-mcp-smoke-"));
const fakeGemini = path.join(tempDir, "gemini");
const captureFile = path.join(tempDir, "capture.json");
fs.writeFileSync(
  fakeGemini,
  `#!/usr/bin/env node
import { spawn } from "node:child_process";
import fs from "node:fs";
const args = process.argv.slice(2);
const promptIndex = args.indexOf("-p");
const prompt = promptIndex === -1 ? "" : args[promptIndex + 1] || "";
if (args.includes("--version")) {
  console.log("fake-gemini 0.0.0");
  process.exit(0);
}
if (process.env.FAKE_GEMINI_CAPTURE) {
  fs.writeFileSync(
    process.env.FAKE_GEMINI_CAPTURE,
    JSON.stringify({ args, cwd: process.cwd() }, null, 2)
  );
}
if (process.env.FAKE_GEMINI_EMPTY === "1") {
  console.log(JSON.stringify({ session_id: "fake", response: "", stats: {} }));
  process.exit(0);
}
function recordSleepPids() {
  if (process.env.FAKE_GEMINI_PID_FILE) {
    fs.writeFileSync(process.env.FAKE_GEMINI_PID_FILE, String(process.pid));
  }
  if (process.env.FAKE_GEMINI_CHILD_PID_FILE) {
    const child = spawn(process.execPath, ["-e", "setInterval(() => {}, 1000);", process.env.GEMINI_MCP_RUN_ID || "no-run-id"], { stdio: "ignore" });
    fs.writeFileSync(process.env.FAKE_GEMINI_CHILD_PID_FILE, String(child.pid));
    child.unref();
  }
}
function spawnTrackedChild(options = {}) {
  if (process.env.FAKE_GEMINI_PID_FILE) {
    fs.writeFileSync(process.env.FAKE_GEMINI_PID_FILE, String(process.pid));
  }
  const ignoreTerm = options.ignoreTerm ? "process.on('SIGTERM', () => {});" : "";
  const child = spawn(process.execPath, ["-e", ignoreTerm + " setInterval(() => {}, 1000);", process.env.GEMINI_MCP_RUN_ID || "no-run-id"], {
    stdio: options.stdio || "ignore"
  });
  if (process.env.FAKE_GEMINI_CHILD_PID_FILE) {
    fs.writeFileSync(process.env.FAKE_GEMINI_CHILD_PID_FILE, String(child.pid));
  }
  child.unref();
  return child;
}
if (/STREAM_GEMINI/u.test(prompt)) {
  recordSleepPids();
  console.log("GEMINI_MCP_STREAM");
  await new Promise((resolve) => setTimeout(resolve, 60000));
}
if (/SLEEP_GEMINI/u.test(prompt)) {
  recordSleepPids();
  await new Promise((resolve) => setTimeout(resolve, 60000));
}
if (/IGNORE_TERM_GEMINI/u.test(prompt)) {
  process.on("SIGTERM", () => {});
  spawnTrackedChild({ ignoreTerm: true });
  await new Promise((resolve) => setTimeout(resolve, 60000));
}
if (/DAEMON_GEMINI/u.test(prompt)) {
  spawnTrackedChild();
}
console.log(
  JSON.stringify({ session_id: "fake", response: "GEMINI_MCP_OK", stats: {} })
);
`
);
fs.chmodSync(fakeGemini, 0o755);

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

const fakeParentPidFile = path.join(tempDir, "fake-gemini-parent.pid");
const fakeChildPidFile = path.join(tempDir, "fake-gemini-child.pid");

await withClient(
  {
    ...baseEnv(),
    GEMINI_MCP_BACKEND: "cli",
    GEMINI_CLI_PATH: fakeGemini,
    FAKE_GEMINI_CAPTURE: captureFile,
    FAKE_GEMINI_PID_FILE: fakeParentPidFile,
    FAKE_GEMINI_CHILD_PID_FILE: fakeChildPidFile
  },
  async (client) => {
    const status = await client.callTool({ name: "gemini_status", arguments: {} });
    const statusPayload = JSON.parse(status.content[0].text);
    assert.equal(statusPayload.effective_backend, "gemini-cli");
    assert.equal(statusPayload.available_auth.gemini_cli_command, fakeGemini);
    assert.equal(statusPayload.available_auth.gemini_cli_version, "fake-gemini 0.0.0");
    assert.equal(statusPayload.default_cli_timeout_ms, 50000);

    const ask = await client.callTool({
      name: "gemini_ask",
      arguments: {
        prompt: "Return exactly GEMINI_MCP_OK.",
        cwd: tempDir,
        includeDirectories: [root],
        timeoutMs: 12345
      }
    });
    assert.equal(ask.isError, undefined);
    const payload = JSON.parse(ask.content[0].text);
    assert.equal(payload.backend, "gemini-cli");
    assert.equal(payload.cliCommand, fakeGemini);
    assert.equal(payload.cliVersion, "fake-gemini 0.0.0");
    assert.equal(payload.cwd, tempDir);
    assert.equal(payload.approvalMode, "yolo");
    assert.deepEqual(payload.includeDirectories, [root]);
    assert.equal(payload.timeoutMs, 12345);
    assert.equal(payload.text, "GEMINI_MCP_OK");
    const captured = JSON.parse(fs.readFileSync(captureFile, "utf8"));
    assert.equal(fs.realpathSync(captured.cwd), fs.realpathSync(tempDir));
    assert.ok(captured.args.includes("--skip-trust"));
    assert.match(captured.args.join(" "), /--approval-mode yolo/u);
    assert.match(captured.args.join(" "), /--include-directories/u);

    const started = await client.callTool({
      name: "gemini_run",
      arguments: {
        prompt: "Return exactly GEMINI_MCP_OK.",
        cwd: tempDir,
        includeDirectories: [root]
      }
    });
    const startedPayload = JSON.parse(started.content[0].text);
    assert.ok(startedPayload.run_id);
    assert.equal(startedPayload.use_tmux, false);

    const waited = await client.callTool({
      name: "gemini_wait",
      arguments: {
        run_id: startedPayload.run_id,
        timeoutMs: 10000
      }
    });
    const waitedPayload = JSON.parse(waited.content[0].text);
    assert.equal(waitedPayload.status, "completed");
    assert.equal(waitedPayload.managed, false);
    assert.match(waitedPayload.final_output_summary, /GEMINI_MCP_OK/u);
    assert.match(waitedPayload.chat_relay.text, /GEMINI_MCP_OK/u);

    const peek = await client.callTool({
      name: "gemini_peek",
      arguments: {
        run_id: startedPayload.run_id,
        cursor: 0
      }
    });
    const peekPayload = JSON.parse(peek.content[0].text);
    assert.ok(peekPayload.next_cursor > 0);
    assert.match(peekPayload.chat_relay.text, /GEMINI_MCP_OK/u);

    const result = await client.callTool({
      name: "gemini_result",
      arguments: {
        run_id: startedPayload.run_id
      }
    });
    const resultPayload = JSON.parse(result.content[0].text);
    assert.equal(resultPayload.status, "completed");
    assert.equal(resultPayload.managed, false);

    const orphanId = `orphan-no-fingerprint-${Date.now()}`;
    writeSyntheticState(orphanId, {});
    const orphanReport = runnerCallJson("resultRun", orphanId);
    assert.equal(orphanReport.status, "orphaned");
    assert.match(orphanReport.orphan_reason, /fingerprint/u);
    const orphanKill = runnerCallJson("killRun", orphanId);
    assert.equal(orphanKill.killed, false);

    fs.rmSync(fakeParentPidFile, { force: true });
    fs.rmSync(fakeChildPidFile, { force: true });
    const longRun = await client.callTool({
      name: "gemini_run",
      arguments: {
        prompt: "SLEEP_GEMINI",
        cwd: tempDir
      }
    });
    const longRunPayload = JSON.parse(longRun.content[0].text);
    await waitForFile(fakeParentPidFile);
    await waitForFile(fakeChildPidFile);
    const longRunParentPid = readPidFile(fakeParentPidFile);
    const longRunChildPid = readPidFile(fakeChildPidFile);
    await new Promise((resolve) => setTimeout(resolve, 250));
    const restartedLongReport = runnerCallJson("resultRun", longRunPayload.run_id);
    assert.equal(restartedLongReport.status, "running_orphaned");
    assert.equal(restartedLongReport.managed, false);
    const killedPayload = runnerCallJson("killRun", longRunPayload.run_id);
    assert.equal(killedPayload.killed, true);
    const killedResult = await client.callTool({
      name: "gemini_wait",
      arguments: {
        run_id: longRunPayload.run_id,
        timeoutMs: 10000
      }
    });
    const killedResultPayload = JSON.parse(killedResult.content[0].text);
    assert.equal(killedResultPayload.status, "killed");
    assert.equal(killedResultPayload.managed, false);
    await waitForPidExit(longRunParentPid, "Gemini parent");
    await waitForPidExit(longRunChildPid, "Gemini child");

    fs.rmSync(fakeParentPidFile, { force: true });
    fs.rmSync(fakeChildPidFile, { force: true });
    const daemonRun = await client.callTool({
      name: "gemini_run",
      arguments: {
        prompt: "DAEMON_GEMINI",
        cwd: tempDir
      }
    });
    const daemonRunPayload = JSON.parse(daemonRun.content[0].text);
    await waitForFile(fakeChildPidFile);
    const daemonChildPid = readPidFile(fakeChildPidFile);
    const daemonWait = await client.callTool({
      name: "gemini_wait",
      arguments: {
        run_id: daemonRunPayload.run_id,
        timeoutMs: 10000
      }
    });
    const daemonWaitPayload = JSON.parse(daemonWait.content[0].text);
    assert.equal(daemonWaitPayload.status, "running_orphaned");
    const daemonRestartedReport = runnerCallJson("resultRun", daemonRunPayload.run_id);
    assert.equal(daemonRestartedReport.status, "running_orphaned");
    const daemonKill = runnerCallJson("killRun", daemonRunPayload.run_id);
    assert.equal(daemonKill.killed, true);
    await waitForPidExit(daemonChildPid, "Gemini daemon child");
    const daemonKilledReport = runnerCallJson("resultRun", daemonRunPayload.run_id);
    assert.equal(daemonKilledReport.status, "killed");

    fs.rmSync(fakeParentPidFile, { force: true });
    fs.rmSync(fakeChildPidFile, { force: true });
    const stubbornRun = await client.callTool({
      name: "gemini_run",
      arguments: {
        prompt: "IGNORE_TERM_GEMINI",
        cwd: tempDir
      }
    });
    const stubbornRunPayload = JSON.parse(stubbornRun.content[0].text);
    await waitForFile(fakeParentPidFile);
    await waitForFile(fakeChildPidFile);
    const stubbornParentPid = readPidFile(fakeParentPidFile);
    const stubbornChildPid = readPidFile(fakeChildPidFile);
    await new Promise((resolve) => setTimeout(resolve, 250));
    const stubbornSoftKill = await client.callTool({
      name: "gemini_kill",
      arguments: {
        run_id: stubbornRunPayload.run_id
      }
    });
    assert.equal(JSON.parse(stubbornSoftKill.content[0].text).killed, true);
    const stubbornStillKilling = await client.callTool({
      name: "gemini_result",
      arguments: {
        run_id: stubbornRunPayload.run_id
      }
    });
    assert.equal(JSON.parse(stubbornStillKilling.content[0].text).status, "killing");
    const stubbornHardKill = await client.callTool({
      name: "gemini_kill",
      arguments: {
        run_id: stubbornRunPayload.run_id
      }
    });
    assert.equal(JSON.parse(stubbornHardKill.content[0].text).killed, true);
    await waitForPidExit(stubbornParentPid, "Gemini stubborn parent");
    await waitForPidExit(stubbornChildPid, "Gemini stubborn child");
    const stubbornKilledResult = await client.callTool({
      name: "gemini_wait",
      arguments: {
        run_id: stubbornRunPayload.run_id,
        timeoutMs: 10000
      }
    });
    assert.equal(JSON.parse(stubbornKilledResult.content[0].text).status, "killed");

    const cleanup = await client.callTool({
      name: "gemini_cleanup_runs",
      arguments: {
        olderThanDays: 14
      }
    });
    assert.match(cleanup.content[0].text, /dry_run/u);

    if (spawnSync("tmux", ["-V"], { encoding: "utf8" }).status === 0) {
      const tmuxRun = await client.callTool({
        name: "gemini_run",
        arguments: {
          prompt: "Return exactly GEMINI_MCP_OK via tmux.",
          cwd: tempDir,
          useTmux: true
        }
      });
      const tmuxRunPayload = JSON.parse(tmuxRun.content[0].text);
      assert.equal(tmuxRunPayload.use_tmux, true);
      assert.ok(tmuxRunPayload.tmux_session);

      const tmuxWait = await client.callTool({
        name: "gemini_wait",
        arguments: {
          run_id: tmuxRunPayload.run_id,
          timeoutMs: 10000
        }
      });
      const tmuxWaitPayload = JSON.parse(tmuxWait.content[0].text);
      assert.equal(tmuxWaitPayload.status, "completed");
      assert.equal(tmuxWaitPayload.use_tmux, true);
      assert.match(tmuxWaitPayload.final_output_summary, /GEMINI_MCP_OK/u);
      assert.ok(tmuxWaitPayload.files.tmux_pane);
      assert.match(fs.readFileSync(tmuxWaitPayload.files.stdout, "utf8"), /GEMINI_MCP_OK/u);
      assert.match(fs.readFileSync(tmuxWaitPayload.files.tmux_pane, "utf8"), /GEMINI_MCP_OK/u);
      await new Promise((resolve) => setTimeout(resolve, 250));
      assert.notEqual(
        spawnSync("tmux", ["has-session", "-t", tmuxRunPayload.tmux_session], { encoding: "utf8" }).status,
        0
      );

      const tmuxResult = await client.callTool({
        name: "gemini_result",
        arguments: {
          run_id: tmuxRunPayload.run_id
        }
      });
      const tmuxResultPayload = JSON.parse(tmuxResult.content[0].text);
      assert.equal(tmuxResultPayload.status, "completed");
      assert.equal(tmuxResultPayload.managed, false);
      assert.ok(tmuxResultPayload.files.tmux_pane);

      fs.rmSync(fakeParentPidFile, { force: true });
      fs.rmSync(fakeChildPidFile, { force: true });
      const streamingTmuxRun = await client.callTool({
        name: "gemini_run",
        arguments: {
          prompt: "STREAM_GEMINI",
          cwd: tempDir,
          useTmux: true
        }
      });
      const streamingTmuxPayload = JSON.parse(streamingTmuxRun.content[0].text);
      await waitForFile(fakeParentPidFile);
      await waitForFile(fakeChildPidFile);
      const streamingParentPid = readPidFile(fakeParentPidFile);
      const streamingChildPid = readPidFile(fakeChildPidFile);
      await new Promise((resolve) => setTimeout(resolve, 500));
      const streamingPeek = await client.callTool({
        name: "gemini_peek",
        arguments: {
          run_id: streamingTmuxPayload.run_id,
          cursor: 0
        }
      });
      const streamingPeekPayload = JSON.parse(streamingPeek.content[0].text);
      assert.equal(streamingPeekPayload.tmux_capture.available, true);
      assert.match(streamingPeekPayload.tmux_capture.text, /GEMINI_MCP_STREAM/u);
      const streamingKilled = await client.callTool({
        name: "gemini_kill",
        arguments: {
          run_id: streamingTmuxPayload.run_id
        }
      });
      const streamingKilledPayload = JSON.parse(streamingKilled.content[0].text);
      assert.equal(streamingKilledPayload.killed, true);
      await new Promise((resolve) => setTimeout(resolve, 250));
      const streamingResult = await client.callTool({
        name: "gemini_result",
        arguments: {
          run_id: streamingTmuxPayload.run_id
        }
      });
      const streamingResultPayload = JSON.parse(streamingResult.content[0].text);
      assert.equal(streamingResultPayload.status, "killed");
      assert.equal(streamingResultPayload.managed, false);
      await waitForPidExit(streamingParentPid, "Gemini tmux parent");
      await waitForPidExit(streamingChildPid, "Gemini tmux child");
      assert.notEqual(
        spawnSync("tmux", ["has-session", "-t", streamingTmuxPayload.tmux_session], { encoding: "utf8" }).status,
        0
      );
    }
  }
);

await withClient(
  {
    ...baseEnv(),
    GEMINI_MCP_BACKEND: "cli",
    GEMINI_CLI_PATH: fakeGemini,
    FAKE_GEMINI_EMPTY: "1"
  },
  async (client) => {
    const ask = await client.callTool({
      name: "gemini_ask",
      arguments: {
        prompt: "Return an empty response."
      }
    });
    assert.equal(ask.isError, true);
    assert.match(ask.content[0].text, /empty text/u);
  }
);

process.stdout.write("gemini-mcp smoke ok\n");
