# Refactor map — 1planning — 2026-08-29

Approved family boundary: `_ops/chat-recall/2026-08-29-152644-codex-01a04d0d.md:18-19`.
Earlier function: `_ops/chat-recall/2026-08-26-220614-claude-4ee6bbef.md:20-23`.

## Function

Decision owner for task admission and material task-level decomposition in
chat. It owns no durable planning file; accepted decisions land in fields owned
by `1plan-map` or `1plan-task`.

## Old instruction groups

| Group | Disposition | Target owner |
| --- | --- | --- |
| Aggressive trigger, native Plan Mode exclusion | keep | description + boundary |
| Read GOAL, map, tasks, root and domain rules | keep, compress | protocol 1 |
| Challenge order, blockers, displacement and epic membership | keep | protocol 2 |
| Visible steps, book-method trace, axis, nearest frontier | keep | protocol 3 |
| Wayfinding/Execution probe and material premises | keep, compress | protocol 3 |
| `1use-principles`, owner questions, exact approval | keep | protocol 4-5 |
| Map/task routing | keep as authority handoff | protocol 6 |
| Reread epic before every material execution step | move | `1plan-task` reconciliation |
| Keep epics/tasks fresh as execution proceeds | absorb | map/task lifecycle owners |
| Goal/product/finding routing menu | cut | generic discovery; not family function |

## New constraints

- Every accepted planning decision names its durable landing value. This closes
  the observed loss of the decomposition axis across clean windows; it removes
  freedom to leave planning truth only in chat.
- The five-invariant replan seam closes ambiguous ownership after new evidence;
  it removes `1plan-task`'s freedom to rebuild across a changed task decision.
- One approval message may cover two explicitly named results. This preserves
  exact approval while removing a two-message ritual that adds no authority.

## Predicted misreadings closed

- “Planning writes the plan file” → protocol 4 forbids the write and emits
  landing values.
- “A map frontier authorizes the next task” → protocol 2 requires admission.
- “Any new evidence means full re-planning” → protocol 6 names five material
  changes; routine execution remains with the task owner.

## Routing cases

- use: `What should we do next?`
- use: `This evidence changed the accepted task boundary.`
- use: `A major error may invalidate our current plan.`
- skip: `Continue the next approved subtask.` → `1plan-task`
- near miss: `Reorder the project epics after launch.` → `1plan-map`

## Current draft count

`draft-2026-08-29/SKILL.md`: 16 top-level instruction units by the current
author count; independent-predicate recount belongs to `check-approve`.
