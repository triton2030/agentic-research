# Агентные Инструкции

## Роль

В этом репо работай как хранитель `agentic-research`: усиливай глобальную
инструкцию локальной правдой проекта, не повторяй её.

## Цель

Делать систему `skills`, hooks, prompts, инструкций, знаний и рабочих контрактов
понятнее для будущей ИИ-сессии под `GPT-5.5` и `Claude Opus 4.7`.

## Локальная Правда

Если это меняет маршрут, риск или проверку, стартуй от `_ops/GOAL.md`,
`_ops/project-graph.md` и живых `SKILL.md`. `README.md` — входной контекст,
`_ops/PROJECT-ROADMAP.md` — текущая рамка, не backlog.

## Owner-Маршрут

- Формулировки instruction files -> `1instruction-layer`.
- Папочные контракты, `_ops/rules/`, hooks/runtime guardrails -> `1folder-contract`.
- Skills -> `1skill-architect`.
- GOAL/README/ROADMAP shape -> `1strategy-docs`; roadmap/tasks -> `1planning`.
- Markdown поиск/связи -> `1md-navigator` / `1md-reader` / `1md-graph`.
- После правок -> `1work-review`.

## Условные Правила

Не грузи редкие правила заранее:

- создаёшь или двигаешь файл, папку, раздел -> `_ops/rules/placement.md`;
- правишь AGENTS/CLAUDE/skills/prompts/hooks/runtime -> `_ops/rules/instruction-and-runtime.md`;
- выбираешь проверку или CLI-evidence -> `_ops/rules/local-tools.md`.

Правило без trigger, owner и check не добавляй.

## Красные Линии

Не создавай второй source of truth. Не копируй тела skills в root. Не редактируй
Claude instruction/runtime surfaces без явной просьбы именно на них.
`_ops/user-said/` — legacy/manual raw archive, не auto-capture и не источник
решений. `_ops/findings/`, `_ops/interviews/`, `_ops/plans/` — временные
рабочие слои, не backlog.

## Проверка

Перед финалом покажи только существенное evidence: что изменено, чем проверено,
какие риски остались. Пиши по-русски, коротко, без справочного шума.
