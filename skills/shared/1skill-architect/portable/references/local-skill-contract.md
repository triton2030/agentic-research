# Local Skill Contract

Open this only when the output includes "make a local skill", "rewrite this
skill", or "port this skill into another supported runtime".

## Contract

- **Failure trace**: start from a repeated real failure, correction, expensive
  workaround, or tool gap. Record what the agent naturally noticed and did;
  do not start from a skill name or desired folder.
- **Necessity proof**: connect natural default -> why it is attractive ->
  trigger-specific harm -> mechanism that breaks the chain -> new cases the
  mechanism should resolve. If ordinary task context or the nearest owner
  already supplies it, do not add a skill.
- **Deficit and proxy**: name the missing control act as a behavioral hypothesis,
  then translate introspective language into a check over observable text,
  context, or artifacts. Do not use model-anatomy metaphors as proof.
- **Surface gate**: explain why this is a skill, not an agent, hook, plain
  reference, instruction file, acceptance criterion, guardrail, or script.
  Safety and invariant surfaces must name the protected risk; use a
  deterministic enforcement layer when compliance cannot depend on reasoning.
- **Type**: name `cognitive shaper`, `operational package`, or a justified
  hybrid. A cognitive shaper changes inference-time representation or decision;
  an operational package supplies unavailable precision, tooling, or fragile
  order.
- **Cognitive core**: for a shaper, keep natural default and tells, `A -> B`
  transformation, observable proxy, one to three operators, human/model
  asymmetry, reusable controller, feedback, and minimal thought demonstrations
  in the hot path. Add a local objective, phase boundary, or checked anchor only
  when it breaks the demonstrated causal chain.
- **Operational core**: state the relevant tool/knowledge advantage, required
  inputs, minimum order-sensitive workflow, exact evidence, and stop. Do not
  invent cognitive ceremony around a deterministic operation. Preserve strict
  order only when order itself is part of correctness.
- **Thought demonstrations**: teach default -> tell -> operation -> changed
  decision. Include a plausible mechanism-free anti-example and a transfer case
  when examples materially cause the behavior. A final-output example alone is
  insufficient for a cognitive claim.
- **Causal cells and form**: central guidance combines operator, machine-level
  rationale, and plausible boundary/anti-example. The package's own decision
  structure demonstrates the behavior it asks the reader to continue.
- **Trigger and description**: name one positive recurring moment. For
  model-invoked skills, front-load condition and stake because selection happens
  before the body is available and metadata may be shortened. Keep full causal
  proof and examples in the body.
- **Progressive disclosure**: long domain variants, limits, source notes, and
  rare branches go to `references/`; deterministic fragile operations go to
  `scripts/`. Do not move the causal core out merely to make `SKILL.md` short.
- **Boundary**: name the authority the skill does not receive and keep neighbor
  menus or non-applicable routing out of its body. Declare an external skill or
  tool dependency only when indispensable: name its exact handle, information
  job, and failure behavior when unavailable.
- **Minimality**: before adding rules, delete or merge obsolete scaffolding,
  repetition, generic brevity, and lines without action-changing Delta. Do not
  prune the causal explanation or example that makes the mechanism transfer.
- **Validation**: structural validation proves packaging; routing cases prove
  selection; a cognitive claim needs changed behavior on an unshown case;
  operational claims need reproducible exact output. Use baseline,
  previous-version, or mechanism ablation when claiming improvement. Increase
  discriminating evidence with breadth, frequency, risk, collision, external
  effects, and regression history. Test proxy, objective, phase, anchor, and
  form claims separately when the design relies on them.

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
- The actual live skill root is verified; no path migration or cross-runtime
  parity is inferred from docs or analogy.
- Structural, routing, cognitive-transfer, operational, and distribution claims
  are reported as separate evidence layers; uncovered layers stay explicit.
