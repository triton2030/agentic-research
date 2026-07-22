---
name: 1readable-code
description: >
  Use when meaningful code changes or reviews expose implementation choices
  that affect future change cost. Prefer fewer concepts and cohesive owners. In
  code-heavy repos, verify the existing architecture owner; skip architecture
  ceremony for scripts and small codebases.
---

# Readable Code

## Outcome

Leave code whose behavior and owner a future agent can find, understand, change
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

## Contract

For the touched behavior:

- Find the existing owner before editing. A small diff in the wrong owner is
  not a small change.
- Keep behavior searchable through stable names in files, symbols, types,
  errors and focused tests.
- Reuse existing seams. Add no dependency, layer, helper family, flag or folder
  pattern unless the current behavior needs it and total owned complexity falls.
- Separate decisions that fail independently: validation, policy, state change,
  IO and formatting. Do not split code for visual symmetry.
- Make supported boundaries and failures visible in code, types, errors or a
  focused proof; comments and broad green tests do not replace the contract.
- Delete obsolete paths exposed by the change, but avoid unrelated cleanup.

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
