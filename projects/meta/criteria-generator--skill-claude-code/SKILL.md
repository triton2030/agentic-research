---
name: criteria-generator
description: >
  Генератор task-level критериев приёмки. Используй перед
  выполнением любой нетривиальной или неоднозначной задачи, чтобы
  зафиксировать что считается «готово» в виде наблюдаемых,
  не-обходимых Must. Триггеры-фразы: "сгенерируй критерии",
  "acceptance criteria", "прежде чем делать — зафиксируй критерии",
  "зафиксируй scope", "как проверим что готово", "критерии",
  "что считается готовым", "contract", "strategy-trace",
  "pulse-check", "проверь alignment", "drift-check", "проверь
  память", "ещё помнишь о чём мы". Также срабатывает на ask, где
  «готово» не очевидно, запрос высокоставочен, легко перечитать
  неверно, приглашает shortcut-поведение. Три режима:
  `contract` (default — узкий execution-контракт), `strategy-trace`
  (только явный запрос — read-only alignment-проверка артефакта),
  `pulse-check` (только явный запрос — read-only memory-probe
  диалога). Читает `_ops/PROJECT-PLAN.md` (Goal + активный Stage +
  Anti-goals) и `_ops/INTERVIEW.md` (предпочтения, ограничивающие
  критерии) как upstream карту, владельца которой — `main-strategy`.
  Читает `_ops/learnings.md` только когда зафиксированная дельта
  реально меняет контракт. Не создаёт и не обновляет `_ops/`. В
  `contract` режиме по умолчанию не останавливает работу: выдаёт
  короткий receipt, простое напоминание что держать в голове из
  `_ops/`, и возвращает агента к задаче.
  SKIP на: тривиальных фактических вопросах без execution-шага;
  когда пользователь уже сам дал testable критерии; когда
  предыдущий ход уже выдал контракт и пользователь его утвердил.
  Если упираешься в нерешённый архитектурный выбор — откат в
  `system-architect`. Если нет плана — откат в `main-strategy`.
---

# Criteria Generator

Объяви в начале короткой строкой под режим:

- Contract: «Использую `criteria-generator` — сгенерирую критерии приёмки».
- Strategy-trace: «Использую `criteria-generator` в режиме `strategy-trace` — проверю alignment».
- Pulse-check: «Использую `criteria-generator` в режиме `pulse-check` — проверю память диалога».

Отвечай и пиши артефакты по-русски, если пользователь явно не просит другой язык.

## Роль

Переводишь проектный Goal и предпочтения пользователя из `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` в **task-level критерии приёмки** — узкий контракт, под которым исполнитель-агент будет проверять сам себя.

Качество исполнения ниже по цепочке держится на постоянном фокусе на Goal и активном Stage. Контракт без якоря в план или профиль слабее, даже если выглядит конкретным.

**Reason wide, emit narrow.** Рассуждай широко: discovery, EVPI, adversarial pass, quality gate. Наружу в чат не вываливай trace рассуждения. Мышление — это продукт; видимый выход — компактный **receipt** и короткое простое напоминание, что держать в голове из `_ops/`. Полный контракт (intent, anchors, assumptions, Must / Must-not / Verification) держи внутри execution-плана и применяй сразу в следующем execution-ходе по умолчанию. Печатай long-form только если пользователь явно попросил `show` или отдельно попросил только критерии.

## Режимы

Три режима, один владелец:

- **`contract`** (по умолчанию) — узкий augmented-prompt как жёсткий execution-контракт. Детали в [references/contract-mode.md](references/contract-mode.md).
- **`strategy-trace`** (только явный запрос) — read-only проверка: служит ли конкретный ask / план / draft Goal и активному Stage. На вход нужен артефакт. Детали в [references/strategy-trace-mode.md](references/strategy-trace-mode.md).
- **`pulse-check`** (только явный запрос) — dialog-time memory probe: держит ли текущая сессия Goal и активный Stage в рабочей памяти. Артефакт не нужен. Детали в [references/pulse-check-mode.md](references/pulse-check-mode.md).

Переключайся в `strategy-trace` только на явный интент: `strategy-trace`, «проверь alignment», «быстрый drift-check», «следует ли это ещё плану». `pulse-check` — только на явный интент: `pulse-check`, «пульс», «проверь память», «ещё помнишь о чём мы». Не подменяй contract-генерацию ни одним из read-only режимов молча.

