---
name: 1skill-architect
description: >-
  Use before creating or substantially revising a Claude skill/control surface:
  correct rules often leave behavior unchanged when Claude treats them as
  ceremony, bypasses them under task pressure, or cannot transfer their purpose
  to a new case. Required when a skill is ignored, followed mechanically,
  overgrown as a checklist, or must be distinguished from an agent, hook,
  instruction, or script. Method: real failure trace → named deficit →
  necessity proof → natural default and tell → observable proxy → only causally
  needed objective/phase/anchor controls → contrastive thought demonstrations →
  owner/trigger/surface → transfer evidence.
---

# Skill Architect

## Why This Skill Exists

Skill authors see the desired behavior and naturally write rules: "check first,"
"consider context," "think systematically." Claude can reproduce that form
while keeping the same representation and decision it would have used without
the skill. Smooth checklist compliance can hide zero cognitive change.

A strong skill must therefore make its own necessity intelligible: show the
natural default, why it is locally reasonable, why it fails at this trigger,
and how the proposed mechanism breaks that causal chain. Then Claude can derive
the rule's purpose in an unshown case instead of merely repeating its wording.

A skill is context, not an executable program. It changes which continuation is
locally coherent. Design the local economics so the intended trajectory is
easier than the old shortcut and the failure becomes observable before it
hardens into output. **Moment-fit** is the admission condition; changed later
trajectory is the root quality measure.

Take exact meanings of **bold terms** from [`GLOSSARY.md`](GLOSSARY.md) only
when a term is ambiguous or the vocabulary itself is being changed.

## Start From Failure, Not a Surface

Take one real or plausibly reproducible trace without the new skill:

- what Claude noticed first;
- what representation it built;
- which default it applied silently and why that move was reasonable;
- where observable harm appeared: wrong decision, rework, risk, weak evidence,
  extra turns, or repeated owner questions;
- what new case should resolve differently after the intervention.

Then name the **cognitive deficit** in one sentence: which control act fails to
appear in time—decision pause, source check, branch before commitment, reframe,
compression, veto, or external anchor. This is a behavioral hypothesis, not a
claim about model anatomy. A vivid "missing organ" metaphor does not replace a
tell, causal chain, and transfer evidence.

## Surface and Admission

After the failure and missing mechanism are understood, determine the surface
type and owner before writing its wording:

- a `skill` returns recurring professional judgment or a tool workflow;
- an `agent` isolates an independent role or context stream;
- `hook-as-code` deterministically observes or constrains a runtime event;
- `instruction-text` sets a durable default rule;
- "no new surface" is the correct result when the nearest owner is sufficient.

A new or substantially rewritten surface is justified only when there is a
recurring moment, a distinct trigger, an observable failure pattern, and a
**Delta** the agent cannot reliably infer from the task, current context, and
nearest owner. Generic competence earns no prompt budget.

## Necessity Proof

Before writing rules, connect:

1. **Natural default:** without the skill Claude is likely to do X.
2. **Attraction:** a prior, local signal, or cheap proxy makes X plausible.
3. **Trigger-specific harm:** here X produces Y.
4. **Blind spot:** ordinary context, competence, or late review does not catch Y
   early enough.
5. **Break mechanism:** operation Z changes the representation, criterion, or
   available tool so the chain no longer passes.
6. **Transfer:** Z resolves new cases without a literal rule for each one.

The rationale is neither praise nor enforcement. A cognitive skill explains
the default, tell, proxy, and changed decision; a tool skill explains its exact
advantage over the likely default; a safety rule names the protected risk. If
the mechanism is inferable from the current request and nearest owner, or does
not change action, remove the line or surface.

## Contract Independence

One skill owns one positive moment and information job. Its body is not a map of
the rest of the system. State when this contract applies, what it changes, what
it must return, and where its own authority stops.

