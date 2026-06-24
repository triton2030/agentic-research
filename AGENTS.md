
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


## `experiments/`

Полигон самостоятельных под-проектов (`claude-bridge`, `gemini-mcp`,
`md-tools`, `flowpage-v4-elk`, `strategy-gallery`,
`global-agent-surface-viewer` и др.). Каждый существенный под-проект держит свою
правду в локальном `README.md` / `AGENTS.md`; правь субтри от его инструкции, не
от корневой. Эти папки — НЕ polygon scope `_ops/GOAL.md` (тот про knowledge и
skill design, не про runtime под-проектов). Связи и зависимости — в
`_ops/project-graph.md`.

## GitHub

GitHub здесь — backup-диск локального `main`, не branch/PR flow. Коммить и пушь
свободно прямо в `main`, без веток, без спроса и без подтверждений. Это
solo-проект; не блокируйся на git.

## Проверка

Перед финалом покажи только существенное evidence: что изменено, чем проверено,
какие риски остались. Пиши по-русски, коротко, без справочного шума.
