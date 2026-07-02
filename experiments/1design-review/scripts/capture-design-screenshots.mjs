#!/usr/bin/env node
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";
import process from "node:process";

const PROFILE_PRESETS = {
  "desktop-1440": {
    viewport: { width: 1440, height: 810 },
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
  },
  "desktop-1080": {
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
  },
  "mobile-iphone": {
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  },
  "mobile-android": {
    viewport: { width: 412, height: 915 },
    deviceScaleFactor: 2.625,
    isMobile: true,
    hasTouch: true,
  },
};

function usage() {
  console.log(`Usage:
  capture-design-screenshots.mjs --plan screenshot-plan.json --out-dir DIR [--url URL]
  capture-design-screenshots.mjs --auto-capture --url URL --out-dir DIR [options]

Options:
  --plan FILE                 Curated screenshot plan written after page inspection.
  --auto-capture              Fallback: broad scroll/section capture without a plan.
  --profiles LIST             Comma-separated profiles.
                              Default: desktop-1440,mobile-iphone,mobile-android
  --interactions FILE         JSON interaction plan.
  --settle-ms N               Wait after load/scroll/click. Default: 1200.
  --progress-interval N       Seconds between capture progress heartbeats.
                              Default: 10.
  --step-ratio N              Scroll step as viewport fraction. Default: 0.5.
  --max-shots-per-profile N   Base screenshot cap before interactions. Default: 36.
  --timeout-ms N              Navigation/action timeout. Default: 45000.
  --headed                    Run browser headed.
  -h, --help                  Show this help.

Interaction plan:
  [
    {"name":"menu","profile":"mobile-iphone","selector":"button[aria-label='Menu']"},
    {"name":"tab","selector":"text=Pricing","scrollY":0}
  ]`);
}

function parseArgs(argv) {
  const options = {
    url: "",
    outDir: "",
    plan: "",
    autoCapture: false,
    profiles: ["desktop-1440", "mobile-iphone", "mobile-android"],
    interactions: "",
    settleMs: 1200,
    progressInterval: 10,
    stepRatio: 0.5,
    maxShotsPerProfile: 36,
    timeoutMs: 45_000,
    headed: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const value = argv[index + 1];
    switch (arg) {
      case "--url":
        options.url = value ?? "";
        index += 1;
        break;
      case "--plan":
        options.plan = value ?? "";
        index += 1;
        break;
      case "--auto-capture":
        options.autoCapture = true;
        break;
      case "--out-dir":
        options.outDir = value ?? "";
        index += 1;
        break;
      case "--profiles":
        options.profiles = (value ?? "")
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean);
        index += 1;
        break;
      case "--interactions":
        options.interactions = value ?? "";
        index += 1;
        break;
      case "--settle-ms":
        options.settleMs = Number(value);
        index += 1;
        break;
      case "--progress-interval":
        options.progressInterval = Number(value);
        index += 1;
        break;
      case "--step-ratio":
        options.stepRatio = Number(value);
        index += 1;
        break;
      case "--max-shots-per-profile":
        options.maxShotsPerProfile = Number(value);
        index += 1;
        break;
      case "--timeout-ms":
        options.timeoutMs = Number(value);
        index += 1;
        break;
      case "--headed":
        options.headed = true;
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

  if (!options.plan && !options.autoCapture) {
    throw new Error("--plan is required unless --auto-capture is explicitly used");
  }
  if (!options.url && !options.plan) throw new Error("--url is required");
  if (!options.outDir) throw new Error("--out-dir is required");
  if (!Number.isFinite(options.settleMs) || options.settleMs < 0) {
    throw new Error("--settle-ms must be >= 0");
  }
  if (!Number.isInteger(options.progressInterval) || options.progressInterval < 1) {
    throw new Error("--progress-interval must be an integer >= 1");
  }
  if (!Number.isFinite(options.stepRatio) || options.stepRatio <= 0 || options.stepRatio > 1) {
    throw new Error("--step-ratio must be > 0 and <= 1");
  }
  if (!Number.isInteger(options.maxShotsPerProfile) || options.maxShotsPerProfile < 4) {
    throw new Error("--max-shots-per-profile must be an integer >= 4");
  }
  if (!Number.isFinite(options.timeoutMs) || options.timeoutMs < 1000) {
    throw new Error("--timeout-ms must be >= 1000");
  }
  for (const profile of options.profiles) {
    if (!PROFILE_PRESETS[profile]) {
      throw new Error(`unknown profile "${profile}". Known: ${Object.keys(PROFILE_PRESETS).join(", ")}`);
    }
  }
  return options;
}

function slug(text) {
  return String(text || "state")
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60) || "state";
}

