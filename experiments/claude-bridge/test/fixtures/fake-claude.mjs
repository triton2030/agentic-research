#!/usr/bin/env node
import { spawn } from "node:child_process";
import fs from "node:fs";

const args = process.argv.slice(2);

if (args.includes("--version")) {
  console.log("2.1.112 (Claude Code fake)");
  process.exit(0);
}

if (args.includes("--help")) {
  console.log(`Usage: claude [options] [command] [prompt]
  --model <model>
  --dangerously-skip-permissions
  --output-format <format>
  --include-partial-messages
  --include-hook-events
  --debug-file <path>
  --disable-slash-commands
  --bare
  stream-json
  --permission-mode <mode>
  --tools <tools...>
  -p, --print`);
  process.exit(0);
}

const debugIndex = args.indexOf("--debug-file");
if (debugIndex !== -1 && args[debugIndex + 1]) {
  fs.writeFileSync(args[debugIndex + 1], "fake debug log\n");
}

const promptIndex = args.indexOf("-p");
const prompt = promptIndex === -1 ? "" : args[promptIndex + 1] || "";
const targetMatch = prompt.match(/Target path:\s*(.+)/);
const targetPath = targetMatch ? targetMatch[1].trim() : null;

function emit(event) {
  console.log(JSON.stringify(event));
}

function writeTrackedPids(child) {
  if (process.env.FAKE_CLAUDE_PID_FILE) {
    fs.writeFileSync(process.env.FAKE_CLAUDE_PID_FILE, String(process.pid));
  }
  if (child && process.env.FAKE_CLAUDE_CHILD_PID_FILE) {
    fs.writeFileSync(process.env.FAKE_CLAUDE_CHILD_PID_FILE, String(child.pid));
  }
}

function spawnTrackedChild({ ignoreTerm = false, stdio = "ignore" } = {}) {
  const code = `${ignoreTerm ? "process.on('SIGTERM', () => {});" : ""} setInterval(() => {}, 1000);`;
  const child = spawn(process.execPath, ["-e", code, process.env.CLAUDE_BRIDGE_RUN_ID || "no-run-id"], {
    stdio
  });
  writeTrackedPids(child);
  child.unref();
  return child;
}

emit({ type: "system", session_id: "fake-session", message: "fake claude started" });
emit({ type: "assistant_delta", text: "Reading context and preparing response." });

if (/SLEEP_BRIDGE/u.test(prompt)) {
  spawnTrackedChild();
  await new Promise((resolve) => setTimeout(resolve, 60000));
}
if (/IGNORE_TERM_BRIDGE/u.test(prompt)) {
  process.on("SIGTERM", () => {});
  spawnTrackedChild({ ignoreTerm: true });
  await new Promise((resolve) => setTimeout(resolve, 60000));
}
if (/DAEMON_BRIDGE/u.test(prompt)) {
  spawnTrackedChild();
}

if (/SELF_REPORT_ONLY/u.test(prompt) && targetPath) {
  emit({ type: "assistant_delta", text: `I read ${targetPath} and found the marker.` });
} else if (/WRONG_TOOL_PATH/u.test(prompt)) {
  emit({
    type: "tool_use",
    name: "Read",
    input: { file_path: "/tmp/wrong-skill.md" }
  });
} else if (targetPath) {
  emit({
    type: "tool_use",
    name: "Read",
    input: { file_path: targetPath }
  });
}
emit({ type: "assistant_delta", text: "BRIDGE_OK" });
emit({ type: "result", text: "BRIDGE_OK" });
