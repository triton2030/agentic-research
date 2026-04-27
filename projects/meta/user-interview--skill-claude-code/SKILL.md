---
name: user-interview
description: >
  Use for durable user knowledge: preferences, vision, goals, constraints, tone, wants, don't-wants, domain-question answers, and conflicts with stored user truth. Own `_ops/INTERVIEW.md`. Route domain/prerequisite uncertainty to `domain-clarifier`; skip one-off task facts and implementation-only details.
---

# User Interview

Capture durable knowledge about the user into `_ops/INTERVIEW.md`.

## Role

Own the user's profile: preferences, vision, constraints, taste, red lines,
answers to domain questions, and reasons for changing prior preferences.

This is not a task planner and not a strategy writer. It makes downstream
skills better by keeping user truth current.

This trigger applies even when the user is mid-flow in another skill
(`strategy-discussion`, `project-roadmap`, `task-contract`). A preference
signal during a strategic dialog still belongs to `INTERVIEW.md` —
`STRATEGY-DISCUSSION.md` is point-in-time decisions, not durable preferences.
Different files, different lifetimes; do not substitute one for the other.

## What It Does

1. Decide whether the signal is durable: preference, red line, vision,
   constraint, taste, success picture, or answer to a consequential question.
2. Read the relevant `INTERVIEW.md` section first.
3. Replace or merge stale duplicates instead of appending noise.
4. If the new signal conflicts with stored user truth, stop and ask what
   changed: situation, priority, evidence, or preference.
5. After the reason is clear, update `INTERVIEW.md` and apply the result to the
   current routing, scope, Must-not, or verification depth.

## Question Discipline

Ask only questions whose answer changes a future decision. Explain briefly:
why the question matters, what choices it affects, and what risk it removes.

If the question is about domain prerequisites, missing middle, or strategic
branching, route to `domain-clarifier`.

## Output Contract

```md
User truth synced: <short label>
Applied as: <scope / Must-not / routing / tone / verification depth>
```

When asking a conflict question:

```md
Stored truth: <short quote>
New signal: <short quote>
Question: What changed?
```

## Skip

Skip one-off task facts, transient artifact comments, implementation choices
owned by the expert, and domain gaps better handled by `domain-clarifier`.

## Role Boundaries

- file writes only `_ops/INTERVIEW.md`.
- Does not update `PROJECT-ROADMAP.md`, task files, skill files, or root docs.
- Does not create strategy or task criteria.

## References

- [references/interview-protocol.md](references/interview-protocol.md)

## Done When

The user truth is current, non-duplicated, dated, and visibly affects the next
decision path.
