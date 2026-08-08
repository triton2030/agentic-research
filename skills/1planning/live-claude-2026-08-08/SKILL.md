---
name: 1planning
description: >
  Use when chosen work must remain steerable across compaction or sessions
  through `_ops/plans/**` or permitted `_ops/backlog/**`. A one-time checklist
  can drift or keep stale assumptions executing: maintain one reread-and-revise
  contract with an honest Wayfinding/Execution mode and lifecycle. Also refresh
  project-routed `STATUS.md`. Skip in Claude Code Plan mode.
---

# Планирование

## Claude Code Native Plan Mode — Veto

До planning-owned read или write проверь permission mode. Если system/runtime
context явно говорит, что активен `plan`, не создавай, не обновляй, не перемещай
и не архивируй `_ops/plans/**` или `_ops/backlog/**`. Используй только native
Plan Mode текущей сессии: read/explore, предложить один план для approval и не
менять source files; затем останови этот skill route.

Не определяй режим по одному наличию `EnterPlanMode` или read-only tools: без
явного active `plan` signal действует обычный Admission ниже.

## Почему Статичный План Не Управляет Работой

Естественный default — один раз разложить destination на правдоподобные шаги и
локально продолжать самый доступный. Planning prose дешевле working code или
prototype, поэтому подробность легко становится ложным proxy прогресса: модель
заранее расписывает обратимые choices и получает ощущение полноты до evidence.
После нового evidence она патчит этот checklist вместо пересборки route.

Planning здесь — перечитываемый и ревизуемый steering contract. Его
наблюдаемый механизм:

```text
accepted destination + current owner facts
→ evidence-state → planning consequence
→ Wayfinding Decision Fork | Execution First-Action Probe
→ one bounded Next | Stop/Handoff
→ net-state rewrite + cold-start check
```

## Результат

Одна выбранная работа имеет один честный durable contract. Active contract
либо находит путь к принятому destination, либо исполняет уже достаточно ясный
путь. Backlog сохраняет выбранную deferred работу без права управлять текущим
execution.

Planning различает две взаимоисключающие active mode:

- **Wayfinding** — Outcome/destination принят, но material route ещё не ясен;
  task разрешает решения, а не изображает преждевременный execution plan.
- **Execution** — material route достаточно ясен; task управляет deliverable
  через milestones, evidence и stop/handoff.

Один task может переходить между mode без нового owner-файла. Staged run —
форма recovery/delegation, а не третья mode.

Мера успеха — не полнота плана, а корректный следующий material act и длина
автономного участка до named reopen/stop.

## Admission

Durable planning допустим только когда:

- Outcome/destination уже выбран владельцем или применимым owner-контекстом;
- состояние нужно сохранить между material slices, compaction или sessions;
- work state является active сейчас либо явно deferred на потом.

Не требуй заранее выбранного подхода: его отсутствие может быть самим предметом
Wayfinding. Но один туман вокруг возможной работы без принятого destination не
является planning state.

Отдели destination от предложенного способа: перепиши Outcome без имени
implementation mechanism. Если после удаления способа исчезает и проверяемое
изменение состояния, destination ещё не принят. User-proposed route остаётся
candidate, пока named owner/evidence не сделали его premise.

Прокси для первого условия. Если работа меняет продукт, «выбран владельцем»
означает подтверждённую цель-сцену в Product Frame (`1product-shaping`), а не
собственную реконструкцию destination из формулировки задачи. Без этого проверки
нет вовсе: агентский дефолт и принятый Outcome выглядят в тексте плана
одинаково, а расходятся только на приёмке. Frame отсутствует — либо пройди
минимальную сверку, либо запиши destination явным допущением с owner-ом. Для
работы внутри существующего scope (починка, уборка, техническая миграция) Frame
читается, если он есть, и его отсутствие блокером не является.

Выйди без planning-файла, если нужна только in-chat decomposition, работа ещё
не выбрана, сигнал является сырой идеей/побочной проблемой либо меняется
project-level GOAL/README. Backlog требует и явного решения `нужно позже`, и
того, чтобы effective project instructions разрешали `_ops/backlog/**` surface.
Если project GOAL/instructions исключают backlog, не материализуй его даже при
принятом defer.

Compact `STATUS.md` принадлежит этому skill только при явном project route; это
projection live planning state, не второй task owner.

## Steering Loop

Применяй loop при create до первого execution action, при resume, перед
delegation/новым material slice и сразу после route-changing evidence:

1. **Reread anchor.** Восстанови `Outcome`, `Scope`, `Done`, Decision Basis,
   mode, один `Next`, authority/red lines, `Reopen When` и `Stop / Handoff`.
2. **Classify delta.** Отдели evidence-state (`confirmed`, `contradicted`,
   `insufficient`, `conflicting`) от planning consequence (`continue`, accepted
   assumption, `blocker`, `reframe`, `handoff`). При reframe reconstruct route
   из current owner facts; не патчь stale `Next`/milestones на месте.
