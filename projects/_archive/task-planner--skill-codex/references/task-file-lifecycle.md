# Task File Lifecycle — Процесс

Default-режим `task-planner`. Семь чекпоинтов. Артефакт — файл `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md` + компактный receipt в чат. После первого receipt — сразу продолжать выполнение текущей задачи, скил работу не блокирует. Во время обсуждения скил держит task context; во время редактирования сверяет работу с критериями; после выполнения вызывается снова для closeout того же файла: отметки, фактический evidence, verification result, закрытие.

## 1. Locate / Create

Найди путь к файлу задачи внутри активной фазы из `_ops/PROJECT-PLAN.md`:

- `NN` — двузначный номер фазы, совпадает со Stage в плане.
- `<slug>` фазы — kebab-case имени Stage (владеет `main-strategy`). Не переименовывай.
- `MM` — двузначный порядковый номер task внутри фазы.
- `<slug>` задачи — kebab-case формулировки текущего ask / рабочей задачи.

Правила:

- Если файл под тот же ask уже есть — открываешь для обновления.
- Если это completion closeout — найди существующий task-файл по текущей задаче. Не создавай новый task-файл под «закрытие» или «итог».
- Если это обсуждение или правка вокруг уже активной задачи — сначала найди текущий task-файл активной фазы; если их несколько, выбери ближайший по названию / Stage / текущему ask и назови ambiguity в receipt.
- Если файла под этот ask нет — создаёшь следующий `task-MM-<slug>.md` в папке активной фазы.
- Если папки `_ops/plans/phase-NN-<slug>/` нет, хотя Stage в плане есть — **стоп**. Это рассинхронизация планового слоя, владелец `main-strategy`. Emit: *«Папка фазы отсутствует. Вызываю `main-strategy` для `ensure-ops.sh --sync`, потом возвращаюсь»*.
- Ни одной папки сам не создаёшь. Файл создаёшь только внутри уже существующей папки фазы.

Артефакт шага: абсолютный путь к task-файлу.

## 2. Discover — сначала план + предпочтения, потом local

Читай upstream-карту **до** локального контекста.

### 2.0. Plan-Anchor Gate (блокирующий — перед всем)

Сначала проверь, что `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` существуют. Если нет — **блок**: *«Проект не bootstrapped в `_ops`. Вызываю `main-strategy` для `ensure-ops.sh`, потом возвращаюсь»*. Не создавай task-файл, не draft'и критерии, не используй `local-only`.

Task якорится хотя бы в одном элементе `_ops/PROJECT-PLAN.md` (Goal / активный Stage / Anti-goal) или релевантной секции `_ops/INTERVIEW.md`?

- **Да** — продолжай с 2.1.
- **Нет, задача тривиальная** (однострочник, typo, renaming, очевидный local fix) — скил не нужен, skip.
- **Нет, задача значимая** — **блок**. Emit: *«Task не якорится в PROJECT-PLAN. Вызываю `main-strategy` для обновления плана, потом возвращаюсь»*. Не draft'и критерии, не пиши файл. `local-only` как обход запрещён.

### 2.1. `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` — обязательно

Переводи только те части, что материально меняют контракт:

- `Goal` — durable-результат, которому задача служит.
- `Approach & Why` — задача не должна его молча нарушать.
- Активный `Stage` — что важно сейчас vs потом; его описание и `Зачем` часто становятся scope-ограничениями.
- `Anti-goals` → Must-not.
- Релевантные секции `INTERVIEW.md` — load-bearing предпочтения → scope, Must, Must-not или verification depth.

`INTERVIEW.md` consumption receipt для себя: 0-3 релевантные preference constraints. Каждая должна быть либо переведена в контракт, либо явно отброшена как not applicable. Если текущий диалог даёт новый, изменённый или конфликтующий preference signal, **не пиши task-файл** до handoff в `main-strategy` на обновление `INTERVIEW.md`.

`PROJECT-PLAN.md` здесь не optional context, а source of truth. Критерии выводятся из утверждённого плана, не из локального угадывания.