function padded(number, width = 3) {
  return String(number).padStart(width, "0");
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function now() {
  return new Date().toISOString();
}

function plannedShotId(groupId, shotIndex) {
  return `${groupId}-${padded(shotIndex + 1)}`;
}

function captureProgressPaths(outDir) {
  return {
    json: path.join(outDir, "capture-progress.json"),
    markdown: path.join(outDir, "capture-progress.md"),
  };
}

let captureWriteChain = Promise.resolve();

function serializeCaptureWrite(task) {
  const run = captureWriteChain.then(task, task);
  captureWriteChain = run.catch(() => {});
  return run;
}

function captureStatusCounts(shots) {
  const counts = { pending: 0, running: 0, done: 0, failed: 0 };
  for (const shot of shots) {
    counts[shot.status] = (counts[shot.status] ?? 0) + 1;
  }
  return counts;
}

function renderCaptureProgress(progress) {
  const counts = captureStatusCounts(progress.shots);
  const total = progress.shots.length;
  const running = progress.shots.filter((shot) => shot.status === "running").map((shot) => shot.id);
  const lines = [
    "# Capture Progress",
    "",
    `Run directory: ${progress.runDir}`,
    `Stage: ${progress.stage}`,
    `Mode: ${progress.mode}`,
    `Started: ${progress.startedAt}`,
    `Updated: ${progress.updatedAt}`,
    `Last heartbeat: ${progress.lastHeartbeatAt || ""}`,
    `URL: ${progress.url}`,
    `Fatal error: ${progress.fatalError || ""}`,
    "",
    "## Summary",
    "",
    `- Shots: ${counts.done}/${total} done, ${counts.running} running, ${counts.pending} pending, ${counts.failed} failed`,
    `- Running: ${running.join(", ") || "none"}`,
    "",
    "## Shots",
    "",
    "| shot | group | status | profile | selector | click | y | file | error |",
    "| --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
  ];

  for (const shot of progress.shots) {
    lines.push(
      `| ${shot.id} | ${shot.groupId} | ${shot.status} | ${shot.profile} | ${shot.selector || ""} | ${shot.click || ""} | ${shot.y ?? ""} | ${shot.file || ""} | ${shot.error || ""} |`,
    );
  }

  return `${lines.join("\n")}\n`;
}

async function writeCaptureProgress(outDir, progress) {
  await serializeCaptureWrite(async () => {
    progress.updatedAt = now();
    const paths = captureProgressPaths(outDir);
    const jsonTmp = `${paths.json}.${process.pid}.${Date.now()}.tmp`;
    await fs.writeFile(jsonTmp, `${JSON.stringify(progress, null, 2)}\n`, "utf8");
    await fs.rename(jsonTmp, paths.json);
    await fs.writeFile(paths.markdown, renderCaptureProgress(progress), "utf8");
  });
}

function printCaptureSummary(progress, label = "progress") {
  const counts = captureStatusCounts(progress.shots);
  const total = progress.shots.length;
  const running = progress.shots.filter((shot) => shot.status === "running").map((shot) => shot.id);
  console.error(
    `[capture-design-screenshots] ${label} stage=${progress.stage} shots=${counts.done}/${total} done running=${counts.running} pending=${counts.pending} failed=${counts.failed} current=${running.join(",") || "none"} file=${captureProgressPaths(progress.runDir).markdown}`,
  );
}

function plannedProgressShots(plan) {
  return plan.groups.flatMap((group) =>
    group.shots.map((shot, shotIndex) => ({
      id: plannedShotId(group.id, shotIndex),
      groupId: group.id,
      shotName: shot.name,
      status: "pending",
      profile: shot.profile,
      selector: shot.selector || "",
      click: shot.click || "",
      file: "",
      y: null,
      error: "",
      startedAt: null,
      endedAt: null,
    })),
  );
}

async function initCaptureProgress(outDir, { url, mode, shots = [] }) {
  const runDir = path.resolve(outDir);
  const startedAt = now();
  const progress = {
    version: 1,
    runDir,
    url,
    mode,
    stage: "capture",
    startedAt,
    updatedAt: startedAt,
    lastHeartbeatAt: startedAt,
    fatalError: "",
    shots,
  };
  await writeCaptureProgress(outDir, progress);
  printCaptureSummary(progress, "init");
  return progress;
}

async function upsertCaptureShot(outDir, progress, shotId, defaults, updates = {}) {
  const shot = progress.shots.find((item) => item.id === shotId);
  const target = shot ?? {
    id: shotId,
    groupId: "",
    shotName: "",
    status: "pending",
    profile: "",
    selector: "",
    click: "",
    file: "",
    y: null,
    error: "",
    startedAt: null,
    endedAt: null,
    ...defaults,
  };
  Object.assign(target, updates);
  if (updates.status === "running" && !target.startedAt) target.startedAt = now();
  if (updates.status === "done" || updates.status === "failed") target.endedAt = now();
  if (!shot) progress.shots.push(target);
  await writeCaptureProgress(outDir, progress);
  printCaptureSummary(progress, updates.status || "progress");
}

async function updateCaptureShot(outDir, progress, shotId, updates) {
  const shot = progress.shots.find((item) => item.id === shotId);
  if (!shot) throw new Error(`unknown capture shot: ${shotId}`);
  await upsertCaptureShot(outDir, progress, shotId, {}, updates);
}

async function recordCaptureHeartbeat(outDir, progress) {
  progress.lastHeartbeatAt = now();
  await writeCaptureProgress(outDir, progress);
  printCaptureSummary(progress, "heartbeat");
}

async function readInteractions(filePath) {
  if (!filePath) return [];
  const raw = await fs.readFile(filePath, "utf8");
  const parsed = JSON.parse(raw);
  const interactions = Array.isArray(parsed) ? parsed : parsed.interactions;
  if (!Array.isArray(interactions)) {
    throw new Error("interaction plan must be a JSON array or { interactions: [...] }");
  }
  return interactions.map((item, index) => ({
    name: slug(item.name ?? `interaction-${index + 1}`),
    profile: item.profile ?? "",
    selector: item.selector ?? "",
    scrollY: item.scrollY,
    beforeSelector: item.beforeSelector ?? "",
  }));
}

async function readScreenshotPlan(filePath, fallbackUrl) {
  if (!filePath) return null;
  const raw = await fs.readFile(filePath, "utf8");
  const plan = JSON.parse(raw);
  const groups = Array.isArray(plan.groups) ? plan.groups : [];
  if (groups.length === 0) {
    throw new Error("screenshot plan must contain a non-empty groups array");
  }

  const normalizedGroups = groups.map((group, groupIndex) => {
    const id = slug(group.id ?? `group-${groupIndex + 1}`);
    const shots = Array.isArray(group.shots) ? group.shots : [];
    if (shots.length < 2 || shots.length > 3) {
      throw new Error(`group "${id}" must contain 2-3 related shots`);
    }
    return {
      id,
      purpose: String(group.purpose ?? group.notes ?? "").trim(),
      questions: Array.isArray(group.questions) ? group.questions.map(String) : [],
      shots: shots.map((shot, shotIndex) => {
        const profile = shot.profile ?? group.profile ?? "desktop-1440";
        if (!PROFILE_PRESETS[profile]) {
          throw new Error(`group "${id}" shot ${shotIndex + 1} uses unknown profile "${profile}"`);
        }
        return {
          name: slug(shot.name ?? `shot-${shotIndex + 1}`),
          profile,
          selector: shot.selector ?? "",
          scrollY: shot.scrollY,
          scrollBy: shot.scrollBy,
          click: shot.click ?? "",
          waitMs: shot.waitMs,
          notes: String(shot.notes ?? "").trim(),
        };
      }),
    };
  });

  return {
    url: plan.url || fallbackUrl,
    notes: String(plan.notes ?? "").trim(),
    groups: normalizedGroups,
  };
}

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    const moduleRoot = process.env.PLAYWRIGHT_MODULE_ROOT;
    if (!moduleRoot) throw error;
    const requireFromModuleRoot = createRequire(
      pathToFileURL(path.join(moduleRoot, "playwright-loader.js")).href,
    );
    return requireFromModuleRoot("playwright");
  }
}

