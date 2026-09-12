import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs/promises";
import { existsSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync, spawn } from "node:child_process";

const packageRoot = path.resolve(import.meta.dirname, "..");
const entryScript = path.join(packageRoot, "scripts", "design-review");
const approvalScript = path.join(packageRoot, "scripts", "approve-design-evidence.mjs");
const captureScript = path.join(packageRoot, "scripts", "capture-design-screenshots.mjs");
const prepareScript = path.join(packageRoot, "scripts", "prepare-design-review-tasks.mjs");
const runnerScript = path.join(packageRoot, "scripts", "run-clean-design-agent.sh");
const fixturePath = path.join(import.meta.dirname, "fixtures", "evidence-page.html");
const templatePath = path.join(import.meta.dirname, "fixtures", "evidence-plan.template.json");
const questionsPath = path.join(packageRoot, "questions.md");

function playwrightRoot() {
  const candidates = [process.env.PLAYWRIGHT_MODULE_ROOT];
  try {
    candidates.push(execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim());
  } catch {
    // The integration test will be skipped when no reviewed runtime is present.
  }
  return candidates.find((candidate) => candidate && existsSync(path.join(candidate, "playwright")));
}

function loadPlaywright(root) {
  const requireFromRoot = createRequire(path.join(root, "__design-review-test__.cjs"));
  return requireFromRoot("playwright");
}

function pngDimensions(buffer) {
  assert.equal(buffer.toString("ascii", 1, 4), "PNG");
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function minimalPng(width = 1, height = 1) {
  const buffer = Buffer.alloc(24);
  buffer.write("\x89PNG\r\n\x1a\n", 0, "latin1");
  buffer.writeUInt32BE(width, 16);
  buffer.writeUInt32BE(height, 20);
  return buffer;
}

async function imageColorStats(playwright, imagePath) {
  const buffer = await fs.readFile(imagePath);
  const browser = await playwright.chromium.launch({ headless: true });
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    const stats = await page.evaluate(async (dataUrl) => {
      const image = new Image();
      image.src = dataUrl;
      await image.decode();
      const canvas = document.createElement("canvas");
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      const drawing = canvas.getContext("2d", { willReadFrequently: true });
      drawing.drawImage(image, 0, 0);
      const data = drawing.getImageData(0, 0, canvas.width, canvas.height).data;
      let red = 0;
      let white = 0;
      const saturated = new Set();
      for (let index = 0; index < data.length; index += 16) {
        const r = data[index];
        const g = data[index + 1];
        const b = data[index + 2];
        if (r > 225 && g < 70 && b < 80) red += 1;
        if (r > 248 && g > 248 && b > 248) white += 1;
        if (Math.max(r, g, b) - Math.min(r, g, b) > 45) {
          saturated.add(`${Math.round(r / 16)}-${Math.round(g / 16)}-${Math.round(b / 16)}`);
        }
      }
      return { red, white, saturatedColorBuckets: saturated.size };
    }, `data:image/png;base64,${buffer.toString("base64")}`);
    return stats;
  } finally {
    await browser.close();
  }
}

function run(command, args, options = {}) {
  return new Promise((resolve) => {
    const child = spawn(command, args, options);
    let stdout = "";
    let stderr = "";
    child.stdout?.setEncoding("utf8");
    child.stderr?.setEncoding("utf8");
    child.stdout?.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr?.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("close", (status) => resolve({ status, stdout, stderr }));
  });
}

test("CLI resolves project runs under the skill-name and MM-DD hierarchy", async () => {
  const projectRoot = await fs.mkdtemp(path.join(os.tmpdir(), "design-review-route-"));
  const planPath = path.join(projectRoot, "plan.json");
  await fs.writeFile(planPath, "{}\n");

  const result = await run(
    "bash",
    [entryScript, "--project", projectRoot, "--plan", planPath, "--label", "route", "--dry-run"],
  );
  assert.equal(result.status, 0, result.stderr || result.stdout);
  const runLine = result.stdout
    .split("\n")
    .find((line) => line.startsWith("[design-review] run_dir: "));
  assert.ok(runLine, result.stdout);
  const runDir = runLine.slice("[design-review] run_dir: ".length);
  assert.match(
    runDir,
    /\/_workspace\/design\/1design-review\/\d{2}-\d{2}\/\d{8}T\d{6}-route$/,
  );
});

