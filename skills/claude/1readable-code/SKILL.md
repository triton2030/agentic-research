---
name: 1readable-code
description: >
  Use when a code change or review introduces meaningful structural choices
  affecting ownership, indirection, implementation concepts, or change radius.
  Skip tiny local edits; explicit interface or seam design →
  `1codebase-design`.
---

# Readable Code

## Outcome

Leave code whose behavior and owner a future agent can find, understand, change,
and verify without mapping the whole project. This skill supplies a structural
preference when several implementations satisfy the requested behavior; it is
not a generic style checklist.

## Structural Preference

Prefer fewer concepts, modes, dependencies and moving parts; direct flows;
cohesive ownership; stable domain names; and a smaller implementation that fits
in context. Accept less convenience, flexibility or feature breadth when the
requested outcome still holds and meaningful complexity disappears.

Do not trade away an explicit requirement, correctness, data integrity,
security or stability. Surface the conflict if simplicity would require that.

## Quality Standard

For the touched behavior, a readable result has:

- one findable owner per decision or contract, with explicit handoffs in a
  genuinely multi-owner flow; a small diff in the wrong owner is still a large
  structural mistake;
- stable search terms across files, symbols, types, errors, and focused tests;
- no new dependency, layer, helper family, flag, or folder pattern unless the
  current behavior needs it and total owned complexity falls;
- independent decisions separated where they can fail independently:
  validation, policy, state change, IO, and formatting—not for visual symmetry;
- supported boundaries and failures visible in code, types, errors, or focused
  proof rather than implied by comments or broad green tests;
- obsolete paths exposed by the change removed without unrelated cleanup.

Prefer deletion or direct local code when behavior is preserved. Add an
abstraction only when it names a real concept, hides meaningful complexity,
isolates a side effect or removes current duplication. Generic wrappers,
managers, providers, option bags and dynamic indirection are not improvements
by themselves.

## Architecture Owner Gate

Open [`references/project-legibility.md`](references/project-legibility.md)
only when several signals show a genuinely code-heavy repository: multiple
long-lived subsystems or processes, consequential persistence/external edges or
dependency direction, and recurring whole-tree mapping cost for fresh agents.

File count alone does not pass. Skip the architecture route for scripts, small
utilities, single-purpose CLIs/apps, snippets, scratch work, generated code and
vendored trees. If the threshold remains unclear, do not create documentation;
report the concrete mapping cost or structural risk.

`1readable-code` does not choose a new canonical document or instruction route.
Missing/competing architecture owner → `1ia-audit`; durable instruction route →
`1instruction-layer`.

## Evidence

Use the smallest durable check that fails when the changed behavior is wrong.
For a bug, connect symptom, owner and cause before fixing. For review or
explanation, keep findings tied to concrete code evidence and do not mutate.

Before closing, establish:

- obvious search terms find the intended behavior;
- the local contract and important failure paths are visible;
- the proof exercises what changed;
- unrun checks, assumptions and material residual risk are named.
