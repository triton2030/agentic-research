# Codex Skill Authoring

Read this when creating or substantially changing a Codex skill, `description`,
invocation policy, runtime transfer, or source-backed claims.

## Contents

- Core Rules
- Trigger Description Method
- Canvas Audit
- Invocation Policy
- Authoring And Distribution
- Evaluation
- Validation Handoff
- Codex-Specific Done
- Source Discipline

## Core Rules

- `description` is the discovery contract when `allow_implicit_invocation` is
  true. Put the positive use case, trigger words, and important stake in the
  opening: name the plausible failure or lost advantage that makes opening the
  body worthwhile. Codex's initial skill list is budgeted; descriptions may be
  shortened and skills may be omitted.
- Classify the package before choosing body shape. A **cognitive shaper** changes
  attention, representation, alternatives, decision policy, verification, or
  learning from feedback. An **operational package** supplies precise knowledge,
  a tool advantage, schema, asset, or fragile order. Do not force both through
  one universal template.
- A cognitive `SKILL.md` keeps the causal core in the hot path: necessity proof,
  natural default, named deficit and tells, observable proxies, explicit
  transformation, minimal operators, contrastive thought demonstrations,
  reusable controller, feedback, evidence, boundary, and stop. This is not
  generic chain-of-thought prescription; it is the mechanism whose absence
  reproduces the observed failure.
- An operational `SKILL.md` stays compact: relevant advantage, required inputs,
  minimal workflow where order matters, evidence, boundary, and stop. Do not
  route the agent to "read all references".
- Frontmatter requires `name` and `description`. House default: add no other
  fields unless the current runtime/spec or user requires a supported field.
- `agents/openai.yaml` owns UI metadata, `policy.allow_implicit_invocation`, and
  declared MCP/tool dependencies.
- A skill is the authoring unit; a plugin is the distribution unit. Start
  instruction-only. Add scripts only for deterministic behavior, external
  tooling, or a repeated fragile operation.
- Safety or invariant claims name the protected risk. If the behavior must hold
  regardless of reasoning quality, use deterministic enforcement rather than a
  prose-only skill.
- Declare an external skill or tool dependency only when the positive moment
  cannot succeed without it. Name the exact handle, information job, and
  failure behavior; neighbor menus and optional reviews are not dependencies.
- Add only action-changing **Delta**: a cognitive act the model does not
  reliably initiate, a non-obvious distinction, domain logic, failure mode,
  correction, or tool advantage it cannot infer reliably from the task, current
  context, and nearest owner. Generic competence does not earn prompt budget.
- Treat claims about model mechanics as behavioral hypotheses. Name an
  observable tell and transfer consequence; do not use "missing organ" or a
  literal incapacity claim as evidence.
- Translate introspective imperatives into observable proxies. When the failure
  depends on the wrong local optimization, phase coupling, early drift, or
  human/model cost asymmetry, add only the causally matching local objective,
  phase boundary, checked anchor, or labor inversion. None is a universal field.
- Write central cognitive guidance as causal cells: operator + why the natural
  default bypasses a naked command + plausible boundary or anti-example. Make
  the skill's own decision structure congruent with the behavior it teaches.
- State required inputs or available context and the expected output explicitly.
- Keep reference files one level below `references/`; if a reference is over
  100 lines, add a plain-text table of contents near the top.
- Keep the body below 500 lines. Move rare branches, long domain variants,
  source notes, limits, and command detail into references. Keep a central
  necessity proof or thought demonstration in `SKILL.md` when removing it makes
  the mechanism arbitrary or teaches only output form.
- For `GPT-5.6`, start from the smallest **causally complete** contract that
  changes the claimed behavior. Prune obsolete scaffolding, repetition, generic
  brevity, and irrelevant tools; do not prune the explanation or example that
  makes a cognitive operator transfer. Preserve strict step order only where
  order itself is a requirement; tune reasoning effort only after the prompt,
  mechanism, and tool contract are sound.

## Trigger Description Method

Implicit descriptions compete in a budgeted initial list and may be shortened or
omitted. A valid description satisfies both the full routing function and its
budgeted form.

### Complete Routing Function

The core is **Condition x Stake**:

- **Condition**: an observable anchor the model can recognize now, such as a
  path, artifact, action, or user phrase. Prefer path/file/action over abstract
  categories.
- **Stake**: the plausible failure or lost advantage that makes the skill worth
  opening. The model sees this before the body and needs a reason to spend
  context on the full mechanism.

It includes the hot zone, trigger-surface-not-capability, and one positive
trigger per branch.

### Budgeted Form

The shorter form preserves the same routing function. The description is a
pointer to the body, not a summary of it.

Useful compression removes:

- identity, full necessity proof, thought demonstrations, and mechanism detail
  that belong in body or references;
- words duplicated by a leading term that already carries anchor and delta;
- skip-routes and descriptions of non-applicable tasks.

If the skill is deliberate/manual and does not need model discovery,
`allow_implicit_invocation: false` removes the discovery cost entirely.

Cut-test: remove a phrase and ask whether the same skill would still fire
against live neighbors. If yes, the phrase is no-op or body material. The
portable ceiling is a limit, not a target; live budget evidence is stronger than
a local character-count heuristic.

If the positive trigger surface cannot be stated in one sentence and separated
from near misses, the design is unresolved. Return to the failure trace, owner,
or boundary; do not hide the ambiguity in a longer description.

## Canvas Audit

Treat the full installed model-invoked description set as the authoring-time
candidate canvas. Runtime co-presence is not guaranteed: audit the full live set,
then inspect the actual prompt surface when the trigger is broad or adjacent.

