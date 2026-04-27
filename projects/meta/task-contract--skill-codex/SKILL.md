---
name: task-contract
description: >
  Use for durable task scope inside a Stage: create empty phase task skeletons,
  detail the current task only, acceptance criteria, Must/Must-not,
  verification, closeout, что считается готовым. Own
  `_ops/plans/phase-NN-*/task-MM-*.md`. Before freezing scope or criteria, route
  to `strategy-discussion` if the same goal could be solved by meaningfully
  different approaches or weak domain grounding changes task order. Route
  durable user truth to `user-truth`; strategy elsewhere. Skip lightweight
  preflight/review moments.
---

# Task Contract

Owner of task-files inside `_ops/plans/phase-NN-*/task-MM-*.md`.

## Role

Create empty task skeletons for a whole phase, then detail only the current
task-file when work enters it. The strategy provides the Stage anchor; domain
grounding explains why the task order is plausible.

A skeleton task names the task and Stage anchor only. Substeps, criteria,
evidence, and verification appear only when that task becomes current.

## Task Boundary

This skill owns level-2 task files and level-3 `Подшаги` only after a roadmap
Stage exists. The level-1 contract lives with `project-roadmap`.

Do not repair a weak roadmap by inventing task files. If no Stage fits, route
to `project-roadmap`; if approach branches remain unresolved, route to
`strategy-discussion`.

## First Read

- `_ops/PROJECT-ROADMAP.md` for Goal, relevant Stage, and Anti-goals.
- `_ops/INTERVIEW.md` for user truth that changes scope, Must-not, or verification depth.
- Existing task-file if this is update or closeout.
- `knowledge/guides/progressive-task-planning-playbook.md` when present and creating or resizing a task.
- `references/discovery-map.md` only when route/context is unclear.
- `references/failure-modes.md` for adversarial criteria design.

## Workflow

0. If the user message contains durable user truth (`хочу`, `предпочитаю`, `always`, `never`), route `user-truth` first when it could affect scope, Must-not, or verification depth.
1. Choose the relevant Stage from `PROJECT-ROADMAP.md`; if no Stage fits, route to `project-roadmap`.
2. If the task could be solved by meaningfully different approaches, or task
   order depends on domain prerequisites you cannot ground, route to
   `strategy-discussion` before freezing scope.
3. For a phase setup, create empty task skeleton files for the phase: title, Stage anchor, and empty required sections only.
4. For current work, detail exactly one task-file: Цель / Подшаги / Must / Must-not / Verification.
5. Reject any Цель that merely echoes the prompt or filename instead of naming the upstream outcome.
6. Run the gates from `references/task-file-lifecycle.md`, including no speculative subtasks/criteria and anchor existence.
7. On closeout, update the same file with actual evidence and verification; do not create a new summary file.

## Output Contract

Emit a compact receipt: phase skeletons created or current task detailed,
anchors, domain/user refs applied, verification status, and whether work may
continue.

## Role Boundaries

- file writes only task-files in `_ops/plans/phase-NN-*/` and the needed
  phase folder for the active Stage.
- Does not update `PROJECT-ROADMAP.md`, `INTERVIEW.md`, `learnings.md`, root instructions, or skill files.
- Does not decide instruction/runtime architecture; route to `instruction-layer` or `repo-shape`.
- Does not invent missing prerequisites or silently choose among valid
  approaches; route weak domain grounding or unresolved approach branches to
  `strategy-discussion`.

## References

- [references/task-file-lifecycle.md](references/task-file-lifecycle.md)
- [references/discovery-map.md](references/discovery-map.md)
- [references/failure-modes.md](references/failure-modes.md)
- [references/format-examples.md](references/format-examples.md)
