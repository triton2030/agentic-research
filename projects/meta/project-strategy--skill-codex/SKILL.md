---
name: project-strategy
description: >
  Use for the top-level project roadmap and direction truth: goal, vision,
  zero-to-done path, stage chain, trajectory, replan, куда дальше, зачем. Own
  `_ops/PROJECT-ROADMAP.md` and `_ops/learnings.md`. Before committing Goal,
  Approach, Stages, or Anti-goals, route unresolved approach branches, weak
  domain grounding, or raw intent to `1strategy-discussion`; route durable user
  truth to `user-truth` and task details to `1task-contract`.
---

# Project Strategy

Owner of the top-level project roadmap: `_ops/PROJECT-ROADMAP.md` and
`_ops/learnings.md`.

## Role

Turn intent, domain knowledge, drift, and evidence into a top-level project
roadmap for human understanding. The roadmap explains how the project gets
from absolute zero to completion at level 1: Goal, success picture, Approach,
Stages as the full sequence of large movements, and Anti-goals.

The roadmap must be grounded enough to make the Stage-chain credible. It does
not carry level-2 tasks, level-3 substeps, status checkboxes, commands,
acceptance criteria, or evidence rows.

## Level 1 Boundary

This skill owns `_ops/PROJECT-ROADMAP.md`, the level-1 zero-to-done roadmap.
The canonical planning-level contract is `references/strategy-protocol.md`.

Do not make the roadmap more "concrete" by adding task lists, task paths,
checkboxes, commands, acceptance criteria, evidence, or substeps. If execution
detail is needed, route to `1task-contract`.

## First Read

- `_ops/PROJECT-ROADMAP.md` when it exists
- `_ops/INTERVIEW.md` as user-truth input, not owner surface
- `_ops/learnings.md`
- `references/file-contracts.md` before writing `_ops`
- `references/strategy-protocol.md` before changing strategy shape
- `references/internal-tools.md` for hidden pressure-test / premortem

## Workflow

0. If `_ops/PROJECT-ROADMAP.md` is missing, use First-Time Setup and stop before execution.
1. Drift sweep: before strategy-touching work, inspect recent closed task-files since the last relevant `learnings.md` entry, capped at 5. Compare their Stage anchors with current Stage wording in `PROJECT-ROADMAP.md`; if closeouts show silent drift, surface it before continuing.
2. Domain grounding: name the project/task domain, typical path from zero to
   done, prerequisites before Stage 1, missing-middle check between Stages, and
   uncertainty.
3. If the user intent is still raw, the Approach is not chosen, domain grounding
   is weak, or consequential branches remain, route to `1strategy-discussion`
   before committing the Stage-chain.
4. Check whether the ask changes Goal, success picture, Approach, Stages, Anti-goals, or learned reality.
5. Apply relevant user truth from `INTERVIEW.md`; route new durable user truth
   to `user-truth` when it should affect future routing, scope, tone, or
   verification depth.
6. Update `PROJECT-ROADMAP.md` or `learnings.md` only when strategy truth changes.
7. Keep phase folder materialization lazy; task-file creation belongs to
   `1task-contract`.
8. Route task-file work to `1task-contract`.

## First-Time Setup

If `_ops/PROJECT-ROADMAP.md` is absent, this is bootstrap.

1. If the first user message is still a raw desire or competing approaches are
   unresolved, route to `1strategy-discussion` before bootstrap.
2. Create `_ops/PROJECT-ROADMAP.md` skeleton: `Goal: TBD`,
   `Stages: TBD`, `Anti-goals: TBD`.
3. Ask the user one question: "Какова цель проекта на ближайшие движения?"
4. Fill Goal and the top-level Stage-chain only as far as it is grounded. If
   the zero-to-done path is not yet clear, write Stage 1 and route the missing
   branches to `1strategy-discussion`; do not invent Stages 2-N.
5. Stop and return control. The next action re-enters through `1before-work`.

Do not start execution from inside this skill. Bootstrap finishes before the
next imperative is honored.

## Output Contract

Give a compact strategy receipt: domain grounding, changed strategy/learnings,
relevant Stage, and route next.

## Role Boundaries

- Does not write `INTERVIEW.md`; use `user-truth`.
- Does not create task-files; use `1task-contract`.
- Does not sync phase folders as a separate route; keep folder materialization
  lazy and task-adjacent.
- Does not decide instruction/runtime architecture; use `1instruction-layer` or `1repo-shape`.
- Does not put level-2 tasks, level-3 substeps, checkbox status, acceptance
  criteria, commands, or evidence rows into `PROJECT-ROADMAP.md`.
- Does not invent domain expertise or choose hidden branches silently; use
  `1strategy-discussion` when prerequisites, Stage order, or Approach are
  uncertain.

## References

- [references/file-contracts.md](references/file-contracts.md)
- [references/strategy-protocol.md](references/strategy-protocol.md)
- [references/internal-tools.md](references/internal-tools.md)
