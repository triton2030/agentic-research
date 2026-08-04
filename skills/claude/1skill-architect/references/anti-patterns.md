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
- **Encyclopedic body**: `SKILL.md` teaches domain theory that changes no tell,
  representation, decision, tool choice, evidence, or stop. A necessity proof
  and central thought demonstration are causal core, not tutorial noise.
- **Procedure without mechanism**: a judgment/design/quality skill prescribes
  stages whose completion does not change representation or decision. An
  ordered cognitive transformation is valid when removing the order reproduces
  the observed failure.
- **Cargo-cult creation**: adding a new skill/agent/hook because a similar one
  exists, without proof and reuse-first gates.
- **Runtime by analogy**: porting another runtime's agent, hook, or skill into
  Claude without adapting Claude invocation, tools, metadata, and validation.
- **Prompt-only guardrail for hard risk**: using prose where enforcement,
  permission, hook, validator, or checkpoint is the right layer.

## Cognitive Failures

- **Unproven necessity**: correct rules are disconnected from the natural
  default and causal failure, so Claude treats them as optional ceremony.
- **Straw-agent diagnosis**: the baseline depicts obvious incompetence instead
  of the locally reasonable prior that makes a capable model fail.
- **Naked imperative**: the body says "always X" without showing why the
  default is attractive, what harm it causes, and how X breaks the chain.
- **Introspection imperative**: "notice", "realize", or "do not forget" is not
  translated into a check over observable text, context, or artifacts.
- **Anatomy as proof**: a vivid claim that the model "has no organ" replaces a
  behavioral tell, causal trace, and transfer evidence.
- **Unchanged economics**: the skill forbids a shortcut while still rewarding
  the same fast, fluent local output that makes it attractive.
- **Phase leak**: exploration, compression, and commitment interfere because
  their boundary is presentational rather than causal.
- **Anchor lock-in**: an early conclusion is externalized without provenance,
  veto, or reopen signal and becomes a more durable error.
- **Checklist theatre**: every field is filled while representation and final
  decision remain those of the no-skill baseline.
- **Output-example trap**: examples teach wording or field order rather than
  default -> tell -> operation -> changed decision.
- **Thought theatre**: fluent reasoning or self-reported confidence is accepted
  as proof of faithful cognition or transfer.
- **Mechanism without controller**: the primary act succeeds once but leaves no
  reusable frame, rule, map, or proof obligation.
- **Form mismatch**: explicit rules ask for one decision structure while the
  skill's own organization demonstrates another latent genre.
- **Explanation bloat**: rationale repeats importance without changing trigger,
  operator, decision, evidence, or feedback.

## Evaluation Failures

- **Matcher-only proof**: showing that a skill can be found, but not that it
  improves the output.
- **Compliance-only proof**: showing required sections but no changed decision,
  probe, or later trajectory on an unshown case.
- **No mechanism ablation**: a central proxy, criterion, phase, anchor, or
  example is assumed causal without testing its removal when the claim matters.
- **No near-miss negatives**: testing obvious should-not prompts but not the
  adjacent tasks that actually cause collision.
- **No sunset signal**: a rule has no observable condition under which it should
  be revisited or removed.

## Language And Priority

- **English voice in Russian truth layer**: mixing language without a reason can
  blur priority and weaken the mental model.
- **Abstract category trigger**: relying on the model to notice "this is design"
  instead of anchoring on visible action, path, artifact, or user phrase.