async function waitForStablePage(page, settleMs) {
  await page.waitForLoadState("domcontentloaded").catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 5000 }).catch(() => {});
  await page.evaluate(async () => {
    if (document.fonts?.ready) {
      await document.fonts.ready.catch(() => {});
    }
    const pendingImages = Array.from(document.images).filter((image) => !image.complete);
    await Promise.all(
      pendingImages.map(
        (image) =>
          new Promise((resolve) => {
            const done = () => resolve();
            image.addEventListener("load", done, { once: true });
            image.addEventListener("error", done, { once: true });
            setTimeout(done, 3000);
          }),
      ),
    );
  }).catch(() => {});
  if (settleMs > 0) {
    await page.waitForTimeout(settleMs);
  }
}

async function pageMetrics(page) {
  return page.evaluate(() => {
    const body = document.body;
    const html = document.documentElement;
    const scrollHeight = Math.max(
      body?.scrollHeight ?? 0,
      html?.scrollHeight ?? 0,
      body?.offsetHeight ?? 0,
      html?.offsetHeight ?? 0,
      body?.clientHeight ?? 0,
      html?.clientHeight ?? 0,
    );
    return {
      scrollHeight,
      viewportHeight: window.innerHeight,
      viewportWidth: window.innerWidth,
    };
  });
}

