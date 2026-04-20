# Plan — Упростить design-auditor до 3 линз (2026-04-17)

Контекст: [projects/design/design-auditor--skill-claude-code/audit-2026-04-17.md](../../projects/design/design-auditor--skill-claude-code/audit-2026-04-17.md).

## Цель

Сохранить центральную идею скилла (ортогональные профессиональные линзы по одному UI), но упростить: 5 агентов → 3, sonnet → opus, убрать хрупкий capture-скрипт, починить runtime-баг dispatch и оформление по `perfect-skills.md`.

## Статус

Исполнено 2026-04-17 в два шага:
1. 2.0.0 → 3.0.0 (упрощение) — задокументировано в [projects/design/design-auditor--skill-claude-code/changes-2026-04-17.md](../../projects/design/design-auditor--skill-claude-code/changes-2026-04-17.md).
2. 3.0.0 → deprecated (выпил, замена на playbook) — задокументировано в [projects/design/design-auditor--skill-claude-code/decision-2026-04-17.md](../../projects/design/design-auditor--skill-claude-code/decision-2026-04-17.md).

Финальная замена — [`knowledge/guides/design-review-playbook.md`](../../knowledge/guides/design-review-playbook.md).

## Что сделано

1. Удалены 5 старых агентов, `scripts/capture_page.mjs`.
2. Созданы 3 новых агента (`structure`, `craft`, `identity`), `model: opus`, `name:` в kebab-case совпадает с filename.
3. Переписан SKILL.md: тонкий, flexible, с «когда не использовать», «done when», output contract, «настойчивым» description.
4. `plugin.json`, `marketplace.json`, `installed_plugins.json` обновлены до 3.0.0.
5. Cache пересобран в `~/.claude/plugins/cache/design-auditor/design-auditor/3.0.0/`.
6. `allowed-tools` в SKILL.md сжат до `Read, Agent` (Bash больше не нужен).

## Что нужно проверить отдельной сессией

- Новой сессией убедиться, что в списке доступных `subagent_type` больше нет `design-auditor:*` — плагин должен полностью отвалиться после рестарта.
- Прогнать пару тестовых запросов («разбери этот скрин», «дизайн аудит https://…», «это AI slop?»), убедиться, что триггеры корректно уходят в `screenshot-design`, `playwright-skill` mode 2 + `screenshot-design`, `impeccable:critique`.
- Если в реальной работе обнаружится сценарий, который playbook не покрывает и который реально повторяется — рассматривать как кандидат на новый узкий скилл, не как повод восстановить design-auditor.
