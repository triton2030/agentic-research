# Task File Lifecycle — Процесс

Default-режим `task-contract`. Семь чекпоинтов. Артефакт — файл `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` + компактный receipt в чат. Во время обсуждения скил держит task context; во время редактирования сверяет работу с критериями; после выполнения задачи вызывается снова для closeout того же файла: отметки, фактический evidence, verification result, закрытие.

## 1. Locate / Create

Найди путь к файлу задачи под активный Step из `_ops/PROJECT-PLAN.md`:

- `NN` — двузначный номер фазы, совпадает со Stage в плане.
- `<slug>` фазы — kebab-case имени Stage (владеет `project-strategy`). Не переименовывай.
- `MM` — двузначный порядковый номер task внутри фазы (по порядку появления Step'ов).
- `<slug>` задачи — kebab-case формулировки Step.

Правила:

- Если Step уже помечен `[~]` и файл есть — открываешь для обновления.
- Если это completion closeout — найди существующий task-файл по текущей задаче. Не создавай новый task-файл под «закрытие» или «итог».
- Если это обсуждение или правка вокруг уже активной задачи — сначала найди текущий task-файл активной фазы; если их несколько, выбери ближайший по названию / Stage / текущему ask и назови ambiguity в receipt.
- Если Step `[ ]` / `[~]` и файла нет — создаёшь.
- Если папки `_ops/plans/phase-NN-<slug>/` нет, хотя Stage в плане есть — **стоп**. Это рассинхронизация планового слоя, владелец `project-strategy`. Emit: *«Папка фазы отсутствует. Вызываю `project-strategy` для синка, потом возвращаюсь»*.
- Ни одной папки сам не создавай. Файл создаёшь только внутри уже существующей папки фазы.

Артефакт шага: абсолютный путь к task-файлу.

## 2. Discover — сначала план + предпочтения, потом local

Читай upstream-карту **до** локального контекста.

### 2.0. Plan-Anchor Gate (блокирующий — перед всем)

Task якорится хотя бы в одном элементе `_ops/PROJECT-PLAN.md` (Goal / активный Stage / Step / Anti-goal) или релевантной секции `_ops/INTERVIEW.md`?

- **Да** — продолжай с 2.1.
- **Нет, задача тривиальная** (однострочник, typo, renaming, очевидный local fix) — скил не нужен, skip.
- **Нет, задача значимая** — **блок**. Emit: *«Task не якорится в PROJECT-PLAN. Вызываю `project-strategy` для обновления плана, потом возвращаюсь»*. Не draft'и критерии, не пиши файл. `local-only` как обход запрещён.

### 2.1. `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` — обязательно

Переводи только те части, что материально меняют контракт:

- `Goal` — durable-результат, которому задача служит.
- `Approach & Why` — выбранный подход; задача не должна его молча нарушать.
- Активный `Stage` — калибрует, что важно сейчас vs потом; открытые Steps часто становятся Must или scope-ограничениями.
- `Anti-goals` — часто становятся Must-not.
- Релевантные секции `_ops/INTERVIEW.md` — load-bearing предпочтения конвертируются в Must или Must-not.

### 2.2. `_ops/learnings.md`

Читай только если зафиксированная дельта материально меняет критерии, запрещённые shortcuts или depth верификации.

### 2.3. Local sources

Только то, что меняет смысл «хорошо» для ЭТОЙ задачи. Маршрут:
- ближайший `projects/{category}/...` если затронута конкретная линия артефакта;
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`;
- `README*`, `docs/`;
- активные instruction-surfaces;
- свежий git state.

Читать всё «на всякий случай» — это bypass. Расширенная маршрутизация — в [discovery-map.md](discovery-map.md).

### Выход шага

- Буллеты `<source>: <one-line takeaway>`.
- `Understood intent` — 1-3 предложения.
- `Unknowns` — недостающие факты, которые могли бы материально изменить критерии.
- `Task context` — existing task-file | planned task | Stage-only | ambiguous.

Если пользователь предложил solution path — явно классифицируй: `accept`, `narrow`, `reject`. Не наследуй путь молча.

## 3. Task Context Guard — Даже Если Только Обсуждаем

Если пользователь обсуждает задачу, подход, текст, статус или риск, но ещё не просит явной правки:

- Назови, к какому task-файлу это относится; если файла нет, назови активный Stage / planned task и нужен ли файл.
- Проверь, меняет ли обсуждение scope, assumption, Must / Must-not, verification depth или blocker.
- Если меняет контракт текущей задачи — обнови task-файл в существующих секциях.
- Если новый preference signal — не записывай сам, handoff в `project-strategy`.
- Если не меняет ничего, emit короткое: «это относится к <task>; критерии пока не меняются».

Task-context note:

```md
## Task-context note

- Context: <task-file | Stage/planned task | ambiguous>
- Applies to: <scope | assumption | Must | Must-not | verification | none>
- Action: <updated task-file | no file change | handoff to project-strategy | needs task file>
```

## 4. Draft → Adversarial → Gate / Criteria Check

Draft минимальные секции task-файла, атакуй, Gate. Повторяй до прохождения.

### Draft — три секции task-файла

**`Цель`** — одна строка, durable-результат этой задачи. Не процесс («настроить X»), а состояние («X настроен и …»).

**`Подшаги`** — 2-5 конкретных шагов **действия** внутри этой задачи. Маркеры `[ ] / [~] / [x]`. Это не пересказ плана, это реальные шаги. Подшаги — помощь исполнителю, не контракт.

**`Критерии приёмки`** — три бакета:

- **`Must`** — условия, блокирующие завершение если отсутствуют. Каждый несёт `Evidence:` (наблюдаемый артефакт) и `Anchored in:` (секция PROJECT-PLAN или INTERVIEW, либо `local-only — <reason>`).
- **`Must not`** — запрещённые shortcuts. Добавляй, только когда bypass и вероятен, и не закрыт уже Must.
- **`Verification protocol`** — 1-3 конкретных действия, упорядоченных по highest-signal proof.

Для кодовых задач — behavior-first `Must`: наблюдаемое изменение поведения, regression proof, no-regression. Implementation details — только когда load-bearing и observable.

Каждый критерий короткий, одно предложение до `Evidence:`. Пересекающиеся обязанности объединяй. Бюджеты: 2-4 `Must`, 0-2 `Must not`, 1-3 verification-шагов.

### Adversarial pass

Представь ленивого агента, формально удовлетворяющего каждый критерий плохой работой. Для каждого bypass — усиливай или объединяй. Один сильный критерий, закрывающий несколько related bypasses, лучше нескольких узких.

Подбери 2-5 модов под тип задачи из [failure-modes.md](failure-modes.md). Не применяй все 13.

### Gate — Семь Правил

Прогони каждый критерий через:

1. **Anchor traceability** — строка `Anchored in:` указывает на конкретную секцию `_ops/PROJECT-PLAN.md` (Goal, Stage, Step, Anti-goal) или `_ops/INTERVIEW.md`. Два уровня:
   - **Task-level anchor (обязательный)** — задача целиком якорится в PLAN или INTERVIEW. Проверяется Plan-Anchor Gate (§2.0). Без него скил не работает.
   - **Criterion-level anchor** — каждый Must несёт свой якорь. Предпочтительно — секция PLAN / INTERVIEW. Fallback `Anchored in: local-only — <reason>` допустим **только для критериев о самом коде** (формат, читаемость данного diff'а, локальный инвариант, naming convention этого модуля) — не для задачи целиком. `local-only` как защита задачи без plan-якоря — нарушение Gate.
   - Якорь `Anchored in:` **не** ссылается на другой task-файл и не на путь внутри `_ops/plans/`: этот слой эфемерный, внешние ссылки запрещены.
2. **Observable** — рецензент проверяет evidence, а не утверждение.
3. **Unambiguous** — два внимательных читателя рассудили бы одинаково.
4. **Non-bypassable** — слабый агент не пройдёт мелкой работой.
5. **Minimal** — удаление критерия материально повышает риск провала.
6. **Non-overlapping** — не защищено другим критерием.
7. **On-trajectory** — `Must` служит чему-то на пути к Goal. `PROJECT-PLAN.md` используется как **whitelist**, а не wishlist: если критерий защищает гипотетическую будущую потребность, через которую траектория не проходит — отбрасывай. Знание плана — license писать **меньше** критериев, не больше.

Любой критерий, не прошедший проверку, — переписать или удалить. Два критерия, защищающих один failure mode → оставить более короткий / сильный.

### EVPI-gate на вопросы

Спрашивай, только если ответ материально меняет контракт. Если один точечный вопрос материально изменит scope, acceptance threshold или irreversible-решение — задай (предпочитай `AskUserQuestion`). Иначе продолжай и запиши unresolved как assumption с префиксом `[EVPI-would-ask]`.

Не контрабанди нерешённую архитектуру в `Must`. Если контракт зависит от решения, где живёт правило — остановись и откатывай в `instruction-layer`.

### Criteria Check — Когда Уже Идёт Правка

Если пользователь редактирует текст, код или артефакт внутри активной задачи:

- Сверь diff/текст/артефакт с текущими Подшагами, Must / Must-not и Verification protocol.
- Отметь, какие критерии затронуты и какие пока блокируют closeout.
- Если критерий уже выполнен наблюдаемым evidence, можно отметить `[x]`; если evidence слабый, оставь `[ ]`.
- Если текущая работа показывает, что критерий устарел, обнови task-файл через обычный Draft → Gate цикл.

Criteria-check receipt:

```md
## Task criteria check

- Path: `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`
- Checked: <substeps/Must/Must-not/verification touched>
- Passing: <brief>
- Blocking: <brief | none>
- Next: <continue | update contract | closeout | handoff>
```

## 5. Commit — Записать Task-Файл

Запиши файл по пути из шага 1. Формат:

```markdown
# <Название задачи — та же формулировка, что Step в PROJECT-PLAN.md>

## Цель
<одна строка — durable-результат этой задачи>

## Подшаги
- [ ] <действие 1>
- [ ] <действие 2>
- [ ] <действие 3>

## Критерии приёмки

### Must
- [ ] <критерий> — **Evidence**: <artifact>
  **Anchored in**: `_ops/PROJECT-PLAN.md#<section>` | `_ops/INTERVIEW.md#<section>` | `local-only — <reason>`

### Must not
- [ ] <shortcut> — **Why this would be bypassed**: <bypass mechanic>

### Verification protocol
1. <command or action>
   Expected: <observable output>
   Actual: <optional closeout result>
```

Если нет `Must not` или нет явных verification-шагов — опускай заголовок.

**Жёсткие правила файла:**

- Никаких секций кроме `Цель`, `Подшаги`, `Критерии приёмки`. Лишние Context / Assumptions / Notes — в receipt или в чат, не в файл.
- `Anchored in:` ссылается **только** на PROJECT-PLAN или INTERVIEW — никаких путей внутри `_ops/plans/`, никаких других task-файлов. Слой эфемерный.
- Если файл уже существует — обновляешь, не переписываешь целиком, если секции `Подшаги` / `Критерии приёмки` реально изменились. Чекбоксы `[x]` для закрытых подшагов сохраняешь.
- В closeout дописываешь результат только внутри существующих секций: `[x]` у Подшагов / Must, уточнённый `Evidence`, optional `Actual:` под verification. Новые секции «Итог», «Notes», «Changelog» не добавляй.
- Никаких комментариев «added by task-contract», «generated on <date>». Файл — живой артефакт.

## 6. Emit — Компактный Receipt

Не вываливай содержимое файла в чат. Emit короткий receipt:

```md
## Task-file receipt

- Path: `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`
- Intent: <одно предложение — что будущий агент должен достичь>
- Anchors: <_ops путь + секция, ...> | weak-grounding — no `_ops/` | local-only — <reason>
- Refs applied: <references/<file>.md#<anchor>, ...>
- Draft: <M> Must · <N> Must-not · <K> Verify
- Gate: <7/7 passed | weak — <reason>> · bypasses closed: <теги или счётчик>
- Assumptions: <счётчик + теги | —>
- User-proposed path: <accept | narrow | reject>
- Ready: <yes | blocked — <reason>>
```

Правила:

- Receipt ≤ 10 строк.
- Пропускай пустые строки, **кроме** `Path:` и `Refs applied:` — обязательны.
- `Refs applied:` перечисляет ref-файлы, реально прочитанные в этой сессии (минимум `task-file-lifecycle.md`; добавляй `failure-modes.md` если прогонял adversarial по конкретным модам; `discovery-map.md` если сверялся по типу проекта).
- `Anchors:` — ссылки на PROJECT-PLAN / INTERVIEW. Путь к самому task-файлу **не** якорь (он downstream).
- Receipt — доказательство, что Locate, Discover, Draft, Adversarial, Gate состоялись **и что references реально использованы**.

После receipt — 1-3 строки простым русским: что именно из `_ops/` важно держать в голове при выполнении (напр. «Держим курс на Goal X, активный Stage — Y, anti-goal Z исключает N»). И сразу возвращаешь агента к задаче — скил работу не блокирует.

Если пользователь явно попросил только критерии (criteria-only / scope-fix без выполнения) — после записи файла и receipt остановись, не продолжай задачу.

## 7. Completion Closeout — После Выполнения

Когда работа по задаче завершена, `task-contract` вызывается повторно и обновляет **тот же** task-файл.

Что сделать:

- Перечитать task-файл, текущий diff / git evidence, релевантный chat context и результаты verification.
- Отметить `[x]` у выполненных Подшагов и Must. Если критерий не выполнен, оставить `[ ]` и назвать blocker в receipt.
- Уточнить `Evidence:` до фактического артефакта, если изначально там был только ожидаемый тип evidence.
- Добавить `Actual:` к verification-шагам, когда это помогает будущему агенту увидеть, что реально проверено.
- Если closeout показывает, что фаза или план изменились по факту, не править PROJECT-PLAN самому: emit handoff в `project-strategy` с коротким evidence summary.

Запрещено:

- Закрывать задачу только финальным сообщением в чат.
- Создавать отдельный task-файл «закрытие задачи».
- Добавлять новые секции в task-файл.
- Перемещать файл в `done/` без явного запроса пользователя или repo-rule.

Closeout receipt:

```md
## Task-file closeout

- Path: `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`
- Closed: <yes | no — blocker>
- Evidence updated: <brief>
- Verification: <passed | partial | not run — reason>
- Plan signal: <none | handoff to project-strategy — reason>
```

## Long-Form (On Explicit Request)

Если пользователь отвечает `show` — emit полный контент task-файла в чат. Никогда по умолчанию.
