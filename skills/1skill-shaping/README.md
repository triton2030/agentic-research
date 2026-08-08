---
description: "Origin, rejected rules and verification evidence for 1skill-shaping."
---

# 1skill-shaping — папка скила: происхождение и потери

Живой owner не здесь: `skills/shared/1skill-shaping/`. Tracked проекции —
`skills/claude/1skill-shaping/` и `skills/codex/1skill-shaping/`; installed —
`~/.claude/skills/` и `~/.codex/skills/`. Их не редактируют напрямую.

Эта папка хранит то, что нельзя восстановить из текста скила:

- `origin.md` — дефицит словами владельца, смена жанра, решения сессии и
  внешнее evidence, на которое опирается конструкция;
- `cut.md` — что не вошло и почему; дописывается, не переписывается;
- `evidence.md` — support envelope и честный статус проверок.

Предшественник — `1skill-architect`, снят 2026-08-08. Все его версии, owner и
проекции лежат в `skills/1skill-architect/`.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1skill-shaping --write --install
python3 skills/shared/sync_simple_projections.py 1skill-shaping --check
```
