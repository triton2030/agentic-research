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

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1product-shaping --write --install
python3 skills/shared/sync_simple_projections.py 1product-shaping --check
```
