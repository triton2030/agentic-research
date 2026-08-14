#!/usr/bin/env node
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function usage() {
  console.log(`Usage:
  approve-design-evidence.mjs --run-dir DIR --all-reviewer-evidence
  approve-design-evidence.mjs --run-dir DIR --evidence ID [--evidence ID ...]

Run only after root has opened every selected PNG and confirmed its target,
state, context, and readability.`);
}

function parseArgs(argv) {
  const options = { runDir: "", evidenceIds: [], all: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--run-dir") {
      options.runDir = argv[index + 1] ?? "";
      index += 1;
    } else if (argument === "--evidence") {
      options.evidenceIds.push(argv[index + 1] ?? "");
      index += 1;
    } else if (argument === "--all-reviewer-evidence") {
      options.all = true;
    } else if (argument === "-h" || argument === "--help") {
      usage();
      process.exit(0);
    } else {
      throw new Error(`unknown argument: ${argument}`);
    }
  }
  if (!options.runDir) throw new Error("--run-dir is required");
  if (options.all === (options.evidenceIds.length > 0)) {
    throw new Error("choose --all-reviewer-evidence or one or more --evidence IDs");
  }
  return options;
}

function pngDimensions(buffer, id) {
  if (buffer.length < 24 || buffer.toString("ascii", 1, 4) !== "PNG") {
    throw new Error(`evidence is not a valid PNG: ${id}`);
  }
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

async function artifactFingerprint(artifact) {
  const canonicalPath = await fs.realpath(artifact.file);
  const bytes = await fs.readFile(canonicalPath);
  const dimensions = pngDimensions(bytes, artifact.id);
  return {
    id: artifact.id,
    canonicalPath,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    size: bytes.length,
    ...dimensions,
  };
}

async function writeJson(filePath, value) {
  const temporary = `${filePath}.${process.pid}.tmp`;
  await fs.writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await fs.rename(temporary, filePath);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const runDir = path.resolve(options.runDir);
  const manifestPath = path.join(runDir, "manifest.json");
  const manifestRaw = await fs.readFile(manifestPath, "utf8");
  const manifest = JSON.parse(manifestRaw);
  const artifactById = new Map(manifest.artifacts.map((artifact) => [artifact.id, artifact]));
  const evidenceIds = options.all
    ? manifest.tasks.flatMap((task) => task.evidenceIds)
    : options.evidenceIds;
  const uniqueIds = [...new Set(evidenceIds)];
  if (uniqueIds.length === 0) throw new Error("no reviewer evidence selected");
  for (const id of uniqueIds) {
    const artifact = artifactById.get(id);
    if (!artifact || artifact.status !== "success") {
      throw new Error(`evidence is unavailable: ${id}`);
    }
    if (artifact.reviewAudience !== "reviewer") {
      throw new Error(`evidence is root-only: ${id}`);
    }
  }
  const approvedArtifacts = await Promise.all(
    uniqueIds.map((id) => artifactFingerprint(artifactById.get(id))),
  );
  const canonicalPaths = approvedArtifacts.map((artifact) => artifact.canonicalPath);
  if (new Set(canonicalPaths).size !== canonicalPaths.length) {
    throw new Error("one physical PNG is assigned to multiple reviewer evidence ids");
  }
  const approvalPath = path.join(runDir, "root-approval.json");
  await writeJson(approvalPath, {
    version: 2,
    manifestSha256: createHash("sha256").update(manifestRaw).digest("hex"),
    approvedEvidenceIds: uniqueIds,
    approvedArtifacts,
    approvedAt: new Date().toISOString(),
  });
  console.log(approvalPath);
}

main().catch((error) => {
  console.error(`approve-design-evidence: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
