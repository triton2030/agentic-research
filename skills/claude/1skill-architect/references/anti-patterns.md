# Anti-patterns

Use this reference for broad audits or when a design keeps adding surfaces.

## Ordering Failures

- **Failure scan before capability inventory**: diagnosing new mechanisms before
  checking what skills, hooks, agents, instructions, or scripts already exist.
- **Forces as epilogue**: naming future pressure after recommendations instead
  of letting it constrain design.
- **Add-only output**: recommendations that add rules but never delete, merge,
  or retire old ones.
- **One failure -> one prescription**: patching symptoms instead of finding a
  single intervention that removes the class.

## Truth-layer Failures

- **Cold upstream**: owner docs, goals, or instructions are treated as current
  even after user corrections or route changes.
- **No freshness mechanism**: a durable rule depends on memory or discipline but
  has no checkpoint, owner, hook, or validation path.
- **One rule in many owners**: the same policy is copied into skill, instruction
  text, hook comments, and planning docs without a single source of truth.

## Surface Failures

- **Capabilities over triggers**: `description` says what the skill can do, not
  when it should be used.
- **Description-in-vacuum**: one model-invoked `description` is polished without
  auditing the full live candidate set and, where material, the visible prompt
  surface.
- **Tutorial body**: `SKILL.md` teaches the whole domain instead of routing to
  the needed reference.
- **Cargo-cult creation**: adding a new skill/agent/hook because a similar one
  exists, without proof and reuse-first gates.
- **Runtime by analogy**: porting another runtime's agent, hook, or skill into
  Claude without adapting Claude invocation, tools, metadata, and validation.
- **Prompt-only guardrail for hard risk**: using prose where enforcement,
  permission, hook, validator, or checkpoint is the right layer.

## Evaluation Failures

- **Matcher-only proof**: showing that a skill can be found, but not that it
  improves the output.
- **No near-miss negatives**: testing obvious should-not prompts but not the
  adjacent tasks that actually cause collision.
- **No sunset signal**: a rule has no observable condition under which it should
  be revisited or removed.

## Language And Priority

- **English voice in Russian truth layer**: mixing language without a reason can
  blur priority and weaken the mental model.
- **Abstract category trigger**: relying on the model to notice "this is design"
  instead of anchoring on visible action, path, artifact, or user phrase.
