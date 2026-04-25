---
name: task-contract
description: >
  Own task files inside the active `_ops/PROJECT-PLAN.md` phase folder.
  Use when a task needs a file-backed execution contract, active task
  context, criteria, scope, status movement, implementation closeout, or
  verification evidence. Trigger when the user starts, discusses, scopes,
  edits, implements, reviews, checks, closes, or changes status on a
  non-trivial task; asks for "criteria", "acceptance criteria", "scope",
  "что считается готовым", "зафиксируй задачу", "закрой задачу", or
  "проверь по критериям"; or when real text/code/artifact work begins
  inside an active phase. Create, update, and close
  `_ops/plans/phase-NN-{slug}/task-MM-{slug}.md` with Цель, Подшаги,
  and Критерии приёмки. Route unresolved architecture to
  `instruction-layer`. Route unbootstrapped `_ops`, unsynced phase folders,
  missing plan anchors, and new preference signals to `project-strategy`.
  Do not trigger for trivial factual questions or tiny mechanical edits.
---

# Task Planner

Объяви в начале короткой строкой:

- Task (default): *«Использую `task-contract` — открою/обновлю файл задачи под активный Step»*.
- Strategy-trace: *«Использую `task-contract` в режиме `strategy-trace` — проверю alignment артефакта»*.
- Pulse-check: *«Использую `task-contract` в режиме `pulse-check` — проверю память диалога»*.

Отвечай и пиши артефакты по-русски.

> **Stop.** Этот файл — маршрут и gate-список. Полный lifecycle (locate → discover → draft → adversarial → write), форма секций task-файла, failure modes, discovery map — **в ref-файлах**. Write task-файла без открытия `task-file-lifecycle.md` = нарушение контракта.

## Роль

Владелец файла задачи `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`. Для каждого активного Step из `_ops/PROJECT-PLAN.md` создаёт, поддерживает и закрывает один файл. Три секции — Цель / Подшаги / Критерии приёмки — пишутся этим скиллом целиком. `project-strategy` владеет планом и папками фаз, но **не** содержимым task-файлов.

Lifecycle двухпроходный: **до работы** открыть/создать task-файл и зафиксировать контракт; **после выполнения** снова вызвать `task-contract`, открыть тот же файл, отметить выполненные Подшаги / Must / Verification, дописать фактический evidence внутри существующих секций и закрыть задачу в task-файле. Chat-only «готово» без обновления файла — нарушение контракта.

Default posture — **active task-context guard**. Включайся на любое движение вокруг задач: обсуждение, уточнение, выбор подхода, редактирование текста, кодовую правку, статус «почти готово», «проверь», «закрыли». Даже если пользователь «просто обсуждает», коротко назови, к какому текущему task-файлу / Stage / planned task относится разговор, и что это меняет для контракта. Если начинается реальная правка текста/кода/артефакта, не отпускай без проверки текущих критериев task-файла.

**Reason wide, emit narrow.** Рассуждай широко (discovery, адверсариал, sanity-checks). Наружу — file write + компактный receipt + 1-3 строки простым языком, что держать в голове. Long-form — только на `show` или явный criteria-only запрос.

## Режимы

- **`task`** (default) — полный lifecycle task-файла: locate/create/update → fill sections → adversarial → commit → receipt; после выполнения: closeout update → receipt. → **required:** [references/task-file-lifecycle.md](references/task-file-lifecycle.md).
- **`strategy-trace`** (только явный запрос) — read-only проверка: служит ли артефакт Goal и активному Stage. Нужен артефакт. → **required:** [references/strategy-trace-mode.md](references/strategy-trace-mode.md).
- **`pulse-check`** (только явный запрос) — dialog-time memory probe. Артефакт не нужен. → **required:** [references/pulse-check-mode.md](references/pulse-check-mode.md).

Не подменяй `task` молча ни одним read-only режимом. Ни один read-only режим не заменяет полный trajectory-audit артефакта.

## Plan-Anchor Gate — Блокирующий

**До всего остального** проверь: задача якорится хотя бы в одном элементе `_ops/PROJECT-PLAN.md` (Goal / активный Stage / Step / Anti-goal) или релевантной секции `_ops/INTERVIEW.md`?

