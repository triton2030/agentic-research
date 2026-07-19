#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";

const args = process.argv.slice(2);

if (args.includes("--version")) {
  console.log("2.1.215 (Claude Code fake)");
  process.exit(0);
}

const authIndex = args.indexOf("auth");
if (authIndex !== -1 && args[authIndex + 1] === "status") {
  const rejectedOption = process.env.FAKE_CLAUDE_REJECT_OPTION;
  if (rejectedOption && args.includes(rejectedOption)) {
    console.error(`error: unknown option '${rejectedOption}'`);
    process.exit(1);
  }
  console.log(JSON.stringify({ loggedIn: true, authMethod: "oauth", apiProvider: "firstParty" }));
  process.exit(0);
}

if (args.includes("--help")) {
  console.log(`Usage: claude [options] [command] [prompt]
  --model <model>
  --effort <level>
  --dangerously-skip-permissions
  --output-format <format>
  --verbose
  --include-partial-messages
  --include-hook-events
  --debug-file <path>
  --disable-slash-commands
  stream-json
  --permission-mode <mode>
  --json-schema <schema>
  --agent <agent>
  --agents <json>
  --plugin-url <url>
  --allow-dangerously-skip-permissions
  --brief
  --file <specs...>
  --input-format <format>
  --replay-user-messages
  --session-id <uuid>
  --resume [session]
  --fork-session
  --name <name>
  --no-session-persistence
  --fallback-model <model>
  --safe-mode
  --forward-subagent-text
  --append-subagent-system-prompt <prompt>
  fable opus sonnet
  --tools <tools...>
  --allowedTools <tools...>
  --disallowedTools <tools...>
  -p, --print`);
  process.exit(0);
}

if (process.env.FAKE_CLAUDE_ENV_CAPTURE) {
  fs.writeFileSync(
    process.env.FAKE_CLAUDE_ENV_CAPTURE,
    JSON.stringify(
      {
        ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || null,
        CLAUDE_API_KEY: process.env.CLAUDE_API_KEY || null
      },
      null,
      2
    )
  );
}

const debugIndex = args.indexOf("--debug-file");
if (debugIndex !== -1 && args[debugIndex + 1]) {
  fs.writeFileSync(args[debugIndex + 1], "fake debug log\n");
}

const promptIndex = args.indexOf("-p");
const prompt = promptIndex === -1 ? "" : args[promptIndex + 1] || "";
const sessionIndex = args.indexOf("--session-id");
const resumeIndex = args.indexOf("--resume");
const modelIndex = args.indexOf("--model");
const requestedModel = modelIndex === -1 ? "opus" : args[modelIndex + 1] || "opus";
const sessionId =
  sessionIndex !== -1
    ? args[sessionIndex + 1]
    : resumeIndex !== -1 && args[resumeIndex + 1] && !args[resumeIndex + 1].startsWith("-")
      ? args[resumeIndex + 1]
      : "fake-session";
const resolvedModel =
  requestedModel === "fable"
    ? "claude-fable-5"
    : requestedModel === "opus"
      ? "claude-opus-4-8"
      : requestedModel;
if (/WRITE_ALLOWED_BRIDGE/u.test(prompt)) {
  fs.writeFileSync("allowed.txt", "changed by fake Claude\n");
}
if (/WRITE_OUT_OF_SCOPE_BRIDGE/u.test(prompt)) {
  fs.writeFileSync("outside.txt", "outside authorized scope\n");
}
if (/WRITE_IGNORED_BRIDGE/u.test(prompt)) {
  fs.writeFileSync("ignored.txt", "ignored out-of-scope write\n");
}
if (/COMMIT_ALLOWED_BRIDGE/u.test(prompt)) {
  fs.writeFileSync("allowed.txt", "committed by fake Claude\n");
  spawnSync("git", ["add", "allowed.txt"]);
  spawnSync("git", ["commit", "-qm", "fake Claude commit"]);
}
if (/RENAME_OUTSIDE_BRIDGE/u.test(prompt)) {
  fs.renameSync("outside.txt", "allowed.txt");
}
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

emit({ type: "system", session_id: sessionId, model: resolvedModel, message: "fake claude started" });
if (/SYNTHETIC_MODEL_AFTER_INIT/u.test(prompt)) {
  emit({ type: "assistant", message: { model: "<synthetic>", content: "synthetic auth error" } });
}
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
  const toolUseId = "fake-read-1";
  const toolUse = { type: "tool_use", id: toolUseId, name: "Read", input: { file_path: targetPath } };
  const toolResult = {
    type: "tool_result",
    tool_use_id: toolUseId,
    is_error: /READ_ERROR/u.test(prompt),
    text: /READ_ERROR/u.test(prompt) ? "ENOENT: read failed" : "SAMPLE_SKILL_MARKER"
  };
  if (/NESTED_TOOL_EVENTS/u.test(prompt)) {
    emit({ type: "assistant", message: { role: "assistant", content: [toolUse] } });
    emit({ type: "user", message: { role: "user", content: [toolResult] } });
  } else {
    emit(toolUse);
    emit(toolResult);
  }
}
emit({ type: "assistant_delta", text: "BRIDGE_OK" });
emit({ type: "result", text: "BRIDGE_OK" });
