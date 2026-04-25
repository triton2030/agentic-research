---
name: before-write
description: >
  Use this skill whenever an imminent substantive Edit/Write/NotebookEdit is about to change user-facing or load-bearing content: "сейчас буду писать", "правлю файл", "вношу изменения", "перед записью", "перед edit", "записывай", "write it", "edit the file", "apply changes", "patch this", "update the file", "change content". Refresh the active task contract and write-scope before the tool call. Skip on user work-start talk (before-work), review/closeout, trivial typo edits, or read-only exploration.
---

# Before Write

Use this as the last lightweight check before a substantive file or artifact write.

## What It Does

1. Identify the intended write target and why it is being changed.
2. Re-open the nearest task contract if one exists; read Цель, current Подшаг, Must, Must-not, and Verification.
3. Confirm the write is within scope. If no contract exists for non-trivial work, route to `task-contract`. If the plan anchor is missing, route to `project-strategy`. If the write changes instruction/runtime shape and owner is unclear, route to `instruction-layer` or `repo-shape`.

## Receipt

```md
**Write target:** <path or artifact>
**Contract:** <task / stage / none>
**Must-not:** <top 1-2 constraints>
**Proceed:** yes | route to <owner-skill>
```

## Skip

Skip for pure reads, terminal checks, generated caches, one-character typo fixes, or when `before-work` already refreshed the same contract in this turn and no write-scope changed.

## Output Contract

Emit a compact receipt, then return control to the current task. Keep it to 3-5 lines unless blocking.

## Role Boundaries

- Do not become a strategy, architecture, or task-file owner.
- Do not broaden scope beyond this moment.
- Route to the owner-skill when durable state must change.

## Done When

The relevant rule is freshly in context, the next owner or action is clear, and no extra artifact was created by this skill.
