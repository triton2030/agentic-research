---
name: 1claude-mcp
description: >-
  Use when Codex specifically needs Claude's model or Claude Code runtime: call
  Claude as an external advisor or authorized worker, continue or manage
  several Claude conversations, use Fable for an exceptional hard problem, or
  prove Claude read a skill or project source.
---

# Claude MCP

Use the managed Claude Bridge, not a raw `claude` subprocess, when Claude must
act as a controlled external agent. The bridge owns model/profile selection,
persistent conversation handles, logs, observation, stop control, relay, and
read evidence.

Default to a read-only `advisor` on the moving `opus` alias. Choose
`fable-advisor` only for a genuinely exceptional long-horizon judgment. Give
Claude write authority only through `worker` with exact `writeFiles`, or through
the explicitly dangerous `unrestricted` profile after the user authorized that
scope.

Use native Codex subagents for ordinary delegation inside Codex. Use this skill
when the distinct value is Claude's model, Claude's own session continuity, or
Claude-side tools and skills. If the user only asks how the Claude CLI works,
check live help/version/auth and answer inline.

## Contract

- **Entry:** Claude adds a named external role: advisor, independent reviewer,
  persistent specialist, skill auditor, or authorized worker.
- **Owner:** the bridge owns Claude process/session state; Codex owns task scope,
  synthesis, user communication, and acceptance.
- **Handoff:** use Claude's `chat_relay.text` or full-output file, then judge it
  against local evidence. Claude's answer is evidence, not an automatic verdict.
- **Stop:** the run is terminal, or the exact failed layer and live tail are
  reported. Never broad-kill `claude`, `tmux`, or bridge processes by name.

## Readiness Gate

Call `claude_doctor` before the first live run in the current task unless this
task already has fresh readiness evidence. Continue only when
`ready_for_live_runs` is true.

`ok` means both:

1. the installed CLI advertises the bridge's core controls; and
2. `claude auth status` reports an authenticated account.

Optional CLI flags are capability-gated per call. The bridge combines live
`claude --help` with non-spending parser probes through `claude auth status`
because Claude's help is not exhaustive. If neither proves support, the bridge
fails before spending a run. `model` is the requested alias; `resolved_model`
is runtime evidence from Claude's stream when available.

## Choose The Route

| Need | Route |
| --- | --- |
| One independent review | `claude_run(profile: "advisor")` |
| Continue one specialist | `claude_thread_start` then `claude_thread_send` |
| Several independent advisors | start several named threads concurrently |
| Hardest strategic/technical judgment | `fable-advisor`, `xhigh` |
| Scoped file edits | `worker` plus exact `writeFiles` |
| Explicit unrestricted execution | `unrestricted` |
| Prove a Claude skill/source was read | `claude_audit_skill` |
| Long visible terminal work | add `useTmux: true` |

Do not use Claude's internal `agents` option as a substitute for several
independent conversations. Codex starts and owns each bridge thread, can resume
each one separately, and synthesizes disagreements without voting.

## Model Routing

Use aliases so the live Claude installation resolves the current model:

- `advisor`: `opus`, `max` — normal complex work, implementation review,
  architecture, debugging, and ongoing specialist conversations.
- `fable-advisor`: `fable`, `xhigh` — rare highest-stakes or longest-horizon
  tasks where the extra capability justifies cost and latency.

Fable is a super-advisor, not the routine default. Give it a complete problem,
explicit authority boundaries, durable sources, and a stop condition. If Fable
declines a valid task, preserve the refusal as evidence and start a **fresh**
Opus advisor thread; do not silently pretend the fallback is the same opinion.
Use `claude_thread_start` for the usual long-horizon Fable consultation; use a
one-shot `claude_run` only when no continuation will be useful.

Read [references/current-model-routing.md](references/current-model-routing.md)
before changing model policy or composing a Fable brief.

## One-Shot Advisor

Start `claude_run` with `profile: "advisor"`, the real `cwd`/`addDir`, and a
compact context packet. The profile uses plan mode and removes Bash/Edit/Write
tools. It is the safe default for reviews and advice.

For material work, structure the brief:

```xml
<role>The external role Claude owns.</role>
<lens>The specific judgment Claude should provide.</lens>
<task>The exact outcome to produce.</task>
<goal>User goal and current state.</goal>
<claim>Codex's plan, diff, conclusion, or risk assessment to challenge.</claim>
<sources>Exact files, logs, URLs, or cwd/addDir roots to inspect.</sources>
<criteria>Owner instructions and acceptance rules.</criteria>
<unknowns>Facts Claude must not invent.</unknowns>
<boundaries>Read/write authority, tools, and must-not actions.</boundaries>
<evidence>Evidence required for each finding.</evidence>
<output>Answer shape and stop condition.</output>
```

