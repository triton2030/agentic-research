# Tighten task-contract discovery and Smit review

## Цель
`task-contract` шире читает task-relevant evidence, но не усложняет output, и вызывает `смит` только когда task-layer стал messy.

## Подшаги
- [x] Добавить в Codex `task-contract` правило active discovery без чтения "на всякий случай".
- [x] Добавить условный handoff к `смит` для messy task планов / task-файлов.
- [x] Синхронизировать installed Codex copy и проверить skill validity.

## Критерии приёмки

### Must
- [x] Discovery rule усиливает чтение task-relevant sources, но сохраняет `Reason wide, emit narrow`. — **Evidence**: правка `projects/meta/task-contract--skill-codex/SKILL.md` и `references/task-file-lifecycle.md`: читать sources, если они меняют scope, Must, Must-not, evidence, verification или blocker.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `смит` указан как условный plan-critique subagent только для messy task-layer, а не как обязательный шаг каждого task-файла. — **Evidence**: правка Codex `task-contract` contract; `смит` ограничен messy / contradictory task-layer и помечен `when available`, без fake review при недоступности.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [x] Repo Codex source и installed Codex copy синхронизированы после правки. — **Evidence**: `rsync -a --delete --exclude README.md projects/meta/task-contract--skill-codex/ /Users/triton/.codex/skills/task-contract/`; `diff -ru --exclude README.md projects/meta/task-contract--skill-codex /Users/triton/.codex/skills/task-contract` clean.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`

### Must not
- [x] Не добавлять новый режим, новый файл-объяснялку или отдельный workflow. — **Why this would be bypassed**: проще расширить skill prose, чем заменить weak defaults точными triggers.

### Verification protocol
1. `python3 /Users/triton/.codex/skills/.system/skill-creator/scripts/quick_validate.py projects/meta/task-contract--skill-codex`
   Expected: `Skill is valid!`
   Actual: `Skill is valid!`
2. `diff -ru --exclude README.md projects/meta/task-contract--skill-codex /Users/triton/.codex/skills/task-contract`
   Expected: no diff.
   Actual: no diff after installed-copy sync.
