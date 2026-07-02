#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function usage() {
  console.log(`Usage:
  design-review-progress.mjs init --run-dir DIR --index group-reviews/index.json --parallel N
  design-review-progress.mjs group --run-dir DIR --id GROUP --status pending|running|done|failed [--pid PID] [--exit-code N]
  design-review-progress.mjs aggregate --run-dir DIR --status pending|running|done|failed [--output FILE] [--log FILE] [--exit-code N]
  design-review-progress.mjs stage --run-dir DIR --stage group-review|aggregate-review|complete|failed
  design-review-progress.mjs heartbeat --run-dir DIR
  design-review-progress.mjs summary --run-dir DIR

Writes <run-dir>/progress.json and <run-dir>/progress.md for long-running clean
design-review fanout.`);
}

const GROUP_STATUSES = new Set(["pending", "running", "done", "failed"]);
const AGGREGATE_STATUSES = new Set(["pending", "running", "done", "failed"]);
const STAGES = new Set(["group-review", "aggregate-review", "complete", "failed"]);

function parseArgs(argv) {
  const [command, ...rest] = argv;
  if (!command || command === "-h" || command === "--help") {
    usage();
    process.exit(command ? 0 : 2);
  }

  const options = { command };
  for (let index = 0; index < rest.length; index += 1) {
    const arg = rest[index];
    const value = rest[index + 1];
    switch (arg) {
      case "--run-dir":
        options.runDir = value ?? "";
        index += 1;
        break;
      case "--index":
        options.index = value ?? "";
        index += 1;
        break;
      case "--parallel":
        options.parallel = value ?? "";
        index += 1;
        break;
      case "--id":
        options.id = value ?? "";
        index += 1;
        break;
      case "--status":
        options.status = value ?? "";
        index += 1;
        break;
      case "--pid":
        options.pid = value ?? "";
        index += 1;
        break;
      case "--exit-code":
        options.exitCode = value ?? "";
        index += 1;
        break;
      case "--output":
        options.output = value ?? "";
        index += 1;
        break;
      case "--log":
        options.log = value ?? "";
        index += 1;
        break;
      case "--stage":
        options.stage = value ?? "";
        index += 1;
        break;
      default:
        throw new Error(`unknown argument: ${arg}`);
    }
  }

  if (!options.runDir) throw new Error("--run-dir is required");
  return options;
}

function now() {
  return new Date().toISOString();
}

function progressPaths(runDir) {
  return {
    json: path.join(runDir, "progress.json"),
    markdown: path.join(runDir, "progress.md"),
    lock: path.join(runDir, ".progress.lock"),
  };
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function withProgressLock(runDir, fn) {
  const { lock } = progressPaths(runDir);
  const deadline = Date.now() + 60_000;
  while (true) {
    try {
      await fs.mkdir(lock);
      break;
    } catch (error) {
      if (error?.code !== "EEXIST") throw error;
      try {
        const stat = await fs.stat(lock);
        if (Date.now() - stat.mtimeMs > 5 * 60_000) {
          await fs.rm(lock, { recursive: true, force: true });
          continue;
        }
      } catch (statError) {
        if (statError?.code !== "ENOENT") throw statError;
      }
      if (Date.now() > deadline) {
        throw new Error(`timed out waiting for progress lock: ${lock}`);
      }
      await sleep(100);
    }
  }

  try {
    return await fn();
  } finally {
    await fs.rm(lock, { recursive: true, force: true });
  }
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function readProgress(runDir) {
  return readJson(progressPaths(runDir).json);
}

function statusCounts(groups) {
  const counts = { pending: 0, running: 0, done: 0, failed: 0 };
  for (const group of groups) {
    counts[group.status] = (counts[group.status] ?? 0) + 1;
  }
  return counts;
}

function terminalStatus(status) {
  return status === "done" || status === "failed";
}

function parseInteger(value, label, { min = Number.NEGATIVE_INFINITY } = {}) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isInteger(parsed) || String(parsed) !== String(value)) {
    throw new Error(`${label} must be an integer`);
  }
  if (parsed < min) {
    throw new Error(`${label} must be >= ${min}`);
  }
  return parsed;
}

function assertAllowed(value, allowed, label) {
  if (!allowed.has(value)) {
    throw new Error(`${label} must be one of: ${[...allowed].join(", ")}`);
  }
}

function renderMarkdown(progress) {
  const counts = statusCounts(progress.groups);
  const total = progress.groups.length;
  const lines = [
    "# Design Review Progress",
    "",
    `Run directory: ${progress.runDir}`,
    `Stage: ${progress.stage}`,
    `Started: ${progress.startedAt}`,
    `Updated: ${progress.updatedAt}`,
    `Last heartbeat: ${progress.lastHeartbeatAt || ""}`,
    `Parallel group reviewers: ${progress.parallel}`,
    "",
    "## Summary",
    "",
    `- Groups: ${counts.done}/${total} done, ${counts.running} running, ${counts.pending} pending, ${counts.failed} failed`,
    `- Aggregate: ${progress.aggregate.status}`,
    "",
    "## Groups",
    "",
    "| group | status | images | pid | exit | started | ended | log | output |",
    "| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |",
  ];

  for (const group of progress.groups) {
    lines.push(
      `| ${group.id} | ${group.status} | ${group.imageCount} | ${group.pid ?? ""} | ${group.exitCode ?? ""} | ${group.startedAt ?? ""} | ${group.endedAt ?? ""} | ${group.log} | ${group.output} |`,
    );
  }

  lines.push(
    "",
    "## Aggregate",
    "",
    `- Status: ${progress.aggregate.status}`,
    `- Output: ${progress.aggregate.output || ""}`,
    `- Log: ${progress.aggregate.log || ""}`,
    `- Exit code: ${progress.aggregate.exitCode ?? ""}`,
  );

  return `${lines.join("\n")}\n`;
}

