---
name: project-strategy
description: >
  Use this skill whenever project direction or plan truth must change: "план", "направление", "цель", "roadmap", "куда дальше", "зачем мы это делаем", "фаза", "пересобери план", "обнови PROJECT-PLAN", "stage", "trajectory", "strategy", "replan", "status changed". Owns `_ops/PROJECT-PLAN.md` and `_ops/learnings.md`. Skip task criteria, preference capture, mechanical phase-folder sync, and instruction architecture.
---

# Project Strategy

Owner of project direction: `_ops/PROJECT-PLAN.md` and `_ops/learnings.md`.

## Role

Turn intent, drift, and evidence into a short project trajectory. Keep the plan larger than task files and concrete enough to anchor downstream work.

## First Read

- `_ops/PROJECT-PLAN.md`
- `_ops/INTERVIEW.md` as input, not owner surface
- `_ops/learnings.md`
- `references/file-contracts.md` before writing `_ops`
- `references/plan-protocol.md` before changing plan shape
- `references/internal-tools.md` for hidden pressure-test / premortem

## Workflow

1. Check whether the ask changes Goal, Approach, active Stage, status, or learned reality.
2. Apply relevant preferences from `INTERVIEW.md`; route new preference capture to `preference-sync` when needed.
3. Update `PROJECT-PLAN.md` or `learnings.md` only when plan truth changes.
4. Route phase-folder materialization to `ops-sync`.
5. Route task-file work to `task-contract`.

## Output Contract

Give a compact strategy receipt: changed plan/learnings, active Stage, route next.

## Role Boundaries

- Does not write `INTERVIEW.md`; use `preference-sync`.
- Does not create task-files; use `task-contract`.
- Does not sync phase folders mechanically; use `ops-sync`.
- Does not decide instruction/runtime architecture; use `instruction-layer` or `repo-shape`.

## References

- [references/file-contracts.md](references/file-contracts.md)
- [references/plan-protocol.md](references/plan-protocol.md)
- [references/internal-tools.md](references/internal-tools.md)
