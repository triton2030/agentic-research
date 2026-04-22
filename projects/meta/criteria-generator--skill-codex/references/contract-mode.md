# Contract Mode — Процесс

Default-режим `criteria-generator`. Четыре чекпоинта. По умолчанию этот режим заканчивается не паузой, а связкой: `receipt -> короткое напоминание из _ops -> немедленное продолжение работы`.

## 1. Capture

Процитируй задачу пользователя дословно.

## 2. Discover — сначала план + предпочтения, потом local

### `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` — обязательно

Переводи только части, что материально меняют контракт:
- `Goal` — durable-результат, которому задача служит.
- `Approach & Why` — задача не должна его молча нарушать.
- Активный `Stage` — что важно сейчас vs потом; открытые Steps → Must или scope-ограничения.
- `Anti-goals` → Must-not.
- Релевантные секции `INTERVIEW.md` — load-bearing предпочтения → Must или Must-not.

### `_ops/learnings.md`

Только если зафиксированная дельта материально меняет критерии или запрещённые shortcuts.

### Local sources

Только то, что меняет смысл «хорошо» для ЭТОЙ задачи. Маршрут: `projects/{category}/...` → `AGENTS.md`, `CLAUDE.md` → `README*`, `docs/` → active instruction-surfaces → git state. Читать всё «на всякий случай» — bypass.

Если нет `_ops/PROJECT-PLAN.md` — отметь **weak strategic grounding**, предпочитай тоньше контракт.

Расширенная маршрутизация — в [discovery-map.md](discovery-map.md).

### Выход шага

- Буллеты `<source>: <one-line takeaway>`.
- `Understood intent` — 1-3 предложения.
- `Unknowns` — что могло бы материально изменить критерии.

Если пользователь предложил solution path — классифицируй: `accept`, `narrow`, `reject`.

## 3. Draft → Adversarial → Gate (один цикл)

### Draft

Три бакета:

- **`Must`** — каждый несёт `Evidence:` (наблюдаемый артефакт) и `Anchored in:` (секция PROJECT-PLAN / INTERVIEW или `local-only — <reason>`).
- **`Must not`** — запрещённые shortcuts. Добавляй, только когда bypass и вероятен, и не закрыт уже Must.
- **`Verification protocol`** — 1-3 конкретных действия, highest-signal proof.

Бюджеты: 2-4 `Must`, 0-2 `Must not`, 1-3 verification-шагов.

### Adversarial pass

Представь ленивого агента, пытающегося формально удовлетворить каждый критерий плохой работой. Усиливай или объединяй. Подбери 2-5 модов из [failure-modes.md](failure-modes.md).

### Gate — Семь Правил

Каждый `Must` обязан пройти:

1. **Anchor traceability** — `Anchored in:` явный или `local-only — <reason>`. Молчаливого отсутствия нет.
2. **Observable** — рецензент проверяет evidence, не утверждение.
3. **Unambiguous** — два читателя рассудили бы одинаково.
4. **Non-bypassable** — слабый агент не пройдёт мелкой работой.
5. **Minimal** — удаление материально повышает риск провала.
6. **Non-overlapping** — не защищено другим критерием.
7. **On-trajectory** — `Must` служит чему-то на пути к Goal. `PROJECT-PLAN.md` — **whitelist, а не wishlist**: критерий на гипотетическое будущее, через которое траектория не проходит, — отбрасывай.

Не прошедший проверку → переписать или удалить. Два критерия на один failure mode → оставить сильнее.

### EVPI

Если один вопрос материально изменит scope или irreversible-решение — задай в чате с inline-опциями. Иначе запиши как `[EVPI-would-ask]` в Assumptions.

Не контрабанди нерешённую архитектуру в `Must` → откат в `system-architect`.

## 4. Emit — Компактный Receipt + Короткое Напоминание Из `_ops`

Держи полный контракт (intent, anchors, assumptions, Must / Must-not / Verification) внутри execution-плана. Emit'и компактный receipt:

```md
## Criteria receipt

- Intent: <одно предложение>
- Anchors: <_ops путь + секция, ...> | weak-grounding | local-only — <reason>
- Refs applied: <references/<file>.md#<anchor>, ...>
- Draft: <M> Must · <N> Must-not · <K> Verify
- Gate: <7/7 passed | weak — <reason>> · bypasses closed: <теги>
- Assumptions: <счётчик + теги | —>
- User-proposed path: <accept | narrow | reject>
- Ready: <yes | blocked — <reason>>
```

Правила:
- Receipt ≤ 9 строк.
- Пропускай поля с `—` — **кроме** `Refs applied:`. Она обязательна: пустая = receipt невалиден.
- `Refs applied:` минимум `contract-mode.md`; добавляй `failure-modes.md` если прогонял adversarial по конкретным модам; `discovery-map.md` если сверялся по типу проекта.
- Не расширяй receipt в отчёт.

Сразу после receipt дай короткий блок простым русским языком:

```md
Помним из _ops:
- <что мы в итоге хотим получить>
- <что важно именно на этом этапе>
- <какой главный anti-goal / preference / learning нельзя потерять>
```

Правила для блока:

- 1-3 строки, только materially relevant вещи.
- Простой русский язык, без цитат, якорей, имён файлов и бюрократии.
- Если `_ops/` нет или там нет load-bearing сигнала для этой задачи — скажи это честно одной строкой и не выдумывай.

После этого:

- если пользователь явно просил только критерии / contract / scope-fix или явно попросил `show` — остановись на артефакте;
- иначе **сразу продолжай выполнение текущей задачи** под этим контрактом, не спрашивая отдельного разрешения.

## Long-Form Contract (On Explicit Request)

```md
## Original task
<verbatim quote>

## Understood intent
<1-3 sentences>

## Context anchors
- <source>: <why it changed the contract>

## Assumptions (not verified with user)
- ...

## Acceptance criteria

### Must (blocks completion)
- [ ] <criterion> — **Evidence**: <artifact>
  **Anchored in**: <_ops/PROJECT-PLAN.md#<section> | _ops/INTERVIEW.md#<section> | local-only — <reason>>

### Must not (anti-patterns)
- [ ] <forbidden shortcut> — **Why this would be bypassed**: <bypass mechanic>

### Verification protocol
1. <command or action>
   Expected: <observable output>
```

Лимиты: до 3 `Context anchors`, до 3 `Assumptions`, 2-4 `Must`, 0-2 `Must not`, 1-3 verification-шагов.
