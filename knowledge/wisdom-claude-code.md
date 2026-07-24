# Wisdom — Claude Code

Снимок на 22 июля 2026.

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
- Raw user-said capture (`_ops/user-said/YYYY-MM-DD.md` или аналог)
  фиксирует цитаты без классификации;
  rules/instructions/decisions — только manual pass.
- Self-learning требует петлю
  `read-before → capture-after → periodic-prune`;
  убрать одну часть — слой деградирует.

### Skills and plugins

- Free skills видит модель, но не UI `/plugin`.
  Plugin skills имеют namespace, version, source и toggle.
- Быстрый личный workflow — free skill.
  Sharable управляемая связка skills/agents/hooks/MCP/commands — plugin.

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

## Опоры

- `knowledge/wisdom-claude-opus-5.md` — model-level baseline для Opus 5.
- `knowledge/wisdom-claude-fable-5.md` — отдельный Fable 5 baseline.
- `knowledge/practical-guides/how-to-write-skills/platform-deltas.md` —
  Claude Code skills, free skills и plugin packaging.
- https://docs.anthropic.com/en/docs/claude-code/hooks-guide — hooks как внешний
  слой контроля.
- https://docs.anthropic.com/en/docs/build-with-claude/computer-use — approvals,
  risk levels и контроль внешних действий.
- https://code.claude.com/docs/en/model-config — live model aliases, overrides и
  фактически resolved model в machine-readable output.
- https://code.claude.com/docs/en/slash-commands — Claude skill discovery,
  frontmatter, invocation и runtime semantics.
- https://code.claude.com/docs/en/sub-agents — background defaults, IDs,
  `SendMessage` resume и current custom-agent runtime.
