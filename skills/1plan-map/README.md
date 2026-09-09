---
description: "Version packages and refactor evidence for 1plan-map."
---

# История 1plan-map

Живой owner находится в `skills/shared/1plan-map/portable/`.
Эта папка хранит историю и не является runtime package.

## Установлено 2026-09-09

[Точная версия](versions/installed-2026-09-09/SKILL.md) установлена в tracked
owner, Codex и Claude: слой канона снят, у эпика и задачи «Основания» вместо
«Канон», маршруты записи решений — `1docs-write` и `1goal`. Основание и карта —
[cut.md](cut.md#2026-09-09--снятие-слоя-канона). Существующие планы не
мигрировались; чекер читает прежние имена.

## Установлено 2026-09-08

[Точная версия](versions/installed-2026-09-08/SKILL.md) установлена в tracked owner,
Codex и Claude. [Результат и проверка](../1planning/work/implementation-2026-09-08/state.md).
Существующие планы не мигрировались.

## Топология

- `versions/<version-id>/` — самостоятельный снимок package: `SKILL.md`,
  runtime metadata и принадлежащие версии assets или references.
- `work/<work-id>/` — служебные материалы создания и проверки: intent, cut,
  evidence, reviews и probes.
- `origin.md`, `cut.md`, `evidence.md`, `product-frame.md` — общая история,
  относящаяся к нескольким версиям.

Версия до этой правки: `versions/candidate-2026-08-31/`.
Его служебное evidence: `work/recheck-2026-08-31/`.

## Рефактор 2026-09-03

Исторический черновик: [candidate-2026-09-03-v3](versions/candidate-2026-09-03-v3/SKILL.md), ещё не установлен.
Исходный пакет: [baseline-2026-09-03](versions/baseline-2026-09-03/SKILL.md).
Продолжение: [состояние](work/refactor-2026-09-03/state.md).
Общее намерение и карта потерь: [рабочая папка тройки](../1planning/work/refactor-2026-09-03/intent.md).
