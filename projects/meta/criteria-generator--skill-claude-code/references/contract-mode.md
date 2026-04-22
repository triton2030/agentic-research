# Contract Mode — Процесс

Default-режим `criteria-generator`. Четыре чекпоинта. По умолчанию этот режим заканчивается не паузой, а связкой: `receipt -> короткое напоминание из _ops -> немедленное продолжение работы`.

## 1. Capture

Процитируй задачу пользователя дословно.

Артефакт: точная цитата для финального блока `Original task`.

## 2. Discover — сначала план + предпочтения, потом local

Читай upstream-карту **до** локального контекста.

### 2.1. `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` — обязательно, если существуют

Переводи только те части, что материально меняют контракт:

- `Goal` из `_ops/PROJECT-PLAN.md` — durable-результат, которому задача служит.
- `Approach & Why` — выбранный подход; задача не должна его молча нарушать.
- Активный `Stage` — калибрует, что важно сейчас vs потом; открытые Steps часто становятся Must или scope-ограничениями.
- `Anti-goals` — часто становятся Must-not.
- Релевантные секции `_ops/INTERVIEW.md` — предпочтения под домен задачи. Load-bearing предпочтения конвертируются в Must или Must-not.

### 2.2. `_ops/learnings.md`

Читай только если зафиксированная дельта материально меняет критерии, запрещённые shortcuts или depth верификации.

### 2.3. Local sources

Только то, что меняет смысл «хорошо» для ЭТОЙ задачи. Маршрут:
- ближайший `projects/{category}/...` если затронута конкретная линия артефакта;
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`;
- `README*`, `docs/`;
- активные instruction-surfaces (system prompts, folder instructions, local skills, hooks, validators);
- свежий git state.

Читать всё «на всякий случай» — это bypass.

Если `_ops/PROJECT-PLAN.md` нет — отметь и продолжай со **слабым strategic grounding**. Предпочитай тоньше контракт, а не выдумывать якоря.

Если есть план без `INTERVIEW.md` — используй план осторожно, отметь, что контракт без preference-слоя.

Расширенная маршрутизация — в [discovery-map.md](discovery-map.md).

### Выход шага

- Буллеты `<source>: <one-line takeaway that changed your understanding>`.
- `Understood intent` — 1-3 предложения, что именно будущий агент должен достичь.
- `Unknowns` — недостающие факты, которые могли бы материально изменить критерии.

Если пользователь предложил solution path — явно классифицируй: `accept`, `narrow`, `reject`. Не наследуй путь молча.

## 3. Draft → Adversarial → Gate (один цикл)

Draft минимальный видимый контракт, который ещё блокирует плохую работу → атакуй → Gate. Повторяй до прохождения.

### Draft

Три бакета:

- **`Must`** — условия, блокирующие завершение если отсутствуют. Каждый несёт `Evidence:` (наблюдаемый артефакт) и `Anchored in:` (секция PROJECT-PLAN / INTERVIEW или `local-only — <reason>`).
- **`Must not`** — запрещённые shortcuts, которые сделали бы работу «готовой», оставаясь слабой. Добавляй, только когда bypass и вероятен, и не закрыт уже Must.
- **`Verification protocol`** — 1-3 конкретных действия, упорядоченных по highest-signal proof.

Для кодовых задач — behavior-first `Must`: наблюдаемое изменение поведения, regression proof, no-regression. Implementation details фиксируются, только когда они load-bearing и observable.

Каждый критерий — короткий. Предпочитай одно предложение до `Evidence:`; пересекающиеся обязанности объединяй. Бюджеты: 2-4 `Must`, 0-2 `Must not`, 1-3 verification-шагов. Превышай, только если тоньше контракт материально ослабит корректность.

### Adversarial pass

Представь ленивого агента, который пытается формально удовлетворить каждый критерий плохой работой. Для каждого найденного bypass — усиливай или объединяй критерии. Один сильный критерий, закрывающий несколько related bypasses, лучше нескольких узких.

Подбери 2-5 модов под тип задачи из [failure-modes.md](failure-modes.md). Не применяй все 13.

### Gate — Семь Правил

Прогони каждый критерий через:

1. **Anchor traceability** — строка `Anchored in:` указывает на конкретную секцию `_ops/PROJECT-PLAN.md` (Goal, Stage, Anti-goal) или `_ops/INTERVIEW.md` (секция предпочтений). Если ни один якорь не применим — `Anchored in: local-only — <reason>`. Молчаливого отсутствия нет.
2. **Observable** — рецензент проверяет evidence, а не утверждение.
3. **Unambiguous** — два внимательных читателя рассудили бы одинаково.
4. **Non-bypassable** — слабый агент не пройдёт мелкой работой.
5. **Minimal** — удаление критерия материально повышает риск провала.
6. **Non-overlapping** — не защищено другим критерием.
7. **On-trajectory** — `Must` служит чему-то на пути к Goal. `PROJECT-PLAN.md` используется как **whitelist**, а не wishlist: если критерий защищает гипотетическую будущую потребность, через которую траектория не проходит — отбрасывай. Знание плана — license писать **меньше** критериев, не больше.

Любой критерий, не прошедший проверку, — переписать или удалить. Два критерия, защищающих один failure mode → оставить более короткий / сильный.

### EVPI-gate на вопросы

Спрашивай, только если ответ материально меняет контракт. Если один точечный вопрос материально изменит scope, acceptance threshold или irreversible-решение — задай сейчас (предпочитай `AskUserQuestion`). Иначе продолжай и запиши unresolved-точку как assumption с префиксом `[EVPI-would-ask]`.

Не контрабанди нерешённую архитектуру в `Must`. Если контракт зависит от решения, где живёт правило (AGENTS.md / skill / hook / validator) — остановись и откатывай в `system-architect`.

Артефакт: финальный набор критериев, прошедший Success Criteria, плюс ответы пользователя или финализированный `Assumptions`.

## 4. Emit — Компактный Receipt + Короткое Напоминание Из `_ops`

Не вываливай полный augmented-prompt в чат. Держи draft (intent, anchors, assumptions, Must / Must-not / Verification) в execution-плане — применишь как жёсткий контракт в следующем execution-ходе по умолчанию.

Emit'и только компактный receipt:

```md
## Criteria receipt

