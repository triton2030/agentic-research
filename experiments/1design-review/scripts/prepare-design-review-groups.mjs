#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

function usage() {
  console.log(`Usage:
  prepare-design-review-groups.mjs --run-dir DIR --questions FILE [--url URL]
  prepare-design-review-groups.mjs --aggregate --run-dir DIR --questions FILE [--url URL]

Options:
  --brief FILE   Optional design direction brief. Default: <run-dir>/design-brief.md
  --comments-ledger FILE
                 Optional review-comment ledger, used only for aggregate iteration memory.

Builds per-group clean-agent prompts from manifest.json. Each review group must
contain 2-3 screenshots because the main agent is expected to curate related
evidence after inspecting the page. Questions are split into focused lens
packets so each clean reviewer handles a narrower design judgment.`);
}

const QUESTION_LENSES = [
  {
    id: "spacing-rhythm",
    title: "Spacing rhythm",
    headings: ["Space And Density", "Spacing And Padding Logic"],
  },
  {
    id: "composition-alignment",
    title: "Composition and alignment",
    headings: ["Composition", "Gestalt Grouping And Alignment", "Spatial Balance"],
  },
  {
    id: "content-typography",
    title: "Content and typography",
    headings: ["Text Load", "Hierarchy And Typography"],
  },
  {
    id: "information-model",
    title: "Information model and attention",
    headings: ["Visual Weight And Attention", "Information Model And Containers"],
  },
  {
    id: "system-components",
    title: "System and components",
    headings: ["Surface Details And Badges", "Consistency And System Logic"],
  },
  {
    id: "taste-creativity",
    title: "Taste, creativity, and visual noise",
    headings: ["Visual Noise", "Brand And Taste", "Beauty And Creative Vitality"],
  },
  {
    id: "interaction-accessibility",
    title: "Interaction and accessibility",
    headings: ["Interaction States", "Accessibility From Visual Evidence"],
  },
  {
    id: "responsive-mobile",
    title: "Responsive and mobile",
    headings: ["Mobile Scroll", "Responsiveness"],
  },
];

const AGGREGATE_ONLY_SECTIONS = new Set(["Verdict", "Fix Recommendations", "Evidence And Severity Rules"]);

