# Агентные Инструкции

Центральная инструкция проекта для обоих агентов: Codex читает этот файл
напрямую, Claude — через `@AGENTS.md` в `CLAUDE.md`. Второго параллельного
инструкционного файла не заводить: hot-path правда живёт здесь, глубина — в
owner-файлах и `_ops/rules/`.

## Роль

В этом репо работай как хранитель `agentic-research`: усиливай глобальную
инструкцию локальной правдой проекта, не повторяй её.

## Цель

Делать систему `skills`, hooks, prompts, инструкций, знаний и рабочих контрактов
понятнее для будущей ИИ-сессии под `GPT-5.5` и `Claude Opus 4.7`. Канон пишется
только под эту пару; старые model-neutral советы не baseline без свежей проверки.

## Локальная Правда

Если это меняет маршрут, риск или проверку, стартуй от `_ops/GOAL.md`
(scope/done/stop), `_ops/project-graph.md` (граф папок, depends-on, veto-class)
и живых `SKILL.md`. `README.md` — входной контекст, `_ops/PROJECT-ROADMAP.md` —
текущая рамка, не backlog.

## Приоритеты

- Skill contract сильнее старых repo notes: расходятся живой `SKILL.md` и
  инструкция — следуй `SKILL.md`.
- Перед правкой skill / agent / instruction начинай с ближайшего
  `knowledge/wisdom-*` и одного guide; для skills сперва
  `knowledge/practical-guides/how-to-write-skills/`.

## Owner-Маршрут

- Формулировки instruction files -> `1instruction-layer`.
- Папочные контракты, `_ops/rules/`, hooks/runtime guardrails -> `1folder-contract`.
- Skills -> `1skill-architect`.
- GOAL/README/ROADMAP shape -> `1strategy-docs`; roadmap/tasks -> `1planning`.
- Подход в моменте задачи / варианты -> `1strategy`.
- Markdown поиск/связи -> `1md-navigator` / `1md-reader` / `1md-graph`.
- После правок -> прямой evidence-closeout текущего owner-а.

## Условные Правила

Не грузи редкие правила заранее:

- создаёшь или двигаешь файл, папку, раздел -> `_ops/rules/placement.md`;
- правишь AGENTS/CLAUDE/skills/prompts/hooks/runtime/модельный baseline -> `_ops/rules/instruction-and-runtime.md`;
- выбираешь проверку или CLI-evidence -> `_ops/rules/local-tools.md`.

Правило без trigger, owner и check не добавляй.

## `experiments/`

Полигон самостоятельных под-проектов (`claude-bridge`, `gemini-mcp`,
`md-embedding-server`, `flowpage-v4-elk`, `strategy-gallery`,
`global-agent-surface-viewer` и др.). Каждый существенный под-проект держит свою
правду в локальном `README.md` / `AGENTS.md`; правь субтри от его инструкции, не
от корневой. Эти папки — НЕ polygon scope `_ops/GOAL.md` (тот про knowledge и
skill design, не про runtime под-проектов). Связи и зависимости — в
`_ops/project-graph.md`.

## Красные Линии

Не создавай второй source of truth — в том числе контентный `CLAUDE.md` рядом с
`@AGENTS.md`-shim. Не копируй тела skills в root. Не редактируй Claude
instruction/runtime surfaces без явной просьбы именно на них. `_ops/user-said/` —
legacy/manual raw archive, не auto-capture и не источник решений.
`_ops/findings/`, `_ops/interviews/`, `_ops/plans/` — временные рабочие слои,
не backlog.

## GitHub

GitHub здесь — backup-диск локального `main`, не branch/PR flow. Коммить и пушь
свободно прямо в `main`, без веток, без спроса и без подтверждений. Это
solo-проект; не блокируйся на git.

## Проверка

Перед финалом покажи только существенное evidence: что изменено, чем проверено,
какие риски остались. Пиши по-русски, коротко, без справочного шума.
