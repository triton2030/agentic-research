# Strategy Protocol

`_ops/PROJECT-ROADMAP.md` is the hot strategic truth layer for the project. `_ops/plans/` is the execution-plan layer. Do not let the names collapse back together.

## Shape

```md
## Goal
<one durable result, not a task>

## Когда стратегия сработала
<2-3 lines: what the happy end looks like>

## Approach & Why
<2-4 paragraphs/sentences: the expert approach and why this path>

## Stages

### 1. <Large movement>
<1-3 lines in cafe-language: what changes in the project and why it matters>

### 2. <Large movement>
<1-3 lines>

## Anti-goals
- <what is not progress>
```

## Domain Grounding

Before committing Stages, produce a short chat receipt:

- domain/type of project;
- typical path from zero to completion;
- prerequisites that must be true before Stage 1;
- missing-middle check between each adjacent Stage;
- uncertainty that would change the Stage-chain.

If this cannot be answered concretely, route to `domain-clarifier` before
writing or updating the Stage-chain. A strategy without domain grounding is a
plausible story, not a reliable plan.

## Altitude Contract

Write for a human who needs to understand direction, not for an LLM executor waiting for coordinates.

Allowed in strategy:
- durable systems and structural zones when they are the subject of the strategy (`_ops`, `_docs`, `app/<route>/_design-system/`, `AGENTS.md`);
- named Stages as large movements;
- tradeoffs, bets, boundaries, and anti-goals;
- enough concrete nouns that the direction is checkable.

Forbidden in strategy:
- Steps, `[ ]/[~]/[x]` status markers, task queues, commands, acceptance criteria, evidence rows, or closeout checklists;
- specific task-file paths under `_ops/plans/**`;
- implementation order that belongs inside a task file;
- skill mechanics unless the strategy itself is about skill/control-surface architecture.

The test: if the sentence tells an executor exactly what file to edit next or how to prove completion, it belongs in `_ops/plans/**/task-*.md`, not in `PROJECT-ROADMAP.md`.

## Stages And `_ops/plans/`

Each Stage heading in `PROJECT-ROADMAP.md` materializes to one `_ops/plans/phase-NN-<slug>/` folder. The folder is execution scaffolding; the Stage is the strategic anchor.

Task files anchor to `PROJECT-ROADMAP.md#Stage N`, then carry their own title, substeps, criteria, verification, and evidence. Strategy does not need a Step for every task.

## Evidence Sweep Before Strategy Changes

Before changing strategy/status truth, gather only enough evidence to avoid stale edits:
- current chat signal;
- relevant git diff/status;
- existing task files as execution evidence;
- learnings that describe strategy/preference deltas.

Do not copy task-file substeps, Must/Must-not, commands, or evidence into strategy.

## Drift Signals

- Strategy contains checkbox statuses or task-level substeps -> move them to task files.
- Strategy mentions concrete `_ops/plans/**/task-*.md` paths -> remove the execution coordinate.
- A meaningful task cannot anchor to any Stage -> update strategy before creating the task file.
- Stage headings changed but `_ops/plans/phase-NN-*` is stale -> route to `ops-sync`.
- A user preference says “make the plan more concrete” without artifact level
  -> route to `user-interview` and classify whether it applies to strategy or
  task files.
- Stage order depends on domain prerequisites the model cannot ground -> route
  to `domain-clarifier`.

## Minor Update Mode

If the request fits an existing Stage and does not change strategy truth, do not edit `PROJECT-ROADMAP.md`. Let `task-contract` handle execution detail in `_ops/plans/**/task-*.md`.
