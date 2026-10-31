---
name: 1t3
description: >-
  Use when work goes to a T3 Code thread — launch, wait, follow-up, close —
  when subscription limits matter, or audio, video or PDF needs Gemini. Whom
  to call and with which model: 1orchestration.
---

# T3 Code threads

## Context

The owner runs the T3 Code app: threads of Codex, Gemini, Muse and Grok on
his subscriptions, which he watches in the app. Its MCP server is `t3` here
and `t3-code` inside a thread; the tools describe themselves, and
`orchestrator_capabilities` is the model catalog. Whom to call, with which
model and effort, is `1orchestration`'s.

T3 does little for the caller. It doesn't wake you when a turn ends, doesn't
know which agent launched a thread, doesn't sandbox the agent, doesn't check
the model name, and a failed turn just stops. The rules below close these
gaps. In commands, `<skill-dir>` is the folder this file was read from.

## Goal

Every thread's answer is read and accepted from disk; from the title the
owner sees what his quota went on; other agents' threads stay untouched.

## When launching

```json
{
  "title": "Codex gpt-6.1-sol/max · doer · <gist>",
  "projectId": "<id>",
  "runtimeMode": "full-access",
  "modelSelection": {
    "instanceId": "codex",
    "model": "gpt-6.1-sol",
    "options": [{"id": "reasoningEffort", "value": "max"},
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
- Always set `runtimeMode`: otherwise the project default applies, and at an
  approval level the thread waits for consent nobody gives.
- Codex: `serviceTier: "default"` — the owner does not pay for Fast
  (31.10.2026); changing it mid-turn interrupted the turn.
- The model name isn't validated: a wrong one fails the first turn within
  seconds with `does not exist or you lack access`. The model an agent names
  in its reply proves nothing.
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

## When writing the brief

A thread has no sandbox: only the brief's words set boundaries. Every brief's
Boundaries carry:

> Don't commit unless asked. Don't touch or revert other people's edits.
> Don't start other agents, workflows or new threads unless asked. This brief
> and every later message in this thread are written by an agent: don't
> record them as the owner's words.

Agents that load the owner's skills act on them otherwise: Muse once started
seven child agents for six files, Codex nearly saved an agent's correction
as the owner's words. A Gemini brief adds "If something fails, record the
exact error and stop; don't look for workarounds" — without it Flash spent
four minutes searching the home folder. Name the project rules the agent
needs: Muse follows `AGENTS.md` himself, Gemini Flash did not, the others
weren't checked. Ask a reader for `path:line` and verbatim quotes. Don't
point agents at files with keys: Meta, Google and Cursor get all they read,
and per the docs Meta may train on it by default.

## Providers

| | Can't | Writes outside the folder | Owner's skills | Message into a running turn |
| --- | --- | --- | --- | --- |
| Muse | open PDF, audio, video | yes | with his personal rules | taken into the same turn |
| Gemini | hear or see — media go to the script below; its tools read and write only inside the project folder — other folders go to the script with `--add-dir` | only via shell | no | cancels and restarts; did the first correction halfway |
| Grok | X search; audio, video, PDF by its tool description | yes | skills only | not measured |
| Codex | native diff review, reading your transcript — the bridge `~/Documents/GitHub/agentic-research/experiments/codex-bridge` does | yes | with his personal rules and a tool that calls Claude | taken into the same turn |

- Claude threads are launched only from Codex; from Claude Code use your own
  subagents.
- Argon is expensive and has its own weekly quota: text writing stays on
  `gemini-3.8-flash-high`. Flash asserts where sources are silent.
- Grok finds recent events only by web search — ask for dated sources. A long
  Grok turn writes two to five full answers in a row; the last one counts.
- Muse `muse-wonder-full-1.0` at `xhigh`: an edit with tests took two
  minutes, an audit of several files about nine.

## When waiting

A finished turn won't wake you. A short turn: `t3_thread_wait` with
`timeoutMs` at most 55000 (the client aborts three minutes). A long one: the
watcher in the background (`run_in_background: true`) with the launch's
`runId`, or the `threadId` to follow its latest turn:

```bash
bash "<skill-dir>/scripts/wake_on_done.sh" '<runId or threadId>'
```

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
  Skipped". Command approvals only the owner gives, in the app. Stalled
  without a question — interrupt.

## When the turn has finished

`completed` means the turn ended, not that the work is right. The final
message: `~/.t3/bin/t3 thread show '<threadId>' --messages 1` (plain text;
`~/.t3/bin` isn't on PATH). Acceptance is `1orchestration`'s; a thread adds:

- the final message may report an earlier task as done — check a doer's diff
  against the brief and every message you sent;
- the `checkpoint` entry lists every changed file in the folder, neighbours'
  included, and misses files outside it;
- an auditor, adviser or reader leaves `git status` as it was; if it
  changed, the agent edited against the brief or a neighbour wrote nearby.

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

A new thread instead: a new round in a thread whose `itemCount` is in the
hundreds (a 636-item Codex thread checked an old port against an old spec),
an independent view, stale context, or another family —
`t3_thread_configure` across providers passes only a selection of messages,
while a new model or effort within a provider keeps the conversation.

Per the docs, a thread idle for three days or with a merged pull request is
settled: it leaves `t3_thread_list` (`settled: true` finds it, and an
archived or settled thread reads in full by `threadId`), and cleanup may
delete its worktree with ignored files like `.env`.

Others' threads: read freely; message, interrupt, archive or pin only at the
owner's request.

## When quota matters

Before big work on another subscription, after a quota refusal, and at the
start of a session that will delegate a lot:

```bash
python3 "<skill-dir>/scripts/limits.py"
```

It shows Codex, Gemini with Argon separately, Claude on the Google
subscription and Muse; the Muse check spends one minimal request, `--only
codex,google` is free. Grok's quota is invisible; the Claude Code
subscription is `mcp__ccd_session_mgmt__get_usage`. If the remainder won't
cover the plan, tell the owner and suggest a subscription with room. Codex's
free resets are the owner's to spend. Claude on the Google subscription is a
reserve he wants spent: `scripts/gemini.py --model claude-opus-5-5-high`
reads, summarizes and drafts when a brief and a folder are enough, and
searches the web with `--full`; it is no independent view for a Claude
caller.

Audio, video and PDF: [references/gemini-media.md](references/gemini-media.md).

## When the route fails

| What you see | Move |
| --- | --- |
| no answer | tell the owner it didn't answer and why; never substitute your own or another model's |
| no `mcp__t3__*` tools | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3773/mcp`: `401` — alive, check this environment's sign-in, then a fresh session; connection error — ask the owner to open T3 |
| `capability_denied` | sign-in expired (30 days per the docs) or is read-only: the owner runs `claude mcp login t3` and picks full access |
| `thread_credential_required` | the tool works only inside a thread (`preview_*`, `device_*`, `html_render`, `delegate_task`, `t3_worktree_status`): give it to a thread as a task |
| model missing even with `search`, or `does not exist or you lack access` | the model left the subscription; the owner picks a replacement |
| Cursor: `not included in your weekly usage` | the model is outside the owner's plan, as GLM 5.3 Flash |
| Grok: `repeated resume attempts made no progress` | the full answer is usually already in the feed: take the last one, ask for more in the same thread |
| Grok: a transport error such as `WritableIterable is closed` | no answer in the feed — only an opening line and the error, neither is the answer: ask to continue in the same thread |
| `usage_limit`, thread Limited | work on disk stays; tell the owner when the quota resets; a message after the reset continues the thread and cancels a resume he scheduled |

T3 docs: repository `pingdotgg/t3code`, folder `docs/`; not local.
