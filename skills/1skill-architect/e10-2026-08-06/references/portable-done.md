# Local Skill Contract

Open this only when the output includes "make a local skill", "rewrite this
skill", or "port this skill into another supported runtime".

## Portable Done

- `SKILL.md` frontmatter includes required `name` and `description`; optional
  fields appear only when the current runtime/spec or user requires them.
- Core necessity/mechanism/examples remain reachable without loading unrelated
  references; references are one level deep.
- Representative use/skip/near-miss cases cover live neighboring descriptions.
- The positive trigger surface can be named in one sentence; if it cannot be
  separated from near misses, return to the failure trace instead of expanding
  the description.
- Portable files contain no platform-only paths, metadata, commands, model
  routing, or validation claims; those live in `platform-skill-authoring.md`
  and the platform-owned package delta.
- A model-dependent deficit names the resolved model or target set, observation
  date, and model-change reopen signal; a stale limitation is deleted rather
  than preserved as timeless theory.
- The actual live skill root is verified; no path migration or cross-runtime
  parity is inferred from docs or analogy.
- Structural, routing, cognitive-transfer, operational, and distribution claims
  are reported as separate evidence layers; uncovered layers stay explicit.

## Progressive disclosure (дословно из LC Contract)

- **Progressive disclosure**: long domain variants, limits, source notes, and
  rare branches go to `references/`; deterministic fragile operations go to
  `scripts/`. Do not move the causal core out merely to make `SKILL.md` short.
