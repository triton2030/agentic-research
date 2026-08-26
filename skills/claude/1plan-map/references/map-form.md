# Epic form and machine invariants

Schema tokens are literal: frontmatter keys, section headings and the status
vocabulary are validated byte-for-byte by the project instrument and read by
the owner — never translate them. File content is written in the project's
language.

## Home

```text
<map root folder>/
  <Epic name>/
    <Epic name>.md               ← folder note: name = folder name
    <Self-describing task name>.md
    _evidence/                   ← heavy proofs; worker returns
```

Nothing else lives in an epic folder; self-describing file names make the
work visible without opening anything. Task form — owner `1plan-task`.

## The epic file

The map is moved by one event: an epic closed by its criterion, with proof.
The criterion names **the evidence to be presented**, not intent; the early
indicator is a separate falsifiable signal able to refute the course before
closure.

```markdown
---
тип: эпик
описание: "<one short line for the owner — a dashboard column>"
область: <part of the project>
порядок: <number in execution order>
статус: <from the vocabulary below>
health: 🟢 | 🟠 | 🔴
запуск: true | false
критерий: "<checkable passing condition>"
ранний-индикатор: "<falsifiable signal before closure>"
зависит-от:
  - "[[<blocking epic>]]"
задач: 0                   # derived — the instrument writes it
задач-готово: 0            # derived
задачи: []                 # derived
evidence: "<link to accepted proof — mandatory at ✅>"
обновлено: <date>          # derived
---

# <epic name>

<what this is, in the owner's plain words — one paragraph>

## Принципы

- "[[<principle or pair>]] — <which fork or criterion it settles here>"

## Аппетит

<how much time or effort before revisiting — Shape Up>

## No-gos

- <what we deliberately do not do; none — say so>

> [!note]- Технические подробности
> <for agents; the owner expands at will>

## Апдейты

- <YYYY-MM-DD> · <🟢/🟠/🔴> · <one line of increment>
```

The section set is fixed in both directions. «Апдейты» is append-only;
`health` and `обновлено` derive from its last line; `задач*` derive from the
task files — an epic never carries subtask totals. Everything derived is
written by the instrument's write mode, never by hand; the one inverse
exception is the task's `эпик-снимок`, written by whoever reread the epic —
the instrument only checks freshness. The hashed "significant part" is the
epic's frontmatter minus derived fields plus the body outside «Апдейты»,
unless the project instrument names another normalization. The epic body is
at most 60 non-empty lines excluding frontmatter and «Апдейты».

## Statuses

`✅ готово · 🔨 в работе · ◽ в очереди · 🔒 заблокировано · 🛑 затык ·
⏳ отложено` — shared by epics and tasks.

- `✅` only with `evidence`; `🔒` derives from an unclosed `зависит-от` and
  flips to `◽` in the move that closes the blocker;
- `🛑` — stopped on a decision or external gate; an open interview form or
  the gate is named;
- `⏳` — deliberately deferred by the owner; it overrides derived `🔒`, is
  excluded from "left to launch" and shown as its own number.

## Frontier and "how much is left"

Statuses in `порядок` order answer it; an epic percentage is never written —
the JIT task set is open, so `100%` would lie. "Left to launch" counts
`запуск: true` only. The **frontier** is the first launch epic neither `✅`
nor `⏳`; it alone may be `🔨`, and only it may hold a `🔨` task. Frontier
`◽` → in the same move either close it with evidence or create the next JIT
task and set both to `🔨`. A queued non-frontier epic may contain only
closed tasks — accepted foundations, not permission to reorder.

## The instrument turns red when

- any form rule of this file is violated — the home, the fixed section set,
  the 60-line body, append-only «Апдейты», derived fields diverging, `✅`
  without `evidence`, the frontier rule;
- the folder note is missing or not named after the folder; «Принципы» is
  empty; the epic body does not open with a context paragraph;
- task-side invariants — owner `1plan-task`, checked by the same instrument.

Warning, not red: more than one `🔨` task in an epic — the boundaries were
cut wrong; rebuild them, it is not a working mode. The content of
`траектория`, influence lines and absence of documentation retelling are
judged at acceptance by a window that didn't write them — machines don't
catch this.
