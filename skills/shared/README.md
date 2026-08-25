---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- `1skill-shaping/portable/` — общий controller: цель, автономная граница, три
  невыводимых правила и девять условных reference-маршрутов для Codex и Claude.
  `platforms/codex/agents/openai.yaml` — только Codex UI и invocation metadata.
  Заменил `1skill-architect`, снятый 2026-08-08 в `skills/1skill-architect/`.
- `1instruction-shaping/portable/` — agent harness: шов между пятью слоями,
  влияющими на поведение агента (корень, папка, скил, хук, план). Семь
  фиксированных разделов, семь условных reference-маршрутов.
  Заменил `1instruction-layer`, снятый 2026-08-08 в `skills/1instruction-layer/`.
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
- `1planning/portable/` создаёт карту эпиков и один живой task-файл внутри
  эпика для работы через сессии; `1index/portable/` держит карты оплаченных
  поиском маршрутов.
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
