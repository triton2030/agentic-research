---
description: "Active Wayfinding/Execution contract as a reread-and-revise steering anchor."
---

# План Как Промпт

Contents: Common Core · Anchor Check · Wayfinding · Resolution · Exit Gate ·
Execution · Autonomy.

Этот reference относится только к active task в `_ops/plans/`. Его исполняет
будущая сессия, поэтому contract передаёт current truth и authority, а не
копирует reasoning прошлой сессии. Сам файл не управляет продолжением: future
executor должен перечитать его и применить Steering Loop из `SKILL.md`.

Backlog не является execution prompt. Он сохраняет stable outcome,
defer/activation context, scope, Done и revalidation anchors; active mode
появляется только после promotion.

## Common Core

Обе active mode явно держат:

- **Outcome** — принятый destination и independently closable change of state;
- **Scope** — весь разрешённый In и явный Out;
- **Done** — наблюдаемая приёмка Outcome;
- **Decision basis** — только load-bearing premise gist с exact owner/evidence
  pointer; предложенный route не становится premise из-за записи в plan;
- **Reopen When** — named evidence/owner changes, опровергающие current anchor;
- **Red lines / authority** — запреты, approvals и allowed side effects;
- **Stop / Handoff** — named blocker, missing authority или next owner.

Task самодостаточен: task-specific owner anchors, paths и evidence нельзя
заменять скрытым chat context или ссылкой на личный runtime. Procedure остаётся
адаптивной, пока не меняет Outcome, Scope, Done, active mode, Next, reopen
signals, red lines или authority.

## Anchor Check В Точке Действия

Перед выбором нового material action перечитай exact `Outcome`, `Scope`, active
mode, mode-specific `Next`, authority/red lines, `Reopen When` и
`Stop / Handoff`, затем current owner/evidence pointers. Если current values
нельзя указать из перечитанного body, contract сейчас не является anchor.

Перед continuation собери компактный **Steering Delta**:

```text
accepted Outcome + authority source
incoming evidence → confirmed | contradicted | insufficient | conflicting
load-bearing premise, которое evidence проверяет
planning consequence → continue | accepted assumption | blocker | reframe | handoff
current mode → one Next | Stop/Handoff
```

Evidence-state и planning consequence независимы. `Insufficient` не является
автоматическим blocker-ом для обратимого non-material action; `confirmed` не
разрешает action за authority boundary. Голая пометка `plan updated` не
показывает, изменил ли evidence следующий акт.

Если premise `contradicted`/`conflicting` и consequence — `reframe`, сначала
убери stale `Next` и reconstruct current mode/route из принятого Outcome,
current owner facts и accepted evidence. Прежние milestones и decision map
после этого только candidates; не редактируй их на месте как исходную форму.
Это clean re-anchor против contextual drag, а не удаление factual completed
evidence.

Сработавший reopen signal либо расхождение с owner truth меняет следующий акт
до continuation: reconcile, mode transition, state transition или handoff.
Формально approved, но не перечитанный или уже опровергнутый plan не получает
authority только из-за своего существования.

## Wayfinding Contract

Wayfinding — planning mode для принятого destination с materially неясным
route. Его output — решения, которые делают путь видимым; не deliverables
destination, кроме bounded enabling action, без которого нельзя получить
решающее evidence.

### Decision Map

- `Ready decisions` содержит precise unblocked questions. Для каждого создай
  **Decision Fork**: какие answer branches остаются live, какой downstream
  route/commitment различает каждую branch и какой cheapest evidence/owner
  способен их различить. Если видна одна branch, назови evidence, уже закрывшее
  rival; иначе это преждевременный commitment.
- `Blocked decisions` содержит уже точные вопросы и exact prerequisite. Не
  прячь сюда fog.
- `Not yet specifiable` содержит только in-scope область, которую пока нельзя
  выразить решаемым вопросом. Это signpost, не обещание будущего ticket tree.
- `Decisions so far` — index: stable name, compact answer/gist и точный pointer
  к owner/evidence. Полный rationale живёт у semantic owner-а или в принятом
  source artifact.
- `Next` выбирает один primary ready decision и bounded способ его разрешения.
  Выбирай не самый лёгкий вопрос, а fork, который раньше остальных меняет
  high-consequence commitment или снимает больше material blockers. При равном
  route impact побеждает более дешёвый discriminating probe.

Fog test: можешь точно сформулировать вопрос сейчас — это frontier, независимо
от answerability. Не можешь — это `Not yet specifiable`. Неясный ответ не
превращает точный вопрос обратно в fog; назови evidence gap или blocker.

### Resolution Route

Выбирай минимальную fidelity, способную различить варианты:

- **research** — неизвестен внешний или локально доказуемый факт;
- **prototype** — реакция на форму/поведение надёжнее prose speculation;
- **owner decision** — tradeoff, смысл, preference или authority нельзя вывести
  из окружения;
- **enabling action** — операция нужна только чтобы открыть evidence для
  решения; её граница и side effects явны.

Локально обнаружимый факт не спрашивай у пользователя. HITL decision не решай
за человека, который является его owner-ом. Independent research slices могут
идти параллельно только при disjoint boundaries; primary Next остаётся один.

