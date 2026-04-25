---
name: plan-drift-watch
description: >
  Use this skill whenever evidence shows plan/status drift: "фаза уже закрыта", "план устарел", "статус не тот", "мы уже сделали", "это больше не актуально", "сверь план", "git говорит другое", "task closed", "plan drift", "status changed", "out of date", "already done", "sync the plan". Signal drift from chat, git, closed tasks, or artifacts. Skip preference-only changes, task criteria drafting, and instruction-layer design.
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
