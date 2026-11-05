# Inside a T3 thread

The owner started you from T3, so `mcp__t3-code__*` tools are yours: use only
them. Work you hand out runs as child tasks under your thread, where he sees
it.

## When delegating

- Codex, Muse or Gemini: `delegate_task` with `target.providerInstanceId`,
  `target.model` and `target.options` from `orchestrator_capabilities`,
  called once per thread before the first delegate. Claude models stay your
  own subagents, per `1orchestration`.
- `title` is the owner's quota ledger: `<agent> <model>/<effort> · <role> ·
  <gist>`.
- Omit `target.projectId`: a local child runs in this thread's project, and
  another project id fails the call. For a sibling repository, give its
  absolute path in `task` and tell the child to work there.
  `isolation: "worktree"` gives a separate checkout of this project, without
  uncommitted edits.
- Omit `runtimeMode`: the child inherits yours.
- `task` carries goal, boundaries, neighbours and
  the starting state. Before relaunching a stopped attempt, look at
  `git status` and `git worktree list` for what it left and describe that
  in `task`: on 2026-11-05 a worktree briefed as empty held almost the
  whole diff.
- Keep the `taskId`; write it into the ticket if the work outlives the window.

## While it runs

- Completion and questions wake your thread: after delegating, end your turn.
  No watcher scripts, sleeps, or `task_status` on a running task.
- A question: `t3_pending_request` with `threadId` set to the child's
  `childThreadId` (without it the call addresses your own thread): `read` the
  `requestId` from the wake, or `list` if the wake has none, then `respond`
  with an offered option; nuance follows as `t3_thread_send` `mode: "steer"`
  to the child thread. Command approvals only the owner gives, in the app.
- A correction mid-turn: `t3_thread_send` `mode: "steer"`. A wrong brief or
  frame: `task_cancel`, then a new `delegate_task`.
- A review or re-check is a new `delegate_task`, never a message into the
  writer's thread.

## When it has finished

- `task_status` after the wake gives `summary`. It is done only at
  `workState: result_available` with no pending child runs; a finished turn
  with live child work is not done. Acceptance is `1orchestration`'s: the
  diff against `task`, not the report.
- A follow-up on the same topic: `t3_thread_send` to the finished child
  thread starts a fresh task that remembers what it read; it returns a new
  `taskId`, which replaces the one you kept.

## Top-level threads

`t3_thread_launch` and `create_threads` only when the owner asks for a new
thread: they live apart from yours and don't wake you.
