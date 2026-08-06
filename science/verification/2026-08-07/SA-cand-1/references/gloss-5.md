# Glossary 5

## Language

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
