---
name: user-truth
description: >
  Use only to sync durable user truth discovered elsewhere: preferences, goals,
  constraints, red lines, tone, success picture, wants, don't-wants, and
  consequential answers that should affect future routing, scope, Must-not, or
  verification depth. Own `_ops/INTERVIEW.md`. Do not run interviews, do not ask
  broad discovery questions, and skip one-off task facts, implementation trivia,
  and strategy/domain branches owned by `1strategy-discussion`.
---

# User Truth

## Role

Store durable truth about the user. This skill is memory sync, not an interview
process.

Most user truth is discovered inside `1strategy-discussion`, `project-strategy`,
or task work. This skill only decides whether the signal is durable, resolves
conflicts with existing memory, and updates `_ops/INTERVIEW.md`.

## What To Store

Store a signal only when it can affect future routing, scope, tone, Must-not,
strategy, task criteria, or verification depth:

- preference or taste;
- goal, vision, success picture, or motivation;
- constraint, red line, don't-want, or risk tolerance;
- answer to a consequential question;
- explanation for changing a prior preference.

Skip one-off facts, current-task details, implementation choices the agent
should decide, and unresolved strategy/domain branches.

## Workflow

1. Read the relevant part of `_ops/INTERVIEW.md` if it exists.
2. Decide whether the new signal is durable and decision-changing.
3. If it conflicts with stored truth, ask one question: what changed: situation,
   priority, evidence, or preference?
4. Update or merge the existing line instead of appending duplicates.
5. Apply the saved truth to the current route, scope, tone, Must-not, or
   verification depth.

## Output Contract

```md
User truth synced: <short label>
Applied as: <routing | scope | tone | Must-not | verification depth>
```

If conflict remains unresolved:

```md
Stored truth: <short quote>
New signal: <short quote>
Question: What changed?
```

## Role Boundaries

- Owns only `_ops/INTERVIEW.md`.
- Does not create strategy, task criteria, instruction rules, or repo shape.
- Routes unresolved approach/domain branches to `1strategy-discussion`.

## Done When

The stored user truth is current, non-duplicated, and visibly affects a future
decision path.
