---
description: "Origin, rejected rules and archived versions of 1goal."
---

# 1goal — папка скила: происхождение, потери, версии

Живой owner: `skills/shared/1goal/`. Tracked проекции — `skills/claude/` и
`skills/codex/`; installed — `~/.claude/skills/` и `~/.codex/skills/`. Их не
редактируют напрямую.

Переформирован 2026-08-08 через `1skill-shaping`: GOAL — верхнеуровневый
контекст, из которого агент выводит решения, не названные дословно; скил выше
просьб владельца в моменте.

- `origin.md` — дефицит, переопределение и цитаты владельца, связки;
- `cut.md` — таблица потерь против прежней версии;
- `evidence.md` — lifecycle, support envelope, честный статус;
- `tracked-claude-2026-08-08/`, `live-claude-2026-08-08/`,
  `live-codex-2026-08-08/` — прежние версии.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1goal --write --install
python3 skills/shared/sync_simple_projections.py 1goal --check
```
