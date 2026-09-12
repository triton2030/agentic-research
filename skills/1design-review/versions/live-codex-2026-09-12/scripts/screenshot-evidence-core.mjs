export const ALGORITHM_VERSION = "design-evidence-v2.1.0";

export const EVIDENCE_KINDS = new Set([
  "viewport",
  "transition",
  "block",
  "family",
  "text-density",
  "spacing",
]);

const DEFAULT_VIEWPORT = Object.freeze({
  width: 1920,
  height: 1080,
  deviceScaleFactor: 1,
});

function finiteNumber(value, label) {
  const number = Number(value);
  if (!Number.isFinite(number)) throw new Error(`${label} must be a finite number`);
  return number;
}

export function normalizeViewport(value = {}) {
  const viewport = {
    width: Math.round(finiteNumber(value.width ?? DEFAULT_VIEWPORT.width, "viewport.width")),
    height: Math.round(finiteNumber(value.height ?? DEFAULT_VIEWPORT.height, "viewport.height")),
    deviceScaleFactor: finiteNumber(
      value.deviceScaleFactor ?? DEFAULT_VIEWPORT.deviceScaleFactor,
      "viewport.deviceScaleFactor",
    ),
  };
  if (viewport.width < 240 || viewport.height < 240) {
    throw new Error("viewport width and height must be at least 240 CSS pixels");
  }
  if (viewport.deviceScaleFactor <= 0 || viewport.deviceScaleFactor > 4) {
    throw new Error("viewport.deviceScaleFactor must be > 0 and <= 4");
  }
  return viewport;
}

export function normalizeRect(rect, label = "rect") {
  if (!rect || typeof rect !== "object") throw new Error(`${label} is required`);
  const normalized = {
    x: finiteNumber(rect.x, `${label}.x`),
    y: finiteNumber(rect.y, `${label}.y`),
    width: finiteNumber(rect.width, `${label}.width`),
    height: finiteNumber(rect.height, `${label}.height`),
  };
  if (normalized.width <= 0 || normalized.height <= 0) {
    throw new Error(`${label} width and height must be > 0`);
  }
  return normalized;
}

export function roundRect(rect, digits = 2) {
  const factor = 10 ** digits;
  return Object.fromEntries(
    Object.entries(rect).map(([key, value]) => [key, Math.round(value * factor) / factor]),
  );
}

export function unionRects(rects) {
  if (!Array.isArray(rects) || rects.length === 0) throw new Error("unionRects requires at least one rect");
  const normalized = rects.map((rect, index) => normalizeRect(rect, `rects[${index}]`));
  const x = Math.min(...normalized.map((rect) => rect.x));
  const y = Math.min(...normalized.map((rect) => rect.y));
  const right = Math.max(...normalized.map((rect) => rect.x + rect.width));
  const bottom = Math.max(...normalized.map((rect) => rect.y + rect.height));
  return { x, y, width: right - x, height: bottom - y };
}

export function expandRect(rect, ratio = 0.1) {
  const target = normalizeRect(rect);
  const dx = target.width * finiteNumber(ratio, "context ratio");
  const dy = target.height * finiteNumber(ratio, "context ratio");
  return {
    x: target.x - dx,
    y: target.y - dy,
    width: target.width + dx * 2,
    height: target.height + dy * 2,
  };
}

export function clampRect(rect, bounds) {
  const target = normalizeRect(rect);
  const limit = normalizeRect(bounds, "bounds");
  const x = Math.max(limit.x, target.x);
  const y = Math.max(limit.y, target.y);
  const right = Math.min(limit.x + limit.width, target.x + target.width);
  const bottom = Math.min(limit.y + limit.height, target.y + target.height);
  if (right <= x || bottom <= y) throw new Error("rect does not intersect source bounds");
  return { x, y, width: right - x, height: bottom - y };
}

export function contextCrop(rects, bounds, ratio = 0.1) {
  const target = unionRects(rects);
  const requested = expandRect(target, ratio);
  const actual = clampRect(requested, bounds);
  return {
    target: roundRect(target),
    requested: roundRect(requested),
    actual: roundRect(actual),
    clipped:
      Math.abs(requested.x - actual.x) > 0.01 ||
      Math.abs(requested.y - actual.y) > 0.01 ||
      Math.abs(requested.width - actual.width) > 0.01 ||
      Math.abs(requested.height - actual.height) > 0.01,
  };
}

export function transitionScrollY(beforeRect, afterRect, viewportHeight, documentHeight) {
  const before = normalizeRect(beforeRect, "beforeRect");
  const after = normalizeRect(afterRect, "afterRect");
  const height = finiteNumber(viewportHeight, "viewportHeight");
  const maxScroll = Math.max(0, finiteNumber(documentHeight, "documentHeight") - height);
  const beforeEnd = before.y + before.height;
  const boundary = after.y < beforeEnd ? after.y : (beforeEnd + after.y) / 2;
  return {
    boundary: Math.round(boundary * 100) / 100,
    scrollY: Math.max(0, Math.min(maxScroll, Math.round(boundary - height / 2))),
  };
}

