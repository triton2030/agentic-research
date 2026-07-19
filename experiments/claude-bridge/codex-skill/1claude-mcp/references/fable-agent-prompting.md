# Fable 5 Agent Prompting

Use Fable as a rare super-advisor for the hardest long-horizon, ambiguous, or
multi-system judgments. Keep the bridge profile read-only unless a separate
write task was explicitly authorized.

Official source:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- https://code.claude.com/docs/en/model-config

## Effort And Task Shape

- Anthropic recommends `high` for most Fable work and `xhigh` for the most
  capability-sensitive workloads. `fable-advisor` uses `xhigh` because the
  route itself is reserved for that exceptional class.
- Expect long turns. Use a persistent bridge thread, observable progress, and
  bounded waits instead of assuming one synchronous response.
- Give the intent and reason, not only a command. Fable often finds a better
  route when it understands the underlying outcome.
- Keep instructions strong but compact. Remove legacy micro-scaffolding that
  merely restates capable default behavior.

## Brief Contract

State the outcome, current claim or decision to attack, exact sources, material
constraints, authority boundary, evidence standard, output shape, and stop
condition. Mark unknowns explicitly. For change tasks, distinguish assessment
from permission to edit.

For long runs add two behavioral constraints:

- ground every progress/completion claim in a tool result from this run;
- pause only for destructive action, real scope change, or input only the user
  can supply.

Do not ask Fable to reveal, transcribe, or explain private reasoning. Ask for
findings, evidence, alternatives, uncertainty, and a direct verdict.

## Delegation And Verification

Fable is strong at parallel and long-lived subagents. Tell it when independent
fan-out is valuable; prefer asynchronous delegation while the lead continues.
Give each worker a self-contained deliverable, source boundary, and ownership.
Use a fresh-context verifier for high-cost acceptance rather than relying only
on self-critique.

Do not request delegation for a task the lead can finish directly, for tightly
sequential work, or when agents would edit the same files. Fable's internal
subagents remain one Fable opinion; use separate bridge threads for independent
advisors owned by Codex.

## Continuation And Refusal

Continue the same thread when accumulated context is an asset. Start a fresh
thread for a blind review or a materially different frame. Fable safety
classifiers can automatically rerun a request on Opus and keep the session on
Opus. Inspect `resolved_model_history`; when it changes, attribute the answer to
the final model. If the configured behavior yields a refusal instead, preserve
it and open a fresh Opus thread. Never report an Opus fallback as Fable's view.
