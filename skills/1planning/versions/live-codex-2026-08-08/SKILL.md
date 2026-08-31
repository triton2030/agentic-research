---
name: 1planning
description: >
  Use when chosen work must remain steerable across compaction or sessions
  through `_ops/plans/**` or permitted `_ops/backlog/**`. A one-time checklist
  can drift or keep stale assumptions executing: maintain one reread-and-revise
  contract with an honest Wayfinding/Execution mode and lifecycle. Also refresh
  project-routed `STATUS.md`. Skip in Codex Plan mode.
---

# Планирование

## Codex Native Plan Mode — Veto

До planning-owned read или write проверь collaboration mode. Если
developer/system context явно говорит, что активен `Plan`, не создавай, не
обновляй, не перемещай и не архивируй `_ops/plans/**` или `_ops/backlog/**`.
Используй только native planning surface текущей сессии (`update_plan`;
`request_user_input`, когда доступен и нужен), затем останови этот skill route.

Не определяй режим по одному наличию `update_plan`: без явного active `Plan`
signal действует обычный Admission ниже.

## Почему Статичный План Не Управляет Работой

Естественный default — один раз разложить destination на правдоподобные шаги и
считать planning завершённым. Planning prose дешевле working code или
prototype, поэтому подробность легко становится ложным proxy прогресса: модель
заранее расписывает обратимые implementation choices и получает ощущение
полноты до evidence. Но непрочитанный файл не участвует в текущем выборе, а
подробный stale checklist превращает раннее предположение в серию всё более
дорогих действий.

Поэтому planning здесь — не документ и не обещание следовать прошлому решению.
Это **перечитываемый и ревизуемый steering contract**: перед material ходом он
возвращает Outcome, authority и текущую развилку в контекст; после нового
evidence либо подтверждает следующий ход, либо сам меняет mode/route/state.

Голая команда «не забывай план» этого не обеспечивает. Простое «перечитай» без
falsifier тоже опасно: оно может лишь усилить stale anchor. Наблюдаемый proxy —
может ли агент перед действием указать current `Outcome`, active mode, один
`Next` и named `Reopen When` из перечитанного contract, а при сработавшем signal
изменить следующий акт. Если нет, plan сейчас не управляет работой.

```text
accepted destination + current owner facts
→ evidence-state → planning consequence
→ Wayfinding Decision Fork | Execution First-Action Probe
→ one bounded Next | Stop/Handoff
→ net-state rewrite + cold-start check
```

## Результат И Мера Успеха

Одна выбранная работа имеет один live durable contract. Active contract либо
разрешает material decisions к принятому destination, либо ведёт уже ясный
route; Backlog сохраняет выбранную deferred работу без права управлять current
execution.

Мера успеха — не полнота плана, а длина корректного автономного участка: каждый
material slice начинается из current anchor, не требует молча изобрести
Outcome/Scope/authority и останавливается либо переписывает contract при
названном invalidating evidence.

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
candidate, пока named owner/evidence не сделали его premise; не материализуй
сикофантный «план выбранного решения» из самой формулировки запроса.

Прокси для первого условия. Если работа меняет продукт, «выбран владельцем»
означает подтверждённую цель-сцену в Product Frame (`$1product-shaping`), а не
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

Применяй loop при create до первого execution action, при resume после
compaction/session, перед delegation или новым material slice и сразу после
evidence, способного изменить route:

1. **Reread anchor.** Восстанови из exact contract и owner pointers `Outcome`,
   `Scope`, `Done`, Decision Basis, mode, один `Next`, authority/red lines,
   `Reopen When` и `Stop / Handoff`.
2. **Classify delta.** Отдели evidence-state (`confirmed`, `contradicted`,
   `insufficient`, `conflicting`) от planning consequence (`continue`, accepted
   assumption, `blocker`, `reframe`, `handoff`). При reframe сначала reconstruct
   route из current owner facts; не патчь stale `Next`/milestones на месте.
3. **Pass the mode gate.** Wayfinding выбирает `Next` через Decision Fork;
   Execution доказывает readiness через First-Action Probe. Голые labels и
   пустые списки gate не проходят.
4. **Act from one current Next.** Не выполняй будущую ветку только потому, что
   она уже записана ниже.
5. **Close the loop.** Перепиши net truth без activity log и проверь, что
   contract проходит cold-start без скрытого chat context.

Формы `Steering Delta`, Decision Fork, clean re-anchor, First-Action и
Cold-Start probes принадлежат
[`references/plan-as-prompt.md`](references/plan-as-prompt.md). **Открой этот
reference перед create/resume, выбором нового material `Next` и mode
transition**: main body только ставит gate, reference содержит operator.