function parseArgs(argv) {
  const options = {
    runDir: "",
    questions: "",
    brief: "",
    commentsLedger: "",
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
      case "--brief":
        options.brief = value ?? "";
        index += 1;
        break;
      case "--comments-ledger":
        options.commentsLedger = value ?? "";
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

function groupPrompt({ manifest, group, shots, questionsMarkdown, designBrief, url }) {
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
Review this screenshot group only through the assigned question lens. Return
concise findings that the aggregate design reviewer can use later. Do not answer
the whole global questionnaire. Ground every claim in screenshot filenames or
ids. If evidence is missing, say so. Output in Russian.
If a design brief is provided, judge taste, creativity, and restraint against
that intended character instead of pushing the screen toward generic neatness.
Use local evidence only: if a question asks about full-page scroll, system-wide
consistency, or desktop/mobile behavior beyond this group, answer only for the
attached screenshots and mark the broader claim as not checkable. Start with the
visible condition and user-visible effect; do not hunt for a defect just because
the question names one. Severity means: high blocks or seriously misleads the
primary action, comprehension, trust, accessibility, or mobile usability; medium
creates repeated friction or weakens hierarchy/character; low is limited polish.

Captured URL: ${url || manifest.url}
Run directory: ${manifest.outDir}
Group: ${group.id}
Group purpose: ${group.purpose || "(not recorded)"}
Group questions: ${(group.questions || []).join(" | ") || "(none)"}
Question lens: ${group.focusTitle}
Source screenshot group: ${group.sourceGroupId || group.id}

<attached_images>
${imageList}
</attached_images>

<group_shot_ledger>
${shotLedger}
</group_shot_ledger>

<questions_markdown>
${questionsMarkdown}
</questions_markdown>

<design_brief>
${designBrief || "No design brief was provided. Judge taste and creativity from the screenshots and product context only."}
</design_brief>

Return this shape:

# GROUP_REVIEW ${group.id}

## Verdict
- ready/needs-pass for this group and question lens only

## Findings
- Severity: high|medium|low. Evidence: screenshot id/file. Finding.

## Out Of Focus Risk
- One line only if a severe issue is visible outside this lens.

## What Works
- Evidence-backed positives worth preserving.

## Not Checkable
- Anything this group cannot prove.
`;
}

function aggregatePrompt({ manifest, groupOutputs, questionsMarkdown, designBrief, commentsLedger, url, reviewTasks }) {
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
If a design brief is provided, preserve the intended character when ranking
fixes; do not flatten the design into generic cleanliness.
You cannot see the screenshots directly. Make page-wide or system-wide claims
only from converging evidence across group outputs; otherwise mark them not
checked. Deduplicate overlapping comments before ranking severity. Do not answer
every subquestion at equal length: expand high/medium evidence-backed issues,
keep low-risk or not-checkable answers compact.
If a comments ledger is provided, use it as iteration memory, not as design law:
map repeated findings to existing rows, treat fixed/rejected/deferred/routed rows
as non-work unless fresh screenshot evidence contradicts the row, and propose
new row candidates for durable new issues. Prepend a short "## Iteration Memory"
section before the question sections when a ledger is provided.

Captured URL: ${url || manifest.url}
Run directory: ${manifest.outDir}
Groups: ${manifest.groups.map((group) => group.id).join(", ")}
Review tasks: ${reviewTasks.map((task) => `${task.id} (${task.focusTitle || "all questions"})`).join(", ")}

<questions_markdown>
${questionsMarkdown}
</questions_markdown>

<design_brief>
${designBrief || "No design brief was provided. Judge taste and creativity from the screenshots and product context only."}
</design_brief>

<comments_ledger>
${commentsLedger || "No comments ledger was provided. Treat this as a first-pass review with no iteration memory."}
</comments_ledger>

<manifest_summary>
${JSON.stringify(
  {
    url: manifest.url,
    screenshotContract: manifest.screenshotContract,
    profiles: manifest.profiles,
    groups: manifest.groups,
    reviewTasks,
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

async function readOptionalDesignBrief(runDir, explicitBriefPath) {
  const briefPath = explicitBriefPath || path.join(runDir, "design-brief.md");
  try {
    const stat = await fs.stat(briefPath);
    if (!stat.isFile()) return "";
    return (await fs.readFile(briefPath, "utf8")).trim();
  } catch (error) {
    if (error?.code === "ENOENT" && !explicitBriefPath) return "";
    throw error;
  }
}

async function readOptionalCommentsLedger(explicitLedgerPath) {
  if (!explicitLedgerPath) return "";
  return (await fs.readFile(explicitLedgerPath, "utf8")).trim();
}

function parseQuestionSections(markdown) {
  const lines = markdown.split(/\r?\n/);
  const intro = [];
  const sections = [];
  let current = null;

  for (const line of lines) {
    const heading = /^##\s+(.+?)\s*$/.exec(line);
    if (heading) {
      current = { title: heading[1], lines: [line] };
      sections.push(current);
      continue;
    }
    if (current) {
      current.lines.push(line);
    } else {
      intro.push(line);
    }
  }

  return {
    intro: intro.join("\n").trim(),
    sections: sections.map((section) => ({
      title: section.title,
      markdown: section.lines.join("\n").trim(),
    })),
  };
}

function buildQuestionBundles(questionsMarkdown) {
  const parsed = parseQuestionSections(questionsMarkdown);
  const sectionByTitle = new Map(parsed.sections.map((section) => [section.title, section]));
  const usedTitles = new Set();
  const bundles = [];

  for (const lens of QUESTION_LENSES) {
    const sections = lens.headings.map((heading) => sectionByTitle.get(heading)).filter(Boolean);
    if (sections.length === 0) continue;
    for (const section of sections) usedTitles.add(section.title);
    bundles.push({
      id: lens.id,
      title: lens.title,
      sections: sections.map((section) => section.title),
      markdown: [parsed.intro, ...sections.map((section) => section.markdown)].filter(Boolean).join("\n\n"),
    });
  }

  const leftovers = parsed.sections.filter((section) => !usedTitles.has(section.title) && !AGGREGATE_ONLY_SECTIONS.has(section.title));
  if (leftovers.length > 0) {
    bundles.push({
      id: "other",
      title: "Other design questions",
      sections: leftovers.map((section) => section.title),
      markdown: [parsed.intro, ...leftovers.map((section) => section.markdown)].filter(Boolean).join("\n\n"),
    });
  }

  if (bundles.length === 0) {
    bundles.push({
      id: "all-questions",
      title: "All design questions",
      sections: parsed.sections.map((section) => section.title),
      markdown: questionsMarkdown,
    });
  }

  return bundles;
}

async function prepareGroups(options) {
  const runDir = path.resolve(options.runDir);
  const manifest = await readJson(path.join(runDir, "manifest.json"));
  const questionsMarkdown = await fs.readFile(options.questions, "utf8");
  const designBrief = await readOptionalDesignBrief(runDir, options.brief);
  const questionBundles = buildQuestionBundles(questionsMarkdown);
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
    for (const questionBundle of questionBundles) {
      const reviewTask = {
        ...group,
        id: `${group.id}--${questionBundle.id}`,
        sourceGroupId: group.id,
        focusId: questionBundle.id,
        focusTitle: questionBundle.title,
        focusSections: questionBundle.sections,
      };
      const groupDir = path.join(groupsDir, reviewTask.id);
      await fs.mkdir(groupDir, { recursive: true });
      const promptPath = path.join(groupDir, "prompt.md");
      const outputPath = path.join(groupDir, "review.md");
      const logPath = path.join(groupDir, "codex.log");
      const imagesPath = path.join(groupDir, "images.txt");
      await fs.writeFile(imagesPath, `${shots.map((shot) => shot.file).join("\n")}\n`, "utf8");
      await fs.writeFile(
        promptPath,
        groupPrompt({
          manifest,
          group: reviewTask,
          shots,
          questionsMarkdown: questionBundle.markdown,
          designBrief,
          url: options.url,
        }),
        "utf8",
      );
      groupEntries.push({
        id: reviewTask.id,
        sourceGroupId: reviewTask.sourceGroupId,
        focusId: reviewTask.focusId,
        focusTitle: reviewTask.focusTitle,
        focusSections: reviewTask.focusSections,
        prompt: promptPath,
        output: outputPath,
        log: logPath,
        images: shots.map((shot) => shot.file),
      });
    }
  }

  const indexPath = path.join(groupsDir, "index.json");
  await fs.writeFile(indexPath, `${JSON.stringify({ groups: groupEntries }, null, 2)}\n`, "utf8");
  console.log(indexPath);
}

async function prepareAggregate(options) {
  const runDir = path.resolve(options.runDir);
  const manifest = await readJson(path.join(runDir, "manifest.json"));
  const questionsMarkdown = await fs.readFile(options.questions, "utf8");
  const designBrief = await readOptionalDesignBrief(runDir, options.brief);
  const commentsLedger = await readOptionalCommentsLedger(options.commentsLedger);
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
      designBrief,
      commentsLedger,
      url: options.url,
      reviewTasks: index.groups,
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
