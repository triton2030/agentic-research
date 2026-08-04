---
description: "Claude Code platform baseline: context, skills, tools, memory, agents and control surfaces."
---

# Wisdom — Claude Code

Снимок на 25 июля 2026.

Только platform-level поведение Claude Code.

Model-level baselines держат `knowledge/wisdom-claude-opus-5.md` и
`knowledge/wisdom-claude-fable-5.md`.
Доменные выводы — `knowledge/research/{category}/`.
Skill deltas —
`knowledge/practical-guides/how-to-write-skills/platform-deltas.md`.

Главная рамка:
Claude Code — reference-среда для внешнего контроля,
packaging и управляемых agents,
не просто chat/coding surface.

## Проверено

### Control surface

- Hooks выносят hard limits из prompt в execution layer.
- Human approval для внешних действий — архитектурная граница, не UX-деталь.
- Считать system prompt, цепочку `CLAUDE.md`, загруженные skills, tool
  descriptions, auto-memory и task references одной context surface.
  Проверять конфликт и повтор между слоями, а не длину одного файла.
- `CLAUDE.md` держать лёгким repo-router: назначение проекта и неочевидные
  gotchas. Общий workflow выносить в skill/reference, инструкции к инструменту
  — в его description/schema; очевидное из файловой структуры не пересказывать.
- Auto-memory владеет runtime-персонализацией и повторно полезными фактами о
  работе; `CLAUDE.md` — устойчивыми repo-инструкциями; project canon — текущей
  истиной. Source-bound цитаты пользователя остаются отдельным workflow, а не
  сырьём для автоматического переписывания instructions.
- `claude doctor` проверяет installation/settings health. Полный `/doctor`
  внутри сессии может предложить rightsizing и исправления; его findings —
  candidates для ручного semantic review и with/without eval, не разрешение на
  автоматическую правку.

### Skills and plugins

- Free skills видит модель, но не UI `/plugin`.
  Plugin skills имеют namespace, version, source и toggle.
- Быстрый личный workflow — free skill.
  Sharable управляемая связка skills/agents/hooks/MCP/commands — plugin.
- Для Opus 5 и Fable 5 skill — лёгкий guide к недостающему decision/tool
  contract и нужной информации.
  Жёсткий процесс оправдан high-risk boundary или измеренным failure mode;
  остальное оставлять judgement модели и progressive disclosure.

### Agent tool

- `subagent_type` выбирает tool surface:
  `Explore` для codebase search,
  `Plan` для архитектуры,
  `general-purpose` для открытого исследования,
  плюс design-auditor/plugin-dev варианты.
- Parallel agents — только для независимых файлов, evidence streams или leaf
  implementation; write ownership и root synthesis остаются обязательными.
- Для custom/general-purpose subagents отсутствие `background` не означает
  старый blocking default: runtime обычно запускает их в фоне. Workflow должен
  явно решить, продолжает ли root параллельно и когда result обязателен для
  synthesis.
- `run_in_background: true` даёт уведомление, без polling/sleep.
  `isolation: "worktree"` создаёт worktree и чистит его, если изменений не было.
- Завершённый custom/general-purpose subagent продолжать через
  `SendMessage(to: agent_id|name)`; новый `Agent` создаёт fresh context.
  Built-in Explore/Plan не возвращают resumable ID.
- Агент не видит текущий разговор;
  prompt включает paths, lines, task и checked evidence.
- Never delegate understanding:
  главный контекст синтезирует;
  агент получает конкретный search/change request.
- Результат агента не виден пользователю напрямую — находки пересказать.

### Deferred tools

- Deferred tools могут не быть загружены в текущий tool surface.
  Вызов без загрузки даёт `InputValidationError`.
- Паттерн: `ToolSearch("select:ToolName") → schema → tool call`.
- Tool-use contract держать в выразительном interface: понятные параметры,
  enum, constraints и короткий description. Примеры добавлять, только если
  schema не передаёт неочевидный формат, вкус или известный failure mode.

## Опоры

- `knowledge/wisdom-claude-opus-5.md` — model-level baseline для Opus 5.
- `knowledge/wisdom-claude-fable-5.md` — отдельный Fable 5 baseline.
- `knowledge/practical-guides/how-to-write-skills/platform-deltas.md` —
  Claude Code skills, free skills и plugin packaging.
- <https://code.claude.com/docs/en/hooks-guide> — hooks как внешний
  слой контроля.
- <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool> — approvals,
  risk levels и контроль внешних действий.
- <https://code.claude.com/docs/en/model-config> — live model aliases,
  overrides и фактически resolved model в machine-readable output.
- <https://code.claude.com/docs/en/slash-commands> — Claude skill discovery,
  frontmatter, invocation и runtime semantics.
- <https://code.claude.com/docs/en/sub-agents> — background defaults, IDs,
  `SendMessage` resume и current custom-agent runtime.
- <https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models>
  Официальный Claude 5 context-engineering baseline: judgement вместо
  obsolete rules, interface-first tools, progressive disclosure, lightweight
  `CLAUDE.md`, auto-memory и rich references.