Ни один read-only режим не заменяет полный trajectory-audit и архитектурное решение. Если реальный вопрос — дрейф качества артефакта, нужен trajectory-auditor. Если реальный вопрос — где жить durable-правилу, маршрут в `system-architect`.

## Когда Использовать

- Перед выполнением нетривиальной задачи, у которой «готово» не очевидно.
- Когда запрос размыт, высокоставочен, легко перечитать неверно или приглашает shortcut-поведение.
- Перед передачей работы исполнителю или конвертацией запроса в бриф.
- Когда критерии отсутствуют, мягкие или легко фейкнуть.
- Перед серьёзным execution — чтобы task-level критерии оставались в alignment с Goal и активным Stage.
- На явный запрос `strategy-trace` — быстрая проверка alignment артефакта.
- На явный запрос `pulse-check` — probe памяти диалога.

## Когда Не Использовать

- Тривиальные фактические вопросы без execution-шага.
- Микро-правки, где пользователь сам определил успех.
- Пользователь уже явно дал testable критерии.
- `strategy-trace`, когда реально нужен полный trajectory-audit артефакта.
- `pulse-check`, когда есть конкретный артефакт (используй `strategy-trace`), или когда сессия только началась.
- Предыдущий ход уже выдал контракт, ask материально не менялся. Следующий шаг — execution, не повторный проход.

Если скил вызван на тривиальной задаче — держи результат минимальным.

## Role Boundaries

- Не выполняй саму задачу пользователя во время работы скила.
- Не создавай `_ops/`, не создавай и не обновляй `_ops/PROJECT-PLAN.md` / `_ops/INTERVIEW.md` / `_ops/learnings.md`. Их владелец — `main-strategy`.
- Инструкционный слой, сформированный `system-architect`, — ближайший upstream для task-критериев. Если владелец / control-surface / форма системы не решены и живут только в чате — остановись и откатывай в `system-architect`.
- В `contract` режиме скилл по умолчанию **не блокирует работу**: после receipt и короткого напоминания из `_ops/` сразу возвращает агента к задаче под этим контрактом.
- Если пользователь явно попросил только критерии / contract / scope-fix без выполнения — emit'и артефакт и остановись на нём.
- `strategy-trace` и `pulse-check` — read-only. Не emit'и `Must`, `Must-not`, verification-протокол. В `pulse-check` если план отсутствует — `forgotten — strategic map unavailable` и стоп.

## Mode Selection

1. `contract` — по умолчанию.
2. `strategy-trace` — только на явный интент. Требует артефакт.
3. `pulse-check` — только на явный интент. Артефакт не берёт.
4. Если есть большой артефакт для аудита — предпочитай trajectory-auditor (когда доступен).
5. Нет плана / нерешённые предпочтения → `main-strategy`. Нерешённый control-surface → `system-architect`.

## Обязательное Чтение — Перед Первым Emit

Load-bearing детали (семь gate-правил, receipt-шейп, verify-шаги) **не живут в этом файле**. Прежде чем выдать любой receipt, прочитай:

- **`contract` mode** → [references/contract-mode.md](references/contract-mode.md) целиком. Без этого не знаешь ни семь gate-правил, ни формат receipt, ни что такое Adversarial pass. Emit без чтения — автоматически нарушение Gate.
- **`strategy-trace` mode** → [references/strategy-trace-mode.md](references/strategy-trace-mode.md) целиком.
- **`pulse-check` mode** → [references/pulse-check-mode.md](references/pulse-check-mode.md) целиком.

Дополнительно по ситуации:
- **Discover шаг** → [references/discovery-map.md](references/discovery-map.md), если тип проекта или маршрут к local sources не очевиден.
- **Adversarial pass** → [references/failure-modes.md](references/failure-modes.md), выбрать 2-5 модов под тип задачи. Без открытия файла выбор модов — импровизация.

**Receipt обязан содержать строку `Refs applied: <path>#<anchor>, ...`** — перечислить references, которые реально использовались. Пустая строка или отсутствие = сбой Gate, receipt невалиден. Это audit trail того, что progressive disclosure сработало, а не был симулирован.

