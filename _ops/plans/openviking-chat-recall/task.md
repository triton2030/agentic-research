---
эпик: "самостоятельный experiment: openviking-chat-recall"
режим: Wayfinding
kind: task
создано: 2026-08-21
---

# OpenViking Wiki для chat-recall

## Цель

Превратить полный статический snapshot `_ops/chat-recall/` в удобную агентам
библиотеку знаний штатным OpenViking Compile и официальным LLM Wiki Skill.
Исходные holders остаются неизменяемым evidence; Wiki — производная,
пересобираемая и неканоническая поверхность чтения.

Работа живёт в самостоятельном `experiments/openviking-chat-recall/` и не
расширяет root `_ops/GOAL.md` до runtime-эксперимента.

## Критерии успеха

- Эксперимент воспроизводимо поднимает pinned stock OpenViking и импортирует
  frozen snapshot всех holders без правки исходников.
- Compile использует официальный LLM Wiki Skill и создаёт навигационный
  `index.md` плюс страницы нужных типов: `entity/`, `concept/`, `method/`,
  `comparison/`, `analysis/`; пустые типы не создаются ради симметрии.
- Семантически одинаковые позиции объединены. Для повторяющейся позиции Wiki
  хранит число отдельных записей, первую и последнюю фиксацию, изменение
  позиции и противоречия со ссылками на источники.
- На проверяемой выборке recurrence-метаданные сходятся с holders вручную;
  непроверенная модельная оценка не считается доказательством.
- Matched retrieval-проверка сравнивает исходные holders, существующий Graphiti
  и OpenViking Wiki по одинаковым вопросам: корректность, chronology,
  применение актуальной позиции, число чтений, токены и время.
- Полный backfill запускается только после pilot-verdict; принятый full snapshot
  имеет inventory receipt без пропусков и дубликатов источников.
- Агент может отвечать по-русски. Английский текст stock Wiki допустим только
  если pilot не показывает материального ухудшения поиска или применения.

## Не входит

- Realtime capture, hooks, watcher или подмена `1chat-recall`.
- Удаление, редактирование или архивирование `_ops/chat-recall/**`.
- Собственная knowledge architecture вместо штатного LLM Wiki Skill.
- Переписывание OpenViking prompts до falsifying stock-pilot.
- Публикация исходных цитат, персональных данных или WebDAV наружу.
- Возобновление незаконченного Graphiti ingest; Graphiti здесь только baseline.

## Решающий вопрос Wayfinding

Может ли stock OpenViking собрать из русского корпуса библиотеку, которая
одновременно:

1. правильно сводит повторы и chronology;
2. сохраняет проверяемый provenance;
3. помогает агенту находить и применять позицию лучше или дешевле исходных
   holders и Graphiti?

Если хотя бы одно условие не подтверждено, полный backfill не начинается:
фиксируется предел и выбирается минимальная следующая развилка — уточнить
compile reason, добавить русский output или отказаться от класса решения.

## Последовательность

1. **Pilot runtime.** Изолированный pinned OpenViking, frozen inventory,
   официальный LLM Wiki Skill, representative corpus и compile receipt.
2. **Pilot audit.** Ручная сверка recurrence/chronology и matched retrieval на
   заранее зафиксированных вопросах.
3. **Переходный verdict.** Только evidence переводит план из Wayfinding в
   Execution либо закрывает эксперимент с отрицательным результатом.
4. **Full backfill.** В режиме Execution компилируется весь frozen corpus,
   проверяется inventory и повторяется held-out retrieval audit.
5. **Handoff.** Принятая библиотека получает короткий agent route; source of
   truth и способ полного rebuild остаются явными.

## Условия входа и stop rules

- Используется локальная конфигурация без внешней публикации и без секретов в
  репозитории.
- Upstream version, commit, официальный Skill и compile reason фиксируются в
  receipt: новая версия не подменяет измеряемый runtime по ходу pilot.
- AGPL-3.0 учитывается как граница эксперимента: код OpenViking не переносится
  в иной продуктовый owner без отдельного решения.
- Если stock output не позволяет проверить recurrence или противоречия,
  модельный текст не принимается как «библиотека знаний» только за гладкость.

## Происхождение требований

- Outcome, static backfill, Luna Max и проверка удобства агентам — решение
  владельца: `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- Неизменяемость holders и их роль source-bound evidence — `_ops/AGENTS.md`,
  разделы `chat-recall/` и «Красные линии».
- Штатная IA и правила дедупликации — официальный OpenViking LLM Wiki Skill:
  `examples/compile/ov-compile-skills/llm-wiki/SKILL.md`.
- Graphiti baseline и его текущий незавершённый scope —
  `_ops/plans/graphiti-codex-finish/{task,status,context}.md`.
