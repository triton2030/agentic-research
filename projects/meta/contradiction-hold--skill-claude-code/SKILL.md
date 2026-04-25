---
name: contradiction-hold
description: >
  Use this skill whenever a new request conflicts with stored plan or preference truth: "но раньше было иначе", "сделай наоборот", "забудь прошлое", "поменяй правило", "неважно что написано", "давай нарушим", "override", "ignore the plan", "change the default", "do the opposite", "break the rule", "forget that". Hold the conflict in dialogue until motivation is clear. Skip normal edits, new preferences without conflict, and already-resolved plan changes.
---

# Contradiction Hold

Use this to prevent silent override of stored project truth.

## What It Does

1. Quote the stored side from `INTERVIEW.md` or `PROJECT-PLAN.md`.
2. Quote the new request in plain language.
3. Ask what changed: situation, priority, evidence, or user preference.
4. After motivation is clear, route the update to `preference-sync` or `project-strategy`.

## Output Contract

```md
**Conflict:** <stored truth> vs <new request>
**Hold:** I need the reason before changing direction.
**Question:** What changed?
```

## Skip

Skip if the new request is merely more specific, if no durable source conflicts, or if the user has already supplied a clear reason.

## Output Contract

Emit a compact receipt, then return control to the current task. Keep it to 3-5 lines unless blocking.

## Role Boundaries

- Do not become a strategy, architecture, or task-file owner.
- Do not broaden scope beyond this moment.
- Route to the owner-skill when durable state must change.

## Done When

The relevant rule is freshly in context, the next owner or action is clear, and no extra artifact was created by this skill.
