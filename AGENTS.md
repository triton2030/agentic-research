
В этом репо работай как хранитель `agentic-research`: усиливай глобальную
инструкцию локальной правдой проекта, не повторяй её.

## Что Это За Репо

`agentic-research` — мастерская знаний и полигон для обсуждений и экспериментов,
но **продукт всегда снаружи репо**: глобальные скилы (`~/.claude/skills/1*`,
`~/.codex/skills/`) и общие паттерны инструкций / промптов / хуков, работающие во
всех проектах. `knowledge/` и разговоры здесь обслуживают эту цель, не существуют
ради себя. Следствие на каждый день: правка скила — глобальный артефакт
(cross-project, veto-class), пиши project-independent. Если package имеет tracked
owner в `skills/**` или `experiments/**`, сначала правь его, а global install
считай projection. Если tracked owner отсутствует, live installed package
остаётся единственной правдой до отдельного решения provenance; не выдумывай
parity или второй source tree. `experiments/**` — независимые под-проекты со своей
правдой.

## Цель

Делать систему `skills`, hooks, prompts, инструкций, знаний и рабочих контрактов
понятнее для будущей ИИ-сессии под рабочий набор моделей, заданный в
`_ops/GOAL.md`. Канон не расширяется до model-neutral; `GPT-5.5` и более старые
OpenAI-модели остаются только историческим evidence, не рабочим target или
fallback.

## Локальная Правда

Если это меняет маршрут, риск или проверку, стартуй от `_ops/GOAL.md`
(scope/done/stop) и живых `SKILL.md`. `README.md` — входной контекст. Граф зон —
`depends-on` в шапках subtree `AGENTS.md` (читает `1md-graph`).

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
skill design, не про runtime под-проектов). Связи и зависимости — в локальных
`AGENTS.md` сабтри.

## GitHub

GitHub здесь — backup-диск локального `main`, не branch/PR flow. Коммить и пушь
свободно прямо в `main`, без веток, без спроса и без подтверждений. Это
solo-проект; не блокируйся на git.

## Проверка

Перед финалом покажи только существенное evidence: что изменено, чем проверено,
какие риски остались. Пиши по-русски, коротко, без справочного шума.
