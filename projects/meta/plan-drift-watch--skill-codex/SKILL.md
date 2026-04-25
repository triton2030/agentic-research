---
name: plan-drift-watch
description: >
  Use when chat, git, task closeout, or artifacts show plan/status drift: already done, plan outdated, status changed, sync plan, фаза закрыта. Report evidence and route to `project-strategy`, `ops-sync`, or `task-contract`. Skip ordinary verification and new preferences.
---

# Plan Drift Watch

Use this when reality and the plan no longer line up.

## What It Does

1. Identify the evidence source: chat, git diff/log, closed task-file, artifact state, or command output.
2. Compare it to `PROJECT-PLAN.md` stage/step status and `learnings.md` if relevant.
3. Emit a drift signal and route: `project-strategy` for plan/status changes, `ops-sync` for phase-folder shape, `task-contract` for task closeout mismatch.

## Output Contract

```md
**Drift evidence:** <source>
**Plan says:** <current stage/status>
**Reality says:** <actual state>
**Route:** <owner-skill>
```

## Skip

Skip ordinary verification, new task scope, or fresh preferences that do not change plan/status truth.

## Output Contract

Emit a compact receipt, then return control to the current task. Keep it to 3-5 lines unless blocking.

## Role Boundaries

- Do not become a strategy, architecture, or task-file owner.
- Do not broaden scope beyond this moment.
- Route to the owner-skill when durable state must change.

## Done When

The relevant rule is freshly in context, the next owner or action is clear, and no extra artifact was created by this skill.