### 2.2. `_ops/learnings.md`

Только если зафиксированная дельта материально меняет критерии или запрещённые shortcuts.

### 2.3. Local sources

Активно читай всё, что может пригодиться для ЭТОЙ задачи: соседние task-файлы, живые skill contracts, `projects/{category}/...`, `AGENTS.md`, `CLAUDE.md`, `README*`, `docs/`, active instruction-surfaces, git state и локальные артефакты. Фильтр один: source должен materially изменить scope, Must, Must-not, evidence, verification или blocker. Читать всё «на всякий случай» — bypass.

Если при чтении видно, что task-layer messy (противоречивые task-файлы, непонятный active task, criteria не бьются с Stage, closeout не сходится с evidence), вызови subagent `смит`, если он доступен, для plan-critique. Передай ему только raw task/plan snippets и вопрос «где сломается handoff?». Не передавай желаемый ответ и не проси переписать план. Если `смит` недоступен, зафиксируй blocker и handoff вверх, не симулируй внешний review.

Расширенная маршрутизация — в [discovery-map.md](discovery-map.md).

### Выход шага

- Буллеты `<source>: <one-line takeaway>`.
- `Understood intent` — 1-3 предложения.
- `Unknowns` — что могло бы материально изменить критерии.
- `Task context` — existing task-file | planned task | Stage-only | ambiguous.

Если пользователь предложил solution path — классифицируй: `accept`, `narrow`, `reject`.

## 3. Task Context Guard — Даже Если Только Обсуждаем

Если пользователь обсуждает задачу, подход, текст, статус или риск, но ещё не просит явной правки:

- Назови, к какому task-файлу это относится; если файла нет, назови активный Stage / planned task и нужен ли файл.
- Проверь, меняет ли обсуждение scope, assumption, Must / Must-not, verification depth или blocker.
- Если меняет контракт текущей задачи — обнови task-файл в существующих секциях.
- Если это новый preference signal — не записывай сам, handoff в `main-strategy`.
- Если не меняет ничего, emit короткое: «это относится к <task>; критерии пока не меняются».

Task-context note:

```md
## Task-context note

- Context: <task-file | Stage/planned task | ambiguous>
- Applies to: <scope | assumption | Must | Must-not | verification | none>
- Action: <updated task-file | no file change | handoff to main-strategy | needs task file>
```

## 4. Draft → Adversarial → Gate / Criteria Check

Draft минимальные секции task-файла, атакуй, Gate. Повторяй до прохождения.

### Draft — три секции task-файла

**`Цель`** — одна строка, durable-результат этой задачи. Не процесс («настроить X»), а состояние («X настроен и …»).

**`Подшаги`** — 2-5 конкретных шагов **действия** внутри этой задачи. Маркеры `[ ] / [~] / [x]`. Это не пересказ плана, а реальные шаги для исполнителя.

**`Критерии приёмки`** — три бакета:

- **`Must`** — условия, блокирующие завершение если отсутствуют. Каждый несёт `Evidence:` (наблюдаемый артефакт) и `Anchored in:` (секция PROJECT-PLAN / INTERVIEW или `local-only — <reason>`).
- **`Must not`** — запрещённые shortcuts. Добавляй, только когда bypass и вероятен, и не закрыт уже Must.
- **`Verification protocol`** — 1-3 конкретных действия, highest-signal proof.

Бюджеты: 2-4 `Must`, 0-2 `Must not`, 1-3 verification-шагов.

### Adversarial pass

Представь ленивого агента, пытающегося формально удовлетворить каждый критерий плохой работой. Усиливай или объединяй. Подбери 2-5 модов из [failure-modes.md](failure-modes.md).

### Gate — Семь Правил

Каждый `Must` обязан пройти:

