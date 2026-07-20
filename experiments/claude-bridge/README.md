# Claude Advisor Bridge

This project lets Codex ask Claude for an independent Opus or Fable opinion
while using the owner's Claude.ai subscription and Claude's native session
history.

The product is deliberately small. It is an adapter around Claude Code, not a
second agent runtime: it owns no durable run registry, conversation database,
tmux session, event log, report store, relay protocol, worker sandbox, or model
routing system.

The exact-pinned Claude Agent SDK owns execution, typed events, process cleanup,
and native session semantics. It is pointed at the owner's installed Claude Code
executable and uses that executable's Claude.ai login. The bridge adds only the
Codex-facing MCP seam, a small subscription preflight, request lifetime, and a
bounded result. There is no provider abstraction or alternate billing route.

The live cutover and its evidence are tracked in
[`_ops/plans/bridge-maintainability/claude-ask-cutover/task.md`](_ops/plans/bridge-maintainability/claude-ask-cutover/task.md).
That Task proves activation; this README owns the supported runtime contract.

## Supported Interface

The MCP entrypoint is `src/ask-server.js`. It exposes one blocking tool:
`claude_ask` runs one advisor turn and returns one bounded terminal packet.

`claude_ask` accepts:

- a non-empty `prompt`;
- fixed `opus_advisor` or `fable_advisor` profile;
- an existing `cwd`;
- an optional native Claude `session_id` for continuation.

The terminal packet contains bounded `text`, native `session_id`, requested and
resolved models, duration, and warnings. A Fable request that Claude resolves to
Opus is not a bridge failure, but the resolution must remain visible and the
bridge must not invent a cause that Claude did not report.

Claude owns the conversation through `session_id`; this bridge does not persist
or index it. A resumed session also owns its model, so `requested_model` is
`null` on continuation. Host cancellation is forwarded through the SDK's
`AbortController`. External-data approval happens in the Codex host before
dispatch and is explicitly configured as `prompt`; the host may retain a prior
authorization instead of showing a new prompt.

## Runtime Boundaries

### Local authority

Advisor runs receive broad local access, subject to the permissions that macOS
and the Claude process actually have. They retain Claude's native tools,
commands, skills, hooks, and settings so Claude can use Bash and other local
analysis workflows when useful.

The advisor prompt says to investigate and advise without changing anything.
That is a behavioral instruction, not an enforced read-only sandbox: a native
command or tool can write or delete local data if Claude ignores the instruction.
The owner accepts that residual risk. Do not recreate a pseudo-sandbox with
folder allowlists, command classification, write detection, hook suppression, or
tool deny lists; those controls would add code without providing the chosen
trust boundary. macOS privacy controls remain the real outer boundary.

### Subscription route

Every request removes explicit API/provider route variables from the SDK query
environment and runs `claude auth status` in that same environment. The request
starts only when the receipt reports a logged-in `claude.ai` / `firstParty`
subscription. The bridge exposes no API key, provider, base URL, or fallback
parameter. Native Claude settings remain active and are intentionally not
scanned; this is personal-tool hygiene, not an adversarial configuration guard.

That proves the observed credential route, not the account's Usage credits
setting. The owner must disable Usage credits in Claude Settings to make
out-of-plan spend unavailable. Claude exposes no documented machine-readable
switch for that account state, so the bridge must not invent billing accounting
or claim to verify it.
See [`docs/subscription-billing.md`](docs/subscription-billing.md) for the exact
maintainer checklist and official sources.

### Process lifetime

Each request has a 30-minute lifetime. The auth preflight is asynchronous; the
Agent SDK owns its Claude process tree and typed event stream. Timeout, host
cancellation, and MCP shutdown abort the same query, and terminal success or
failure is compact. The live regression observes the SDK root plus descendants
during cancellation and requires all of them to disappear afterward.

There is no restart recovery. If the MCP server exits, it cancels its live
children. Start a new advisor request; reuse a known native `session_id` only
when the earlier Claude turn completed.

## Code Owners

The public surface stays small while independent failure reasons remain local:

| Module | Owns | Must not own |
| --- | --- | --- |
| `src/ask-server.js` | the single MCP schema, annotations, host cancellation, shutdown, and transport mapping | Claude policy, execution, durable request state |
| `src/claude-ask.js` | the deep `askClaude(request, signal)` composition seam and request lifetime | MCP schema or SDK event details |
| `src/claude-policy.js` | request/cwd/session/profile validation, explicit route-env hygiene, and subscription preflight | settings governance, SDK execution, or result formatting |
| `src/claude-sdk.js` | the exact Agent SDK query, advisor instruction, native resume, and top-level model evidence | public packet shape or billing policy |
| `src/claude-result.js` | compact typed failures and the bounded public packet | auth or SDK process ownership |

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

The live suite exercises parallel Opus and Fable calls, both native resumes,
broad cwd/home/system reads, and cancellation with no observed SDK process tail.
A schema or entrypoint change also requires discovery and one real request from
a fresh Codex process; an already-open task may retain an old MCP server, schema,
or authorization state.

Before release, also run syntax and diff checks. Source and installed copies of
`1claude-mcp` must match, and the Codex MCP configuration must point to
`src/ask-server.js` with a 30-minute timeout and per-tool
`approval_mode = "prompt"`.

## Change Rule

Do not add a tool, mode, flag, persistent store, background protocol, or worker
path because it might be useful later. First record the exact acceptance story
that fails without it and prove the failure with the current adapter. Prefer a
smaller repair inside an existing owner.

Before writing a wrapper, check the current official Claude Code, Agent SDK,
Codex, and MCP documentation plus the installed runtime. Claude already owns
native sessions, resume, typed SDK events, background agents (`--bg`), agent
monitoring, logs, stop/respawn, worktrees, permissions, and MCP isolation. If a
future story genuinely needs one of those capabilities, adapt the native owner
instead of recreating its state machine here.

The former control plane and handwritten CLI stream/process implementation are
not supported rollback paths. Git owns source rollback; ignored historical
`runs/` remain local evidence, not active runtime truth.
