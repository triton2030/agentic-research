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
- **Procedure without mechanism**: a judgment/design/quality skill prescribes
  stages whose completion does not change the model's representation or
  decision, narrowing judgment and rewarding checklist compliance. An ordered
  cognitive transformation is valid when removing the order reproduces the
  observed failure.
- **Cargo-cult creation**: adding a new skill/agent/hook because a similar one
  exists, without proof and reuse-first gates.
- **Oversized first intervention**: a full cognitive mechanism is designed
  before testing whether one rule, question, check, or nearest-owner delta
  already closes the failure trace.
- **Runtime by analogy**: porting another runtime's agent, hook, or skill
  without adapting invocation, tools, metadata, and validation to the target.
- **Prompt-only guardrail for hard risk**: using prose where enforcement,
  permission, hook, validator, or checkpoint is the right layer.

## Cognitive Failures

- **Unproven necessity**: correct rules are disconnected from the natural
  default and causal chain of failure, so the agent treats them as optional
  ceremony under task pressure.
- **Straw-agent diagnosis**: the baseline depicts obvious incompetence instead
  of the locally reasonable prior that makes a capable model fail.
- **Naked imperative**: the body says "always X" without explaining why the
  default is attractive, what harm it causes here, and how X breaks the chain.
- **Introspection imperative**: "notice", "realize", or "do not forget" is not
  translated into a check over observable text, context, or artifacts.
- **Distant critical rule**: a concrete check that must survive concurrent load
  appears only in early rationale, not at the command, template, or phase
  boundary where it constrains action.
- **Anatomy as proof**: a vivid claim that the model "has no organ" or is
  incapable replaces a behavioral tell, causal trace, and transfer evidence.
- **Unchanged economics**: the skill forbids a shortcut while still rewarding
  the same fast, fluent local output that makes the shortcut attractive.
- **Phase leak**: exploration, compression, and commitment interfere because
  their boundary exists only as prose or presentational stages.
- **Anchor lock-in**: an early conclusion is externalized without provenance,
  veto, or reopen signal, or a stale anchor is obeyed without rereading and
  revision, so it becomes a more durable error.
- **Checklist theatre**: every field is filled while the representation and
  final decision remain those of the no-skill baseline.
- **Output-example trap**: examples teach wording, style, or field order but do
  not demonstrate default -> tell -> operation -> changed decision.
- **Demonstration overclaim**: transfer of an operator, style, or decision
  structure is reported as improved task accuracy without matching evidence.
- **False contrast**: the negative example is cartoonishly bad, so it does not
  locate the real boundary between two plausible moves.
- **Thought theatre**: fluent reasoning text or self-reported confidence is
  accepted as proof of faithful cognition or transfer.
- **Mechanism without controller**: the primary act succeeds once but leaves no
  reusable principle, frame, map, or proof obligation for later decisions.
- **Controller as decoration**: the agent repeats the full procedure or asks the
  owner about cases the controller already resolves.
- **Cargo-cult cognition**: scenes, acts, frames, and thought examples are copied
  from a strong skill without a local failure trace or causal benefit.
- **Form mismatch**: explicit rules ask for one decision structure while the
  skill's own organization and examples demonstrate another latent genre.
- **Explanation bloat**: rationale repeats importance without changing trigger,
  operator, decision, evidence, or feedback.

## Evaluation Failures

- **Matcher-only proof**: showing that a skill can be found, but not that it
  improves the output.
- **Compliance-only proof**: showing that required sections appear, but not that
  an unshown decision, probe, or later trajectory changed.
- **Leaked demonstration**: an eval succeeds only because the expected answer
  or diagnosis was embedded in the thought example.
- **No mechanism ablation**: a central explanation or example is assumed to
  cause the effect without testing whether behavior survives its removal or
  replacement when the claim is material.
- **No near-miss negatives**: testing obvious should-not prompts but not the
  adjacent tasks that actually cause collision.
- **Elastic defense**: a failed run is rescued by a post-hoc explanation when
  no bypass prediction and revision criterion were recorded before it.
- **No sunset signal**: a rule has no observable condition under which it should
  be revisited or removed.
- **Undated model deficit**: a model-dependent limitation has no resolved model,
  observation date, or target-model change trigger for revalidation.

## Language And Priority

- **English voice in Russian truth layer**: mixing language without a reason can
  blur priority and weaken the mental model.
- **Abstract category trigger**: relying on the model to notice "this is design"
  instead of anchoring on visible action, path, artifact, or user phrase.