### Advance The Map

После material answer сначала присвой evidence-state и planning consequence,
затем перепиши net state, а не добавляй chronology:

1. Сохрани accepted gist и evidence/owner pointer.
2. Удали resolved question из ready/blocked.
3. Исправь, descoped или invalidated связанные decisions.
4. После снятия prerequisite перенеси decision из blocked в ready.
5. Перенеси из fog только то, что теперь стало precise question.
6. Выбери новый primary Next либо примени Exit Gate.

Out-of-scope не является fog и не graduates обратно без изменения Outcome или
Scope. Не создавай отдельный planning task для каждого decision: sibling task
появляется только у нового independently closable Outcome.

### Exit Gate

Route достаточно ясен, когда:

- не осталось material fog, скрывающего обязательное решение;
- каждый material route-changing question resolved либо сознательно descoped;
- любой оставшийся question явно non-blocking и сохранён как owner handoff;
- named material blocker оставляет task в Wayfinding blocked либо ведёт к
  Stop/Handoff, а не считается основанием для Execution;
- будущий executor может выбрать bounded action без изобретения product,
  architecture или authority decisions на ходу.

Пустая decision map сама по себе последний пункт не доказывает. Проведи
**First-Action Probe**: мысленно начни proposed Execution `Next` и выпиши каждое
material решение, которое пришлось бы принять до наблюдаемого результата.
Каждое должно иметь owner/evidence pointer в decision basis. Unowned или
unsourced route-changing choice возвращает task в Wayfinding, даже когда
`Ready`, `Blocked` и fog формально пусты.

Если downstream deliverable входит в текущий Outcome, сначала классифицируй
каждый незакрытый вопрос: material blocker запрещает transition; допустимый
non-blocking handoff должен сохраниться в `Stop / Handoff`. Только затем замени
Wayfinding block на Execution и перенеси load-bearing decision basis/pointers.
Если сам Outcome был decision/spec/map, close или handoff task по фактическому
Done.

## Execution Contract

Execution держит 2–5 наблюдаемых milestones одного Outcome, evidence для Done и
один `Next` — bounded action текущего ясного route. Milestone — промежуточное
состояние, а не вопрос, файл, layer или activity.

### Planning Compression Gate

Contract пишется для competent executor-а. Он обязан покрывать весь Outcome,
material boundaries, load-bearing context/decisions и acceptance, но не
предсказывать всю procedure. Для каждого method detail мысленно удали его и
спроси: сможет ли другой умный агент восстановить корректный обратимый ход из
Outcome, Scope, Decision Basis, red lines, evidence и `Next`? Если да — удали
detail из plan-а.

Сохраняй method detail только когда без него меняется material route или
constraint, скрывается редкий tool contract, нарушается fragile/order-dependent,
irreversible либо safety-critical операция или перестаёт быть воспроизводимым
proof. Во всех остальных случаях method имеет lowest sufficient fidelity;
file-by-file steps, pseudocode и локальные implementation choices принадлежат
executor-у.

Когда неизвестность надёжнее снимается поведением, формой или измерением,
запланируй один минимальный prototype/benchmark как evidence-producing `Next`.
Назови, какие branches различит его результат, и не расписывай downstream route
так, будто evidence уже получено. Prototype не заменяет Outcome, границы или
Done; он заменяет speculative method detail.

Перед transition и каждым новым material `Next` повтори First-Action Probe.
`Next` называет ближайшее observable state/evidence, а не только activity.
Когда несколько actions ведут к нему, предпочитай минимальный обратимый
commitment, сохраняющий live branches до discriminating evidence; delayed
consequence раннего шага учитывается до его выполнения, не после rework.

Пиши exact step order только для хрупкой, необратимой, safety-critical или
порядко-зависимой операции. В остальных случаях фиксируй что должно стать
истинным, границы и proof; путь выбирает executor.

Не оставляй рядом прежний decision tree. Нужные решения сохраняй как compact
`Decision basis` с owner/evidence pointers. Если новое evidence опровергает
route, Scope, Done или authority, останови затронутый execution и:

- верни тот же task в Wayfinding, если Outcome остаётся принят;
- replan Execution, если route остаётся достаточно ясен;
- defer/archive/handoff, если изменился lifecycle state или owner.

## Язык И Автономность

- Пиши нормальным рабочим тоном без `CRITICAL`, CAPS и generic persistence.
- Не кодируй model-family stereotypes; scope, autonomy и stop задаёт task.
- Доводи разрешённый mode до его gate: Wayfinding — до ясного route или exact
  blocker; Execution — до Done или exact Stop/Handoff.
- На resume и перед новым material slice перечитывай anchor; после material
  evidence переписывай `Next` и reopen signals как net truth.
- Перед materialization устрани противоречия между task, applicable
  instructions и project authority.
- Перед handoff проведи **Cold-Start Probe**: без chat history назови из одного
  contract-а accepted Outcome/source, current evidence-state load-bearing
  premises, mode, один Next и точный stop. Если для этого надо угадать premise
  или решение, contract ещё не готов к следующей сессии.
