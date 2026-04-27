---
name: work-review
description: >
  Use after work or before final: review, check, verify, done, closeout, готово,
  проверь, закрыли. Compare diff/artifact to goal, criteria, evidence,
  verification, open substeps, task shape, and execution lesson. Keep repairing
  until task criteria pass. Route task-file closeout or orphan work to
  `1task-contract`, durable user truth to `user-truth`, new unresolved branches
  to `1strategy-discussion`, and strategy/status reconciliation to
  `project-strategy`. Skip preflight and unrelated code review.
---

# Work Review

Use this after an action, before claiming completion.

## Ordering

If the same user message contains a user-truth signal (`хочу` / `предпочитаю` /
`люблю` / `не хочу` / `always` / `never` / `make this default`),
`user-truth` fires first when it affects this review or future work; this
skill runs after it.

## What It Does

1. Inspect what changed: diff, artifact, command output, or delivered text.
2. Compare against the active task contract: Цель, Подшаги, Must, Must-not, Verification, and execution lesson.
3. Check for orphan work: if any Подшаги remain open while completion is being claimed, route to `1task-contract` to continue the same task or split surviving work into a new task-file.
4. Check task shape: if the task proved too big, too small, or wrong-shape, emit a learnings handoff to `project-strategy` for a one-line `learnings.md` entry. Do not write learnings from this skill.
5. If the work revealed a new approach branch, hidden risk, or domain question
   that changes future strategy or scope, route to `1strategy-discussion`.
6. If evidence or quality fails, do not finalize. Continue repair in the current task until criteria and verification pass, or name the blocker and route to the owner-skill.
7. If the result changes strategy/status truth, route reconciliation to `project-strategy`.
8. If React/TS/Markdown structure changed, `$repo-power-tools` evidence may be `knip`, `lychee`, `markdownlint-cli2`, `tsc`, `biome`, `depcruise`, or `ast-grep`.

## Receipt

```md
**Changed:** <diff/artifact summary>
**Matches:** <goal/criteria yes-no>
**Evidence:** <tests/checks/inspection>
**Repair loop:** done | continue | blocked
**Closeout:** ready | needs `1task-contract` | strategy route | blocked
```

## Skip

Skip before any substantive action, during open-ended design talk, or when the user asks for a full independent code review rather than task closeout.

## Output Contract

Emit a compact receipt, then return control to the current task. Keep it to 3-5 lines unless blocking.

## Role Boundaries

- Do not become a strategy, architecture, or task-file owner.
- Do not broaden scope beyond this moment.
- Route to the owner-skill when durable state must change.

## Done When

The relevant rule is freshly in context, the next owner or action is clear, and no extra artifact was created by this skill.
