# PROJECT-ROADMAP

## Goal

Главный контракт проекта живёт в `_ops/GOAL.md`.

Этот файл держит только текущий режим движения: как сейчас работать с
контрактом, knowledge, user-said, findings, interviews и plans.

## Когда стратегия сработала

Новая сессия без устного контекста понимает, что это не работа от дорожной карты.
Она выбирает релевантные файлы из `knowledge/`, `_ops/interviews/` и
`_ops/findings/` под текущую просьбу, не восстанавливает старые поверхности и
не превращает эксперимент в backlog.

## Текущие активные фронты

**mcp-self-sufficiency** (`_ops/plans/mcp-self-sufficiency/`): ⚠️ **Active.**
- Цель: сделать `md-mcp` самодостаточным продуктом (27 public tools, self-sufficient descriptions, CLI-equivalent reduced).
- Skills становятся overlay (учат **когда применять / как интерпретировать**, не дублируют tool spec).
- Phases: A (backend expand) → B1-B4 (skills rewrite в parallel) → C (final sweep).
- См. [README](plans/mcp-self-sufficiency/README.md).

**knowledge-description-cleanup** (`_ops/plans/knowledge-description-cleanup/`):
- ⚠️ 27 из 37 файлов в `knowledge/` без frontmatter `description` (surfaced via `md_orient`). Task created not started.

**Archived 2026-05-21**:
- `md-tools-refactor` — Refactor complete: backend unified, MCP 0.5.x, 19 tools, smoke 24/24. См. `_ops/findings/2026-05-21-md-refactor-editorial-verification.md`.
- `md-skills-cross-check` — Cross-check skills consistency после refactor (4 parallel subagents, 6 edits).

## Как здесь работать

Опираемся на лёгкую форму полигона: содержательные знания лежат в `knowledge/`,
сырые цитаты пользователя капчатся в `_ops/user-said/YYYY-MM-DD.md` через
`1user-said`, длинные вопросы к пользователю собираются во временных
`_ops/interviews/**`, актуальные проблемы до задач лежат в `_ops/findings/`,
а `_ops/plans/**` используется только по явному запросу для активной сложной
работы.

Фокус не в расширении каталога и не в закрытии стадий, а в качестве решений:
агент не пишет skill или instruction “из головы”, если в репо есть релевантное
знание. Старые task-файлы и spiral notes не являются источником истины после
перехода в режим полигона.

`_ops/findings/` остаётся временным слоем только для реальных актуальных
проблем: файл проблемы не является задачей или решением, пока отдельный
стратегический шаг не решит, что с ним делать.

Этот файл больше не обязан давать цепочку стадий. Он нужен как короткий
верхнеуровневый ориентир: зачем существует проект и как не спутать его с
планировщиком задач.
