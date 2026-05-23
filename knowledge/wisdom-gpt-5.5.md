# Wisdom — GPT-5.5

Снимок на 22 мая 2026.

Здесь живут только правила, которые важны именно для `GPT-5.5`. Общие свойства
LLM держит `wisdom-llm.md`; платформенные правила Codex держит
`wisdom-codex.md`.

## Проверено

- Начинать с outcome, constraints, allowed side effects, evidence rules, output shape и stop condition.
- Не переносить старый process-heavy stack как есть. Пошаговый процесс нужен только там, где порядок сам является требованием продукта.
- `reasoning.effort` и `text.verbosity` считать runtime-настройками, а не текстом prompt.
- `medium` — базовый режим для сложной, но обычной работы; `low` проверять для быстрых tool/planning задач; `high` и `xhigh` включать только по сложности или eval-сигналу.
- Tool-specific guidance чаще класть в tool descriptions, а не в общий системный prompt. В prompt оставлять только policy, общий для tools.
- Для большого tool surface использовать narrow descriptions и tool search / deferred discovery, а не грузить весь каталог в основной контекст.
- Для long-running Responses agents сохранять continuation state: completed actions, active assumptions, IDs, tool outcomes, blockers и next concrete goal. Технически — `previous_response_id` или round-trip output items.
- Для Responses workflows не терять assistant items, `phase` для preambles/final и compaction после больших milestones. Иначе preamble может стать ложным финалом.
- Compact outcome-first context обычно лучше старого defensive repetition; повторять главное правило в нескольких местах только при доказанном partial-loading risk.
- В `AGENTS.md` / `.cursor/rules` особенно вредны vague или conflicting
  instructions: GPT-5.5 лучше следует правилам, поэтому плохая конкретика
  сильнее backfire-ит.
- Папочные инструкции должны уменьшать exploration и validation failures, а не
  добавлять красивые требования. Если правило не меняет решение агента, убрать.
- Для дорогих ограничений текст не считать enforcement: ставить test,
  validator, hook или явный checkpoint.

## Что Не Делать

- Не лечить слабый task contract ростом prompt.
- Не держать старую историю процесса, если она не меняет следующий ход.
- Не повышать effort как универсальную ручку качества.
- Не превращать skill body в длинный ритуал, если GPT-5.5 держит задачу по outcome и evidence.
- Не оптимизировать folder layout как магическую ручку adherence; свежая
  эмпирика по coding-agent config files не показывает такого эффекта.

## Где Использовать

- `perfect-system-prompts.md` — при написании системных промптов.
- `perfect-context-engineering.md` — при сборке контекста.
- `practical-guides/how-to-write-skills/` — при authoring skills.
- `wisdom-codex.md` — когда GPT-5.5 работает внутри Codex-подобного coding agent.

## Опоры

- https://developers.openai.com/api/docs/guides/latest-model
  Модельная guidance про outcome-first prompts, reasoning effort, state и tool-heavy workflows.

- https://platform.openai.com/docs/api-reference/responses
  Responses state, output items и reasoning settings.

- https://cdn.openai.com/API/docs/gpt-5-for-coding-cheatsheet.pdf
  GPT-5 coding guidance: точность, отсутствие конфликтов и аккуратный
  reasoning effort.

- https://arxiv.org/abs/2602.11988
  Empirical warning: unnecessary requirements in AGENTS/context files can lower
  success and raise cost.
