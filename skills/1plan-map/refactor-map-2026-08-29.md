# Refactor map — 1plan-map — 2026-08-29

Approved family boundary: `_ops/chat-recall/2026-08-29-152644-codex-01a04d0d.md:18-19`.
Earlier function: `_ops/chat-recall/2026-08-26-220614-claude-4ee6bbef.md:24`.

## Function

Decision and durable owner for epic composition and epic state, including the
owner dashboard. It exposes a task-admission need but never decides or writes
the task.

## Old instruction groups

| Group | Disposition | Target owner |
| --- | --- | --- |
| Frames, principles and GOAL before composition | keep | protocol 1 |
| Bootstrap map root and instrument | keep, compress | protocol 1 |
| Create, audit/refactor, event update | keep as two authorities | protocol 2 |
| Outcome epics, non-overlap, order and dependencies | keep | protocol 3 + map-form |
| Carrier evidence, permanent closed/deferred history | keep | protocol 5 + map-form |
| Visible composition approval | keep | protocol 3 |
| Dashboard templates and machine schema | keep | references |
| Frontier creates the next JIT task | move decision/write | `1planning` → `1plan-task` |
| Task-side invariants in map red-list | keep as instrument integration | map-form |

## New constraints

- Composition and state are two named write scopes. This closes the observed
  two-writer ambiguity; it removes freedom for a state update to alter epic
  topology incidentally.
- A taskless frontier is a planning signal, not task authorization. This closes
  triple ownership of JIT creation; it removes the map's freedom to create a
  task in the same state move.

## Predicted misreadings closed

- “Advancing the frontier includes inventing the next task” → protocol 4
  exposes the need and routes admission.
- “Updating status permits opportunistic reorder” → protocol 2 separates state
  from composition before the write.
- “Task closure lets `1plan-task` edit the epic directly” → boundary makes the
  map skill the state writer.

## Routing cases

- use: `Audit and reorder the current epic map.`
- use: `Close this epic and advance the frontier.`
- skip: `Write the approved task file now.` → `1plan-task`
- near miss: `Should this candidate task start now?` → `1planning`

## Current draft count

Top-level author count: `SKILL.md` 14 · `map-form.md` 18 · `dashboard.md` 6;
independent-predicate recount belongs to `check-approve`.
