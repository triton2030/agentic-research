---
name: work-review
description: >
  Use this skill whenever current work is done or the user asks to verify/close it: "готово", "проверь", "закрыли", "финальная проверка", "перед финалом", "сверь", "что получилось", "review the work", "check it", "verify", "done", "close this", "final check". Compare result against goal, task criteria, evidence, and expected verification. Skip before-work/pre-write moments, pure brainstorming, and unrelated code review.
---

# Work Review

Use this after an action, before claiming completion.

## What It Does

1. Inspect what changed: diff, artifact, command output, or delivered text.
2. Compare against the active task contract: Цель, Подшаги, Must, Must-not, Verification.
3. Name missing evidence or blockers. If the task-file needs same-file closeout, route to `task-contract`; if the result changes the plan, route to `plan-drift-watch` / `project-strategy`.

## Receipt

```md
**Changed:** <diff/artifact summary>
**Matches:** <goal/criteria yes-no>
**Evidence:** <tests/checks/inspection>
**Closeout:** ready | needs `task-contract` | blocked
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
