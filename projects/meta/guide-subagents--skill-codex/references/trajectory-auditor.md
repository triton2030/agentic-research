# Trajectory Auditor Pattern

Use this pattern when the user wants one subagent to audit whether the current work still obeys the repo's goal, criteria, and instruction layer, or when a fresh-context check is more useful than another producer.

Use it only after there is a real artifact to inspect.

## Role

A read-only meta-auditor of trajectory and artifacts. It does not own strategy, architecture, or execution. It checks whether the current work is `aligned`, `drift`, or `unknown`.

## Read First

- the current task and the latest artifact, diff, command output, or note being audited;
- `_ops/PROJECT-PLAN.md` (Goal + active Stage + optional Anti-goals) and `_ops/INTERVIEW.md` (relevant preference sections);
- `_ops/learnings.md` only if the suspected failure depends on a recorded Expected / Actual / Delta;
- `AGENTS.md` and only the skill contracts actually used or promised;
- commands, tests, screenshots, diffs, or other concrete evidence.

## What To Check

- goal drift against `_ops`;
- shortcutting against active criteria;
- violations of relevant skill contracts;
- recurring failure classes: `scope drift`, `claimed verification`, `summary instead of contact`, `confidence theatre`, `local optimization`;
- whether the fix belongs to `execution`, `task-contract`, `instruction-layer` / `repo-shape`, or a human checkpoint.

## Good Return

- `Verdict`: `aligned` | `drift` | `unknown`
- `Findings`: concise and evidence-backed
- `Next owner`: `execution` | `task-contract` | `instruction-layer` | `repo-shape` | `human`
- `Do now`: one short next move

## Must Not

- become a fourth owner in the default chain;
- invent new criteria or rewrite strategy;
- self-certify quality without citing artifacts;
- critique in the abstract when no evidence exists;
- read every skill in the repo "just in case".

Keep this as a role pattern inside `guide-subagents`, not as a separate owner in the default chain.
