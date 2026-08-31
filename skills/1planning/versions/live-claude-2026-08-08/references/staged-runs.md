---
description: "Opt-in staged-run contract для context recovery, bounded Modules и root-owned replanning."
---

# Staged Runs

Contents: Gate · Shape И Authority · Stage Binding · Task Continuity · Module
Brief · Worker Contract · Root Cold Start · Replanning.

Открывай только после Large-run Gate. Это не новый skill и не обязательная форма
durable task.

## Gate

Включай staged run, если истинно хотя бы одно:

- работа должна точно восстановиться после compaction или session boundary;
- execution имеет несколько независимых context/write slices, которые можно
  выдать параллельным исполнителям без общего corpus context.

Не включай его только из-за длины одного документа, одного audit, обычной
локальной правки, большого числа строк или желания заранее разложить будущее.
Если для такого случая независимо доказана потребность в durable state,
используй flat task; иначе не создавай planning-файл.

## Shape И Authority

```text
_ops/plans/
└── <stage>/
    ├── <task-slug>/
    │   ├── task.md
    │   ├── modules/          # lazy; только active briefs
    │   └── _archive/         # inactive Module briefs
    └── _archive/             # inactive Task directories
```

Stage — semantic planning namespace без файла, status и acceptance. Task —
единственный mutable owner outcome и execution truth. Module — root-authored
immutable assignment projection, не task и не execution log. Вложенных Modules
нет.

Staged shape ортогонален active mode: Task содержит ровно один top-level
`Wayfinding` или `Execution` block по
[`file-contracts.md`](file-contracts.md). Stage/Modules не образуют третью mode.

Exact Task/Module frontmatter and forbidden computed fields are owned by
[`file-contracts.md`](file-contracts.md). Path shows active/archive state;
runtime shows the executor.

## Stage Binding

До первого staged assignment root получает из исходного user/caller assignment
однозначные project read/write roots и фиксирует один exact Stage path: берёт
явно назначенный либо один раз именует новый из принятого scope. Перед созданием
он проверяет exact target path на conflicting live work и объявляет binding;
неясная или уже занятая Stage даёт handoff. После первого выбранного или
созданного Task root-сессия bound к Stage и не переключает её поиском.

Stage path задаёт boundary active staged planning, но не concurrency lock и не
permission на одноимённую project folder. Task `Scope` отдельно владеет project
execution boundary, а user/caller — disjoint allocation между orchestrators.
Если assignment пересекается с известным live write scope другого orchestrator,
остановись с handoff вместо самоназначения.

Binding даёт alignment и context hygiene, не hard filesystem isolation.
Случайно увиденное path metadata не назначает sibling Stage current context;
нулевая visibility требует отдельного cwd/worktree/tool sandbox от caller-а.

Binding объявляется в root assignment/handoff и выводится из filesystem path;
не дублируй Stage полем или строкой в Task/Continuity. Module наследует её своим
path и parent pointer.

После binding planning-file body reads и Task/Module writes остаются внутри Stage.
Module выдаётся только при `Module boundary ⊆ Task project boundary`;
cross-stage execution need или выход за project boundary даёт blocker/handoff.
Lifecycle transfer в backlog/archive меняет authority конкретного Task, но
binding снимает только окончание исходного assignment или явный handoff.

## Task Continuity

В `task.md` сохраняй common active core, ровно одну mode, а также компактный
`## Continuity`:

- принятый root-ом module evidence, ещё не отражённый в semantic owner-ах;
- active module assignments и task blockers, если есть;
- следующий bounded root recovery/assignment action.

Continuity — не журнал. Root переписывает её до минимального current state после
каждого принятого return и до следующего assignment/handoff. Chat, Module
returns и archive не становятся вторыми owners истины.

Decision map живёт только в `Wayfinding`, milestones/evidence — только в
`Execution`. Mode-specific `Next` остаётся в mode block, `Reopen When` — в
common task core. Continuity может указывать, какой Module двигает `Next`, но
не копирует mode state или reopen signals.

## Module Brief

Каждый brief содержит только:

1. parent Task pointer, active mode и конкретный вклад в один ready decision
   либо execution slice;
2. exact owner anchors: paths и необходимые headings/lines;
3. read boundary и write boundary — более узкую immutable projection Task
   project boundary;
4. ожидаемый return;
5. проверки, которые выполнит root;
6. условия `blocked` и `split-proposal`.

Не добавляй Module собственные Outcome, Milestones, Done, current frontier,
task blockers или next execution owner. Если assignment надо изменить после
выдачи, архивируй brief неизменным и создай новый.

## Worker Contract

Worker читает только project instructions, свой Module и exact owner anchors.
Он не читает parent Task, chat, sibling/archived Modules, backlog или весь corpus;
не открывает sibling Stages, не изменяет Module и parent Task, не создаёт
grandchildren. Module path и parent pointer должны принадлежать одной bound
Stage; mismatch или необходимость выйти за Module read/write boundary дают
`blocked`, а не самостоятельное расширение scope.

Return:

```text
status: success | blocked | split-proposal
changes: <что изменено или none>
evidence: <проверки и адресуемые результаты>
gaps: <непокрытое, blocker или предлагаемая граница>
```

`split-proposal` только предлагает новый bounded slice или independently
closable outcome. Worker не создаёт planning-файлы сам.

## Root Cold Start

Предпочтительный inventory:

```bash
md orient _ops/plans/<stage> \
  --frontmatter-field kind \
  --frontmatter-field after \
  --json
```

Если runtime не предоставляет `md`, используй эквивалентный exact filesystem
inventory Stage с `kind`/`after` metadata и без preload task bodies.

Exact Stage берётся из binding, не обнаруживается глобальным поиском. Map
инвентаризирует её live planning tree; bodies всех sibling Tasks не preload.
Затем root читает один выбранный `task.md`, только его active `modules/*.md` и
указанные exact owner anchors, применяет Steering Loop из `SKILL.md` и лишь
после этого выдаёт новый assignment. Не preload archive/backlog или sibling
Stages. Recovery budget: один Stage map, один Task, active Modules и exact
anchors.

До assignment root обязан получить из contract-а проходящий Cold-Start Probe и
собрать current Steering Delta. Для Execution assignment дополнительно проведи
First-Action Probe внутри Module boundary: worker не должен изобретать material
decision, которое Task не разрешил.

Root один:

1. принимает или отклоняет worker evidence;
2. проверяет `Module boundary ⊆ Task boundary` до assignment;
3. обновляет Wayfinding/Execution current truth и compact Task Continuity;
4. выполняет mode transition, если evidence пересёк его Gate;
5. архивирует использованный Module brief;
6. материализует новый Module, sibling Task или Backlog только по фактической
   новой границе.

## Replanning

- тот же bounded context → продолжить Module;
- новый source/write slice того же Outcome и mode → sibling Module;
- route стал достаточно ясен → root заменяет Wayfinding на Execution до нового
  assignment;
- material route снова неясен → root останавливает затронутые execution Modules
  и заменяет Execution на Wayfinding;
- independently closable Outcome → sibling Task;
- принято делать позже → Backlog;
- сработал `Reopen When` либо опровергнуты Outcome, Scope или Done → остановить
  затронутые Modules, классифицировать evidence-state/planning consequence и
  clean re-anchor Task до продолжения.

Sibling Task допустим только внутри той же bound Stage и принятого project
boundary. Новый outcome для другой Stage или project root возвращай caller-у;
не переходи туда из текущего run.

При расхождении decision map, milestones или owner truth не компенсируй его
чтением всего corpus. Исправь Task mode/Module contract или metadata projection,
затем повтори cold start.
