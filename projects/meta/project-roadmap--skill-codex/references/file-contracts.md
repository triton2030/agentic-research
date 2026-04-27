# File contracts — `_ops` surface

`project-roadmap` owns `_ops/PROJECT-ROADMAP.md` and `_ops/learnings.md`.
`user-truth` owns `_ops/INTERVIEW.md`. `task-contract` owns task files and
lazy phase-folder materialization inside `_ops/plans/**`.

## Deciding Where Truth Lives

1. Durable user preference, taste, red line, or process default -> `INTERVIEW.md`.
2. Goal, success picture, strategic approach, full Stage-chain from zero to
   done, or Anti-goals -> `PROJECT-ROADMAP.md`.
3. Concrete execution tasks, substeps, acceptance criteria, commands, evidence,
   and closeout -> `_ops/plans/**/task-*.md`.
4. Reality contradicted expected strategy/preference and future sessions must not repeat it -> `learnings.md`.

If one role needs two truth files, ownership is drifting. Creating the folder
needed to place a task file is scaffolding, not truth ownership.

## `PROJECT-ROADMAP.md`

Purpose: explain the project direction like an experienced person would explain
it in a cafe: what result we want, why this route, what large movements get us
from absolute zero to completion, and what is not progress.

Works when:
- a human can understand the path without task context;
- task files can anchor to a Stage without the strategy listing their Steps;
- Stages cover the full high-level route and are concrete enough to constrain
  decisions, but not executable checklists;
- no `[ ]/[~]/[x]`, commands, evidence rows, task queues, or `_ops/plans/**/task-*.md` paths appear in strategy.

Drifts when:
- it does not explain the zero-to-done route;
- it becomes a roadmap spreadsheet or execution checklist;
- it uses “concrete” to mean filenames and commands rather than strategic nouns;
- it avoids all names and becomes too airy to constrain downstream work.

## `_ops/plans/phase-NN-<slug>/`

Purpose: materialize each strategic Stage as an execution folder. One Stage heading -> one phase folder. Folders are ephemeral execution scaffolding and may be recreated when strategy changes.

Rules:
- number and slug follow the Stage heading in `PROJECT-ROADMAP.md`;
- folder contents are task files and optional `done/` task-file archive when the project uses it;
- task-contract may create the needed phase folder lazily from the active Stage;
- external surfaces should not depend on task-file paths under `_ops/plans/**`.

## Task Files

Task files are the execution plan. They own title, Цель, Подшаги, Критерии приёмки, verification, evidence, and closeout.

A task anchors to `PROJECT-ROADMAP.md#Stage N` or a relevant `INTERVIEW.md` section. It does not require a Step in strategy. If no Stage fits, route back to `project-roadmap`.

## `learnings.md`

Purpose: preserve reality-vs-strategy or reality-vs-preference deltas so the same mistake does not repeat.

A learning needs Expected, Actual, Delta, and the owner it applies to. Once the delta is applied to `PROJECT-ROADMAP.md` or `INTERVIEW.md`, the learning may be removed.