Cut repeated characterization of neighboring skills, bare pointers to them,
skip-routes, handoff catalogs, and repeated meta scaffolding. Resolve collisions
by narrowing the positive trigger of the owners themselves. Keep near-miss cases
in evaluation; do not serialize the candidate canvas into a skill body.

Do not cut shared trigger phrases by literal dedupe. A shared trigger phrase is
a collision/ownership question. Decide which surface owns the moment, or make
the dual-fire intentional and documented.

Literal grep undercounts duplication because the duplicate is often semantic:
the same routing thought in different words.

## Invocation Policy

Choose model-invoked when Codex must discover the skill without the user naming
it.

Choose user-invoked when the skill is a deliberate expert lens, expensive, rare,
or personally routed by the user. In Codex:

```yaml
policy:
  allow_implicit_invocation: false
```

For user-invoked skills, keep `interface.default_prompt` short and explicitly
mention `$skill-name`.

## Authoring And Distribution

- Start from a working failure trace, correction, runbook, command, or accepted
  output when one exists. For a cognitive shaper, reconstruct what the model
  noticed, represented, defaulted, and treated as sufficient evidence before
  writing rules. For an operational package, identify the exact precision,
  safety, or reproducibility advantage the default route lacks.
- Thought demonstrations teach the transition, not merely the final artifact.
  Prefer a compact set containing a plausible default, transformation,
  mechanism-free anti-example, and transfer case. Do not treat visible reasoning
  as proof of faithful private chain-of-thought.
- If a workflow is easier to show than describe, Record & Replay is a
  conditional drafting route; the result still needs review and validation.
- Use the platform's live authoring tools for concrete examples, degrees of
  freedom, progressive disclosure, reusable resources, scaffolding, structural
  validation, and forward testing. This design contract does not replace those
  mechanics.
- Distribution and multi-skill/tool bundles are packaging concerns, not branches
  of a skill body.
- If the surface gate chooses an agent, hook, or instruction instead of a skill,
  stop skill authoring after naming the owner and hand off to that live surface.

## Evaluation

Design chooses observable claims and the evidence capable of refuting them;
platform authoring tools execute the measurement mechanics.

- Admission claims need a real recurring moment, Delta, and failure evidence.
- Routing claims need representative use/skip/near-miss cases against live
  neighboring descriptions.
- Structure claims need the platform validator and reachable bundled resources.
- Cognitive mechanism claims need an observable changed representation,
  decision, probe, escalation pattern, or response to feedback on a realistic
  unshown task. Filled fields and fluent explanations are compliance evidence,
  not transfer evidence.
- Proxy, objective, phase, and anchor claims need their own discriminating
  observation: the proxy changes action, the metric survives shortcut pressure,
  phases prevent the named interference, and an anchor can reopen when wrong.
- Thought-demonstration claims benefit from ablation: remove or replace the
  central example and check whether the intended operation still transfers.
- Form-congruence claims benefit from a continuation case outside literal rule
  coverage: does the text's latent genre still produce the intended decision?
- Operational behavior claims need an exact output, reproducible run, or other
  observable assertion on a realistic task.
- Relative-improvement claims need a baseline or previous version.
- Distribution claims need metadata/projection sync where those surfaces exist.

Broad, frequent, risky, credential/network, collision-prone, or
already-regressed surfaces require stronger discriminating evidence for the
risks they raise, not a fixed package of every check.

## Validation

- Run structural validation, metadata sync, and any forward test through the
  live platform authoring tools; do not rebuild a parallel matcher pipeline.
- For collision-prone implicit surfaces, inspect the current prompt surface
  through the live runtime when visibility is material; keep the mechanism out
  of this design contract.
- Treat prompt visibility as selection evidence, not output-quality proof. A
  behavioral claim still needs an observable with/without, previous-version, or
  mechanism-ablation comparison when the relative effect is material.

## Codex-Specific Done

- `SKILL.md` frontmatter includes required `name` and `description`; optional
  fields appear only when the current runtime/spec or user requires them.
- `agents/openai.yaml` default prompt names `$skill-name`, communicates the
  current mechanism, and matches the intended implicit-invocation policy.
- Required MCP/tool dependencies are declared in `agents/openai.yaml`.
- The actual live Codex skill root is verified; no path migration or
  cross-runtime parity is inferred from docs or analogy.
- No Claude-only runtime paths, fields, or commands remain in the Codex
  projection.
- Tracked runtime projection and installed package match the shared owner.

## Source Discipline

- OpenAI-endorsed claims need official OpenAI sources:
  `developers.openai.com`, `platform.openai.com`, or bundled OpenAI skills/docs.
- Local engineering patterns can be stated as local engineering, not OpenAI
  recommendations.
- Do not invent metrics or availability. Re-fetch current docs when model, API,
  or product behavior could have changed.

Official baseline:

- `https://developers.openai.com/codex/build-skills`
- `https://learn.chatgpt.com/use-cases/reusable-codex-skills`
- `https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6`
- `https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6`
- `https://developers.openai.com/codex/codex-manual.md`

Local engineering heuristics, not OpenAI requirements: **Condition x Stake**,
necessity proof, cognitive-shaper/operational-package distinction, thought
demonstrations, candidate-canvas vocabulary, and risk-proportional evidence
selection.

Current Codex docs, public packages, and the live bundled runtime can expose
different skill roots or package revisions. Verify the actual live root and
prompt surface; do not infer a path migration from one source alone.
