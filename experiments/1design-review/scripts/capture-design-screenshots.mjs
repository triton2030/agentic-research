#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";
import {
  ALGORITHM_VERSION,
  clampRect,
  contextCrop,
  familyLayout,
  intersectRects,
  normalizeRect,
  roundRect,
  transitionScrollY,
  unionArea,
  validatePlan,
} from "./screenshot-evidence-core.mjs";

function usage() {
  console.log(`Usage:
  capture-design-screenshots.mjs --plan FILE --out-dir DIR [--url URL]

Options:
  --plan FILE       Plan version 2.
  --out-dir DIR     Run artifact directory.
  --url URL         Fallback URL for a URL source whose url is omitted.
  --settle-ms N     Delay after load and state actions. Default: 350.
  -h, --help        Show this help.`);
}

function parseArgs(argv) {
  const options = { plan: "", outDir: "", url: "", settleMs: 350 };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    const value = argv[index + 1];
    switch (argument) {
      case "--plan":
        options.plan = value ?? "";
        index += 1;
        break;
      case "--out-dir":
        options.outDir = value ?? "";
        index += 1;
        break;
      case "--url":
        options.url = value ?? "";
        index += 1;
        break;
      case "--settle-ms":
        options.settleMs = Number(value);
        index += 1;
        break;
      case "-h":
      case "--help":
        usage();
        process.exit(0);
        break;
      default:
        throw new Error(`unknown argument: ${argument}`);
    }
  }
  if (!options.plan) throw new Error("--plan is required");
  if (!options.outDir) throw new Error("--out-dir is required");
  if (!Number.isFinite(options.settleMs) || options.settleMs < 0) {
    throw new Error("--settle-ms must be a non-negative number");
  }
  return options;
}

async function loadPlaywright() {
  try {
    return { module: await import("playwright"), moduleRoot: "package-resolution" };
  } catch {
    // Continue through explicit and common global npm roots.
  }
  const roots = [
    process.env.PLAYWRIGHT_MODULE_ROOT,
    "/opt/homebrew/lib/node_modules",
    "/usr/local/lib/node_modules",
  ].filter(Boolean);
  for (const root of roots) {
    try {
      const requireFromRoot = createRequire(path.join(path.resolve(root), "__design-review__.cjs"));
      return { module: requireFromRoot("playwright"), moduleRoot: path.resolve(root) };
    } catch {
      // Try the next reviewed runtime root.
    }
  }
  throw new Error(
    "Playwright is not available. Install it in the skill/project or set PLAYWRIGHT_MODULE_ROOT to an existing npm module root.",
  );
}

function safeName(value) {
  const normalized = String(value).replace(/[^A-Za-z0-9_.-]+/g, "-").replace(/^-+|-+$/g, "");
  if (!normalized) throw new Error(`unsafe empty filename for id: ${value}`);
  return normalized;
}

function mimeFor(filePath) {
  const extension = path.extname(filePath).toLowerCase();
  if (extension === ".jpg" || extension === ".jpeg") return "image/jpeg";
  if (extension === ".webp") return "image/webp";
  if (extension === ".gif") return "image/gif";
  return "image/png";
}

async function writeJson(filePath, value) {
  const temporary = `${filePath}.${process.pid}.tmp`;
  await fs.writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  await fs.rename(temporary, filePath);
}

async function uniqueElementRect(page, selector, label = selector) {
  const locator = page.locator(selector);
  const count = await locator.count();
  if (count !== 1) throw new Error(`${label} must match exactly one element; matched ${count}`);
  const rect = await locator.evaluate((element) => {
    const box = element.getBoundingClientRect();
    return {
      x: box.left + window.scrollX,
      y: box.top + window.scrollY,
      width: box.width,
      height: box.height,
    };
  });
  return normalizeRect(rect, label);
}

async function documentBounds(page) {
  return page.evaluate(() => ({
    x: 0,
    y: 0,
    width: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth ?? 0),
    height: Math.max(document.documentElement.scrollHeight, document.body?.scrollHeight ?? 0),
  }));
}

