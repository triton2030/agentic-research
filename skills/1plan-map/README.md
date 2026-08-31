---
description: "Version packages and refactor evidence for 1plan-map."
---

# История 1plan-map

Живой owner находится в `skills/shared/1plan-map/portable/`.
Эта папка хранит историю и не является runtime package.

## Топология

- `versions/<version-id>/` — самостоятельный снимок package: `SKILL.md`,
  runtime metadata и принадлежащие версии assets или references.
- `work/<work-id>/` — служебные материалы создания и проверки: intent, cut,
  evidence, reviews и probes.
- `origin.md`, `cut.md`, `evidence.md`, `product-frame.md` — общая история,
  относящаяся к нескольким версиям.

Последний кандидат: `versions/candidate-2026-08-31/`.
Его служебное evidence: `work/recheck-2026-08-31/`.
