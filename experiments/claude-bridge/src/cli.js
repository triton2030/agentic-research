#!/usr/bin/env node
import {
  archiveThread,
  auditSkill,
  cleanupRuns,
  discoverSkills,
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
} from "./runner.js";

function print(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

function getArg(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  if (index === -1) return fallback;
  return process.argv[index + 1] ?? fallback;
}

function getArgs(name) {
  const values = [];
  for (let index = 0; index < process.argv.length; index += 1) {
    if (process.argv[index] === `--${name}` && process.argv[index + 1]) {
      values.push(process.argv[index + 1]);
    }
  }
  return values;
}

function getOptionalArgs(name) {
  const values = getArgs(name);
  return values.length ? values : undefined;
}

function getJsonArg(name) {
  const value = getArg(name);
  return value === undefined ? undefined : JSON.parse(value);
}

const command = process.argv[2] || "help";

if (command === "help") {
  process.stdout.write(`Usage:
  node src/cli.js doctor
  node src/cli.js profiles
  node src/cli.js run --prompt "..." [--profile advisor] [--model opus] [--effort xhigh] [--cwd /path]
  node src/cli.js thread-start --topic "..." --prompt "..." [--profile advisor] [--model opus] [--effort xhigh]
  node src/cli.js thread-send --thread-id <id> --prompt "..."
  node src/cli.js threads [--cwd /path] [--include-archived]
  node src/cli.js thread-archive --thread-id <id> [--unarchive]
  node src/cli.js peek --run-id <id>
  node src/cli.js wait --run-id <id>
  node src/cli.js kill --run-id <id>
  node src/cli.js result --run-id <id>
  node src/cli.js discover-skills [--cwd /path]
  node src/cli.js audit-skill --skill-path /path/to/SKILL.md [--prompt "..."]
  node src/cli.js cleanup [--days 14] [--confirm]
`);
} else if (command === "doctor") {
  print(doctor());
} else if (command === "profiles") {
  print(profiles());
} else if (command === "run") {
  print(
    startRun({
      prompt: getArg("prompt", ""),
      profile: getArg("profile", "advisor"),
      cwd: getArg("cwd", process.cwd()),
      title: getArg("title"),
      topic: getArg("topic"),
      model: getArg("model"),
      effort: getArg("effort"),
      maxTurns: getArg("max-turns"),
      fallbackModel: getArg("fallback-model"),
      sessionId: getArg("session-id"),
      resume: getArg("resume"),
      forkSession: process.argv.includes("--fork-session"),
      name: getArg("name"),
      noSessionPersistence: process.argv.includes("--no-session-persistence"),
      permissionMode: getArg("permission-mode"),
      jsonSchema: getJsonArg("json-schema"),
      agent: getArg("agent"),
      agents: getJsonArg("agents"),
      pluginUrl: getArgs("plugin-url"),
      allowedTools: getArgs("allowed-tools"),
      disallowedTools: getArgs("disallowed-tools"),
      addDir: getArgs("add-dir"),
      file: getArgs("file"),
      inputFormat: getArg("input-format"),
      brief: process.argv.includes("--brief"),
      replayUserMessages: process.argv.includes("--replay-user-messages"),
      forwardSubagentText: process.argv.includes("--forward-subagent-text"),
      safeMode: process.argv.includes("--safe-mode"),
      writeFiles: getOptionalArgs("write-file"),
      useTmux: process.argv.includes("--tmux") || process.argv.includes("--use-tmux"),
      disableAutoMemory: process.argv.includes("--disable-auto-memory")
    })
  );
} else if (command === "thread-start") {
  print(
    startThread({
      prompt: getArg("prompt", ""),
      topic: getArg("topic", ""),
      profile: getArg("profile", "advisor"),
      model: getArg("model"),
      effort: getArg("effort"),
      cwd: getArg("cwd", process.cwd()),
      useTmux: process.argv.includes("--tmux") || process.argv.includes("--use-tmux")
    })
  );
} else if (command === "thread-send") {
  print(
    sendThread({
      thread_id: getArg("thread-id"),
      prompt: getArg("prompt", ""),
      cwd: getArg("cwd"),
      profile: getArg("profile"),
      useTmux: process.argv.includes("--tmux") || process.argv.includes("--use-tmux")
    })
  );
} else if (command === "threads") {
  print(
    listThreads({
      cwd: getArg("cwd"),
      includeArchived: process.argv.includes("--include-archived")
    })
  );
} else if (command === "thread-archive") {
  print(
    archiveThread({
      thread_id: getArg("thread-id"),
      archived: !process.argv.includes("--unarchive")
    })
  );
} else if (command === "peek") {
  print(
    peekRun(getArg("run-id"), {
      limit: Number(getArg("limit", 12)),
      cursor: Number(getArg("cursor", 0))
    })
  );
} else if (command === "wait") {
  print(await waitRun(getArg("run-id")));
} else if (command === "kill") {
  print(killRun(getArg("run-id")));
} else if (command === "result") {
  print(resultRun(getArg("run-id")));
} else if (command === "discover-skills") {
  print(discoverSkills({ cwd: getArg("cwd", process.cwd()) }));
} else if (command === "audit-skill") {
  print(
    await auditSkill({
      skillPath: getArg("skill-path"),
      prompt: getArg("prompt"),
      cwd: getArg("cwd", process.cwd())
    })
  );
} else if (command === "cleanup") {
  print(
    cleanupRuns({
      olderThanDays: Number(getArg("days", 14)),
      confirm: process.argv.includes("--confirm")
    })
  );
} else {
  process.stderr.write(`Unknown command: ${command}\n`);
  process.exitCode = 1;
}
