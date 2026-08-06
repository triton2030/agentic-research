# Anti-patterns

Use this reference for broad audits or when a design keeps adding surfaces.

## Contents

- Ordering Failures
- Truth-layer Failures
- Surface Failures
- Cognitive Failures
- Evaluation Failures
- Language And Priority

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
- **Encyclopedic body**: `SKILL.md` teaches domain theory that changes no tell,
  representation, decision, tool choice, evidence, or stop. A necessity proof
  and central thought demonstration are causal core, not tutorial noise.
