# Task File Lifecycle

A task file is the execution plan for one bounded unit of work. It lives in
`_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` and anchors to
`_ops/PROJECT-ROADMAP.md#Stage N` or a relevant `INTERVIEW.md` section.

Its job is to capture the phase task map as empty skeletons, then detail only
the current task's next frontier.

`PROJECT-ROADMAP.md` has the level-1 Stage-chain from zero to done. It does
not have task-level Steps or status checkboxes. Do not ask strategy to provide
execution subtasks.

## 1. Locate / Create

1. Read `_ops/PROJECT-ROADMAP.md` and choose the Stage that the task serves.
2. Use the matching `_ops/plans/phase-NN-<stage-slug>/` folder. If missing,
   create that phase folder lazily from the active Stage.
3. If updating or closing work, find the existing task file by task title or
   current ask.
4. If creating a new task, choose the next `task-MM-<task-slug>.md`; the task
   slug comes from the task purpose, not from a strategy Step.
5. If creating a phase task map, create empty skeleton task-files for the whole
   phase. Do not fill substeps, criteria, evidence, or verification yet.
6. If selecting current work, detail exactly one task: the smallest bounded
   outcome that advances the Stage, is feasible with current tools/context,
   and can produce observable evidence.

Do not create unrelated phase folders. Only create the phase folder needed for
the current Stage or phase skeleton work.

## 2. Discover

Translate only load-bearing upstream truth:

- `PROJECT-ROADMAP.md#Goal` — durable outcome.
- `PROJECT-ROADMAP.md#Stage N` — why this work is on trajectory.
- `PROJECT-ROADMAP.md#Anti-goals` — shortcuts to forbid.
- `INTERVIEW.md` — durable preferences, tone, boundaries, verification depth.
- `learnings.md` — relevant reality-vs-strategy deltas.

If the task cannot anchor to any Stage or preference, stop and route to
`project-roadmap`.

Do not read "just in case". Read sources only when they can change scope,
Must/Must-not, evidence, verification, blocker, or task shape.

## 3. Draft

Detailed current task shape:

```md
# <task title>

## Цель
<one durable result this task creates>

## Подшаги
- [ ] <execution action>
- [ ] <execution action>

## Критерии приёмки

### Must
- [ ] <criterion> — **Evidence**: <observable artifact>
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#stage-N-...`

### Must not
- [ ] <shortcut> — **Why this would be bypassed**: <bypass mechanic>

### Verification protocol
1. <command/action>
   Expected: <observable output>
   Actual: <closeout output, when known>
```

Only these three sections belong in the file: `Цель`, `Подшаги`,
`Критерии приёмки`.

Empty phase skeleton shape:

```md
# <task title>

## Цель

Anchored in: `_ops/PROJECT-ROADMAP.md#Stage N`

## Подшаги

## Критерии приёмки
```

Skeleton files exist to preserve task order for the phase. They do not contain
substeps, criteria, evidence, or verification until the task becomes current.

Draft only what is needed to execute or verify the next frontier. Do not add
speculative subtasks, distant task chains, or criteria "на всякий случай".
Criterion anchors may point to `PROJECT-ROADMAP.md`, `INTERVIEW.md`, or
`local-only — <reason>` when the gate is local code hygiene only.

## 4. Gates

- Task-level anchor: the whole task anchors to `PROJECT-ROADMAP.md#Stage N`
  or `INTERVIEW.md`.
- Criterion-level anchor: each Must has an `Anchored in:` line.
- **Anchor existence:** each `Anchored in:` path+section pair must resolve to
  a real heading in the target file. Before committing a criterion, verify with
  `grep -F "## <section>" <file>` mentally or through Bash.
- No `Anchored in:` points to another task file or to a path inside
  `_ops/plans/**`.
- Criteria are observable, unambiguous, non-bypassable, minimal,
  non-overlapping, and on-trajectory.
- `local-only` is allowed only for local code hygiene criteria, not as the
  task's strategic anchor.
- No speculative criteria: each Must is required to execute or verify the
  current bounded outcome.
- Empty skeleton tasks are valid before a task becomes current; detailed
  criteria are invalid at phase-skeleton time.
- No mini-plan inflation: only decompose a substep deeper when it has a
  blocker, unknown fact, broad/risky write, separate evidence, multiple
  decisions, or a prior direct-execution failure.
- Write-back: if execution discovers required work outside the current
  `Подшаги`, update this task-file via `task-contract` before continuing.

## 5. Closeout

Update the same task file: mark completed Подшаги/Must, refine Evidence, add
Actual under verification where useful. Do not add summary/changelog sections
and do not create a separate closeout file.

At closeout, scan remaining Подшаги and classify each:

- **Completed:** mark `[x]`.
- **Won't do (descoped):** strike-through plus one-line reason.
- **Orphan:** still relevant, not closed in this task. Leave open and emit a
  handoff back to `task-contract` with the decision: new task-file or migration
  as a Подшаг in a sibling task-file in the same Stage.

Closeout cannot be claimed if any Подшаг remains outside these three classes.

If closeout changes strategy truth, emit a handoff to `project-roadmap`; do
not edit strategy from this skill.
