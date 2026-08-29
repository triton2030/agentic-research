# Epic form and machine invariants

Schema tokens are literal: frontmatter keys, section headings, and status
vocabulary are validated byte-for-byte and read by the owner. File content is
written in the project's language.

## Home

```text
<map root folder>/
  <Epic name>/
    <Epic name>.md
    <Self-describing task name>.md
    _evidence/
```

The epic file is the folder note and shares its name with the folder. Nothing
else lives here; task form belongs to `1plan-task`.

## Epic file

```markdown
---
тип: эпик
описание: "<one short owner-facing line>"
область: <part of the project>
порядок: <number in execution order>
статус: <from the vocabulary below>
health: 🟢 | 🟠 | 🔴
запуск: true | false
критерий: "<evidence to present for closure>"
ранний-индикатор: "<falsifiable signal before closure>"
зависит-от:
  - "[[<blocking epic>]]"
задач: 0
задач-готово: 0
задачи: []
evidence: "<accepted carrier proof; mandatory at ✅>"
обновлено: <date>
---

# <Epic name>

<what this is, in the owner's plain words — one paragraph>

## Принципы

- "[[<principle or pair>]] — <which fork or criterion it settles here>"

## Аппетит

<time or effort before revisiting>

## No-gos

- <what is deliberately excluded; none — say so>

> [!note]- Технические подробности
> <agent-facing detail>

## Апдейты

- <YYYY-MM-DD> · <🟢/🟠/🔴> · <one line of increment>
```

Composition owns `описание`, `область`, `порядок`, `запуск`, `критерий`,
`ранний-индикатор`, `зависит-от`, «Принципы», «Аппетит», and «No-gos».
State events own `статус`, `health`, `evidence`, and append-only «Апдейты»;
they never alter composition.

The section set is fixed in both directions. `health` and `обновлено` derive
from the last update; `задач*` derive from task files and are written only by
the instrument. The task's inverse `эпик-снимок` is written by whoever reread
the epic and checked by the instrument. Unless the project instrument names a
different normalization, significant content is frontmatter minus derived
fields plus the body outside «Апдейты». The criterion names closure evidence;
the early indicator is a separate signal able to refute the course before
closure. The epic body is at most 60 non-empty lines outside frontmatter and
updates.

## Status and frontier

`✅ готово · 🔨 в работе · ◽ в очереди · 🔒 заблокировано · 🛑 затык ·
⏳ отложено` is shared by epics and tasks.

- `✅` requires accepted `evidence`; `🔒` derives from an open dependency and
  becomes `◽` when the blocker closes.
- `🛑` names the decision or external gate; `⏳` records the owner's reason,
  overrides derived `🔒`, and does not count as left to launch.
- Statuses in `порядок` answer how much is left; epic percentage is forbidden
  because the JIT task denominator is open, and left to launch counts only
  `запуск: true`.
- The frontier is the first launch epic neither `✅` nor `⏳`; it alone may be
  `🔨`, and only it may contain a `🔨` task.
- Frontier `◽` without a live task is a visible admission need. `1planning`
  decides whether and how to cut the task; `1plan-task` writes it; only then a
  map state event sets the task and epic to `🔨`.
- A queued non-frontier epic may contain only closed tasks accepted as
  foundations; their presence never permits reorder.

## Instrument

The instrument rejects a broken home or folder note, wrong section set,
overlong body, changed append-only updates, divergent derived fields, `✅`
without evidence, an empty «Принципы», missing context paragraph, or a broken
frontier invariant; it also checks task-side invariants owned by `1plan-task`.

More than one `🔨` task in an epic is a warning that task boundaries need
replanning, not a working mode. Trajectory, principle influence, and absence
of documentation retelling are accepted by a window that did not write them.
