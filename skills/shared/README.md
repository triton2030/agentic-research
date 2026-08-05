# Shared Skill Owners

Эта папка владеет пакетами, у которых переносимый смысл и runtime-дельты
должны меняться как одно целое. Она не является третьим installed runtime.

## Живые Owners

- `1skill-architect/portable/` — общий `SKILL.md`, словарь и portable
  references для Codex и Claude.
- `1skill-architect/platforms/<runtime>/` — только честные platform deltas:
  authoring mechanics и runtime metadata.
- `1md-read/portable/` и `1md-search/portable/` — общий cognitive/tool core для
  Codex и Claude; `platforms/codex/agents/openai.yaml` — только Codex UI и
  invocation metadata.
- `1deep-agents/portable/` — общий framework-routing, trace и synthesis
  contract; runtime launch deltas для Codex `spawn_agent` и Claude `Agent`
  живут в одной адресуемой reference, а Codex UI metadata — в
  `platforms/codex/agents/openai.yaml`.

Source-only `portable/references/platform-skill-authoring.md` — pointer-router
к двум platform owners. Он делает source links разрешимыми, но не входит в
projection manifest: в собранном package тот же address занимает выбранная
runtime delta.

`skills/codex/1skill-architect/` и `skills/claude/1skill-architect/` — tracked
projections этого owner-а. `~/.codex/skills/1skill-architect/` и
`~/.claude/skills/1skill-architect/` — installed projections следующего уровня.
Их не редактируют напрямую.

## Синхронизация

После правки source owner-а:

```bash
python3 skills/shared/1skill-architect/sync_projections.py --write --install
python3 skills/shared/1skill-architect/sync_projections.py --check
```

Для простых shared packages и runtime-owned `1md-graph`:

```bash
python3 skills/shared/sync_simple_projections.py \
  1md-read 1md-search 1md-graph --write --install
python3 skills/shared/sync_simple_projections.py \
  1md-read 1md-search 1md-graph --check
```

Generic script собирает все portable files и непересекающуюся runtime delta.
Он не обслуживает special-manifest `1skill-architect` и отказывается удалять
unexpected projection files: их provenance сначала разрешается явно.

Скрипт копирует только явный manifest и удаляет только названные obsolete
runtime-файлы. Неизвестные лишние файлы он не удаляет: `--check` останавливается
и показывает расхождение, чтобы projection не стала скрытым вторым owner-ом.
