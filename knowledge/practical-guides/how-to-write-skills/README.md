---
description: "Единый вход в компактный канон написания эффективных skills."
read-before-edit: []
edit-after-edit: []
---

# Как Писать Скиллы

Единый вход для skill authoring. [`authoring-canon.md`](authoring-canon.md)
владеет portable authoring principles; platform/runtime mechanics принадлежат
`platform-deltas.md` и системным creator skills. [`checklist.md`](checklist.md)
— acceptance gate для уже выбранного решения, а не следующий обязательный
workflow.

## Что Здесь Лежит

- [`authoring-canon.md`](authoring-canon.md) — короткий канон: когда скилл
  нужен, как держать scope, `description`, тело и доказательство качества.
- [`platform-deltas.md`](platform-deltas.md) — различия Codex, Claude Code,
  Agent Skills standard и API/runtime.
- [`research-2026-mar-may.md`](research-2026-mar-may.md) — source-backed выводы
  из официальных docs и исследований марта-мая 2026.
- [`research-matt-pocock-skill-writing-2026-08.md`](research-matt-pocock-skill-writing-2026-08.md)
  — форензика 25 promoted skills: формулировки, порядок, размеры,
  отрицательное пространство и границы переноса в `1skill-shaping`.
- [`research-mid-trajectory-trigger-descriptions-2026-08.md`](research-mid-trajectory-trigger-descriptions-2026-08.md)
  — датированный evidence-report о short descriptions и позднем автоматическом
  вызове по состоянию длинной работы.
- [`mid-trajectory-trigger-descriptions.md`](mid-trajectory-trigger-descriptions.md)
  — узкий практический профиль для event/state-trigger descriptions; дополняет,
  но не дублирует общий канон.
- [`checklist.md`](checklist.md) — post-hoc acceptance gate для candidate
  design, draft или review.

## Главное Решение

Скилл — не тема, заметка или обязательный алгоритм. Это повторяемое
профессиональное вмешательство с отдельным trigger, полезной Delta, границами
и проверяемым результатом. Если скилл не меняет поведение агента на реальной
задаче, его лучше не писать.

Default для judgment/design/quality skills — **outcome/decision contract**:
какой результат должен стать истинным, как разрешать материальные tradeoffs и
чем результат доказать. Пошаговый workflow нужен только когда порядок сам
обеспечивает корректность, безопасность или работу хрупкого инструмента.

## Достаточный Авторский Результат

- Admission доказан: повторяемый момент, отдельный trigger и полезная Delta
  действительно требуют skill surface.
- `description` различает use, skip и соседние задачи по реалистичным фразам.
- `SKILL.md` держит outcome, decision rules, boundaries, evidence и stop;
  workflow присутствует только под order-sensitive failure.
- Rare detail находится в `references/`, детерминированная хрупкая операция —
  в `scripts/`, выходной ресурс — в `assets/`.
- Evidence способен опровергнуть материальные claims именно этого изменения.
  Глобальность и риск повышают силу доказательства, но не задают обязательный
  пакет проверок.

## Свежесть

Research-файлы — датированные snapshots, а не вечная истина. Для
mid-trajectory descriptions текущий срез —
[`research-mid-trajectory-trigger-descriptions-2026-08.md`](research-mid-trajectory-trigger-descriptions-2026-08.md).
Перед audit'ом current/default/best-practice решений сверяй свежие официальные
docs; канон в `authoring-canon.md` держит только выводы, которые переживают
такую сверку.

## Не Создавать

- Второй общий guide про скиллы рядом с этой папкой.
- Installed skill с `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md` или
  другой human-doc историей.
- Скилл ради единичной идеи, общего знания или красивого названия.
