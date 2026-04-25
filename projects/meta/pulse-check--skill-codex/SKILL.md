---
name: pulse-check
description: >
  Use for explicit memory/context probe: pulse-check, пульс, помнишь, context check, recall goal. First recall from dialogue, then compare to `_ops`. Read-only; verdict remembered/drift/forgotten. Skip artifact alignment, task criteria, execution, and status reports.
---

# Pulse Check

Read-only probe of whether the current dialogue still holds the project goal and active line.

## First Read

Do not read `_ops` before the cold recall. Then read:

- `references/pulse-check-mode.md`
- `_ops/PROJECT-PLAN.md`
- `_ops/INTERVIEW.md` if relevant
- `references/failure-modes.md` for pulse-check failure modes

## Workflow

1. Emit cold `Recalled` from current session memory.
2. Read actual plan truth.
3. Emit `Actual`, 3-step `Trace`, verdict, and `Delta` only when not remembered.

## Output Contract

Verdict is exactly one of `remembered`, `drift`, `forgotten`.

## Role Boundaries

- Read-only; writes no files.
- Does not inspect artifact quality; route that to `strategy-trace`.
- Does not create task criteria or update plans.

## References

- [references/pulse-check-mode.md](references/pulse-check-mode.md)
- [references/failure-modes.md](references/failure-modes.md)
- [references/format-examples.md](references/format-examples.md)
