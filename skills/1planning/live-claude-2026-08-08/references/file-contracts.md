---
description: "Active/backlog/staged schemas и task/milestone boundary."
---

# Контракты Файлов

Contents: Location Is State · Metadata · Active Task Modes · Staged Task And
Module · Backlog Contract · Task, Decision Или Milestone.

Этот reference владеет формой planning contracts. Переходы между формами и
closeout — в [`task-file-lifecycle.md`](task-file-lifecycle.md); staged worker
protocol — в [`staged-runs.md`](staged-runs.md).

## Location Is State

- `_ops/plans/` — active: contract может управлять текущим execution.
- `_ops/backlog/` — deferred: работа выбрана и сохранена, но не является current.
- `/_archive/` — contract больше не live, независимо от успеха.

Не дублируй path-state полем `Status`, если проект уже не требует его convention.
Один outcome не должен одновременно иметь live-файлы в plans и backlog.

## Metadata Is Not State Registry

`1planning` не задаёт закрытый словарь frontmatter. Local project contract или
path-scoped profile может добавить различающий `description`, identity/type и
независимые execution relationships, если у поля есть отдельная функция и
owner. Это не разрешение хранить вычисляемые копии: active/deferred/archive
выводи из path, milestones — из body, active workers — из runtime.

Execution ordering не выражай через `depends-on`: в `md-tools` это hard
semantic invalidation edge holder → source. Open frontmatter принимает custom
metadata; staged-run `kind` и `after` имеют узкий контракт ниже. `md strip`
удаляет только deprecated graph fields и не должен сносить planning metadata.

## Active Task Modes

Один task-файл = один independently closable outcome с одной приёмкой.
Используй существующую project naming convention; при её отсутствии достаточно
`task-<slug>.md`.

Общий active core:

```md
# <task title>

## Outcome
<одно устойчивое изменение состояния>

## Scope
- In:
- Out:

## Decision Basis
- <load-bearing premise> — confirmed: <exact owner/evidence pointer>
- <если нужно: accepted assumption, его owner, предел действия и reopen signal>

<ровно одна mode: Wayfinding либо Execution>

## Done
- [ ] <наблюдаемая приёмка или проверка>

## Authority / Red Lines
- <разрешённые полномочия, approval boundary и запрещённые side effects>

## Reopen When
- <named evidence/owner change, которое сделает current anchor ложным>

## Stop / Handoff
- <named blocker, approval boundary или next owner>
```

`Reopen When` — falsifier current contract: конкретный сигнал, способный
изменить Outcome, Scope, authority, active mode или material route. Фраза
«если что-то изменится» не даёт future executor-у наблюдаемого gate. Сработавший
signal запрещает продолжать stale `Next` до reconcile/mode transition/handoff.
Это minimum prediction, не whitelist: неожиданное противоречащее evidence также
reopen-ит contract через Steering Loop.

Wayfinding mode:

```md
## Wayfinding

### Ready decisions
- [ ] **<decision name>** — <точный вопрос>
  - Live branches / route divergence: <что изменит каждый остающийся ответ>
  - Discriminator: <cheapest evidence/owner, различающий branches>

### Blocked decisions
- [ ] **<decision name>** — <точный вопрос>; blocked by <prerequisite>

### Not yet specifiable
- <in-scope fog, который пока нельзя выразить точным вопросом>

### Decisions so far
- **<decision name>** — <compact gist>; evidence-state → planning consequence;
  <evidence/owner pointer>

### Next
- <один primary ready decision и bounded способ его разрешения>
```

Execution mode:

```md
## Execution

### Milestones
- [ ] <промежуточное наблюдаемое состояние одного Outcome>

### Evidence
- <чем доказать Done>

### Next
- <один bounded action текущего ясного route>
```

Execution template намеренно sparse. Полнота означает, что покрыты Outcome,
границы, load-bearing context/decisions, milestones и proof, а не что перечислен
каждый будущий шаг. Не добавляй file-by-file procedure, pseudocode, команды и
обратимые implementation choices, если их не удержал Planning Compression Gate
из [`plan-as-prompt.md`](plan-as-prompt.md). Prototype/benchmark записывай как
один evidence-producing `Next` с различаемыми branches, не как предлог заранее
расписать последующую реализацию.