- Intent: <одно предложение — что будущий агент должен достичь>
- Anchors: <_ops путь + секция, ...> | weak-grounding — no `_ops/` | local-only — <reason>
- Refs applied: <references/<file>.md#<anchor>, ...>
- Draft: <M> Must · <N> Must-not · <K> Verify
- Gate: <7/7 passed | weak — <reason>> · bypasses closed: <короткие теги или счётчик>
- Assumptions: <счётчик + теги | —>
- User-proposed path: <accept | narrow | reject>
- Ready: <yes | blocked — <reason>>
```

Правила:

- Receipt ≤ 9 строк.
- Пропускай любую строку, чьё поле пустое, не применимо или `—` — **кроме** `Refs applied:`. Она обязательна: пустая = receipt невалиден.
- `Refs applied:` перечисляет references, реально прочитанные в этой сессии (минимум `contract-mode.md`; добавляй `failure-modes.md` если прогонял adversarial по конкретным модам; `discovery-map.md` если сверялся по типу проекта).
- `User-proposed path` — только если путь был предложен пользователем.
- Receipt — доказательство, что Discover, Draft, Adversarial, Gate состоялись **и что references реально использованы**. Это не сам контракт.
- Не расширяй receipt в отчёт. Если тянет добавить narrative — сожми.

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

Emit'и только когда пользователь ответил `show` или явно попросил полный контракт. Никогда по умолчанию.

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

Если `Context anchors`, `Assumptions` или `Must not` пустые — опусти заголовок.

Лимиты: до 3 `Context anchors`, до 3 `Assumptions`, 2-4 `Must`, 0-2 `Must not`, 1-3 verification-шагов. Выше — только если короче контракт материально ослабит корректность.

Предпочитай one-line критерии. Избегай multi-clause буллетов и мини-эссе.
