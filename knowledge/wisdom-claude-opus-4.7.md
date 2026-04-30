# Wisdom — Claude Opus 4.7

Снимок на 29 апреля 2026.

Здесь живут только правила, которые важны именно для `Claude Opus 4.7`. Общие
свойства LLM держит `wisdom-llm.md`; платформенные правила Claude Code держит
`wisdom-claude-code.md`.

## Проверено

- Явный scope важнее умного намёка. Если правило должно применяться ко всем секциям, файлам, шагам или артефактам, это нужно писать прямо.
- `effort` — главный рычаг поведения. Низкий effort не лечить длинным prompt; сначала выбрать правильный режим, потом чинить точечные провалы.
- На `low` и `medium` модель строже держится буквального запроса и меньше идёт дальше сама.
- Для intelligence-sensitive задач безопаснее начинать с `high`; для coding/agentic work — с `high` или `xhigh`, если качество важнее скорости.
- Tool/subagent policy задавать явно. Opus 4.7 чаще думает сам и реже зовёт tools/subagents без причины.
- Не компенсировать редкую авто-делегацию автоматическим fan-out. Параллельные агенты нужны только при независимых файлах, evidence streams или leaf implementation.
- Progress updates уже лучше держатся без старого scaffolding; прогресс-ритуалы оставлять только если baseline без них проседает.
- При `xhigh`/`max` effort нужен большой `max_tokens` headroom, иначе thinking/tool/subagent loop может не поместиться.
- Для open-ended agentic задач task budget задавать только если нужна самоограниченность по расходу; для quality-first работы budget может ухудшить исследование.
- Если продукт показывал reasoning/progress из thinking blocks, thinking content может быть скрыт; нужен явный summarized display.

## Что Не Делать

- Не надеяться, что Opus сам распространит локальное правило на весь набор артефактов.
- Не заменять tool policy общим пожеланием “будь инициативным”.
- Не тащить старые self-check и periodic-progress правила без свежей проверки.
- Не делать автоматический fan-out только потому, что модель стала меньше делегировать сама.

## Где Использовать

- `perfect-system-prompts.md` — при написании системных промптов.
- `perfect-context-engineering.md` — при сборке длинного контекста.
- `perfect-skills.md` и `practical-guides/claude-code-skills.md` — при authoring Claude skills.
- `wisdom-claude-code.md` — когда Opus 4.7 работает внутри Claude Code.

## Опоры

- https://docs.anthropic.com/ko/release-notes/claude-apps
  Release notes с запуском Claude Opus 4.7.

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
  Prompt engineering guidance: явность инструкций, scope, tool policy, thinking и long context.

- https://platform.claude.com/docs/en/about-claude/models/migration-guide
  Migration guidance по literalness, effort, tool use, verbosity и task budgets.
