---
name: 1planning
description: >-
  Use when “what next?”, a candidate task, major error, or material replan
  needs admission and a visible task-level cut before plan files change. Not
  for epic composition or routine execution.
---

# Planning — admission and task-level cut

## Unique Context

Planning is the owner's skeptical gate, not a plan-file writer. Starting the
available task is easy; proving that it is the right task, exposing the cut in
chat, and preserving the accepted decision for a clean window are the missing
intervention.

## User Goals

- Candidate work is admitted or rejected against `GOAL.md`, the current epic
  map and queue, blockers, displacement, and the rules governing its domain.
- Admitted work has a visible task-level cut in chat: boundary, mode, named
  axis, methods, material premises, and the nearest checkable frontier.
- Only the owner's approval of the shown cut becomes durable; every accepted
  decision lands in the map or task contract instead of disappearing with chat.

## Behavior Protocol

> «когда вызывается скилл планирование, я хочу, чтобы агент прямо в чате мне
> обязательно написал его шаги, как он считает лучше подойти к этой задаче»

1. Read `GOAL.md`, the current epic and live tasks, root instructions, and the
   domain instructions and skills; show the lines that constrain the decision.
2. Challenge admission: name why the candidate is next, what it displaces, and
   which blocker or map order supports it; missing or changing epic composition
   goes to `1plan-map` and returns here before task admission.
3. Show the cut in chat: method point → changed plan element, one named axis
   rather than bare chronology, and only the nearest checkable frontier;
   Wayfinding puts Next at the earliest expensive divergence, while Execution
   uses the written invention probe and prefers the reversible door at equal
   outcomes. Unknowns stay research or decision gates, and a material premise
   stops the cut.
4. Apply `1use-principles` and show each principle with what it settled;
   unresolved owner-only choices go through `1interview-tool`; produce the
   landing values for epic, trajectory, mode, axis, boundary, premise, and
   evidence target without writing plan files.
5. Obtain the owner's approval of this exact cut; the opening request is not
   approval, while one message may approve map composition and the task cut
   only when it names both.
6. Route the approved values to `1plan-task`, or the approved epic composition
   to `1plan-map`; routine execution stays there, but a changed goal, epic,
   priority, boundary, or axis re-enters this protocol.

## Boundaries

Native Plan Mode active → stay silent. Epic composition and map state belong
to `1plan-map`; task serialization and routine execution belong to
`1plan-task`.