async function writeProgress(runDir, progress) {
  progress.updatedAt = now();
  const paths = progressPaths(runDir);
  const jsonTmp = `${paths.json}.${process.pid}.${Date.now()}.tmp`;
  await fs.writeFile(jsonTmp, `${JSON.stringify(progress, null, 2)}\n`, "utf8");
  await fs.rename(jsonTmp, paths.json);
  await fs.writeFile(paths.markdown, renderMarkdown(progress), "utf8");
}

async function initProgress(options) {
  if (!options.index) throw new Error("--index is required for init");
  const runDir = path.resolve(options.runDir);
  const index = await readJson(options.index);
  const startedAt = now();
  const parallel = Number.parseInt(options.parallel || "1", 10);
  if (!Number.isInteger(parallel) || parallel < 1) {
    throw new Error("--parallel must be a positive integer");
  }

  const progress = {
    version: 1,
    runDir,
    stage: "group-review",
    parallel,
    startedAt,
    updatedAt: startedAt,
    lastHeartbeatAt: startedAt,
    groups: index.groups.map((group) => ({
      id: group.id,
      status: "pending",
      imageCount: group.images.length,
      prompt: group.prompt,
      output: group.output,
      log: group.log,
      pid: null,
      exitCode: null,
      startedAt: null,
      endedAt: null,
    })),
    aggregate: {
      status: "pending",
      output: "",
      log: "",
      exitCode: null,
      startedAt: null,
      endedAt: null,
    },
  };
  await withProgressLock(runDir, async () => {
    await writeProgress(runDir, progress);
  });
  console.log(progressPaths(runDir).markdown);
}

async function updateGroup(options) {
  if (!options.id) throw new Error("--id is required for group");
  if (!options.status) throw new Error("--status is required for group");
  assertAllowed(options.status, GROUP_STATUSES, "--status");
  const runDir = path.resolve(options.runDir);
  await withProgressLock(runDir, async () => {
    const progress = await readProgress(runDir);
    const group = progress.groups.find((item) => item.id === options.id);
    if (!group) throw new Error(`unknown group: ${options.id}`);

    if (!(options.status === "running" && terminalStatus(group.status))) {
      group.status = options.status;
    }
    if (options.pid) group.pid = parseInteger(options.pid, "--pid", { min: 1 });
    if (options.exitCode !== undefined) group.exitCode = parseInteger(options.exitCode, "--exit-code", { min: 0 });
    if (options.status === "running" && !group.startedAt) group.startedAt = now();
    if (terminalStatus(options.status)) group.endedAt = now();

    await writeProgress(runDir, progress);
  });
}

async function updateAggregate(options) {
  if (!options.status) throw new Error("--status is required for aggregate");
  assertAllowed(options.status, AGGREGATE_STATUSES, "--status");
  const runDir = path.resolve(options.runDir);
  await withProgressLock(runDir, async () => {
    const progress = await readProgress(runDir);
    progress.aggregate.status = options.status;
    if (options.output) progress.aggregate.output = options.output;
    if (options.log) progress.aggregate.log = options.log;
    if (options.exitCode !== undefined) {
      progress.aggregate.exitCode = parseInteger(options.exitCode, "--exit-code", { min: 0 });
    }
    if (options.status === "running" && !progress.aggregate.startedAt) progress.aggregate.startedAt = now();
    if (terminalStatus(options.status)) progress.aggregate.endedAt = now();
    await writeProgress(runDir, progress);
  });
}

async function updateStage(options) {
  if (!options.stage) throw new Error("--stage is required");
  assertAllowed(options.stage, STAGES, "--stage");
  const runDir = path.resolve(options.runDir);
  await withProgressLock(runDir, async () => {
    const progress = await readProgress(runDir);
    if (options.stage === "complete") {
      const unfinished = progress.groups.filter((group) => group.status !== "done");
      if (unfinished.length > 0 || progress.aggregate.status !== "done") {
        throw new Error("cannot mark complete before all groups and aggregate are done");
      }
    }
    progress.stage = options.stage;
    await writeProgress(runDir, progress);
  });
}

async function recordHeartbeat(options) {
  const runDir = path.resolve(options.runDir);
  await withProgressLock(runDir, async () => {
    const progress = await readProgress(runDir);
    progress.lastHeartbeatAt = now();
    await writeProgress(runDir, progress);
  });
}

async function printSummary(options) {
  const runDir = path.resolve(options.runDir);
  const progress = await readProgress(runDir);
  const counts = statusCounts(progress.groups);
  const total = progress.groups.length;
  console.log(
    `[design-review-progress] stage=${progress.stage} groups=${counts.done}/${total} done running=${counts.running} pending=${counts.pending} failed=${counts.failed} aggregate=${progress.aggregate.status} file=${progressPaths(runDir).markdown}`,
  );
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  switch (options.command) {
    case "init":
      await initProgress(options);
      break;
    case "group":
      await updateGroup(options);
      break;
    case "aggregate":
      await updateAggregate(options);
      break;
    case "stage":
      await updateStage(options);
      break;
    case "heartbeat":
      await recordHeartbeat(options);
      break;
    case "summary":
      await printSummary(options);
      break;
    default:
      throw new Error(`unknown command: ${options.command}`);
  }
}

main().catch((error) => {
  console.error(`design-review-progress: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
