#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function usage() {
  console.log(`Usage:
  prepare-design-review-tasks.mjs --run-dir DIR --questions FILE

Creates exactly one clean-review task for every ready task in manifest.json.
No lens multiplication and no aggregate task are produced.`);
}

function parseArgs(argv) {
  const options = { runDir: "", questions: "" };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    const value = argv[index + 1];
    if (argument === "--run-dir") {
      options.runDir = value ?? "";
      index += 1;
    } else if (argument === "--questions") {
      options.questions = value ?? "";
      index += 1;
    } else if (argument === "-h" || argument === "--help") {
      usage();
      process.exit(0);
    } else {
      throw new Error(`unknown argument: ${argument}`);
    }
  }
  if (!options.runDir) throw new Error("--run-dir is required");
  if (!options.questions) throw new Error("--questions is required");
  return options;
}

function safeName(value) {
  const name = String(value);
  if (!/^[A-Za-z0-9][A-Za-z0-9_.-]*$/.test(name)) {
    throw new Error(`unsafe task id: ${value}`);
  }
  return name;
}

function reviewerPrompt({ task, artifacts, context, questions }) {
  const evidenceLedger = artifacts.map((artifact) => ({
    id: artifact.id,
    kind: artifact.kind,
    file: artifact.file,
    viewport: artifact.viewport,
    targetRect: artifact.targetRect,
    contextRect: artifact.contextRect,
    members: artifact.members,
    containers: artifact.containers,
    warnings: artifact.warnings,
    stats: artifact.stats,
  }));
  return `You are one clean visual design reviewer.

You are intentionally isolated. Do not search for project files, code, chat
history, local instructions, other findings, or root interpretation. Inspect
only the attached PNG evidence and the manifest excerpt below. Answer in
Russian.

QUESTION: ${task.question}
DECISION THIS ANSWER MAY CHANGE: ${task.decision}

CONTEXT:
- audience: ${context.audience ?? "unknown"}
- primary action: ${context.primaryAction ?? "unknown"}
- intended character: ${context.intendedCharacter ?? "unknown"}
- taste constraints: ${Array.isArray(context.tasteConstraints) ? context.tasteConstraints.join(" | ") : (context.tasteConstraints ?? "unknown")}

EVIDENCE MANIFEST:
${JSON.stringify(evidenceLedger, null, 2)}

REVIEW CONTRACT:
${questions}
`;
}

async function writeJson(filePath, value) {
  const temporary = `${filePath}.${process.pid}.tmp`;
  await fs.writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await fs.rename(temporary, filePath);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const runDir = path.resolve(options.runDir);
  const questionsPath = path.resolve(options.questions);
  const manifest = JSON.parse(await fs.readFile(path.join(runDir, "manifest.json"), "utf8"));
  const questions = await fs.readFile(questionsPath, "utf8");
  if (Array.isArray(manifest.failures) && manifest.failures.length > 0) {
    throw new Error(`manifest has ${manifest.failures.length} failure(s); repair capture before fanout`);
  }
  const artifactById = new Map(manifest.artifacts.map((artifact) => [artifact.id, artifact]));
  const reviewRoot = path.join(runDir, "reviewers");
  await fs.mkdir(reviewRoot, { recursive: true });
  const reviewTasks = [];
  const taskDirectories = new Set();

  for (const task of manifest.tasks) {
    if (task.status !== "ready") throw new Error(`task ${task.id} is not ready`);
    const artifacts = task.evidenceIds.map((id) => artifactById.get(id));
    if (artifacts.some((artifact) => !artifact || artifact.status !== "success")) {
      throw new Error(`task ${task.id} references unavailable evidence`);
    }
    const taskDirectory = safeName(task.id);
    if (taskDirectories.has(taskDirectory)) {
      throw new Error(`task directory collision: ${task.id}`);
    }
    taskDirectories.add(taskDirectory);
    const taskDir = path.join(reviewRoot, taskDirectory);
    await fs.mkdir(taskDir, { recursive: true });
    const prompt = path.join(taskDir, "prompt.md");
    const output = path.join(taskDir, "review.md");
    const log = path.join(taskDir, "codex.log");
    await fs.writeFile(
      prompt,
      reviewerPrompt({
        task,
        artifacts,
        context: manifest.context ?? {},
        questions,
      }),
      "utf8",
    );
    reviewTasks.push({
      id: task.id,
      question: task.question,
      decision: task.decision,
      evidenceIds: task.evidenceIds,
      images: artifacts.map((artifact) => artifact.file),
      prompt,
      output,
      log,
      status: "pending",
    });
  }

  const indexPath = path.join(reviewRoot, "index.json");
  await writeJson(indexPath, { version: 1, runDir, tasks: reviewTasks });
  console.log(indexPath);
}

main().catch((error) => {
  console.error(`prepare-design-review-tasks: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
