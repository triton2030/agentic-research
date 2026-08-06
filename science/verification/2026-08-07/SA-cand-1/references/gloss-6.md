# Glossary 6

## Language

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
