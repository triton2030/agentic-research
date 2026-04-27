---
name: before-work
description: >
  Use before non-trivial work starts: implement, fix, edit, write, continue, or
  create artifacts. Re-anchor the intended action against PROJECT-ROADMAP,
  user truth, and the task contract; run a light frame check before execution.
  Route new unresolved branches, risky framing, or hidden approach tradeoffs to
  `strategy-discussion`; route durable user truth to `user-truth`, missing task
  contract to `task-contract`, missing strategy anchor to `project-roadmap`.
  Skip typos, facts, review, pure strategy talk, and imminent write checks.
---

# Before Work

Объяви в начале одной строкой: «Использую `before-work` — сверяю следующий ход со strategy».

This is a lightweight decision gate. It does not write files and does not own strategy or task contracts.

## Planning Boundary Check

Use the owner, not copied planning text, to choose the next route. If the next
action changes the roadmap, route to `project-roadmap`. If it needs task scope
or substeps, route to `task-contract`. If the right approach is still unclear,
route to `strategy-discussion`.

## Ordering

If the same user message contains a durable user-truth signal (`хочу` /
`предпочитаю` / `люблю` / `не хочу` / `always` / `never` / `make this default`),
`user-truth` fires first when it changes scope, Must-not, or verification depth;
this skill runs after it.

## What It Does

1. Read `_ops/PROJECT-ROADMAP.md` for Goal, relevant Stage, Anti-goals, and
   domain grounding.
2. Read relevant `_ops/INTERVIEW.md` user truth when it can change scope,
   Must-not, tone, or verification depth.
3. Look for an existing task file in the matching `_ops/plans/phase-NN-*`
   folder when execution work is about to start.
4. Compare the intended action against strategy, user truth, and task criteria.
5. Run a light frame check: if the intended action hides a new branch, risky
   framing, or materially different approach, route to `strategy-discussion`.
6. Extract the execution lesson: what these sources change about how this work
   should be done now.
7. If the ask does not fit any Stage, route to `project-roadmap`; if execution
   is non-trivial and no task contract exists, route to `task-contract`.

## Receipt

```md
**Stage:** <relevant Stage from PROJECT-ROADMAP>
**Upstream Goal:** <Goal or Stage outcome, not prompt paraphrase>
**Why this action serves Goal:** <one sentence>
**Execution lesson:** <how strategy/task/user truth changes this work>
**Must-not:** <top 1-2 anti-goals or task Must-not>
**Next / Shift:** <next task-file/owner-layer move>
```

Do not look for `[~]` in strategy. Execution status lives in task files.

## Role Boundaries

- Does not update `PROJECT-ROADMAP.md`; route strategy drift to `project-roadmap`.
- Does not create or close task files; route durable task scope to `task-contract`.
- Does not run expert discussion or domain clarification; route unresolved
  branches to `strategy-discussion`.

## Done When

The relevant Stage is named, the next owner/action is clear, and no file was changed by this skill.