async function sectionAnchors(page) {
  return page.evaluate(() => {
    const selectors = [
      "header",
      "main",
      "nav",
      "section",
      "article",
      "footer",
      "[data-section]",
      "[data-testid]",
      "h1",
      "h2",
      "h3",
    ];
    const seen = new Set();
    return Array.from(document.querySelectorAll(selectors.join(",")))
      .map((element) => {
        const rect = element.getBoundingClientRect();
        const y = Math.max(0, Math.round(rect.top + window.scrollY));
        const labelSource =
          element.getAttribute("aria-label") ||
          element.getAttribute("data-section") ||
          element.getAttribute("data-testid") ||
          element.id ||
          element.textContent ||
          "";
        const label = String(labelSource).replace(/\s+/g, " ").trim().slice(0, 80);
        return {
          y,
          tag: element.tagName.toLowerCase(),
          label,
        };
      })
      .filter((anchor) => {
        const key = `${anchor.y}:${anchor.tag}:${anchor.label}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return Number.isFinite(anchor.y);
      });
  });
}

function mergeNearPoints(points, threshold = 48) {
  const sorted = [...points].sort((a, b) => a.y - b.y || a.mode.localeCompare(b.mode));
  const merged = [];
  for (const point of sorted) {
    const last = merged[merged.length - 1];
    if (last && Math.abs(last.y - point.y) <= threshold) {
      if (!last.modes.includes(point.mode)) last.modes.push(point.mode);
      if (point.label && !last.labels.includes(point.label)) last.labels.push(point.label);
      continue;
    }
    merged.push({
      y: point.y,
      modes: [point.mode],
      labels: point.label ? [point.label] : [],
    });
  }
  return merged;
}

function limitPoints(points, maxCount) {
  if (points.length <= maxCount) return points;
  const selected = [];
  const lastIndex = points.length - 1;
  for (let index = 0; index < maxCount; index += 1) {
    const sourceIndex = Math.round((index * lastIndex) / (maxCount - 1));
    selected.push(points[sourceIndex]);
  }
  return selected.filter((point, index, list) => index === 0 || point.y !== list[index - 1].y);
}

function buildCapturePoints(metrics, anchors, stepRatio, maxShotsPerProfile) {
  const maxY = Math.max(0, metrics.scrollHeight - metrics.viewportHeight);
  const step = Math.max(1, Math.round(metrics.viewportHeight * stepRatio));
  const points = [];

  for (let y = 0; y <= maxY; y += step) {
    points.push({ mode: "scroll", y, label: "" });
  }
  if (points.length === 0 || points[points.length - 1].y !== maxY) {
    points.push({ mode: "scroll", y: maxY, label: "bottom" });
  }

  const sectionYs = [];
  for (const anchor of anchors) {
    const y = clamp(anchor.y, 0, maxY);
    sectionYs.push(y);
    points.push({
      mode: `section-${anchor.tag}`,
      y,
      label: anchor.label,
    });
  }

  const uniqueSectionYs = [...new Set(sectionYs)].sort((a, b) => a - b);
  for (let index = 0; index < uniqueSectionYs.length - 1; index += 1) {
    const current = uniqueSectionYs[index];
    const next = uniqueSectionYs[index + 1];
    if (next - current > metrics.viewportHeight * 0.35) {
      points.push({
        mode: "bridge",
        y: Math.round((current + next) / 2),
        label: "between sections",
      });
    }
  }

  const merged = mergeNearPoints(points);
  return limitPoints(merged, maxShotsPerProfile);
}

async function gotoAndSettle(page, url, timeoutMs, settleMs) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
  await waitForStablePage(page, settleMs);
}

async function captureAtPoint(page, screenshotDir, profileName, point, sequence, settleMs) {
  await page.evaluate((y) => window.scrollTo(0, y), point.y);
  await waitForStablePage(page, settleMs);
  const mode = slug(point.modes.join("+"));
  const fileName = `${padded(sequence)}-${profileName}-${mode}-y${padded(point.y, 6)}.png`;
  const filePath = path.join(screenshotDir, fileName);
  await page.screenshot({
    path: filePath,
    fullPage: false,
    caret: "hide",
    animations: "allow",
  });
  return {
    id: `${profileName}-${padded(sequence)}`,
    file: filePath,
    filename: fileName,
    profile: profileName,
    y: point.y,
    modes: point.modes,
    labels: point.labels,
  };
}

async function captureInteraction(page, options, screenshotDir, profileName, interaction, sequence) {
  if (!interaction.selector) {
    return {
      profile: profileName,
      interaction: interaction.name,
      ok: false,
      error: "missing selector",
    };
  }

  await gotoAndSettle(page, options.url, options.timeoutMs, options.settleMs);

  if (Number.isFinite(Number(interaction.scrollY))) {
    await page.evaluate((y) => window.scrollTo(0, y), Number(interaction.scrollY));
    await waitForStablePage(page, options.settleMs);
  }

  if (interaction.beforeSelector) {
    await page.locator(interaction.beforeSelector).first().scrollIntoViewIfNeeded({ timeout: 5000 });
    await waitForStablePage(page, options.settleMs);
  }

  await page.locator(interaction.selector).first().click({ timeout: 8000 });
  await waitForStablePage(page, options.settleMs);

  const y = await page.evaluate(() => Math.round(window.scrollY));
  const fileName = `${padded(sequence)}-${profileName}-interaction-${interaction.name}-y${padded(y, 6)}.png`;
  const filePath = path.join(screenshotDir, fileName);
  await page.screenshot({
    path: filePath,
    fullPage: false,
    caret: "hide",
    animations: "allow",
  });

  return {
    id: `${profileName}-${padded(sequence)}`,
    file: filePath,
    filename: fileName,
    profile: profileName,
    y,
    modes: ["interaction"],
    labels: [interaction.name, interaction.selector],
  };
}

async function positionForPlannedShot(page, shot, settleMs) {
  if (shot.selector) {
    await page.locator(shot.selector).first().scrollIntoViewIfNeeded({ timeout: 8000 });
    await waitForStablePage(page, settleMs);
  }

  if (Number.isFinite(Number(shot.scrollY))) {
    await page.evaluate((y) => window.scrollTo(0, y), Number(shot.scrollY));
    await waitForStablePage(page, settleMs);
  }

  if (Number.isFinite(Number(shot.scrollBy))) {
    await page.evaluate((delta) => window.scrollBy(0, delta), Number(shot.scrollBy));
    await waitForStablePage(page, settleMs);
  }

  if (shot.click) {
    await page.locator(shot.click).first().click({ timeout: 8000 });
    await waitForStablePage(page, settleMs);
  }

  if (Number.isFinite(Number(shot.waitMs)) && Number(shot.waitMs) > 0) {
    await page.waitForTimeout(Number(shot.waitMs));
  }
}

async function capturePlannedShot(browser, options, plan, group, shot, shotIndex) {
  const preset = PROFILE_PRESETS[shot.profile];
  const screenshotDir = path.join(options.outDir, "screenshots", group.id);
  await fs.mkdir(screenshotDir, { recursive: true });

  const context = await browser.newContext({
    viewport: preset.viewport,
    deviceScaleFactor: preset.deviceScaleFactor,
    isMobile: preset.isMobile,
    hasTouch: preset.hasTouch,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(options.timeoutMs);

  try {
    await gotoAndSettle(page, plan.url, options.timeoutMs, options.settleMs);
    await positionForPlannedShot(page, shot, options.settleMs);
    const y = await page.evaluate(() => Math.round(window.scrollY));
    const fileName = `${padded(shotIndex + 1)}-${shot.profile}-${shot.name}-y${padded(y, 6)}.png`;
    const filePath = path.join(screenshotDir, fileName);
    await page.screenshot({
      path: filePath,
      fullPage: false,
      caret: "hide",
      animations: "allow",
    });
    return {
      id: `${group.id}-${padded(shotIndex + 1)}`,
      groupId: group.id,
      groupPurpose: group.purpose,
      shotName: shot.name,
      file: filePath,
      filename: path.join(group.id, fileName),
      profile: shot.profile,
      y,
      modes: ["planned"],
      labels: [shot.notes].filter(Boolean),
      selector: shot.selector || null,
      click: shot.click || null,
    };
  } finally {
    await context.close();
  }
}

async function writeLedgers(outDir, manifest) {
  const manifestPath = path.join(outDir, "manifest.json");
  const markdownPath = path.join(outDir, "screenshots.md");
  await fs.writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");

  const lines = [
    "# Design Review Screenshots",
    "",
    `URL: ${manifest.url}`,
    `Created: ${manifest.createdAt}`,
    `Profiles: ${manifest.profiles.join(", ")}`,
  ];

  if (manifest.groups?.length) {
    lines.push("", "## Review Groups", "");
    for (const group of manifest.groups) {
      lines.push(`- ${group.id}: ${group.purpose || "no purpose recorded"}`);
    }
  }

  lines.push(
    "",
    "## Screenshots",
    "",
    "| id | group | profile | y | modes | file |",
    "| --- | --- | --- | ---: | --- | --- |",
  );

  for (const shot of manifest.screenshots) {
    lines.push(
      `| ${shot.id} | ${shot.groupId || "-"} | ${shot.profile} | ${shot.y} | ${shot.modes.join(", ")} | ${shot.filename} |`,
    );
  }

  if (manifest.failures.length > 0) {
    lines.push("", "## Failures", "");
    for (const failure of manifest.failures) {
      lines.push(`- ${failure.profile || "all"} / ${failure.interaction || failure.phase}: ${failure.error}`);
    }
  }

  await fs.writeFile(markdownPath, `${lines.join("\n")}\n`, "utf8");
}

async function captureProfile(browser, options, profileName, interactions, captureProgress) {
  const preset = PROFILE_PRESETS[profileName];
  const screenshotDir = path.join(options.outDir, "screenshots", profileName);
  await fs.mkdir(screenshotDir, { recursive: true });

  const context = await browser.newContext({
    viewport: preset.viewport,
    deviceScaleFactor: preset.deviceScaleFactor,
    isMobile: preset.isMobile,
    hasTouch: preset.hasTouch,
  });
  const page = await context.newPage();
  page.setDefaultTimeout(options.timeoutMs);

  const screenshots = [];
  const failures = [];
  let sequence = 1;

  try {
    await gotoAndSettle(page, options.url, options.timeoutMs, options.settleMs);
    const metrics = await pageMetrics(page);
    const anchors = await sectionAnchors(page);
    const points = buildCapturePoints(metrics, anchors, options.stepRatio, options.maxShotsPerProfile);

    for (const point of points) {
      const progressShotId = `${profileName}-${padded(sequence)}`;
      const progressDefaults = {
        groupId: profileName,
        shotName: point.modes.join("+"),
        profile: profileName,
        selector: "",
        click: "",
      };
      try {
        if (captureProgress) {
          await upsertCaptureShot(options.outDir, captureProgress, progressShotId, progressDefaults, {
            status: "running",
          });
        }
        const capturedShot = await captureAtPoint(page, screenshotDir, profileName, point, sequence, options.settleMs);
        screenshots.push(capturedShot);
        if (captureProgress) {
          await upsertCaptureShot(options.outDir, captureProgress, progressShotId, progressDefaults, {
            status: "done",
            file: capturedShot.filename,
            y: capturedShot.y,
          });
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        failures.push({
          profile: profileName,
          interaction: "",
          phase: "auto-capture-point",
          error: message,
        });
        if (captureProgress) {
          await upsertCaptureShot(options.outDir, captureProgress, progressShotId, progressDefaults, {
            status: "failed",
            error: message,
          });
        }
      }
      sequence += 1;
    }

    const profileInteractions = interactions.filter(
      (interaction) => !interaction.profile || interaction.profile === profileName,
    );
    for (const interaction of profileInteractions) {
      const progressShotId = `${profileName}-${padded(sequence)}`;
      const progressDefaults = {
        groupId: profileName,
        shotName: interaction.name,
        profile: profileName,
        selector: interaction.beforeSelector || "",
        click: interaction.selector || "",
      };
      try {
        if (captureProgress) {
          await upsertCaptureShot(options.outDir, captureProgress, progressShotId, progressDefaults, {
            status: "running",
          });
        }
        const capturedShot = await captureInteraction(page, options, screenshotDir, profileName, interaction, sequence);
        screenshots.push(capturedShot);
        if (captureProgress) {
          await upsertCaptureShot(options.outDir, captureProgress, progressShotId, progressDefaults, {
            status: "done",
            file: capturedShot.filename,
            y: capturedShot.y,
          });
        }
        sequence += 1;
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        failures.push({
          profile: profileName,
          interaction: interaction.name,
          selector: interaction.selector,
          phase: "auto-capture-interaction",
          error: message,
        });
        if (captureProgress) {
          await upsertCaptureShot(options.outDir, captureProgress, progressShotId, progressDefaults, {
            status: "failed",
            error: message,
          });
        }
        sequence += 1;
      }
    }

    return {
      profile: profileName,
      viewport: preset.viewport,
      metrics,
      screenshots,
      failures,
    };
  } finally {
    await context.close();
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  await fs.mkdir(options.outDir, { recursive: true });
  const plan = await readScreenshotPlan(options.plan, options.url);
  if (plan?.url) {
    options.url = plan.url;
  }
  if (!options.url) {
    throw new Error("url is required either in --url or in the screenshot plan");
  }
  const interactions = await readInteractions(options.interactions);
  const { chromium } = await loadPlaywright();
  const captureProgress = await initCaptureProgress(options.outDir, {
    url: options.url,
    mode: plan ? "curated-plan" : "auto-capture",
    shots: plan ? plannedProgressShots(plan) : [],
  });
  let browser = null;
  let heartbeat = null;
  const manifest = {
    url: options.url,
    createdAt: new Date().toISOString(),
    outDir: path.resolve(options.outDir),
    profiles: plan
      ? [...new Set(plan.groups.flatMap((group) => group.shots.map((shot) => shot.profile)))]
      : options.profiles,
    groups: plan?.groups.map((group) => ({
      id: group.id,
      purpose: group.purpose,
      questions: group.questions,
      shotCount: group.shots.length,
    })) ?? [],
    planNotes: plan?.notes ?? "",
    screenshotContract: {
      desktop: "16:9 viewport screenshots",
      mode: plan ? "curated-plan" : "auto-capture",
      scroll: plan ? "main-agent planned shots" : `overlap step ${options.stepRatio} of viewport height`,
      settleMs: options.settleMs,
      sectionAnchors: !plan,
      bridgeShots: !plan,
      interactions: interactions.length,
    },
    profileRuns: [],
    screenshots: [],
    failures: [],
  };

  try {
    browser = await chromium.launch({ headless: !options.headed });
    let heartbeatBusy = false;
    heartbeat = setInterval(() => {
      if (heartbeatBusy) return;
      heartbeatBusy = true;
      recordCaptureHeartbeat(options.outDir, captureProgress)
        .catch((error) => {
          console.error(`capture-design-screenshots heartbeat: ${error instanceof Error ? error.message : String(error)}`);
        })
        .finally(() => {
          heartbeatBusy = false;
        });
    }, options.progressInterval * 1000);

    if (plan) {
      for (const group of plan.groups) {
        for (let shotIndex = 0; shotIndex < group.shots.length; shotIndex += 1) {
          const shot = group.shots[shotIndex];
          const progressShotId = plannedShotId(group.id, shotIndex);
          try {
            if (captureProgress) {
              await updateCaptureShot(options.outDir, captureProgress, progressShotId, { status: "running" });
            }
            const capturedShot = await capturePlannedShot(browser, options, plan, group, shot, shotIndex);
            manifest.screenshots.push(capturedShot);
            if (captureProgress) {
              await updateCaptureShot(options.outDir, captureProgress, progressShotId, {
                status: "done",
                file: capturedShot.filename,
                y: capturedShot.y,
              });
            }
          } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            manifest.failures.push({
              phase: "planned-shot",
              groupId: group.id,
              shotName: shot.name,
              profile: shot.profile,
              error: message,
            });
            if (captureProgress) {
              await updateCaptureShot(options.outDir, captureProgress, progressShotId, {
                status: "failed",
                error: message,
              });
            }
          }
        }
      }
      for (const profileName of manifest.profiles) {
        const profileShots = manifest.screenshots.filter((shot) => shot.profile === profileName);
        manifest.profileRuns.push({
          profile: profileName,
          viewport: PROFILE_PRESETS[profileName].viewport,
          metrics: null,
          screenshotCount: profileShots.length,
          failureCount: manifest.failures.filter((failure) => failure.profile === profileName).length,
        });
      }
    } else {
      for (const profileName of options.profiles) {
        const profileRun = await captureProfile(browser, options, profileName, interactions, captureProgress);
        manifest.profileRuns.push({
          profile: profileRun.profile,
          viewport: profileRun.viewport,
          metrics: profileRun.metrics,
          screenshotCount: profileRun.screenshots.length,
          failureCount: profileRun.failures.length,
        });
        manifest.screenshots.push(...profileRun.screenshots);
        manifest.failures.push(...profileRun.failures);
      }
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    captureProgress.stage = "failed";
    captureProgress.fatalError = message;
    await writeCaptureProgress(options.outDir, captureProgress);
    printCaptureSummary(captureProgress, "failed");
    throw error;
  } finally {
    if (heartbeat) clearInterval(heartbeat);
    if (browser) {
      await browser.close().catch(() => {});
    }
  }

  captureProgress.stage = manifest.failures.length === 0 ? "complete" : "failed";
  await writeCaptureProgress(options.outDir, captureProgress);
  printCaptureSummary(captureProgress, captureProgress.stage);

  await writeLedgers(options.outDir, manifest);
  console.log(
    JSON.stringify(
      {
        ok: manifest.failures.length === 0,
        outDir: path.resolve(options.outDir),
        screenshots: manifest.screenshots.length,
        failures: manifest.failures.length,
      },
      null,
      2,
    ),
  );

  if (manifest.failures.length > 0) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(`capture-design-screenshots: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
