---
name: 1claude-mcp
description: >-
  Когда нужно независимое ревью, второе мнение или совет от принципиально другой
  модели, либо пользователь прямо просит Claude, Opus или Fable: используй
  managed Claude Bridge. Native Codex fresh eyes → `1fresh-eyes`.
---

# Claude MCP

Use Claude when the distinct value is a genuinely different model-family
perspective, retained Claude context, or Claude-side tools, skills, and memory.
Always use the managed Claude Bridge, never a raw `claude` subprocess. The bridge
owns profile/model controls, subscription auth, process/session state, resumable
threads, logs, observation, stop control, relay, and local footprint evidence.
Codex owns scope, synthesis, user communication, and acceptance; Claude's answer
is evidence, not a verdict.

Default to read-only `advisor` on `opus`. Use `fable-advisor` only for a rare
capability-sensitive, long-horizon judgment. Use `worker` plus exact
`writeFiles` only after edits were authorized. `unrestricted` requires explicit
broad authority.

## Gate And Route

Run `claude_doctor` once per task unless fresh readiness evidence exists. Start
only when `ready_for_live_runs` is true and billing mode is
`subscription_oauth`. Read
[subscription-billing.md](references/subscription-billing.md) before the first
live run or any auth/billing change. The bridge proves the credential route; the
user must still decline optional API credits at the plan limit.

| Need | Route |
| --- | --- |
| One independent review | `claude_run(profile: "advisor")` |
| Retained specialist | `claude_thread_start`, then `claude_thread_send` |
| Several independent opinions | separate named threads, started concurrently |
| Hardest long-horizon judgment | `fable-advisor`, `xhigh`, normally a thread |
| Helpers inside one Claude answer | safe inspectable `agents` definitions |
| Scoped edits | `worker` plus exact `writeFiles` |
| Broad authorized edits/execution | `unrestricted` |
| Prove a skill/source read | `claude_audit_skill` |
| Long visible terminal work | `useTmux: true` |

Use native Codex subagents for ordinary Codex delegation.

## Brief Claude

Pass the current decision state and exact owner sources, not a raw chat dump.
For material work use this compact packet:

```xml
<role>External role and authority.</role>
<task>Exact deliverable and stop condition.</task>
<claim>Plan, diff, conclusion, or risk to challenge.</claim>
<sources>Exact files, logs, URLs, cwd, or addDir roots.</sources>
<boundaries>Read/write/tools authority and must-not actions.</boundaries>
<evidence>Evidence required; separate verified fact from inference.</evidence>
<output>Verdict first; default to a compact decision handoff, with detail only in an evidence appendix.</output>
```

State the intent behind material constraints and facts Claude must not invent.
Ask for findings, evidence, uncertainty, and a direct verdict, never private
reasoning. Put large source context before the final ask. Unless the user needs a
long-form deliverable, keep the decision handoff within about 1200 words; Claude
may place decision-relevant depth after `## Evidence appendix` for selective
relay.

## Models

- `advisor`: moving `opus`, `xhigh`; normal coding, architecture, debugging,
  review, and ongoing specialist work.
- `fable-advisor`: moving `fable`, `xhigh`; exceptional hardest/longest work.
- `advisor` and `worker` may use only bounded `opus`/`fable` and explicit effort
  overrides; their permission boundary never widens. `fable-advisor` is fixed.

Inspect `resolved_model_history`, `resolved_model`, and
`model_switch_observed`, not only the requested alias. Fable can automatically
continue on Opus after a classifier fallback; attribute the answer to the final
model. A missing resolved identity is unknown.

Read [current-model-routing.md](references/current-model-routing.md) before a
policy change, [fable-agent-prompting.md](references/fable-agent-prompting.md)
before a Fable brief, and
[opus-agent-prompting.md](references/opus-agent-prompting.md) before tuning Opus.

## Persistent And Parallel Advisors

Start one named topic per retained specialist. Always pass the current `cwd` on
start/send. A thread is bound to its UUID, profile, model, effort, exact cwd,
Git worktree, and ref. Use a new thread after a branch/worktree or model-policy
change. Per-thread atomic leases prevent different Codex processes from claiming
the same turn; the shared registry lets multiple Codex tasks recover their own
handles after restart or compaction.

