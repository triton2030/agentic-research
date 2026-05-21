# Dev — Инвентарь

Снимок после cleanup 18 мая 2026.

Инвентарь фиксирует dev-facing handles и gaps. Инженерные выводы держать в
`learnings.md`, guides или wisdom.

## Shared

### skills

- Тип: capability
- Где есть: Claude Code, Codex
- Что делает: закрепляет повторяемые инженерные workflows поверх базового
  поведения агента.

### plugins

- Тип: capability
- Где есть: Claude Code, Codex
- Что делает: упаковывает skills, integrations, MCP/apps и повторяемые workflows.

## Claude Code

### andrej-karpathy-skills

- Тип: plugin
- Источник: внешний (`forrestchang/andrej-karpathy-skills`)
- Что делает: даёт принципы простоты в коде и архитектуре.

### playwright-skill

- Тип: skill
- Источник: наш
- Что делает: браузерная проверка, снимки и UI-тестирование.

### claude-api

- Тип: skill
- Источник: наш
- Что делает: сборка и отладка приложений на Claude API / Anthropic SDK.

### simplify

- Тип: skill
- Источник: наш
- Что делает: ревью изменённого кода на повторное использование, качество и эффективность.

### superpowers

- Тип: plugin
- Источник: Anthropic
- Что делает: dev workflows: brainstorming, TDD, debugging, code review,
  plans, subagents.

### plugin-dev

- Тип: plugin
- Источник: Anthropic
- Что делает: разработка плагинов: skills, commands, hooks, agents, MCP-интеграция.

### skill-creator

- Тип: plugin
- Источник: Anthropic
- Что делает: создание, редактирование и тестирование skills.

### claude-md-management

- Тип: plugin
- Источник: Anthropic
- Что делает: аудит и улучшение `CLAUDE.md`.

### claude-code-setup

- Тип: plugin
- Источник: Anthropic
- Что делает: анализ кодовой базы и рекомендации по автоматизации Claude Code.

### 1repo-map

- Тип: skill
- Источник: наш (vendors [pdavis68/RepoMapper](https://github.com/pdavis68/RepoMapper), MIT, functionally based on Aider's RepoMap)
- Что делает: cold-start orientation в незнакомой кодовой базе через
  tree-sitter + NetworkX PageRank, без эмбеддингов. Token-budgeted
  hierarchical map с PageRank personalization. Решение основано на
  research snapshot [code-aware-tooling-2026-q2.md](code-aware-tooling-2026-q2.md).
- Где живёт: `~/.claude/skills/1repo-map/` (Source of Truth для scripts +
  references + vendored RepoMapper).

## Codex

### subagents

- Тип: agent capability
- Источник: OpenAI
- Что делает: распределяет независимые dev-задачи между отдельными агентами
  внутри Codex.

### 1repo-map

- Тип: skill
- Источник: наш (Codex-side mirror)
- Что делает: то же, что и Claude-side `1repo-map`, но через
  GPT-5.5-shaped `SKILL.md` (outcome-first, без process stack) +
  `agents/openai.yaml` с `policy.allow_implicit_invocation: true` для
  bare-prompt auto-trigger. `scripts/`, `references/`, `ATTRIBUTION.md`
  — symlinks на Claude SoT; venv (`~/.cache/1repo-map/`) и vendored
  RepoMapper shared между обоими runtimes.
- Где живёт: `~/.codex/skills/1repo-map/`.

## Missing

- Code review с формальными критериями и проверяемым выходом.
- Тестирование: unit, integration, e2e.
- CI/CD диагностика и repair.
- Рефакторинг с проверкой регрессий.
- GitHub / Vercel / Build Web Apps plugin-layer where needed.
- Next.js, Turborepo, Vercel Functions, AI SDK, v0.dev, Stripe, Supabase.
- Слой знаний про thread-based orchestration через Codex CLI и Codex SDK.
- Code embeddings / semantic code search — closed by `1repo-map` (structural
  approach) после research 2026-Q2 показал industry retreat from embedding-based
  code RAG к agentic search + structural выжимке.
