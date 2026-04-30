# Wisdom — GPT-5.5

Снимок на 29 апреля 2026.

Здесь живут только правила, которые важны именно для `GPT-5.5`. Общие свойства
LLM держит `wisdom-llm.md`; платформенные правила Codex держит
`wisdom-codex.md`.

## Проверено

- Начинать с outcome, constraints, allowed side effects, evidence rules, output shape и stop condition.
- Не переносить старый process-heavy stack как есть. Пошаговый процесс нужен только там, где порядок сам является требованием продукта.
- `reasoning.effort` и `text.verbosity` считать runtime-настройками, а не текстом prompt.
- `medium` — базовый режим для сложной, но обычной работы; `low` проверять для быстрых tool/planning задач; `high` и `xhigh` включать только по сложности или eval-сигналу.
- Tool-specific guidance чаще класть в tool descriptions, а не в общий системный prompt.
- Для большого tool surface использовать narrow descriptions и tool search / deferred discovery, а не грузить весь каталог в основной контекст.
- Для long-running Responses agents сохранять continuation state: completed actions, active assumptions, IDs, tool outcomes, blockers и next concrete goal.
- Для Responses workflows не терять assistant items, `phase` для preambles/final и compaction после больших milestones.
- Compact outcome-first context обычно лучше старого defensive repetition; повторять главное правило в нескольких местах только при доказанном partial-loading risk.

## Что Не Делать

- Не лечить слабый task contract ростом prompt.
- Не держать старую историю процесса, если она не меняет следующий ход.
- Не повышать effort как универсальную ручку качества.
- Не превращать skill body в длинный ритуал, если GPT-5.5 держит задачу по outcome и evidence.

## Где Использовать

- `perfect-system-prompts.md` — при написании системных промптов.
- `perfect-context-engineering.md` — при сборке контекста.
- `perfect-skills.md` и practical guides — при authoring skills.
- `wisdom-codex.md` — когда GPT-5.5 работает внутри Codex-подобного coding agent.

## Опоры

- https://developers.openai.com/api/docs/guides/latest-model
  Модельная guidance про outcome-first prompts, reasoning effort, state и tool-heavy workflows.

- https://platform.openai.com/docs/api-reference/responses
  Responses state, output items и reasoning settings.
