---
description: "Semantic owners and projection contracts for cross-runtime skills."
---

# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- `1skill-shaping/portable/` — общий controller (семь фиксированных разделов) и
  семь условных reference-маршрутов для Codex и Claude.
  `platforms/codex/agents/openai.yaml` — только Codex UI и invocation metadata.
  Заменил `1skill-architect`, снятый 2026-08-08 в `skills/1skill-architect/`.
- `1instruction-shaping/portable/` — agent harness: шов между пятью слоями,
  влияющими на поведение агента (корень, папка, скил, хук, план). Семь
  фиксированных разделов, семь условных reference-маршрутов.
  Заменил `1instruction-layer`, снятый 2026-08-08 в `skills/1instruction-layer/`.
- `1md-read/portable/` и `1md-search/portable/` — общий cognitive/tool core для
  Codex и Claude; `platforms/codex/agents/openai.yaml` — только Codex UI и
  invocation metadata.
- `1deep-agents/portable/` — общий framework-routing, trace и synthesis
  contract; runtime launch deltas для Codex `spawn_agent` и Claude `Agent`
  живут в одной адресуемой reference, а Codex UI metadata — в
  `platforms/codex/agents/openai.yaml`.

`skills/codex/<name>/` и `skills/claude/<name>/` — tracked projections owner-а.
`~/.codex/skills/<name>/` и `~/.claude/skills/<name>/` — installed projections
следующего уровня. Их не редактируют напрямую.

## Синхронизация

После правки source owner-а:

```bash
python3 skills/shared/sync_simple_projections.py \
  1skill-shaping 1md-read 1md-search 1md-graph --write --install
python3 skills/shared/sync_simple_projections.py \
  1skill-shaping 1md-read 1md-search 1md-graph --check
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
