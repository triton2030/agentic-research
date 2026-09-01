---
description: "Version packages and refactor evidence for 1plan-task."
---

# История 1plan-task

Живой owner находится в `skills/shared/1plan-task/portable/`.
Эта папка хранит историю и не является runtime package.

## Топология

- `versions/<version-id>/` — самостоятельный снимок package: `SKILL.md`,
  runtime metadata и принадлежащие версии assets или references.
- `work/<work-id>/` — служебные материалы создания и проверки: intent, cut,
  evidence, reviews и probes.
- `origin.md`, `cut.md`, `evidence.md`, `product-frame.md` — общая история,
  относящаяся к нескольким версиям.

Последний кандидат: `versions/candidate-2026-09-02-criteria/` — установлен 2026-09-02.
Его служебное evidence: `work/refactor-2026-09-02/` (intent, clean-room-draft, loss-map, wave-1, wave-2).
