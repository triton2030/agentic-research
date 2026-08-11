---
description: "Origin, rejected rules and verification evidence for 1use-principles."
---

# 1use-principles — папка скила: происхождение и потери

Живой owner: `skills/shared/1use-principles/portable/`. Tracked проекции —
`skills/claude/` и `skills/codex/`; installed — `~/.claude/skills/` и
`~/.codex/skills/`. Их не редактируют напрямую.

Создан 2026-08-08, расширен 2026-08-09: Applicator принципов закрывает
развилку либо строит варианты для пустоты через сцену продукта, затем проводит
свип осей → матрицу → обратный проход → тайбрейкер/эскалацию → след. Пара к
Creator-у `1product-shaping`.

- `origin.md` — заказ и коррекции владельца (эталон Индии), разбор шести
  дефолтов и человеческих практик;
- `cut.md` — отклонённые и снятые как дубли правила;
- `evidence.md` — различающий прогон генеративной ветки и его границы.

## Синхронизация после правки owner-а

```bash
python3 skills/shared/sync_simple_projections.py 1use-principles --write --install
python3 skills/shared/sync_simple_projections.py 1use-principles --check
```
