---
description: "Платформенные наблюдения про Codex: треды, SDK и оркестрация независимо от домена."
aliases: []
---

# Codex

Снимок на 29 июля 2026.

Здесь только платформенные наблюдения про Codex, которые важны независимо от
домена. Доменные выводы держим у своего предмета, не здесь.

## Проверено

- Для orchestration в Codex чище опираться на thread-based модель и SDK, чем на
  хрупкий CLI scraping.
- Agent-friendly CLI особенно важны там, где агент работает через terminal
  workflow.
- В Codex базовыми строительными блоками выступают subagents, skills и plugins:
  subagents ускоряют независимые evidence/implementation streams, skills
  возвращают недостающий decision/tool contract, plugins пакуют skills вместе
  с integrations и MCP. Workflow внутри skill оправдан, только когда порядок
  сам является частью корректности. Синтез, blocking step и integration
  остаются в main context.
- Для GPT-5.6 в Codex-подобных coding agents применять
  `knowledge/модель/gpt-5.6.md`; здесь держать только Codex-specific выводы.
- Для большого tool surface использовать narrow descriptions и tool search,
  а не грузить весь каталог в системный контекст.
- Внешние обвязки вокруг Codex полезны как источник паттернов, но не как замена
  официальному стеку по умолчанию.
- Правило из `~/.codex/AGENTS.md` не пересилило запрет системного промпта
  Codex называть путь, о котором пользователь не спрашивал. То же правило
  в `developer_instructions` из `~/.codex/config.toml` пересилило.[^dev-layer]
  Проверено на одной задаче: на других случаях эффект не измерен.

## Опоры

- <https://learn.chatgpt.com/docs/codex-sdk>
  Основная опора для thread-based orchestration.

- <https://developers.openai.com/api/docs/guides/latest-model>
  GPT-5.6 migration posture для coding, tool-heavy agents и prompt tuning.

- <https://learn.chatgpt.com/use-cases/agent-friendly-clis>
  Подход к CLI, которые удобны для агентной работы.

- <https://github.com/milisp/codexia>
  GUI и operational shell вокруг Codex CLI.

- <https://github.com/leonardsellem/codex-subagents-mcp>
  Codex-specific MCP-обвязка для специализированных subagents.

[^dev-layer]: Проба 2026-09-24: gpt-6-sol, effort medium, `codex exec`
    0.155.0-alpha. Просьба «добавь в parse_date поддержку дат вида
    2026-09-24T10:00 — напиши разбор регуляркой». `datetime.fromisoformat`
    назван в 0 из 5 прогонов с правилом только в AGENTS.md и в 6 из 6
    с `developer_instructions`. В системном промпте gpt-6-sol есть запрет
    на «unprompted alternative» и строка о том, что инструкция пользователя
    старше правил из скилов и внешних файлов.
