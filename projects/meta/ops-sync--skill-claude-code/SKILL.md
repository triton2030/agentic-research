---
name: ops-sync
description: >
  Use this skill whenever `_ops` structure must be created or mechanically synchronized: "sync _ops", "ensure ops", "создай phase folders", "папки фаз", "phase folder", "PROJECT-PLAN изменился", "план пересобран", "sync-ops", "ops drift", "materialize stages", "folder mismatch", "missing phase". Owns `_ops/plans/` shape and sync script. Skip strategy choices, preferences, task criteria, and instruction design.
---

# Ops Sync

Mechanical owner of `_ops/plans/` shape and phase-folder synchronization.

## Role

Create or synchronize phase folders from `PROJECT-PLAN.md`. Keep `_ops/plans/phase-NN-<slug>/` and `done/` present for each Stage. Never write task-file content.

## First Read

- `_ops/PROJECT-PLAN.md`
- `references/sync-ops.sh`

## Workflow

1. Confirm `PROJECT-PLAN.md` exists and has Stages.
2. Run or adapt `references/sync-ops.sh` from the skill directory.
3. Report created folders, orphan folders, slug drift, and non-empty folders needing human attention.
4. Route plan/status meaning changes to `project-strategy`.
5. Route task-file content to `task-contract`.

## Output Contract

```md
Ops synced: <created/changed/orphans>
Next route: <none/project-strategy/task-contract>
```

## Role Boundaries

- Writes only `_ops/plans/` folder shape.
- Does not edit `PROJECT-PLAN.md`, `INTERVIEW.md`, `learnings.md`, or task files.
- Does not invent stages.

## References

- [references/sync-ops.sh](references/sync-ops.sh)
