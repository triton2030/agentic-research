---
description: "Origin, rejected rules and verification evidence for 1interview-tool."
---

# 1interview-tool — происхождение, потери и проверка

Живой owner: `skills/shared/1interview-tool/`. Tracked проекции —
`skills/claude/1interview-tool/` и `skills/codex/1interview-tool/`; installed —
`~/.claude/skills/1interview-tool/` и `~/.codex/skills/1interview-tool/`.
Проекции напрямую не редактируются.

- `origin.md` — слова владельца, одобренный синтез и допуск к пересборке;
- `cut.md` — снятые правила и таблица потерь;
- `evidence.md` — support envelope и результаты проверок.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1interview-tool --write --install
python3 skills/shared/sync_simple_projections.py 1interview-tool --check
```
