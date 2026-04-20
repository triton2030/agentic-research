# Issues

Use this file for discovered problems, risks, anomalies, and unknowns that are not yet scheduled work.

When an issue becomes planned work, move it out of this file and create the task in `ops/TASKS.md`.

## Open Issues

### Boundary Between Research Tracks And Base Guidance

Why it matters:
If the boundary is blurry, the research folders will duplicate `AGENTS.md`, `knowledge/guides/perfect-skills.md`, and `knowledge/guides/perfect-system-prompts.md` instead of strengthening them.

Current signal:
The repository now has both a stable instruction layer and several research tracks, but the promotion rule is not yet written down.

What is still unknown:
How much evidence is enough before a point moves from research into the base layer.

When to promote into a task:
When duplication starts appearing or when the same insight is reused across multiple sessions.

### Evidence Quality For `ops`

Why it matters:
Without concrete examples, research about `ops` can become persuasive language without proof.

Current signal:
We now have a place for hypotheses and reasoning, but not yet a case library that shows where the pattern really pays off.

What is still unknown:
Which evidence signals matter most: speed to clarity, fewer wrong turns, better decisions, or stronger reusable instructions.

When to promote into a task:
When we have enough real sessions to compare outcomes with and without `ops`.

### Scope Boundary: `meta/` vs Domain Tracks

Why it matters:
If the boundary stays fuzzy, cross-cutting ideas may bounce between `meta/` and the domain folders without a stable home.

Current signal:
`meta/` now exists as a separate top-level direction, but the exact line between cross-cutting research and domain-specific research is not yet formalized.

What is still unknown:
Which questions should belong in `meta/` by default and which should stay inside `design/`, `dev/`, or `business/`.

When to promote into a task:
When similar notes start appearing in two places or when a new research topic has no obvious home.
