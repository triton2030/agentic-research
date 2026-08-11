---
description: "Узкий практический профиль коротких descriptions для автоматического вызова skill по состоянию, возникшему во время длинной работы."
read-before-edit:
  - authoring-canon.md
  - research-mid-trajectory-trigger-descriptions-2026-08.md
edit-after-edit: []
---

# Mid-Trajectory Trigger Descriptions

Этот файл дополняет [`authoring-canon.md`](authoring-canon.md) только для одного
случая: skill должен автоматически выбираться **по ходу длинной работы**, когда
необходимость стала видна из промежуточного результата, новой фазы или
выведенной подзадачи. Evidence и ссылки принадлежат
[`research-mid-trajectory-trigger-descriptions-2026-08.md`](research-mid-trajectory-trigger-descriptions-2026-08.md).

## Целевой Механизм

Нужный эффект выглядит так:

```text
тип текущей работы
  + вход в определённую смысловую фазу
  + наблюдаемый признак, что фаза уже началась
  → semantic match короткого description
  → automatic invocation нужного skill
```

Это не hook на имя команды и не match только исходного prompt. Skill заранее
«подписан» на **смысловой момент работы**: агент начал диагностику, получил
candidate findings, перешёл от реализации к визуальной проверке, дошёл до
материального решения или собирается объявить completion.

Description владеет условием выбора. Body владеет тем, что делать после
выбора. Условие, спрятанное только в body, не может вызвать skill.

## Главный Принцип

Не убеждай агента «захотеть» skill. Дай ему короткое правило распознавания
текущего состояния:

> `Use when <observable state/event during work> makes <capability> necessary,
> even without an explicit user request. <Operation> produces <outcome>. Skip
> <nearest parent/sibling case>.`

Description должна различать три решения:

1. **use now** — условие уже наступило;
2. **not yet** — тема похожа, но нужного состояния ещё нет;
3. **use neighbor** — нужна соседняя функция.

Если фраза не меняет ни одного решения, удалить её.

## Сначала Определи Желаемый Момент

До wording заполни пять полей:

```text
Work type:       какая более широкая работа идёт?
Target phase:    к какой части работы агент только что приступил?
Entry evidence:  что уже видно в context и доказывает вход в эту фазу?
Skill delta:     что отдельный skill должен изменить именно сейчас?
Not yet / next:  какой похожий момент ещё слишком ранний или принадлежит соседу?
```

Пример:

```text
Work type:       frontend implementation
Target phase:    post-implementation visual review
Entry evidence:  UI уже запущен и доступен для просмотра
Skill delta:     screenshot-grounded design verdict
Not yet / next:  не во время написания компонентов и не для causal bug diagnosis
```

Если `Entry evidence` нельзя назвать, желаемый момент пока определён только
интуитивно. Такое description будет срабатывать по теме, а не в нужной фазе.

### Перевод Момента В Description

Для phase-conditioned invocation используй более точную форму:

```text
Use when [work type] has reached [target phase], evidenced by [observable
artifact/state], even without an explicit user request. [Operation] produces
[skill delta]. Do not use before [not-yet boundary] or for [nearest neighbor].
```

`evidenced by` не обязательно писать буквально. Важно, чтобы признак находился
в текущем контексте и модель могла сопоставить его с description.

## Что Ставить В Начало

Первая фраза одновременно называет **состояние и функцию**:

```text
Use when implementation or verification reveals broken, flaky, slow, or
unexplained behavior and the cause is not yet established.
```

Это сильнее, чем:

```text
Helps diagnose software problems and improve reliability.
```

Во втором варианте есть тема, но нет момента вызова. В первом есть наблюдаемый
event, граница знания и операция. Front-load обязателен: runtime может сократить
хвост metadata.

## Четыре Детали Candidate

### 1. Наблюдаемое Состояние

Пиши то, что уже присутствует в рабочем контексте:

- `a test or tool result reveals...`;
- `the current workflow has produced candidate findings...`;
- `work reaches a material decision or completion claim...`;
- `continuing now requires a missing input / derived subtask...`;
- `the active approach is exhausted or ineffective...`.

Не писать скрытую психологию модели: `when uncertain`, `when it feels useful`,
`periodically`, `for important work`. Эти признаки нельзя надёжно проверить.

### 2. Точная Capability И Delta

Называй операцию и наблюдаемый результат, а не широкую тему:

```text
Re-check the active route against the stated goal and name the next necessary
move.
```

Тематические слова вроде `video`, `security`, `planning` объединяют соседние
skills. Операция и output их различают.

### 3. Implicit Route

Если skill должен срабатывать без прямой просьбы, скажи это рядом с условием:

```text
...even if the user did not request a trajectory review.
```

Это калиброванная assertiveness. Не писать `always use whenever possible`:
такая настойчивость поднимает fire rate вместе с ложными вызовами.

### 4. Одна Ближайшая Граница

Добавляй exclusion только для реального parent/sibling collision:

```text
Do not use as the entry point for a full repository scan.
```

Не превращай description в каталог соседних skills. Один настоящий near-miss
полезнее полного routing menu.

## Готовая Форма

```text
Use when [observable event/state] during [broader work] makes [specific
capability] necessary, even without an explicit user request. [Operation]
produces [observable outcome]. Skip [nearest false-positive state].
```

Стартовый candidate — примерно 40–60 английских слов, если все четыре детали
действительно нужны. Это исследовательский setting, не норматив. Сокращай до
минимума, который сохраняет `use now / not yet / neighbor`; не дополняй текст до
числа слов.

