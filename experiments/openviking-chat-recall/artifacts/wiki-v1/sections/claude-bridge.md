---
type: index
title: Вызов Claude через мост 1claude-mcp
description: Какие модели можно вызывать через 1claude-mcp, какую роль владелец отводит Claude, как писать для него промпты и что умеет инструмент claude_sessions
topic: claude-bridge
---
# Вызов Claude через мост 1claude-mcp

Какие модели можно вызывать через 1claude-mcp, какую роль владелец отводит Claude, как писать для него промпты и что умеет инструмент claude_sessions

- [Как должен пройти полный рефактор `1claude-mcp`?](../method/claude-mcp-full-refactor.md) — По контракту `1skill-shaping`, с проверкой кода против изменений инструмента Claude и переработкой инструкций по протоколу упрощения.
- [Как обновлять Claude Code и Agent SDK?](../method/updating-claude-code-agent-sdk.md) — Решение владельца — обновить до последней версии и провести полный проверочный цикл.
- [Как писать промпты для Claude?](../concept/writing-prompts-for-claude.md) — Критерий владельца — по лучшим практикам Anthropic, отталкиваясь от цели и проблемы, без предписания модели хода мыслей или действий.
- [Какие модели можно вызывать через `1claude-mcp`?](../entity/claude-mcp-allowed-models.md) — Модельная граница `1claude-mcp`: Fable запрещена, использовать только Opus.
- [Какую роль владелец отводит Claude в своей работе?](../concept/claude-advisor-reviewer-role.md) — Роль Claude по решению владельца — советник/ревьюер, подключаемый до начала работы и параллельно во время неё.
- [Может ли Claude читать другие файлы?](../concept/claude-file-read-access.md) — Право Claude читать другие файлы закреплено критерием владельца.
- [Что умеет MCP tool `claude_sessions`?](../entity/claude-sessions-tool.md) — Read-only инструмент для списка активных локальных Claude-сессий и чтения видимой переписки; необязательная дополнительная возможность.
