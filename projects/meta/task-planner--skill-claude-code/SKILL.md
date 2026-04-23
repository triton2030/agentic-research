---
name: task-planner
description: >
  Владелец файла задачи `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`.
  Создаёт, обновляет и закрывает файл под активный Step из
  `_ops/PROJECT-PLAN.md`. Пишет секции Цель, Подшаги, Критерии
  приёмки **целиком** — это его артефакт, не shared с `main-strategy`.
  Триггеры: Step в PROJECT-PLAN.md перешёл в `[~]` и task-файла нет
  или он устарел; начинается нетривиальная работа без task-файла;
  запрос «сгенерируй критерии», «acceptance criteria», «что
  считается готовым», «зафиксируй scope», «прежде чем делать —
  зафиксируй критерии»; ask высокоставочен или «готово» не
  очевидно. Критерии приёмки — Must / Must-not с обязательным
  `Anchored in:` на Goal / Stage / Step / Anti-goal в PROJECT-PLAN
  или раздел INTERVIEW. `local-only` — только для критериев о
  самом коде (формат diff'а, читаемость, локальный инвариант), не
  для задачи целиком. Три режима: `task` (default — владение
  файлом задачи), `strategy-trace` (только явный запрос — read-only
  проверка alignment артефакта против Goal+Stage), `pulse-check`
  (только явный запрос — read-only memory-probe диалога). Читает
  `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` как upstream —
  владелец `main-strategy`. Читает `_ops/learnings.md`, если
  зафиксированная дельта реально меняет контракт. SKIP на:
  тривиальных фактических вопросах; микро-правках с очевидным
  успехом; задачах, где пользователь уже дал testable критерии;
  актуальном task-файле без изменений в ask. Если упираешься в
  нерешённый архитектурный выбор — откат в `system-architect`.
  Если task не якорится ни в одном элементе PROJECT-PLAN — **блок**,
  откат в `main-strategy` для обновления плана, потом возвращаюсь.
---

# Task Planner

Объяви в начале короткой строкой:

- Task (default): *«Использую `task-planner` — открою/обновлю файл задачи под активный Step»*.
- Strategy-trace: *«Использую `task-planner` в режиме `strategy-trace` — проверю alignment артефакта»*.
- Pulse-check: *«Использую `task-planner` в режиме `pulse-check` — проверю память диалога»*.

Отвечай и пиши артефакты по-русски.

> **Stop.** Этот файл — маршрут и gate-список. Полный lifecycle (locate → discover → draft → adversarial → write), форма секций task-файла, failure modes, discovery map — **в ref-файлах**. Write task-файла без открытия `task-file-lifecycle.md` = нарушение контракта.

## Роль

Владелец файла задачи `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`. Для каждого активного Step из `_ops/PROJECT-PLAN.md` создаёт, поддерживает и закрывает один файл. Три секции — Цель / Подшаги / Критерии приёмки — пишутся этим скиллом целиком. `main-strategy` владеет планом и папками фаз, но **не** содержимым task-файлов.

**Reason wide, emit narrow.** Рассуждай широко (discovery, адверсариал, sanity-checks). Наружу — file write + компактный receipt + 1-3 строки простым языком, что держать в голове. Long-form — только на `show` или явный criteria-only запрос.

## Режимы

- **`task`** (default) — полный lifecycle task-файла: locate/create → fill sections → adversarial → commit → receipt. → **required:** [references/task-file-lifecycle.md](references/task-file-lifecycle.md).
- **`strategy-trace`** (только явный запрос) — read-only проверка: служит ли артефакт Goal и активному Stage. Нужен артефакт. → **required:** [references/strategy-trace-mode.md](references/strategy-trace-mode.md).
- **`pulse-check`** (только явный запрос) — dialog-time memory probe. Артефакт не нужен. → **required:** [references/pulse-check-mode.md](references/pulse-check-mode.md).

Не подменяй `task` молча ни одним read-only режимом. Ни один read-only режим не заменяет полный trajectory-audit артефакта.

## Plan-Anchor Gate — Блокирующий

**До всего остального** проверь: задача якорится хотя бы в одном элементе `_ops/PROJECT-PLAN.md` (Goal / активный Stage / Step / Anti-goal) или релевантной секции `_ops/INTERVIEW.md`?

- **Да** — продолжай lifecycle.
- **Нет, и задача тривиальная** (однострочник, typo, переименование, очевидная локальная правка) — скил не нужен, skip.
- **Нет, и задача значимая** — **блок**. Emit короткое сообщение: «Task не якорится в PROJECT-PLAN. Вызываю `main-strategy` для обновления плана, потом возвращаюсь в `task-planner`». **Не** создавай task-файл. `local-only` не обходит этот gate: `local-only` — только для критериев **о самом коде** (формат данного diff'а, локальный инвариант), не для задачи целиком.

Этот gate поддерживает hot-triad принцип: task без якоря в плане — сигнал, что PROJECT-PLAN требует обновления, а не flexibility в критериях.

## Gate — Когда Использовать

- Step в PROJECT-PLAN.md перешёл в `[~]` — task-файл нужен.
- Начинается нетривиальная работа без task-файла в соответствующей фазе.
- Существующий task-файл устарел: Подшаги не отражают реальность, критерии не бьют с Goal / активным Stage.
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

Пять чекпоинтов. Полные детали, форма секций, бюджеты, семь gate-правил для критериев — в [references/task-file-lifecycle.md](references/task-file-lifecycle.md).

1. **Locate / Create** — найти или создать файл `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` под активный Step.
2. **Read upstream** — Goal + активный Stage + Anti-goals из PROJECT-PLAN, релевантные секции INTERVIEW. → при неочевидном типе проекта / маршруте: **required:** [references/discovery-map.md](references/discovery-map.md).
3. **Draft** — заполнить Цель / Подшаги / Критерии приёмки. Критерии — Must / Must-not с `Anchored in:`.
4. **Adversarial → Gate** — один цикл против failure modes. → **required:** [references/failure-modes.md](references/failure-modes.md), выбрать 2-5 модов под тип задачи.
5. **Commit + Receipt** — записать файл, emit короткий receipt с `Refs applied:`.

Работать по скелету без открытия `task-file-lifecycle.md` **нельзя**: там семь gate-правил, точный шейп секций, бюджеты.

## Output Contract

- Владеешь только task-файлом. `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md` не трогаешь. Папки `_ops/plans/phase-NN-<slug>/` не создаёшь — это зона `main-strategy`.
- Task-файл: три секции — Цель / Подшаги / Критерии приёмки. Формат — [references/format-examples.md](references/format-examples.md).
- После write — компактный receipt: путь task-файла + Must-count + `Refs applied:` + 1-3 строки простым языком, что помнить из `_ops/`. Сразу возвращаешь агента к задаче.
- Long-form контракт — только на `show` или явный criteria-only запрос.
- `strategy-trace` и `pulse-check` — read-only. Не emit'и `Must`, `Must-not`, verification-протокол.
- `pulse-check`: если плана нет — `forgotten — strategic map unavailable` и стоп.
- **`Refs applied: <path>#<anchor>, ...` обязательна.** Пустая = сбой Gate, receipt невалиден.

Форма receipt, форма verdict strategy-trace, три-значный verdict pulse-check, Anchor-правила для Must, примеры — в соответствующем mode-ref. Формы и примеры целиком → [references/format-examples.md](references/format-examples.md).

## Role Boundaries

- Не выполняй саму задачу пользователя во время работы скила.
- Не создавай и не обновляй `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md`, папки фаз — владелец `main-strategy`.
- Инструкционный слой — upstream. Владелец `system-architect`. Нерешённый control-surface → откат туда.
- Ни один файл вне `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` этот скил не изменяет.
- В `task` default **не блокирует работу**: после записи файла и короткого receipt сразу возвращает к задаче.
- Если пользователь явно попросил только критерии — emit long-form артефакт и стоп.

## Escalation Rules

- Нет `_ops/PROJECT-PLAN.md` или Goal размыт / план обрывается → откат в `main-strategy`.
- **Task не якорится ни в одном элементе PROJECT-PLAN** и не тривиален → блок, откат в `main-strategy`. `local-only` как обход не допускается.
- Папки `_ops/plans/phase-NN-<slug>/` нет, хотя Stage в плане есть → сигнал `main-strategy`: плановый слой рассинхронизирован. Скил сам папку не создаёт.
- Владелец правила / control-surface / форма системы не решены → откат в `system-architect`.
- Substantial evidence артефакта, нужен full trajectory-audit → trajectory-auditor, не этот скил.
- Явный запрос `strategy-trace` без артефакта → вернуть запрос на артефакт или переключиться в `pulse-check`.
- Артефакт передан под `pulse-check` → переключиться на `strategy-trace`.

## Эфемерный Слой — Жёсткое Правило

`_ops/plans/` — эфемерный слой. Когда пользователь разворачивает план (меняется Goal, подход, технология — напр. переход React → Webflow), `main-strategy` может удалить или переставить фазы целиком. Поэтому task-файлы и папки фаз **никто не должен цитировать снаружи** — ни код, ни `knowledge/`, ни другие скиллы, ни репорты, ни summaries.

Единственные legal якорные точки — элементы `_ops/PROJECT-PLAN.md` (Goal / Stage / Step / Anti-goal) и секции `_ops/INTERVIEW.md`. Владелец обоих — `main-strategy`.

Это значит:
- `Anchored in:` в Критериях приёмки ссылается **только** на PROJECT-PLAN или INTERVIEW, не на другой task-файл и не на путь внутри `_ops/plans/`.
- Не дублируй содержимое task-файла в отчётах, summaries, README, knowledge/.
- При удалении Stage из плана task-файл может исчезнуть — никто снаружи не должен сломаться.

## Связь С Другими Скиллами

- **`main-strategy`** — upstream-владелец `PROJECT-PLAN.md`, `INTERVIEW.md`, `learnings.md`, папок фаз. Этот скил **читает**, не пишет.
- **`system-architect`** — upstream для инструкционного слоя.
- **`step-back`** — session-local reframe линии рассуждения. Напрямую не примыкает.

## References

- [references/task-file-lifecycle.md](references/task-file-lifecycle.md) — полный процесс default-режима: Locate, Discover, Draft, Adversarial, Commit, Receipt; семь gate-правил для критериев.
- [references/strategy-trace-mode.md](references/strategy-trace-mode.md) — read-only проверка alignment артефакта.
- [references/pulse-check-mode.md](references/pulse-check-mode.md) — dialog-time memory probe.
- [references/discovery-map.md](references/discovery-map.md) — маршрутизация discovery по типу проекта и задачи.
- [references/failure-modes.md](references/failure-modes.md) — модели для adversarial pass.
- [references/format-examples.md](references/format-examples.md) — форма task-файла и receipts, примеры.
