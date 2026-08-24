---
name: 1planning
description: >-
  Use when work must survive sessions or compaction, a plan continues, or the
  user asks for a plan, project remainder, stopping point, or epic map. Not in
  native Plan mode or for local checklists.
---

# Planning

A plan file is written for agents, not for the owner. This skill orchestrates
the autonomous work of many agents **in sequence**: the next agent opens a
clean window, picks the files up cold, and continues or stops by the files
alone — no shared chat, no parallel fleet by default. The owner watches
through the dashboard; agents live in the files. So write every line for a
reader who has none of your context and all of the weaknesses listed in
Delta — and prove readability with a fresh reader, not with your own eyes:
the fresh-reader check in [contract](references/contract.md).

Autonomy is steered not by long precise procedures — however much you spell
out, the forgotten clause is exactly where the error will live — but by a
goal that cannot be understood any way except correctly, plus transferred
intent pointing at it (commander's intent; the map runs from "Done means" in
`GOAL.md` — Covey's "begin with the end in mind"). Book and method names here
are deliberate compression: the model already knows the book, so the name
carries the how. Stated gates, forms and invariants always win over anything
a book implies.

Division of labor is hard: **documentation says "what and how"; planning says
only "in what order and where we are"**; the address rule and its
counterweight — the derivation act — are held by
[contract](references/contract.md).

A task has two modes, and "finding the path is itself a task to execute":
**Wayfinding** — the path is materially unclear, subtasks are questions;
**Execution** — the path is clear, subtasks are results. A full plan ahead
plus re-planning on evidence is many times cheaper than step-by-step control;
mode mechanics and the correction cycle — [modes](references/modes.md).

## Structure: folders, files, links

```text
<map root — named by the project instruction>/
└── <Epic name>/               ← epic folder
    ├── <Epic name>.md         ← epic file (folder note: name = folder name)
    ├── <Self-describing task name>.md   ← task: exactly one file
    ├── <Self-describing task name>.md
    └── _evidence/             ← heavy proof artifacts; subtask reports
                                  link to them
```

Nothing else lives in an epic folder: the path itself declares a task's
parent, and self-describing file names make the work visible without opening
anything.

**Schema tokens are literal.** Frontmatter keys (`тип`, `эпик`, `статус` …),
section headings («Зачем», «Принципы», «Подзадачи» …), the status vocabulary
and the dashboard file names are validated byte-for-byte by the project
instrument and read by the owner — never translate them. File content is
written in the project's language.

Every link between files is checkable:

- **task → epic**: the task frontmatter carries the `эпик` link,
  `эпик-снимок`, the `траектория` line and a quoted epic criterion — traces
  that the epic was actually read; the reconciliation gate —
  [contract](references/contract.md).
- **epic → tasks, progress**: task and subtask counters are derived; only
  the project instrument writes them; form and full list —
  [map](references/map.md).
- **epic and task → principles**: the mandatory «Принципы» section with an
  influence line — the entry point of `1use-principles`; rule owner —
  [map](references/map.md), task form — [contract](references/contract.md).
- **map → owner dashboard**: the map ships with a dashboard in the folder
  above the map root: `Дашборд.md` — one screen, `Дашборд.base` — epics and
  questions, `Планы.base` — tasks; forms and progress formulas —
  [map](references/map.md).
- **epics and tasks are independent**; both levels carry `порядок`; the rule
  and cross-cutting work as its own epic — [map](references/map.md).

## Goal

In hand: an epic map and the living file of the chosen task (self-describing
name inside its epic's folder), from which the next clean-window session
continues or stops **by the files themselves**, with no hidden chat — while
the owner sees without a retelling: how many epics remain, in order; what is
blocked; where the stuck point is; subtask progress of every living task.
The task file names the `GOAL.md` item it advances through its epic's
criterion.

Out of scope: the project goal (`1goal`) · creating principles
(`1product-shaping`) · side findings (`1findings`) · routes to knowledge
(`1index`) · project dashboard views beyond the map form (owner — the
project instruction).

## Success criteria

- The task file passes the fresh-reader check from
  [contract](references/contract.md): an agent without this chat
  reconstructs what · why · boundaries · on what evidence · when to stop —
  and names no line it can read two ways.
- Every material requirement carries provenance: owner's word / Frame /
  document / planner's assumption; "owner's word" is provable by a
  chat-recall record.
- One current Next; the subtasks written below it are a queue, not
  permission to execute everything at once.
- Affected epics and tasks conform to [map](references/map.md): machine
  invariants, statuses, dependencies, evidence at `✅`, progress counters.

## Invariants

- The plan trusts the executor with the route but never lets them invent the
  intent: a gap in intent is a question or an assumption with provenance,
  not a silent default.
- The «Принципы» section is read before work; a fork not covered by the plan
  goes to `1use-principles` first — principles and the goal close it without
  the owner; silence of the principles → a derivation marked "derived", not
  an escalation; the decision lands as a `решение:` line in the subtask
  report, not in chat.
- Plan files are written only by the orchestrating window: subagents and
  workers never write them (their returns go to `_evidence/**`); hooks and
  the project instrument hold the reminder and the ban.
- The map's composition changes only by the rules of
  [map](references/map.md): silently editing the denominator turns "how much
  is left" into decoration.
- A question to the owner lives as a question note per
  [questions](references/questions.md), not as a chat line that dies with
  the window.

## Delta — the weaknesses this skill compensates

The model decomposes work into steps easily. It reliably cannot:

- hold the project's total remainder — "how much is left" degrades into
  session memory and gut feel;
- stop decomposition until evidence — it draws a tree over three unverified
  routes;
- rebuild a plan instead of patching — it patches the stale;
- tell "the path is clear" from "the path feels clear";
- cut by dependencies — it cuts by chronology, hiding risk in the seams
  between stages;
- carry intent out of the chat — the file says "what" while "why" dies with
  the window;
- honor commitments at the tail of a long list;
- keep its own default from becoming "the owner's will" after two
  retellings.

Write plan files against these weaknesses. The fresh-reader check exists
because the last one applies to the writer too: ambiguity is invisible to
its author.

## Known failures

`when → failure → cost → route`

- plan before evidence → a step tree over unverified routes → the whole tree
  is redone → [modes](references/modes.md)
- new evidence → a patch on top of subtasks → a zombie plan keeps steering
  the work → [modes](references/modes.md)
- path unclear, but subtasks are "results" → an architectural choice made on
  the fly without grounds → [modes](references/modes.md)
- cutting heavy work → chronology instead of an axis → risk hidden between
  stages → [decompose](references/decompose.md)
- a requirement without provenance → the planner's guess became "the owner's
  will" → [contract](references/contract.md)
- the plan retells SPEC/Canon → a second truth rots silently →
  [contract](references/contract.md)
- deliverable composition owned by contract/canon/spec, derivation act not
  performed → a missed requirement stays silent until acceptance →
  [contract](references/contract.md)
- `[x]` set without proof → the progress bar lies to the owner →
  [contract](references/contract.md)
- a task outgrew its subtask list → a monster file nobody rereads →
  [contract](references/contract.md)
- the session changed → report statuses no longer match reality → the next
  session redoes finished work → [contract](references/contract.md)
- work wider than one context → workers without a file-disjoint contract →
  clobbered edits → [delegation](references/delegation.md)
- a worker writes into a plan file → broken form and counters →
  [delegation](references/delegation.md)
- an epic closed on the executor's word → `✅` without evidence → the map
  lies to the owner → [map](references/map.md)
- a plan written or a task continued without rereading the epic → a local
  Next drives against the shared trajectory — caught by the owner →
  [contract](references/contract.md)
- an owner question asked as a chat line mid-wave → lost with the window →
  the branch stalls or gets invented → [questions](references/questions.md)

## Mechanics

Two hard transitions — everything else is postconditions:

- **The owner's "yes" before any files; questions before the
  justification**: first, every visible owner question is filed as a
  question note per [questions](references/questions.md) — what stops the
  affected branch and what continues on an assumption is decided by its
  blocking vocabulary; the justification carries the trace: note or recall
  addresses, or an explicit "no forks found". The justification (place on
  the map: which epic and why it is next by order and blockers · goal ·
  value · mode · appetite) goes to chat; files — after consent. Work that
  cannot find its epic is a question to the map, not a license to dig
  without one. Before the justification, run `1use-principles` over the
  plan's composition, not only over a noticed fork: without it the
  `Frame/principle` provenance mark may not be used.
- **Reread the current epic file and the questions folder before every new
  material step**; immediately verify the task's `эпик-снимок`: stale —
  reread the epic and re-verify the task in the same move. Continuing from
  chat memory is where zombie plans come from; evidence classification and
  rebuild — [modes](references/modes.md).

Admission: the work is chosen and outlives the session; native Plan Mode
active → stay silent; otherwise — a discussion in chat, no file.

Postconditions of the living task file — per
[contract](references/contract.md): exactly the fixed sections, provenance
and "true while" in «Зачем», principles with influence lines, subtasks cut
along a named axis ([decompose](references/decompose.md)), size per the
contract rule.

## Completion

Closure follows the task file's criteria and the
[contract](references/contract.md) rules, not fatigue: proofs sit at the
checkboxes and in the task's `evidence`; the seam is accepted by its
consumer. Affected map epics are updated in the same move per
[map](references/map.md): status, evidence link, released blockers, an
«Апдейты» line; the project instrument has been run — counters are fresh;
the project `STATUS.md` (if routed) is updated. The next session can
continue or close by the files. Whatever did not make it in — a separate
line in the last subtask's report, with the reason.
