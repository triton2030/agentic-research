# Claude Advisor Bridge

This project lets Codex ask Claude for an independent Opus 5 opinion
through a blocking default or an opt-in transient session adapter, while using
the owner's Claude.ai subscription and Claude's native session history.

The product is deliberately small. It is an adapter around Claude Code, not a
second agent runtime. It may hold bounded process-local state for active Claude
leases and a small tail of terminal snapshots, keyed by native `session_id`; it
owns no durable run registry, second session identity, conversation database,
tmux session, event log, report store, relay protocol, worker sandbox, or model
routing system.

The exact-pinned Claude Agent SDK owns execution, typed events, process cleanup,
native session semantics, and supported local session reads. It is pointed at
the owner's installed Claude Code executable and uses that executable's
Claude.ai login. The bridge adds only the Codex-facing MCP seam, a small
subscription preflight, transient lease lifetime, and bounded results,
observations, and visible-session reads. There is no provider abstraction or
alternate billing route.

The completed adapter cutover and its acceptance evidence are archived in
[`_ops/plans/bridge-maintainability/_archive/claude-session-adapter/task.md`](_ops/plans/bridge-maintainability/_archive/claude-session-adapter/task.md).
That Task is historical evidence; this README owns the supported runtime
contract.

## Supported Interface

The MCP entrypoint is `src/ask-server.js`. The supported surface has exactly
four tools: blocking `claude_ask`, transient `claude_session`, pull-only
`claude_observe`, and read-only `claude_sessions`.

### Blocking Default

`claude_ask` accepts:

- a non-empty `prompt`;
- the fixed `opus_advisor` profile;
- an existing `cwd`;
- an optional native Claude `session_id` for continuation.

Fresh calls pin the profile to the exact `claude-opus-5` model ID. The compact
public `requested_model` field is `opus`; `resolved_model` carries Claude's exact
runtime evidence.

The terminal packet contains bounded `text`, native `session_id`, requested and
resolved models, duration, and warnings. A fresh call, resumed session, or
runtime fallback that exposes a non-Opus primary model fails closed with
`unsupported_model`.

A nominal SDK success with a non-completing `terminal_reason`, such as
`background_requested`, fails closed with a resumable typed error. The blocking
path never labels an answer terminal after Claude moved required work into the
background.

Warnings retain only compact typed evidence: explicit subscription
overage/credits signals, model-refusal fallback, permission-denied tool names,
environment stripping, resume ownership, and truncation. They never retain
permission inputs, denial prose, tool output, or fallback explanation text.

Claude owns the conversation through `session_id`; this bridge does not persist
or index it. A resumed session also owns its model, so `requested_model` is
`null` on continuation. Host cancellation is forwarded through the SDK's
`AbortController`. External-data approval happens in the Codex host before
dispatch and is explicitly configured as `prompt`; the host may retain a prior
authorization instead of showing a new prompt.

`claude_ask` remains the ordinary path: it runs one advisor turn, waits, and
returns one bounded terminal packet. The session tools do not make blocking ask
a compatibility afterthought or require callers to manage a lifecycle. Use the
advisor before work, during a parallel host track, or after work as a review;
parallel execution uses the opt-in session path below.

### Transient Session Control

`claude_session` controls live Agent SDK leases without introducing another
session identity:

- `open_fresh` includes the initial prompt and returns Claude's native
  `session_id` once the live adapter can truthfully identify it;
- `open_resume` accepts a known native `session_id` plus a new prompt;
- later send, steer, and stop commands address the same native `session_id`.

The process-local registry is bounded and contains live lease state plus a small
tail of terminal snapshots. Distinct native sessions may run in parallel; their
prompts, queues, observations, cancellation, and results stay isolated. A
second active lease for the same native `session_id` is rejected.

The native `session_id` is both the public address and the durable conversation
identity. There is no public lease handle. If the MCP server restarts, every
active lease and retained observation disappears. A caller can still use
`open_resume` with the same known native ID and a new prompt; the bridge does not
recover the old process, reconstruct an abandoned turn, or persist registry
state.

