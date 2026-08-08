# Контракты Файлов - `1goal`

`1goal` владеет двумя стратегическими surfaces проекта:

- `_ops/GOAL.md` - outcome-first contract: что делаем, in scope, NOT in scope,
  definition of done, stop rules.
- `README.md` - narrative context / on-ramp: что это за проект, зачем он так
  устроен, какие файлы читать первыми.

Все execution details, task statuses, task links, archive/reconcile и substeps
живут в `_ops/plans/**` через `1planning`. Instruction rules живут в
`AGENTS.md` / `CLAUDE.md` / `_ops/rules/**` через `1instruction-shaping`.

## Карта Владельцев

- `_ops/GOAL.md` -> `1goal`.
- `README.md` -> `1goal`.
- `_ops/plans/**/task-*.md` -> `1planning`.
- `AGENTS.md` / `CLAUDE.md` / subtree instructions -> `1instruction-shaping`.
- Goal-цитата в `AGENTS.md` / `CLAUDE.md` -> прямой sync после изменения
  `_ops/GOAL.md#Что делаем`.
Если правка хочет записать и strategic contract, и execution detail в один файл,
это owner drift: раздели смысл и пиши только в owner surface.

## `_ops/GOAL.md`

Назначение: короткий project charter, который fresh agent читает перед
нетривиальной работой.

Фиксированные разделы:

- **Что делаем** - 1-2 предложения про основной outcome.
- **In scope** - 3-7 проверяемых пунктов.
- **NOT in scope** - 3-7 пунктов.
- **Definition of done** - проверяемые условия завершения.
- **Stop rules** - когда остановиться, эскалировать или вернуться к выбранному
  подходу.

Работает, когда:

- fresh agent понимает scope, anti-scope и критерии завершения без устного
  контекста;
- closeout можно сверить против `Definition of done`;
- `AGENTS.md` / `CLAUDE.md` Goal-цитата синхронизирована с `Что делаем`;
- документ остаётся одной страницей и не превращается в narrative или task list.

Дрейфует, когда:

- появляются мотивационные абзацы -> README;
- появляются substeps, task lists, statuses, commands, evidence -> `1planning`;
- появляются rule-form правила "every X must Y" -> `1instruction-shaping`;
- durable preference или red line записывается как интерпретация, а не как
  подтверждённая цель.

## `README.md`

Назначение: одна страница narrative context для outside reader, fresh agent и
самого пользователя при re-orientation.

Работает, когда:

- cold reader понимает, что это за проект и зачем он существует;
- fresh agent понимает narrative/approach/on-ramp без повторного интервью;
- README не дублирует scope/done из GOAL и не хранит active status;
- ссылки ведут к устойчивым owner surfaces, а не к moving task files.

Дрейфует, когда:

- повторяет `GOAL.md` sections;
- превращается в project-status registry;
- содержит task files, phase folders, commands, evidence rows или closeout;
- хранит operational rules вместо `AGENTS.md` / `_ops/rules/**`;
- становится длиннее одной страницы без явной причины.

## Goal-Цитата

После правки `_ops/GOAL.md#Что делаем` обнови 3-5 строк essence в root
`AGENTS.md` и `CLAUDE.md` в том же ходе. Это прямое действие `1goal`: не отдельный
handoff и не routing через удалённый system owner.

Если изменение затрагивает graph-bearing claim/heading, `1md-graph` даёт
structural holders. Green graph не доказывает semantic sync: открой target
quote и сверь смысл вручную.
