# Simplify skill chain with domain grounding

## Цель

Живые Codex/Claude skills и installed copies используют новый основной контур:
`project-roadmap`, `domain-clarifier`, `user-interview`, `ops-sync`,
`task-contract`, `before-work`, `before-write`, `work-review`.
Удалённые диагностические skills больше не участвуют в routing, а domain
understanding становится обязательным основанием стратегии и задач.

## Подшаги

- [x] Создать `domain-clarifier` source + installed для Codex и Claude.
- [x] Заменить старый preference skill на `user-interview` source + installed.
- [x] Удалить retired skills из source + installed copies.
- [x] Обновить core skill contracts и routing docs.
- [x] Проверить validation, stale refs, sync diffs и markdown.

## Критерии приёмки

### Must

- [x] `project-roadmap` требует domain grounding перед Stage-chain и routes
  unclear domain knowledge к `domain-clarifier`. — **Evidence**: source +
  installed Codex/Claude copies содержат domain grounding workflow.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [x] `domain-clarifier` существует в source + installed Codex/Claude и задаёт
  только consequential questions. — **Evidence**: skill validation passes and
  source-to-installed diffs are clean.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `user-interview` replaces the old preference skill, owns `_ops/INTERVIEW.md`,
  and handles preference/vision conflicts itself. — **Evidence**: active refs
  use `user-interview`; no active refs to the old skill.
  **Anchored in**: `_ops/INTERVIEW.md#Рабочий-Режим`
- [x] `task-contract` creates empty phase task skeletons and delays substeps,
  criteria, evidence, and verification until a task becomes current. —
  **Evidence**: lifecycle and SKILL.md specify skeleton mode.
  **Anchored in**: `_ops/INTERVIEW.md#Минимальный-След`
- [x] `before-work` and `before-write` extract an execution lesson from
  strategy/task/user-interview before continuing. — **Evidence**: both
  SKILL.md files require execution lesson and route missing prerequisites.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [x] `work-review` loops repair until task criteria/evidence are satisfied
  and owns status reconciliation with `project-roadmap`. — **Evidence**:
  SKILL.md no longer routes to the retired drift router.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`
- [x] Retired skills are hard-deleted from source and installed copies. —
  **Evidence**: filesystem and `rg` checks show no active routing references.
  **Anchored in**: `_ops/PROJECT-ROADMAP.md#Stage 1`

### Must not

- [x] Не добавлять runtime hook.
- [x] Не архивировать retired skills вместо удаления.
- [x] Не раскрывать criteria/substeps для всей фазы заранее.

### Verification protocol

1. `quick_validate.py <kept/new skill dirs>`
   Expected: `Skill is valid!`.
   Actual: passed for source and installed Codex/Claude core skills,
   `domain-clarifier`, `user-interview`, and updated Codex `step-back`.
2. `rg <retired skill names> <active surfaces>`
   Expected: no active stale routing refs.
   Actual: no matches in active docs/skills; installed copies also clean.
3. `diff -ru --exclude README.md <source> <installed>`
   Expected: no diff for changed installed Codex/Claude skills.
   Actual: no diff for changed source-to-installed skills.
4. `markdownlint-cli2 <new and contract markdown files>`
   Expected: 0 errors.
   Actual: 0 errors. Broad legacy-root markdownlint was not used for closeout
   because existing root docs contain pre-existing line-length noise.
5. Manual dry-read scenario.
   Expected: strategy emits domain grounding, domain uncertainty routes to
   `domain-clarifier`, task-contract creates empty skeletons, before-work
   extracts execution lesson, and work-review loops failed criteria.
   Actual: dry-read grep confirmed those clauses in source and installed
   skill bodies.
