---
description: "Аудит и правка reference topology 1ia-audit и 1instruction-layer."
kind: module
---

# IA и instruction layer

Parent Task: `_ops/plans/skill-quality/audit-reference-topology-2026-07-19/task.md`.

## Вклад

Прочитать и исправить только два skill-пакета так, чтобы их `SKILL.md` были
micro-router-ами, references имели одну функцию и условный маршрут чтения, а
IA/reference material не дублировался внутри пакета или между этими двумя
пакетами.

## Owner Anchors

- `/Users/triton/.codex/skills/1ia-audit/SKILL.md`
- `/Users/triton/.codex/skills/1ia-audit/references/**`
- `/Users/triton/.codex/skills/1instruction-layer/SKILL.md`
- `/Users/triton/.codex/skills/1instruction-layer/references/**`
- `/Users/triton/Documents/GitHub/agentic-research/knowledge/practical-guides/how-to-write-skills/authoring-canon.md`

## Boundaries

- Read: applicable project instructions, this Module, all files in the two
  packages, and exact linked owner facts needed to verify a claim.
- Write: only the two package directories above. Do not edit this Module,
  parent Task, other skills, repo knowledge or unrelated user changes.
- You are not alone in the workspace: do not revert others; accommodate any
  concurrent edits outside your boundary.

## Return

`status: success | blocked | split-proposal`; `changes`: files and IA decision;
`evidence`: before/after lines plus validations; `gaps`: unresolved owner or
runtime fact. Escalate when a proposed deletion needs cross-package ownership
outside this boundary.

Root will verify every diff, local links, reference routing and package
validation.
