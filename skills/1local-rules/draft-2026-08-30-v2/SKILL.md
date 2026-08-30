---
name: 1local-rules
description: >-
  Use when an ordinary skill is being created, updated, or retired as a
  project-local 2* skill for both Claude and Codex.
---

# Локальные скилы

## Уникальный контекст

Локальный скил — обычный скил одного проекта с префиксом `2` и проекциями для
Claude и Codex. Общий authoring принадлежит `1skill-creation`.

## Результат

При создании или обновлении вызови `$1skill-creation` на финальном кандидате,
который уже:

- package активен только в одном целевом проекте;
- имя пакета начинается с цифры `2`;
- содержание совместимо с применимыми глобальными инструкциями Claude и Codex
  и корневыми инструкциями своего проекта.

Перед установкой, обновлением или снятием выполни [проверку
совместимости](references/conflict.md), а после неё —
[синхронизацию](references/sync.md). Для `2*` эти режимы исполняют installation-
обязательства `$1skill-creation`, а не создают второй install.
