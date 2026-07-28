# Claude Session Adapter

Read this only when a blocking call would prevent useful parallel work, or when
the task materially benefits from follow-up, mid-turn correction, user-visible
progress, liveness checks, or explicit stop.

## Start And Address

- Fresh: `claude_session` with `op: open_fresh`, initial `prompt`, `profile`,
  `cwd`, and optional `effort: max`.
- Native continuation after a bridge restart: `op: open_resume` with the known
  `session_id`, same project `cwd`, and a new prompt.
- Keep the returned native `session_id`. It is both the live address and
  Claude's durable conversation identity; there is no second bridge handle.
- Use distinct IDs for independent parallel advisors. Never open two live
  leases for the same native session.

`open_*` returns after native initialization, while Claude continues the turn.
Do useful local work meanwhile. Do not start a polling loop.

## Observe Without Spending Codex Context

`claude_observe` is pull-only and every view is bounded:

- `summary` is the default O(1) liveness snapshot: state, cursor, last activity,
  visible direction, active tool name, thinking-token estimate, subagent count,
  stall heuristic, model evidence, and terminal kind.
- `activity` is a small normalized event diff after a known cursor.
- `conversation` is an explicit bounded peek at visible user/assistant text.
- `diagnostic` is compact process/error metadata.

Use summary when the user asks for status, before steering, or after a material
silence. Use one `wait_ms` long-poll when you are genuinely waiting; do not loop
it. Request activity/conversation only when their content will change the next
decision. The bridge never returns private reasoning, partial-token streams,
raw tool inputs/outputs, hook logs, nested subagent transcripts, or whole
history. A tool name, permission denial, subscription overage/credits signal, or
model-refusal fallback may appear as compact typed activity/warning evidence;
its raw inputs, output, denial prose, and fallback explanation never do.

## Continue, Correct, Finish

- State `idle`: use `op: send` for a follow-up.
- Active state (`thinking`, `tool`, `subagent`, `retrying`): use `op: steer`
  only when the correction materially changes the running task. It interrupts
  the current turn first, then applies the correction in the same live process
  when possible. A native resume is used only after any required process cleanup
  has actually completed.
- `requires_action` means Claude is waiting on user/permission action; inspect
  one diagnostic snapshot, then steer or stop deliberately. `closing` reserves
  capacity until process cleanup is actually complete; never reopen or send
  while it remains visible.
- State `idle` with terminal success: request one bounded `conversation` view
  to read the answer, verify material claims locally, then `stop` unless another
  follow-up is already justified.
- Use `stop` to end the process-local lease. Native history remains resumable.

`possibly_stalled` is a heuristic, not proof of death. First request one
activity or diagnostic snapshot; steer/stop only from evidence. A lost
process-local lease is not recovered automatically: call `open_resume` with the
known native ID, cwd, and a new prompt.
