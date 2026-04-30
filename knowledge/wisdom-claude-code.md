# Wisdom — Claude Code

Снимок на 28 апреля 2026.

Здесь только платформенные наблюдения про Claude Code. Модельные различия для
Opus 4.7 держит `knowledge/wisdom-claude-opus-4.7.md`; доменные выводы держим в
`knowledge/research/{category}/`.

## Проверено

- Claude Code особенно полезен как reference-среда для внешнего слоя контроля: hooks, approvals и ограничений на действия.
- Hooks — наиболее наглядный путь вынести критические ограничения из текста prompt в слой исполнения.
- Human approval в workflows с внешними действиями нужно трактовать как часть архитектуры, а не как необязательную UX-деталь.
- Для Opus 4.7-specific scope, effort, tool policy и progress guidance читать
  `knowledge/wisdom-claude-opus-4.7.md`.
- В Claude Code свободные скиллы и plugin-скиллы — это разные слои упаковки: свободные видит модель, но не UI `/plugin`; plugin-скиллы имеют namespace, версию, источник и toggle.
- Быстрый личный workflow разумно держать как свободный skill, а sharable и управляемую связку skills и agents — как plugin.
- Committed project criteria (`_ops/criteria/*.md` или аналог в репо)
  превращают устойчивые уроки в team knowledge: любой член команды начинает с
  критериев приёмки, а не с личной памяти одного пользователя.
- Self-learning criteria layer должен быть связкой из трёх петель: read-before,
  capture-after и periodic-prune. Любая из трёх без остальных деградирует файл:
  без read — контекст не влияет, без capture — не обновляется, без prune —
  превращается в мусор.

### Agent tool

- Agent tool поддерживает специализированные `subagent_type`: `Explore` (поиск по кодовой базе), `Plan` (архитектурный дизайн), `general-purpose`, design-auditor-варианты и plugin-dev-варианты — у каждого свой набор инструментов.
- Parallel agents включать только когда есть независимые файлы, evidence
  streams или leaf implementation; модельная причина и anti-fan-out правило
  живут в `knowledge/wisdom-claude-opus-4.7.md`.
- Параллельные агенты запускаются в одном сообщении несколькими `Agent` tool call — они выполняются одновременно.
- `run_in_background: true` — агент не блокирует ход работы; результат приходит уведомлением. Никакого polling или sleep.
- `isolation: "worktree"` — создаётся изолированный git worktree; очищается автоматически, если агент не делал изменений.
- Агент не видит текущий разговор. Промпт должен быть self-contained: пути к файлам, номера строк, что именно изменить, что уже проверено.
- "Never delegate understanding": нельзя писать "по результатам исследования исправь баг" — агент получает конкретику, синтез остаётся в главном контексте.
- Результат агента не виден пользователю напрямую — нужно явно пересказывать находки в текстовом ответе.
- Subagent для исследования: `Explore` достаточно для поиска файлов по паттернам или ключевым словам; `general-purpose` — для многошаговых открытых исследований.

### Deferred Tools

- Часть инструментов (TodoWrite, WebFetch, WebSearch, EnterPlanMode и др.) не загружена по умолчанию. Вызов без загрузки → `InputValidationError`.
- Перед вызовом такого инструмента: `ToolSearch("select:ToolName")` — получить полную JSON-схему параметров.
- Паттерн: `ToolSearch → получить схему → вызвать инструмент`.

## Опоры

- `knowledge/wisdom-claude-opus-4.7.md`
  Модельный baseline для Opus 4.7.

- https://docs.anthropic.com/en/docs/claude-code/hooks-guide
  Практика hooks как внешнего слоя контроля.

- https://docs.anthropic.com/en/docs/build-with-claude/computer-use
  Approval, уровни риска и контроль внешних действий.

- `/knowledge/practical-guides/claude-code-plugins-vs-skills.md`
  Короткая операционная памятка по различию между свободными skills и plugins в Claude Code.
