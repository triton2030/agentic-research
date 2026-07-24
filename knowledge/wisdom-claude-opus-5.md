---
description: "Claude Opus 5-specific prompting, effort, scope, tool and delegation baseline."
---

# Wisdom — Claude Opus 5

Снимок на 25 июля 2026.

Здесь живут только правила, которые меняют работу именно с `Claude Opus 5`.
Общие свойства LLM держит `wisdom-llm.md`; платформенные правила Claude Code
держит `wisdom-claude-code.md`; отличный от Opus маршрут сложнейших задач —
`wisdom-claude-fable-5.md`.

## Проверено

- Передавать полный task-spec в первом ходе: outcome, intent, live sources,
  constraints, scope, success criteria и stop. Opus 5 особенно силён в
  long-horizon agentic work, когда видит задачу целиком.
- `effort` — первый рычаг качества и стоимости. Для coding/agentic work
  `xhigh` остаётся рекомендуемым стартом, но `low` и `medium` уже дают сильный
  результат; перенос старого default требует effort sweep на своих evals.
- Явно калибровать длину ответа, progress cadence и размер письменных
  deliverables. Opus 5 подробнее прежних Opus и охотно narrates agentic work;
  короткий положительный пример формата надёжнее списка запретов.
- Не добавлять generic «double-check», отдельный verification pass или
  subagent-verifier. Opus 5 сам исправляет и проверяет работу; старое
  scaffolding вызывает over-verification, лишние latency и token cost.
- Для узкой задачи явно удерживать requested scope и stop. Модель может сама
  расширить работу полезными, но не запрошенными шагами.
- Делегировать только genuinely independent sizeable tracks. Opus 5 охотнее
  запускает subagents: если достаточно одного, использовать одного; мелкую
  работу в несколько tool calls оставлять root и держать spawn count низким.
- Не прописывать полный tool choreography. Claude Code сам выбирает доступные
  native tools и через `ToolSearch` открывает deferred tools; точное имя
  указывать, когда конкретный `Skill`, permission rule или capability является
  частью acceptance.
- Tool use часто сильнее дополнительного thinking, особенно для vision и
  iterative verification. Обязательный внешний evidence/tool называть явно,
  но не заменять им outcome.
- В code review разделять recall и filtering. Если нужен полный поиск, просить
  сообщить все candidates, затем фильтровать по severity отдельным проходом.

## Что Не Делать

- Не переносить Opus 4.x prompt stack как действующий baseline без новой
  проверки; старые prompts — только старт миграции.
- Не компенсировать неверный effort длинным process scaffolding.
- Не требовать automatic fan-out, self-review или повторную проверку по
  умолчанию.
- Не смешивать Claude Code tool/runtime metadata с model-level prompting.
- Не объявлять отсутствие finding доказательством отсутствия проблемы, если
  review prompt одновременно поднял reporting threshold.

## Миграция С Opus 4.8

1. Переключить exact model id на `claude-opus-5`, сохранив working prompt.
2. Снять baseline и effort sweep на representative evals.
3. Удалить generic verification и automatic subagent scaffolding.
4. Откалибровать scope, visible response length и progress cadence.
5. Возвращать только точечные правила под наблюдаемый failure.

## Где Использовать

- `perfect-system-prompts.md` — при написании системных промптов.
- `perfect-context-engineering.md` — при сборке длинного контекста.
- `practical-guides/how-to-write-skills/` — при authoring Claude skills.
- `wisdom-claude-code.md` — когда Opus 5 работает внутри Claude Code.

## Опоры

- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
  Официальный model-specific guide: effort, scope, verbosity,
  over-verification, tool use и subagent delegation.
- <https://code.claude.com/docs/en/tools-reference>
  Живой owner точных native tool names и runtime semantics.
- <https://platform.claude.com/docs/en/about-claude/models/migration-guide>
  API-level migration; перед переносом production harness сверять live
  параметры здесь.
