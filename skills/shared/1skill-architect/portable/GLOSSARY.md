# Glossary - Skill Architecture

Domain model for making a control surface change the agent's trajectory at the
moment where its natural default would fail. **Causal grip** is the root design
virtue; **Moment-fit** is the admission condition that makes the intervention
available; **Trajectory evidence** is how the changed path is tested. This
glossary owns architecture language for this package; platform mechanics belong
to the current runtime authoring rules. Read it only when a term is ambiguous
or the vocabulary itself is being changed.

## Contents

- Language
- Failure Modes

## Language

### Moment-fit

How well a surface activates at the right moment of work on the right
**Surface**. A skill with strong causal content but a missed trigger does not
exist for the agent; a skill that triggers perfectly but changes nothing is
only visible ceremony.

_Avoid_: topic, usefulness, about-X, capabilities

### Causal Grip

How well the skill makes its intervention a necessary consequence of a concrete
failure model: natural default, why that default is attractive, trigger-specific
harm, and the mechanism that breaks the chain. Causal grip lets the agent
reconstruct a rule in novel cases instead of complying only when wording is
repeated.

_Avoid_: persuasive tone, importance claim, motivation paragraph

### Delta

The action-changing value a surface adds beyond the task, current context,
nearest owner, and the model's reliable general competence. A Delta may be a
missing cognitive act, non-obvious distinction, correction, failure mode,
domain rule, or tool advantage. If removing a line changes neither a decision
nor its evidence, that line does not earn prompt budget.

_Avoid_: novelty, extra detail, capability list, generic best practice

### Cognitive Shaper

A skill whose missing value is an inference-time change in attention,
representation, alternatives, decision criteria, questioning, verification, or
learning from feedback. The capability usually exists in the model; the skill
makes the right cognitive act occur at the right moment.

_Avoid_: personality prompt, generic "think harder", workflow by default

### Operational Package

A skill whose missing value is precise knowledge, a tool advantage, schema,
asset, or fragile order that the model cannot reproduce reliably from general
competence. It still explains the failure prevented, but does not invent a deep
cognitive theory where a deterministic contract is enough.

_Avoid_: cognitive shaper, documentation bundle, capability catalog

### Natural Default

The locally reasonable behavior the model is likely to choose without the
surface. A useful default is charitable and causal: it explains why a capable
agent fails, rather than describing an obviously incompetent straw man.

_Avoid_: bad behavior, mistake list, hypothetical stupidity

### Tell

An observable signal that the natural default is active: confidence without a
source, one interpretation where several are plausible, proxy success, a local
patch without a discriminating probe, or a slogan where a conflict rule is
needed. A tell makes the intervention self-triggering inside the loaded skill.

_Avoid_: symptom list without a decision consequence

### Cognitive Deficit

The control act that the model's default continuation does not reliably produce
at the trigger moment: a decision pause, source check, branch before commitment,
reframe, compression, veto, or external anchor. It is a behavioral hypothesis,
not a metaphysical claim about model anatomy.

_Avoid_: missing organ, inability claim without a tell, generic weakness

### Proxy Translation

The conversion of unreliable introspection into a check over observable text,
context, or artifacts. "Know whether you know" becomes "name the source for
this confidence"; the proxy makes the missing act executable and testable.

_Avoid_: self-report, confidence request, another abstract reminder

### Necessity Proof

A short causal chain showing why ordinary task context and model competence do
not reliably prevent the failure, and why the proposed mechanism does. It earns
the agent's inference-time commitment; it is not proof that the author likes
the practice.

_Avoid_: rationale, praise, restated user goal, enforcement language

### Cognitive Transformation

The explicit transition from a natural representation or decision policy to a
new one, written as `A -> B` and supported by one to three operators. The
transformation is the reusable mechanism; its visible template is incidental.

_Avoid_: desired personality, generic quality, checklist completion

### Local Objective

The measure of success inside the skill that changes the relative cost of
candidate actions. It makes the desired trajectory locally coherent and the
old shortcut visibly expensive, including on cases not named by a rule.

_Avoid_: quality slogan, universal metric, vanity count

### Phase Separation

A control boundary between modes that interfere when mixed, such as exploration,
compression, and commitment. Use it only when their coupling causes premature
convergence or unfiltered output; it is not a universal workflow template.