1. **Anchor traceability** — `Anchored in:` явный. Два уровня:
   - **Task-level anchor (обязательный)** — задача целиком якорится в PLAN или INTERVIEW. Проверяется Plan-Anchor Gate (§2.0).
   - **Criterion-level anchor** — предпочтительно секция PLAN / INTERVIEW. Fallback `Anchored in: local-only — <reason>` допустим **только для критериев о самом коде** (формат, читаемость данного diff'а, локальный инвариант) — не для задачи целиком.
   - Якорь `Anchored in:` **не** ссылается на другой task-файл и не на путь внутри `_ops/plans/`: этот слой эфемерный, внешние ссылки запрещены.
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
# <Название задачи — краткая формулировка текущего ask>

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

- Никаких секций кроме `Цель`, `Подшаги`, `Критерии приёмки`. Context / Assumptions / Notes — в receipt или в чат, не в файл.
- `Anchored in:` ссылается **только** на PROJECT-PLAN или INTERVIEW — никаких путей внутри `_ops/plans/`, никаких других task-файлов.
- Если файл уже существует — обновляешь, не переписываешь целиком. Чекбоксы `[x]` для закрытых подшагов сохраняешь.
- В closeout дописываешь результат только внутри существующих секций: `[x]` у Подшагов / Must, уточнённый `Evidence`, optional `Actual:` под verification. Новые секции «Итог», «Notes», «Changelog» не добавляй.
- Никаких комментариев «added by task-planner», «generated on <date>». Файл — живой артефакт.

## 6. Emit — Компактный Receipt

Не вываливай содержимое файла в чат. Emit короткий receipt:

```md
## Task-file receipt

- Path: `_ops/plans/phase-NN-<slug>/task-MM-<slug>.md`
- Intent: <одно предложение — что будущий агент должен достичь>
- Anchors: <_ops путь + секция, ...>
- Interview applied: <0-3 preference constraints | none relevant>
- Refs applied: <references/<file>.md#<anchor>, ...>
- Draft: <M> Must · <N> Must-not · <K> Verify
- Gate: <7/7 passed | weak — <reason>> · bypasses closed: <теги или счётчик>
- Assumptions: <счётчик + теги | —>
- User-proposed path: <accept | narrow | reject>
- Ready: <yes | blocked — <reason>>
```

Правила:

- Receipt ≤ 10 строк.
- Пропускай пустые строки, **кроме** `Path:`, `Interview applied:` и `Refs applied:` — обязательны.
- `Refs applied:` перечисляет ref-файлы, реально прочитанные в этой сессии (минимум `task-file-lifecycle.md`; добавляй `failure-modes.md` если прогонял adversarial; `discovery-map.md` если сверялся по типу проекта).
- `Anchors:` — ссылки на PROJECT-PLAN / INTERVIEW. Путь к самому task-файлу **не** якорь.

После receipt — 1-3 строки простым русским: что из `_ops/` важно держать в голове при выполнении. И сразу возвращаешь агента к задаче.

Если plan gate заблокирован или `_ops` unbootstrapped — вместо file write и project-link-receipt emit короткий blocked handoff в `main-strategy`.

## 7. Completion Closeout — После Выполнения

Когда работа по задаче завершена, `task-planner` вызывается повторно и обновляет **тот же** task-файл.

Что сделать:

- Перечитать task-файл, текущий diff / git evidence, релевантный chat context и результаты verification.
- Отметить `[x]` у выполненных Подшагов и Must. Если критерий не выполнен, оставить `[ ]` и назвать blocker в receipt.
- Уточнить `Evidence:` до фактического артефакта, если изначально там был только ожидаемый тип evidence.
- Добавить `Actual:` к verification-шагам, когда это помогает будущему агенту увидеть, что реально проверено.
- Если closeout показывает, что фаза или план изменились по факту, не править PROJECT-PLAN самому: emit handoff в `main-strategy` с коротким evidence summary.

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
- Plan signal: <none | handoff to main-strategy — reason>
```

## Long-Form (On Explicit Request)

Если пользователь явно просит `show` / только критерии / scope-fix без выполнения — emit содержимое task-файла в чат. Никогда по умолчанию.
