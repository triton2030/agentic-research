# Glossary - Skill Architecture

Domain model for making a control surface found and activated at its moment.
Each term below is a lever on **Moment-fit**. This glossary owns architecture
language for `1skill-architect`; general skill-writing discipline belongs to
the official Claude `skill-creator` and current Claude skill authoring rules.
Read it only when a term is ambiguous or the vocabulary itself is being
changed.

## Contents

- Language
- Failure Modes

## Language

### Moment-fit

How well a surface activates at the right moment of work on the right
**Surface**. The root virtue: a skill with correct content but a missed trigger
does not exist for the agent.

_Avoid_: topic, usefulness, about-X, capabilities

### Surface

The control surface where a pattern lives: skill, agent, hook-as-code, or
instruction-text. Each has a different runtime, owner, validation path, and
side-effect profile. Pick the surface before improving wording.

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

The machine-facing contract that tells Claude when to open a model-invoked
skill. It lives in frontmatter `description`; `disable-model-invocation: true`
turns off model discovery. A weak discovery contract makes a strong body
invisible.

_Avoid_: summary, annotation, frontmatter

### Hot Zone

The opening clause or sentence of a model-invoked `description`. Put the main
moment and trigger words here because discovery metadata can be truncated.
Treat 120-200 characters as a local authoring heuristic, not a platform
guarantee.

_Avoid_: intro, preface

### Observable Anchor

The condition side of a trigger: a file path, artifact type, action, or user
phrase the model can recognize immediately. Prefer path/file/action over
abstract categories that require self-classification.

_Avoid_: topic, relevance, category

### Delta-in-Trigger

The non-obvious stake visible in the trigger itself. The model decides whether
to open a skill before reading the body; if the description says only the
obvious, the important body may never load.

_Avoid_: rationale, body summary, explanation

### Condition x Delta

The discovery test for a model-invoked description. It should fire only when the
observable condition is present and the delta matters. Condition without delta
is generic; delta without condition is vague.

_Avoid_: keyword bundle, generic trigger

### Description Budget

The discipline of making `description` a pointer to the body, not a digest of
the body. Preserve the routing function that matters against live neighbors;
move identity, rationale, examples, and proof into the body or references.

_Avoid_: 1024 as target, body summary

### Candidate Canvas

The full live set of model-invoked descriptions audited at authoring-time.
Runtime visibility can differ from that set, so the candidate canvas exposes
ownership and collision problems without pretending that full co-presence is
guaranteed.

_Avoid_: runtime guarantee, description in isolation

### Canvas Audit

Reading the candidate canvas as one document, then checking the actual visible
prompt surface for broad or adjacent triggers. It cuts repeated characterization,
no-op skip routes, and meta scaffolding. It does not cut shared trigger phrases
blindly; they are evidence for ownership/collision work.

_Avoid_: n-gram dedupe, isolated description review

### Micro-router

The ideal shape of `SKILL.md`: a short router with root virtue, boundaries,
decision standard, conditional reference routes, validation, and stop
condition. It is not a tutorial or mandatory reasoning algorithm.

_Avoid_: tutorial, full manual, exhaustive process

### Collision

Competition between neighboring model-invoked skills for the same trigger
surface. A description can look good in isolation and still steal or lose a
moment in the live skill set.

_Avoid_: overlap, duplicate wording

### Proof Gate

The admission test for a new or substantially rewritten surface: repeated work,
distinct trigger, real failure pattern, and a reason existing instructions,
acceptance criteria, guardrails, or scripts do not cover it.

_Avoid_: justification, "would be useful"

### Reuse-first Gate

The check that existing surfaces were inspected before adding another one. It
must name the closest existing owner and the concrete gap.

_Avoid_: duplicate check, search for similar names

### Evidence Gate

The claim-matched proof bar for a new or changed surface. Routing, behavior,
relative-improvement, structure and distribution claims need different
evidence; risk raises discriminating strength without creating a fixed package.

_Avoid_: minimum/strict ritual, matcher-only proof

### Design-time

This skill's phase: choosing surface, owner, trigger, body shape, reference
routes, validation, and collision/canvas strategy before measured benchmark
work.

_Avoid_: benchmark, optimization loop

### Measurement-time

The official Claude `skill-creator` phase: validation scripts, forward testing,
measured benchmarks, packaging mechanics, and iteration from observed runs.

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
