---
description: "Acceptance checklist для candidate skill design, draft или review."
read-before-edit: []
edit-after-edit: []
---

# Checklist

Применяй к уже выбранному candidate design, draft или review. Это не порядок
authoring: любой материально слабый ответ меняет решение или блокирует done.

## Evidence Pressure

Evidence соответствует заявленному claim и цене ошибки. Малой локальной правке
может хватить structural check и одного различающего output probe. Глобальный,
частый, collision-prone, risky или already-regressed surface требует более
сильного evidence именно по поднятому риску, но не фиксированного test package.

## Go / No-Go

- Это повторяемый момент профессионального решения или действия, а не тема,
  идея или разовая задача?
- У момента есть отдельный trigger и полезная Delta, которую модель без skill
  выполняет ненадёжно?
- Это точно не `AGENTS.md`, system prompt, plain script или reference?
- Без скилла агент реально ошибается, тратит лишние ходы или забывает
  локальную экспертизу?
- Есть реальные примеры: успешный run, corrections, issue/review comments,
  failure cases или user-provided contract?

## Routing

- `description` говорит, когда использовать skill?
- Opening самостоятельно несёт главный use case и trigger words?
- Есть boundaries и skip-cases?
- Representative use и skip cases покрывают заявленный trigger?
- Negative prompts — реальные near-misses, а не очевидно нерелевантные задачи?
- Collision-prone trigger проверен против живых соседних descriptions?

## Shape

- Один coherent unit of work?
- Выбрана правильная форма: outcome/decision contract по умолчанию или
  workflow только когда порядок является частью корректности?
- Outcome, decision criteria, constraints, evidence и stop достаточны без
  пошагового процесса?
- Если workflow остался, каждый обязательный шаг закрывает конкретный
  order-sensitive failure mode?
- В `SKILL.md` осталось только ядро?
- Длинные детали вынесены в `references/`?
- Хрупкая повторяемая логика вынесена в `scripts/`?
- Выходные шаблоны и ресурсы вынесены в `assets/`?
- Нет `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md` внутри installed skill?

## Platform

- Codex: проверен `~/.codex/skills/<name>` и, если нужна переносимость,
  `$HOME/.agents/skills/<name>`?
- Codex: `agents/openai.yaml` нужен по функции, сгенерирован и синхронизирован?
- Claude: `description` прошло trigger и near-miss probe на фактически resolved
  target model без предположения, что undertrigger/overtrigger одинаковы?
- Claude: нет Codex-only metadata вроде `agents/openai.yaml`?
- Mixed-runtime: body держит нижний общий bound, а platform deltas не смешаны.

## Proof

- Структурная проверка платформы прошла?
- Есть наблюдаемая проверка каждого материального behavior/routing claim?
- Baseline или previous version есть, если заявлено улучшение относительно них?
- Metadata/projections синхронизированы, если изменение их затрагивает?
- Assertions проверяют наблюдаемое, а human review оставлен для вкуса/качества?
- После прогона удалено всё, что не улучшает routing, качество, скорость или
  надёжность?
