---
name: 1plan-task
description: >-
  Use after one task is approved, or while its accepted bounds still hold, to
  write, continue, or rebuild its isolated durable contract. Not for admission
  or epic composition.
---

# Plan task — isolated execution contract

## Unique Context

The task file is the interface for a parallel agent or clean window that does
not share the planning chat. Its special job is isolation: preserve the
accepted decision, make execution and stopping unambiguous, and prevent one
task from taking work owned by another task or epic.

## User Goals

- One approved task becomes one self-sufficient, hard-bounded contract inside
  exactly one current epic, using addresses instead of retelling owned truth.
- A clean window can execute, hand off, or stop from the file alone: intent,
  boundary, mode, axis, ordered outcomes, provenance, evidence, next, and stop.
- State remains evidence-true: routine execution may rebuild within the
  accepted decision, while a broken goal, epic, priority, boundary, or axis
  stops the task and returns it to `1planning`.

## Behavior Protocol

> «скилл задач — это скилл изолированности задач»

1. For a new task, require the approved `1planning` landing values; for an
   existing task, treat its recorded values as the accepted decision until
   evidence breaks them.
2. Reread the full current epic, write and verify `эпик-снимок`, and confirm
   exactly one epic contains the task; a mismatch stops serialization and
   returns to the planning/map owners.
3. Write or reconcile the contract per [task-form](references/task-form.md),
   preserving provenance and recording trajectory, mode, axis, boundary,
   premise, evidence target, and rejected routes without re-deciding admission.
4. On new evidence, compare goal, epic, priority, boundary, and axis with their
   accepted carriers; if all hold, rebuild only affected subtasks, otherwise
   record the break, stop execution, and re-enter `1planning`.
5. Only the orchestrating window writes the task file; workers and subagents
   return addressable proof under the epic's `_evidence/**`, while wave
   mechanics remain with `1orchestration`.
6. Close only with evidence for the task as a whole and consumer acceptance;
   invalidate downstream proofs after an upstream change, then ask
   `1plan-map` to own the epic state event and run the project instrument.
7. Before handoff, a clean reader reconstructs intent, boundary, mode, axis,
   evidence, next, and stop and names every ambiguous line; fix the file, not
   the chat.

## Boundaries

Admission and material replan belong to `1planning`. Epic composition, state,
and dashboard writes belong to `1plan-map`; owner-only questions live through
`1interview-tool`, with only their address in the task.
