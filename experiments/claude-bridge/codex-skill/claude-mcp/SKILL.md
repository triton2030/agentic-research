---
name: claude-mcp
description: >
  Use when Codex should run Claude Code as a controlled External Peer
  Review agent for a project/folder/diff: second opinion, code/opinion
  check, bug hunt, architecture or instruction audit, behavior
  comparison with Gemini, web research, or any long observable Claude
  Bridge run with run/peek/wait/kill, logs, full relay, agent-behavior
  evidence, and tail cleanup; skip ordinary inline answers and raw
  `claude` calls that do not need bridge control.
---

# Claude MCP

Use the Claude Bridge MCP/server when Claude should act as a controlled external
peer reviewer with profiles, logs, observation, stop control, context access,
full relay, or skill-read evidence. Relay Claude's actual `chat_relay.text`
when the user asks for Claude's answer; use `chat_relay.full_text_file` when
the visible relay is truncated.

Default to **External Peer Review** for project/folder/diff checks: Claude gets
a compact context packet, inspects the real sources, returns findings with
evidence, and stops. Codex then judges the answer, applies any changes locally,
and reports both the findings and Claude's agent behavior.

Bridge default is full-power: `claude_run` profile `normal` requests the `opus`
alias with max effort, stream-json logs, permission bypass, and no bridge-side
tool allowlist. Use `read-only` only as the explicit exception when planning
mode and `Read,Bash` are the intended limit.

## Active Contract

- **Entry:** controlled External Peer Review: independent review, advice,
  audit, research, bug hunt, or Codex claim-checking, not ordinary inline
  answering.
- **Boundary:** use bridge controls for work that needs profiles, observation,
  logs, context access, relay, or stop control; raw `claude` is not a substitute.
- **Handoff:** return to Codex after Claude's relay/report, warnings,
  `agent_behavior`, and evidence are available, or after the exact missing
  layer is named.
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
   promoting it directly to `_ops/plans/**`.

## External Peer Review

Use this as the main reusable scenario across projects.

Quick user intent: "дай Claude проверить `/path` на баги/архитектуру/инструкции"
means: build a read-only context packet from that project, run Claude with
`cwd`/`addDir` on the real sources, observe progress, then return findings plus
run-quality evidence.

**Brief Claude as a reviewer, not a worker.** Default boundary:

- read files and logs through `cwd`/`addDir`;
- do not edit files, create plan files, run a private closeout, or read global
  skills unless that is the explicit task;
- return findings, patch suggestions, missing evidence, and the recommended
  next move;
- stop after the report.

**Codex closeout after Claude returns:**

- summarize Claude's findings separately from Codex's local judgment;
- name false positives or unverified claims;
- include `agent_behavior`: what was observed, whether the relay was full,
  warnings, and tail status;
- apply or stage changes only after Codex rereads local criteria.

## Independent Reviewer Mode

Use this when the user wants Claude as a project advisor
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
- **Criteria:** relevant instructions, task files, or acceptance rules.
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
warnings, `agent_behavior`, whether `chat_relay.truncated` was true,
`chat_relay.full_text_file` when available, process-tail status, activity trace,
and skill/context-read evidence when that matters. `activity` is observable
tool/file/log/tmux progress, not private chain-of-thought. A
`node .../experiments/claude-bridge/src/server.js` process held by Codex
app-server is the MCP transport, not a Claude model run; do not treat it as a
paid tail.

## Stop Rule

If bridge MCP tools are unavailable or return `Transport closed`, use the
repo-local controlled CLI runner fallback once and report that recovery path as
not a clean MCP call. If that fallback also fails, stop with the exact missing
layer: registration/session exposure, Node dependencies, Claude CLI, auth,
unsupported flag, or missing evidence. Do not silently fall back to an
uncontrolled raw `claude` command for work that needs observation or proof.

## References

- Read [references/opus-4-7-prompting.md](references/opus-4-7-prompting.md)
  for complex briefs, profiles, or model/prompt-control changes.
- Read [references/managed-runs-and-relay.md](references/managed-runs-and-relay.md)
  for role-fit, audit briefs, `run/peek/wait/result/kill`, relay, timeout,
  logs, or process-tail work.
- Read [references/mcp-failure-handling.md](references/mcp-failure-handling.md)
  when tools, bridge/backend/auth/config, direct recovery, or relay text fail.