test("runner preserves a sixty-task one-image queue and rejects parallelism above three", async () => {
  const runDir = await fs.mkdtemp(path.join(os.tmpdir(), "design-review-long-queue-"));
  const fakeRoot = await fs.mkdtemp(path.join(os.tmpdir(), "design-review-fake-cli-"));
  const fakeBin = path.join(fakeRoot, "bin");
  const fakeAuth = path.join(fakeRoot, "auth.json");
  const concurrencyRoot = path.join(fakeRoot, "concurrency");
  await fs.mkdir(fakeBin);
  await fs.mkdir(concurrencyRoot);
  await fs.writeFile(
    path.join(fakeBin, "codex"),
    `#!/bin/sh
output=""
image=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--output-last-message" ]; then output="$2"; shift 2; else shift; fi
  if [ "$1" = "-i" ]; then image="$2"; shift 2; fi
done
[ -n "$image" ] || exit 40
dd if="$image" of=/dev/null 2>/dev/null || exit 41
if dd if="$DESIGN_REVIEW_FORBIDDEN_FILE" of=/dev/null 2>/dev/null; then exit 44; fi
slot=""
for candidate in 1 2 3; do
  if mkdir "$DESIGN_REVIEW_TEST_CONCURRENCY/slot-$candidate" 2>/dev/null; then slot="$candidate"; break; fi
done
[ -n "$slot" ] || exit 42
trap 'rmdir "$DESIGN_REVIEW_TEST_CONCURRENCY/slot-'"$slot"'"' EXIT
if [ "$slot" = "3" ]; then
  touch "$DESIGN_REVIEW_TEST_CONCURRENCY/peak-3"
fi
task="$(basename "$(dirname "$output")")"
if ! mkdir "$DESIGN_REVIEW_TEST_CONCURRENCY/launched-$task" 2>/dev/null; then exit 43; fi
sleep 0.03
printf 'VERDICT: NO_MATERIAL_ISSUE\n' > "$output"
`,
  );
  await fs.chmod(path.join(fakeBin, "codex"), 0o755);
  await fs.writeFile(fakeAuth, "{}\n");

  const artifacts = [];
  const tasks = [];
  for (let index = 1; index <= 60; index += 1) {
    const id = `block-${String(index).padStart(2, "0")}`;
    const file = path.join(runDir, `${id}.png`);
    await fs.writeFile(file, minimalPng(index, index));
    artifacts.push({ id, kind: "block", reviewAudience: "reviewer", file, status: "success" });
    tasks.push({
      id: `task-${String(index).padStart(2, "0")}`,
      question: `Inspect narrow region ${index}`,
      decision: `region ${index}`,
      evidenceIds: [id],
      status: "ready",
    });
  }
  await fs.writeFile(
    path.join(runDir, "manifest.json"),
    `${JSON.stringify({ version: 2, failures: [], artifacts, tasks }, null, 2)}\n`,
  );
  const approval = await run(
    process.execPath,
    [approvalScript, "--run-dir", runDir, "--all-reviewer-evidence"],
  );
  assert.equal(approval.status, 0, approval.stderr || approval.stdout);
  const env = {
    ...process.env,
    CODEX_AUTH_JSON: fakeAuth,
    DESIGN_REVIEW_TEST_CONCURRENCY: concurrencyRoot,
    DESIGN_REVIEW_FORBIDDEN_FILE: artifacts[0].file,
    PATH: `${fakeBin}:${process.env.PATH}`,
  };
  const queuePromise = run(
    "bash",
    [runnerScript, "--run-dir", runDir, "--questions", questionsPath, "--parallel", "3"],
    { env },
  );
  const lockPath = path.join(runDir, "reviewers", ".runner.lock");
  for (let attempt = 0; attempt < 100 && !existsSync(lockPath); attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  assert.ok(existsSync(lockPath), "expected the first runner to hold the run lock");
  const otherRunDir = await fs.mkdtemp(path.join(os.tmpdir(), "design-review-other-run-"));
  const competingRun = await run(
    "bash",
    [runnerScript, "--run-dir", otherRunDir, "--questions", questionsPath, "--parallel", "3"],
    { env },
  );
  assert.equal(competingRun.status, 2);
  assert.match(competingRun.stderr, /global reviewer limit is three/);
  const duplicateRun = await run(
    "bash",
    [runnerScript, "--run-dir", runDir, "--questions", questionsPath, "--parallel", "3"],
    { env },
  );
  assert.equal(duplicateRun.status, 2);
  assert.match(duplicateRun.stderr, /already running/);
  const queueRun = await queuePromise;
  assert.equal(queueRun.status, 0, queueRun.stderr || queueRun.stdout);
  const summary = JSON.parse(
    await fs.readFile(path.join(runDir, "reviewers", "summary.json"), "utf8"),
  );
  assert.equal(summary.tasks.length, 60);
  assert.ok(summary.tasks.every((task) => task.status === "done"));
  const concurrencyEntries = await fs.readdir(concurrencyRoot);
  assert.equal(concurrencyEntries.filter((entry) => entry.startsWith("launched-")).length, 60);
  assert.ok(concurrencyEntries.includes("peak-3"));

  const tooWide = await run(
    "bash",
    [runnerScript, "--run-dir", runDir, "--questions", questionsPath, "--parallel", "4", "--dry-run"],
    { env },
  );
  assert.equal(tooWide.status, 2);
  assert.match(tooWide.stderr, /integer from 1 to 3/);
});

test("fixture produces all six evidence kinds, diagnostic colors, collage, and one task per question", async (t) => {
  const moduleRoot = playwrightRoot();
  if (!moduleRoot) {
    t.skip("Playwright runtime is not available");
    return;
  }
  const fixture = await fs.readFile(fixturePath);
  const server = http.createServer((request, response) => {
    response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    response.end(fixture);
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  t.after(() => new Promise((resolve) => server.close(resolve)));

  const address = server.address();
  const runDir = await fs.mkdtemp(path.join(os.tmpdir(), "design-evidence-fixture-"));
  const template = await fs.readFile(templatePath, "utf8");
  const planPath = path.join(runDir, "plan.json");
  await fs.writeFile(planPath, template.replace("__FIXTURE_URL__", `http://127.0.0.1:${address.port}/`));

  const capture = await run(
    process.execPath,
    [captureScript, "--plan", planPath, "--out-dir", runDir, "--settle-ms", "0"],
    {
      env: { ...process.env, PLAYWRIGHT_MODULE_ROOT: moduleRoot },
    },
  );
  assert.equal(capture.status, 0, capture.stderr || capture.stdout);

  const manifest = JSON.parse(await fs.readFile(path.join(runDir, "manifest.json"), "utf8"));
  assert.equal(manifest.failures.length, 0);
  assert.deepEqual(
    new Set(manifest.artifacts.map((artifact) => artifact.kind)),
    new Set(["viewport", "transition", "block", "family", "text-density", "spacing"]),
  );
  assert.ok(manifest.artifacts.every((artifact) => artifact.status === "success"));
  assert.equal(
    manifest.artifacts.find((artifact) => artifact.kind === "viewport").reviewAudience,
    "root-only",
  );
  assert.ok(
    manifest.artifacts
      .filter((artifact) => artifact.kind !== "viewport")
      .every((artifact) => artifact.reviewAudience === "reviewer"),
  );
  assert.equal(manifest.artifacts.find((artifact) => artifact.kind === "block").contextRect.ratio, 0.1);
  assert.equal(manifest.artifacts.find((artifact) => artifact.kind === "family").members.length, 4);

  const broadRunDir = await fs.mkdtemp(path.join(os.tmpdir(), "design-evidence-broad-block-"));
  const broadPlanPath = path.join(broadRunDir, "plan.json");
  await fs.writeFile(
    broadPlanPath,
    JSON.stringify({
      version: 2,
      sources: [{ id: "page", type: "url", url: `http://127.0.0.1:${address.port}/` }],
      evidence: [{ id: "too-broad", kind: "block", sourceId: "page", selector: "body" }],
      tasks: [
        {
          id: "too-broad-task",
          question: "Inspect the whole body",
          decision: "must be rejected",
          evidenceIds: ["too-broad"],
        },
      ],
    }),
  );
  const broadCapture = await run(
    process.execPath,
    [captureScript, "--plan", broadPlanPath, "--out-dir", broadRunDir, "--settle-ms", "0"],
    { env: { ...process.env, PLAYWRIGHT_MODULE_ROOT: moduleRoot } },
  );
  assert.equal(broadCapture.status, 1);
  const broadManifest = JSON.parse(
    await fs.readFile(path.join(broadRunDir, "manifest.json"), "utf8"),
  );
  assert.match(broadManifest.artifacts[0].error, /too large to isolate one visual question/);

  const playwright = loadPlaywright(moduleRoot);
  const density = manifest.artifacts.find((artifact) => artifact.kind === "text-density");
  const spacing = manifest.artifacts.find((artifact) => artifact.kind === "spacing");
  const family = manifest.artifacts.find((artifact) => artifact.kind === "family");
  const transition = manifest.artifacts.find((artifact) => artifact.kind === "transition");
  const densityStats = await imageColorStats(playwright, density.file);
  const spacingStats = await imageColorStats(playwright, spacing.file);
  assert.ok(densityStats.red > 20, `expected red density blocks, got ${JSON.stringify(densityStats)}`);
  assert.ok(densityStats.white > 20, `expected white density background, got ${JSON.stringify(densityStats)}`);
  assert.ok(
    spacingStats.saturatedColorBuckets >= 3,
    `expected multiple spacing colors, got ${JSON.stringify(spacingStats)}`,
  );
  const familySize = pngDimensions(await fs.readFile(family.file));
  assert.ok(familySize.width > 500 && familySize.height > 250, JSON.stringify(familySize));
  const transitionSize = pngDimensions(await fs.readFile(transition.file));
  assert.ok(
    transitionSize.height <= Math.floor(transition.viewport.height * 0.35),
    JSON.stringify(transitionSize),
  );

  const imageRunDir = await fs.mkdtemp(path.join(os.tmpdir(), "design-evidence-image-"));
  const imagePlanPath = path.join(imageRunDir, "plan.json");
  await fs.writeFile(
    imagePlanPath,
    JSON.stringify(
      {
        version: 2,
        sources: [{ id: "supplied", type: "image", path: manifest.artifacts[0].file }],
        evidence: [
          {
            id: "supplied-viewport",
            kind: "viewport",
            sourceId: "supplied",
          },
          {
            id: "supplied-block",
            kind: "block",
            sourceId: "supplied",
            rect: { x: 40, y: 40, width: 420, height: 260 },
          },
          {
            id: "supplied-family",
            kind: "family",
            sourceId: "supplied",
            members: [
              { id: "left", rect: { x: 40, y: 420, width: 170, height: 90 } },
              { id: "right", rect: { x: 230, y: 420, width: 170, height: 90 } },
            ],
          },
        ],
        tasks: [
          {
            id: "supplied-block-task",
            question: "Does the block crop preserve the selected pixels?",
            evidenceIds: ["supplied-block"],
            decision: "standalone block support",
          },
          {
            id: "supplied-family-task",
            question: "Does the family collage preserve the selected pixels?",
            evidenceIds: ["supplied-family"],
            decision: "standalone family support",
          },
        ],
      },
      null,
      2,
    ),
  );
  const suppliedCapture = await run(
    process.execPath,
    [captureScript, "--plan", imagePlanPath, "--out-dir", imageRunDir, "--settle-ms", "0"],
    { env: { ...process.env, PLAYWRIGHT_MODULE_ROOT: moduleRoot } },
  );
  assert.equal(suppliedCapture.status, 0, suppliedCapture.stderr || suppliedCapture.stdout);
  const suppliedManifest = JSON.parse(
    await fs.readFile(path.join(imageRunDir, "manifest.json"), "utf8"),
  );
  assert.equal(suppliedManifest.failures.length, 0);
  assert.equal(suppliedManifest.artifacts.length, 3);
  assert.ok(suppliedManifest.artifacts.every((artifact) => artifact.status === "success"));

  const unapproved = await run(
    process.execPath,
    [prepareScript, "--run-dir", runDir, "--questions", questionsPath],
  );
  assert.equal(unapproved.status, 1);
  assert.match(unapproved.stderr, /root approval is missing/);

  const approval = await run(
    process.execPath,
    [approvalScript, "--run-dir", runDir, "--all-reviewer-evidence"],
  );
  assert.equal(approval.status, 0, approval.stderr || approval.stdout);

  const approvedArtifact = manifest.artifacts.find(
    (artifact) => artifact.reviewAudience === "reviewer",
  );
  const approvedBytes = await fs.readFile(approvedArtifact.file);
  await fs.appendFile(approvedArtifact.file, Buffer.from([0]));
  const changedPixels = await run(
    process.execPath,
    [prepareScript, "--run-dir", runDir, "--questions", questionsPath],
  );
  assert.equal(changedPixels.status, 1);
  assert.match(changedPixels.stderr, /approved PNG changed/);
  await fs.writeFile(approvedArtifact.file, approvedBytes);
  const refreshedApproval = await run(
    process.execPath,
    [approvalScript, "--run-dir", runDir, "--all-reviewer-evidence"],
  );
  assert.equal(refreshedApproval.status, 0, refreshedApproval.stderr || refreshedApproval.stdout);

  const duplicateRunDir = await fs.mkdtemp(path.join(os.tmpdir(), "design-evidence-duplicate-"));
  const duplicateArtifact = { ...approvedArtifact, id: "duplicate-physical-file" };
  const duplicateManifest = {
    ...manifest,
    artifacts: [approvedArtifact, duplicateArtifact],
    tasks: [
      {
        id: "original-file-task",
        question: "Inspect original evidence",
        decision: "original",
        evidenceIds: [approvedArtifact.id],
        status: "ready",
      },
      {
        id: "duplicate-file-task",
        question: "Inspect duplicate evidence",
        decision: "duplicate",
        evidenceIds: [duplicateArtifact.id],
        status: "ready",
      },
    ],
  };
  await fs.writeFile(
    path.join(duplicateRunDir, "manifest.json"),
    `${JSON.stringify(duplicateManifest, null, 2)}\n`,
  );
  const duplicateApproval = await run(
    process.execPath,
    [approvalScript, "--run-dir", duplicateRunDir, "--all-reviewer-evidence"],
  );
  assert.equal(duplicateApproval.status, 1);
  assert.match(duplicateApproval.stderr, /one physical PNG/);

  const prepared = await run(
    process.execPath,
    [prepareScript, "--run-dir", runDir, "--questions", questionsPath],
  );
  assert.equal(prepared.status, 0, prepared.stderr || prepared.stdout);
  const taskIndex = JSON.parse(await fs.readFile(prepared.stdout.trim(), "utf8"));
  assert.equal(taskIndex.tasks.length, manifest.tasks.length);
  assert.ok(taskIndex.tasks.every((task) => !task.id.includes("--")));
  const isolatedPrompt = await fs.readFile(taskIndex.tasks[0].prompt, "utf8");
  assert.doesNotMatch(isolatedPrompt, new RegExp(runDir.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.doesNotMatch(isolatedPrompt, /viewport-hero\.png/);

  const fakeRoot = await fs.mkdtemp(path.join(os.tmpdir(), "design-review-fake-codex-"));
  const fakeBin = path.join(fakeRoot, "bin");
  const fakeCodex = path.join(fakeBin, "codex");
  const fakeAuth = path.join(fakeRoot, "auth.json");
  await fs.mkdir(fakeBin);
  await fs.writeFile(fakeCodex, "#!/bin/sh\nexit 0\n");
  await fs.chmod(fakeCodex, 0o755);
  await fs.writeFile(fakeAuth, "{}\n");
  await fs.writeFile(taskIndex.tasks[0].output, "stale review\n");
  const missingOutputRun = await run(
    "bash",
    [
      runnerScript,
      "--run-dir",
      runDir,
      "--questions",
      questionsPath,
      "--parallel",
      "2",
    ],
    {
      env: {
        ...process.env,
        CODEX_AUTH_JSON: fakeAuth,
        PATH: `${fakeBin}:${process.env.PATH}`,
      },
    },
  );
  assert.equal(missingOutputRun.status, 1, missingOutputRun.stderr || missingOutputRun.stdout);
  assert.match(missingOutputRun.stderr, /produced no output/);
  const failedSummary = JSON.parse(
    await fs.readFile(path.join(runDir, "reviewers", "summary.json"), "utf8"),
  );
  assert.ok(failedSummary.tasks.every((task) => task.status === "failed"));
});
