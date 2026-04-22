# Agent Design

An agent is not just a prompt. It is a role plus a boundary on action.

## Core elements

- `Role`: one primary professional lens.
- `Audience`: who consumes the result or bears the cost of a bad decision.
- `Success`: what the agent should make easier.
- `Priorities`: what wins when quality, speed, safety, or completeness conflict.
- `Boundaries`: what must be escalated, verified, or kept out of scope.
- `Evidence`: what counts as a real sign of completion.

## Strong defaults

- Prefer narrow roles over one super-agent.
- Separate reasoning freedom from action boundaries.
- Keep high-risk roles read-only or approval-gated by default.
- Evaluate traces and artifacts, not only the final answer.
- Use human checkpoints and explicit uncertainty when evidence is weak.

## Failure signals

- The role sounds impressive but has unclear decision rights.
- The prompt mixes stable identity with the current task.
- Tool power is broad but action boundaries are vague.
- The agent is judged only by final prose, not by what it actually read, ran, or changed.

## Better move

If the problem is risky or repeatable, strengthen runtime controls, approvals, or verification instead of only rewriting the prompt.
