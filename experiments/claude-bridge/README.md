# Claude Bridge Control

Repo-owned control plane for calling Claude Code from Codex. It provides safe
advisor defaults, current model aliases, resumable named conversations, parallel
independent advisors, guarded writes, logs/relay, skill-read evidence, and
restart-tolerant process control.

The global Codex MCP name is `claude-mcp`; its server is this project's
`src/server.js`. The bridge prefers native `~/.local/bin/claude` and never edits
Claude's skills or settings.

## Current Defaults

- `advisor`: moving `opus` alias, `max` effort, plan mode, no Bash/Edit/Write.
- `fable-advisor`: `fable`, `xhigh`, same read-only boundary; exceptional hard
  problems only.
- `worker`: Opus with auto permissions, exact `writeFiles`, clean-target gate,
  and Git postflight reporting.
- `unrestricted`: explicit permission bypass plus Git-footprint observation
  when available. `normal` and `turbo` are safe advisor compatibility aliases.

Claude's configured skills, plugins, MCP tools, session persistence, and auto
memory remain available unless a diagnostic profile disables them. The bridge
strips `ANTHROPIC_API_KEY` and `CLAUDE_API_KEY` from direct and tmux children so
ambient shell variables cannot silently move work onto API billing.

## Install And Verify

```bash
npm install
npm run doctor
npm run smoke
```

`doctor.ok` and `ready_for_live_runs` require both compatible core CLI flags and
live Claude authentication. Optional controls use live `claude --help` plus
non-spending parser probes through `claude auth status`; the CLI intentionally
omits some supported flags from help.

After changing `src/server.js` or its MCP schemas, restart Codex Desktop before
judging the installed MCP surface. Already-open Codex tasks can retain an older
server process and tool schema even though the configured file path is current.
The repo CLI is the controlled fallback during that reload boundary.

## MCP Tools

- run lifecycle: `claude_run`, `claude_peek`, `claude_observe`, `claude_wait`,
  `claude_result`, `claude_kill`
- conversations: `claude_thread_start`, `claude_thread_send`, `claude_threads`,
  `claude_thread_archive`
- capability/evidence: `claude_profiles`, `claude_doctor`,
  `claude_discover_skills`, `claude_audit_skill`
- retention: `claude_cleanup_runs`

The CLI exposes equivalent `run`, `thread-start`, `thread-send`, `threads`,
`thread-archive`, lifecycle, audit, doctor, and cleanup commands.

## Persistent Conversations

`run_id` identifies one process invocation. `thread_id` identifies one Claude
conversation and can span many runs. Start with `claude_thread_start`, finish the
turn with `wait`, continue with `claude_thread_send`, and recover handles with
`claude_threads`. Archiving the bridge handle does not delete Claude's session.

Several named threads can run concurrently and remain independently resumable.
Continuation inherits earlier framing, so use a fresh thread for a blind second
opinion. Threads also record exact cwd plus Git worktree/common-dir/ref identity;
cross-process leases serialize turns, and a different branch/worktree must use a
different thread.

## Guarded Worker

`worker` requires a Git worktree and exact paths relative to `cwd`:

```json
{
  "profile": "worker",
  "writeFiles": ["src/auth.js", "test/auth.test.js"]
}
```

Dirty target files are rejected before launch. The final report compares Git
status/fingerprints, ignored paths, live filesystem observations, and HEAD
movement with the baseline. This detects persistent out-of-scope changes but is
not an OS sandbox and never auto-reverts files. Guarded tmux runs report
`unknown` because their filesystem observation cannot be proven complete.

## Logs, Relay, And Tail

Each run writes prompt, profile, command, durable state, stream events,
stdout/stderr, debug log, final output, and report under ignored `runs/`. These
artifacts may contain sensitive content.

Reports include requested/resolved model, effort, session/topic, warnings,
observable activity, chat-ready relay, and worker scope status. If relay is
truncated, use its full-output file. A wait timeout does not stop Claude; close
only after a terminal status or an honestly explained orphan.

`useTmux: true` adds a saved, observable terminal session while retaining the
same logs and exact-session kill behavior. Never broad-kill Claude, tmux, or MCP
server processes by name.

Cleanup is dry-run by default and skips runs still proved active:

```bash
node src/cli.js cleanup --days 14
node src/cli.js cleanup --days 14 --confirm
```

`claude_audit_skill` passes only when an exact-path Read event is paired with a
successful tool result. Claude's self-report alone is `unknown`; a failed Read
does not pass.
