---
name: task-contract
description: >
  Use this skill whenever task scope or acceptance criteria must become durable: "task-файл", "критерии", "scope", "acceptance criteria", "что считается готовым", "зафиксируй задачу", "создай контракт", "обнови подшаги", "закрой задачу", "closeout", "Must/Must-not", "verification". Owns `_ops/plans/phase-NN-*/task-MM-*.md`. Skip strategy, preferences, instruction architecture, and lightweight preflight/review moments.
---

# Task Contract

Owner of task-files inside `_ops/plans/phase-NN-*/task-MM-*.md`.

## Role

Create, update, and close one task-file for non-trivial work inside the active stage. The file has exactly three load-bearing sections: Цель / Подшаги / Критерии приёмки. Use `references/task-file-lifecycle.md` before writing.

## First Read

- `_ops/PROJECT-PLAN.md` for Goal, active Stage, and Anti-goals.
- `_ops/INTERVIEW.md` for preferences that change scope, Must-not, or verification depth.
- Existing task-file if this is update or closeout.
- `references/discovery-map.md` only when route/context is unclear.
- `references/failure-modes.md` for adversarial criteria design.

## Workflow

1. Locate or create the task-file inside the active phase folder.
2. Prove the task anchors in `PROJECT-PLAN.md` or `INTERVIEW.md`; if not, route to `project-strategy`.
3. Draft Цель / Подшаги / Must / Must-not / Verification.
4. Run the seven gates from `references/task-file-lifecycle.md`.
5. On closeout, update the same file with actual evidence and verification; do not create a new summary file.

## Output Contract

Emit a compact receipt: path, intent, anchors, refs applied, Must count, verification status, and whether work may continue.

## Role Boundaries

- Writes only task-files in `_ops/plans/phase-NN-*/`.
- Does not update `PROJECT-PLAN.md`, `INTERVIEW.md`, `learnings.md`, root instructions, or skill files.
- Does not decide instruction/runtime architecture; route to `instruction-layer` or `repo-shape`.

## References

- [references/task-file-lifecycle.md](references/task-file-lifecycle.md)
- [references/discovery-map.md](references/discovery-map.md)
- [references/failure-modes.md](references/failure-modes.md)
- [references/format-examples.md](references/format-examples.md)