### Pull-Only Observation

`claude_observe` reads one bounded snapshot for an active native `session_id`.
The caller selects a summary, activity, conversation, or diagnostic view:

- summary reports compact status and current/last-turn outcome;
- activity reports a bounded normalized account of recent work;
- conversation reports a bounded user/assistant view;
- diagnostic reports compact session, model, queue, timeout, and failure
  evidence.

Observation is pull-only: there is no push stream, background feed, or raw event
log. The bridge never copies a continuous transcript, extended thinking, or raw
tool inputs/outputs into Codex context. Bounds apply to retained state and every
response, not only to display formatting. Tool activity can be derived from a
typed assistant `tool_use` block even when Claude Code emits no separate
`tool_progress`; only the tool name is retained.

Successful MCP calls use `structuredContent` as the only context-bearing
payload; the text block is a constant short receipt, not a serialized duplicate.
A fresh Codex host probe must prove it can read a marker present only in
`structuredContent` before this compatibility tradeoff is changed.

### Existing Session Discovery

`claude_sessions` exposes two read-only operations over active local Claude
Code and Claude Desktop sessions:

- `list_active` returns at most twenty active native sessions with their native
  `session_id`, name, kind, cwd, title, branch, and start time, but no
  conversation text;
- `read` accepts one active native `session_id` plus an optional cwd scope and
  returns a bounded tail of visible user/assistant messages.

The installed Claude executable owns the active-process list through
`claude agents --json`; the exact Agent SDK owns session metadata and message
reads. The bridge does not parse Claude's private transcript format, index
history, or retain another copy. System messages, thinking, tool calls/results,
hooks, and subagent transcripts never cross this seam. Unreadable optional
metadata does not hide an active session; CLI identity and project fields still
remain available.

Discovery does not send, resume, steer, stop, or otherwise mutate a session. A
session discovered as active may have a writer in Claude Desktop or another
process, so its ID is not permission to open another live writer through
`claude_session`.

## Runtime Boundaries

### Local authority

Advisor runs receive broad local access, subject to the permissions that macOS
and the Claude process actually have. They retain the current Claude session's
native tools, commands, skills, hooks, settings and deferred tool discovery.
The exact tool set is runtime-owned and can vary with version, provider, mode
and settings.

The advisor prompt says to investigate and advise without changing anything.
That is a behavioral instruction, not an enforced read-only sandbox: a native
command or tool can write or delete local data if Claude ignores the instruction.
The owner accepts that residual risk. Do not recreate a pseudo-sandbox with
folder allowlists, command classification, write detection, hook suppression, or
tool deny lists; those controls would add code without providing the chosen
trust boundary. macOS privacy controls remain the real outer boundary.

The bridge does not auto-approve a native Claude permission prompt. A denied
tool remains fail-closed and its name becomes compact warning/activity evidence;
the prompt arguments and denial body do not cross the observation seam.

### Subscription route

Every new native process removes explicit API/provider route variables from the
SDK query environment and runs `claude auth status` in that same environment.
The process starts only when the receipt reports a logged-in `claude.ai` /
`firstParty` subscription. The bridge exposes no API key, provider, base URL, or
fallback parameter. Native Claude settings remain active and are intentionally
not scanned; this is personal-tool hygiene, not an adversarial configuration
guard.

Pinned Claude Code emits its SDK initialization only after the first streaming
input arrives. The exact-environment auth preflight therefore gates launch
before input, and the SDK credential receipt is checked immediately after init;
a contradiction aborts the turn before its result is accepted.

That proves the observed credential route, not the account's Usage credits
setting. The owner must disable Usage credits in Claude Settings to make
out-of-plan spend unavailable. Claude exposes no documented machine-readable
switch for that account state, so the bridge must not invent billing accounting
or claim to verify it.
See [`docs/subscription-billing.md`](docs/subscription-billing.md) for the exact
maintainer checklist and official sources.

### Process lifetime

