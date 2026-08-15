---
description: "Source-bound форензика 25 promoted skills Matt Pocock: формулировки, порядок, размеры, отрицательное пространство и границы переноса в 1skill-shaping."
read-before-edit:
  - authoring-canon.md
edit-after-edit: []
---

# Research: Как Matt Pocock Пишет Skills

Срез на **15 августа 2026** по
`mattpocock/skills@8b78b531ab965735c5dc74f6f7a219e1e37326df`.
Тип: Research & Evidence Report. Это evidence, не новый authoring canon и не
принятая правка `1skill-shaping`.

## Вопрос

Нужно восстановить не тему skills Pocock, а его способ письма:

- какие формулировки он использует для определения, команды, условия,
  ветвления, причины, границы и завершения;
- в каком порядке располагает эти функции;
- сколько символов реально несут его skills и активные композиции;
- что он систематически не пишет;
- что из этого можно проверять как кандидат для нашего `1skill-shaping`.

Owner-сигнал:
`../../../_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:18-22`.
Владелец отдельно потребовал сохранить отчёт, чтобы будущая сессия не изучала
стиль заново.

## Корпус И Метод

Первичный корпус:

- repository:
  [mattpocock/skills](https://github.com/mattpocock/skills);
- commit:
  [8b78b531](https://github.com/mattpocock/skills/tree/8b78b531ab965735c5dc74f6f7a219e1e37326df);
- promoted denominator: ровно 25 путей из
  [`.claude-plugin/plugin.json`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/.claude-plugin/plugin.json);
- non-promoted `misc/`, `in-progress/` и `deprecated/` исключены;
- длина: `wc -m`, Unicode-символы;
- body: файл после первого frontmatter-блока;
- wording/absence: чтение 25 тел плюс exact-pattern probes;
- active path: сумма реально адресованных skill/reference-файлов, а не размер
  entrypoint.

Важная воспроизводимая граница: простой поиск всех `skills/**/SKILL.md` даёт
35 файлов и неверный denominator. Promoted set определяется plugin manifest и
совпадает с правилом в `CLAUDE.md` репозитория.

Дополнительные независимые чтения:

| Поток | Метод | Продукт |
|---|---|---|
| Claude Opus 5 | Полная read-only форензика корпуса | Формулировки, counts, отрицательное пространство, сравнение с `1skill-shaping` |
| Deep agent 1 | Rhetorical Move-Step Analysis | Коммуникативные moves и их порядок |
| Deep agent 2 | Change-Amplification & Deep-Module Analysis | Owners, composition и стоимость будущего изменения |
| Deep agent 3 | Competing Causal Hypotheses | Отделение длины от active obligations, routing, gates и внешней популярности |

Opus: `requested_model=opus` · `requested_effort=xhigh` ·
`resolved_model=claude-opus-5` ·
`session_id=84784dff-dea0-4ef0-8c76-9568aeb4f952`. Transport обрезал длинный
ответ; видимый terminal-текст восстановлен из нативной session history.

## Короткий Ответ

Метод Pocock нельзя свести к «каждый skill короче N символов».

Его более точная конструкция:

1. Постоянная selection-поверхность мала.
2. Skill платит телом только после вызова.
3. Ветка раскрывает одну нужную ветвь.
4. Повторяемое поведение и понятие имеют одного owner.
5. Каждая оставшаяся фраза выполняет action, route, boundary, gate,
   composition или causal функцию.
6. Церемониальная проза удаляется; операционные запреты остаются.

Краткость — следствие малой активной нагрузки и высокой функциональной
плотности, а не самостоятельный числовой закон.

## Количественный Профиль

### 25 promoted `SKILL.md`

| Метрика | Весь файл | Body без frontmatter |
|---|---:|---:|
| Минимум | 147 | 28 |
| Медиана | 3 536 | 3 355 |
| Среднее | 4 616 | 4 401 |
| Максимум | 11 777 | 11 509 |
| Сумма | 115 404 | 110 018 |

Самые длинные тела:

| Skill | Символов body |
|---|---:|
| `wayfinder` | 11 509 |
| `ask-matt` | 11 232 |
| `writing-for-agents` | 10 734 |
| `teach` | 9 318 |
| `diagnosing-bugs` | 8 702 |

Следствие: абсолютная краткость не описывает корпус. Четыре promoted skills
длиннее 9 000 символов body.

### Invocation surface

- 14 skills: `disable-model-invocation: true` — индексом служит человек.
- 11 skills: model-invoked.
- Их 11 model-facing `description` вместе: 2 195 символов.
- Средний model-facing `description`: около 200 символов.

Это главный короткий always-loaded слой. User-invoked body не становится
model-context до ручного вызова.

### Три Бюджета

| Бюджет | Что считать | Почему |
|---|---|---|
| Entry | `description` или микро-router | Платится до раскрытия |
| Direct active | Вызванный skill плюс непосредственно названные skill owners | Реальные одновременно доступные обязательства |
| Transitive | Достигнутые reference/branch-файлы | Платится только по условию пути |

Проверенные суммы полных файлов:

| Путь | Entry | Direct active | Возможное дальнейшее раскрытие |
|---|---:|---:|---:|
| `grill-me → grilling` | 147 | 2 003 | — |
| `grill-with-docs → grilling + domain-modeling` | 245 | 5 318 | conditional domain files |
| `implement → tdd + code-review` | 433 | 10 515 | до 14 210, если достигнуты оба TDD reference |
| `writing-for-agents → SKILL-MECHANICS` | 10 884 | 13 519 | — |

Микро-entrypoint не доказывает малый active context. Composition управляет
моментом и ownership раскрытия, а не магически удаляет текст.

## Грамматика Формулировок

| Функция | Наблюдаемая форма | Эффект |
|---|---|---|
| Определение | `**Термин** — одна операционная фраза` или `X is Y` | Термин определяется один раз и дальше заменяет повтор |
| Команда | Голый императив с конкретным объектом | Действие начинается без persona и motivational setup |
| Условие | `When/If/Once X, сделай Y` | Condition стоит до действия или рядом с ним |
| Ветка | `**вопрос/симптом** → /skill или [FILE]. результат` | Discriminator виден до общих правил |
| Причина | Одно предложение о конкретном провале | Rationale остаётся только если меняет выбор или compliance |
| Boundary | Короткий факт настоящего времени | Жёсткость без капслок-усилителя |
| Gate | `Done when: <наблюдаемое>` или `No X, no Y` | Блокирует преждевременный переход |
| Composition | `/skill` + его точная роль | Caller не пересказывает чужую процедуру |
| Reference | условие открытия + адрес + содержимое | Ссылка сама решает, когда читать target |

Короткие образцы:

- `Run a /grilling session.`
- `The question decides the shape.`
- `No red-capable command, no Phase 2.`

Источники:
[`prototype`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/engineering/prototype/SKILL.md),
[`diagnosing-bugs`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/engineering/diagnosing-bugs/SKILL.md),
[`grilling`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/grilling/SKILL.md).

## Порядок По Классу Skill

Единого обязательного `Context → Goal → Procedure` нет.

| Класс | Типичный порядок |
|---|---|
| Микро-orchestrator | команда → composition |
| Procedure | назначение → precondition → process → шаги → observable done → output template |
| Reference/deep module | рабочее понятие → glossary/principles → rejected framings → conditional deepening |
| Branching prototype | определение объекта → causal discriminator → branches → общие rules |
| Discipline с gates | центральный инвариант → safety → phases → gate каждого рискованного перехода |
| Router | центральная карта → основной flow → on-ramps → boundaries → standalone cases |
| Stateful world | ситуация → инвариант → структура артефактов → object types → invocation modes |

Повторяется не surface-template, а отношение:

`operational object/action → local condition → required work → transition
control → observable completion`.

## Move-Step Codebook

Rhetorical Move-Step агент вывел восемь функций:

| Move | Функция |
|---|---|
| `M0` | Selection pointer |
| `M1` | Operational frame/definition |
| `M2` | Action |
| `M3` | Conditional route |
| `M4` | Boundary, scope или ownership |
| `M5` | Gate, wait или completion |
| `M6` | Composition/reference |
| `M7` | Embedded causal rationale |

Genre grammar:

`M0 + { M6 | M2 → (M4/M3) → M2* → M5 → (M6/M2) |
(M1 ↔ M2) → M7 → (M3 ↔ M2)* → (M4/M6) → M5 }`.

Скобки означают optionality, не обязательные разделы. Heading, отрицание и
imperative mood сами по себе не являются move: кодируется функция clause.

## Отрицательное Пространство

Exact-pattern scan 25 promoted bodies:

- uppercase `IMPORTANT|CRITICAL|MANDATORY|MUST|ALWAYS|NEVER`: 0;
- persona openings `You are a/an/the…|Act as|Your role is|Your task is`: 0;
- из generic headings
  `Overview|When to use|Prerequisites|Examples|Success criteria|Checklist|Limitations|Troubleshooting|Notes`
  найден ровно один `## Notes` в `wayfinder`;
- frontmatter использует только `name`, `description`,
  `disable-model-invocation` и `argument-hint`;
- code examples редки;
- generic tool-failure/retry boilerplate и ответные word limits не образуют
  повторяемой формы;
- trigger description не пересказывается отдельным обязательным
  `When to use`-разделом тела;
- итоговый summary не является обязательным жанровым элементом.

Коррекция прежнего chat-отчёта: там было сказано «service headings — ноль».
Повторный exact scan при записи нашёл один `## Notes`. Остальная перечисленная
группа — 0.

Что не отсутствует:

- `don't`: 44 exact body occurrences;
- `never`: 27 exact-word body occurrences, включая `Never`;
- `do not`: 8 case-insensitive body occurrences.

Отрицательное пространство Pocock — не отсутствие запретов. Он удаляет
церемониальное усиление, но сохраняет operational boundaries.

## Как Он Объясняет

Отдельное `Why` встречается редко. Объяснение обычно встроено:

- в definition, если оно задаёт рабочий объект;
- в causal discriminator, если от причины зависит branch;
- рядом с запретом, если модель по умолчанию выберет опасный ход;
- рядом с completion criterion, если возможен преждевременный переход.

Механику, которую модель способна исполнить напрямую, он часто не мотивирует.
Причина оплачивается только против наблюдаемого или ожидаемого дефолтного
сбоя.

## Ownership И Composition

Change-Amplification агент проверил пять типичных будущих изменений:

- interview/frontier меняется в `grilling`, wrappers не переписываются;
- prototype branch меняется у `prototype`;
- red gate меняется у `diagnosing-bugs`;
- `implement` владеет orchestration, `tdd` и `code-review` — своей механикой;
- invocation policy меняется в `SKILL-MECHANICS` и затрагивает только
  соответствующие entrypoints.

Классификация:

- `grill-me` — shallow alias с отдельной человеческой достижимостью;
- `grill-with-docs` — composition adapter;
- `implement` — thin orchestrator;
- `prototype`, `grilling`, `diagnosing-bugs`,
  `writing-for-agents` — deep modules.

Более сильная structural-метрика:

> не «сколько символов», а «сколько владельцев надо менять при изменении одного
> поведения».

## Заявленный Метод Против Корпуса

Подтверждено корпусом:

- context pointer как условный адрес;
- две нагрузки: context load и human cognitive load;
- front-loaded leading word;
- one trigger per branch;
- progressive disclosure по ветке;
- co-location связанного смысла;
- completion criterion;
- single source of truth;
- sentence-level no-op deletion.

Основные тексты:
[`writing-for-agents/SKILL.md`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/writing-for-agents/SKILL.md)
и соседний
[`SKILL-MECHANICS.md`](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/writing-for-agents/SKILL-MECHANICS.md).
В корпусе нет `references/` по этому адресу: `SKILL-MECHANICS.md` лежит рядом
с `SKILL.md`.

Продуктивные противоречия:

1. `writing-for-agents` называет sprawl failure mode, но четыре promoted тела
   длиннее 9 000 символов.
2. Он предпочитает positive target, но сам широко применяет отрицание как
   hard boundary.
3. `diagnosing-bugs` остаётся длинным монолитом, хотя объявленный branching
   test допускает дальнейшее disclosure.

Вывод: правила соблюдаются как критерии решения, не как абсолютная
стилистическая чистота.

## Конкурирующие Причины Эффективности

| Hypothesis | Статус после корпуса |
|---|---|
| `H1`: чем меньше raw characters, тем сильнее | Строгая версия отвергнута |
| `H2`: важнее число одновременно активных обязательств | Описательно поддержана |
| `H3`: важнее front-loading и локальная адресуемость | Описательно поддержана |
| `H4`: важнее composition и single ownership | Самая сильная structural support |
| `H5`: сложные workflows держат observable gates | Поддержана на phase-heavy skills |
| `H6`: популярность объясняет бренд, distribution или полезность задач | Не устранена |

Популярность — evidence практической востребованности набора, но не
различающий тест текстовых механизмов.

## Сравнение С `1skill-shaping`

Срез локального live package на 15 августа 2026:

- main `SKILL.md`: 9 670 символов;
- все Markdown package files: 34 958;
- installed main совпадает с tracked owner
  [`skills/shared/1skill-shaping/portable/SKILL.md`](../../../skills/shared/1skill-shaping/portable/SKILL.md).

Total package size не равен active load: reference должен считаться только на
фактически достигаемом пути.

### Сохранить У Нас

- active obligations вместо fixed character cap;
- source/provenance и различение fact/inference;
- owner approval;
- trigger probe голой пользовательской фразой;
- cognitive audit с наблюдаемым следом;
- behavioral acceptance и comparator;
- локальные Product Frame / Principles gates.

### Кандидаты От Pocock

- выбирать форму по функции skill, а не по обязательному surface-template;
- делать первую содержательную строку operator-bearing;
- показывать branch до общих rules;
- признать micro-router отдельным жанром;
- использовать pretrained concept как compression device;
- держать condition возле command;
- считать entry, active obligations и transitive package отдельно;
- проверять sentence-level no-op удалением целого предложения.

Самый сильный кандидат на проверку: обязательная поверхность
`Контекст → Цель → …`. Corpus поддерживает наличие context/goal-смысла, но не
единые одноимённые разделы и не универсальный порядок.

Это candidate, не разрешение менять `1skill-shaping`.

## Реконструированный Метод Pocock

1. Назвать точный момент вызова и consumer: человек или модель.
2. Выбрать жанр: router, procedure, reference, branching workflow или
   discipline.
3. Определить центральный рабочий объект одной фразой.
4. Найти существующее сильное понятие из известной практики; выдуманный термин
   требует собственной цены определения.
5. Первой строкой дать command, operational definition или blocking invariant.
6. Если есть branches — показать discriminator раньше общих rules.
7. Писать команды прямыми императивами.
8. Ставить condition до действия или непосредственно рядом.
9. Оставлять rationale только против вероятной ошибки или неоднозначного
   выбора.
10. Закрывать рискованный переход observable gate.
11. Не пересказывать соседнюю процедуру: назвать owner и точную роль.
12. Проверить каждую clause: меняет ли она selection, action, route, boundary,
    gate, composition или completion.
13. Удалить целиком no-op clause; не «улучшать краткость» косметической
    заменой слов.
14. Измерить entry, active obligations и transitive package.
15. До глобального переноса проверить поведение на matched holdout tasks.

## Следующий Различающий Эксперимент

Matched A/B одной инструкции:

- A: минимальная функциональная версия;
- B: те же obligations, порядок, pointers и gates плюс redundant
  framing/restatement.

Фиксировать:

- точность выбора branch;
- нарушение gate;
- ложное объявление completion;
- task outcome;
- resolved model/settings;
- повторные runs, если заявляется вероятностный сдвиг.

Отдельный второй эксперимент нужен для composition:

- composed owner/router package;
- flattened body с тем же смыслом;
- одинаковая задача и acceptance.

## Что Не Доказано

- Что краткость вызвала популярность набора.
- Что Pocock-style улучшит наши target models без matched run.
- Что любой длинный skill слаб.
- Что wrapper-size описывает active context.
- Что отсутствие persona/headings само по себе причинно улучшает adherence.
- Что user-invoked reliability переносится на model-invoked selection:
  14 из 25 promoted skills индексирует человек.
- Что все правила `writing-for-agents` последовательно соблюдены его же
  корпусом.

## Что Сознательно Не Записано

- Нет universal character cap.
- Нет принятой переработки `1skill-shaping`.
- Нет полного transcript советников: сохранены их framework, evidence и
  decision-changing выводы.
- Нет второго общего guide: portable truth остаётся в
  [`authoring-canon.md`](authoring-canon.md).
- Нет текущих GitHub popularity numbers: они дрейфуют и не различают
  причинные гипотезы.

## Source Ledger

### Pocock

- [README](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/README.md)
- [Plugin manifest](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/.claude-plugin/plugin.json)
- [Writing for agents](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/writing-for-agents/SKILL.md)
- [Skill mechanics](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/writing-for-agents/SKILL-MECHANICS.md)
- [Prototype](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/engineering/prototype/SKILL.md)
- [Diagnosing bugs](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/engineering/diagnosing-bugs/SKILL.md)
- [Grilling](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/productivity/grilling/SKILL.md)
- [Codebase design](https://github.com/mattpocock/skills/blob/8b78b531ab965735c5dc74f6f7a219e1e37326df/skills/engineering/codebase-design/SKILL.md)

### Local

- [Authoring canon](authoring-canon.md)
- [Research 2026 Mar-May](research-2026-mar-may.md)
- [`1skill-shaping` tracked owner](../../../skills/shared/1skill-shaping/portable/SKILL.md)
- Owner evidence:
  `../../../_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:18-22`

## Downstream Owner

Этот файл владеет только датированным evidence snapshot.

- Portable authoring truth:
  [`authoring-canon.md`](authoring-canon.md).
- Runtime skill contract:
  tracked `1skill-shaping` owner и его shaping/approval lifecycle.
- Promotion из этого отчёта:
  отдельное решение + `1skill-shaping` cognitive audit + behavioral proof.
- Повторное исследование:
  не делать, пока не изменился source commit, target runtime/model или
  проверяемая гипотеза. Сначала читать этот snapshot и проверять только delta.
