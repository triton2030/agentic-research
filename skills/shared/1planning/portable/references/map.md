# Epic — a large finite work with checkable closure

Moment: the map is being created or changed — epics, their order, statuses,
dependencies and task homes. The map is the owner's instrument panel: it
answers "where are we and how much is left" without a retelling. The exact
map root folder, the instrument command and the moment it runs are named by
the project instruction; the skill owns the form and the requirement that
the instrument exists.

## Home of an epic and its tasks

Every epic is a folder; inside — the epic file named after the folder
(folder note), its task files and `_evidence/`:

```text
<map root folder>/
  <Epic name>/
    <Epic name>.md
    <Self-describing task name>.md
    _evidence/
```

The epic folder is the only home of its tasks; nothing else lives there — a
stray file turns the instrument red. The exact task form is held by
[contract](contract.md). Epics are independent: an epic is constructed so
that work inside it does not take work away from other epics; a task does
not touch other tasks; `порядок` and `зависит-от` are the only links.
Internal decomposition by itself changes neither the number nor the status
of epics, but every task rereads its current epic and serves its closure
criterion. There is no class of "cross-cutting plan on top of other
epics" — how such work is shaped is held by the postcondition
"Cross-cutting work has its own owner" below.

A closed epic is never deleted or hidden: it stays on the map forever with
status `✅`, so the owner sees the chapter and its completion.

## An epic is one note

The map is moved by one event: an epic closed by its criterion, with proof.
The criterion names **the evidence to be presented**, not a description of
intent: "the criterion is what it is proven by". The early indicator is a
separate falsifiable observation able to refute the course before closure;
it does not replace the closure criterion.

```markdown
---
тип: эпик
описание: "<one short line for the owner — a dashboard column>"
область: <launch-critical part of the project>
порядок: <number in execution order>
статус: <from the vocabulary below>
health: 🟢 | 🟠 | 🔴
запуск: true | false
критерий: "<checkable passing condition>"
ранний-индикатор: "<falsifiable signal before closure>"
зависит-от:
  - "[[<blocking epic>]]"
задач: 0                   # derived — the instrument writes it
задачи: []                 # derived — the instrument writes it
подзадач: 0                # derived — the instrument writes it
подзадач-готово: 0         # derived — the instrument writes it
evidence: "<link to the accepted proof — mandatory at ✅>"
обновлено: <date of the last update>
---

# <epic name>

<what this is, in the owner's plain words — one paragraph>

## Принципы

- "[[<matching pair or principle>]] — <which fork or criterion it settles
  right here>"

## Аппетит

<how much time or effort we are willing to spend before revisiting; the
form comes from Shape Up>

## No-gos

- <what we deliberately do not do; if there are no prohibitions, say so>

> [!note]- Технические подробности
> <for agents; the owner expands at will>

## Апдейты

- <YYYY-MM-DD> · <🟢/🟠/🔴> · <one line of increment>
```

The body section set is fixed: «Принципы» · «Аппетит» · «No-gos» ·
«Апдейты»; a missing section and an extra one are both red. Updates are
append-only: `date · 🟢/🟠/🔴 · one line`; earlier entries are never
rewritten. `health` and `обновлено` derive from the last «Апдейты» line;
`задач`, `задачи`, `подзадач`, `подзадач-готово` derive from the task
files; everything derived is written by the instrument (write mode), never
by hand. `health` describes the risk of the course, `статус` — the position
on the map; 🔴 does not substitute for 🛑.

**«Принципы» is always present**, even when nothing applies. Principles and
frames are blurry direction-setters; the influence line says what they act
on in this specific epic — that is the `1use-principles` entry point for
decisions made without the owner. A generic "sets the principles" does not
count: the truth lives with the pair, the epic carries only the route. The
sign a pair is needed: it stands in the provenance of the epic's task
requirements or settles a fork inside the epic. If no pair fits — that is a
completeness test for `1product-shaping`: invoke the skill; it returns "no
frame" — an explicit line `нет принципа — <reason>`; the instrument counts
the line as filled, the honesty of the gap is judged at audit.

The epic body is at most 60 non-empty lines, counting headings and callout
content, excluding frontmatter and the «Апдейты» section; count after
rumdl normalization.

## Status vocabulary

