---
name: 1goal
description: >
  Когда меняется цель, scope, done/stop или on-ramp проекта: `_ops/GOAL.md`,
  `README.md`, vision. Не для task plans или rules placement.
---

# Стратегические Документы

## Результат

`_ops/GOAL.md` и `README.md` держат две разные работы: scope contract и
context/on-ramp. Goal/scope/done/stop сформированы до записи, duplicate truth
между documents не создана, Goal-цитата в `AGENTS.md`/`CLAUDE.md` обновлена в том
же ходу. Ни один документ не стал rulebook.

Скилл владеет **мышлением и записью** двух стратегических документов.
Goal-formation, scope, NOT in scope, definition of done и stop rules — внутренняя
работа здесь, не handoff в другой skill. Мысленные инструменты — локальная часть
этого скилла.

## Вход / Пропуск

Используй, когда запрос касается: что проект делает / не делает / когда готов;
README/GOAL shape, on-ramp, vision, narrative; scope / anti-scope / stop / outcome
contract; риска, что README/GOAL хранят operational rules, task links или project
status.

Эскалируй:

- `1planning` — task-файлы, статусы, archive, reconcile;
- `1instruction-shaping` — wording и placement instruction prose;
- память проекта — durable quote / preference / red line;
- фундаментальный gap в frame до commit — остановись и сообщи; если конкретная
  скрытая premise меняет outcome/scope, передай ground-check в
  `1assumption-audit`.

## Default Path

1. Назови желаемый эффект: какой документ должен стать понятнее, точнее, честнее.
2. Проверь owner: GOAL = contract, README = context. Если смысл — правило
   поведения → AGENTS/CLAUDE / `_ops/rules/` / skill / hook. Если task/status →
   `_ops/plans/**` через `1planning`.
3. Прочитай локальную правду, меняющую границы: root/local instructions,
   существующие GOAL/README, active task/findings (если влияют на placement/stop).
4. **Думай** через мысленные инструменты (в голове, не в файле).
5. Выбери одну owner surface; смысл между документами переводи в язык целевого, не копируй.
6. Если target несёт graph frontmatter, меняется heading/claim или планируется
   move/rename, передай holders/anchors/impact в `1md-graph`. Обычная
   strategic prose правка не требует graph ceremony.
7. Пиши минимально: одна функция файла, без side-docs, rulebook-секций, task mechanics.
8. Сверь GOAL и README прямым чтением. Если риск paraphrase-дубля остаётся,
   получи bounded semantic evidence через `1md-search`, не меняя owner root.
9. Маршрутизируй последствия: GOAL outcome changed → обнови Goal-цитату в root `AGENTS.md`/`CLAUDE.md` в том же ходу; literal quote → память проекта; instruction wording → `1instruction-shaping`.

**Вход от пользователя.** После local discovery задай одним компактным блоком
только user-owned вопросы, ответы на которые materially меняют scope, anti-scope,
done или stop. Используй native user-input UI текущего runtime, если он доступен,
иначе обычный диалог; не спрашивай факты, которые можно безопасно найти в проекте.

## Document Boundaries

**`_ops/GOAL.md` — project charter.** Outcome contract. Читается fresh agent перед
нетривиальной работой; источник Goal-цитаты в `AGENTS.md`/`CLAUDE.md`.
Формат — одна страница: **Что делаем** (1-2 предложения про outcome), **In scope**
(3-7 проверяемых пунктов), **NOT in scope** (3-7), **Definition of done**
(проверяемые условия), **Stop rules**. Не: narrative, task lists, operational rules.

**`README.md` — narrative context.** Одна страница. Audience: внешний человек
(GitHub home), fresh agent для narrative-контекста, пользователь при re-orientation.
Содержит: project description, vision/motivation, approach narrative, on-ramp
(«какие файлы агенту читать первыми»). Не: scope contract → GOAL; project status,
task lists/statuses → plans; rules → AGENTS/CLAUDE или `_ops/rules/`.

## Mental Tools

В голове, не в файле (`## Inversion` как heading = театр, откат):

- **Pressure-test** — «пользователь сказал X, имеет в виду Y?».
- **Inversion** — один конкретный failure mode goal/scope.
- **Premortem** — что медленно разъест scope через полгода.
- **Adversarial self-play** — циничный скептик на draft.
- **Fresh-session check** — хватит ли GOAL + README fresh-агенту завтра без меня?

## Drift Detection

Сначала сравни тела GOAL и README: одинаковая тема допустима, одинаковая
durable scope/done truth — нет. Для неочевидной paraphrase-пары передай
`1md-search` два коротких независимо извлекаемых тезиса и project root.
`README.md` лежит в root, поэтому `_ops` не является corpus для этой сверки и
не должен получать отдельный index. `1md-search` возвращает candidates и coverage;
`1goal` решает contract-vs-context, а split/merge/move verdict принадлежит
`1ia-audit`.

## Goal-цитата в AGENTS / CLAUDE

После правки `_ops/GOAL.md#Что делаем` — обновить Goal-цитату (3-5 строк essence)
в `AGENTS.md` и корневом `CLAUDE.md` в том же ходу, не молчаливо.
Graph holders из `1md-graph`, если route был нужен, — structural checklist, но
semantic sync Goal-цитаты всё равно подтверждается прямым чтением.

## Локальные Gotchas

- README и GOAL не являются project-status registry. Задачи и статусы — task-файлы
  в `_ops/plans/**`.
- Durable red line не превращай в GOAL из интерпретации — сначала память проекта.
- `GOAL.md#Что делаем` изменение → обнови Goal-цитату в AGENTS/CLAUDE в том же ходу (не молчаливо).
- Если в README/GOAL просится правило: hot-path → AGENTS/CLAUDE, conditional rule →
  `_ops/rules/` через `1instruction-shaping`, workflow → skill, hard guardrail → hook.
- Не создавай новый файл/раздел, пока существующий strategic owner держит функцию.

## Готово Когда

- выбран один document function: contract / context;
- strategic truth не дублируется в README/GOAL (direct read; при неясной
  paraphrase — evidence packet от `1md-search`);
- README/GOAL не хранят rules (кроме собственных scope/done/stop) и project status / task links;
- In scope звучит как outcome, а не список проделанных действий;
- fresh-agent завтра понимает проект из README + GOAL без устного контекста;
- Goal-цитата в AGENTS/CLAUDE обновлена (если GOAL#Что делаем менялся);
- downstream handoff назван.

## Остановка

Остановись, когда граница документа чистая, выбранная поверхность держит одну
работу, duplicate truth предотвращена или удалена, Goal-цитата обновлена или явно
не нужна, последствия маршрутизированы.
