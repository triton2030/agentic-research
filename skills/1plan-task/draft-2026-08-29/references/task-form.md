# Task file form

One task is one self-describing file inside one epic folder. Exactly three
sections are allowed; schema tokens are literal and file content uses the
project's language. «Зачем» stays visible; status and proof live only in the
collapsed subtask reports.

```markdown
---
тип: задача
эпик: "[[<Epic name>]]"
эпик-снимок: "<hash written after rereading the epic>"
траектория: "<accepted 1planning answer: epic movement and why it beats the queue>"
режим: execution | wayfinding
статус: <map vocabulary>
порядок: <number in the epic task queue>
подзадач: 0
подзадач-готово: 0
обновлено: <date>
evidence: "<mandatory at ✅ — proof of the whole task>"
---

# <Self-describing task name — a checkable result>

## Зачем

<owner problem, required effect, and boundary; addresses of SPEC, canon, and
instructions instead of retelling>

- происхождение: <owner address / principle / document / explicit assumption>
- ось: <accepted decomposition axis and nearest checkable frontier>
- верно, пока: <material premise; collapsed → stop and replan>
- отпавшие ходы: <rejected route + reason>

## Принципы

- [[<principle or pair>]] — <what it settles here>
- <none fits: нет принципа — <reason>>

## Подзадачи

- [x] <Execution result or Wayfinding agent-resolvable question>

> [!note]- Отчёт
> статус <date>: <where we are>
> доказательство: <run, `_evidence/` file, or consumer acceptance>
> решение: <a willful decision via `1use-principles`, if any>
> <free-form result and findings>

- [ ] <next subtask>

> [!note]- Отчёт
> статус <date>: <where we are>
```

The report callout stands without indentation immediately after its checkbox;
indented, Obsidian renders code instead of a collapsed toggle.

## Admission and reconciliation

A new task requires the exact `1planning` approval that produced its
`траектория`, `режим`, `ось`, boundary, premise, and evidence target. The form
records these values and never recomputes whether the task should exist.

Creation and every rebuild reread the full current epic, write a fresh
`эпик-снимок`, quote the epic criterion in «Зачем», and reconcile any mismatch
before execution. A missing `ось:` in an older task is unresolved planning
state: establish it through `1planning` before the next rebuild.

## Routine rebuild versus material replan

Before changing subtasks after new evidence, compare five accepted invariants:
goal/effect in «Зачем», `эпик`, priority in `траектория`, boundary in «Зачем»,
and `ось`. If all hold, rebuild only affected subtasks. If one breaks, append
`- разрыв: <invariant · evidence>` in «Зачем», stop execution, and return to
`1planning`; the break is removed only by a newly approved cut.

## Task rules

- The task name is a checkable result and its evidence target is known at
  creation; if proof cannot be named, the task is Wayfinding or blurry.
- The file contains 3–7 ordered subtasks, each one move with one proof; work
  that grows its own checklist becomes another admitted task. Reports may grow;
  the task file has no line limit.
- A line enters only when no semantic owner exists; otherwise use an address.
  For source-owned composition, keep a `required → built` coverage line.
- Subtasks never touch another task or epic, and `[x]` requires a
  `доказательство:` address.
- Fog remains a line in «Зачем», not a subtask; an owner-only question appears
  only as its `1interview-tool` address, and a recurring class of such questions
  signals a principles gap for `1product-shaping`.
- Before writing a new task, reject duplicates against names in the epic. A
  frontier or JIT need is only a trigger for `1planning`; after approval,
  `1plan-task` alone creates the file.

## Lifecycle

Active and closed tasks remain in the epic folder; history lives in git, and a
report diverging from git is repaired before continuation. `⏳` records the
owner's deferral and reason; re-entry passes admission and reconciliation
again. Explicit backlog work lives once under `_ops/backlog/**`, while project
`STATUS.md` is only a projection. External runtime state is only a dated
`handle · observed_at · source` snapshot and must be re-resolved before a
dependent action; an unreachable source is `unknown`, never `active`.
