---
description: "Origin, rejected rules and archived versions of 1index."
---

# 1index — папка скила: происхождение, потери, версии

Живой owner: `skills/shared/1index/`. Tracked проекции — `skills/claude/` и
`skills/codex/`; installed — `~/.claude/skills/` и `~/.codex/skills/`. Их не
редактируют напрямую.

Последняя установленная редакция — 2026-09-08: каждая запись INDEX выражает
условие работы и даёт точные ссылки с действием у источников. Назначение и
прежние ограничения сохранены. Состояние — `state.md`, основания и проверки —
`review-2026-09-08/decisions.md`; старый пакет — `before-2026-09-08/`.

Переформирован 2026-08-08 через `1skill-shaping`: суть — запись в INDEX
оплачена прошлым поиском, не сгенерирована из листинга.

- `origin.md` — класс, дефицит, решения и цитаты владельца, evidence;
- `cut.md` — таблица потерь против прежней версии;
- `evidence.md` — support envelope и честный статус;
- `live-claude-2026-08-08/`, `live-codex-2026-08-08/` — прежние установленные
  версии (разошедшиеся; repo-владельца до этого дня не было).

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1index --write --install
python3 skills/shared/sync_simple_projections.py 1index --check
```