3. **Pass the mode gate.** Wayfinding выбирает `Next` через Decision Fork;
   Execution доказывает readiness через First-Action Probe.
4. **Act from one current Next.** Не выполняй будущую ветку только потому, что
   она записана ниже.
5. **Close the loop.** Перепиши net truth без activity log и проверь cold-start
   без скрытого chat context.

Формы Steering Delta, Decision Fork, clean re-anchor, First-Action и Cold-Start
probes принадлежат
[`references/plan-as-prompt.md`](references/plan-as-prompt.md). **Открой этот
reference перед create/resume, выбором нового material `Next` и mode
transition**: main body только ставит gate, reference содержит operator.

## State Model

```text
discussion
  └─ accepted destination + persistent need
       ├─ active Wayfinding ⇄ active Execution
       └─ deferred Backlog

active Wayfinding | active Execution | Backlog
  └─ inactive → Archive
```

- Path задаёт lifecycle state: `_ops/plans/` = active, `_ops/backlog/` =
  deferred, `/_archive/` = inactive.
- Active body содержит ровно одну mode: `Wayfinding` либо `Execution`.
- Mode transition переписывает тот же contract; не создаёт sibling task и не
  оставляет прежнюю mode вторым owner-ом.
- Defer/promote перемещает и reconciles один contract; stale mode не переносит
  право управлять execution через backlog.

Schemas и task/milestone boundary принадлежат
[`references/file-contracts.md`](references/file-contracts.md); lifecycle
transitions —
[`references/task-file-lifecycle.md`](references/task-file-lifecycle.md).

## Wayfinding Mode

Wayfinding нужен, когда destination уже фиксирует scope, но путь зависит от
material decisions, которые не помещаются в один transient conversation slice.

Он держит одну mutable decision map:

- **Ready decisions** — точные, unblocked вопросы, ответы на которые меняют
  route;
- **Blocked decisions** — точные вопросы с названным prerequisite;
- **Not yet specifiable** — in-scope fog, который пока нельзя честно выразить
  как точный вопрос;
- **Decisions so far** — compact gist и evidence/owner pointer, не копия
  полного source;
- **Next** — один primary ready decision.

Точный вопрос — decision даже без ответа; невыразимая пока область — fog. Для
каждого material ready decision reference требует live answer branches,
downstream route divergence и discriminating evidence/owner. `Next` выбирается
по раннему high-consequence divergence и снятию blockers, не по лёгкости
вопроса. Не создавай speculative milestones из fog.

Unknown fact разрешается bounded research, наблюдаемая форма — prototype,
разовый tradeoff/authority — owner decision, evidence-only операция — enabling
action. Повторяющийся класс owner-вопросов означает gap Product Frame, а не
поток локальных эскалаций.

После material answer обнови evidence-state → planning consequence, перепиши
net map и выбери новый fork. Wayfinding переходит в Execution только после Exit
Gate + First-Action Probe из `plan-as-prompt.md`; named material blocker оставляет
task в Wayfinding либо ведёт к Stop/Handoff.

## Execution Mode

Execution начинается только когда route достаточно ясен для bounded action.
Держи 2–5 наблюдаемых milestones одного independently closable Outcome,
evidence и один bounded `Next`, называющий ближайшее observable state/proof.
Обратимую procedure оставляй исполнителю.

План пишется для другого умного агента: он должен восстановить что делаем,
зачем, в каких границах и на каком evidence, а не получить симуляцию каждого
будущего движения. Перед сохранением method detail примени Planning Compression
Gate из [`plan-as-prompt.md`](references/plan-as-prompt.md); completeness здесь
означает coverage material outcome/границ/решений/proof, не exhaustive procedure.

Milestones порождает разбивка, а не жанр. Без неё естественный
набор — «спроектировать, реализовать, проверить»: хронология, в которой границы
milestone не совпадают с зависимостями, и первый же блокер вскрывается внутри
уже начатого этапа. Назови ось разреза сам и покажи, по какой
зависимости проходят границы. Его «ближайший проверяемый фронтир» — не
`frontier decision` из Wayfinding: первый про ближайший наблюдаемый результат
работы, второй про вопрос, ответ на который меняет route.

Перед новым material `Next` First-Action Probe должен показать, что executor не
изобретает product/architecture/authority decision. При равном outcome выбирай
минимальный обратимый commitment, сохраняющий live branches до evidence. Не
сохраняй Wayfinding tree рядом с milestones; новое material uncertainty
останавливает затронутый execution и возвращает тот же task в Wayfinding.

## Контрастивные Развилки

> **Premature execution.** Destination принят, но первый implementation action
> требует выбрать ownership model. Пустая decision map выглядит готовой;
> First-Action Probe возвращает unsourced choice в Wayfinding Decision Fork.

> **Static-anchor theatre.** Owner сменил provider A на B. Note поверх старых
> milestones не является replan: `contradicted → reframe` удаляет stale route и
> reconstruct-ит mode из current owner facts.

> **Easy frontier.** UI-copy закрывается быстро, а storage owner меняет API,
> migration и conflicts. Decision Fork ставит owner-вопрос первым; дешёвый
> вопрос выигрывает только при равном downstream impact.