`✅ готово · 🔨 в работе · 🟡 надо сделать · 🔒 заблокировано · 🛑 затык ·
⏳ отложено`

(done · in progress · to do · blocked · stuck · deferred — the tokens
themselves are literal and never translated)

- `✅` — only with a link in `evidence`: a fresh run or consumer
  acceptance; the executor's transcript and self-report are not proof
  (copy of the contract rule "[x] with proof" — edit together).
- `🔒` is true exactly when `зависит-от` contains an unclosed epic;
  blockers closed — `🟡`. The move that closes an epic flips `🔒 → 🟡` in
  the same move.
- `🛑` — the branch is stopped on a decision or an external event; an open
  question sits next to it ([questions](questions.md)) or the external gate
  is named.
- `⏳` — deliberately deferred; excluded from "how much is left to launch"
  and shown as its own number: a growing "deferred" is also a signal.

The vocabulary is shared by epics and tasks.

## "How much is left"

Statuses in execution order answer it: the `✅` bar descends from the top;
below it — `🔨`, `🛑` and the queue. A hand-written percent is never
written — an uncheckable number drifts toward optimism; a **computed**
subtask percent is legitimate only as the dashboard formula over the
instrument's counters (owner decision 2026-08-24) and shows progress
inside, without replacing the in-order bar. `область` and `запуск` are the
map's axes: "how much is left to launch" is counted over `запуск: true`
only.

## The project instrument

The map instrument turns red when any machine invariant of the form is
violated:

- an epic folder holds a file other than the folder note, the task files
  and `_evidence/`; the folder note is missing or not named after the
  folder;
- the markdown section set of an epic or a task differs from the fixed
  one — in either direction: a missing mandatory section or an extra one;
- «Принципы» is empty (in an epic or a task); the epic body does not start
  with a non-empty context paragraph before the first section;
- a subtask checkbox has no report callout, or the callout does not stand
  right after the checkbox line;
- a task lacks the `эпик` link, the link does not match the folder, there
  is no `эпик-снимок` or `траектория` line, or `эпик-снимок` is stale;
- `[x]` without a `доказательство:` line carrying an address; the
  `подзадач`/`подзадач-готово`/`задач`/`задачи` counters diverge from the
  files;
