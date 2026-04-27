---
name: before-write
description: >
  Use immediately before substantive repo-tracked edits: `apply_patch`,
  generated file creation, bulk rewrite, or content/schema/instruction changes.
  Check target, task contract, Must-not, write scope, and the execution lesson
  from strategy/task/user truth. Route new unresolved branches or hidden
  approach/domain tradeoffs to `strategy-discussion`; route durable user truth
  to `user-truth`, and missing contract or out-of-substep work to
  `task-contract`. Skip pure reads, shell checks, trivial typos, and work-start
  talk handled by `before-work`.
---

# Before file write

Use this as the last lightweight check before a substantive repo-tracked file or artifact edit.

## Write Boundary Check

Verify that the target file matches the owner layer. Do not approve a write
that puts task scope, task paths, criteria, commands, evidence, or substeps into
`PROJECT-ROADMAP.md`. Do not use a task file to compensate for a missing Stage.

## Ordering

If the same user message contains a user-truth signal (`хочу` / `предпочитаю` /
`люблю` / `не хочу` / `always` / `never` / `make this default`),
`user-truth` fires first when it changes this write's scope, Must-not, or
verification depth; this skill runs after it.

## What It Does

1. Identify the intended edit target and why it is being changed. `Why` means upstream purpose from plan/contract, not “because this file was requested”.
2. Re-open the nearest task contract if one exists; read Цель, current Подшаг, Must, Must-not, and Verification.
3. Read relevant strategy/user truth only enough to extract the execution lesson for this write.
4. Confirm the write is within scope. If the only purpose you can name is the local operation (“исправить файл”, “обновить текст”), stop and re-read the plan/task; route instead of writing if the upstream purpose remains unclear.
4a. Confirm the imminent write is covered by an existing Подшаг in the task-file. If this action is a new step not listed in Подшаги (setup, fix-of-fix, side-effect work), STOP and route to `task-contract` for a one-line Подшаг addition, then resume the write.
5. If domain prerequisites, hidden requirements, or alternate approaches affect
   this write and are unclear, route to `strategy-discussion`.
6. If no contract exists for non-trivial work, route to `task-contract`. If the plan anchor is missing, route to `project-roadmap`. If the write changes instruction/runtime shape and owner is unclear, route to `instruction-layer` or `repo-shape`.
7. Self-check: compare `Upstream Goal` and `Why this write serves Goal` in the receipt with the current user prompt. If 3+ consecutive words from the prompt appear in either field, this is paraphrase failure. Re-read the contract; do not continue the write.
8. For React/TS/Markdown moves, deletes, or cleanup, consider `$repo-power-tools` for `knip`, `lychee`, `markdownlint-cli2`, `tsc`, `biome`, `depcruise`, or `ast-grep` evidence.

## Receipt

**Discipline rule:** поля приходят из контракта verbatim или близко к тексту источника. Один collapsed field схлопывается в paraphrase prompt'а, поэтому два отдельных поля: что цель плана, и отдельно как этот write её обслуживает. Без второго поля receipt — декорация.

```md
**file edit target:** <path or artifact>
**Upstream Goal:** <from task-file/Stage — not a paraphrase of the user request>
**Why this write serves Goal:** <explicit connection in one sentence>
**Execution lesson:** <how strategy/task/user truth changes this write>
**Must-not:** <top 1-2 constraints from contract>
**Proceed:** yes | route to <owner-skill>
```

**Anti-example:** request “patch this file” → “Upstream Goal: patch this file”, “Why: to patch the file”. Both are paraphrase prompt. Read the contract instead.

## Skip

Skip for pure reads, terminal checks, generated caches, one-character typo fixes, or when `before-work` already refreshed the same contract in this turn and no write-scope changed.

## Output Contract

Emit a compact receipt, then return control to the current task. Keep it to 3-5 lines unless blocking.

## Role Boundaries

- Do not become a strategy, architecture, or task-file owner.
- Do not broaden scope beyond this moment.
- Route to the owner-skill when durable state must change.
- Do not approve a write whose purpose merely repeats the prompt or filename.

## Done When

The relevant rule is freshly in context, the next owner or action is clear, and no extra artifact was created by this skill.