_Avoid_: stages for presentational neatness, mandatory process without failure

### Commitment Anchor

A checked principle, frame, or decision externalized so later actions condition
on it instead of drifting locally. A sound anchor has provenance or veto and a
reopen signal; otherwise it hardens an early error.

_Avoid_: first guess promoted to truth, ownerless memory, anchor without sunset

### Thought Demonstration

A concise, observable decision trace that demonstrates the transformation:
default, tell, operation, and changed choice. It teaches a reasoning pattern,
not a claim about private chain-of-thought and not merely the shape of the final
answer.

_Avoid_: output example, hidden-reasoning disclosure, project fact disguised as
example

### Causal Cell

The smallest causally complete authoring unit: an operator, an explanation of
why the natural default bypasses a naked command, and a plausible boundary or
anti-example. Each part changes how the other two are interpreted.

_Avoid_: rule alone, rationale alone, caricatured negative

### Form Congruence

Alignment between the decision structure a skill teaches and the structure its
own text demonstrates. If the reader continues the text's latent genre where
literal rules end, the intended behavior should remain likely.

_Avoid_: visual imitation, copied section names, style consistency alone

### Contrastive Example

A pair or small set in which a plausible but mechanism-free move is separated
from the move that actually changes the decision. Contrast defines the boundary
better than a lone ideal output.

_Avoid_: good/bad style comparison, caricatured negative

### Reusable Controller

The principle, frame, causal model, diagnostic map, decision policy, or proof
obligation produced by the cognitive act and reused on later decisions. If the
agent must repeat the entire ceremony for every local choice, the controller did
not compress the right thing.

_Avoid_: summary, specification copy, filled template

### Trajectory Evidence

Evidence that the skill changes later behavior on an unshown case: a different
representation, decision, escalation pattern, rework rate, probe, or response to
feedback. Immediate format compliance is not trajectory evidence.

_Avoid_: self-report, lint result, prompt visibility, one copied example

### Surface

The control surface where a pattern lives: skill, agent, hook-as-code,
instruction-text, script, or no new surface. Each has a different runtime,
owner, validation path, and side-effect profile. Pick the surface after the
failure mechanism is understood and before improving wording.

_Avoid_: format, wrapper, file type

### Trigger Surface

The set of moments, phrases, states, and artifacts where a surface should
activate. It organizes `description` and body around "when this is needed", not
"what this can do".

_Avoid_: keywords, tags, feature list

### Capability List

A description organized around what a surface can do instead of when it should
be used. This causes undertrigger and overtrigger because the model chooses by
task moment, not by an implementation catalog.

_Avoid_: features, abilities, menu

### Discovery Contract

The machine-facing contract that tells the model when to open a model-invoked
skill. It begins in frontmatter `description`; the current runtime owns any
additional invocation metadata. A weak discovery contract makes a strong body
invisible.

_Avoid_: summary, annotation, frontmatter

### Hot Zone

The opening clause or sentence of an implicit `description`. Put the main
moment and trigger words here because runtime discovery can shorten metadata or
decide before the body is available.

_Avoid_: intro, preface

### Observable Anchor

The condition side of a trigger: a file path, artifact type, action, or user
phrase the model can recognize immediately. Prefer path/file/action over
abstract categories that require self-classification.

_Avoid_: topic, relevance, category

### Stake-in-Trigger

The non-obvious harm or lost advantage visible in the trigger itself. The model
decides whether to open a skill before reading the body; if the description says
only the capability, the causal mechanism may never load.

_Avoid_: full necessity proof, body summary, generic importance

### Condition x Stake

The discovery test for a model-invoked description. It should fire only when the
observable condition is present and the stake matters. Condition without stake
is generic; stake without condition is vague.

_Avoid_: keyword bundle, generic trigger

### Description Budget

The state in which `description` preserves its full routing function while
remaining a pointer to the body, not a digest. Identity, rationale, examples,
and proof remain in the body or references.

_Avoid_: 1024 as target, premature shortening

### Candidate Canvas

The full live set of model-invoked descriptions audited at authoring-time.
Runtime visibility may be budgeted or context-dependent, so descriptions can
be shortened or omitted. The candidate canvas exposes ownership and collision
problems without pretending that full co-presence is guaranteed.

