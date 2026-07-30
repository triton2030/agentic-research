---
name: 1skill-architect
description: >
  Use when designing or substantially revising a Claude skill/control surface
  before implementation: decide owner, trigger, collisions, and
  outcome-vs-workflow shape. Create/update/validate → `skill-creator`.
---

# Skill Architect

## Result

The right expertise returns at the moment of action through one correct surface,
and its contract changes observable agent behavior without unnecessary process
scaffolding. **Moment-fit**—the surface is found and activated at the right
moment—is the root virtue: strong content that never loads does not exist for
the agent.

Take exact meanings of **bold terms** from [`GLOSSARY.md`](GLOSSARY.md) only
when a term is ambiguous or the vocabulary itself is being changed.

## Surface and Admission

Determine the surface type and owner before writing the wording:

- a `skill` returns recurring professional judgment or a tool workflow;
- an `agent` isolates an independent role or context stream;
- `hook-as-code` deterministically observes or constrains a runtime event;
- `instruction-text` sets a durable default rule;
- "no new surface" is the correct result when the nearest owner is sufficient.

A new or substantially rewritten surface is justified only when there is a
recurring moment, a distinct trigger, an observable failure pattern, and a
**Delta** the agent cannot reliably infer from the task, current context, and
nearest owner. Generic competence earns no prompt budget.

## Delta and Causal Benefit

**Delta** is knowledge, a distinction, or a tool advantage the agent does not
know or cannot reliably infer from the request, current context, and nearest
owner. Make it explicit in the body: do not merely say "use X"; name the likely
default or failure it prevents and how it helps achieve the user's outcome
faster, more easily, or more reliably.

The rationale is neither praise nor enforcement. It is a decision standard that
transfers the rule beyond its literal wording:

- a cognitive or judgment skill explains the model default or tell and how the
  correction changes criteria, a decision, or evidence;
- a tool skill explains the tool's relevant advantage over the likely default
  and when it changes the route or result;
- an invariant or safety rule names the protected risk or side effect.

Do not praise a tool abstractly or restate the user's goal. If you cannot name
the unknown Delta and its action-changing benefit, remove the line or surface.

## Body Shape

An **outcome/decision contract is the default** for judgment, design, and
quality skills. It holds the desired state, leading decision standard, material
boundaries, falsifiable evidence, conditional routes, and stop/handoff. The
model chooses its own path.

A **workflow contract is the exception** for fragile, irreversible,
safety-critical, or tool-bound work where order itself is part of correctness.
Keep only the sequence whose absence reproduces a concrete failure.

A **micro-router** means a compact contract and conditional disclosure, not a
mandatory reasoning algorithm. Do not turn `SKILL.md` into a textbook or route
the agent to read every reference.

## Discovery Contract

For a model-invoked Claude skill, `description` participates in discovery
before the body loads:

- the opening names an observable condition and the important Delta;
- the trigger describes a moment, not a capability catalog;
- each adjacent near-miss belongs to one owner;
- the description remains a pointer to the body, not its summary.

The complete live candidate canvas and the prompt surface actually visible to
the model are stronger evidence than an isolated wording. A shared trigger
phrase is a collision/ownership signal, not a literal-deduplication task.
Describe neighbors with bare pointers.

## Evidence Gate

Evidence must be capable of refuting the material change claim. A global,
broad, frequent, risky, collision-prone, or already-regressed surface raises
the required discriminating strength without creating a fixed test package.
A relative-improvement claim needs a baseline, a routing claim needs near-miss
cases, a distribution claim needs projection sync for real copies, and a
behavior claim needs an observable output assertion. Structural validity and
prompt visibility do not prove useful behavior.

For Opus 5 and Fable 5, remove obsolete scaffolding, repetition, and generic
brevity rules first. Restore a rigid workflow only for an order-sensitive
failure; model, effort, and long-run rules remain with model and platform
owners, not in the portable skill core.

## Failure Modes — Brooks Lens

Quick self-check (full catalog:
[`references/anti-patterns.md`](references/anti-patterns.md)):

- **Central model violation**—`description` lists capabilities instead of the
  trigger surface.
- **Shallow abstraction**—`description` retells the body and saves no
  implementation reading.
- **Procedure by default**—a judgment skill imposes stages without an
  order-sensitive failure mode.
- **Configuration explosion**—several surfaces share one moment without an
  owner.
- **Cargo-cult creation**—a new surface is created "by analogy" without a
  proof/reuse gate.
- **Naked imperative**—the body requires X without explaining the unknown
  Delta, prevented failure, and benefit to the user's outcome.
- **Description-in-vacuum**—one `description` is edited without auditing the
  complete live candidate set and visible prompt surface.

**Stop rule:** if you cannot name the trigger surface in one sentence, that is
a finding; do not keep adding to `description`.

## Routes

- [`GLOSSARY.md`](GLOSSARY.md)—only when a term is ambiguous or vocabulary is
  changing.
- [`references/claude-skill-authoring.md`](references/claude-skill-authoring.md)
  —when creating or substantially revising a Claude skill or `description`.
- [`references/local-skill-contract.md`](references/local-skill-contract.md)
  —when the result includes "create a local skill" or "rewrite this skill."
- [`references/anti-patterns.md`](references/anti-patterns.md)—for a broad
  audit or when a surface is expanding into a system.
- [`references/deep-audit.md`](references/deep-audit.md)—only for a deep audit
  of the skill landscape, runtime, or control surface: eight steps, lenses, and
  output shape.

## Boundaries and Handoff

- `skill-creator` owns creation/scaffolding, packaging, structural validation,
  forward testing, measured benchmarks, and prompt evals; its tool-specific
  steps do not become the mandatory shape of a skill body.
- `1skill-architect` owns design-time surface, trigger, body shape,
  candidate-canvas/collision, owner, and evidence-gate decisions before
  implementation.
- Task contract or current path → `1planning`.
- Prose, folder placement, or instruction wording → `1instruction-layer`.
- Runtime settings, permissions, hooks, or CLI wiring → the live settings/hook
  pass.
- Independent, context-free structural critique → `1fresh-eyes` when the
  change is load-bearing.
