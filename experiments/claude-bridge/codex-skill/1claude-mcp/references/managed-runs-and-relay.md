# Managed Runs, Threads, And Relay

Use the bridge as the control plane around Claude Code. Codex owns the user task
and synthesis; Claude owns only the role named in the brief.

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
- `claude_peek` / `claude_observe`: visible activity, warnings, and relay cursor.
- `claude_wait` / `claude_result`: bounded wait or current/final report.
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
2. For long work, poll `claude_observe` with the previous `next_cursor`.
3. Use `claude_wait` with a bounded timeout. Timeout means the process may still
   be live.
4. Read `claude_result`; if the run is wrong or unwanted, use `claude_kill`.
5. Close only at a terminal status: `completed`, `failed`, `killed`, or safely
   explained `orphaned`.

`running_orphaned` means the bridge can still fingerprint the saved live
process after its original controller disappeared. It is not complete. A second
kill call may escalate a fingerprint-matched process group that ignored TERM.

For `useTmux: true`, the bridge records one exact tmux session, captures the
pane, tees stdout/stderr, strips Claude API key environment variables, and kills
only that saved session. A Codex-held `server.js` process is MCP plumbing, not a
paid model tail.

## Relay And Evidence

Final reports provide:

- `chat_relay.text` and `.markdown` for the user-visible Claude answer;
- `chat_relay.truncated` and `.full_text_file` for long output;
- requested `model`, stream-derived `resolved_model`, and `effort`;
- `activity`, warnings, files, status, and `agent_behavior`;
- `write_scope` for guarded workers.

`activity` exposes stream/tool/file/log/tmux observations, not private
chain-of-thought. Relay Claude's actual answer when requested, then distinguish
Claude's finding from Codex's acceptance judgment.

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

## Logs And Cleanup

Each run stores prompt, command/profile, state, events, stdout/stderr, debug log,
final output, and report under `experiments/claude-bridge/runs/`. These files can
contain sensitive prompt/tool content and are ignored by Git.

Cleanup is dry-run by default. Confirm deletion only for resolved run IDs; the
bridge refreshes old waitable state and skips anything still active. Never use a
broad process-name kill or broad filesystem deletion as cleanup.
