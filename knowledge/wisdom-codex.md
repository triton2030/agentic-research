# Wisdom — Codex

Снимок на 28 апреля 2026.

Здесь только платформенные наблюдения про Codex, которые важны независимо от домена.
Доменные выводы держим в category `_research/`.

## Проверено

- Для orchestration в Codex чище опираться на thread-based модель и SDK, чем на хрупкий CLI scraping.
- Agent-friendly CLI особенно важны там, где агент работает через terminal workflow.
- В Codex базовыми строительными блоками выступают subagents, skills и plugins:
  subagents ускоряют независимые evidence/implementation streams, skills
  фиксируют workflow, plugins пакуют workflow вместе с integrations и MCP.
  Синтез, blocking step и integration остаются в main context.
- Для GPT-5.5 в Codex-подобных coding agents применять
  `knowledge/wisdom-gpt-5.5.md`; здесь держать только Codex-specific выводы.
- Для большого tool surface использовать narrow descriptions и tool search,
  а не грузить весь каталог в системный контекст.
- Внешние обвязки вокруг Codex полезны как источник паттернов, но не как замена официальному стеку по умолчанию.

## Опоры

- https://developers.openai.com/codex/sdk
  Основная опора для thread-based orchestration.

- https://developers.openai.com/api/docs/guides/latest-model
  GPT-5.5 migration posture для coding, tool-heavy agents и prompt tuning.

- https://developers.openai.com/codex/use-cases/agent-friendly-clis
  Подход к CLI, которые удобны для агентной работы.

- https://github.com/milisp/codexia
  GUI и operational shell вокруг Codex CLI.

- https://github.com/leonardsellem/codex-subagents-mcp
  Codex-specific MCP-обвязка для специализированных subagents.
