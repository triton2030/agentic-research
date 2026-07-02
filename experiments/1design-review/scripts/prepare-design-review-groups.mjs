#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function usage() {
  console.log(`Usage:
  prepare-design-review-groups.mjs --run-dir DIR --questions FILE [--url URL]
  prepare-design-review-groups.mjs --aggregate --run-dir DIR --questions FILE [--url URL]

Builds per-group clean-agent prompts from manifest.json. Each review group must
contain 2-3 screenshots because the main agent is expected to curate related
evidence after inspecting the page.`);
}

function parseArgs(argv) {
  const options = {
    runDir: "",
    questions: "",
    url: "",
    aggregate: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const value = argv[index + 1];
    switch (arg) {
      case "--run-dir":
        options.runDir = value ?? "";
        index += 1;
        break;
      case "--questions":
        options.questions = value ?? "";
        index += 1;
        break;
      case "--url":
        options.url = value ?? "";
        index += 1;
        break;
      case "--aggregate":
        options.aggregate = true;
        break;
      case "-h":
      case "--help":
        usage();
        process.exit(0);
        break;
      default:
        throw new Error(`unknown argument: ${arg}`);
    }
  }
  if (!options.runDir) throw new Error("--run-dir is required");
  if (!options.questions) throw new Error("--questions is required");
  return options;
}

function groupPrompt({ manifest, group, shots, questionsMarkdown, url }) {
  const imageList = shots.map((shot) => shot.file).join("\n");
  const shotLedger = shots
    .map((shot) => `- ${shot.id}: ${shot.filename}; ${shot.profile}; y=${shot.y}; ${shot.labels?.join("; ") || ""}`)
    .join("\n");

  return `You are a clean visual design subreviewer.

You are intentionally running from a neutral cwd. Do not search for or follow
project AGENTS.md, local skills, source code, git history, or chat history.
Use only the 2-3 attached screenshots, the group context, and the question
contract pasted below.

Task:
Review this screenshot group only. Return concise findings that the aggregate
design reviewer can use later. Do not answer the whole global questionnaire.
Ground every claim in screenshot filenames or ids. If evidence is missing, say
so. Output in Russian.

Captured URL: ${url || manifest.url}
Run directory: ${manifest.outDir}
Group: ${group.id}
Group purpose: ${group.purpose || "(not recorded)"}
Group questions: ${(group.questions || []).join(" | ") || "(none)"}

<attached_images>
${imageList}
</attached_images>

<group_shot_ledger>
${shotLedger}
</group_shot_ledger>

<questions_markdown>
${questionsMarkdown}
</questions_markdown>

Return this shape:

# GROUP_REVIEW ${group.id}

## Verdict
- ready/needs-pass for this group only

## Findings
- Severity: high|medium|low. Evidence: screenshot id/file. Finding.

## What Works
- Evidence-backed positives worth preserving.

## Not Checkable
- Anything this group cannot prove.
`;
}

function aggregatePrompt({ manifest, groupOutputs, questionsMarkdown, url }) {
  return `You are a clean visual design aggregate reviewer.

You are intentionally running from a neutral cwd. Do not search for or follow
project AGENTS.md, local skills, source code, git history, or chat history.
Use only the group review outputs, manifest summary, and question contract
pasted below. Do not invent evidence beyond the group outputs.

Task:
Answer the questions in the same Markdown structure as the question contract.
Be direct and critical. Ground claims in group ids and screenshot filenames.
If a question was not covered by the screenshot groups, write
\`не проверено по скриншотам\`. Output in Russian.

Captured URL: ${url || manifest.url}
Run directory: ${manifest.outDir}
Groups: ${manifest.groups.map((group) => group.id).join(", ")}

<questions_markdown>
${questionsMarkdown}
</questions_markdown>

<manifest_summary>
${JSON.stringify(
  {
    url: manifest.url,
    screenshotContract: manifest.screenshotContract,
    profiles: manifest.profiles,
    groups: manifest.groups,
    screenshotCount: manifest.screenshots.length,
    failures: manifest.failures,
  },
  null,
  2,
)}
</manifest_summary>

<group_reviews>
${groupOutputs}
</group_reviews>
`;
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function prepareGroups(options) {
  const runDir = path.resolve(options.runDir);
  const manifest = await readJson(path.join(runDir, "manifest.json"));
  const questionsMarkdown = await fs.readFile(options.questions, "utf8");
  if (!Array.isArray(manifest.groups) || manifest.groups.length === 0) {
    throw new Error("manifest has no review groups; run capture with --plan first");
  }

  const groupsDir = path.join(runDir, "group-reviews");
  await fs.mkdir(groupsDir, { recursive: true });
  const groupEntries = [];

  for (const group of manifest.groups) {
    const shots = manifest.screenshots.filter((shot) => shot.groupId === group.id);
    if (Number.isInteger(group.shotCount) && shots.length !== group.shotCount) {
      throw new Error(`group "${group.id}" has ${shots.length} captured screenshots; expected planned count ${group.shotCount}`);
    }
    if (shots.length < 2 || shots.length > 3) {
      throw new Error(`group "${group.id}" has ${shots.length} screenshots; expected 2-3`);
    }
    const groupDir = path.join(groupsDir, group.id);
    await fs.mkdir(groupDir, { recursive: true });
    const promptPath = path.join(groupDir, "prompt.md");
    const outputPath = path.join(groupDir, "review.md");
    const logPath = path.join(groupDir, "codex.log");
    const imagesPath = path.join(groupDir, "images.txt");
    await fs.writeFile(imagesPath, `${shots.map((shot) => shot.file).join("\n")}\n`, "utf8");
    await fs.writeFile(
      promptPath,
      groupPrompt({ manifest, group, shots, questionsMarkdown, url: options.url }),
      "utf8",
    );
    groupEntries.push({
      id: group.id,
      prompt: promptPath,
      output: outputPath,
      log: logPath,
      images: shots.map((shot) => shot.file),
    });
  }

  const indexPath = path.join(groupsDir, "index.json");
  await fs.writeFile(indexPath, `${JSON.stringify({ groups: groupEntries }, null, 2)}\n`, "utf8");
  console.log(indexPath);
}

async function prepareAggregate(options) {
  const runDir = path.resolve(options.runDir);
  const manifest = await readJson(path.join(runDir, "manifest.json"));
  const questionsMarkdown = await fs.readFile(options.questions, "utf8");
  const index = await readJson(path.join(runDir, "group-reviews", "index.json"));
  const outputs = [];
  for (const group of index.groups) {
    outputs.push(await fs.readFile(group.output, "utf8"));
  }
  const promptPath = path.join(runDir, "aggregate-prompt.md");
  await fs.writeFile(
    promptPath,
    aggregatePrompt({
      manifest,
      groupOutputs: outputs.join("\n\n---\n\n"),
      questionsMarkdown,
      url: options.url,
    }),
    "utf8",
  );
  console.log(promptPath);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.aggregate) {
    await prepareAggregate(options);
  } else {
    await prepareGroups(options);
  }
}

main().catch((error) => {
  console.error(`prepare-design-review-groups: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
