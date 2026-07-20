# Claude Bridge Instructions

This subtree is a standalone runtime experiment. Its supported behavior and
module ownership live in [`README.md`](README.md); active migration evidence
lives in the current `_ops/plans/**/task.md`. Do not treat an archived task,
installed skill copy, or old bridge source as current runtime truth.

## Preserve The Adapter Shape

- Keep the public surface and module seams described in `README.md`. A new tool,
  mode, flag, store, or protocol requires a recorded acceptance story that the
  current adapter demonstrably cannot satisfy.
- Keep the external interface to one blocking `claude_ask`. Do not add tmux,
  request/status lifecycle, persistence, restart recovery, run/thread
  registries, event logs, reports, relay, cleanup, or a worker path without a
  separately accepted goal and a proven failing story.
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
- Keep `claude_ask` explicitly configured for `approval_mode = "prompt"` in the
  Codex host. MCP annotations describe the tool but do not enforce host approval.
- Keep the subscription route fail-closed in `src/claude-policy.js`. Billing
  details and the external Usage credits prerequisite have one owner:
  [`docs/subscription-billing.md`](docs/subscription-billing.md). Do not copy that
  contract into the task-time skill.
- A Fable-to-Opus resolution is not a bridge failure, but must remain visible as
  requested versus resolved model evidence. Do not invent its cause.
- Keep the per-request auth probe asynchronous, abortable, and bounded. A
  synchronous child process in the MCP event loop serializes advisors and hides
  host cancellation.
- Keep the Agent SDK and installed Claude Code versions exact and compatible.
  Preserve `omit=optional` while an explicit local executable is supplied, and
  rerun clean-install plus live cancellation evidence on upgrades.

## Prove Changes At The Changed Seam

- Use the auth fixture and injected SDK query for deterministic request, billing,
  result, cancellation, and MCP failures; use live Claude only for
  model/session/access/process-tree/host stories the fakes cannot prove.
- Any MCP schema or entrypoint change requires focused tests plus discovery and
  one real call from a fresh Codex process. Already-open tasks can retain stale
  tools.
- Keep repo and installed `1claude-mcp` copies identical after an accepted skill
  change. Update `README.md` when supported behavior or module ownership changes;
  update the billing owner only when its claim or enforcement changes.
- Remove superseded runtime paths after a proven cutover. Do not leave two
  supported architectures for rollback convenience; Git owns rollback history.
