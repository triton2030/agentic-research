# Local Claude Skill Contract

Open this only when the output includes "make a local skill", "rewrite this
skill", or "port this skill into Claude Code".

## Contract

- **Proof gate**: repeated work, distinct trigger, real failure pattern, and a
  reason the behavior is not better owned by system prompt, `CLAUDE.md`,
  acceptance criteria, runtime guardrail, or script.
- **Surface gate**: explain why this is a skill, not an agent, hook, plain
  reference, instruction file, or script.
- **Trigger**: name the positive recurring moment. Keep near-miss cases in
  evaluation, not in the runtime contract.
- **Description**: one positive routing formulation with use case, trigger
  words, and important Delta. For model-invoked skills, front-load the opening
  because body is unavailable before activation.
- **Core body**: outcome/decision contract by default — result, decision
  standard, in-scope constraints, evidence, own conditional resources, and stop. Include a
  workflow only when order itself closes an observed failure.
- **Progressive disclosure**: long variants, examples, limits, source notes, and
  rare branches go to `references/`; deterministic fragile operations go to
  `scripts/`.
- **Validation**: run the official Claude structural check and
  an observable check for each material claim. Baseline or previous-version
  comparison is required only for relative-improvement claims. Choose the
  evidence bar here; use the live platform authoring tools for measurement mechanics.

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
