---
description: "Version packages and refactor evidence for 1planning."
---

# История 1planning

Живой owner находится в `skills/shared/1planning/portable/`.
Эта папка хранит историю и не является runtime package.

## Топология

- `versions/<version-id>/` — самостоятельный снимок package: `SKILL.md`,
  runtime metadata и принадлежащие версии assets или references.
- `work/<work-id>/` — служебные материалы создания и проверки: intent, cut,
  evidence, reviews и probes.
- `origin.md`, `cut.md`, `evidence.md`, `product-frame.md` — общая история,
  относящаяся к нескольким версиям.

Последний кандидат: `versions/candidate-2026-08-31-genie-v2/`.
Его служебное evidence: `work/refactor-2026-08-31-doctrine/`.

Предыдущий подробный README сохранён в
`work/README-before-2026-08-31.md` как исторический service artifact.