## Процесс — Contract Mode (скелет)

Четыре чекпоинта. Детали и артефакты каждого — в [references/contract-mode.md](references/contract-mode.md).

1. **Capture** — точная цитата задачи.
2. **Discover** — план + предпочтения до local.
3. **Draft → Adversarial → Gate** (один цикл).
4. **Emit** — компактный receipt с `Refs applied:`.

Работать по скелету без открытия `contract-mode.md` нельзя: здесь нет семи gate-правил, нет точного шейпа receipt'а, нет бюджетов. Не реконструируй их по памяти — открой файл.

## Output Constraint

Выдаёшь только mode-appropriate артефакт. В `contract` режиме default — компактный receipt, затем 1-3 короткие строки простым русским языком: что важно помнить из `_ops/`, и после этого сразу продолжаешь работу. Вопрос задавай только если есть load-bearing EVPI или если пользователь явно запросил criteria-only / `show`. Никаких support-файлов в `_ops/`, кода задачи, частичной реализации и side-work вне текущей задачи.

## Красные Флаги

- «Задача очевидная, можно пропустить discovery» — нет, неверные критерии почти всегда начинаются отсюда.
- «Adversarial pass — overkill» — нет, скил существует ради этого шага.
- «Можно сказать что проверено, не называя артефакт» — Evidence обязан быть explicit.
- «Тонкий контекст значит импровизировать» — нет, тонкий контекст — причина существования EVPI-gate.
- «Evidence подразумевается критерием» — нет, LLM пропускают implied obligations.
- «Больше constraints = безопаснее» — нет, over-constraint — свой bypass.
- «Нашёл шесть plausible рисков — перечислю все» — сожми до немногих, материально меняющих execution.
- «Must очевидно связан с целью — anchor не нужен» — делай anchor явным или `local-only` с причиной.
- «Можно использовать `strategy-trace` как дешёвый full-review» — он проверяет alignment памяти, не качество артефакта.
- «Можно назвать aligned, не цитируя цепочку в `_ops/`» — verdict без anchors — театр.
- «`pulse-check` без cold recall — ок, просто прочитаю `_ops/` сначала» — probe тестирует, что сессия держит, а не что ты можешь вывести.
- «`partial` достаточно для pulse-check» — три-значный verdict намеренный.
- «Если мышление было хорошее — покажу полный контракт» — default receipt; long-form on-demand.
- «Можно после receipt по привычке остановиться и ждать разрешения» — нет, в default `contract` режиме надо продолжать работу.

## Escalation Rules

- Нет `_ops/PROJECT-PLAN.md` или Goal размыт / план обрывается → откат в `main-strategy`.
- Владелец правила / control-surface / форма системы не решены → откат в `system-architect`.
- Substantial evidence артефакта для аудита, нужен full trajectory-audit → trajectory-auditor, не этот скил.
- Пользователь явно просит `strategy-trace`, но артефакта нет → вернуть запрос на артефакт или переключиться в `pulse-check`.
- Пользователь передал артефакт под `pulse-check` → переключиться на `strategy-trace`.

## Связь С Другими Скиллами

- **`main-strategy`** — upstream-владелец `INTERVIEW.md`, `PROJECT-PLAN.md`, `learnings.md`. Этот скил **читает** их как карту, но не пишет.
- **`system-architect`** — upstream для инструкционного слоя. Нерешённый owner / control-surface → откат сюда.
- **`step-back`** — session-local reframe, когда drift произошёл в самой линии размышления. К `criteria-generator` не примыкает напрямую.

## References

- [references/contract-mode.md](references/contract-mode.md) — полный процесс default-режима: Capture, Discover, Draft→Adversarial→Gate, Emit.
- [references/strategy-trace-mode.md](references/strategy-trace-mode.md) — read-only проверка alignment артефакта.
- [references/pulse-check-mode.md](references/pulse-check-mode.md) — dialog-time memory probe.
- [references/discovery-map.md](references/discovery-map.md) — расширенная маршрутизация discovery по типу проекта и задачи.
- [references/failure-modes.md](references/failure-modes.md) — модели для adversarial pass.
- [references/format-examples.md](references/format-examples.md) — форма выходов.
