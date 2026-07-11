---
description: "Короткий Go/No-Go checklist перед созданием или правкой skill."
read-before-edit: []
edit-after-edit: []
---
# Checklist

Пройди сверху вниз. Если первые ответы слабые — скилл пока не писать. Сначала
выбери глубину проверки: минимальную (`minimum gate`) или строгую
(`strict gate`).

## Режим Проверки

**Минимальная проверка (`minimum gate`)** — маленький, локальный,
низкорисковый скилл или узкая правка существующего скила.

**Строгая проверка (`strict gate`)** — глобальный / часто вызываемый скилл,
широкий или спорный trigger, scripts/network/credentials, высокий blast radius,
безопасность, перенос между runtime или уже замеченные regressions.

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
- Первая фраза содержит главный use case и trigger words, а `120-200` символов
  opening используются только как локальная эвристика?
- Есть boundaries и skip-cases?
- Минимум: есть 2-3 concrete use cases и реальные trigger phrases?
- Строго: есть 8-10 `should-trigger` и 8-10 `should-not-trigger` prompts?
- Строго: negative prompts — near-misses, а не очевидно нерелевантные запросы?
- Строго: проверено, что соседние skills не делят тот же trigger surface?

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

- Минимум: прошла структурная проверка (`quick_validate.py` для Codex)?
- Минимум: есть одна наблюдаемая проверка результата: команда, dry-run, `wc -m`,
  grep, пример output или ручная сверка с коротким критерием?
- Строго: есть baseline — without skill или previous version?
- Строго: есть один реалистичный with-skill прогон?
- Строго: зафиксированы regressions, а не только improvements?
- Строго: assertions проверяют наблюдаемое, а human review оставлен для
  вкуса/качества?
- После прогона удалено всё, что не улучшает routing, качество, скорость или
  надёжность?
