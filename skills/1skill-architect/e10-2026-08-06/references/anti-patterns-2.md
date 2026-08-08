# Anti-patterns 2/4 (продолжение, дословно)

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
