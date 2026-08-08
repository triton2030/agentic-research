---
description: "Origin, rejected rules and archived versions of 1planning."
---

# 1planning — папка скила: происхождение, потери, версии

Живой owner: `skills/shared/1planning/`. Tracked проекции — `skills/claude/` и
`skills/codex/`; installed — `~/.claude/skills/` и `~/.codex/skills/`. Их не
редактируют напрямую.

Переформирован 2026-08-08 через `1skill-shaping`: план — инструкция от агента
агенту с триадой и пунктом GOAL; разбивка (`1break-down`) поглощена; развилки
вне плана идут в `1use-principles`; файл не создаётся без «да» владельца.

- `origin.md` — решения и цитаты владельца, research, что сохранено;
- `cut.md` — таблица потерь против прежних 6 references;
- `evidence.md` — lifecycle и честный статус;
- `live-claude-2026-08-08/`, `live-codex-2026-08-08/` — прежние версии
  целиком (включая все старые references — источник точечных возвратов).

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1planning --write --install
python3 skills/shared/sync_simple_projections.py 1planning --check
```