Можно использовать русские эквиваленты заголовков. Active task содержит ровно
одну mode. При transition замени целый mode block; не оставляй Wayfinding рядом
с Execution и не переноси speculative decisions в milestones.

Дополнительные общие секции добавляй только если меняют исполнение:
`Applicable instructions` и exact owner anchors. `Decision Basis` — compact
index, не rationale или копия owner truth. `Next` есть в обеих mode, но означает
разное: primary decision в Wayfinding, bounded action ясного route в Execution.
Полный decision body остаётся у semantic owner-а; task не дублирует ADR,
research или prototype.

Wayfinding rules, evidence routes и transition gate — в
[`plan-as-prompt.md`](plan-as-prompt.md).

## Staged Task And Module

Large-run Task живёт в `_ops/plans/<stage>/<task-slug>/task.md`. Stage — только
semantic namespace: не создавай `stage.md`, stage status или stage acceptance.
Task использует общий active core, одну Wayfinding/Execution mode и добавляет
compact `Continuity`.
Его `Scope` явно разделяет разрешённые project read roots, write roots и exact
exceptions: Stage path сам по себе не даёт project permission. Для
staged work mode state остаётся в своём top-level block; `Continuity` хранит
только root recovery state, а не вторую decision map или execution plan.

```yaml
---
description: "<что завершает task>"
kind: task
after:
  - predecessor-task-slug
---
```

`after` optional и хранит только текущие неснятые prerequisites среди sibling
Tasks той же Stage. Удали prerequisite после его удовлетворения; не добавляй
`stage`, `parent`, `status`, `ready`, `blocked`, `completed`, `agent` или
`blocks`.

Module живёт в `modules/<module-slug>.md`, создаётся root-ом только для текущего
assignment и после выдачи не редактируется:

```yaml
---
description: "<конкретный вклад в parent Task>"
kind: module
---
```

Module не получает собственный outcome state. Полный состав brief, worker/root
contract и replanning — в [`staged-runs.md`](staged-runs.md). Его read/write
boundary должен быть подмножеством Task project boundary;
parent pointer и filesystem path выражают Stage, отдельное поле `stage` не
добавляй.

## Backlog Contract

Backlog принимает только работу, про которую в текущем контексте уже решено:
outcome нужен, делать его сейчас не следует, durable запись оправдана. Это не
inbox идей и не автономный capture побочных проблем.

Минимальная форма:

```md
# <task title>

## Outcome
<какое устойчивое состояние должно стать правдой>

## Why Later
<почему работа сознательно не active сейчас>

## Activate / Revisit When
<условие, dependency, decision point или честный revisit anchor>

## Stable Scope
- In:
- Out:

## Done
- [ ] <наблюдаемая будущая приёмка>

## Revalidate Before Start
- <owner truth, premise, scope или dependency, которые могут устареть>
```

Не добавляй milestones, порядок действий, current execution owner или evidence,
которое ещё не существует. `Existing State / Evidence` допустим только при defer
уже начатого task и хранит факты, а не будущие обещания.

При defer Wayfinding `Decisions so far` сжимаются в factual `Existing State /
Evidence`; ready/blocked questions и fog становятся revalidation anchors в
`Revalidate Before Start`. Сам Wayfinding block и его `Next` в backlog не
переезжают. В любой active mode актуальные `Reopen When` также переходят в
`Revalidate Before Start`, а не остаются управляющим active gate.

При promotion deferred route и прежние assumptions являются candidates, а не
current basis. Сначала reconstruct Outcome/Scope/Decision Basis из current owner
facts; только подтверждённые premises возвращаются в active contract.

## Task, Decision Или Milestone

Создавай sibling task, когда часть имеет самостоятельный outcome и её можно
независимо принять/закрыть, передать или остановить, не делая текущий task
формально незавершимым.

Оставляй milestone внутри task, когда это промежуточное состояние того же
outcome, которое разделяет общую приёмку и closeout. Отдельный файл, owner,
команда или blocker сам по себе ещё не требует sibling task.

Оставляй decision внутри Wayfinding, когда результат лишь выбирает route к тому
же Outcome. Precise question, отдельный research/prototype slice или human
choice не создают sibling task. Если вопрос раскрывает новый independently
closable Outcome, сначала revalidate Scope и только затем materialize sibling.
