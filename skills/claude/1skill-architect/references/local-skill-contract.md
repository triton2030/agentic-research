# Local Claude Skill Contract

Open this only when the output includes "make a local skill", "rewrite this
skill", or "port this skill into Claude Code".

## Contract

- **Failure trace**: start from repeated real failure, correction, expensive
  workaround, or tool gap. Record what Claude naturally noticed and did.
- **Necessity proof**: connect natural default -> attraction -> trigger-specific
  harm -> blind spot -> break mechanism -> transfer. If task context or the
  nearest owner already supplies the mechanism, do not add a skill.
- **Deficit and proxy**: name the missing control act as a behavioral hypothesis
  and translate introspection into a check over visible text/context/artifacts.
- **Surface gate**: explain why this is a skill, not an agent, hook, plain
  reference, instruction file, or script.
- **Trigger**: name the positive recurring moment. Keep near-miss cases in
  evaluation, not in the runtime contract.
- **Description**: one positive routing formulation with use case, trigger
  words, and important stake. For model-invoked skills, front-load the opening
  because body is unavailable before activation.
- **Type**: cognitive shaper, operational package, or justified hybrid.
- **Cognitive core**: default/tell, deficit/proxy, `A -> B` transformation, one
  to three operators, only causally needed objective/phase/anchor controls,
  human/model asymmetry, controller, feedback, and thought demonstrations.
- **Operational core**: exact tool/knowledge advantage, required inputs, minimum
  order-sensitive workflow, evidence, boundary, and stop. Use deterministic
  enforcement when compliance cannot depend on reasoning.
- **Causal cells and form**: central guidance combines operator, machine-level
  rationale, and plausible boundary/anti-example. The package's own decision
  structure demonstrates the behavior it asks Claude to continue.
- **Progressive disclosure**: long variants, examples, limits, source notes, and
  rare branches go to `references/`; deterministic fragile operations go to
  `scripts/`.
- **Minimality**: delete obsolete scaffolding, repetition, generic brevity, and
  lines without action-changing Delta. Keep the causal explanation or example
  that makes the mechanism transfer.
- **Validation**: run the official Claude structural check and
  an observable check for each material claim. Baseline or previous-version
  comparison is required only for relative-improvement claims. Choose the
  evidence bar here; use live platform authoring tools for measurement
  mechanics. Test proxy, objective, phase, anchor, and form claims separately
  when the design relies on them.

## Claude-Specific Done

- `SKILL.md` frontmatter has `name` and `description`; optional
  `disable-model-invocation` and `allowed-tools` match real runtime intent.
- Model-invoked versus user-invoked behavior is deliberate.
- References are one level deep and every bundled file has an action-changing
  route from `SKILL.md`.
- The actual live Claude skill root is verified; no path migration is inferred
  from another runtime.
- No `agents/openai.yaml`, Codex-only tool names, or Codex validation commands
  remain.
- Repository canonical copy and installed package are semantically identical.
