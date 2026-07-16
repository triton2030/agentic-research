---
read-before-edit:
  - '[[AGENTS.md]]'
  - '[[_ops/GOAL.md]]'
edit-after-edit: []
description: Snapshot-пакет карт hook surfaces для Codex и Claude.
---

# Обзор Хуков

Папка содержит две самодостаточные HTML-карты:

* [`codex-hooks.html`](https://github.com/triton2030/agentic-research/blob/main/experiments/%D0%BE%D0%B1%D0%B7%D0%BE%D1%80-%D1%85%D1%83%D0%BA%D0%BE%D0%B2/codex-hooks.html) — активные Codex hooks.
* [`claude-hooks.html`](https://github.com/triton2030/agentic-research/blob/main/experiments/%D0%BE%D0%B1%D0%B7%D0%BE%D1%80-%D1%85%D1%83%D0%BA%D0%BE%D0%B2/claude-hooks.html) — активные Claude hooks.

## Что Обязано Быть В Карте

* live sources: где лежит wiring и где лежат hook/plugin files;
* active hooks: событие, matcher, действие, state, видимый результат;
* agent-visible examples: короткий пример injected context/reminder/status, который агент реально получает после hook-а;
* inactive/legacy: отдельный блок для файлов, которые есть на диске, но не подключены;
* дата snapshot-а.

## Чего Не Должно Быть

* тела hook-скриптов;
* shell-команды запуска;
* длинные prompt dumps;
* общий материал о том, зачем hooks нужны;
* второй source of truth рядом с live config/settings.

## Как Обновлять

1. Прочитать live wiring:
   * Codex: `~/.codex/config.toml`, `~/.codex/hooks.json`;
   * Claude: `~/.claude/settings.json`, enabled plugin hook bundles.
2. Проверить hook files только чтобы понять behavior и agent-visible output.
3. Обновить HTML-карту конкретного runtime.
4. Проверить desktop и mobile rendering.
5. Если новый active hook меняет project scope, done или stop rule,
   остановиться и сверить `_ops/GOAL.md`; обычное runtime wiring остаётся
   в live config/settings, а не во втором project registry.
