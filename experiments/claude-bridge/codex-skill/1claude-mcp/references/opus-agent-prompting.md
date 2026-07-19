# Opus 4.8 Agent Prompting

Use Opus as the normal high-capability advisor and authorized worker for coding,
architecture, debugging, reviews, and retained project specialties.

Official source:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

## Effort

- Use `xhigh` for coding and agentic work. It is the bridge default.
- Use at least `high` for intelligence-sensitive work when latency or plan
  allocation matters more than maximum quality.
- Treat `max` as an evaluated exception: Anthropic reports possible gains but
  also diminishing returns and overthinking. Do not make it a named-profile
  default without task-specific evidence.
- Use `low` only for short, tightly scoped, latency-sensitive work.

The default profile uses `xhigh`. A bounded advisor/worker override may select a
different effort or Fable without changing its permission boundary; state the
reason so concurrent Codex agents do not drift accidentally.

## First-Turn Brief

Opus follows instructions literally. Put the task, intent, current state, exact
sources, constraints, authority, acceptance checks, expected output, and stop
condition in the first turn. This reduces clarification turns and subscription
usage. Say explicitly when it must use tools, read sources, or verify a claim.

Prefer a compact structured brief over a chat transcript. Large documents go
before the final query. Do not ask for work outside the stated outcome and do
not rely on Opus to generalize one instruction to unstated cases.

## Subagent Steering

Opus 4.8 spawns fewer subagents by default. Tell it to delegate when independent
fan-out, multiple source areas, verbose tool output, or fresh verification will
materially help. Tell it to work directly for a single visible change or a task
whose phases share the same context.

For each requested subagent name the deliverable, sources, tool/write boundary,
and return format. Prefer simultaneous delegation for independent work. A
subagent starts with a fresh context, so do not assume it saw the lead's chat or
previous reads.

Use a continued bridge thread for iterative work with one retained specialist.
Use a fresh bridge thread, not an internal subagent, when Codex needs an
independent opinion it can resume and compare directly.
