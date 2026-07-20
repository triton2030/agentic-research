# Claude Bridge Failure Handling

Preserve the requested Claude role. Do not silently replace it with Codex's own
reasoning or an uncontrolled raw CLI call.

## Classify First

- **Tool visibility:** MCP tools are absent in the current Codex window.
- **Transport:** tool exists but the transport is closed/stale.
- **CLI compatibility:** native CLI/version/help lacks a core or requested flag.
- **Auth:** `claude auth status` is not logged in or OAuth refresh failed.
- **Context:** cwd/addDir/file permissions do not expose the real sources.
- **Permission:** advisor cannot perform an authorized write, or worker scope is
  missing/dirty.
- **Upstream external-data approval:** Codex rejects the tool call before a
  `run_id` exists because local material would be sent to Claude's service.
- **Model:** alias unavailable, rate limit, or Fable refusal.
- **Evidence/output:** self-report without tool evidence, truncated relay, or
  malformed stream.
- **Lifecycle:** timeout, orphaned controller, ignored TERM, or lingering tmux.

Run `claude_doctor` for setup/auth/flag failures. Its `ok` is intentionally false
when CLI syntax is compatible but the account is not ready for live runs. Read
`flag_evidence`: `advertised` comes from help and `parser_probe` from a
non-spending `auth status` parse, because help does not expose every live flag.

## Recovery Ladder

1. Correct the profile, context roots, exact write scope, or supported option.
2. If an upstream gate rejects external-data transfer before the bridge starts,
   name the failed layer accurately. Preserve the requested file-level task,
   state the minimum exact `addDir` roots made readable, the exact requested
   files, and that content Claude reads would be sent to Anthropic's service;
   then ask for explicit user confirmation after that warning. On approval,
   retry the original managed call with the same `cwd`, `addDir`, role, and
   sources. Do not silently strip owners, anonymize the brief, or substitute
   native agents. If the user declines or the platform rejects the confirmed
   retry, stop the Claude route. Offer a sanitized/meta review only as a new
   user choice; do not start it automatically.
3. If MCP registration/transport is the problem, compare the visible tools with
   the repo's current server schema. An already-open Codex task may retain an old
   MCP process and schema after a bridge update. Use the repo-local controlled
   CLI once, then restart Codex Desktop before judging the installed MCP surface.
   The CLI shares the same runner, logs, threads, and stop rules.
4. If subscription auth is false, stop and ask the user to complete
   `claude auth login` with their Claude.ai plan. Do not claim fake/smoke
   execution as a live Claude result.
5. If Fable refuses a valid task, preserve the refusal and create a fresh Opus
   advisor thread. Label it as fallback evidence.
6. If relay is truncated, read the recorded full-output file before raw logs.
7. If a wait times out, observe or kill the still-live run; timeout is not stop.
8. If a saved process ignores TERM, a second bridge kill may escalate only the
   fingerprint-matched process group.

Do not broad-kill Claude, tmux, or all bridge servers. Do not pass hidden API
keys or provider/gateway credentials to force a different billing path. The
runner removes all higher-precedence auth environments and refuses
`apiKeyHelper` before direct or tmux launch. A subscription rate limit is not
authority to switch to paid credits; wait for reset unless the user explicitly
changes the billing scope.

## Skill And Memory Failures

Claude's configured skills and auto memory remain available by default. If a
task depends on one skill, use `claude_audit_skill` for exact-path read evidence
and check the resulting behavior separately. `unknown` means Claude mentioned
the path without a structured tool event. `timed_out` means the audit was stopped
and provides no read proof.

`no-skills` and `no-memory` intentionally change Claude's environment while
keeping the read-only advisor boundary; use them only to isolate a suspected
skill/memory problem.

## Report A Blocker

State the requested Claude role, failed layer, evidence, recovery attempted,
whether a live process remains, and the next concrete user/system action. A
blocked Claude review is not a completed review.
