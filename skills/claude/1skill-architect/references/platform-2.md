# Claude Skill Authoring

Read this reference when creating or substantially revising a Claude skill,
`description`, invocation policy, runtime transfer, or source-backed claims.

## Desired Result

The skill activates at the right moment and causally changes an observable
decision or supplies a precise operational advantage. It does not merely make
Opus 5 or Fable 5 perform an authoring checklist.

A cognitive core keeps necessity, natural default, named deficit, observable
proxy, transformation, minimal operators, thought demonstrations, controller,
feedback, evidence, and stop in the hot path. An operational core keeps the
exact advantage and minimum reproducible contract. Ordered steps appear only
when violating order reproduces a correctness, safety, or tool failure.

## Authoring Mechanics

Design chooses the surface, contract shape, routing claim, and evidence bar.
The official Claude authoring tools perform scaffolding, validation, forward
testing, measured benchmarks, and packaging.

Its step list is the mechanics of a specific tool, not the mandatory shape of
a skill body or a universal authoring ritual. Do not reproduce the matcher/eval
pipeline in this reference.

## Claude-Specific Done

- `SKILL.md` frontmatter has `name` and `description`; optional
  `disable-model-invocation` and `allowed-tools` match real runtime intent.
- Model-invoked versus user-invoked behavior is deliberate.
- References are one level deep and every bundled file has an action-changing
  route from `SKILL.md`.
- The actual live Claude skill root is verified; no path migration is inferred
  from another runtime.
- No `agents/openai.yaml`, Codex-only tool names, or Codex validation commands
  remain in the Claude projection.
- Tracked runtime projection and installed package match the shared owner.