Do not add neighbor menus, "X → another route," handoff catalogs, or sections
explaining what to do when the skill does not apply. Non-applicable cases belong
to ordinary discovery and candidate-canvas evaluation, not to this body. Keep a
negative boundary only when it prevents this skill from overclaiming authority
inside its own trigger; state the limit without prescribing another surface.

Keep an exact external skill handle only when it is indispensable to execution:
the called package supplies a required protocol, command, or artifact whose
identity cannot be expressed as a capability. State that concrete dependency
and its failure mode. A neighboring capability, a suggested review, or a
generic handoff never meets this bar.

## Two Skill Classes

Choose what must change before choosing body shape.

### Cognitive Shaper

Use when Claude has the capability but does not activate it at the trigger, or
when default continuation does not reliably create the required control. The
skill changes attention, representation, alternatives, decision policy,
verification, or learning from conflict. Its product is a reusable controller:
a principle, causal model, frame, diagnostic map, or proof obligation.

### Operational Package

Use when the gap is precise knowledge, a tool advantage, schema, asset, or
fragile sequence. Explain why the ordinary default loses precision, safety, or
reproducibility, then give the smallest sufficient tool/workflow contract.
Strict order is justified only where order itself is correctness. If compliance
must not depend on reasoning quality, use a hook, permission, validator, or
other deterministic layer.

Do not make an operational package perform cognitive theatre or compress a
cognitive shaper into a runbook. A hybrid separates causal/judgment core from
deterministic tool layer explicitly.

## Design the Cognitive Mechanism

Describe a transition, not a desired personality:

```text
natural default
-> observable tell
-> proxy or gate
-> missing cognitive act
-> changed representation
-> decision rule, local objective, or phase boundary
-> reusable controller or checked external anchor
-> feedback when shaping fails
```

Use this as causal vocabulary, not a mandatory output template. Name the
default, tell, deficit, observable proxy, `A -> B` transformation, one to three
operators, local success measure, human/model asymmetry, and feedback only to
the depth needed to explain the failure.

### Five Control Levers

Choose only levers whose absence reproduces the trace:

- **Proxy translation:** convert "know whether you know" into "name the source
  for this confidence" or another check over visible text/context/artifacts.
- **Objective rebasing:** define a measure that resolves new cases and makes the
  old shortcut expensive: autonomous distance, prevented rework, preview/outcome
  agreement, or another claim-bound criterion.
- **Phase separation:** separate exploration, compression, and commitment when
  mixing them causes premature convergence or publishes unfiltered noise. This
  is a control boundary, not a universal staged workflow.
- **Commitment anchor:** externalize a checked frame, principle, or decision so
  later work conditions on it. Require provenance or veto and a reopen signal;
  otherwise the anchor only hardens an early error.
- **Labor inversion:** Claude performs cheap generation and compression; the
  human performs cheap recognition, veto, or correction. Do not ask the owner
  to author what they can more cheaply recognize in a proposed version.

Do not demand private chain-of-thought. Use observable decision traces and
intermediate artifacts—alternatives, sources, causal links, discriminating
probes, conflict rules, and evidence.

## Thought Demonstrations and Form

A final-output example teaches wording and fields. A thought demonstration
teaches the decision transition. The smallest causally complete unit is a
**causal cell**:

- operator: what Claude does differently;
- machine-level rationale: why the natural default bypasses the naked command;
- plausible boundary or anti-example: where the form is satisfied but the
  mechanism is absent.

Use short default, transformation, anti-example, and transfer traces where the
central mechanism needs them. Avoid caricatured negatives and leaked eval
answers.

The whole skill is also a demonstration. Its own decision structure should
embody what it teaches: a compression skill compresses into a controller; an
alternatives skill shows a real fork; a veto skill names its default and veto
point. If Claude continues the text's latent genre beyond literal rule coverage,
the intended behavior should remain likely. This is **form congruence**, not
visual imitation.

## Discovery Contract

For a model-invoked Claude skill, `description` participates in discovery
before the body loads:

- the opening names an observable condition and the important stake: what
  plausible failure or lost advantage makes opening the body worthwhile;
