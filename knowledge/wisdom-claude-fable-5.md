---
description: "Claude Fable 5-specific routing, brief, autonomy, evidence and delegation baseline."
---

# Wisdom — Claude Fable 5

Снимок на 22 июля 2026.

Здесь живут только правила, которые меняют работу именно с `Claude Fable 5`.
Fable — target для самых сложных long-horizon, ambiguous и high-stakes задач,
не универсальная замена `Claude Opus 4.8`. Общие свойства LLM держит
`wisdom-llm.md`, платформу — `wisdom-claude-code.md`.

## Когда Выбирать Fable

- Работа требует долгой автономии, связывает несколько систем или workstreams,
  либо раньше разваливалась на итерациях и handoff.
- Цена первого неверного решения высока: architecture, hard debugging,
  сложный review, dense visual evidence, enterprise artifacts.
- Неопределённость — часть задачи, и модель должна определить следующий ход, а
  не только выполнить заранее известный рецепт.
- Для routine или хорошо ограниченной работы начинать с Opus; Fable оправдан,
  когда его capability меняет outcome, а не ради «лучшей модели вообще».

## Brief Contract

- Дать реальный outcome и зачем он нужен, а не только локальную команду.
- Назвать live owner files, уже проверенное evidence и первый спорный
  claim/decision, который нужно подтвердить или атаковать.
- Явно задать authority: read-only или write scope, допустимые tools, границы
  subagent delegation и действия, требующие пользователя.
- Зафиксировать success criteria, output shape, неопределённость и stop.
- Не просить private reasoning. Просить findings, evidence, alternatives,
  confidence и неразрешённые gaps.

## Поведение И Поправки

- `high` — рабочий default; `xhigh` — для capability-sensitive задач. На routine
  work сначала снижать effort, а не обрастать prompt-ограничениями.
- На high effort отдельно запрещать unrequested features, surrounding refactor,
  speculative abstractions и future-proofing. Достаточен простейший ход,
  закрывающий observable outcome.
- Когда информации достаточно, действовать: не переоткрывать уже принятое
  решение, не перечислять варианты, которые не будут выбраны, и не превращать
  ambiguity в бесконечное планирование.
- Ground progress claims в tool results текущего run. Непроверенное называть
  непроверенным; failed test не пересказывать как почти-success.
- Граница request type обязательна: assessment/review/diagnosis заканчивается
  отчётом; fix/build разрешает scoped edits. Не расширять одно в другое.
- Fable охотнее делегирует и устойчивее ведёт parallel subagents. Давать только
  независимые потоки с write ownership и return contract; root продолжает свою
  работу, синтезирует evidence и останавливает ушедший в сторону fan-out.
- Для долгой работы memory полезна, но одна мысль имеет одного owner-а. Не
  сохранять то, что уже держит repo/chat; исправлять или удалять неверную запись
  вместо нового компенсирующего файла.
- Короткая сильная инструкция обычно лучше перечисления микроповедений. Сжимать
  выбором материала, не фрагментами, jargon и arrow-chain shorthand.
- Финал после длинного run писать как re-grounding для читателя: outcome,
  materially important evidence, gaps и требуемый следующий выбор.

## Что Не Делать

- Не переносить старые skills/prompts целиком: Fable может деградировать от
  лишней предписанности. Сначала baseline, затем удаление obsolete scaffolding.
- Не использовать Fable как дорогой serial worker для множества одинаковых
  механических задач.
- Не принимать self-critique за независимую проверку; для material work лучше
  fresh-context verifier с отдельным evidence contract.
- Не добавлять memory, guardrail, fallback или validation без конкретного
  failure mode либо реальной system boundary.

## Где Использовать

- `perfect-system-prompts.md` — устойчивый system layer.
- `perfect-context-engineering.md` — owner/evidence ordering и long-run context.
- `practical-guides/how-to-write-skills/` — concise dual-model Claude skill core.
- `wisdom-claude-code.md` — platform packaging и runtime semantics.

## Опоры

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
  Официальный model-specific guide: long runs, effort, scope, progress,
  subagents, memory, brevity и migration of existing skills.
- `experiments/claude-bridge/codex-skill/1claude-mcp/references/fable-agent-prompting.md`
  Локальный bounded brief для вызова Fable через bridge; profile/session details
  остаются bridge-specific и не входят в этот owner.