async function disableMotionAndWait(page, settleMs) {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-delay: 0s !important;
        animation-duration: 0s !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-delay: 0s !important;
        transition-duration: 0s !important;
        caret-color: transparent !important;
      }
    `,
  });
  const warnings = await page.evaluate(async () => {
    const warnings = [];
    const waitAtMost = async (promise, milliseconds, warning) => {
      const result = await Promise.race([
        Promise.resolve(promise).then(() => "ready"),
        new Promise((resolve) => setTimeout(() => resolve("timeout"), milliseconds)),
      ]);
      if (result === "timeout") warnings.push(warning);
    };
    if (document.fonts?.ready) {
      await waitAtMost(document.fonts.ready, 5000, "fonts-wait-timeout");
    }
    const images = [...document.images].filter((image) => {
      if (image.complete) return false;
      const rect = image.getBoundingClientRect();
      const intersectsViewport =
        rect.bottom > 0 &&
        rect.right > 0 &&
        rect.top < window.innerHeight &&
        rect.left < window.innerWidth;
      return image.loading !== "lazy" || intersectsViewport;
    });
    await waitAtMost(
      Promise.all(
        images.map(
          (image) =>
            new Promise((resolve) => {
              image.addEventListener("load", resolve, { once: true });
              image.addEventListener("error", resolve, { once: true });
            }),
        ),
      ),
      5000,
      "visible-or-eager-images-wait-timeout",
    );
    return warnings;
  });
  if (settleMs > 0) await page.waitForTimeout(settleMs);
  return warnings;
}

async function applyState(page, evidence, settleMs) {
  const state = evidence.state ?? {};
  for (const [index, action] of (state.actions ?? evidence.actions ?? []).entries()) {
    if (!action || typeof action !== "object") throw new Error(`state action ${index} must be an object`);
    const selector = action.selector;
    if (typeof selector !== "string" || selector.trim() === "") {
      throw new Error(`state action ${index} requires selector`);
    }
    const locator = page.locator(selector);
    const count = await locator.count();
    if (count !== 1) throw new Error(`state action ${index} selector matched ${count} elements`);
    if (action.type === "click") await locator.click();
    else if (action.type === "hover") await locator.hover();
    else if (action.type === "focus") await locator.focus();
    else throw new Error(`unsupported state action: ${action.type}`);
    if (settleMs > 0) await page.waitForTimeout(settleMs);
  }
  const requestedScroll = evidence.scrollY ?? state.scrollY;
  if (requestedScroll !== undefined) {
    await page.evaluate((scrollY) => window.scrollTo(0, Number(scrollY)), requestedScroll);
    if (settleMs > 0) await page.waitForTimeout(settleMs);
  }
}

async function openSource(browser, source, evidence, planDir, settleMs) {
  const requestedViewport = evidence.viewport;
  const context = await browser.newContext({
    viewport: { width: requestedViewport.width, height: requestedViewport.height },
    deviceScaleFactor: requestedViewport.deviceScaleFactor,
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  let imageSize = null;
  if (source.type === "url") {
    await page.goto(source.url, { waitUntil: "domcontentloaded" });
  } else {
    const absoluteImage = path.resolve(planDir, source.path);
    const buffer = await fs.readFile(absoluteImage);
    const dataUrl = `data:${mimeFor(absoluteImage)};base64,${buffer.toString("base64")}`;
    await page.setContent(
      `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:white}img{display:block;max-width:none}</style><img id="design-source" src="${dataUrl}">`,
      { waitUntil: "load" },
    );
    imageSize = await page.locator("#design-source").evaluate((image) => ({
      width: image.naturalWidth,
      height: image.naturalHeight,
    }));
    if (!imageSize.width || !imageSize.height) throw new Error(`image source did not decode: ${absoluteImage}`);
    await page.setViewportSize({ width: imageSize.width, height: imageSize.height });
  }
  const waitWarnings = await disableMotionAndWait(page, settleMs);
  await applyState(page, evidence, settleMs);
  return {
    context,
    page,
    viewport:
      source.type === "image"
        ? { width: imageSize.width, height: imageSize.height, deviceScaleFactor: 1 }
        : requestedViewport,
    sourceState: {
      type: source.type,
      url: source.type === "url" ? source.url : undefined,
      path: source.type === "image" ? path.resolve(planDir, source.path) : undefined,
      state: evidence.state ?? {},
      requestedScrollY: evidence.scrollY ?? evidence.state?.scrollY ?? 0,
    },
    waitWarnings,
  };
}

async function viewportClipForDocumentRect(page, documentRect, viewport) {
  if (documentRect.width > viewport.width || documentRect.height > viewport.height) {
    throw new Error("crop plus context must fit inside the selected viewport");
  }
  const bounds = await documentBounds(page);
  const requestedScrollX = Math.max(
    0,
    Math.min(bounds.width - viewport.width, documentRect.x + documentRect.width / 2 - viewport.width / 2),
  );
  const requestedScrollY = Math.max(
    0,
    Math.min(bounds.height - viewport.height, documentRect.y + documentRect.height / 2 - viewport.height / 2),
  );
  await page.evaluate(
    ({ x, y }) => window.scrollTo(x, y),
    { x: requestedScrollX, y: requestedScrollY },
  );
  await page.waitForTimeout(50);
  const scroll = await page.evaluate(() => ({ x: window.scrollX, y: window.scrollY }));
  const clip = {
    x: documentRect.x - scroll.x,
    y: documentRect.y - scroll.y,
    width: documentRect.width,
    height: documentRect.height,
  };
  if (
    clip.x < -0.1 ||
    clip.y < -0.1 ||
    clip.x + clip.width > viewport.width + 0.1 ||
    clip.y + clip.height > viewport.height + 0.1
  ) {
    throw new Error("browser could not position the requested crop fully inside the viewport");
  }
  return { clip, scroll };
}

async function screenshotDocumentClip(page, filePath, documentRect, viewport) {
  const positioned = await viewportClipForDocumentRect(page, documentRect, viewport);
  await page.screenshot({
    path: filePath,
    clip: positioned.clip,
    animations: "disabled",
    caret: "hide",
    scale: "css",
    captureBeyondViewport: false,
  });
  return positioned;
}

async function renderSvg(browser, filePath, width, height, body) {
  const safeWidth = Math.max(1, Math.ceil(width));
  const safeHeight = Math.max(1, Math.ceil(height));
  const context = await browser.newContext({
    viewport: { width: safeWidth, height: safeHeight },
    deviceScaleFactor: 1,
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  await page.setContent(
    `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:white;overflow:hidden}svg{display:block}</style><svg xmlns="http://www.w3.org/2000/svg" width="${safeWidth}" height="${safeHeight}" viewBox="0 0 ${safeWidth} ${safeHeight}">${body}</svg>`,
  );
  await page.screenshot({ path: filePath, animations: "disabled", caret: "hide", scale: "css" });
  await context.close();
}

function svgRect(rect, attributes) {
  const normalized = roundRect(rect);
  return `<rect x="${normalized.x}" y="${normalized.y}" width="${normalized.width}" height="${normalized.height}" ${attributes}/>`;
}

async function composeFamily(browser, filePath, members) {
  const layout = familyLayout(members.map((member) => member.crop.actual));
  const gap = 24;
  const outer = 24;
  const labelHeight = 30;
  const totalWidth = outer * 2 + layout.columns * layout.cellWidth + (layout.columns - 1) * gap;
  const totalHeight =
    outer * 2 + layout.rows * (layout.cellHeight + labelHeight) + (layout.rows - 1) * gap;
  const context = await browser.newContext({
    viewport: { width: totalWidth, height: totalHeight },
    deviceScaleFactor: 1,
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  const cells = members
    .map(
      (member) => `
        <figure>
          <div class="image-cell">
            <img src="data:image/png;base64,${member.buffer.toString("base64")}"
              width="${Math.round(member.crop.actual.width * layout.scale)}"
              height="${Math.round(member.crop.actual.height * layout.scale)}">
          </div>
          <figcaption>${member.id.replace(/[<>&"]/g, "")}</figcaption>
        </figure>`,
    )
    .join("");
  await page.setContent(`<!doctype html>
    <meta charset="utf-8">
    <style>
      *{box-sizing:border-box}
      html,body{margin:0;background:#f4f2ed;color:#383733;font:16px/1.2 system-ui,sans-serif}
      main{display:grid;grid-template-columns:repeat(${layout.columns},${layout.cellWidth}px);gap:${gap}px;padding:${outer}px}
      figure{margin:0;width:${layout.cellWidth}px}
      .image-cell{width:${layout.cellWidth}px;height:${layout.cellHeight}px;background:white;border:1px solid #cbc7bd;display:flex;align-items:center;justify-content:center;overflow:hidden}
      img{display:block;max-width:none}
      figcaption{height:${labelHeight}px;padding-top:8px;font-weight:650;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    </style>
    <main>${cells}</main>`);
  await page.screenshot({ path: filePath, animations: "disabled", caret: "hide", scale: "css" });
  await context.close();
  return layout;
}

async function captureViewport(page, evidence, filePath) {
  if (evidence.kind === "transition") throw new Error("internal: transition uses captureTransition");
  await page.screenshot({
    path: filePath,
    fullPage: false,
    animations: "disabled",
    caret: "hide",
    scale: "css",
  });
  return {
    targetRect: null,
    contextRect: null,
    stats: {
      scrollY: await page.evaluate(() => window.scrollY),
    },
    warnings: [],
  };
}

async function captureTransition(page, evidence, filePath, viewport) {
  const beforeRect = await uniqueElementRect(page, evidence.beforeSelector, "beforeSelector");
  const afterRect = await uniqueElementRect(page, evidence.afterSelector, "afterSelector");
  const bounds = await documentBounds(page);
  const transition = transitionScrollY(beforeRect, afterRect, viewport.height, bounds.height);
  await page.evaluate((scrollY) => window.scrollTo(0, scrollY), transition.scrollY);
  await page.screenshot({
    path: filePath,
    fullPage: false,
    animations: "disabled",
    caret: "hide",
    scale: "css",
  });
  return {
    targetRect: roundRect({ x: 0, y: transition.scrollY, width: viewport.width, height: viewport.height }),
    contextRect: null,
    stats: {
      boundaryY: transition.boundary,
      scrollY: transition.scrollY,
      beforeRect: roundRect(beforeRect),
      afterRect: roundRect(afterRect),
    },
    warnings: [],
  };
}

async function targetRects(page, source, evidence) {
  if (source.type === "url") {
    const selectors = evidence.selector ? [evidence.selector] : evidence.selectors;
    return Promise.all(selectors.map((selector) => uniqueElementRect(page, selector, selector)));
  }
  const rects = evidence.rect ? [evidence.rect] : evidence.rects;
  return rects.map((rect, index) => normalizeRect(rect, `rects[${index}]`));
}

async function captureBlock(page, source, evidence, filePath, viewport) {
  const bounds = await documentBounds(page);
  const rects = await targetRects(page, source, evidence);
  const crop = contextCrop(rects, bounds, 0.1);
  if (
    crop.target.height > viewport.height * 2.5 ||
    (crop.target.width > bounds.width * 0.98 && crop.target.height > viewport.height * 1.5)
  ) {
    throw new Error("block target is too large to isolate one visual question");
  }
  const positioned = await screenshotDocumentClip(page, filePath, crop.actual, viewport);
  return {
    targetRect: crop.target,
    contextRect: {
      ratio: 0.1,
      requested: crop.requested,
      actual: crop.actual,
      clipped: crop.clipped,
    },
    stats: { targetCount: rects.length, captureScroll: positioned.scroll },
    warnings: crop.clipped ? ["context-clipped-and-recorded"] : [],
  };
}

async function captureFamily(browser, page, source, evidence, filePath, viewport) {
  const bounds = await documentBounds(page);
  const members = [];
  for (const member of evidence.members) {
    let rect =
      source.type === "url"
        ? await uniqueElementRect(page, member.selector, `family member ${member.id}`)
        : normalizeRect(member.rect, `family member ${member.id}`);
    const crop = contextCrop([rect], bounds, 0.1);
    const positioned = await viewportClipForDocumentRect(page, crop.actual, viewport);
    if (source.type === "url") {
      rect = await uniqueElementRect(page, member.selector, `family member ${member.id}`);
    }
    const buffer = await page.screenshot({
      clip: positioned.clip,
      animations: "disabled",
      caret: "hide",
      scale: "css",
      captureBeyondViewport: false,
    });
    members.push({
      id: member.id,
      selector: member.selector,
      rect: roundRect(rect),
      crop,
      buffer,
      captureScroll: positioned.scroll,
    });
  }
  const layout = await composeFamily(browser, filePath, members);
  return {
    targetRect: null,
    contextRect: null,
    members: members.map(({ id, selector, rect, crop, captureScroll }) => ({
      id,
      selector,
      rect,
      captureScroll,
      context: {
        ratio: 0.1,
        requested: crop.requested,
        actual: crop.actual,
        clipped: crop.clipped,
      },
    })),
    stats: {
      memberCount: members.length,
      layout: `${layout.columns}x${layout.rows}`,
      commonScale: Math.round(layout.scale * 10000) / 10000,
    },
    warnings: members.some((member) => member.crop.clipped)
      ? ["member-context-clipped-and-recorded"]
      : [],
  };
}

async function captureTextDensity(browser, page, evidence, filePath) {
  const payload = await page.evaluate((selector) => {
    const matches = document.querySelectorAll(selector);
    if (matches.length !== 1) throw new Error(`selector must match exactly one element; matched ${matches.length}`);
    const root = matches[0];
    const rootBox = root.getBoundingClientRect();
    const target = {
      x: rootBox.left + window.scrollX,
      y: rootBox.top + window.scrollY,
      width: rootBox.width,
      height: rootBox.height,
    };
    const rects = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node.textContent || !node.textContent.trim()) continue;
      const parent = node.parentElement;
      if (!parent) continue;
      const style = getComputedStyle(parent);
      if (style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const rect of range.getClientRects()) {
        if (rect.width <= 0 || rect.height <= 0) continue;
        rects.push({
          x: rect.left + window.scrollX,
          y: rect.top + window.scrollY,
          width: rect.width,
          height: rect.height,
        });
      }
    }
    const warnings = [];
    if (root.querySelector("canvas")) warnings.push("canvas-text-not-observable");
    if (root.querySelector("iframe")) warnings.push("iframe-content-not-observable");
    const generated = [...root.querySelectorAll("*")].some((element) => {
      const before = getComputedStyle(element, "::before").content;
      const after = getComputedStyle(element, "::after").content;
      return (before && before !== "none" && before !== '""') || (after && after !== "none" && after !== '""');
    });
    if (generated) warnings.push("generated-content-not-measured");
    warnings.push("closed-shadow-dom-not-observable");
    return { target, rects, warnings };
  }, evidence.selector);

  const target = normalizeRect(payload.target, "text-density target");
  const visibleRects = payload.rects
    .map((rect) => intersectRects(rect, target))
    .filter(Boolean)
    .map((rect) => ({
      x: rect.x - target.x,
      y: rect.y - target.y,
      width: rect.width,
      height: rect.height,
    }));
  const redRects = visibleRects.map((rect) => svgRect(rect, 'fill="#ef2727"')).join("");
  await renderSvg(browser, filePath, target.width, target.height, `<rect width="100%" height="100%" fill="#fff"/>${redRects}`);
  const occupiedArea = unionArea(visibleRects);
  return {
    targetRect: roundRect(target),
    contextRect: null,
    stats: {
      rectCount: visibleRects.length,
      occupiedRatio: Math.round((occupiedArea / (target.width * target.height)) * 1000000) / 1000000,
    },
    warnings: payload.warnings,
  };
}

function hueFor(value) {
  let hash = 2166136261;
  for (const character of String(value)) {
    hash ^= character.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return Math.abs(hash) % 360;
}

async function captureSpacing(browser, page, evidence, filePath) {
  const payload = await page.evaluate(
    ({ rootSelector, requestedContainers }) => {
      const exactlyOne = (selector, label) => {
        const matches = document.querySelectorAll(selector);
        if (matches.length !== 1) throw new Error(`${label} must match exactly one element; matched ${matches.length}`);
        return matches[0];
      };
      const root = exactlyOne(rootSelector, "spacing root");
      const rootBox = root.getBoundingClientRect();
      const toRect = (box) => ({
        x: box.left + window.scrollX,
        y: box.top + window.scrollY,
        width: box.width,
        height: box.height,
      });
      const specs = [{ id: "root", selector: rootSelector }, ...requestedContainers];
      const seen = new Set();
      const containers = [];
      const warnings = [];
      for (const spec of specs) {
        if (seen.has(spec.selector)) continue;
        seen.add(spec.selector);
        const element = exactlyOne(spec.selector, `spacing container ${spec.id}`);
        if (element !== root && !root.contains(element)) {
          throw new Error(`spacing container ${spec.id} is outside the selected root`);
        }
        const box = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        const number = (value) => Number.parseFloat(value) || 0;
        const border = {
          top: number(style.borderTopWidth),
          right: number(style.borderRightWidth),
          bottom: number(style.borderBottomWidth),
          left: number(style.borderLeftWidth),
        };
        const padding = {
          top: number(style.paddingTop),
          right: number(style.paddingRight),
          bottom: number(style.paddingBottom),
          left: number(style.paddingLeft),
        };
        const rect = toRect(box);
        const contentBox = {
          x: rect.x + border.left + padding.left,
          y: rect.y + border.top + padding.top,
          width: Math.max(0, rect.width - border.left - border.right - padding.left - padding.right),
          height: Math.max(0, rect.height - border.top - border.bottom - padding.top - padding.bottom),
        };
        const children = [...element.children]
          .map((child) => {
            const childBox = child.getBoundingClientRect();
            const childStyle = getComputedStyle(child);
            if (childBox.width <= 0 || childBox.height <= 0 || childStyle.display === "none") return null;
            return {
              rect: toRect(childBox),
              position: childStyle.position,
              margin: {
                top: number(childStyle.marginTop),
                right: number(childStyle.marginRight),
                bottom: number(childStyle.marginBottom),
                left: number(childStyle.marginLeft),
              },
            };
          })
          .filter(Boolean);
        if (style.transform !== "none") warnings.push(`${spec.id}:transform`);
        if (["absolute", "fixed"].includes(style.position)) warnings.push(`${spec.id}:absolute-positioning`);
        if (
          !["flex", "grid", "inline-flex", "inline-grid"].includes(style.display) &&
          children.some((child) => Object.values(child.margin).some((value) => value > 0))
        ) {
          warnings.push(`${spec.id}:possible-collapsed-margins`);
        }
        if (children.some((child) => ["absolute", "fixed"].includes(child.position))) {
          warnings.push(`${spec.id}:absolute-child`);
        }
        containers.push({
          id: spec.id,
          selector: spec.selector,
          rect,
          contentBox,
          padding,
          rowGap: number(style.rowGap),
          columnGap: number(style.columnGap),
          display: style.display,
          children,
        });
      }
      return { target: toRect(rootBox), containers, warnings: [...new Set(warnings)] };
    },
    { rootSelector: evidence.selector, requestedContainers: evidence.containers ?? [] },
  );

  const target = normalizeRect(payload.target, "spacing target");
  const zones = [];
  const containers = payload.containers.map((container) => {
    const color = `hsla(${hueFor(container.id)},72%,58%,0.74)`;
    const rect = normalizeRect(container.rect);
    const padding = container.padding;
    const innerX = rect.x + padding.left;
    const innerY = rect.y + padding.top;
    if (padding.top > 0) zones.push({ owner: container.id, kind: "padding-top", color, rect: { x: rect.x, y: rect.y, width: rect.width, height: padding.top } });
    if (padding.bottom > 0) zones.push({ owner: container.id, kind: "padding-bottom", color, rect: { x: rect.x, y: rect.y + rect.height - padding.bottom, width: rect.width, height: padding.bottom } });
    if (padding.left > 0) zones.push({ owner: container.id, kind: "padding-left", color, rect: { x: rect.x, y: innerY, width: padding.left, height: Math.max(0, rect.height - padding.top - padding.bottom) } });
    if (padding.right > 0) zones.push({ owner: container.id, kind: "padding-right", color, rect: { x: rect.x + rect.width - padding.right, y: innerY, width: padding.right, height: Math.max(0, rect.height - padding.top - padding.bottom) } });

    const children = container.children.map((child) => child.rect);
    for (let firstIndex = 0; firstIndex < children.length - 1; firstIndex += 1) {
        const first = children[firstIndex];
        const second = children[firstIndex + 1];
        const verticalTop = Math.min(first.y + first.height, second.y + second.height);
        const verticalBottom = Math.max(first.y, second.y);
        const horizontalLeft = Math.max(first.x, second.x);
        const horizontalRight = Math.min(first.x + first.width, second.x + second.width);
        if (verticalBottom > verticalTop && horizontalRight > horizontalLeft) {
          zones.push({
            owner: container.id,
            kind: "gap-row",
            color,
            rect: {
              x: horizontalLeft,
              y: verticalTop,
              width: horizontalRight - horizontalLeft,
              height: verticalBottom - verticalTop,
            },
          });
        }
        const horizontalGapLeft = Math.min(first.x + first.width, second.x + second.width);
        const horizontalGapRight = Math.max(first.x, second.x);
        const verticalOverlapTop = Math.max(first.y, second.y);
        const verticalOverlapBottom = Math.min(first.y + first.height, second.y + second.height);
        if (horizontalGapRight > horizontalGapLeft && verticalOverlapBottom > verticalOverlapTop) {
          zones.push({
            owner: container.id,
            kind: "gap-column",
            color,
            rect: {
              x: horizontalGapLeft,
              y: verticalOverlapTop,
              width: horizontalGapRight - horizontalGapLeft,
              height: verticalOverlapBottom - verticalOverlapTop,
            },
          });
        }
    }
    return {
      id: container.id,
      selector: container.selector,
      color,
      rect: roundRect(container.rect),
      contentBox: roundRect(container.contentBox),
      computed: {
        padding: container.padding,
        rowGap: container.rowGap,
        columnGap: container.columnGap,
        display: container.display,
      },
    };
  });

  const clippedZones = zones
    .map((zone) => {
      const clipped = intersectRects(zone.rect, target);
      return clipped ? { ...zone, rect: clipped } : null;
    })
    .filter(Boolean);
  const overlaps = [];
  for (let first = 0; first < clippedZones.length; first += 1) {
    for (let second = first + 1; second < clippedZones.length; second += 1) {
      if (clippedZones[first].owner === clippedZones[second].owner) continue;
      const overlap = intersectRects(clippedZones[first].rect, clippedZones[second].rect);
      if (overlap) overlaps.push(overlap);
    }
  }
  const relative = (rect) => ({
    x: rect.x - target.x,
    y: rect.y - target.y,
    width: rect.width,
    height: rect.height,
  });
  const contentBoxes = containers
    .map((container) => intersectRects(container.contentBox, target))
    .filter(Boolean)
    .map((rect) => svgRect(relative(rect), 'fill="#fff" stroke="#8c8c8c" stroke-width="1"'));
  const zoneRects = clippedZones.map((zone) => svgRect(relative(zone.rect), `fill="${zone.color}"`));
  const overlapRects = overlaps.map((rect) => svgRect(relative(rect), 'fill="#ff00a8" fill-opacity="0.9"'));
  const outlines = containers
    .map((container) => intersectRects(container.rect, target))
    .filter(Boolean)
    .map((rect) => svgRect(relative(rect), 'fill="none" stroke="#5d5d5d" stroke-width="1"'));
  await renderSvg(
    browser,
    filePath,
    target.width,
    target.height,
    `<rect width="100%" height="100%" fill="#fff"/>${contentBoxes.join("")}${zoneRects.join("")}${overlapRects.join("")}${outlines.join("")}`,
  );
  return {
    targetRect: roundRect(target),
    contextRect: null,
    containers,
    stats: {
      containerCount: containers.length,
      zoneCount: clippedZones.length,
      overlapCount: overlaps.length,
    },
    warnings: payload.warnings,
  };
}

async function captureEvidence(browser, source, evidence, outputDir, planDir, settleMs) {
  const filePath = path.join(outputDir, `${safeName(evidence.id)}.png`);
  const opened = await openSource(browser, source, evidence, planDir, settleMs);
  const { context, page, viewport, sourceState, waitWarnings } = opened;
  try {
    let details;
    if (evidence.kind === "viewport") details = await captureViewport(page, evidence, filePath);
    else if (evidence.kind === "transition") details = await captureTransition(page, evidence, filePath, viewport);
    else if (evidence.kind === "block") details = await captureBlock(page, source, evidence, filePath, viewport);
    else if (evidence.kind === "family") {
      details = await captureFamily(browser, page, source, evidence, filePath, viewport);
    }
    else if (evidence.kind === "text-density") details = await captureTextDensity(browser, page, evidence, filePath);
    else if (evidence.kind === "spacing") details = await captureSpacing(browser, page, evidence, filePath);
    else throw new Error(`unsupported kind: ${evidence.kind}`);
    const stat = await fs.stat(filePath);
    if (!stat.isFile() || stat.size === 0) throw new Error("capture produced an empty file");
    sourceState.actualScrollY = await page.evaluate(() => window.scrollY);
    return {
      id: evidence.id,
      kind: evidence.kind,
      status: "success",
      file: filePath,
      sourceId: evidence.sourceId,
      sourceState,
      viewport,
      algorithmVersion: ALGORITHM_VERSION,
      ...details,
      warnings: [...waitWarnings, ...(details.warnings ?? [])],
    };
  } finally {
    await context.close();
  }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const planPath = path.resolve(options.plan);
  const planDir = path.dirname(planPath);
  const outDir = path.resolve(options.outDir);
  await fs.mkdir(outDir, { recursive: true });
  const rawPlan = JSON.parse(await fs.readFile(planPath, "utf8"));
  const plan = validatePlan(rawPlan, options.url);
  await writeJson(path.join(outDir, "screenshot-plan.json"), plan);

  const { module: playwright, moduleRoot } = await loadPlaywright();
  const browser = await playwright.chromium.launch({ headless: true });
  const artifacts = [];
  try {
    const sourceById = new Map(plan.sources.map((source) => [source.id, source]));
    for (const evidence of plan.evidence) {
      process.stderr.write(`[design-review] capture ${evidence.id} (${evidence.kind})\n`);
      try {
        artifacts.push(
          await captureEvidence(
            browser,
            sourceById.get(evidence.sourceId),
            evidence,
            outDir,
            planDir,
            options.settleMs,
          ),
        );
      } catch (error) {
        artifacts.push({
          id: evidence.id,
          kind: evidence.kind,
          status: "failed",
          sourceId: evidence.sourceId,
          algorithmVersion: ALGORITHM_VERSION,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }
  } finally {
    await browser.close();
  }

  const artifactById = new Map(artifacts.map((artifact) => [artifact.id, artifact]));
  const tasks = plan.tasks.map((task) => {
    const failedEvidenceIds = task.evidenceIds.filter(
      (evidenceId) => artifactById.get(evidenceId)?.status !== "success",
    );
    return {
      ...task,
      status: failedEvidenceIds.length === 0 ? "ready" : "failed",
      failedEvidenceIds,
    };
  });
  const failures = [
    ...artifacts
      .filter((artifact) => artifact.status === "failed")
      .map((artifact) => ({ type: "evidence", id: artifact.id, error: artifact.error })),
    ...tasks
      .filter((task) => task.status === "failed")
      .map((task) => ({
        type: "task",
        id: task.id,
        error: `references failed evidence: ${task.failedEvidenceIds.join(", ")}`,
      })),
  ];
  const manifest = {
    version: 2,
    algorithmVersion: ALGORITHM_VERSION,
    generatedAt: new Date().toISOString(),
    outDir,
    playwrightModuleRoot: moduleRoot,
    sources: plan.sources,
    context: plan.context ?? {},
    artifacts,
    tasks,
    failures,
  };
  await writeJson(path.join(outDir, "manifest.json"), manifest);
  process.stderr.write(
    `[design-review] manifest ${path.join(outDir, "manifest.json")} · ${artifacts.length - failures.filter((failure) => failure.type === "evidence").length}/${artifacts.length} artifacts ready\n`,
  );
  if (failures.length > 0) process.exitCode = 1;
}

main().catch((error) => {
  console.error(`capture-design-screenshots: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
