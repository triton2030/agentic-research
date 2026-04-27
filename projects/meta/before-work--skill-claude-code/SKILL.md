---
name: before-work
description: >
  Use before non-trivial work starts: implement, fix, edit, write, continue, or create artifacts. Re-anchor the intended action against PROJECT-ROADMAP, user truth, and the task contract; extract the execution lesson that changes how the work should be done. Route user truth to `user-interview`, missing domain prerequisites to `domain-clarifier`, missing task contract to `task-contract`, missing strategy anchor to `project-roadmap`. Skip typos, facts, review, pure interview talk, and imminent write checks.
---

# Before Work

Объяви в начале одной строкой: «Использую `before-work` — сверяю следующий ход со strategy».

This is a lightweight decision gate. It does not write files and does not own strategy or task contracts.

## Ordering

If the same user message contains a user-truth signal (`хочу` / `предпочитаю` /
`люблю` / `не хочу` / `always` / `never` / `make this default`),
`user-interview` fires first when it changes scope, Must-not, or verification
depth; this skill runs after it.

## What It Does

1. Read `_ops/PROJECT-ROADMAP.md` for Goal, relevant Stage, Anti-goals, and
   domain grounding.
2. Read relevant `_ops/INTERVIEW.md` user truth when it can change scope,
   Must-not, tone, or verification depth.
3. Look for an existing task file in the matching `_ops/plans/phase-NN-*`
   folder when execution work is about to start.
4. Compare the intended action against strategy, user truth, and task criteria.
5. Extract the execution lesson: what these sources change about how this work
   should be done now.
6. If the ask does not fit any Stage, route to `project-roadmap`; if domain
   prerequisites are unclear, route to `domain-clarifier`; if execution is
   non-trivial and no task contract exists, route to `task-contract`.

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
- Does not ask domain questions; route to `domain-clarifier`.

## Done When

The relevant Stage is named, the next owner/action is clear, and no file was changed by this skill.
