---
name: project-roadmap
description: >
  Use for project direction and strategy truth: goal, vision, roadmap, stage chain, trajectory, replan, куда дальше, зачем. Own `_ops/PROJECT-ROADMAP.md` and `_ops/learnings.md`. Require domain grounding before committing Stages; route unclear domain prerequisites to `domain-clarifier`, user truth to `user-interview`, phase folders to `ops-sync`, task details to `task-contract`.
---

# Project Roadmap

Owner of project direction: `_ops/PROJECT-ROADMAP.md` and `_ops/learnings.md`.

## Role

Turn intent, domain knowledge, drift, and evidence into a short project
strategy for human understanding. The strategy explains how the project most
likely gets from zero to completion: Goal, success picture, approach, Stages as
large movements, and Anti-goals.

The strategy must be grounded enough to make the Stage-chain credible. It does
not carry Steps, status checkboxes, task queues, commands, criteria, or
evidence rows.

## Planning Levels

1. This skill owns level 1: `_ops/PROJECT-ROADMAP.md`, the zero-to-done phase path.
2. `task-contract` owns level 2: bounded task files inside one phase.
3. Task-file `Подшаги` are level 3: execution substeps inside one task.

Do not make level 1 more "concrete" by adding task lists, task paths,
checkboxes, commands, or substeps. If level 2 or 3 is needed, route to
`task-contract`.

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
2. Domain grounding: name the project/task domain, typical path, prerequisites before Stage 1, missing-middle check between Stages, and uncertainty.
3. If domain grounding is weak or consequential questions remain, route to `domain-clarifier` before committing the Stage-chain.
4. Check whether the ask changes Goal, success picture, Approach, Stages, Anti-goals, or learned reality.
5. Apply relevant user truth from `INTERVIEW.md`; route new user truth capture to `user-interview` when needed.
6. Update `PROJECT-ROADMAP.md` or `learnings.md` only when strategy truth changes.
7. Route phase-folder materialization to `ops-sync`.
8. Route task-file work to `task-contract`.

## First-Time Setup

If `_ops/PROJECT-ROADMAP.md` is absent, this is bootstrap.

1. Create `_ops/PROJECT-ROADMAP.md` skeleton: `Goal: TBD`,
   `Stages: TBD`, `Anti-goals: TBD`.
2. Ask the user one question: "Какова цель проекта на ближайшие движения?"
3. Fill Goal and Stage 1 from the answer. Do not invent Stages 2-N.
4. Stop and return control. The next action re-enters through `before-work`.

Do not start execution from inside this skill. Bootstrap finishes before the
next imperative is honored.

## Output Contract

Give a compact strategy receipt: domain grounding, changed strategy/learnings,
relevant Stage, and route next.

## Role Boundaries

- Does not write `INTERVIEW.md`; use `user-interview`.
- Does not create task-files; use `task-contract`.
- Does not sync phase folders mechanically; use `ops-sync`.
- Does not decide instruction/runtime architecture; use `instruction-layer` or `repo-shape`.
- Does not put execution Steps, checkbox status, acceptance criteria, commands, or evidence rows into `PROJECT-ROADMAP.md`.
- Does not invent domain expertise; use `domain-clarifier` when prerequisites or Stage order are uncertain.

## Структурная критика — Smith-оптика (швы стратегии)

Применяю к Goal / Stages / trajectory:

- **Missing intermediate Stage** (между текущим и целевым нет необходимого промежуточного)
- **Phantom prerequisite** (Stage ссылается на «уже сделано», чего нет)
- **Vague boundary** (Stage не даёт понять, какое крупное движение происходит)
- **Hidden coupling** (два «независимых» Stages на самом деле зависят)

**Stop-rule:** если не могу назвать траекторию Goal-к-сегодня в одной фразе — это и есть находка, остановись и спроси.

**Subagent fallback:** `smith` (опционально) при пересборке стратегии с 5+ Stages, на крупных handoffs или когда траектория чувствуется «не сходится».

Полный словарь: `knowledge/wisdom-structural-critique.md`.

## References

- [references/file-contracts.md](references/file-contracts.md)
- [references/strategy-protocol.md](references/strategy-protocol.md)
- [references/internal-tools.md](references/internal-tools.md)