- an epic lacks `ранний-индикатор` or the «Аппетит» and «No-gos» slots;
- updates or their derived fields violate
  ["An epic is one note"](#an-epic-is-one-note); the epic body exceeds 60
  non-empty lines;
- `статус`, `зависит-от`, `порядок` or the `evidence` mandatory at `✅`
  violate ["Changing the map"](#changing-the-map).

The instrument also warns (not red): more than one `🔨` task in an epic — a
sign the tasks were cut wrong, or they conflict ("cannot do one without
starting the other") — a signal to rebuild the boundaries, not a working
mode.

Derived fields are written only by the instrument's write mode.
`эпик-снимок` is the exception with the inverse role: it is written by
whoever reread, the instrument only verifies ([contract](contract.md), the
reconciliation gate). The content of `траектория`, of the principle
influence lines, and the absence of documentation retelling are judged at
acceptance by a window that didn't write them — machines don't catch this;
the moment and the lens are named by the project instruction.

The machine-readable layer = frontmatter + the body sections named here;
dashboards read frontmatter only.

## The owner's dashboard

A map without a screen is half the work: the owner follows the project
through the dashboard, not the files. When a map is created, the dashboard
is created at once; on any other map edit a missing file is created from
the template, while existing files are never overwritten — project views
live in them. The dashboard's home is the folder above the map root;
`<map root folder>` and `<questions folder>` are named by the project
instruction. The dashboard is the owner's surface: its file names, headings
and view names stay in the owner's language.

`Дашборд.base` — epics and open questions:

```yaml
filters:
  or:
    - file.inFolder("<map root folder>")
    - file.inFolder("<questions folder>")
formulas:
  Прогресс: 'if(note["подзадач"] > 0, ((note["подзадач-готово"] / note["подзадач"]) * 100).round().toString() + "%", "—")'
views:
  - type: table
    name: По порядку
    filters:
      and:
        - тип == "эпик"
        - запуск == true
    order:
      - порядок
      - file.name
      - описание
      - статус
      - health
      - задач
      - formula.Прогресс
      - задачи
      - зависит-от
    sort:
      - property: порядок
        direction: ASC
  - type: table
    name: Затыки
    filters:
      and:
        - тип == "эпик"
        - статус == "🛑 затык"
    order:
      - file.name
      - критерий
  - type: table
    name: Открытые вопросы
    filters:
      and:
        - тип == "вопрос"
        - статус == "открыт"
    order:
      - file.name
      - касается
  - type: table
    name: Отложенное
    filters:
      and:
        - тип == "эпик"
        - статус == "⏳ отложено"
    order:
      - file.name
      - область
      - критерий
```

`Планы.base` — tasks by their own files:

```yaml
filters:
  and:
    - file.inFolder("<map root folder>")
    - тип == "задача"
formulas:
  Прогресс: 'if(note["подзадач"] > 0, ((note["подзадач-готово"] / note["подзадач"]) * 100).round().toString() + "%", "—")'
views:
  - type: table
    name: Живые задачи
    filters:
      and:
        - статус != "✅ готово"
    order:
      - file.name
      - эпик
      - статус
      - режим
      - порядок
      - formula.Прогресс
      - обновлено
    sort:
      - property: эпик
        direction: ASC
      - property: порядок
        direction: ASC
```

No questions folder — the «Открытые вопросы» view stays empty; an address
is not invented.

`Дашборд.md` — the owner's single screen, embedding the views:

```markdown
# 🚀 <project name> — путь к цели

<one or two lines: the status legend and what the ✅ bar means>

## 🗺️ Путь по порядку

![[Дашборд.base#По порядку]]

## 📋 Живые задачи

![[Планы.base#Живые задачи]]

## 🛑 Где затык

![[Дашборд.base#Затыки]]

## ❓ Вопросы ко мне

![[Дашборд.base#Открытые вопросы]]

## ⏳ Отложенное

![[Дашборд.base#Отложенное]]
```

Project views and columns are added in these same files. Hyphenated
property names in formulas are addressed as `note["имя-с-дефисом"]` — a
bare name parses as subtraction.

## Changing the map

The map is the denominator of the promise. Splitting an epic, merging,
reordering, a new epic — a separate visible change with a reason line. An
epic is never deleted: leaving the path is status `⏳` with a reason line;
closure is a visible `✅` with evidence; the note and its home remain on
the map (copy of the "Home of an epic" invariant — edit together). Editing
a status as work proceeds is a normal move; editing the map's composition
"while we're at it" is not.

Map↔task coherence is verified by the project instrument (a script or a
fresh window against the code, not against the plan), not by the hand that
draws the bar. A divergence is a finding, not a silent fix. The project
instruction names the instrument and the cadence **before** the map is
declared the owner's instrument: a bar drawn and verified by the same hand
is worse than no bar.

## Creating the map

The map is built once, from the current state to "Done means" in `GOAL.md`;
composition approval is the owner's word with a chat-recall record
(address); silence does not approve. From then on the map lives by the
change rules above. Epics express results, not activity: "Studio
registration works", not "work on registration".

Composition postconditions — before the owner's "yes":

- **Status proven by its carrier.** Every epic names the source of its
  current state, by address: code, a run, an artifact (subagent scouting is
  cheaper than being wrong). Plan files and documents are not status
  sources: they go stale first, and silently.
- **Size estimated by engineering.** Epics are commensurate in volume; the
  estimate comes from general practice, not from summing documents; the fat
  is cut, the small is merged: the bar is honest only when the units
  compare.
- **Cross-cutting work has its own owner.** A large draft-experiment
  running through several parts of the system is its own epic with its own
  home and `зависит-от` edges; tasks on top of other epics do not
  substitute for it.
- **The map's axis is named.** An early structural epic is a thin thread
  through all layers to the end of the process (tracer bullet); polish
  epics depend on it. No cross-cutting epic — name the reason.
- **Order is presented as a rule.** Dependencies → maximum knowledge per
  day of work (riskiest first) → external gates: work later, order earlier.
  Every epic carries a "why here" line.
- **Grounds are closed.** A `1use-principles` run and the product frames
  read — before composition; the trace is the names in the justification
  (copy of the plan gate in the body — edit together). Owner conflicts and
  unresolved buy-vs-build forks on the path of the early epics form a
  «Подготовка» (Preparation) epic: only what affects the nearest epics,
  closed by presentable evidence.
