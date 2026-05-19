---
description: "Единый вход в компактный канон написания эффективных skills."
read-before-edit: []
edit-after-edit: []
---
# Как Писать Скиллы

Единый вход для skill authoring. Если нужна одна страница — читай
[`authoring-canon.md`](authoring-canon.md), потом
[`checklist.md`](checklist.md).

## Что Здесь Лежит

- [`authoring-canon.md`](authoring-canon.md) — короткий канон: когда скилл
  нужен, как держать scope, `description`, тело и доказательство качества.
- [`platform-deltas.md`](platform-deltas.md) — различия Codex, Claude Code,
  Agent Skills standard и API/runtime.
- [`research-2026-mar-may.md`](research-2026-mar-may.md) — source-backed выводы
  из официальных docs и исследований марта-мая 2026.
- [`checklist.md`](checklist.md) — Go/No-Go перед созданием или правкой скилла.

## Главное Решение

Скилл — не тема и не заметка. Это повторяемый workflow с отдельным trigger,
границами, входом, выходом и проверкой. Если скилл не меняет поведение агента
на реальной задаче, его лучше не писать.

## Быстрый Маршрут

1. Проверь Go/No-Go в [`checklist.md`](checklist.md).
2. Пиши `description` как routing contract: когда использовать, когда не
   использовать, какие реальные фразы пользователя должны сработать.
3. В `SKILL.md` оставь только ядро: workflow, gotchas, defaults, validation,
   stop condition и ссылки на нужные bundled files.
4. Длинные детали вынеси в `references/`, детерминированные операции — в
   `scripts/`, выходные ресурсы — в `assets/`.
5. Проверь на реальных `should-trigger` / `should-not-trigger` prompts и хотя
   бы одном `with_skill` vs baseline прогоне.

## Не Создавать

- Второй общий guide про скиллы рядом с этой папкой.
- Installed skill с `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md` или
  другой human-doc историей.
- Скилл ради единичной идеи, общего знания или красивого названия.
