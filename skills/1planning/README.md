---
description: "Origin, rejected rules and archived versions of 1planning."
---

# 1planning — папка скила: происхождение, потери, версии

Живой owner: `skills/shared/1planning/`. Tracked проекции — `skills/claude/` и
`skills/codex/`; installed — `~/.claude/skills/` и `~/.codex/skills/`. Их не
редактируют напрямую.

Переформирован 2026-08-09 через `1skill-shaping`: план — живой контракт плюс
`context.md`, который переносит отсутствующий у project owners замысел из
чата. Разбивка (`1break-down`) поглощена; развилки вне плана идут в
`1use-principles`; файлы не создаются без «да» владельца.

- `origin.md` — решения владельца о `context.md` и дедупликации тела;
- `cut.md` — таблица потерь и принятых рисков;
- `evidence.md` — различающий прогон и внешнее ревью;
- `live-claude-2026-08-08/`, `live-codex-2026-08-08/` — прежние версии
  целиком (включая все старые references — источник точечных возвратов).

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1planning --write --install
python3 skills/shared/sync_simple_projections.py 1planning --check
```