export function intersectRects(first, second) {
  const a = normalizeRect(first, "first");
  const b = normalizeRect(second, "second");
  const x = Math.max(a.x, b.x);
  const y = Math.max(a.y, b.y);
  const right = Math.min(a.x + a.width, b.x + b.width);
  const bottom = Math.min(a.y + a.height, b.y + b.height);
  if (right <= x || bottom <= y) return null;
  return { x, y, width: right - x, height: bottom - y };
}

export function unionArea(rects) {
  if (!Array.isArray(rects) || rects.length === 0) return 0;
  const normalized = rects.map((rect, index) => normalizeRect(rect, `rects[${index}]`));
  const xs = [...new Set(normalized.flatMap((rect) => [rect.x, rect.x + rect.width]))].sort(
    (a, b) => a - b,
  );
  let area = 0;
  for (let index = 0; index < xs.length - 1; index += 1) {
    const left = xs[index];
    const right = xs[index + 1];
    if (right <= left) continue;
    const intervals = normalized
      .filter((rect) => rect.x < right && rect.x + rect.width > left)
      .map((rect) => [rect.y, rect.y + rect.height])
      .sort((a, b) => a[0] - b[0]);
    let covered = 0;
    let start = null;
    let end = null;
    for (const [top, bottom] of intervals) {
      if (start === null) {
        start = top;
        end = bottom;
      } else if (top > end) {
        covered += end - start;
        start = top;
        end = bottom;
      } else {
        end = Math.max(end, bottom);
      }
    }
    if (start !== null) covered += end - start;
    area += (right - left) * covered;
  }
  return area;
}

export function familyLayout(memberRects) {
  if (!Array.isArray(memberRects) || memberRects.length < 1 || memberRects.length > 4) {
    throw new Error("family requires 1-4 member rects");
  }
  const rects = memberRects.map((rect, index) => normalizeRect(rect, `members[${index}]`));
  const columns = rects.length === 1 ? 1 : 2;
  const rows = Math.ceil(rects.length / columns);
  const maxWidth = Math.max(...rects.map((rect) => rect.width));
  const maxHeight = Math.max(...rects.map((rect) => rect.height));
  const scale = Math.min(2, 720 / maxWidth, 420 / maxHeight);
  const cellWidth = Math.max(1, Math.ceil(maxWidth * scale));
  const cellHeight = Math.max(1, Math.ceil(maxHeight * scale));
  return { columns, rows, scale, cellWidth, cellHeight };
}

function requireString(value, label) {
  if (typeof value !== "string" || value.trim() === "") throw new Error(`${label} must be a non-empty string`);
  return value.trim();
}

function requireSafeId(value, label) {
  const id = requireString(value, label);
  if (!/^[A-Za-z0-9][A-Za-z0-9_.-]*$/.test(id)) {
    throw new Error(`${label} must match [A-Za-z0-9][A-Za-z0-9_.-]*`);
  }
  return id;
}

