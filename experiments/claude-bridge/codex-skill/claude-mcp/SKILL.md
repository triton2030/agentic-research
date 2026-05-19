---
name: claude-mcp
description: Use when Codex should delegate to Claude Code as an independent reviewer/advisor for long chats, large project work, important decisions, second opinions, code/opinion checks, web research, or controlled Claude Bridge MCP runs with run/peek/wait/kill controls, profiles, logs, observation, context access, or skill-read evidence; skip ordinary inline answers and one-off raw `claude` commands that do not need bridge control.
---

# Claude MCP

Use the Claude Bridge MCP/server when Claude should act as a controlled external
agent with profiles, logs, observation, stop control, context access, or
skill-read evidence. Relay Claude's actual `chat_relay.text` when the user asks
for Claude's answer.

Default to **Independent Reviewer Mode** for long chats, large project work, or
important decisions: Claude checks Codex's current claim against real project
sources as a second strong advisor, not as a vague "ask Claude" side chat.

## Active Contract

- **Entry:** controlled Claude Code peer work: independent review, advice,
  audit, research, or Codex claim-checking, not ordinary inline answering.
- **Boundary:** use bridge controls for work that needs profiles, observation,
  logs, context access, relay, or stop control; raw `claude` is not a substitute.
- **Handoff:** return to Codex after Claude's relay/report, warnings, and
  evidence are available, or after the exact missing layer is named.
- **Stop:** done only when Claude's answer/evidence is relayed and the managed
  run/process tail is terminal or honestly unknown.

## Default Path

1. Before starting, state the distinct Claude role: what independent judgment,
   audit, research, or Codex claim-check Claude adds. If there is no distinct
   role, answer inline instead.
2. Use `claude_doctor` when setup, flags, auth, or current capability are
   uncertain.
3. Use `claude_profiles` before choosing a non-default profile.
4. Start with `claude_run`; observe long or risky work with `claude_observe`
   or `claude_peek`, and finish with `claude_wait` or `claude_result`.
   For hour-scale or human-observable work, pass `useTmux: true` so Claude runs
   in a real terminal session with logs and `tmux_capture`.
5. Use `claude_kill` when a run loops, goes wrong, or the user asks to stop it.
6. After `wait`, `result`, or `kill`, check the run is not still
   `running`/`running_orphaned` before closing the conversation.
7. Give Claude a context packet, not a raw long-chat dump: role, lens, task,
   user goal/current state, Codex claim to check, project sources, relevant
   criteria, targets, open questions/assumptions, boundaries, evidence
   requirements, output shape, and stop condition. Lens, task, goal, and claim
   must come from the user request or explicit project sources; do not invent
   them.
8. Use `cwd`/`addDir` when file access matters; do not ask Claude to judge only
   a Codex summary when the evidence is in files, logs, screenshots, or URLs.
   For tighter per-call control, use first-class fields such as
   `permissionMode`, `allowedTools`, `disallowedTools`, `jsonSchema`,
   `agent`/`agents`, `pluginUrl`, `file`, `brief`, and `inputFormat` instead
   of hiding important behavior in `extraArgs`.
9. Treat Claude's findings as external evidence, not automatic task scope. If a
   finding describes a real current problem but strategy has not decided action,
   Codex may stage it in `_ops/findings/**` after local review instead of
   promoting it directly to `_ops/plans/**` or `_ops/criteria/*.md`.

## Independent Reviewer Mode

Use this as the default mode when the user wants Claude as a project advisor
during a long chat, major decision, large implementation, or close review.

Build a compact context packet from durable sources plus the current working
state:

- **Role/lens/task:** the specific kind of second opinion Claude should provide
  and the exact outcome it should produce.
- **Goal/current state:** what the user is trying to achieve and where Codex is
  now.
- **Codex claim:** the plan, diff, conclusion, or risk assessment to check.
- **Sources:** `cwd`/`addDir`, key files, diffs, logs, URLs, screenshots, or
  docs Claude should inspect directly.
- **Criteria:** relevant instructions, `_ops/criteria/*.md`, task files, or
  acceptance rules.
- **Unknowns:** assumptions, unresolved questions, and what Claude must not
  invent.
- **Boundaries:** read-only by default; ask for findings, patch suggestions, or
  instructions unless the user explicitly chose Claude-side edits.
- **Evidence:** what files, logs, tool calls, checks, or citations must support
  the answer.
- **Output:** findings first, evidence per finding, open questions, recommended
  next move, and stop after the report.

For non-trivial Opus runs, format that packet with XML tags so instructions,
evidence, and variable context do not blur:

```xml
<role>Read-only external reviewer.</role>
<lens>The specific judgment Claude should provide.</lens>
<task>The exact outcome Claude should produce.</task>
<goal>User goal and current project state.</goal>
<claim>Codex's plan, diff, conclusion, or risk assessment to check.</claim>
<sources>Exact files, diffs, logs, URLs, screenshots, or cwd/addDir roots.</sources>
<criteria>Relevant instructions, criteria files, task contract, or acceptance rules.</criteria>
<unknowns>Assumptions and facts Claude must treat as unknown if not evidenced.</unknowns>
<boundaries>Allowed moves, read/write policy, tools, and must-not rules.</boundaries>
<evidence>For each finding, cite file/log/tool evidence or say what evidence is missing.</evidence>
<output>Findings first with evidence, open questions, recommended next move, then stop.</output>
```

Do not pass the whole chat history by default. Summarize only the current state
that changes judgment, then anchor Claude in the same owner files and evidence
Codex used. For large context, put source material before the ask and require
evidence before conclusions. This makes Claude strong without importing stale
conversation noise.

## Evidence

Report profile, cwd/addDir, context packet sources, run_id/log_dir, status,
warnings, whether `chat_relay.truncated` was true, whether the answer was
recovered from bridge logs, process-tail status, activity trace, and
skill/context-read evidence when that matters. `activity` is observable
tool/file/log/tmux progress, not private chain-of-thought. A
`node .../experiments/claude-bridge/src/server.js` process held by Codex
app-server is the MCP transport, not a Claude model run; do not treat it as a
paid tail.

## Stop Rule

If bridge MCP tools are unavailable and the controlled CLI fallback also fails,
stop with the exact missing layer: registration, Node dependencies, Claude CLI,
auth, unsupported flag, or missing evidence. Do not silently fall back to an
uncontrolled raw `claude` command for work that needs observation or proof.

## References

- Read [references/opus-4-7-prompting.md](references/opus-4-7-prompting.md)
  for complex briefs, profiles, or model/prompt-control changes.
- Read [references/managed-runs-and-relay.md](references/managed-runs-and-relay.md)
  for role-fit, audit briefs, `run/peek/wait/result/kill`, relay, timeout,
  logs, or process-tail work.
- Read [references/mcp-failure-handling.md](references/mcp-failure-handling.md)
  when tools, bridge/backend/auth/config, direct recovery, or relay text fail.
