# Task file form

One task — one file with a self-describing name inside its epic's folder.
Exactly three sections; a missing mandatory section and an extra one both
break the instrument. Schema tokens are literal and never translated; file
content is written in the project's language. Context lives in «Зачем»,
status and proofs — only in the subtask reports.

```markdown
---
тип: задача
эпик: "[[<Epic name>]]"
эпик-снимок: "<hash of the epic's significant part — written by whoever reread it>"
траектория: "<how this moves the epic criterion and why it beats the queue>"
режим: execution | wayfinding
статус: <from the map vocabulary>
порядок: <number in the epic's task queue>
подзадач: 0                # derived — the instrument writes it
подзадач-готово: 0         # derived
обновлено: <date>          # derived
evidence: ""               # mandatory at ✅ — proof of the task as a whole
---

# <Self-describing task name — a checkable result>

## Зачем

<commander's intent: the problem in the owner's words (recall address), the
effect completion must produce, boundaries; addresses of SPEC/Canon/
instructions instead of a retelling>

- происхождение: <owner (recall address) / principle / document / planner's
  assumption with an escalation condition>
- верно, пока: <premise; it collapsed → stop and rebuild, don't finish up>
- отпавшие ходы: <rejected + reason, so a re-plan does not reopen them>

## Принципы

- [[<principle or pair>]] — <what it affects in this task specifically>
- <none fits — an explicit line: нет принципа — <reason>>

## Подзадачи

- [x] <subtask — a result (Execution) or an agent-resolvable question (Wayfinding)>

> [!note]- Отчёт
> статус <date>: <one line — where we are>
> доказательство: <address: a run, a file in `_evidence/`, consumer acceptance>
> решение: <a willful decision via `1use-principles`, if any>
> <free form: what was done, why, findings>

- [ ] <next subtask>

> [!note]- Отчёт
> статус <date>: <one line>
```

The report callout stands **without indentation**, right after its checkbox
line — indented, Obsidian renders a code block instead of a collapsed
toggle. «Зачем» is always visible — the owner reads it; only the reports are
collapsed.

## Rules

- **Reconciliation gate.** Creating a task and every rebuild begin by
  rereading the current full epic file; in the same move write a fresh
  `эпик-снимок`, quote the epic's criterion in «Зачем», and phrase
  `траектория` as two
  answers: how the task moves the epic's criterion, and why it matters more
  than other open work. A task↔epic mismatch is fixed in the same move.
- **Size is measured in subtasks: 3–7.** A subtask is one move with one
  proof; it grew its own checkboxes — promote it to a task. The file has no
  line limit — reports may grow.
- **The task name is a checkable result and its evidence is named at
  creation.** Cannot name the proof up front — that is Wayfinding in
  disguise, or a blurry formulation.
- **Single source of truth.** A line enters the file only if its truth has
  no owner anywhere in the repo; otherwise — an address. When deliverable
  composition is owned by a contract/canon/spec: first enumerate it from the
  source and keep a Done line "required → built" that fails on any uncovered
  requirement — a missed requirement announces itself only in the coverage
  line.
- **Subtasks go in order** and never touch other tasks' subtasks — in this
  epic or any other. `[x]` only with a `доказательство:` address.
- **Boundary tests before creating.** Duplicate: reread the task names in
  the epic folder — a new subtask fitting two tasks equally means the
  boundary is wrong, move it, don't duplicate work. Queue (just-in-time): a
  task is created when it is next by `порядок` or unblocks the next one; an
  epic is not pre-cut — pre-cut goes stale faster than it gets executed, and
  an epic holds few living tasks (≈ up to five).

## Lifecycle

- Active and closed tasks live in their epic's folder; a closed one stays at
  its address. History lives in git; reports diverging from git → trust git,
  fix the report, then continue.
- `⏳` on a task is the owner's deferral with a reason line; re-entry passes
  the reconciliation gate anew.
- `_ops/backlog/**` is the separate surface for the explicitly deferred; one
  Outcome — one living file. The project `STATUS.md` is a projection, not a
  second owner.
- External runtime state (`thread`, job, deployment) in a report is only a
  dated snapshot `handle · observed_at · source`; re-resolve through the
  live owner before a dependent action — source unreachable is `unknown`,
  not `active`.