Loop не требует self-report о внимательности. Его evidence — другой следующий
акт: continue, revise, mode transition, state transition либо stop.

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
- `Reopen When` задаёт falsifier current anchor, но не образует третью mode или
  отдельный risk register.

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
зависимости проходят границы. Его `execution frontier` — не `frontier decision`
из Wayfinding: первый про ближайший наблюдаемый результат работы, второй про
вопрос, ответ на который меняет route.

Перед новым material `Next` First-Action Probe должен показать, что executor не
изобретает product/architecture/authority decision. При равном outcome выбирай
минимальный обратимый commitment, сохраняющий live branches до evidence. Не
сохраняй Wayfinding tree рядом с milestones; новое material uncertainty
останавливает затронутый execution и возвращает тот же task в Wayfinding.

## Контрастивные Развилки

> **Premature execution.** Destination «перенести auth» принят, но выбор между
> двумя несовместимыми ownership models меняет migration route. Milestone
> «реализовать новую schema» выглядит как план, но прячет material decision.
> First-Action Probe показывает решение без owner/evidence; Wayfinding строит
> Decision Fork, и только discriminator может породить Execution milestones.

> **Static-anchor theatre.** Execution contract говорит использовать provider
> A, а перечитанный owner теперь требует B. Добавить note и продолжить A —
> формальное обновление без steering. `Contradicted → reframe` удаляет stale
> Next/milestones и reconstruct route из current owner facts; A-route остаётся
> только historical candidate.

> **Easy frontier.** UI-copy закрывается за минуту, а нерешённый storage owner
> изменит API, migration и conflict policy. Выбор UI как `Next` двигает
> checklist, но не route. Decision Fork ставит owner-вопрос первым; дешёвый
> вопрос выигрывает только при равном downstream impact.

> **Planning theatre.** До первого prototype агент расписал 40 file-level
> действий для трёх ещё не проверенных routes. Planning Compression Gate
> оставляет Outcome, границы, competing premises и один discriminating
> prototype; downstream method detail появляется только из его evidence.

> **Near miss.** Небольшой fix помещается в текущую сессию, route ясен и
> durable recovery не нужен. Даже хороший список шагов остаётся in-chat
> decomposition: новый `_ops/plans/**` contract не создаётся.

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
  Done, Decision Basis, Next, Reopen When, red lines, evidence и Stop/Handoff
  не зависят от скрытого chat context.
- Project-routed `STATUS.md` кратко следует за live state и не получает
  собственных decisions, milestones или evidence.
- Plan-invalidating evidence вызывает revalidation и mode/state transition, а
  не механическое продолжение старого плана.
- Существование, давность или формальное approval contract не доказывают, что
  anchor был перечитан и остаётся current.
- Когда пара Frame/Principles существует, привязка задач принадлежит правилу
  «Работа по паре» в `$1product-shaping`: contract называет приближаемую сцену и
  применяемые `P-*`. Здесь только pointer; смысл правила не пересказывай.

Exact-first discovery и duplicate classification — в
[`references/discovery-map.md`](references/discovery-map.md); folder/archive
placement — в
[`references/archive-and-folders.md`](references/archive-and-folders.md).

## Материализация И Lifecycle

После Veto/Admission найди один live contract exact-first; archive используй
только как evidence. Выбери actual lifecycle state, для active — одну mode, а
flat/staged shape реши независимо. Материализуй только выбранную schema и сразу
запусти Steering Loop; дальнейшие переходы принадлежат lifecycle contract.

**Перед write/create/mode transition открой** schemas и task/milestone boundary
из
[`references/file-contracts.md`](references/file-contracts.md); create,
defer/promote, mode transitions, refresh `STATUS.md` и closeout —
[`references/task-file-lifecycle.md`](references/task-file-lifecycle.md).

## Готово Когда

- один live contract соответствует принятому destination и фактическому state;
- deliverable с отложенным составом несёт перечисление из источника и
  Done-строку, падающую при непокрытом требовании;
- active task содержит ровно одну честную mode;
- Wayfinding различает ready, blocked и not-yet-specifiable, а Next указывает
  один Decision Fork с различающим evidence;
- Execution прошёл First-Action Probe, не скрывает material unresolved
  decisions под milestones и держит один bounded Next;
- method detail прошёл Planning Compression Gate: сохранено только то, без чего
  меняется material route, constraint, fragile order или proof;
- material evidence имеет отдельные evidence-state и planning consequence;
- `Reopen When` называет evidence, способное опровергнуть current anchor, а
  сработавший signal меняет следующий акт до continuation и не наследует stale
  route shape;
- переход mode/state удалил obsolete управляющую форму и сохранил только
  current truth;
- staged shape, backlog, archive и STATUS не стали вторыми owners;
- Cold-Start Probe доказывает, что следующий executor может продолжить либо
  остановиться по самому contract без скрытого chat context.

## Остановка

Остановись после проверенного planning action или на named blocker/authority
boundary. Не создавай новую surface, sibling task или execution tree только
потому, что впереди остаётся fog.