- the trigger describes a moment, not a capability catalog;
- the description remains a pointer to the body, not its summary.

The complete live candidate canvas and the prompt surface actually visible to
the model are stronger evidence than an isolated wording. A shared trigger
phrase is a collision/ownership signal, not a literal-deduplication task.
Resolve near misses in design and evaluation; do not serialize the neighboring
system into the runtime description.

## Result: Skill Frame

Before implementation, return a compact design frame:

- **Scene:** which agent acts differently at what moment, with what observable
  downstream result.
- **Failure/deficit:** baseline trace, natural default, missing control act, and
  harm.
- **Necessity:** causal chain from default to intervention.
- **Type:** cognitive shaper, operational package, or justified hybrid.
- **Mechanism:** tell -> proxy -> transformation -> only causally needed
  objective/phase/anchor operators -> controller -> feedback.
- **Thought demonstrations:** default, transition, anti-example, and transfer in
  the smallest sufficient set.
- **Form congruence:** which decision structure the text itself continues.
- **Surface/owner:** why this layer and where its authority ends.
- **Discovery:** condition, stake, use/near-miss cases, and collision decision.
- **Minimality/dependencies:** obsolete scaffolding removed or merged, and only
  indispensable external dependencies.
- **Evidence:** what can refute routing, mechanism, and transfer claims.
- **Stop/sunset:** when design is sufficient and what reopens it.

## Evidence Gate

Evidence must be capable of refuting the material change claim. A global,
broad, frequent, risky, collision-prone, or already-regressed surface raises
the required discriminating strength without creating a fixed test package.
A relative-improvement claim needs a baseline, a routing claim needs near-miss
cases, a distribution claim needs projection sync for real copies, and a
behavior claim needs an observable output assertion. Structural validity and
prompt visibility do not prove useful behavior.

A cognitive claim needs changed behavior on a realistic unshown case. Check
whether Claude acts on the proxy, keeps the new local objective under shortcut
pressure, prevents the named interference between phases, reopens a wrong
anchor, and continues the intended decision structure beyond literal rule
coverage. Use with/without, previous-version, or ablation of the central proxy,
criterion, phase boundary, anchor, or thought demonstration when the claim is
material.

For Opus 5 and Fable 5, remove obsolete scaffolding, repetition, and generic
brevity rules first. Restore a rigid workflow only for an order-sensitive
failure; model, effort, and long-run rules remain with model and platform
owners, not in the portable skill core.

## Failure Modes

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
- **Naked imperative**—the body requires X without connecting natural default,
  prevented failure, and break mechanism.
- **Introspection imperative**—"notice" or "do not forget" is not translated
  into a check over visible text, context, or artifacts.
- **Unchanged economics**—the skill forbids a shortcut but still rewards the
  same fast, fluent local output.
- **Phase leak**—exploration, compression, and commitment interfere because
  their boundary is presentational rather than causal.
- **Anchor lock-in**—an early conclusion is externalized without provenance,
  veto, or reopen signal.
- **Form mismatch**—explicit rules teach one decision structure while the
  skill's own latent genre demonstrates another.
- **Description-in-vacuum**—one `description` is edited without auditing the
  complete live candidate set and visible prompt surface.
- **Router residue**—the body explains where unrelated cases should go, so a
  local contract becomes coupled to the surrounding skill landscape.

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

## Boundary and Stop

- This surface owns design-time failure/deficit diagnosis, necessity proof,
  cognitive or operational mechanism, thought demonstrations, trigger,
  candidate-canvas/collision, owner, surface, and evidence-gate decisions.
- It does not scaffold, package, distribute, wire, execute measurement, or
  independently critique the chosen surface. Platform authoring mechanics do
  not become the mandatory shape of a skill body.
- Stop when a fresh session can implement the surface without guessing why it
  exists or what cognition it must change, and the evidence can refute those
  claims. If necessity, transfer, or the trigger cannot be stated, return to the
  failure trace instead of expanding the description.
