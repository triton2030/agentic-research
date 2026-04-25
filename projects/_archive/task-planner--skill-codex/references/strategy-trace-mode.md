# Strategy-Trace Mode

Явно-запрашиваемый режим компактной upstream-alignment проверки. Проверяет: служит ли конкретный ask / план / draft Goal и активному Stage из `_ops/PROJECT-PLAN.md`.

Триггеры: явный `strategy-trace`, «проверь alignment», «быстрый drift-check», «следует ли это ещё плану». Требует конкретный артефакт на вход.

## Success Criteria

1. **Chain-shaped** — ходит от Goal → активный Stage (или Anti-goal) → local implication → observed target.
2. **Anchored** — каждый шаг цепочки цитирует `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md` или проверяемый артефакт. Без свободно-плавающих утверждений.
3. **Compact** — обычно 3-4 шага цепочки + один verdict. Не расширяй в полный контракт.
4. **Decisive** — ровно один verdict: `aligned`, `partial`, `drift`, `unknown`.
5. **Actionable** — один самый маленький следующий шаг, снижающий drift или неопределённость.
6. **Read-only** — не изобретай стратегию, архитектуру или `Must`.

## Read Path

1. Цитируй конкретный target: текущий ask, план, draft, короткое summary артефакта.
2. Читай `_ops/PROJECT-PLAN.md` (Goal + активный Stage) и `_ops/INTERVIEW.md` (релевантная preference-секция под домен target'а).
3. `_ops/learnings.md` — только если зафиксированная дельта влияет на выбор между `partial`, `drift`, `unknown`.
4. Читай только конкретный local-артефакт. Не расширяйся в repo-scan.

## Emit

Верни ровно этот шейп:

```md
## Trace target
<verbatim quote or named artifact>

## Strategic chain
1. Goal: <durable outcome that matters here>
   **Anchored in**: _ops/PROJECT-PLAN.md#Goal
2. Active stage or preference: <current stage, anti-goal, or load-bearing preference>
   **Anchored in**: _ops/PROJECT-PLAN.md#<stage> | _ops/INTERVIEW.md#<section>
3. Local implication: <what this target must do or avoid if it is aligned>
   **Anchored in**: <_ops path + section | local artifact>
4. Observed target: <what the ask, plan, or draft is actually trying to do>
   **Anchored in**: <user quote | artifact>

## Verdict
<aligned | partial | drift | unknown>

## Why
- <1-2 evidence-backed bullets>

## Do now
- <one short next move>
```

Если шаг 4 не добавляет информации сверх `Trace target` — опусти.

Если `_ops/PROJECT-PLAN.md` или `_ops/INTERVIEW.md` отсутствует — скажи явно: `unknown — unbootstrapped _ops`. Не создавай файлы. `Do now`: handoff в `main-strategy` на `ensure-ops.sh`, потом повторить trace.

Лимиты: 3-4 шага цепочки, до 2 `Why` буллетов, 1 `Do now`.

Не emit'и `Must`, `Must not`, verification-протокол в этом режиме.

После emit'а — один вопрос:

`Strategy trace checked. Превратить в жёсткий execution-контракт?`

## Когда не использовать

- Есть большой артефакт для аудита, реально нужен отдельный read-only artifact audit, а не compact trace.
- Пользователь явно просит `pulse-check` — это другой режим (memory probe диалога), используй [pulse-check-mode.md](pulse-check-mode.md).
- Артефакт не передан → вернуть запрос на артефакт или переключиться в `pulse-check`.

## Anti-patterns

- «Можно использовать `strategy-trace` как дешёвый full-review». Нет — он проверяет alignment памяти, не качество артефакта.
- «Можно назвать aligned, не цитируя цепочку в `_ops/`». Нет — verdict без anchors — театр.
- Расширение в полный контракт. Нет — это read-only.
