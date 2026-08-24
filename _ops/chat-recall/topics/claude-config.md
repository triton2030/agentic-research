---
topic: claude-config
title: Состав глобального окружения Claude Code: настройки, MCP и стартовый след агентов
sources: 1
---
# Состав глобального окружения Claude Code: настройки, MCP и стартовый след агентов

Граница темы: обе реплики решают состав глобального окружения Claude Code — отключаемые ключи settings.json, снос MCP-сервера и стартовый контекстный след агентов, — а существующие темы покрывают только инструкции, routing skills или внешние provider-мосты, не сам runtime-конфиг.

## Добавлено 2026-08-24

- Владелец решил внести в ~/.claude/settings.json ключи disableClaudeAiConnectors, disableBundledSkills, disableWorkflows, disableArtifact, autoMemoryEnabled: false, отключающие Claude AI connectors, встроенные скилы, workflows, artifacts и auto-memory, а также блок permissions с deny-списком и defaultMode: bypassPermissions. [2026-08-22-165215-claude-88b5677e.md#L15]
- Владелец решил, что MCP-сервер clickup можно полностью удалить. [2026-08-22-165215-claude-88b5677e.md#L16]
- По агентам в ~/.claude/agents владелец решения не принял: он не уверен, что при старте любой сессии у агентов видны только короткие имена, а весь текст агента не загружается. [2026-08-22-165215-claude-88b5677e.md#L16]

