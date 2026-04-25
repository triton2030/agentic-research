# Instruction-layer Brooks handoff

## Цель
`instruction-layer` условно вызывает `brooks` для целостной структурной критики системы, когда архитектурный вывод зависит от связности нескольких поверхностей.

## Подшаги
- [x] Добавить в Codex `instruction-layer` узкое правило Brooks handoff.
- [x] Обновить workflow / output shape так, чтобы проверка была видима fresh-session агенту.
- [x] Синхронизировать installed Codex copy и проверить skill validity.

## Критерии приёмки

### Must
- [x] `brooks` указан как условный whole-system structural-critique subagent для систем из документов, картинок, бизнес-планов, instruction surfaces, repo-shape, guardrails или их связок. — **Evidence**: `projects/meta/instruction-layer--skill-codex/SKILL.md`, `references/workflow.md`, `references/output-shape.md`, `agents/openai.yaml`; installed copy синхронизирована.
  **Anchored in**: `_ops/PROJECT-PLAN.md#Stages`
- [x] Правило явно требует не симулировать review, если `brooks` недоступен, и не редактировать его роль через `instruction-layer`. — **Evidence**: `SKILL.md` содержит boundary "не редактируй роль Brooks"; `workflow.md` требует `needed but unavailable`, если `brooks` недоступен.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] Repo Codex source и installed Codex copy синхронизированы после правки. — **Evidence**: `rsync -a --delete --exclude README.md ...`; `diff -ru --exclude README.md projects/meta/instruction-layer--skill-codex /Users/triton/.codex/skills/instruction-layer` clean.
  **Anchored in**: `_ops/PROJECT-PLAN.md#Stages`

### Must not
- [x] Не добавлять новый skill, новый режим или обязательный Brooks-gate для каждого вызова `instruction-layer`. — **Why this would be bypassed**: легко превратить точечную критику в ceremony-spam и замедлить чистые instruction edits.

### Verification protocol
1. `python3 /Users/triton/.codex/skills/.system/skill-creator/scripts/quick_validate.py projects/meta/instruction-layer--skill-codex`
   Expected: `Skill is valid!`
   Actual: `Skill is valid!`
2. `python3 /Users/triton/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/triton/.codex/skills/instruction-layer`
   Expected: `Skill is valid!`
   Actual: `Skill is valid!`
3. `diff -ru --exclude README.md projects/meta/instruction-layer--skill-codex /Users/triton/.codex/skills/instruction-layer`
   Expected: no diff.
   Actual: no diff.