- **Да** — продолжай lifecycle.
- **Нет, и задача тривиальная** (однострочник, typo, переименование, очевидная локальная правка) — скил не нужен, skip.
- **Нет, и задача значимая** — **блок**. Emit короткое сообщение: «Task не якорится в PROJECT-PLAN. Вызываю `project-strategy` для обновления плана, потом возвращаюсь в `task-contract`». **Не** создавай task-файл. `local-only` не обходит этот gate: `local-only` — только для критериев **о самом коде** (формат данного diff'а, локальный инвариант), не для задачи целиком.

Этот gate поддерживает hot-triad принцип: task без якоря в плане — сигнал, что PROJECT-PLAN требует обновления, а не flexibility в критериях.

## Gate — Когда Использовать

- Step в PROJECT-PLAN.md перешёл в `[~]` — task-файл нужен.
- Начинается нетривиальная работа без task-файла в соответствующей фазе.
- Идёт любое обсуждение вокруг задачи, даже без исполнения: надо поднять текущий task context и сказать, к какой задаче относится разговор.
- Идёт редактирование текста, кода или артефакта внутри активной задачи: надо сверить работу с Подшагами, Must / Must-not и Verification protocol текущего task-файла.
- Существующий task-файл устарел: Подшаги не отражают реальность, критерии не бьют с Goal / активным Stage.
- Завершена нетривиальная задача с task-файлом: нужно отметить выполненное, дописать фактический evidence / verification и закрыть файл задачи.
- Запрос «зафиксируй критерии», «acceptance criteria», «что считается готовым», «зафиксируй scope».
- Явный запрос `strategy-trace` (есть артефакт) или `pulse-check` (начало сессии с планом в `_ops/`).

### SKIP

- Тривиальные фактические вопросы без execution-шага.
- Микро-правки, где пользователь сам определил успех.
- Пользователь уже явно дал testable критерии в запросе.
- Task-файл актуален, ask материально не менялся.
- `strategy-trace`, когда реально нужен полный trajectory-audit артефакта.
- `pulse-check`, когда есть конкретный артефакт (используй `strategy-trace`) или сессия только началась.

## Workflow — Task Mode (скелет)

Шесть чекпоинтов. Полные детали, форма секций, бюджеты, семь gate-правил для критериев — в [references/task-file-lifecycle.md](references/task-file-lifecycle.md).

1. **Locate / Create / Update** — найти или создать файл `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` под активный Step; при обсуждении/правке найти связанный текущий task-файл; при closeout открыть тот же файл, не создавать новый.
2. **Read upstream** — Goal + активный Stage + Anti-goals из PROJECT-PLAN, релевантные секции INTERVIEW. → при неочевидном типе проекта / маршруте: **required:** [references/discovery-map.md](references/discovery-map.md).
3. **Task Context Guard** — если это обсуждение, коротко назови связанный task-файл / Stage / planned task и что обсуждение меняет: scope, assumption, risk, criterion или nothing.
4. **Draft / Criteria Check** — для нового/изменённого контракта заполнить Цель / Подшаги / Критерии приёмки; для реальной правки проверить diff/текст/артефакт против текущих Подшагов, Must / Must-not и Verification protocol.
5. **Adversarial → Gate** — один цикл против failure modes. → **required:** [references/failure-modes.md](references/failure-modes.md), выбрать 2-5 модов под тип задачи.
6. **Commit + Receipt** — записать файл, emit короткий receipt с `Refs applied:`.
7. **Completion Closeout** — после выполнения задачи снова обновить тот же task-файл: отметить `[x]`, вписать фактический evidence / verification result и emit closeout receipt.

Работать по скелету без открытия `task-file-lifecycle.md` **нельзя**: там семь gate-правил, точный шейп секций, бюджеты.

## Output Contract

- Владеешь только task-файлом. `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md` не трогаешь. Папки `_ops/plans/phase-NN-<slug>/` не создаёшь — это зона `project-strategy`.
- Task-файл: три секции — Цель / Подшаги / Критерии приёмки. Формат — [references/format-examples.md](references/format-examples.md).
- После write — компактный receipt: путь task-файла + Must-count + `Refs applied:` + 1-3 строки простым языком, что помнить из `_ops/`. Сразу возвращаешь агента к задаче.
- При обсуждении без правки emit короткий task-context note вместо полного task-file receipt: связанный Stage/task, применимые критерии, что это меняет.
- При правке текста/кода/артефакта emit criteria-check receipt: какие Must/Must-not затронуты, что проходит, что блокирует closeout.
- После выполнения нетривиальной задачи `task-contract` вызывается снова для closeout. Итог выполнения фиксируй в task-файле, не только в финальном ответе: `[x]` на выполненных Подшагах и Must, фактический Evidence / Actual verification, короткий closeout receipt.
- Long-form контракт — только на `show` или явный criteria-only запрос.
- `strategy-trace` и `pulse-check` — read-only. Не emit'и `Must`, `Must-not`, verification-протокол.
- `pulse-check`: если плана нет — `forgotten — strategic map unavailable` и стоп.
- **`Refs applied: <path>#<anchor>, ...` обязательна.** Пустая = сбой Gate, receipt невалиден.

Форма receipt, форма verdict strategy-trace, три-значный verdict pulse-check, Anchor-правила для Must, примеры — в соответствующем mode-ref. Формы и примеры целиком → [references/format-examples.md](references/format-examples.md).

## Role Boundaries

- Не выполняй саму задачу пользователя во время работы скила.
- Не создавай и не обновляй `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md`, папки фаз — владелец `project-strategy`.
- Инструкционный слой — upstream. Владелец `instruction-layer`. Нерешённый control-surface → откат туда.
- Ни один файл вне `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` этот скил не изменяет.
- Closeout обновляет только существующие секции task-файла: чекбоксы Подшагов / Must, конкретный evidence, verification result. Новые секции «Итог», «Notes», «Changelog» не добавляй.
- В `task` default **не блокирует работу**: после записи файла и короткого receipt сразу возвращает к задаче.
- Если пользователь явно попросил только критерии — emit long-form артефакт и стоп.

## Escalation Rules

- Нет `_ops/PROJECT-PLAN.md` или Goal размыт / план обрывается → откат в `project-strategy`.
- **Task не якорится ни в одном элементе PROJECT-PLAN** и не тривиален → блок, откат в `project-strategy`. `local-only` как обход не допускается.
- Папки `_ops/plans/phase-NN-<slug>/` нет, хотя Stage в плане есть → сигнал `project-strategy`: плановый слой рассинхронизирован. Скил сам папку не создаёт.
- Владелец правила / control-surface / форма системы не решены → откат в `instruction-layer`.
- Substantial evidence артефакта, нужен full trajectory-audit → trajectory-auditor, не этот скил.
- Явный запрос `strategy-trace` без артефакта → вернуть запрос на артефакт или переключиться в `pulse-check`.
- Артефакт передан под `pulse-check` → переключиться на `strategy-trace`.

## Эфемерный Слой — Жёсткое Правило

`_ops/plans/` — эфемерный слой. Когда пользователь разворачивает план (меняется Goal, подход, технология — напр. переход React → Webflow), `project-strategy` может удалить или переставить фазы целиком. Поэтому task-файлы и папки фаз **никто не должен цитировать снаружи** — ни код, ни `knowledge/`, ни другие скиллы, ни репорты, ни summaries.

Единственные legal якорные точки — элементы `_ops/PROJECT-PLAN.md` (Goal / Stage / Step / Anti-goal) и секции `_ops/INTERVIEW.md`. Владелец обоих — `project-strategy`.

Это значит:
- `Anchored in:` в Критериях приёмки ссылается **только** на PROJECT-PLAN или INTERVIEW, не на другой task-файл и не на путь внутри `_ops/plans/`.
- Не дублируй содержимое task-файла в отчётах, summaries, README, knowledge/.
- При удалении Stage из плана task-файл может исчезнуть — никто снаружи не должен сломаться.

## Связь С Другими Скиллами

- **`project-strategy`** — upstream-владелец `PROJECT-PLAN.md`, `INTERVIEW.md`, `learnings.md`, папок фаз. Этот скил **читает**, не пишет. После closeout task-файла, если изменилась фаза, траектория или реальность против плана, верни сигнал в `project-strategy`.
- **`instruction-layer`** — upstream для инструкционного слоя.
- **`step-back`** — session-local reframe линии рассуждения. Напрямую не примыкает.

## Субагенты

- **`smith`** (`~/.claude/agents/smith.md`) — критик плана на швах. Опционален на шаге 5 Adversarial для task-файлов с 3+ Подшагами с хэндоффами между ними или для phase-папок с накопившимися задачами, которые не сверялись между собой. Возвращает список швов (`missing_intermediate`, `phantom_prerequisite`, `vague_boundary`, `hidden_coupling`) с `location`-привязками — инкорпорируй в Подшаги/Критерии или сними после проверки допущения. Не заменяет `references/failure-modes.md`, дополняет его на крупных task-файлах и на cross-task consistency. Одной adversarial-итерации (своя или Smith) достаточно — вторая обычно over-engineering.
- **`brooks`** (`~/.claude/agents/brooks.md`) — критик LLM-сгенерированного кода. В `task`-режиме задействуется редко: task-contract код не ревьюит. Возможное применение — на Completion Closeout, если evidence включает сгенерированный код и нужен структурный sanity-check (central_model_violation / shallow_abstraction / red_flag) перед `[x]`. Не расширяй контракт task-contract ради его использования — если structural issues значимые, это сигнал на новый task-файл под refactor, а не на блокировку closeout.

## References

- [references/task-file-lifecycle.md](references/task-file-lifecycle.md) — полный процесс default-режима: Locate, Discover, Draft, Adversarial, Commit, Receipt, Completion Closeout; семь gate-правил для критериев.
- [references/strategy-trace-mode.md](references/strategy-trace-mode.md) — read-only проверка alignment артефакта.
- [references/pulse-check-mode.md](references/pulse-check-mode.md) — dialog-time memory probe.
- [references/discovery-map.md](references/discovery-map.md) — маршрутизация discovery по типу проекта и задачи.
- [references/failure-modes.md](references/failure-modes.md) — модели для adversarial pass.
- [references/format-examples.md](references/format-examples.md) — форма task-файла и receipts, примеры.
