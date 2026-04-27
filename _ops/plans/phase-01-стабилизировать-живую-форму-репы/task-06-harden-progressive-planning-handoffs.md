# Harden progressive planning handoffs

## Цель

Существующие skills удерживают progressive task planning как исполнимую цепочку:
strategy задаёт Stage, `task-contract` выбирает минимальный next frontier,
moment-skills проверяют write/review моменты, а drift routes не смешиваются с
обычным обсуждением стратегии.

## Подшаги

- [x] Усилить `project-roadmap`: bootstrap на fresh-репе и drift sweep.
- [x] Усилить `task-contract` и lifecycle gates: minimal frontier,
  no speculative criteria, anchor existence, closeout classification.
- [x] Усилить moment-skills: portable ordering, routine substantive checks,
  write-back при новом подшаге.
- [x] Усилить `work-review`: sizing feedback и orphan open substeps.
- [x] Синхронизировать installed Codex/Claude copies и проверить skill validity.

## Критерии приёмки

### Must

- [x] `project-roadmap` явно обрабатывает fresh-repo bootstrap и periodic
  drift sweep. — **Evidence**: Claude/Codex source + installed copies содержат
  `First-Time Setup` и `Drift sweep`.
  **Anchored in**: `_ops/INTERVIEW.md#Минимальный-След`
- [x] `task-contract` явно владеет next-task selection внутри Stage и запрещает
  раскрывать task/subtask/criteria глубже необходимого. — **Evidence**:
  Claude/Codex source + installed copies содержат minimal next frontier /
  speculative criteria guards.
  **Anchored in**: `_ops/INTERVIEW.md#Минимальный-След`
- [x] Anchor existence проверяется как gate: `Anchored in:` должен указывать на
  существующий section target. — **Evidence**: lifecycle gate добавлен в
  Claude/Codex source + installed copies.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [x] Moment-skills фиксируют portable preference ordering и не пропускают
  routine substantive writes/reviews. — **Evidence**: `before-work`,
  `before-write`, `work-review` Claude/Codex source + installed copies
  обновлены.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `before-write` останавливает действие, если оно лежит вне текущих
  Подшагов task-файла, и роутит к `task-contract` для write-back. —
  **Evidence**: Claude/Codex source + installed `before-write` содержат
  scope/write-back rule.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `work-review` проверяет wrong-sized task и orphan open substeps перед
  claim завершения. — **Evidence**: Claude/Codex source + installed
  `work-review` содержит feedback/orphan routing.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`

### Must not

- [x] Не создавать новый planning skill или новый root surface.
- [x] Не превращать moment-skills в owner-skills.
- [x] Не добавлять runtime hook без отдельного `repo-shape` решения.

### Verification protocol

1. `quick_validate.py <changed-skill-dir>`
   Expected: `Skill is valid!` for each changed source and installed copy.
   Actual: passed for 20 source/installed skill dirs; task-contract rerun passed
   after reference formatting.
2. `diff -ru --exclude README.md projects/meta/<skill>--skill-codex /Users/triton/.codex/skills/<skill>`
   Expected: no diff for changed installed Codex skills after sync.
   Actual: no diff for changed Codex installed skills.
3. `diff -ru --exclude README.md projects/meta/<skill>--skill-claude-code /Users/triton/.claude/marketplaces/my-skills/skills/<skill>`
   Expected: no diff for changed installed Claude skills after sync.
   Actual: no diff for changed Claude installed skills.
4. `npx markdownlint-cli2 <changed markdown refs and playbook>`
   Expected: 0 errors.
   Actual: 0 errors.
