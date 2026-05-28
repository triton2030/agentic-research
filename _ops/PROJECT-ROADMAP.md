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

**Archived 2026-05-22**:
- `md-mcp-to-cli-refactor` — Refactor complete: Node MCP removed, 29 tools mapped to Python CLI `md`, library/CLI split (`navigator/` + `md_cli/`), envelope golden tests, stateless transactions, and Claude/Codex skills migrated. См. `_ops/findings/2026-05-22-mcp-refactor-closeout.md`.
- `knowledge-description-cleanup` — descoped по запросу пользователя при смене активного фронта на md-mcp-to-cli-refactor.

**Archived 2026-05-21**:
- `md-tools-refactor` — Refactor complete: backend unified, MCP 0.5.x, 19 tools, smoke 24/24. См. `_ops/findings/2026-05-21-md-refactor-editorial-verification.md`.
- `md-skills-cross-check` — Cross-check skills consistency после refactor (4 parallel subagents, 6 edits).
- `mcp-self-sufficiency` — MCP v0.6.0 with 27 self-sufficient tools (11 new wrappers + merged extract + mutating guards). 16 SKILL.md (Claude+Codex×8) переписаны в overlay style. Smoke 37/37. Phases A → B1-B4 (parallel) → C done.

## Как здесь работать

Опираемся на лёгкую форму полигона: содержательные знания лежат в `knowledge/`,
длинные слова пользователя автоматически капчатся в
`_ops/user-said/YYYY-MM-DD.md` глобальным `UserPromptSubmit` hook-ом, длинные
вопросы к пользователю собираются во временных
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
