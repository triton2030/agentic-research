# design-auditor — Claude Code Skill [DEPRECATED]

Плагин `design-auditor` выпилен 2026-04-17. Заменён на [`knowledge/guides/design-review-playbook.md`](../../../knowledge/guides/design-review-playbook.md).

## Почему выпилен

Обе реализации (2.0.0 и 3.0.0) оказались теневой копией уже установленных скиллов:

- `my-skills:screenshot-design` — rigid Visual Evidence Ledger, покрывает structure и craft с якорями.
- `my-skills:playwright-skill` mode 2 — даёт числа (APCA, spacing rhythm, visual weight) на живом URL.
- `impeccable:critique` — уже реализует «два независимых sub-agents» с AI Slop Detection, опираясь на каталог anti-patterns из `impeccable` base.
- `impeccable:arrange / typeset / colorize / audit` — узкие подходы под конкретные слои.
- `taste-skill:*` — эстетические mood-фреймы.

Три prose-агента design-auditor давали тот же взгляд без ledger, без чисел и без каталога anti-patterns — слабее в каждом сценарии. При этом коллизия триггеров с `screenshot-design` (мандатен по глобальному CLAUDE.md) делала его почти невозможно вызвать.

Подробный анализ и 10 failure-mode сценариев — в [decision-2026-04-17.md](decision-2026-04-17.md).

## Что осталось в репо

- [audit-2026-04-17.md](audit-2026-04-17.md) — исторический аудит версии 2.0.0, обоснование упрощения до 3.0.0.
- [changes-2026-04-17.md](changes-2026-04-17.md) — что именно менялось при переходе 2.0.0 → 3.0.0.
- [decision-2026-04-17.md](decision-2026-04-17.md) — финальное решение о выпиле, landscape-анализ, симуляции.

План миграции — [`ops/plans/plan-2026-04-17-design-auditor-shrink.md`](../../../ops/plans/plan-2026-04-17-design-auditor-shrink.md).

## Где взять капчур-логику при необходимости

Node-скрипт `capture_page.mjs` из 2.0.0 сохранён в `~/.claude/backups/design-auditor.pre-marketplace-fix.20260416-230044/skills/design-auditor/scripts/`. Использовать только если `playwright-skill` MCP недоступен — скрипт требует `playwright` в CWD и нарушает глобальное правило «не поднимать отдельный Chromium».