> **Planning theatre.** До первого prototype агент расписал 40 file-level
> действий для трёх ещё не проверенных routes. Planning Compression Gate
> оставляет Outcome, границы, competing premises и один discriminating
> prototype; downstream method detail появляется только из его evidence.

## Shape И Authority

- Flat active task — default для одного owner/context.
- Staged run — opt-in, когда нужен точный recovery после session boundary или
  несколько независимых context/write slices. Он может нести Wayfinding или
  Execution и не меняет task Outcome.
- Task — единственный mutable owner. Root-authored Module — immutable bounded
  assignment projection; worker не меняет planning state.
- Sibling task появляется только для independently closable Outcome, не из-за
  размера, отдельного вопроса, файла, worker-а или blocker-а.

Large-run Gate, Stage binding и worker protocol принадлежат
[`references/staged-runs.md`](references/staged-runs.md).

## Общие Инварианты

- **IMPORTANT — отложенный состав требует акта вывода.** Когда contract, canon
  или spec владеют составом deliverable, plan их не копирует — но обязан
  назвать перечисление из источника **первым актом** и держать Done-строку,
  падающую при непокрытом требовании. Названный destination актом вывода не
  является: между «довести X» и «перечислить, из чего X состоит» помещается вся
  потеря. Список внутри задания всегда побеждает ссылку на источник, поэтому
  чужой список — вход для сверки, а не замена перечислению. Пропущенное
  требование не сообщает о себе ни экраном, ни тестом, ни зелёной сборкой: оно
  видно только строкой покрытия «требуется, не построено». Сверка с приёмочной
  матрицей источника, запланированная в конец, стоит переделки deliverable
  вместо правки списка.
- Один Outcome имеет один live contract: plans либо backlog, не оба.
- Current truth важнее chronology: обновляй material state, не activity log.
- Decision map является index: не дублируй ADR, owner canon, research body или
  prototype; храни gist и точный pointer.
- Полнота contract-а означает coverage Outcome, Scope, load-bearing context,
  material decisions и proof; обратимую procedure экстраполирует executor.
- Backlog — stable kernel, не queue исполнения и не замороженный active plan.
- Active contract самодостаточен для будущей сессии: Outcome, Scope, mode,
  Done, Decision Basis, Next, Reopen When, red lines, evidence и Stop/Handoff не
  зависят от скрытого chat context.
- Project-routed `STATUS.md` кратко следует за live state и не получает
  собственных decisions, milestones или evidence.
- Plan-invalidating evidence вызывает revalidation и mode/state transition, а
  не механическое продолжение старого плана.
- Существование, давность или формальное approval contract не доказывают, что
  anchor был перечитан и остаётся current.
- Когда пара Frame/Principles существует, привязка задач принадлежит правилу
  «Работа по паре» в `1product-shaping`: contract называет приближаемую сцену и
  применяемые `P-*`. Здесь только pointer; смысл правила не пересказывай.

Exact-first discovery и duplicate classification — в
[`references/discovery-map.md`](references/discovery-map.md); folder/archive
placement — в
[`references/archive-and-folders.md`](references/archive-and-folders.md).

## Default Path

1. Примени native-mode Veto и Admission.
2. Найди один live contract exact-first; archive используй только как evidence.
3. Выбери lifecycle state, а для active — Wayfinding или Execution; отдельно
   реши flat/staged shape.
4. Перед create/resume/Next/mode transition открой `plan-as-prompt.md`; перед
   write — `file-contracts.md` и `task-file-lifecycle.md`. Материализуй только
   schema выбранного state/mode.
5. После material evidence запиши evidence-state → planning consequence,
   перепиши current truth и выполни нужный transition.
6. Refresh project-routed `STATUS.md`, если применимо, и верни current owner,
   Next либо exact Stop/Handoff.

## Готово Когда

- один live contract соответствует принятому destination и фактическому state;
- deliverable с отложенным составом несёт перечисление из источника и
  Done-строку, падающую при непокрытом требовании;
- active task содержит ровно одну честную mode;
- Wayfinding различает ready, blocked и not-yet-specifiable, а Next указывает
  один Decision Fork с различающим evidence;
- Execution прошёл First-Action Probe и не скрывает material unresolved
  decisions под milestones;
- method detail прошёл Planning Compression Gate: сохранено только то, без чего
  меняется material route, constraint, fragile order или proof;
- material evidence имеет отдельные evidence-state и planning consequence;
- сработавший reopen signal не наследует stale route shape;
- переход mode/state удалил obsolete управляющую форму и сохранил только
  current truth;
- staged shape, backlog, archive и STATUS не стали вторыми owners;
- Cold-Start Probe доказывает, что следующий executor может продолжить либо
  остановиться по самому contract без скрытого chat context.

## Остановка

Остановись после проверенного planning action или на named blocker/authority
boundary. Не создавай новую surface, sibling task или execution tree только
потому, что впереди остаётся fog.
