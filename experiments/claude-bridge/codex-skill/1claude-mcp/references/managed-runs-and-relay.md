# Managed Runs, Threads, And Relay

Use the bridge as the control plane around Claude Code. Codex owns the user task
and synthesis; Claude owns only the role named in the brief.

## Contents

- Tool Map
- Run And Thread Identity
- Run Lifecycle
- Compact Wire, Relay, And Evidence
- Guarded Writes
- Logs And Cleanup

## Tool Map

- `claude_doctor`: CLI compatibility plus live auth readiness.
- `claude_profiles`: current bridge profiles and exact CLI flags.
- `claude_run`: one managed invocation with a saved Claude session by default;
  use thread tools for bridge-owned durable continuation.
- `claude_thread_start`: create one named bridge-owned Claude conversation.
- `claude_thread_send`: resume that conversation by its stable `thread_id`.
- `claude_threads`: recover thread handles and last status after restart or
  context compaction.
- `claude_thread_archive`: hide/unhide a handle without deleting Claude's store.
- `claude_peek` / `claude_observe`: bounded activity delta after a caller-owned
  cursor.
- `claude_wait`: one long wait returning only a compact control envelope.
- `claude_result`: recover the compact current/final acceptance packet.
- `claude_relay`: read the terminal Claude answer in bounded cursor chunks.
- `claude_kill`: stop only the saved process group or tmux session.
- `claude_audit_skill`: prove an exact target path appeared in a structured tool
  event.
- `claude_cleanup_runs`: dry-run or remove old terminal run logs; active runs are
  skipped.

## Run And Thread Identity

`run_id` identifies one process invocation and its logs. `thread_id` identifies
one persistent Claude conversation and normally equals its Claude `session_id`.
One thread can therefore have many run IDs.

The append-only thread registry stores topic, cwd, requested model/profile,
Git worktree/common-dir/ref identity, turn count, archive state, and last run.
It does not duplicate Claude's chat contents; Claude Code owns those. A bridge
archive is reversible and is not a delete operation.

Use continuation only when inherited context is useful. Start a fresh thread
when the user wants a blind reviewer, a second opinion, or a different framing.
Multiple independent threads can run concurrently; wait for and close every run.
Different Codex agents and Git worktrees share the registry safely: each
conversation has a UUID, each send takes an atomic cross-process lease, and a
resume must match the original cwd/worktree/ref. Use a new thread after changing
branches rather than importing stale branch context.

## Run Lifecycle

1. Start and retain `run_id`, `session_id`/`thread_id`, and `log_dir`.
2. Start one long `claude_wait`. If Codex receives a host continuation/cell
   handle, wait on that same handle instead of launching another bridge wait.
3. Only when progress matters, call `claude_observe` with that consumer's
   previous `next_cursor`; it returns recent bounded updates, never history.
4. At terminal status, inspect the wait acceptance packet. Use `claude_result`
   only after restart, compaction, or a lost wait.
5. Call `claude_relay` for the answer. Follow `next_cursor` selectively; do not
   read the full output/report file by default.
6. If the trajectory is wrong or unwanted, use `claude_kill`.
7. Close only at a terminal status: `completed`, legacy `completed_unknown`,
   `failed`, `killed`, or safely explained `orphaned`. `completed_unknown`
   permits relay but is not verified success; preserve its
   `legacy_terminal_status_unknown` warning in the handoff.

`running_orphaned` means the bridge can still fingerprint the saved live
process after its original controller disappeared. It is not complete. A second
kill call may escalate a fingerprint-matched process group that ignored TERM.

For `useTmux: true`, the bridge records one exact tmux session, captures the
pane, tees stdout/stderr, strips every higher-precedence Claude auth/provider
environment, and kills only that saved session. A Codex-held `server.js` process
is MCP plumbing, not a paid model tail.

## Compact Wire, Relay, And Evidence

The bridge separates three planes:

- **control:** `wait`, `observe`, and `result` return status, cursor, warning
  kinds, model/output handles, and one `_envelope.next_step`;
- **relay:** `claude_relay` returns only one bounded answer chunk plus
  `next_cursor`/`has_more`;
- **evidence:** command, raw stream, activity, files, full answer, and report stay
  under the run directory.

Control responses never contain the cumulative report or Claude's answer.
`claude_observe` defaults to three updates and is capped at eight. A caller owns
its cursor: different Codex agents can inspect the same run without mutating a
shared "already read" state. `claude_relay` behaves the same way for final text.

The terminal acceptance packet exposes requested/resolved model, model-switch
history when relevant, effort, session/topic, billing, warnings, output/report
handles, and compact `write_scope`. Read targeted full-report fields only when a
warning or acceptance decision requires them. Observable events contain
tool/file/log/tmux and model-visible updates, not private chain-of-thought.
Relay Claude's answer when requested, then distinguish Claude's finding from
Codex's acceptance judgment.

## Guarded Writes

`worker` requires exact `writeFiles` inside a Git worktree. Before launch, the
bridge rejects allowed targets with pre-existing dirty edits. The prompt forbids
other files and Git-history operations. Terminal reporting compares dirty-file
fingerprints, ignored-path state, filesystem observations, and HEAD movement
with the baseline. Symlink targets are rejected before launch, and a path that
becomes a symlink is a violation.

`write_scope.status: passed` proves only the detected persistent Git footprint
stayed inside the exact list. It is not an OS sandbox and cannot prove that
Claude never read or temporarily touched another path. `failed` or `unknown`
requires local inspection; the bridge never auto-reverts.
If the watcher cannot reach a complete terminal handoff, including a guarded
tmux worker, the verdict is `unknown`.

`unrestricted` has no allowed-file boundary, but the bridge still snapshots a
Git worktree when available and reports only persistent changes relative to
that baseline. `observed` is footprint evidence, not a safety pass. `unknown`
means a Git baseline was unavailable.

Read-only profiles also snapshot the Git-worktree footprint and fail their
evidence check if a persistent local change appears. Attribution stays unknown
when concurrent agents share a worktree. This catches some subagent/MCP
mutation, but cannot prove there was no temporary write or external-service
side effect.

## Logs And Cleanup

Each run stores prompt, command/profile, state, events, stdout/stderr, debug log,
final output, and report under `experiments/claude-bridge/runs/`. These files can
contain sensitive prompt/tool content and are ignored by Git.

Cleanup is dry-run by default. Confirm deletion only for resolved run IDs; the
bridge refreshes old waitable state and skips anything still active. Never use a
broad process-name kill or broad filesystem deletion as cleanup.
