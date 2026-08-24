В этом репо работай как хранитель `agentic-research`: усиливай глобальную
инструкцию локальной правдой проекта, не повторяй её.

Здесь мало правил и много ориентировки. Правила — только там, где мой дефолт
в этом репо приведёт к неверному действию. Всё остальное ниже — сухие адреса.
Маршруты, оплаченные чужим поиском, — в [`INDEX.md`](INDEX.md).

## Что Это За Репо

`agentic-research` — мастерская знаний и полигон для обсуждений и экспериментов,
но **продукт всегда снаружи репо**: глобальные скилы (`~/.claude/skills/1*`,
`~/.codex/skills/`) и общие паттерны инструкций / промптов / хуков, работающие
во всех проектах. `knowledge/` и разговоры здесь обслуживают эту цель, не
существуют ради себя.

Цель проекта, границы, done и stop — `_ops/GOAL.md`. Рабочий набор моделей задан
там же; канон не расширяется до model-neutral, `GPT-5.5` и Claude 4.x остаются
историческим evidence, не target и не fallback.

## Карта Репо

| Где | Что лежит | Владелец правды |
| --- | --- | --- |
| `_ops/GOAL.md` | контракт проекта: scope / done / stop | `1goal` |
| `_ops/product-frames/` | project-wide пара frame + principles | `1product-shaping` |
| `_ops/chat-recall/` | слова владельца: руда `raw/` + слой тем `topics/` | `_ops/chat-recall/AGENTS.md` |
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

- **За позицией владельца иди сперва в `_ops/chat-recall/topics/`.** Слой тем —
  один файл на предмет вместо трёх разговоров, и слепая приёмка 2026-08-24 дала
  на нём ноль уверенно-неверных ответов против одного у штатного поиска. Это
  project-local уточнение `1chat-recall`: его `chat_digest.py` по умолчанию
  ведёт в сырой корпус (`_ops/chat-recall/raw/`), здесь — сначала слой, потом
  реплика по якорю пункта. Доказательством остаётся реплика, не пункт: слой
  обзорный, без даты и без отменённого. Контракт обоих слоёв и обновление —
  `_ops/chat-recall/AGENTS.md`.
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
- **Живой `SKILL.md` сильнее старых repo notes.** Расходятся — следуй
  `SKILL.md`. Расхождение с matching Product Frame — конфликт product intent и
  runtime: предъяви оба адреса, не выбирай молча.
- **До первого существенного суждения** прочитай целиком
  `_ops/product-frames/agentic-research{,.principles}.md`. При правке скила —
  плюс `product-frame*.md` из его tracked owner-папки, если она есть; рамки
  неприменимых скилов не pre-load'ятся.
- **Перед правкой skill / agent / instruction** начинай с ближайшего
  `knowledge/wisdom-*` и одного guide; для skills сперва
  `knowledge/practical-guides/how-to-write-skills/`.
- **Новый или переписанный скил — только через `1skill-shaping`**, и он же
  запрещает писать скил без разговора с владельцем и его «да».
- **`experiments/**` правь от локальной инструкции**, не от корневой. Эти папки
  не входят в polygon scope `_ops/GOAL.md`.
- **GitHub здесь — backup-диск локального `main`**, не branch/PR flow. Коммить
  и пушь свободно прямо в `main`, без веток, без спроса. Не блокируйся на git.
- **Перед финалом** покажи только существенное evidence: что изменено, чем
  проверено, какие риски остались. По-русски, коротко, без справочного шума.
