# Current Claude Model Routing

Use this reference for model choice and model-specific prompting. Treat the
official docs and live CLI as volatile owners; do not pin copied version names
into the bridge default.

Official sources:

- https://platform.claude.com/docs/en/about-claude/models/choosing-a-model
- https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
- https://code.claude.com/docs/en/cli-usage
- https://code.claude.com/docs/en/model-config

## Aliases And Evidence

- `opus` is the bridge's normal high-capability advisor/worker alias.
- `fable` is reserved for the hardest long-horizon advisor tasks.
- The bridge records the requested alias as `model` and the stream-reported
  primary identities as `resolved_model_history`. `resolved_model` is the last
  one. A missing identity is unknown, not proof that an alias selected a release.
- Fable can automatically continue on Opus after a safety-classifier fallback.
  A history change is routing evidence; attribute the answer to the final model.
- Check `claude_doctor` when aliases or controls may have changed.

## Fable

Fable is useful when the problem needs the strongest widely available model,
long autonomous reasoning, difficult multi-system synthesis, or an unusually
consequential second opinion. It is not the routine code-review default.

Use `fable-advisor` at `xhigh` effort. Give it:

- the complete problem and durable sources;
- explicit authority and safety boundaries;
- success criteria and a stop condition;
- permission to keep a long-lived line of inquiry coherent;
- a request to cite evidence and expose uncertainty.

Fable can refuse tasks that another Claude model accepts. Preserve the refusal.
If the task remains valid, start a fresh `advisor` thread on Opus and state that
this is a fallback, not a continuation or confirmation.

## Opus

Opus is the default for complex coding, architecture, debugging, implementation,
and ongoing project advice. Use `xhigh` effort for normal coding and agentic
work. Treat `max` as a measured exception because it can add diminishing returns
and overthinking. Prefer a short structured brief over a long ritual:

- say the desired outcome, evidence, boundaries, and stop condition;
- put large source context before the final ask;
- tell Claude when tools and direct source inspection are required;
- ask for a general solution rather than a test-only patch;
- keep independent opinions in fresh threads.

## Multiple Advisors

Parallelism belongs at the bridge-thread level when Codex needs independent
opinions. Start separate named Opus/Fable conversations, keep their sources and
claims comparable, and synthesize disagreements in Codex. Claude-internal
subagents may help one Claude solve its own task, but they do not create
independent resumable advisors for Codex.
