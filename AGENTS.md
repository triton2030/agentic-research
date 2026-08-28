`agentic-research` — мастерская знаний и полигон для обсуждений и экспериментов,
но **продукт всегда снаружи репо**: глобальные скилы (`~/.claude/skills/1*`,
`~/.codex/skills/`) и общие паттерны инструкций / промптов / хуков, работающие
во всех проектах. `knowledge/` и разговоры здесь обслуживают эту цель, не
существуют ради себя.


## Карта Репо

| Где | Что лежит | Владелец правды |
| --- | --- | --- |
| `_ops/GOAL.md` | контракт проекта: scope / done / stop | `1goal` |
| `_ops/product-frames/` | project-wide пара frame + principles | `1product-shaping` |
| `_ops/chat-recall/` | слова владельца: дословные выдержки, файл на разговор | `_ops/chat-recall/AGENTS.md` |
| `_ops/findings/` | inbox побочных проблем до маршрутизации | `1findings` |
| `_ops/plans/` | task-файлы активной многосессионной работы | `1planning` |
| `_ops/handoffs/` | continuation packets закрытых сессий | `1handoff` |
| `_ops/interviews/`, `_ops/rules/`, `_ops/user-said/`, `_ops/self-learning/` | временные и замороженные поверхности | `_ops/AGENTS.md` |
| `knowledge/` | wisdom-файлы, guides, practical guides, research, examples | папочные README |
| `science/` | тезисы об управлении мышлением ЛЛМ + evidence-статусы | `science/README.md` |
| `skills/shared/` | cross-runtime owners пакетов (`<name>/portable/`) | `skills/shared/README.md` |
| `skills/claude/`, `skills/codex/` | runtime owners либо tracked projections | `skills/claude/README.md` |
| `skills/1<name>/` | **архив истории скила**, не сам скил | — |
| `experiments/` | независимые под-проекты со своей правдой | локальный `AGENTS.md` |
| `_workspace/` | рабочие артефакты, HTML-зона, оркестрации | `_workspace/*/AGENTS.md` |

Детальные контракты папок `_ops` — в `_ops/AGENTS.md`, включая красные линии.
Граф зон — `depends-on` в шапках subtree `AGENTS.md` (читает `1md-graph`).
`README.md` — входной контекст для человека.

## Правила Этого Репо

- **Правка скила — глобальный артефакт** (cross-project, veto-class): пиши
  project-independent, без путей и допущений текущего проекта.
- **Владелец пакета — сначала tracked owner.** Есть папка в `skills/shared/**`
  или `skills/{claude,codex}/**` — правь её, а `~/.claude/skills/` и
  `~/.codex/skills/` считай projection. Нет tracked owner — live installed
  package остаётся единственной правдой; parity и второй source tree не
  выдумывай. Реестр владельцев — `skills/shared/README.md`.
- **`skills/1<name>/` — история, не скил.** Внутри `origin.md`, `cut.md`,
  `evidence.md`, снапшоты `live-*` и `tracked-*`, иногда `product-frame*.md`
  снятого скила. Никогда не правь их как живой контракт и не принимай их
  `product-frame*.md` за действующий.
- **До первого существенного суждения** прочитай целиком
  `_ops/product-frames/agentic-research{,.principles}.md`. При правке скила —
  плюс `product-frame*.md` из его tracked owner-папки, если она есть; рамки
  неприменимых скилов не pre-load'ятся.
- **Перед правкой skill / agent / instruction** начинай с ближайшего
  `knowledge/wisdom-*` и одного guide; для skills сперва
  `knowledge/practical-guides/how-to-write-skills/`.
- **GitHub здесь — backup-диск локального `main`**, не branch/PR flow. Коммить
  и пушь свободно прямо в `main`, без веток, без спроса. Не блокируйся на git.
- **Перед финалом** покажи только существенное evidence: что изменено, чем
  проверено, какие риски остались. По-русски, коротко, без справочного шума.
