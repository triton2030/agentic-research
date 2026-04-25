---
name: preference-sync
description: >
  Use this skill whenever the user reveals a durable preference or red line, even casually: "хочу", "не хочу", "люблю", "не люблю", "предпочитаю", "важно чтобы", "мне нравится", "мне не нравится", "всегда", "никогда", "I want", "I prefer", "I like", "I hate", "make this the default". Capture into `_ops/INTERVIEW.md` only. Skip one-off task facts, implementation details, and preferences already captured without drift.
---

# Preference Sync

Capture durable user preference signals into `_ops/INTERVIEW.md`.

## What It Does

1. Decide whether the phrase is a durable preference, red line, tone/style default, or must-not.
2. Read the relevant `INTERVIEW.md` section first.
3. Replace or merge stale/duplicate lines instead of appending noise.
4. Apply the preference to the current decision path by naming its routing or scope effect.

## Output Contract

```md
Preference synced: <short label>
Applied to this task as: <scope / Must-not / routing / tone>
```

## Skip

Skip factual corrections, transient taste about one artifact, technical decisions better owned by `instruction-layer` or `repo-shape`, and pure plan direction without a preference signal.

## Role Boundaries

- Writes only `_ops/INTERVIEW.md`.
- Does not update `PROJECT-PLAN.md`, task files, skill files, or root instructions.
- If the new preference contradicts stored truth, route to `contradiction-hold` before writing.

## References

- [references/interview-protocol.md](references/interview-protocol.md)

## Done When

The preference is current, non-duplicated, dated, and has a visible effect on the current work.