Pass the current decision state, not a raw long-chat dump. Anchor Claude in the
same owner files Codex used. Ask for evidence before conclusions and findings
before prose.

## Persistent Advisors

Use first-class thread tools when future turns should retain Claude's own
conversation context:

1. `claude_thread_start(topic, prompt, profile, cwd)` returns `thread_id` and
   `run_id`.
2. Finish that turn with `claude_wait` or `claude_result`.
3. `claude_thread_send(thread_id, prompt)` resumes the same Claude session.
4. `claude_threads` recovers topics, projects, models, turn counts, last run,
   status, and output after Codex compaction or bridge restart.
5. `claude_thread_archive` hides a handle without deleting Claude's underlying
   session store; unarchive it explicitly before resuming.

Always pass the current `cwd` to MCP start/send calls. A thread is bound to its
exact directory plus Git worktree/ref identity. If another Codex task uses a
different branch/worktree, start a new thread there; the bridge rejects a resume
across that boundary.

A continuation is not an independent second opinion: it inherits the earlier
conversation and framing. Start a fresh thread for blind review or disagreement.
Use clear topics such as `auth-architecture` or `pricing-risk`, not generic
labels such as `advisor-1`.

Several advisors may run concurrently when their questions are independent.
Keep their `thread_id`/`run_id` pairs separate, wait for every live tail, compare
evidence, and synthesize yourself. Do not let one advisor summarize the others.
The registry is shared across Codex agents, while UUID thread IDs and atomic
per-thread leases prevent two processes from claiming one conversation turn.

## Writable Subagent

Use `profile: "worker"` only after the user authorized edits. Supply exact paths
relative to `cwd` through `writeFiles`.

The worker gate:

- requires a Git worktree and at least one exact file;
- refuses targets that already contain dirty user edits;
- tells Claude not to touch any other file or Git state;
- combines the final Git footprint with live filesystem observation, including
  ignored paths;
- reports `write_scope.status`, changed files, and any out-of-scope files.

This is prompt control plus postflight detection, not an OS sandbox. It never
auto-reverts a violation because that could destroy user work. If the task truly
requires broad write authority, use `unrestricted` only when that material scope
was explicit. The bridge captures a Git baseline when possible and reports an
observed persistent footprint; inspect that evidence and the final diff yourself.

Named safe profiles own their model, effort, and permission boundary. Do not try
to override `advisor`, `fable-advisor`, or `worker`; the runtime rejects such
drift. Only `unrestricted` accepts model/effort overrides, and even there raw
extra arguments cannot replace bridge-owned model/permission/tool controls.
Run guarded workers without tmux: if filesystem observation is unavailable or
lost, the bridge returns `write_scope.status: unknown`, never a safety pass.

Claude may read project sources and use its normal configured skills, plugins,
MCP tools, and auto memory unless the chosen profile/arguments disable them.
`no-skills` and `no-memory` are diagnostic exceptions, not defaults. Session
persistence and Claude auto memory are separate: a thread preserves chat
context; auto memory is Claude's own cross-session feature.

## Observe, Relay, Stop

- `claude_peek` / `claude_observe`: recent visible events, files/tools, warnings,
  relay cursor, and tmux capture. This is observable work, not private reasoning.
- `claude_wait`: bounded wait. A timeout stops waiting, not the Claude process.
- `claude_result`: current/final report and full-output file.
- `claude_kill`: stop only the saved fingerprinted process group or tmux session.
- `claude_cleanup_runs`: dry-run first; it skips runs still proved active.

Relay `chat_relay.text` when the user asked for Claude's answer. If truncated,
read `chat_relay.full_text_file`. Before closeout, require a terminal status:
`completed`, `failed`, `killed`, or safely explained `orphaned`. Report requested
and resolved model, profile, topic/thread, sources, status, warnings, write-scope
result when relevant, and whether the relay was complete.

## Skills And Memory Evidence

Do not treat Claude saying "I read the skill" as proof. Use
`claude_audit_skill`; `passed` requires a structured tool event with the exact
target path paired with a successful tool result. A failed/permission-denied
Read is `failed`; plain answer text is `unknown`; timeout stops the managed run
and reports `timed_out`.

For a real skill-use check, ask Claude to use a distinctive behavior from the
target skill, then separately inspect tool evidence and outcome quality. The
read audit proves access, not correct application.

## Failure And Recovery

If tools are missing or the MCP transport is stale, use the repo-controlled CLI
runner once and report that fallback. Do not replace a managed run with raw
`claude`. Classify failures as registration, CLI compatibility, auth, flag,
context, permission, model refusal, output, or process tail.

Read [references/managed-runs-and-relay.md](references/managed-runs-and-relay.md)
for lifecycle details and
[references/mcp-failure-handling.md](references/mcp-failure-handling.md) for
recovery. If both MCP and controlled CLI fail, stop with the exact missing layer.
