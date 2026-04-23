# Pulse-Check Mode

Явно-запрашиваемый режим dialog-time memory probe. Проверяет, держит ли текущая сессия Goal и активный Stage в рабочей памяти — **не** alignment артефакта (это `strategy-trace`).

Триггеры: явный `pulse-check`, «пульс», «проверь память», «ещё помнишь о чём мы». Артефакт не берёт.

## Success Criteria

1. **Cold recall honest** — блок recall формулируется **до** чтения `_ops/` в этом вызове и не переписывается после verify.
2. **Anchored specifically** — каждая actual-строка цитирует `_ops/PATH#section`, а не просто `_ops/`.
3. **Three-step trace** — ровно 3 шага: `goal → active stage → this dialog`. Два — недобор, четыре — это уже `strategy-trace`.
4. **Decisive verdict** — ровно одно из `remembered`, `drift`, `forgotten`. Никакого `partial`.
5. **Size-bounded** — видимый выход ≤ 15 строк.
6. **Read-only** — никаких записей, новой стратегии, предложений «починить» `_ops/`.

## Алгоритм (cold recall → verify → compare)

Порядок **load-bearing**. Emit блок recall **до** чтения `_ops/` в этом вызове. Не переписывай recall после verify.

### 1. Recall — из session-памяти, без чтения `_ops/`

- `Goal`: одно предложение, что ты сейчас считаешь целью проекта.
- `Active stage`: одно предложение, что ты считаешь активным Stage.
- `This dialog`: одно предложение, над чем этот диалог реально работает сейчас.

### 2. Verify — прочитай `_ops/PROJECT-PLAN.md`

- `Goal`: короткая цитата из `_ops/PROJECT-PLAN.md#Goal`.
- `Active stage`: короткая цитата из Stage, который лучше всего совпадает с диалогом (с `[~]` или самый ранний `[ ]`).

### 3. Trace — компактная 3-шаговая цепочка

`goal → active stage → this dialog`. Каждый шаг несёт `Anchored in:`. Не достраивается — скажи явно.

### 4. Verdict — ровно одно из

- **`remembered`** — recall совпадает с actual, диалог чисто сидит под активным Stage.
- **`drift`** — recall частично прав, но диалог ушёл от активного Stage или игнорирует Anti-goal / load-bearing preference.
- **`forgotten`** — recall материально перепутал Goal или Stage, либо не смог ничего существенного вспомнить без чтения.

### 5. Delta

Только когда verdict не `remembered`. 1-3 строки: что recall перепутал и почему это важно.

## Emit

Верни ровно этот шейп:

```md
## Pulse check

### Recalled
- Goal: <one line>
- Active stage: <one line>
- This dialog: <one line>

### Actual
- Goal: "<quote>" — _ops/PROJECT-PLAN.md#Goal
- Active stage: "<quote>" — _ops/PROJECT-PLAN.md#<stage-heading>

### Trace
<goal> → <active stage> → <this dialog>

### Verdict
<remembered | drift | forgotten>

### Delta
<only if not remembered — 1-3 lines>
```

Видимый выход ≤ 15 строк. Если `_ops/PROJECT-PLAN.md` нет — `forgotten — strategic map unavailable` и стоп. Не создавай отсутствующий файл — это территория `main-strategy`.

Не emit'и `Must`, `Must not`, verification-протокол.

После emit'а — один вопрос:

`Pulse checked. Зафиксировать это task-файлом (task mode) или прогнать artifact-alignment trace (strategy-trace mode)?`

## Когда не использовать

- Есть конкретный артефакт для оценки → используй `strategy-trace`.
- Сессия только началась и диалоговой памяти почти нет.
- Пользователь передал артефакт под `pulse-check` → переключиться на `strategy-trace`.

## Anti-patterns

- «`pulse-check` без cold recall — ок, просто прочитаю `_ops/` сначала». Нет — probe тестирует, что сессия реально держит, а не что ты можешь вывести из файлов.
- «`partial` достаточно для pulse-check». Нет — три-значный verdict намеренный.
- «Recall может быть paraphrase of `_ops/`». Нет — текстовое совпадение с файлом — это reread, не memory-check.