function validateEvidence(evidence, sourceById, ids) {
  const id = requireSafeId(evidence?.id, "evidence.id");
  if (ids.has(id)) throw new Error(`duplicate evidence id: ${id}`);
  ids.add(id);
  const kind = requireString(evidence.kind, `evidence ${id}.kind`);
  if (!EVIDENCE_KINDS.has(kind)) throw new Error(`evidence ${id} has unsupported kind: ${kind}`);
  const reviewAudience = kind === "viewport" ? "root-only" : "reviewer";
  if (evidence.reviewAudience !== undefined && evidence.reviewAudience !== reviewAudience) {
    throw new Error(`evidence ${id}.reviewAudience must be ${reviewAudience}`);
  }
  evidence.reviewAudience = reviewAudience;
  const sourceId = requireSafeId(evidence.sourceId, `evidence ${id}.sourceId`);
  const source = sourceById.get(sourceId);
  if (!source) throw new Error(`evidence ${id} references unknown source: ${sourceId}`);
  if (source.type === "image" && (kind === "text-density" || kind === "spacing" || kind === "transition")) {
    throw new Error(`evidence ${id}: ${kind} requires a URL source`);
  }

  if (kind === "transition") {
    requireString(evidence.beforeSelector, `evidence ${id}.beforeSelector`);
    requireString(evidence.afterSelector, `evidence ${id}.afterSelector`);
  }
  if (kind === "block") {
    const selectorCount = [evidence.selector, ...(evidence.selectors ?? [])].filter(Boolean).length;
    const rectCount = [evidence.rect, ...(evidence.rects ?? [])].filter(Boolean).length;
    if (source.type === "url" && (selectorCount < 1 || selectorCount > 2)) {
      throw new Error(`evidence ${id}: block requires one or two selectors`);
    }
    if (source.type === "image" && (rectCount < 1 || rectCount > 2)) {
      throw new Error(`evidence ${id}: image block requires one or two rects`);
    }
  }
  if (kind === "family") {
    if (!Array.isArray(evidence.members) || evidence.members.length < 1 || evidence.members.length > 4) {
      throw new Error(`evidence ${id}: family requires 1-4 explicitly selected members`);
    }
    const memberIds = new Set();
    evidence.members.forEach((member, index) => {
      const memberId = requireSafeId(member.id, `evidence ${id}.members[${index}].id`);
      if (memberIds.has(memberId)) throw new Error(`evidence ${id}: duplicate member id ${memberId}`);
      memberIds.add(memberId);
      if (source.type === "url") requireString(member.selector, `evidence ${id}.members[${index}].selector`);
      else normalizeRect(member.rect, `evidence ${id}.members[${index}].rect`);
    });
  }
  if (kind === "text-density" || kind === "spacing") {
    requireString(evidence.selector, `evidence ${id}.selector`);
  }
  if (kind === "spacing" && evidence.containers !== undefined) {
    if (!Array.isArray(evidence.containers)) throw new Error(`evidence ${id}.containers must be an array`);
    evidence.containers.forEach((container, index) => {
      requireSafeId(container.id, `evidence ${id}.containers[${index}].id`);
      requireString(container.selector, `evidence ${id}.containers[${index}].selector`);
    });
  }
}

export function validatePlan(input, fallbackUrl = "") {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new Error("plan must be an object");
  if (input.version !== 2) throw new Error("plan.version must be 2");
  if (!Array.isArray(input.sources) || input.sources.length === 0) throw new Error("plan.sources must not be empty");
  if (!Array.isArray(input.evidence) || input.evidence.length === 0) throw new Error("plan.evidence must not be empty");
  if (!Array.isArray(input.tasks)) throw new Error("plan.tasks must be an array");

  const plan = structuredClone(input);
  const sourceById = new Map();
  for (const [index, source] of plan.sources.entries()) {
    const id = requireSafeId(source.id, `sources[${index}].id`);
    if (sourceById.has(id)) throw new Error(`duplicate source id: ${id}`);
    source.type = requireString(source.type, `source ${id}.type`);
    if (!["url", "image"].includes(source.type)) throw new Error(`source ${id} has unsupported type: ${source.type}`);
    if (source.type === "url") source.url = requireString(source.url || fallbackUrl, `source ${id}.url`);
    if (source.type === "image") source.path = requireString(source.path, `source ${id}.path`);
    sourceById.set(id, source);
  }

  const evidenceIds = new Set();
  for (const evidence of plan.evidence) {
    evidence.viewport = normalizeViewport(evidence.viewport);
    validateEvidence(evidence, sourceById, evidenceIds);
  }

  const taskIds = new Set();
  const assignedEvidenceIds = new Set();
  for (const [index, task] of plan.tasks.entries()) {
    const id = requireSafeId(task.id, `tasks[${index}].id`);
    if (taskIds.has(id)) throw new Error(`duplicate task id: ${id}`);
    taskIds.add(id);
    task.question = requireString(task.question, `task ${id}.question`);
    task.decision = requireString(task.decision, `task ${id}.decision`);
    if (!Array.isArray(task.evidenceIds) || task.evidenceIds.length !== 1) {
      throw new Error(`task ${id}.evidenceIds must contain exactly one evidence id`);
    }
    for (const evidenceId of task.evidenceIds) {
      if (!evidenceIds.has(evidenceId)) throw new Error(`task ${id} references unknown evidence: ${evidenceId}`);
      const evidence = plan.evidence.find((item) => item.id === evidenceId);
      if (evidence.reviewAudience !== "reviewer") {
        throw new Error(`task ${id} references root-only evidence: ${evidenceId}`);
      }
      if (assignedEvidenceIds.has(evidenceId)) {
        throw new Error(`evidence ${evidenceId} is assigned to more than one reviewer task`);
      }
      assignedEvidenceIds.add(evidenceId);
    }
  }
  const unassignedEvidenceIds = plan.evidence
    .filter((evidence) => evidence.reviewAudience === "reviewer" && !assignedEvidenceIds.has(evidence.id))
    .map((evidence) => evidence.id);
  if (unassignedEvidenceIds.length > 0) {
    throw new Error(`reviewer evidence has no task: ${unassignedEvidenceIds.join(", ")}`);
  }
  return plan;
}
