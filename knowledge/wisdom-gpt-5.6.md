# Wisdom — GPT-5.6

Снимок на 29 июля 2026.

Здесь живут только правила, которые важны именно для `GPT-5.6`. Общие свойства
LLM держит `wisdom-llm.md`; платформенные правила Codex держит
`wisdom-codex.md`.

## Проверено

- Начинать с user-visible outcome, важных constraints, доступного evidence,
  success criteria и stop condition. Путь поиска, tools и reasoning не
  расписывать, если порядок сам не является требованием.
- Стартовать с минимального prompt и tool set, который проходит evals. Перед
  добавлением новой инструкции удалить obsolete scaffolding, повторы,
  неработающие examples, уже надёжно выполняемый process и нерелевантные tools.
- Добавлять правило, example или tool только под измеренный failure mode.
  Противоречащие правила опаснее недостающей второстепенной детали.
- `ALWAYS`, `NEVER`, `must`, `only` оставлять для настоящих инвариантов. Для
  поиска, уточнений, tool use и итераций задавать decision rules.
- Явные значения пользователя сохранять как заданные. Если правильный выбор
  неявен, давать критерии решения; не подменять domain judgment универсальными
  defaults, keyword maps или широкими semantic shortcuts.
- Personality и collaboration style разделять и держать короткими: первая
  управляет тоном, вторая — вопросами, допущениями, инициативой, tradeoffs,
  проверкой и неопределённостью.
- Не задавать generic brevity: GPT-5.6 уже склонна к компрессии и может потерять
  обязательный evidence или часть артефакта. Указывать, что сохранить, а резать
  сначала introductions, repetition, reassurance и optional background.
- Если API surface поддерживает `text.verbosity`, общей подробностью управлять
  этой ручкой, а prompt использовать для task-specific содержания, структуры и
  того, что нельзя потерять при сжатии.
- Permissions задавать один раз по типу запроса: answer/review/diagnose/plan —
  read-only inspection без внедрения; change/build/fix — in-scope local edits и
  non-destructive validation; external writes, destructive actions и material
  scope expansion — только после подтверждения.
- Для long-running work явно называть текущий слой: research, design,
  implementation, review или external coordination. Не разрешать молчаливый
  переход между слоями.
- Показывать только task-relevant tools. Tool description должна объяснять
  `what`, `when`, важные return fields и error behavior.
- `PTC` использовать для bounded deterministic reduction над уже полученными
  данными. Semantic judgment, citations, approval-sensitive и внешние действия
  оставлять прямым tool calls: сжатие orchestration не должно скрывать
  решение, источник или authority boundary.
- Для grounded ответа задавать evidence bar и retrieval budget. Повторный поиск
  нужен, когда отсутствует обязательный факт, owner, дата, ID, source или
  citation; отсутствие результата не превращать в уверенное «нет» без одного-
  двух осмысленных fallback.
- В tool-heavy работе давать короткий preamble перед первым вызовом и редкие
  outcome-based updates на смене фазы; routine tool calls не комментировать.
- Persisted reasoning использовать, пока стабильны objective, assumptions и
  priorities. Stale reasoning не сохранять как always-on optimization: оно
  якорит старый подход и раздувает tokens/latency.
- `reasoning.effort` — last-mile knob. Начинать с текущего режима, сравнивать его
  с уровнем ниже на representative evals; `medium` — balanced start, `high` /
  `xhigh` / `max` — только по измеренному выигрышу, не глобальный default.
- Bare alias `gpt-5.6` сейчас разрешается в `gpt-5.6-sol`. Для runtime evidence
  фиксировать resolved slug, а не считать requested alias доказательством.
- До повышения effort проверить success criteria, dependency rules, tool
  routing и validation loop.
- Внутри GPT-5.6 family `Sol` — capability-first кандидат для root/synthesis и
  сложной неоднозначной работы, `Terra` — price/performance кандидат для
  повседневных и supporting задач, `Luna` — volume/low-cost кандидат.
  Это не жёсткий mapping: variant/effort подтверждать representative evals, а
  доступный slug — в живом runtime конкретной платформы.
- В prompt явно назвать значимую проверку результата. Для кода — targeted
  tests/build/smoke по риску; для frontend и visual artifacts — render и
  визуальная инспекция перед финалом.

## Что Не Делать

- Не переносить старый prompt stack целиком из предыдущей модели.
- Не компенсировать слабый outcome повтором `be thorough`, `be concise`, `think
  step by step`, длинным self-check stack или лишними examples.
- Не повторять `ask first` по всему prompt: это провоцирует лишние permission
  checks для безопасных ожидаемых действий.
- Не оптимизировать tokens, latency или tool calls ценой неполного
  user-visible результата.
- Не переписывать working prompt и одновременно менять model, tools и effort:
  источник регрессии станет неразличим.

## Критерий Миграции

Миграция завершена, когда representative evals подтверждают нужный outcome на
GPT-5.6, а источник изменения различим. Сохраняй достаточно стабильными model,
prompt, tools и effort, чтобы сравнение что-то доказывало; сначала измеряй
baseline и pruning, затем возвращай только минимальную Delta под наблюдаемый
failure. Это evidence contract, а не обязательная стадийная процедура.

## Где Использовать

- `perfect-system-prompts.md` — при написании системных промптов.
- `perfect-context-engineering.md` — при сборке контекста.
- `practical-guides/how-to-write-skills/` — при authoring skills.
- `wisdom-codex.md` — когда GPT-5.6 работает внутри Codex-подобного coding agent.

## Опоры

- <https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6#prompting-best-practices>
  Официальная GPT-5.6 guidance: prompt pruning, outcome/stop, response length,
  permissions, tools, retrieval, state, effort и validation.

- <https://developers.openai.com/api/docs/guides/latest-model>
  Текущий model-family baseline и migration posture.

- <https://platform.openai.com/docs/api-reference/responses>
  Responses state, output items и reasoning settings.
