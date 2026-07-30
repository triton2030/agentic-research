# Claude Skill Authoring

Read this reference when creating or substantially revising a Claude skill,
`description`, invocation policy, runtime transfer, or source-backed claims.

## Desired Result

The skill activates at the right moment and returns the missing professional
contract to Claude. Its body improves the observable outcome without making
Opus 5 or Fable 5 perform an authoring procedure.

The portable core defines the outcome, decision standard, boundaries, evidence,
conditional routes, and stop. Ordered steps appear only when violating the
order reproduces a correctness, safety, or tool failure.

## Core Contract

- `description` is the discovery contract for a model-invoked skill. The main
  use case, trigger words, and adjacent boundaries must survive metadata
  shortening; the body is unavailable before activation.
- `SKILL.md` is a compact contract, not a textbook. Keep the core outcome,
  decision criterion, materially important boundaries, evidence, conditional
  routes, and stop/handoff.
- Include only **Delta** in a skill: non-obvious domain logic, a failure mode,
  a correction, or a professional move the model cannot reliably infer from
  the task, current context, and nearest owner.
- Name authority, required output, and side-effect boundaries only when they
  change the permitted action.
- Do not instruct the agent to read every reference. Give each bundled file an
  action-changing route from `SKILL.md`.
- Keep reference files one level deep; give a long reference a short plain-text
  content map. A body under 500 lines is a ceiling, not a target.
- Scripts are justified by deterministic behavior, external tooling, or a
  recurring fragile operation; examples do not compensate for a weak
  interface.

## Outcome or Workflow

An outcome/decision contract is the default for judgment, design, and quality
work:

- the state that must become true;
- the decision standard that resolves a tradeoff;
- the boundaries that are actually material;
- the evidence that can refute success;
- when a reference, tool, or agent is needed;
- where to stop or hand off.

A workflow contract is justified when order itself is part of correctness: an
irreversible operation, safety boundary, transactional sequence, protocol, or
fragile tool handoff. Keep only the invariant sequence, not a universal
procedure "for reliability."

## Discovery Contract

A model-invoked description must preserve one routing function:
**Condition × Delta**.

- **Condition** is an observable anchor Claude can recognize now: a user
  phrase, action, artifact, file, or path. An abstract topic is weaker than an
  observable moment.
- **Delta** is the non-obvious stake that makes opening the body worthwhile.
- A capability catalog does not replace a trigger.
- A near-miss boundary is needed only where a neighbor genuinely claims the
  same moment.
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
- A skill's own description owns its truth; a neighbor uses a bare pointer
  instead of retelling it.
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
- relative-improvement claim—a baseline or previous version;
- distribution claim—source/installed projection sync.

A global, frequent, broad, risky, collision-prone, or already-regressed surface
requires stronger evidence for the risk it raises. This does not become a fixed
number of prompts, a mandatory benchmark, or a universal verification ritual.

Prompt visibility proves only that selection is possible. A matcher or
structural validation does not prove useful output.

## Model Baseline

- Give Opus 5 and Fable 5 a lightweight skill with progressive disclosure.
- Generic self-review, an automatic verifier, and fan-out are not part of the
  portable baseline. Add objective validation and an independent verifier
  according to the task/risk contract.
- Model, effort, thinking, long-run, and fallback rules belong to the current
  model owner/runtime. Do not copy them into the skill.
- Older Claude 4.x skills and prompts are historical migration evidence, not an
  active baseline or fallback.

## `skill-creator` Handoff

`1skill-architect` chooses the surface, contract shape, routing claim, and
evidence bar. The official Claude `skill-creator` performs scaffolding,
validation, forward testing, measured benchmarks, and packaging.

Its step list is the mechanics of a specific tool, not the mandatory shape of
a skill body or a universal authoring ritual. Do not reproduce the matcher/eval
pipeline in this reference.

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
- <https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md>
