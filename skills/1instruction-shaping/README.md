---
description: "Origin, rejected rules and verification evidence for 1instruction-shaping."
---

# 1instruction-shaping — папка скила: происхождение и потери

Живой owner не здесь: `skills/shared/1instruction-shaping/`. Tracked проекции —
`skills/claude/` и `skills/codex/`; installed — `~/.claude/skills/` и
`~/.codex/skills/`. Их не редактируют напрямую.

Это `agent harness` под своим именем: он владеет швом между всеми слоями,
влияющими на поведение агента — корень, папка, скил, хук, план.

- `origin.md` — определение и цель словами владельца, три его поправки,
  внешнее evidence под каждой ключевой строкой;
- `cut.md` — что не вошло и почему;
- `evidence.md` — support envelope, честный статус и известные слабые места.

Предшественник — `1instruction-layer`, снят 2026-08-08; вся его гейтовая
машина сохранена в `skills/1instruction-layer/`.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1instruction-shaping --write --install
python3 skills/shared/sync_simple_projections.py 1instruction-shaping --check
```
