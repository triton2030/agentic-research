---
name: domain-clarifier
description: >
  Use when strategy, task ordering, prerequisites, or implementation direction depends on domain knowledge the agent cannot honestly ground. Ask only consequential questions and explain why each answer changes strategy, task structure, architecture, scope, or criteria. Skip preference capture handled by `user-interview`.
---

# Domain Clarifier

Ask consequential domain questions before the agent invents expertise.

## Role

This skill protects planning quality. It fires when the agent cannot honestly
judge whether a Stage, task, subtask, prerequisite, or branch is complete
without domain knowledge.

## What It Does

1. Name the domain uncertainty in plain language.
2. State the decision that depends on it: strategy, task order, architecture,
   scope, criteria, or verification.
3. Ask the smallest set of questions whose answers change that decision.
4. For every question, explain why it matters and what future risk it removes.
5. After the user answers, route durable user truth to `user-interview`, route
   strategy changes to `project-roadmap`, and route task shape to
   `task-contract`.

## Question Gate

Do not ask if every plausible answer leads to the same next move. Take a
position instead and name the assumption.

Ask when the answer can change:

- whether Stage 1 is actually first;
- whether a missing intermediate Stage exists;
- whether a prerequisite task must come before current work;
- whether a task belongs in this phase;
- whether criteria or verification need to be different.

## Output Contract

```md
Domain uncertainty: <what is unknown>
Decision affected: <strategy / task order / architecture / scope / criteria>
Question: <one consequential question>
Why it matters: <what changes by answer>
Risk removed: <future failure avoided>
```

## Skip

Skip ordinary preference capture, routine task criteria, implementation trivia,
and questions whose answer does not change the plan.

## Role Boundaries

- Does not write files directly.
- Does not become strategy, task, or interview owner.
- Routes answers to `user-interview`, `project-roadmap`, or `task-contract`.

## References

- [references/question-discipline.md](references/question-discipline.md)
