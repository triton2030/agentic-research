---
name: strategy-trace
description: >
  Use for explicit alignment trace: strategy-trace, alignment, drift-check, follows plan, against goal. Read-only audit of artifact/request against Goal, Stage, and intent. Route drift to `plan-drift-watch`. Skip task-file creation, quality review, and execution.
---

# Strategy Trace

Read-only alignment audit of a concrete artifact, proposal, or request.

## First Read

- `references/strategy-trace-mode.md`
- `_ops/PROJECT-PLAN.md`
- `_ops/INTERVIEW.md` only if preferences affect the trace
- The artifact or request being traced

## Workflow

1. Identify the trace target.
2. Build a 3-4 step chain from Goal / active Stage / Anti-goal / preference to the target.
3. Return one verdict: `aligned`, `drift`, or `unclear`.
4. Name one next move.

## Output Contract

Use the shape from `references/format-examples.md`: Trace target, Strategic chain, Verdict, Why, Do now.

## Role Boundaries

- Read-only; writes no files.
- Does not produce task criteria or project strategy.
- If the trace reveals plan drift, route to `plan-drift-watch` / `project-strategy`.

## References

- [references/strategy-trace-mode.md](references/strategy-trace-mode.md)
- [references/format-examples.md](references/format-examples.md)
