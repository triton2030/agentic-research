---
description: "Cut over the Claude advisor bridge to one Agent SDK-backed MCP tool"
kind: task
---

# Claude Advisor SDK Cutover

## Outcome

Activate the runtime contract owned by [`README.md`](../../../../README.md): one
blocking `claude_ask`, native Claude sessions, a compact terminal result and no
second agent control plane. This Task owns migration evidence only.

## Accepted Decision

- Keep MCP as the Codex-facing approval and typed-result boundary.
- Use exact-pinned `@anthropic-ai/claude-agent-sdk@0.3.215` with explicit
  `/Users/triton/.local/bin/claude` (Claude Code `2.1.215`).
- Keep cohesive owners for MCP transport, request/subscription validation,
  Agent SDK execution and bounded result formatting.
- Preserve Claude's native tools, settings, skills, hooks and MCP integrations.
  The no-modification instruction is behavioral, not a sandbox.
- Native `session_id` owns resume history and model. An initial Fable-to-Opus
  resolution is visible but not assigned an invented cause.
- Billing setup has one owner: [`docs/subscription-billing.md`](../../../../docs/subscription-billing.md).

## Completion Checklist

- [x] Production hot path uses the Agent SDK through one `askClaude` seam.
- [x] Superseded CLI/runner/server/profile/process-parser paths and the disposable
      SDK spike are removed. Git is source rollback.
- [x] Historical ignored `runs/` evidence is preserved and is not active code.
- [x] Deterministic policy/session/result/cancellation/MCP tests pass.
- [x] Live Opus, Fable, both resumes, parallel scope isolation, broad reads and
      full observed descendant-tree cancellation pass.
- [x] Clean install omits the bundled optional Claude binary and a subsequent
      live SDK call passes.
- [x] Fresh Codex Desktop discovers exactly one `claude_ask` and completes one
      real call through the configured MCP entrypoint.
- [x] Repo/global `1claude-mcp` skills are identical and valid.
- [x] README, AGENTS and subscription docs match final modules (coordinator owner).
- [x] Independent architecture/readability, developer and acceptance reviews pass.
- [x] Final full verification passes after docs-green.
- [ ] Commit and push `main`.

## Evidence

### Focused contract

- `npm run ask:test`: 11/11 green through `askClaude` plus an in-memory MCP call.
- Covered: fixed initial profiles; resume omits model/effort; independent parallel
  auth/session state; explicit route-env stripping; native config preservation;
  subscription rejection; invalid request/cwd/session; cancellation during auth;
  SDK cancellation and timeout; bounded typed failures/results; auxiliary model
  exclusion from `resolved_model`; cause-neutral model mismatch; one honest MCP
  schema with nullable resumed `requested_model`; MCP host cancellation and
  shutdown reach the same deep `askClaude(request, signal)` signal.

### Live contract

- Parallel initial sessions:
  - Opus `8531cb40-440a-4e13-927b-a2f152009a19`, resolved
    `claude-opus-4-8`, read its cwd marker, repo README and `/etc/hosts`.
  - Fable `cb35fbd7-4aee-4191-8fbb-8c6850ef57a1`, resolved
    `claude-fable-5`, read only its independent marker.
- Both sessions resumed with the opposite caller profile; each kept its UUID,
  original resolved model and returned `requested_model: null` plus
  `resume_session_owns_model`.
- Abort attributed SDK root PID `58942` as a direct child of the live-test host,
  observed its descendant tree before and throughout cancellation, and found
  every observed PID dead within the bounded five-second cleanup window.
- Final native-authority diagnostic session
  `71374576-b181-4856-bb33-db3757386f0e` captured successful typed `Bash`
  (`pwd && uname -s` -> bridge cwd + `Darwin`) and `Skill`
  (`1smart-simple` -> `Launching skill: 1smart-simple`) tool results through the
  production `askClaude` interface. No permission override or write was needed.

### Install and host activation

- `npm ci`: 99 packages installed, zero audit vulnerabilities.
- `.npmrc` omits optional dependencies; installed tree is 41 MB and does not
  contain `@anthropic-ai/claude-agent-sdk-darwin-arm64` (the default spike install
  duplicated a 246 MB binary).
- Post-clean-install live resume returned `SDK_CLEAN_INSTALL_OK`, native session
  `f9eb5513-b7ff-4fab-a32c-729429224e24`, resolved `claude-opus-4-8`.
- Fresh Desktop Task `019f7f2f-b2a2-77d1-be00-e04b8cbcf0a6` discovered exactly
  `mcp__claude_mcp__claude_ask` and returned `SDK_FRESH_HOST_OK` in one call with
  session `f9eb5513-b7ff-4fab-a32c-729429224e24`, Opus resolution and no warning.
  Config has `approval_mode = "prompt"`; the host showed no new prompt because
  authorization was already retained, and the bridge did not bypass it.

### Final active shape

- Production: 450 LOC across `ask-server.js` (transport/schema),
  `claude-ask.js` (composition/lifetime), `claude-policy.js` (request/auth),
  `claude-sdk.js` (typed SDK execution) and `claude-result.js` (bounded packet).
- Tests: 659 LOC across the focused suite, live suite and auth fixture.
- Exact SDK adds 22 installed package/version deltas over the earlier dependency
  tree while removing the handwritten CLI policy/process layers and the entire
  legacy control plane.

## Remaining Gate

Do not commit until the coordinator returns docs-green and independent reviews
map every remaining checklist item. Do not revive a lifecycle, registry,
background, provider abstraction or worker path in this cutover.
