# Task file contract

One task — one file with a self-describing name inside its epic's folder.
Exactly three sections: «Зачем», «Принципы», «Подзадачи» — a missing
mandatory section and an extra one both break the instrument. Context,
status and proofs live in this same file: context in «Зачем», status and
evidence in the subtask reports.

## Form

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
подзадач-готово: 0         # derived — the instrument writes it
обновлено: <date>          # derived — the instrument writes it
evidence: ""               # mandatory at ✅ — proof of the task as a whole
---

# <Self-describing task name — a checkable result>

## Зачем

<intent: what problem the owner sees (their words, with a recall address),
what effect completion must produce, boundaries; addresses of
SPEC/Canon/instructions instead of a retelling>

- происхождение: <owner (recall address) / Frame principle / document /
  planner's assumption with an escalation condition>
- верно, пока: <premise; it collapsed → stop and rebuild, don't finish up>
- отпавшие ходы: <discussed and rejected + the reason — so a re-plan does
  not reopen them; cross out dead branches, the block is not a chronicle>

## Принципы

- [[<principle or pair>]] — <what it affects in this task specifically>
- <none fits — an explicit line: нет принципа — <reason>; the section is
  always present>

## Подзадачи

- [x] <subtask — a result (Execution) or a question (Wayfinding)>

> [!note]- Отчёт
> статус <date>: <one line — where we are>
> доказательство: <address: a run, a file in `_evidence/`, consumer acceptance>
> решение: <a willful decision via `1use-principles`, if any>
> <then free form: what was done, why, findings>

- [ ] <next subtask>

> [!note]- Отчёт
> статус <date>: <one line>
```

The report callout stands **without indentation**, right after the checkbox
line: indented inside a list, Obsidian renders it as a code block instead of
a collapsed toggle. «Зачем» is always visible — the owner reads it; only
the reports are collapsed.

## Rules

- **`[x]` — only with a `доказательство:` line carrying an address in the
  report.** A self-report of "done" and the executor's transcript are not
  proof (copy of the map rule "✅ only with evidence" — edit together). The
  `подзадач`/`подзадач-готово` counters are written by the instrument,
  never by hand.
- **`✅` on the task requires `evidence`** — proof of the task as a whole;
  10/10 checkboxes is not closure. A seam with a neighboring task is
  confirmed by the **consumer** — acceptance or a contract test, not the
  delivering side.
- **Single source of truth — do not duplicate documentation.** A line may
  enter the task file on one admission only: its truth has no owner anywhere
  in the repo; otherwise — an address, not a copy. The check at writing
  time: name the owner where you verified the absence; can't — write a
  link. Content is judged at acceptance by a window that didn't write it —
  machines don't catch this.
- **The derivation act is the counterweight to the address rule**
  (requirements traceability). When deliverable composition is owned by a
  contract/canon/spec: as the first move, enumerate the composition from
  the source and keep a Done line "required → built" in the report that
  fails on any uncovered requirement. A list inside the assignment always
  beats a link to the source — so verify a foreign list against the source
  rather than replacing your enumeration with it. A missed requirement
  announces itself neither on screen nor in a green build — only in the
  coverage line.
- **Subtasks go in order** and do not touch other tasks' subtasks. The
  report is the only place for status; status sits physically under its
  subtask.
- **Wayfinding**: a subtask is phrased as a question; its proof is a
  recorded decision with provenance; the question map and the transition to
  Execution — [modes](modes.md).
- The task file has no line limit: subtask reports are a free field and may
  grow; size is held by the number of subtasks (below), not by lines.

## Size: measured in subtasks

- **3–7 subtasks** — Miller's span. Fewer than three — this is a subtask of
  someone else's task; merge into it. More than seven — cut: past ~7 the
  grip on the tail of the list degrades (the recorded Delta failure
  "commitments at the tail of a long list", SKILL.md).
- **A subtask is one move with one proof.** It grew its own checkboxes —
  promote it to a task.
- **The task name is a checkable result; the evidence is named at
  creation.** Cannot name the proof up front — that is Wayfinding in
  disguise, or a blurry formulation.

## Boundaries: three tests before creating the file

- **Epic test.** The task pulls two epics — fix the epic boundaries or set
  `зависит-от`; shared tasks do not exist.
- **Duplicate test.** Reread the task names in the epic's folder — that is
  what they lie side by side for. A new subtask fits two tasks equally —
  the boundary is wrong: move the boundary, don't duplicate work. Two
  living tasks for one Outcome — a rebuild signal, not neighbors.
- **Queue test (just-in-time).** A task is created when it is next by
  `порядок` or unblocks the next one; an epic is not pre-cut into tasks —
  what is cut in advance goes stale faster than it gets executed. An epic
  has few living tasks (≈up to five); more — the epic is too big or the
  tasks too small.

## Task↔epic reconciliation gate

Creating a task file and every rebuild begin by rereading the current full
epic file. In the same move the planner verifies the goal and boundaries,
writes a fresh `эпик-снимок`, quotes the epic's criterion in «Зачем» (the
third trace that the epic was actually read), and phrases `траектория` —
two linked answers: how the task moves the epic's criterion, and why it
matters more than other open tasks and epics closer in `порядок`.
`эпик-снимок` is a hash of the epic's significant part (frontmatter minus
derived fields + body outside «Апдейты»; the exact normalization is set by
the project instrument). It is written by **whoever reread**; the
instrument only checks freshness — an auto-written hash would make the gate
unable to turn red. A stale snapshot demands the same rereading and
re-verification; swapping the hash without re-verifying does not close the
gate. A task↔epic mismatch is fixed in the same move: by editing the epic
(per "Changing the map" in [map](map.md)) if its truth changed, or by
rebuilding the task.

## Provenance — why every line

A planner's default becomes "the owner's will" after two retellings, and
the redo arrives at acceptance, where it costs the most. Hence in «Зачем»:

- **owner** — only with a chat-recall record or a direct quote; "they would
  want it" is an assumption;
- **Frame/principle** — name the `P-*` or the Frame item;
- **document** — file#section;
- **planner's assumption** — an honest label + an escalation condition:
  which owner answer makes the requirement drop out.

## Lifecycle

- Active and closed tasks live in their epic's folder; a closed one stays
  at the same address — visible, like a closed epic. History lives in git.
- `_ops/backlog/**` is a separate surface for the explicitly deferred;
  backlog is a stable core, not an execution queue: a stale regime does not
  carry the right to steer work through backlog. One Outcome — one living
  file: the epic folder or backlog, not both.
- The project `STATUS.md` is a projection, not a second owner: no decisions
  or evidence of its own.
- Owner questions do not live in the task file — their lifecycle is
  [questions](questions.md).
- External runtime state (`thread`, job, deployment) in a report is only a
  dated snapshot `handle · observed_at · source`; before a dependent
  action, re-resolve the handle through the live owner; source unreachable
  — `unknown`, not `active`.

## Fresh-reader check

Before handing off, the file must survive a reader who was not in this chat
— and the writer cannot judge that: ambiguity is invisible to its author.
Run a fresh subagent with no chat context over the current epic file and
the task file; no subagent runtime available — reread both with cold eyes
as a degraded fallback. The reader first verifies the freshness of
`эпик-снимок` and the sense of `траектория` (copy of the gate above — edit
together); then it must reconstruct: what we are doing · why · boundaries ·
what evidence we stand on · what is next · when to stop · how the task
moves the epic's criterion — and name any line it can read two ways.
Anything not reconstructed means the file is not self-sufficient: fix the
file, don't explain in chat.
