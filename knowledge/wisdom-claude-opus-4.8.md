---
description: "Claude Opus 4.8-specific prompting, effort, tool, subagent and migration baseline."
---

# Wisdom — Claude Opus 4.8

Снимок на 22 июля 2026.

Здесь живут только правила, которые важны именно для `Claude Opus 4.8`.
Общие свойства LLM держит `wisdom-llm.md`; платформенные правила Claude Code
держит `wisdom-claude-code.md`; отличный от Opus маршрут сложнейших задач —
`wisdom-claude-fable-5.md`.

## Проверено

- Явно задавать task, intent, значимые constraints, scope распространения,
  success criteria и stop. Opus 4.8 особенно буквально следует инструкциям на
  низком effort и не обязан сам распространять локальное правило на весь набор.
- `effort` — первый рычаг качества и стоимости. Для coding/agentic work начинать
  с `xhigh`, для intelligence-sensitive задач — не ниже `high`; `max` проверять
  только на самых трудных evals из-за diminishing returns и overthinking.
- Не лечить under-thinking длинным prompt: сначала поднять effort. При `xhigh` и
  `max` оставлять достаточный output-token headroom для tool/subagent loop.
- Tool policy задавать явно там, где tools обязательны. Opus 4.8 склонен сначала
  рассуждать; `high`/`xhigh` и точная инструкция «когда и зачем вызвать tool»
  увеличивают фактический tool use.
- Subagent policy должна быть decision rule. Opus 4.8 запускает их реже по
  умолчанию: direct work оставлять root, независимые files/evidence streams
  разрешать fan-out явно.
- Не тащить ритуал progress updates из старого harness. Модель уже даёт
  регулярные обновления; добавлять формат только под наблюдаемый провал.
- Длину и стиль ответа задавать, если продукт зависит от них. Положительный
  пример желаемой плотности надёжнее списка запретов на verbosity.
- Для interactive long-horizon задач передавать полный task-spec в первом ходе:
  постепенное доуточнение повышает token cost и может ухудшить performance.
- В code-review сначала разделять recall и filtering. Если нужен полный поиск,
  просить сообщать все candidates с confidence/severity, а ranking выполнять
  отдельным шагом; расплывчатое «только важное» модель соблюдает буквально.
- Для frontend не полагаться на default taste: Opus 4.8 устойчиво тянется к
  cream/serif/terracotta. Давать конкретное visual direction или сначала просить
  materially distinct варианты, если направление ещё не выбрано.

## Что Не Делать

- Не переносить старый Opus 4.7 prompt stack без baseline на 4.8.
- Не компенсировать неверный effort process scaffolding, self-check stack или
  повтором общих пожеланий.
- Не требовать automatic fan-out для работы, которую root видит целиком.
- Не смешивать Claude Code metadata/runtime с model-level prompting.
- Не объявлять отсутствие finding доказательством отсутствия проблемы, если
  review prompt одновременно поднял reporting threshold.

## Миграция С Opus 4.7

1. Переключить модель без переписывания working prompt: 4.8 обычно хорошо
   работает с существующими 4.7 prompts.
2. Снять baseline на representative evals.
3. Сначала откалибровать effort, token headroom и обязательный tool policy.
4. Удалить forced progress и старый process scaffolding, который baseline уже
   выполняет сам.
5. Добавлять только точечную правку под наблюдаемый trace failure.

## Где Использовать

- `perfect-system-prompts.md` — при написании системных промптов.
- `perfect-context-engineering.md` — при сборке длинного контекста.
- `practical-guides/how-to-write-skills/` — при authoring Claude skills.
- `wisdom-claude-code.md` — когда Opus 4.8 работает внутри Claude Code.

## Опоры

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
  Официальный model-specific guide: effort, literal scope, tool/subagent use,
  progress, frontend defaults и review harness.
- https://platform.claude.com/docs/en/about-claude/models/migration-guide
  API-level migration с Opus 4.7; перед переносом production harness сверять
  live параметры здесь.
