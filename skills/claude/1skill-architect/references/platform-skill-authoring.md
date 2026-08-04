# Claude Skill Authoring

Read this reference when creating or substantially revising a Claude skill,
`description`, invocation policy, runtime transfer, or source-backed claims.

## Contents

- Desired Result
- Core Contract
- Class and Body Shape
- Discovery Contract
- Candidate Canvas and Invocation
- Evidence by Claim
- Model Baseline
- Authoring Mechanics
- Claude-Specific Done
- Source Discipline

## Desired Result

The skill activates at the right moment and causally changes an observable
decision or supplies a precise operational advantage. It does not merely make
Opus 5 or Fable 5 perform an authoring checklist.

A cognitive core keeps necessity, natural default, named deficit, observable
proxy, transformation, minimal operators, thought demonstrations, controller,
feedback, evidence, and stop in the hot path. An operational core keeps the
exact advantage and minimum reproducible contract. Ordered steps appear only
when violating order reproduces a correctness, safety, or tool failure.

## Core Contract

- `description` is the discovery contract for a model-invoked skill. The main
  positive use case, trigger words, and important Delta must survive metadata
  shortening; the body is unavailable before activation.
- Classify the body as cognitive shaper, operational package, or justified
  hybrid before choosing its shape. Do not force both through one template.
- `SKILL.md` is the smallest causally complete contract, not a textbook. Keep
  the mechanism whose removal reproduces the observed failure in the hot path.
- Include only **Delta** in a skill: non-obvious domain logic, a failure mode,
  a correction, or a professional move the model cannot reliably infer from
  the task, current context, and nearest owner.
- Treat model-mechanics claims as behavioral hypotheses. Name an observable
  tell and transfer consequence; a "missing organ" metaphor is not evidence.
- Translate introspective imperatives into observable proxies. Add a local
  objective, phase boundary, checked anchor, or labor inversion only when the
  demonstrated failure depends on that lever.
- Write central cognitive guidance as causal cells: operator + why the natural
  default bypasses a naked command + plausible boundary or anti-example. Make
  the skill's own decision structure congruent with the behavior it teaches.
- Name authority, required output, and side-effect boundaries only when they
  change the permitted action.
- Do not instruct the agent to read every reference. Give each bundled file an
  action-changing route from `SKILL.md`.
- Keep reference files one level deep; give a long reference a short plain-text
  content map. A body under 500 lines is a ceiling, not a target.
- Scripts are justified by deterministic behavior, external tooling, or a
  recurring fragile operation; examples do not compensate for a weak
  interface.

## Class and Body Shape

A **cognitive shaper** changes attention, representation, alternatives,
decision policy, verification, or learning from feedback. Keep its necessity
proof, default/tell, deficit/proxy, `A -> B` transformation, causally selected
control levers, contrastive thought demonstrations, reusable controller,
feedback, evidence, boundary, and stop.

An **operational package** supplies precise knowledge, a tool advantage, schema,
asset, or fragile order. Keep the relevant advantage, required inputs, minimum
order-sensitive workflow, exact evidence, boundary, and stop. Do not invent
cognitive ceremony around deterministic work.

A workflow is justified when order itself is correctness: an irreversible
operation, safety boundary, transactional sequence, protocol, or fragile tool
handoff. Keep only the invariant sequence. If compliance must not depend on
reasoning, use deterministic enforcement rather than prose.

## Discovery Contract

A model-invoked description must preserve one routing function:
**Condition × Stake**.

- **Condition** is an observable anchor Claude can recognize now: a user
  phrase, action, artifact, file, or path. An abstract topic is weaker than an
  observable moment.
- **Stake** is the plausible failure or lost advantage that makes opening the
  body worthwhile.
- A capability catalog does not replace a trigger.
- The description remains a pointer to the body, not its digest.

Cut test: if removing a phrase does not change which skill should activate
against live neighbors, it is a no-op or body material.

## Candidate Canvas and Invocation

The complete installed set of model-invoked descriptions is the authoring-time
candidate canvas. Runtime co-presence is not guaranteed, so a broad or adjacent
trigger also needs checking against the prompt surface actually visible to the
model.

- A shared trigger phrase is a collision/ownership question, not literal
  deduplication.
- Resolve collisions by narrowing the positive triggers of the owners. Keep
  near-miss cases in evaluation, not as neighbor pointers in runtime text.
- `disable-model-invocation: true` suits a deliberate/manual skill that should
  not compete in model discovery.
- Verify the live Claude skill root and resolved model rather than inferring
  them from an alias, old path, or another platform.

## Evidence by Claim

Evidence must discriminate the exact property being claimed:

- admission claim—a recurring moment, useful Delta, and observable gap;
- routing claim—representative use/skip/near-miss cases and live collisions;
- structure claim—a platform validator and reachable bundled resources;
- behavior claim—an observable assertion on a realistic task;
- cognitive-transfer claim—a changed representation, decision, probe,
  escalation pattern, or response to feedback on an unshown case;
- relative-improvement claim—a baseline or previous version;
- distribution claim—source/installed projection sync.

A global, frequent, broad, risky, collision-prone, or already-regressed surface
requires stronger evidence for the risk it raises. This does not become a fixed
number of prompts, a mandatory benchmark, or a universal verification ritual.

Prompt visibility proves only that selection is possible. A matcher or
structural validation does not prove useful output.

Proxy, objective, phase, anchor, thought-demonstration, and form-congruence
claims need discriminating observations or ablations matched to the mechanism:
the proxy changes action, the criterion survives shortcut pressure, phases stop
the named interference, a wrong anchor can reopen, and the latent genre carries
the intended decision beyond literal rule coverage.

## Model Baseline

- Give Opus 5 and Fable 5 a lightweight skill with progressive disclosure.
- Generic self-review, an automatic verifier, and fan-out are not part of the
  portable baseline. Add objective validation and an independent verifier
  according to the task/risk contract.
- Model, effort, thinking, long-run, and fallback rules belong to the current
  model owner/runtime. Do not copy them into the skill.
- Older Claude 4.x skills and prompts are historical migration evidence, not an
  active baseline or fallback.

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

## Source Discipline

- An Anthropic-endorsed claim requires a current official source:
  `platform.claude.com/docs`, `code.claude.com/docs`,
  `anthropic.com/engineering`, or `github.com/anthropics/skills`.
- Label local engineering as local engineering, not an Anthropic
  recommendation.
- Do not invent metrics, limits, or runtime availability. Recheck a drift-prone
  fact in live docs/runtime.

Current anchors:

- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5>
- <https://code.claude.com/docs/en/slash-commands>
