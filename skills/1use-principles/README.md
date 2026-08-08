---
description: "Origin, rejected rules and verification evidence for 1use-principles."
---

# 1use-principles — папка скила: происхождение и потери

Живой owner: `skills/shared/1use-principles/`. Tracked проекции —
`skills/claude/` и `skills/codex/`; installed — `~/.claude/skills/` и
`~/.codex/skills/`. Их не редактируют напрямую.

Создан 2026-08-08: Applicator принципов — двухпроходная мини-матрица
(варианты → свип осей по последствиям → специфицирование → обратный проход →
тайбрейкер/эскалация → след) перед чистовой записью и на развилках автономной
работы. Пара к Creator-у `1product-shaping`.

- `origin.md` — заказ и коррекции владельца (эталон Индии), разбор шести
  дефолтов и человеческих практик;
- `cut.md` — отклонённые правила;
- `evidence.md` — lifecycle и честный статус (кандидат, прогонов не было).

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1use-principles --write --install
python3 skills/shared/sync_simple_projections.py 1use-principles --check
```
