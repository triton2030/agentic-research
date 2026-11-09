# T3 from plain Claude Code

You run outside T3 (no `mcp__t3-code__*` tools): the T3 tools come from the
`t3` server, a thread you launch is top-level, and T3 doesn't wake you when
its turn ends or know which agent launched it.

## When launching

```json
{
  "title": "Codex gpt-6.1-sol/<effort> · doer · <gist>",
  "projectId": "<id>",
  "runtimeMode": "full-access",
  "modelSelection": {
    "instanceId": "codex",
    "model": "gpt-6.1-sol",
    "options": [{"id": "reasoningEffort", "value": "<effort>"},
                {"id": "serviceTier", "value": "default"}]
  },
  "message": "<brief>"
}
```

- `instanceId` is the catalog's `providerInstanceId`; option ids come from
  the catalog (Grok's effort is `reasoning_effort`, Gemini's is in the model
  name). Without a project pass `scratch: true`.
- The title `<agent> <model>/<effort> · <role> · <gist>` is the owner's
  ledger of his quota.
- Always set `runtimeMode`: otherwise the project default applies. Below
  `full-access` the thread waits for consent nobody gives; `auto` too, since
  the provider's review asks about non-routine actions (per the docs).
- The thread works in the project root, next to other threads. Before a
  writing thread check `t3_thread_list` with `statuses: ["running"]` and give
  it a zone nobody edits, or `workspaceStrategy` `worktree`: that copy lacks
  uncommitted edits and ignored files like `node_modules`, and the project's
  `runOnWorktreeCreate` did not run — put setup into the brief.
- Keep the `threadId` from the response. All the owner's Claude sessions sign
  in as one client and see each other's threads, and titles look alike: the
  id is the only proof the thread is yours. Give the owner the response's
  `link` with role and task; if another session will return, write the id
  into the work note.
- Set `clientRequestId` only to retry, made unique: `CLAUDE_CODE_SESSION_ID`,
  gist, number.
  The key is shared by all agents, and a reused key with new text silently
  returns the old receipt without delivering.

## When waiting

A finished turn won't wake you. A short turn: `t3_thread_wait` with
`timeoutMs` at most 55000 (the client aborts three minutes). A long one: the
watcher in the background (`run_in_background: true`) with the launch's
`runId`, or the `threadId` to follow its latest turn:

```bash
bash "<skill-dir>/scripts/wake_on_done.sh" '<runId or threadId>'
```

Several threads at once, or a doer you check on a schedule: one background
`scripts/wake_on_any.sh [--tick MIN] <id>...` exits on the first thread that
ends or asks, naming the ids still watched, or after the tick; start it again
with those ids. One watcher per thread plus a timer woke a session separately
for each of six tasks (2026-11-03).

It reads the turn's status from T3's database for free, exits when the turn
ends or the agent asks, and follows a turn T3 continued after a restart. In
a session without a human (`claude -p`, cloud) give the background command
`timeout: 7200000`: otherwise it dies at 30 minutes. In probes a subagent
wasn't woken by a background command; it waits with `t3_thread_wait`.
Status `waiting` is not a question: the provider finished and the checkpoint
is being saved. Do independent work meanwhile, then keep waiting until you
have read the result or named a blocker.

## While a turn runs

Watch `t3_thread_read` with `view: "activity"`; judge the frame, not the
clock.

- Right goal, drifting — one correction with `t3_thread_send` `mode: "auto"`.
  Ignored — stop the thread: a second correction makes the brief a moving
  target. Delivered isn't done.
- Your brief's frame, scope or premise was wrong — `t3_thread_interrupt` and
  a new thread with a fixed brief.
- New circumstances (the owner changed the task, a neighbour edited the zone)
  — tell at once what changed, what it changes and what stands; `mode:
  "restart"` if what the agent read is still useful.
- Stalled with a question — `t3_pending_request`: `list`, then `respond`.
  Gemini accepts only an offered option, and `respond` doesn't check: answer
  with an option's value as `read` shows it, or the agent gets "User
  Skipped". When no option fits exactly, answer with the nearest and right
  after send the difference with `t3_thread_send` `mode: "auto"`: the agent
  resumes from the bare option at once (Codex, 2026-11-03). Command approvals
  only the owner gives, in the app. Stalled without a question — interrupt.

## When the turn has finished

`completed` means the turn ended, not that the work is right. The final
message: `~/.t3/bin/t3 thread show '<threadId>' --messages 1` (plain text;
`~/.t3/bin` isn't on PATH). Acceptance is `1orchestration`'s; a thread adds:

- the final message may report an earlier task as done — check a doer's diff
  against the brief and every message you sent;
- the `checkpoint` entry lists every changed file in the folder, neighbours'
  included, and misses files outside it;

## When continuing

A follow-up, a repair, the next task on the topic go to the same thread: it
remembers what it read. Send it with `run_in_background: true`:

```bash
~/.t3/bin/t3 thread send '<threadId>' - --wait <<'EOF'
<message>
EOF
```

Exit 0 — the output is the answer; 1 — the turn failed or was cancelled, the
output is only the error and the agent's text before it is in
`t3_thread_read`; 2 — the agent asked a question. The command queues behind a
running turn and never steers it; after a T3 restart it errors — wait with
the watcher on the `threadId`.

A new round in a thread whose `itemCount` is in the hundreds (a 636-item
Codex thread checked an old port against an old spec), or stale context:
`t3_thread_send` with `freshContext: true`, which starts the agent without
the thread's earlier context (per its description, not tried), then the
watcher on the `threadId`; or a new thread. An independent view or another
family — a new thread: `t3_thread_configure` across providers passes only a
selection of messages, while a new model or effort within a provider keeps
the conversation.

A thread idle for the days in `sidebarAutoSettleAfterDays`
(`~/.t3/userdata/settings.json`; the owner's 1 on 2026-11-09, default 7), or
whose pull request merged or closed, is settled: it leaves `t3_thread_list`
(`settled: true` finds it, and an archived or settled thread reads in full by
`threadId`). Per the docs, T3 deletes a settled thread's worktree only when
the owner turned on Settings → Worktrees → Cleanup (off by default), and then
by default with ignored files like `.env`.

## When the `t3` server fails

| What you see | Move |
| --- | --- |
| no `mcp__t3__*` tools | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3773/mcp`: `401` — alive, check this environment's sign-in, then a fresh session; connection error — ask the owner to open T3 |
| `capability_denied`, or `runtime_mode_escalation_denied` on launch | sign-in expired (30 days per the docs), is read-only, or allows less than `full-access` — a new sign-in defaults to Auto: the owner runs `claude mcp login t3` and picks Full access |
