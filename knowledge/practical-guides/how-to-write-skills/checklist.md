---
description: "Короткий Go/No-Go checklist перед созданием или правкой skill."
read-before-edit: []
edit-after-edit: []
---
# Checklist

Пройди сверху вниз. Если первые ответы слабые — скилл пока не писать.

## Go / No-Go

- Это повторяемый workflow, а не тема, идея или разовая задача?
- У workflow есть отдельный trigger и свой порядок работы?
- Это точно не `AGENTS.md`, system prompt, plain script или reference?
- Без скилла агент реально ошибается, тратит лишние ходы или забывает
  локальную экспертизу?
- Есть реальные примеры: успешный run, corrections, issue/review comments,
  failure cases или user-provided workflow?

## Routing

- `description` говорит, когда использовать skill?
- Первый sentence содержит главный use case и trigger words?
- Есть boundaries и skip-cases?
- Есть 8-10 `should-trigger` и 8-10 `should-not-trigger` prompts?
- Negative prompts — near-misses, а не очевидно нерелевантные запросы?
- Проверено, что соседние skills не делят тот же trigger surface?

## Shape

- Один coherent unit of work?
- Один default path?
- Outcome, constraints, evidence и stop condition идут раньше процесса?
- В `SKILL.md` осталось только ядро?
- Длинные детали вынесены в `references/`?
- Хрупкая повторяемая логика вынесена в `scripts/`?
- Выходные шаблоны и ресурсы вынесены в `assets/`?
- Нет `README.md`, `CHANGELOG.md`, `QUICK_REFERENCE.md` внутри installed skill?

## Platform

- Codex: проверен `~/.codex/skills/<name>` и, если нужна переносимость,
  `$HOME/.agents/skills/<name>`?
- Codex: `agents/openai.yaml` нужен по функции, сгенерирован и синхронизирован?
- Claude: `description` достаточно явный для undertrigger risk?
- Claude: нет Codex-only metadata вроде `agents/openai.yaml`?
- Mixed-runtime: body держит нижний общий bound, а platform deltas не смешаны.

## Proof

- Есть baseline: without skill или previous version?
- Есть один реалистичный with-skill прогон?
- Зафиксированы regressions, а не только improvements?
- Assertions проверяют наблюдаемое, а human review оставлен для вкуса/качества?
- После прогона удалено всё, что не улучшает routing, качество, скорость или
  надёжность?