A continuation inherits earlier context and framing. Start a fresh thread for a
blind review, disagreement, or different role. Several independent threads may
run concurrently: keep every `thread_id`/`run_id` pair separate, wait for each
live tail, and let Codex synthesize without voting or asking one advisor to
summarize another.

Use `claude_threads` to recover handles and `claude_thread_archive` to hide one
without deleting Claude's session. Read
[managed-runs-and-relay.md](references/managed-runs-and-relay.md) for identity,
lifecycle, evidence, and cleanup.

## Claude Subagents And Teams

Bridge threads, Claude subagents, and agent teams are different control planes.
Use subagents only when one Claude lead should own independent fan-out, noisy
tool work, or fresh verification. Give each a self-contained deliverable,
sources, tool/write boundary, and return format; non-fork subagents do not inherit
the lead's full chat.

Named safe profiles reject opaque `--agent` files, permission/model/effort drift,
write-capable advisor definitions, hooks, and arbitrary MCP additions. They add
the bridge boundary to every subagent, including ambient definitions. For
workers, keep ownership disjoint and inside the same exact `writeFiles` scope.

Agent teams are experimental and disabled by normal profiles. Use them only
after explicit opt-in and a dedicated tested profile when peer messaging and a
shared task list are essential. Read
[claude-agent-orchestration.md](references/claude-agent-orchestration.md) before
using `agents`, nesting, or teams.

## Writes, Skills, And Memory

`worker` requires a Git worktree, exact project-relative `writeFiles`, and clean
targets. It injects the boundary into lead and supplied subagents, observes the
filesystem, and compares the final Git footprint. `passed` proves only the
detected persistent footprint stayed inside the list; it is not an OS sandbox.
The bridge never auto-reverts violations.

Read-only runs also compare the persistent Git-worktree footprint and fail that
evidence check on change. Attribution is unknown when concurrent agents share a
worktree. This cannot prove no temporary write or external MCP mutation, so
inspect warnings and the final diff. Run guarded workers without
tmux; lost observation yields `unknown`, never a safety pass.

Claude's configured skills, plugins, MCP tools, and auto memory remain available
unless a diagnostic profile disables them. Thread continuity and auto memory are
separate. Use `claude_audit_skill` for exact structured Read evidence; self-report
is `unknown`, and read access alone does not prove correct skill application.

## Finish Or Recover

Start one long `claude_wait` per run. If the host yields a continuation/cell
handle, keep waiting on that same host call; do not start another bridge wait.
Use `claude_peek`/`claude_observe` only when progress evidence is useful, always
passing that consumer's previous `next_cursor`. A wait timeout does not stop
Claude.

The terminal wait already returns the compact acceptance packet. Use
`claude_result` only to recover current/final state after restart, compaction, or
a lost wait; it never returns Claude's answer. Use `claude_relay` once for the
bounded final answer and follow its `next_cursor` only when the omitted remainder
is decision-relevant or the user requested the full Claude response. Do not open
`report_file` or `full_text_file` by default; inspect a targeted report field when
warnings, failure, model switching, or write-scope evidence requires it.

Use `claude_kill` only for the saved fingerprinted process group or tmux session;
never broad-kill processes by name. Finish only at a terminal state:
`completed`; legacy `completed_unknown`; `failed`; `killed`; or safely explained
`orphaned`. Treat `completed_unknown` as terminal but never as verified success:
relay is allowed, and closure must preserve the
`legacy_terminal_status_unknown` warning. Report profile, requested and resolved
model history, topic/thread, status, billing, warnings, sources, and write-scope
evidence when relevant.

If MCP tools are absent or stale, use the repo-controlled CLI once and report
the fallback; never use raw Claude. Classify the failed layer before recovery.
Read [mcp-failure-handling.md](references/mcp-failure-handling.md) for the exact
ladder. If both managed surfaces fail, stop with the missing layer and any live
tail.
