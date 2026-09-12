#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { createHash } from "node:crypto";

function usage() {
  console.log(`Usage:
  prepare-design-review-tasks.mjs --run-dir DIR --questions FILE

Creates exactly one clean-review task with exactly one PNG for every ready task
in manifest.json. No lens multiplication and no aggregate task are produced.`);
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

function pngDimensions(buffer, id) {
  if (buffer.length < 24 || buffer.toString("ascii", 1, 4) !== "PNG") {
    throw new Error(`evidence is not a valid PNG: ${id}`);
  }
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

async function verifyApprovedArtifact(artifact, approved) {
  if (!approved) throw new Error(`evidence lacks pixel-bound root approval: ${artifact.id}`);
  const canonicalPath = await fs.realpath(artifact.file);
  const bytes = await fs.readFile(canonicalPath);
  const dimensions = pngDimensions(bytes, artifact.id);
  const fingerprint = {
    canonicalPath,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    size: bytes.length,
    ...dimensions,
  };
  for (const key of ["canonicalPath", "sha256", "size", "width", "height"]) {
    if (approved[key] !== fingerprint[key]) {
      throw new Error(`approved PNG changed after root inspection: ${artifact.id}`);
    }
  }
  return canonicalPath;
}

function reviewerPrompt({ task, artifacts, context, questions }) {
  const evidenceLedger = (() => {
    const artifact = artifacts[0];
    return {
    id: artifact.id,
    kind: artifact.kind,
    viewport: artifact.viewport,
    targetRect: artifact.targetRect,
    contextRect: artifact.contextRect,
    members: artifact.members,
    containers: artifact.containers,
    warnings: artifact.warnings,
      stats: artifact.stats,
    };
  })();
  return `You are one clean visual design reviewer.

You are intentionally isolated. Do not search for project files, code, chat
history, local instructions, other findings, or root interpretation. Inspect
only the one attached narrow PNG and the manifest excerpt below. Answer in
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
  const manifestPath = path.join(runDir, "manifest.json");
  const manifestRaw = await fs.readFile(manifestPath, "utf8");
  const manifest = JSON.parse(manifestRaw);
  if (Array.isArray(manifest.failures) && manifest.failures.length > 0) {
    throw new Error(`manifest has ${manifest.failures.length} failure(s); repair capture before fanout`);
  }
  let approvalRaw;
  try {
    approvalRaw = await fs.readFile(path.join(runDir, "root-approval.json"), "utf8");
  } catch (error) {
    if (error?.code === "ENOENT") throw new Error("root approval is missing");
    throw error;
  }
  const approval = JSON.parse(approvalRaw);
  if (approval.version !== 2) throw new Error("unsupported or stale root approval version");
  const manifestSha256 = createHash("sha256").update(manifestRaw).digest("hex");
  if (approval.manifestSha256 !== manifestSha256) {
    throw new Error("root approval is stale for the current manifest");
  }
  const approvedEvidenceIds = new Set(approval.approvedEvidenceIds ?? []);
  const approvedArtifactById = new Map(
    (approval.approvedArtifacts ?? []).map((artifact) => [artifact.id, artifact]),
  );
  const questions = await fs.readFile(questionsPath, "utf8");
  const artifactById = new Map(manifest.artifacts.map((artifact) => [artifact.id, artifact]));
  const reviewRoot = path.join(runDir, "reviewers");
  await fs.mkdir(reviewRoot, { recursive: true });
  const reviewTasks = [];
  const taskDirectories = new Set();
  const assignedEvidenceIds = new Set();
  const assignedCanonicalPaths = new Set();

  for (const task of manifest.tasks) {
    if (task.status !== "ready") throw new Error(`task ${task.id} is not ready`);
    const artifacts = task.evidenceIds.map((id) => artifactById.get(id));
    if (task.evidenceIds.length !== 1 || artifacts.length !== 1) {
      throw new Error(`task ${task.id} must resolve to exactly one PNG`);
    }
    if (artifacts.some((artifact) => !artifact || artifact.status !== "success")) {
      throw new Error(`task ${task.id} references unavailable evidence`);
    }
    if (artifacts[0].reviewAudience !== "reviewer") {
      throw new Error(`task ${task.id} references root-only evidence`);
    }
    if (!approvedEvidenceIds.has(task.evidenceIds[0])) {
      throw new Error(`task ${task.id} evidence lacks root approval`);
    }
    const canonicalPath = await verifyApprovedArtifact(
      artifacts[0],
      approvedArtifactById.get(task.evidenceIds[0]),
    );
    if (assignedCanonicalPaths.has(canonicalPath)) {
      throw new Error(`one physical PNG is assigned to multiple reviewer tasks: ${canonicalPath}`);
    }
    assignedCanonicalPaths.add(canonicalPath);
    if (assignedEvidenceIds.has(task.evidenceIds[0])) {
      throw new Error(`evidence ${task.evidenceIds[0]} is assigned to multiple reviewer tasks`);
    }
    assignedEvidenceIds.add(task.evidenceIds[0]);
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
      images: [canonicalPath],
      imageSha256: approvedArtifactById.get(task.evidenceIds[0]).sha256,
      prompt,
      output,
      log,
      status: "pending",
    });
  }
  const unassignedEvidenceIds = manifest.artifacts
    .filter(
      (artifact) =>
        artifact.status === "success" &&
        artifact.reviewAudience === "reviewer" &&
        !assignedEvidenceIds.has(artifact.id),
    )
    .map((artifact) => artifact.id);
  if (unassignedEvidenceIds.length > 0) {
    throw new Error(`reviewer evidence has no task: ${unassignedEvidenceIds.join(", ")}`);
  }
  if (reviewTasks.length === 0) throw new Error("reviewer queue is empty");

  const indexPath = path.join(reviewRoot, "index.json");
  await writeJson(indexPath, { version: 1, runDir, tasks: reviewTasks });
  console.log(indexPath);
}

main().catch((error) => {
  console.error(`prepare-design-review-tasks: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