Each active turn has an internal bridge deadline that expires before the Codex
host tool timeout. This ordering leaves time for a typed timeout response and
bounded cleanup instead of letting the host sever transport first. Idle leases
do not consume an active-turn deadline.

The auth preflight is asynchronous for each new native process. The Agent SDK
owns its Claude process tree and typed event stream. Explicit stop, internal
timeout, MCP shutdown, and cancellation of a still-opening lease converge on
bounded close and process-tail cleanup; the first terminal cause wins.

There is no restart recovery. If the MCP server exits, it cancels live children
and loses its active registry. The same native `session_id` may later be resumed
through a new process, but the bridge does not claim continuity for an abandoned
in-flight turn.

## Code Owners

The public surface stays small while independent failure reasons remain local:

| Module | Owns | Must not own |
| --- | --- | --- |
| `src/ask-server.js` | the four MCP schemas, annotations, per-call cancellation, shutdown, and transport mapping | Claude policy, SDK events, or durable state |
| `src/claude-ask.js` | the blocking `askClaude(request, signal)` compatibility seam over transient execution | MCP schema, session registry, or SDK event details |
| `src/claude-session.js` | the bounded process-local registry keyed by native `session_id`; open/resume, send, steer, stop, bounded observation-event projection, and shutdown | durable identity, persistence, Claude history, or raw event logs |
| `src/claude-sessions.js` | active native-session discovery, official SDK metadata/message reads, visible-text filtering, and output bounds | live lease control, persistence, raw transcript parsing, or session mutation |
| `src/claude-policy.js` | request/cwd/session/profile validation, explicit route-env hygiene, and subscription preflight | settings governance, SDK execution, or result formatting |
| `src/claude-sdk.js` | the exact streaming Agent SDK query, controlled input, turn-completion/model reduction, compact runtime-warning normalization, native resume, and session evidence | registry policy, public packet shape, or billing policy |
| `src/claude-result.js` | compact typed failures and bounded blocking/session packets | auth, registry, or SDK process ownership |

Do not split files for symmetry and do not merge independently failing request
policy, SDK execution, transport state, and formatting into a god module. Add
an abstraction only when current complexity makes the seam real.

## Develop And Verify

Install the exact lockfile and run the deterministic contract suite:

```bash
npm ci
npm run ask:test
```

The local `.npmrc` omits optional packages because the SDK is deliberately
pointed at the already installed Claude Code executable. A clean install must
not download the SDK's duplicate native Claude binary.

Run live acceptance only when its subscription usage and local side effects are
intended:

```bash
npm run ask:live
```

The live suite exercises parallel blocking Opus calls,
native resume, bounded observation, follow-up, steer, stop, broad
cwd/home/system reads, and cancellation with no observed SDK process tail. A
schema or entrypoint change also requires fresh Codex discovery of exactly the
four supported tools, one real blocking call, one real session flow, and one
real active-session list/read. An already-open task may retain an old MCP
server, schema, or authorization state.

Before release, also run syntax and diff checks. Source and installed copies of
`1claude-mcp` must match after an accepted projection change. The Codex MCP
configuration must point to `src/ask-server.js`; its host timeout must be
strictly longer than the bridge's active-turn timeout, and external-data
dispatch remains explicitly host-approved.

## Change Rule

Do not add another tool, mode, flag, persistent store, background protocol, or
worker path because it might be useful later. First record the exact acceptance
story that fails without it and prove the failure with the current adapter.
Prefer a smaller repair inside an existing owner.

Before writing a wrapper, check the current official Claude Code, Agent SDK,
Codex, and MCP documentation plus the installed runtime. Claude already owns
native sessions, resume, typed SDK events, background agents (`--bg`), agent
monitoring, logs, stop/respawn, worktrees, permissions, and MCP isolation. If a
future story genuinely needs one of those capabilities, adapt the native owner
instead of recreating its state machine here.

The former control plane and handwritten CLI stream/process implementation are
not supported rollback paths. Git owns source rollback; ignored historical
`runs/` remain local evidence, not active runtime truth.
