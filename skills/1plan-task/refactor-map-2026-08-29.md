# Refactor map — 1plan-task — 2026-08-29

Approved family boundary: `_ops/chat-recall/2026-08-29-152644-codex-01a04d0d.md:18-19`.
Earlier function: `_ops/chat-recall/2026-08-26-220614-claude-4ee6bbef.md:25-26`.

## Function

Durable owner for one approved task and its routine execution lifecycle. It
serializes admission decisions but does not make them, and it requests rather
than owns epic state writes.

## Old instruction groups

| Group | Disposition | Target owner |
| --- | --- | --- |
| Epic reread, snapshot and exactly-one-epic bound | keep | protocol 2 + task-form |
| Provenance and address-over-retelling | keep | protocol 3 + task-form |
| Wayfinding/Execution mode and zombie rebuild | keep with gate | protocol 4 |
| Evidence-gated closure and proof invalidation | keep | protocol 6 |
| Update epic in the same move | move write authority | `1plan-map` state event |
| Orchestrator-only plan writes and worker evidence | keep | protocol 5 |
| Fresh-reader reconstruction | keep | protocol 7 |
| Why this beats the queue | keep only as receipt | accepted `1planning` trajectory |
| JIT rule decides task creation | move decision | `1planning`; task-form records precondition |

## New constraints

- Required `ось:` in «Зачем» gives the planning cut a durable carrier. This
  closes clean-window guessing; it removes freedom to rebuild without knowing
  the accepted decomposition basis.
- The five-invariant gate separates routine rebuild from material replan. It
  closes `1plan-task`'s open-ended rebuild authority; it removes freedom to
  continue after the accepted task decision changes.
- Epic state changes are requested from `1plan-map`. This closes the two-writer
  seam; it removes direct epic writes from the task lifecycle.

## Predicted misreadings closed

- “Trajectory asks me to choose priority again” → the form labels it an
  accepted admission receipt.
- “Contradictory evidence always means rebuild locally” → the five-invariant
  comparison precedes rebuild.
- “Closing the task authorizes editing epic composition” → protocol 6 allows
  only a map-owned state event.

## Routing cases

- use: `Write the approved task contract now.`
- use before evidence classification: `New evidence arrived for the current task.`
- use after classification: `The accepted bounds still hold; rebuild subtasks.`
- skip: `Evidence changed the accepted task axis.` → `1planning`
- near miss: `Update the epic after task closure.` → `1plan-map`

## Current draft count

Top-level author count: `SKILL.md` 16 · `task-form.md` 18;
independent-predicate recount belongs to `check-approve`.
