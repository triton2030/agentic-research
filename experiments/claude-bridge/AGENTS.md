# Claude Bridge Instructions

This subtree is a standalone runtime experiment. Its supported behavior and
module ownership live in [`README.md`](README.md). Active migration evidence,
when present, lives in a current `_ops/plans/**/task.md`; completed evidence is
archived below the same plan. Do not treat an archived task, installed skill
copy, or old bridge source as current runtime truth.

## Preserve The Adapter Shape

- Keep the public surface and module seams described in `README.md`. The accepted
  surface is one blocking default, `claude_ask`, plus the opt-in
  `claude_session` control seam and pull-only `claude_observe`. Another tool,
  mode, flag, store, or protocol requires a recorded failing acceptance story.
- Keep session control transient and process-local. Each active registry entry
  is keyed by its native Claude `session_id`; never introduce a second handle or
  identity. Restart may discard every active lease, but the same native session
  can still be resumed in a new lease. Do not add persistence, restart recovery,
  a durable run/thread registry, event log, report store, relay, tmux, or worker
  path.
- Keep `claude_ask` blocking and compatible as the ordinary path.
  `claude_session.open_fresh` includes the initial prompt and returns the native
  `session_id`; `open_resume` accepts that ID plus a new prompt. Later send,
  steer, stop, and every `claude_observe` call address the same native ID. Never
  push a continuous stream or copy raw transcripts, extended thinking, or tool
  inputs/outputs into Codex context.
- Keep request/subscription policy, SDK execution, transient transport state,
  and result formatting in their existing owners. Do not create shallow
  manager/provider/factory layers or merge those independent failure reasons
  into one file.
- Claude owns conversation history through its native `session_id`; this bridge
  must not read or reproduce Claude's private session format.
- Before implementing infrastructure, check current official Claude Code,
  Agent SDK, Codex, and MCP documentation plus the installed runtime. Prefer
  Claude's native sessions, resume, typed SDK events, `--bg`/agent view,
  worktrees, permissions, and process supervision over locally reimplementing
  them. The exact Agent SDK is the sole execution implementation; do not restore
  handwritten process/stream protocol or a multi-provider layer.

## Preserve The Chosen Trust Boundary

- Advisor access is broad and uses Claude's native commands, skills, hooks, and
  settings. The prompt instructs Claude to investigate without modifying data;
  this is deliberately a trust-based behavior contract, not an enforced
  read-only sandbox. Do not add folder allowlists, command classification,
  write detection, hook suppression, or tool deny lists unless the owner changes
  that product decision. Preserve host cancellation and process-tail checks.
- Keep `claude_ask` and `claude_session` explicitly configured for
  `approval_mode = "prompt"` in the Codex host. MCP annotations describe the
  tools but do not enforce host approval.
- Keep the subscription route fail-closed in `src/claude-policy.js`. Billing
  details and the external Usage credits prerequisite have one owner:
  [`docs/subscription-billing.md`](docs/subscription-billing.md). Do not copy that
  contract into the task-time skill.
- A Fable-to-Opus resolution is not a bridge failure, but must remain visible as
  requested versus resolved model evidence. Do not invent its cause.
- Preserve compact typed warnings for subscription overage/credits,
  model-refusal fallback, and denied tool names. Never expose denial prose,
  permission inputs, raw tool output, or fallback explanation text.
- Keep the auth probe for each new native process asynchronous, abortable, and
  bounded. A synchronous child process in the MCP event loop serializes
  advisors and hides host cancellation.
- Keep the Agent SDK and installed Claude Code versions exact and compatible.
  Preserve `omit=optional` while an explicit local executable is supplied, and
  rerun clean-install plus live cancellation evidence on upgrades.

## Prove Changes At The Changed Seam

- Use the auth fixture and injected SDK query for deterministic request, billing,
  result, cancellation, and MCP failures; use live Claude only for
  model/session/access/process-tree/host stories the fakes cannot prove.
- Prove parallel lease isolation, bounded observation, steer/stop ordering,
  shutdown cleanup, and restart-loss/resume behavior at the session adapter
  seam. The bridge's internal active-turn deadline must expire before the Codex
  host tool timeout so it can return a typed result and clean its process tree.
- Any MCP schema or entrypoint change requires focused tests plus discovery and
  real blocking and session calls from a fresh Codex process. Already-open tasks
  can retain stale tools. Every public tool must expose a non-empty,
  model-usable JSON Schema after the MCP SDK converts its Zod owner.
- Keep one context-bearing success carrier: bounded `structuredContent`. The
  text block is a constant receipt because a fresh Codex probe proves it reads
  structured-only evidence; do not restore a serialized duplicate without new
  host evidence.
- Keep repo and installed `1claude-mcp` copies identical after an accepted skill
  change. Update `README.md` when supported behavior or module ownership changes;
  update the billing owner only when its claim or enforcement changes.
- Remove superseded runtime paths after a proven cutover. Do not leave two
  supported architectures for rollback convenience; Git owns rollback history.