## Примеры

### Проверка Траектории

Слабое:

```text
Use for reviews, planning, and long complex work.
```

Сильнее:

```text
Use when a long task reaches a material decision, evidence conflicts, or a
completion claim, even if the user did not request review. Re-check the active
route against the stated goal and name the next necessary move. Skip routine
status updates and local implementation checks.
```

### Валидация Находок

Слабое:

```text
Validates security findings.
```

Сильнее:

```text
Use when the current workflow has produced candidate findings and must decide
which are valid, even without an explicit validation request. Return evidence
for accepted and rejected findings. Do not use as the entry point for a full
repository scan.
```

### Диагностика

Слабое:

```text
Use for bugs and failures.
```

Сильнее:

```text
Use when implementation or verification reveals broken, flaky, slow, or
unexplained behavior and the cause is not yet established. Separate symptom
from cause and return discriminating evidence before any fix. Skip applying an
already-proven correction.
```

## Eval Именно Для Позднего Автовызова

Обычный список одношаговых prompts проверяет initial routing, но не этот
контракт. Нужны trajectory cases, где trigger появляется после старта.

### Набор

Начать с 20 сценариев:

- 2 direct positives — capability явно нужна с первого сообщения;
- 6 mid-trajectory positives — event появляется только после чтения, tool
  result, diff или phase transition;
- 2 restart positives — то же состояние после нового turn или compaction;
- 4 premature negatives — тот же positive до наступления события;
- 3 parent/sibling near-misses;
- 3 surface-overlap traps — та же тема и лексика, другая функция.

Половина positives должна обходиться без слов из name/description. Запускать с
полным реальным каталогом, в чистых sessions, по три повтора. Черновые правки
делать на 60% cases; выбирать версию по оставшимся 40%.

### Наблюдаемый Trace

Для каждого сценария заранее записать:

- событие, после которого skill становится применим;
- окно вызова — например, ближайшие 0–2 model samples/actions;
- что считается вызовом: реальное чтение `SKILL.md` или runtime `Skill` call;
- какой parent/sibling не должен загрузиться;
- downstream результат, который skill должен изменить.

Не засчитывать слова «я учёл skill» без trace загрузки.

### Метрики

- **late-trigger recall** — доля applicable trajectories с вызовом в окне;
- **premature-trigger rate** — вызовы до события;
- **near-miss false-positive rate**;
- **neighbor accuracy**;
- **trigger latency** — actions между событием и загрузкой;
- **task delta** — изменился ли результат после вызова;
- **adherence** — выполнен ли body; считать отдельно от trigger.

## Как Чинить По Провалу

- **Пропущен после события** — перенести event + capability в первую фразу.
- **Вызван раньше времени** — добавить `after X exists` или точную phase
  boundary.
- **Перехватывает sibling** — назвать различающую операцию/output; при
  необходимости добавить один exclusion.
- **Ловит тему, но не функцию** — заменить topic nouns на required input,
  operation и outcome.
- **Хвост обрезан** — удалить фон; guard перенести ближе к началу.
- **Fire rate вырос, task success — нет** — не усиливать wording; проверить
  body, timing и необходимость skill.
- **После compaction/turn match нестабилен** — не раздувать prose; вынести
  обязательный момент в checkpoint, hook или orchestrator.

Менять одну причину за итерацию. Иначе непонятно, какая часть description
изменила поведение.

## Когда Description — Не Тот Слой

Description остаётся вероятностным model routing. Используй явный lifecycle
механизм, если:

- пропуск создаёт невосстановимый, safety- или money-critical риск;
- skill обязан запускаться в каждом цикле или строго после конкретного event;
- обязательна цепочка parent → child skills;
- каталог недоступен после нужной границы;
- eval показывает нестабильный recall, который wording не исправляет.

Тогда правильный инструмент — workflow checkpoint, hook, orchestrator,
dependency graph или explicit invocation. Хорошая prose не заменяет control
flow.

## Три Уровня Надёжности

### 1. Чистый Semantic Trigger — Default

Каталог остаётся доступен модели, а description называет phase + evidence +
delta. Никакой hook не выбирает skill. Это полностью отвечает цели смыслового
автовызова, но остаётся вероятностным.

Использовать, если пропуск восстанавливаем и trajectory eval показывает
приемлемые recall, timing и false positives.

### 2. Semantic Re-Evaluation Checkpoint

Если модель знает descriptions, но в длинной работе забывает снова свериться с
каталогом, checkpoint не должен хардкодить имя skill. Он требует только
операцию:

```text
At a material phase transition, re-evaluate the available skill descriptions
against the current task state before continuing.
```

Checkpoint возвращает внимание к routing surface, а нужный skill всё ещё
выбирается **по смыслу текущей работы**. Это предпочтительный fallback для
нестабильного late recall.

### 3. Explicit Phase → Skill Mapping

Hook или orchestrator напрямую вызывает конкретный skill после события. Это
детерминированнее, но уже не semantic selection.

Использовать только когда пропуск неприемлем или runtime не даёт модели снова
увидеть каталог. Не начинать с этого слоя, если цель — обучить смысловой выбор.

## Acceptance

Description готово, когда:

- первая фраза различает state + capability без чтения body;
- positive может возникнуть только по ходу работы и всё равно вызывает skill;
- похожий pre-event case не вызывает его раньше;
- ближайший parent/sibling не перехватывается;
- хвост можно удалить без потери главного trigger;
- реальные traces показывают timing и task delta, а не только fire rate.
