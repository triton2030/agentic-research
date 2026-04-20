# Wisdom — Codex

Снимок на 16 апреля 2026.

Здесь только платформенные наблюдения про Codex, которые важны независимо от домена.
Доменные выводы держим в category `_research/`.

## Проверено

- Для orchestration в Codex чище опираться на thread-based модель и SDK, чем на хрупкий CLI scraping.
- Agent-friendly CLI особенно важны там, где агент работает через terminal workflow.
- В Codex базовыми строительными блоками выступают subagents, skills и plugins: первый слой распределяет работу, второй фиксирует workflow, третий пакует workflow вместе с integrations и MCP.
- Внешние обвязки вокруг Codex полезны как источник паттернов, но не как замена официальному стеку по умолчанию.

## Опоры

- https://developers.openai.com/codex/sdk
  Основная опора для thread-based orchestration.

- https://developers.openai.com/codex/use-cases/agent-friendly-clis
  Подход к CLI, которые удобны для агентной работы.

- https://github.com/milisp/codexia
  GUI и operational shell вокруг Codex CLI.

- https://github.com/leonardsellem/codex-subagents-mcp
  Codex-specific MCP-обвязка для специализированных subagents.
