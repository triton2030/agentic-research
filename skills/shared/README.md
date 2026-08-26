---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- Семья авторинга — пять скилов по различимым моментам запуска, заменили пару
  `1skill-shaping` + `1instruction-shaping`, снятую 2026-08-26 (архивы в
  `skills/1skill-shaping/` и `skills/1instruction-shaping/`; решение владельца —
  `_ops/chat-recall/raw/2026-08-26-201025-claude-4e40828f.md#L15`):
  - `1instruction-authoring/portable/` — создание инструкций: корень-роутер
    (≤20 единиц знаний, связки «папка → её инструкция»), цепочка папочных
    инструкций, новое правило; владеет `interview.md`, `wording.md`,
    `knowledge-out.md`, `placement.md` (траекторный счёт);
  - `1context-refactor/portable/` — рефактор контекста: мета-анализ прошедшего
    диалога — найти шероховатости (лишнее чтение, переделки, долгая работа),
    установить причину, чинить настоящего виновника (инструкции, документ,
    скил, слова владельца); владеет `refactor.md` (схема карты смыслов),
    `coherence.md`, `simplify.md`, базовыми `audit.md`/`check.md`;
  - `1skill-creation/portable/` — создание скиллов (бывший `1skill-authoring`,
    полная перекройка 2026-08-26, архив в `skills/1skill-authoring/`): извлечь
    из слов владельца функцию, которую он подразумевает под именем скила, и
    написать кратчайший недвусмысленный скил; владеет `canon.md` (канон
    методик), `formulation.md`, `agent-defaults.md` («налог на строгость»),
    `skills-science.md` и мягким бюджетом ~20 единиц на тело и на reference;
  - `1skill-routing/portable/` — кнопка запуска: имя, description, триггер;
    владеет `description.md` и лимитом 200 символов на описания и
    строки-аннотации;
  - `1skill-refactor/portable/` — рефактор скила: сверка со `1skill-creation`
    и пошаговый протокол абстрагирования инструкций в высший порядок без потери
    смысла; владеет своими `refactor.md`, `failures.md`, `check.md` (дельты
    поверх базы `1context-refactor`).
  У каждого `platforms/codex/agents/openai.yaml` — только Codex UI metadata.
  Reference-файл живёт ровно у одного владельца; соседи ссылаются относительно.
- `1md-search/portable/` — общий cognitive/tool core для
  Codex и Claude; `platforms/codex/agents/openai.yaml` — только Codex UI и
  invocation metadata. Сосед `1md-read` снят 2026-08-22 по решению владельца,
  архив в `skills/1md-read/`.
- `1deep-agents/portable/` — общий framework-routing, trace и synthesis
  contract; runtime launch deltas для Codex `spawn_agent` и Claude `Agent`
  живут в одной адресуемой reference, а Codex UI metadata — в
  `platforms/codex/agents/openai.yaml`.
- `1product-shaping/portable/` создаёт чистые Product Principles + Frame и
  журнал обоснований; `1use-principles/portable/` применяет их к развилкам и
  пустотам.
- Семья планирования — тройка по моментам запуска, раскроена 2026-08-26 из
  монолита `1planning` (решение владельца —
  `_ops/chat-recall/raw/2026-08-26-220614-claude-4ee6bbef.md`; карта раскройки
  и снимок — `skills/1planning/`):
  - `1planning/portable/` — страж и когнитивный протокол в чате: любая мысль
    «что дальше», спор о допуске задачи, доказанная пошаговая декомпозиция по
    книжным методикам до любых план-файлов; без references;
  - `1plan-map/portable/` — эпики и верхний уровень проекта: рамки и принципы
    до состава, карта от GOAL, дашборд Obsidian; владеет `map-form.md`,
    `dashboard.md`;
  - `1plan-task/portable/` — изолированность задач: самодостаточный жёстко
    ограниченный task-файл, режимы, доказательства, fresh-reader; владеет
    `task-form.md`.
- `1index/portable/` держит карты оплаченных поиском маршрутов.
- `1interview-tool/portable/` создаёт адресуемую plain-Markdown форму и держит
  lifecycle `решения владельца → настоящие owners → архив`; Codex invocation
  metadata живёт в `platforms/codex/agents/openai.yaml`.

`skills/codex/<name>/` и `skills/claude/<name>/` — tracked projections owner-а.
`~/.codex/skills/<name>/` и `~/.claude/skills/<name>/` — installed projections
следующего уровня. Их не редактируют напрямую.

## Product Owners

`1chat-recall/`, `1handoff/` и `1hermes/` владеют только общей продуктовой
правдой `product-frame*.md` — Frame и, где она уже существует, Principles.
Они не становятся source owner-ами runtime package и не входят в projection
sync. Поведение остаётся у tracked или live `SKILL.md`; при расхождении product
intent и runtime нужен явный reconcile, а не копия пары в оба runtime.

Runtime `1hermes` с 2026-08-22 tracked: `skills/claude/1hermes/` и
`skills/codex/1hermes/` — owner-ы своих семей, установленные пути стали
симлинками. Общего portable-ядра у них нет и не планируется: копии расходятся
намеренно (`--isolated` только у Claude, `agents/openai.yaml` только у Codex),
поэтому правку кода вноси в обе руками, а не через sync.

## Синхронизация

После правки source owner-а передай имена изменённых пакетов позиционными
аргументами. Например, для текущей группы:

```bash
python3 skills/shared/sync_simple_projections.py \
  1product-shaping 1use-principles 1planning 1index --write --install
python3 skills/shared/sync_simple_projections.py \
  1product-shaping 1use-principles 1planning 1index --check
```

Generic script собирает все portable files и непересекающуюся runtime delta.
Он отказывается удалять unexpected projection files: их provenance сначала
разрешается явно.

Special-manifest скрипт `1skill-architect/sync_projections.py` вышел из
обращения вместе со скилом; он лежит в
`skills/1skill-architect/shared-owner-2026-08-08/`.

Special-manifest скрипт копирует явный manifest и удаляет только названные
obsolete runtime-файлы. Неизвестные лишние файлы он не удаляет: `--check`
останавливается, чтобы projection не стала скрытым вторым owner-ом.
