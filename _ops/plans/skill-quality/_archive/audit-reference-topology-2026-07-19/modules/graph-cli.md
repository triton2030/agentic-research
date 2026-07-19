---
description: "Аудит и правка reference topology 1md-graph и 1cli-tools."
kind: module
---

# Markdown graph и CLI evidence

Parent Task: `_ops/plans/skill-quality/audit-reference-topology-2026-07-19/task.md`.

## Вклад

Прочитать и исправить только `1md-graph` и `1cli-tools`: убрать reference/body
дубли и catalog-like сведения вне hot path, проверить, что runtime/schema
детали живут в правильном owner-е, а каждый reference route загружает только
нужный слой доказательств.

## Owner Anchors

- `/Users/triton/.codex/skills/1md-graph/SKILL.md`
- `/Users/triton/.codex/skills/1md-graph/references/**`
- `/Users/triton/.codex/skills/1cli-tools/SKILL.md`
- `/Users/triton/.codex/skills/1cli-tools/references/**`
- `/Users/triton/.codex/skills/1cli-tools/scripts/**`
- `/Users/triton/Documents/GitHub/agentic-research/knowledge/practical-guides/how-to-write-skills/authoring-canon.md`

## Boundaries

- Read: applicable project instructions, this Module, all files in the two
  packages, and live `md`/tool help only where a retained fact depends on it.
- Write: only the two package directories above. Do not edit this Module,
  parent Task, other skills, repo knowledge or unrelated user changes.
- You are not alone in the workspace: do not revert others; accommodate any
  concurrent edits outside your boundary.

## Return

`status: success | blocked | split-proposal`; `changes`: files and routing
decision; `evidence`: before/after lines, exact CLI/runtime checks and package
validation; `gaps`: stale or unverified live fact. Escalate cross-package owner
conflicts instead of editing outside the boundary.

Root will verify diffs, local links, live command claims and changed scripts.
