import test from "node:test";
import assert from "node:assert/strict";
import {
  contextCrop,
  familyLayout,
  transitionScrollY,
  unionArea,
  validatePlan,
} from "../scripts/screenshot-evidence-core.mjs";

test("context crop adds ten percent per side and records clamp", () => {
  const crop = contextCrop(
    [{ x: 10, y: 20, width: 100, height: 50 }],
    { x: 0, y: 0, width: 500, height: 500 },
  );
  assert.deepEqual(crop.requested, { x: 0, y: 15, width: 120, height: 60 });
  assert.equal(crop.clipped, false);

  const clipped = contextCrop(
    [{ x: 2, y: 2, width: 100, height: 50 }],
    { x: 0, y: 0, width: 500, height: 500 },
  );
  assert.equal(clipped.clipped, true);
  assert.equal(clipped.actual.x, 0);
  assert.equal(clipped.actual.y, 0);
});

test("transition centers a gap and uses after start for overlap", () => {
  assert.deepEqual(
    transitionScrollY(
      { x: 0, y: 0, width: 100, height: 400 },
      { x: 0, y: 500, width: 100, height: 300 },
      200,
      1000,
    ),
    { boundary: 450, scrollY: 350 },
  );
  assert.deepEqual(
    transitionScrollY(
      { x: 0, y: 0, width: 100, height: 500 },
      { x: 0, y: 450, width: 100, height: 300 },
      200,
      1000,
    ),
    { boundary: 450, scrollY: 350 },
  );
});

test("union area does not double-count overlapping text rects", () => {
  assert.equal(
    unionArea([
      { x: 0, y: 0, width: 10, height: 10 },
      { x: 5, y: 0, width: 10, height: 10 },
    ]),
    150,
  );
});

test("family layout uses one common scale and max four members", () => {
  const layout = familyLayout([
    { x: 0, y: 0, width: 100, height: 40 },
    { x: 0, y: 0, width: 180, height: 60 },
    { x: 0, y: 0, width: 120, height: 50 },
    { x: 0, y: 0, width: 140, height: 55 },
  ]);
  assert.equal(layout.columns, 2);
  assert.equal(layout.rows, 2);
  assert.ok(layout.scale > 0);
  assert.throws(
    () => familyLayout(new Array(5).fill({ x: 0, y: 0, width: 10, height: 10 })),
    /1-4/,
  );
});

test("plan rejects implicit family trimming and diagnostic on image source", () => {
  const base = {
    version: 2,
    sources: [{ id: "image", type: "image", path: "/tmp/example.png" }],
    evidence: [
      {
        id: "family",
        kind: "family",
        sourceId: "image",
        members: new Array(5).fill(null).map((_, index) => ({
          id: `m${index}`,
          rect: { x: index * 10, y: 0, width: 8, height: 8 },
        })),
      },
    ],
    tasks: [],
  };
  assert.throws(() => validatePlan(base), /1-4/);

  base.evidence = [
    { id: "density", kind: "text-density", sourceId: "image", selector: "body" },
  ];
  assert.throws(() => validatePlan(base), /requires a URL source/);
});

test("plan rejects task ids that can collide after path normalization", () => {
  const plan = {
    version: 2,
    sources: [{ id: "page", type: "url", url: "http://127.0.0.1" }],
    evidence: [{ id: "screen", kind: "block", sourceId: "page", selector: "main" }],
    tasks: [
      {
        id: "a/b",
        question: "Is the screen coherent?",
        evidenceIds: ["screen"],
        decision: "signoff",
      },
    ],
  };
  assert.throws(() => validatePlan(plan), /must match/);
  plan.tasks[0].id = "a?b";
  assert.throws(() => validatePlan(plan), /must match/);
});

test("plan enforces one narrow evidence artifact per reviewer", () => {
  const plan = {
    version: 2,
    sources: [{ id: "page", type: "url", url: "http://127.0.0.1" }],
    evidence: [
      { id: "whole", kind: "viewport", sourceId: "page" },
      { id: "block-a", kind: "block", sourceId: "page", selector: "#a" },
      { id: "block-b", kind: "block", sourceId: "page", selector: "#b" },
    ],
    tasks: [
      { id: "review", question: "What is visible?", evidenceIds: ["whole"], decision: "signoff" },
    ],
  };
  assert.throws(() => validatePlan(plan), /root-only evidence/);
  plan.tasks[0].evidenceIds = ["block-a", "block-b"];
  assert.throws(() => validatePlan(plan), /exactly one/);
  plan.tasks = [
    { id: "review-a", question: "What is visible?", evidenceIds: ["block-a"], decision: "a" },
    { id: "review-b", question: "What else?", evidenceIds: ["block-a"], decision: "b" },
  ];
  assert.throws(() => validatePlan(plan), /more than one reviewer/);
  plan.tasks = [
    { id: "review-a", question: "What is visible?", evidenceIds: ["block-a"], decision: "a" },
  ];
  assert.throws(() => validatePlan(plan), /reviewer evidence has no task: block-b/);
});
