---
description: "Origin, snapshots, cuts and verification evidence for 1product-shaping."
---

# 1product-shaping — папка скила: происхождение и потери

Живой owner: `skills/shared/1product-shaping/`. Installed — `~/.claude/skills/`
и `~/.codex/skills/`; напрямую не редактируются.

Переработан 2026-08-08 по канону `1skill-shaping`: Creator продуктовой правды
(сверка → пара Principles + Frame, привязанная к GOAL). Применение пары ушло
`1use-principles`; предшественник 2026-08-05 (36.6KB, продиктован владельцем)
— в снапшотах.

- `origin.md` — решения владельца, допуск к черновику, вердикты по аудиту;
- `cut.md` — что не вошло и куда ушло;
- `evidence.md` — lifecycle и честный статус (candidate, прогонов не было);
- `live-claude-2026-08-08/`, `live-codex-2026-08-08/` — снапшоты
  предшественника.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1product-shaping --write --install
python3 skills/shared/sync_simple_projections.py 1product-shaping --check
```