_Avoid_: runtime guarantee, description in isolation

### Canvas Audit

Reading the candidate canvas as one document, then checking the actual visible
prompt surface for broad or adjacent triggers. It cuts repeated characterization,
no-op skip routes, and meta scaffolding. It does not cut shared trigger phrases
blindly; they are evidence for ownership/collision work.

_Avoid_: n-gram dedupe, isolated description review

### Micro-router

The right shape for a frequent operational package or a cognitive skill whose
causal mechanism is already reliably available from context: a short hot path
with conditional disclosure. It is not the universal ideal. Do not remove a
necessity proof or central thought demonstration when that text causes the
claimed cognitive transformation.

_Avoid_: universal body template, tutorial, full manual

### Collision

Competition between neighboring model-invoked skills for the same trigger
surface. A description can look good in isolation and still steal or lose a
moment in the live skill set.

_Avoid_: overlap, duplicate wording

### Proof Gate

The admission test for a new or substantially rewritten surface: repeated work,
distinct trigger, real failure pattern, and a reason existing instructions,
acceptance criteria, guardrails, or scripts do not cover it. For a cognitive
skill it also requires a necessity proof and a falsifiable transfer claim.

_Avoid_: justification, "would be useful"

### Reuse-first Gate

The check that existing surfaces were inspected before adding another one. It
must name the closest existing owner and the concrete gap.

_Avoid_: duplicate check, search for similar names

### Claim-bound Evidence

Evidence selected because it can refute a material admission, routing,
structure, mechanism, transfer, relative-improvement, or distribution claim.
Risk and collision pressure raise the required discriminating strength, but do
not activate a fixed package of checks.

_Avoid_: minimum/strict ritual, matcher-only proof

### Design-time

This skill's phase: diagnosing the natural default, proving necessity,
designing the cognitive or operational mechanism and thought demonstrations,
then choosing surface, owner, trigger, reference routes, validation, and
collision/canvas strategy before measured benchmark work.

_Avoid_: benchmark, optimization loop

### Measurement-time

The platform authoring phase: validation scripts, forward testing, measured
benchmarks, packaging mechanics, and iteration from observed runs.

_Avoid_: design critique

### Two Users

Every durable surface serves a human operator and a fresh AI session. A topology
that only the model can use is brittle; a topology that only the human can
navigate is cosmetic.

_Avoid_: audience, reader

## Failure Modes

### Central Model Violation

The interface is written as capabilities instead of trigger surface. The model
cannot reliably decide when to use the surface because the description answers
"what it does", not "when it matters".

_Avoid_: bad description

### Shallow Abstraction

The discovery contract merely restates the body. It does not save the model
from reading the implementation, so selection remains a guess.

_Avoid_: thin wrapper

### Configuration Explosion

Multiple skills, agents, hooks, or instructions split one trigger surface
without a clear owner. Each task moment becomes a routing lottery.

_Avoid_: too many skills

### Cargo-cult Creation

Adding a new surface because a similar one exists, without proof that this one
catches a distinct failure or moment.

_Avoid_: copying, imitation

### Description-in-Vacuum

Editing one model-invoked description without checking the full live candidate
canvas and, where material, the actual prompt surface. The local description may
improve while global routing gets noisier or more collision-prone.

_Avoid_: local-only trigger polish

### Unproven Necessity

Rules are reasonable but disconnected from the model's natural default and the
causal chain of failure. Under task pressure the model treats them as optional
ceremony or reproduces only their visible format.

_Avoid_: weak rationale

### Checklist Theatre

The agent fills every required field while retaining the same representation
and decision it would have used without the skill. Compliance is mistaken for
cognitive effect.

_Avoid_: incomplete output

### Output-example Trap

Examples demonstrate the final artifact but not the transition that produced
it, so the model learns style, wording, or field order rather than the intended
operator.

_Avoid_: insufficient examples

### Thought Theatre

A plausible textual explanation is accepted as faithful cognition or transfer
without an observable changed decision on a new case.

_Avoid_: concise reasoning summary, legitimate decision trace

### Surface-first Design

The author chooses `skill`, `agent`, hook, or instruction before diagnosing the
missing mechanism. The selected format then distorts the problem and produces a
surface justified by its own existence.

_Avoid_: surface gate
