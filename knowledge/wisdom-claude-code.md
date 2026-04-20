# Wisdom — Claude Code

Снимок на 20 апреля 2026.

Здесь только платформенные наблюдения про Claude Code, которые важны независимо от домена.
Доменные выводы держим в category `_research/`.

## Проверено

- Claude Code особенно полезен как reference-среда для внешнего слоя контроля: hooks, approvals и ограничений на действия.
- Hooks — наиболее наглядный путь вынести критические ограничения из текста prompt в слой исполнения.
- Human approval в workflows с внешними действиями нужно трактовать как часть архитектуры, а не как необязательную UX-деталь.
- Для Claude Opus 4.7 важнее явный scope, чем "умный" намёк. Модель следует инструкциям более буквально: если правило должно применяться ко всем секциям, файлам или шагам, это нужно писать явно.
- Для Claude Opus 4.7 `effort` стал одним из главных рычагов поведения. На `low` и `medium` модель заметно строже держится буквального запроса и меньше "идёт дальше сама"; для intelligence-sensitive задач безопаснее начинать с `high`, а для coding/agentic work — с `high` или `xhigh`.
- Не компенсировать низкий `effort` раздутым системным промптом. Сначала настраивать `effort`, потом чинить точечные провалы в инструкциях.
- Claude Opus 4.7 по умолчанию реже использует tools и спаунит меньше subagents, чем Opus 4.6. Если нужен более инструментальный или fan-out режим, это надо задавать явно в инструкции.
- Claude Opus 4.7 уже лучше даёт progress updates в длинных agentic traces. Старый scaffolding вида "после каждых N tool calls отчитайся" стоит убирать и переснимать baseline, а не тащить по инерции.
- В Claude Code свободные скиллы и plugin-скиллы — это разные слои упаковки: свободные видит модель, но не UI `/plugin`; plugin-скиллы имеют namespace, версию, источник и toggle.
- Быстрый личный workflow разумно держать как свободный skill, а sharable и управляемую связку skills и agents — как plugin.
- Committed project learnings (`ops/learnings.md` или аналог в репо) превращает индивидуальный опыт в team knowledge: любой член команды начинает сессию с накопленного контекста. Это отличает Claude Code от single-user memory-систем, где опыт заперт в профиль одного пользователя.
- Self-learning skill должен быть связкой из трёх петель: read-before, capture-after и periodic-prune. Любая из трёх без остальных деградирует файл: без read — контекст не влияет, без capture — не обновляется, без prune — превращается в мусор.

### Agent tool

- Agent tool поддерживает специализированные `subagent_type`: `Explore` (поиск по кодовой базе), `Plan` (архитектурный дизайн), `general-purpose`, design-auditor-варианты и plugin-dev-варианты — у каждого свой набор инструментов.
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

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  Живой Anthropic reference по prompt engineering для Claude 4.x и Opus 4.7: явность инструкций, scope, tool policy, thinking, long context.

- https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7
  Краткая карта behavioural changes и новых рычагов Opus 4.7.

- https://platform.claude.com/docs/en/about-claude/models/migration-guide
  Что именно меняется при переходе на Opus 4.7: literalness, effort, tool use, verbosity, task budgets.

- https://docs.anthropic.com/en/docs/claude-code/hooks-guide
  Практика hooks как внешнего слоя контроля.

- https://docs.anthropic.com/en/docs/build-with-claude/computer-use
  Approval, уровни риска и контроль внешних действий.

- `/knowledge/practical-guides/claude-code-plugins-vs-skills.md`
  Короткая операционная памятка по различию между свободными skills и plugins в Claude Code.
