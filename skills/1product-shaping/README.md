---
description: "Origin, snapshots, cuts and verification evidence for 1product-shaping."
---

# 1product-shaping — папка скила: происхождение и потери

Живой owner: `skills/shared/1product-shaping/`. Installed — `~/.claude/skills/`
и `~/.codex/skills/`; напрямую не редактируются.

Переработан 2026-08-09 по канону `1skill-shaping`: Creator держит чистые
текущие Principles + Frame и один append-only журнал обоснований. Дословные
слова владельца живут в журнале и recall; применение пары — у
`1use-principles`. Предшественник 2026-08-05 — в снапшотах.

- `origin.md` — диагноз смешения чистовика, evidence и состояния; решения
  владельца о чистовиках и журнале;
- `cut.md` — таблица потерь перехода к чистовикам;
- `evidence.md` — диагноз старого формата, независимый разбор и различающий
  прогон нового;
- `live-claude-2026-08-08/`, `live-codex-2026-08-08/` — снапшоты
  предшественника.
- `live-claude-2026-09-04/` — установленный пакет Claude на 2026-09-04; до
  2026-10-22 лежал в `~/.claude/skills/_backups/`. Файлы Codex-копии того дня
  уже есть в `candidate-repair-2026-08-31/` и
  `candidate-2026-08-30/platforms/codex/`[^backups].

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1product-shaping --write --install
python3 skills/shared/sync_simple_projections.py 1product-shaping --check
```

[^backups]: [Слова владельца, 2026-10-22](../../_ops/chat-recall/2026-10-22-235727-claude-code-4acb96f5.md#recall-bdd2d81f8fce4bd79924703b6be3c6c6).
