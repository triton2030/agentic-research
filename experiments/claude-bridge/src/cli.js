#!/usr/bin/env node
import {
  auditSkill,
  cleanupRuns,
  discoverSkills,
  doctor,
  killRun,
  peekRun,
  profiles,
  resultRun,
  startRun,
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

const command = process.argv[2] || "help";

if (command === "help") {
  process.stdout.write(`Usage:
  node src/cli.js doctor
  node src/cli.js profiles
  node src/cli.js run --prompt "..." [--profile normal] [--cwd /path]
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
      profile: getArg("profile", "normal"),
      cwd: getArg("cwd", process.cwd()),
      title: getArg("title"),
      maxTurns: getArg("max-turns"),
      disableAutoMemory: process.argv.includes("--disable-auto-memory")
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
