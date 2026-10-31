---
name: 1t3
description: >-
  Use when work goes to a T3 Code thread — launch, wait, follow-up, close —
  when subscription limits matter, or audio, video or PDF needs Gemini. Whom
  to call and with which model: 1orchestration.
---

# T3 Code — agents for Claude Code and Codex

## Context

The owner runs the T3 Code app. It hosts threads of agents from several
families on his subscriptions: Codex, Claude, Gemini, Muse and Grok. Its MCP
server is connected to Claude Code as `t3`, loaded through tool search; an
agent inside a thread sees the same server as `t3-code`. The owner watches
threads in the app. Runs spend those subscriptions, not your context.

The server's tools describe themselves, and the model catalog is
`orchestrator_capabilities`. This skill adds only what they don't say:
measured behaviour of threads and providers, the owner's rules for threads,
and scripts. Whom to call, with which model and effort, is decided by
`1orchestration`.

In commands below, `<skill-dir>` is the absolute path of the folder this
`SKILL.md` was read from, usually `~/.claude/skills/1t3`.

## Task

Launch and run T3 Code threads, send audio and video to the script, and close
out each answer.

## Goal

From the thread title in T3 Code the owner can tell what his quota was spent
on. Other agents' threads are the same after your work as before it.

## What each agent in a thread can't do

| Agent | Limits |
| --- | --- |
| Muse | can't open PDF, audio or video. `muse-wonder-full-1.0` at `xhigh`: a small edit with tests took two minutes, an audit of several files about nine |
| Gemini | in a thread can't hear or see: audio, video and PDF go to the script below. Effort is part of the model name. Argon has its own weekly quota, separate from Flash, and is expensive: the owner keeps writing, editing and shortening text on `gemini-3.8-flash-high`. Flash is confident where it is wrong, so audit and route choice are not its work |
| Grok | web search only, no X search; its read tool takes text and images, not audio, video or PDF. It finds recent events only through web search: ask for dated sources |
| Codex | no native diff review and no reading of the caller's transcript: for those the Claude bridge `~/Documents/GitHub/agentic-research/experiments/codex-bridge` |
| Claude | only Codex launches Claude threads — [how](references/t3-code.md#claude-in-a-thread); from Claude Code use your own subagents |

Audio and video go only to the script. Gemini in a thread is a different
Google agent that can't hear or see: it gets media as raw bytes and spends
minutes hunting for a workaround across the disk. Only the Antigravity CLI
hears and sees, hence `scripts/gemini.py`; it defaults to Flash, and
`--model gemini-4-argon-high` switches it to Argon. Measured on Flash; Argon
was not tried with media. How to call the script and check a transcript —
[references/gemini-media.md](references/gemini-media.md).

The owner's Google subscription includes Claude Opus and Sonnet with a quota
separate from Gemini, and he wants that quota spent too: the script with
`--model claude-opus-5-5-high` reads, summarizes, drafts and searches the web
when a brief and a folder are enough. It is not an independent view from
another family when the caller is Claude.

## When writing the brief

How to write a brief is `1orchestration`'s; a thread adds the following.
Muse follows the project's `AGENTS.md` himself; Gemini Flash did not in a
probe, Argon wasn't checked; Grok receives the root `AGENTS.md`, but following
it wasn't checked — name the project rules they need in the brief. Ask a
reader for `path:line` and verbatim quotes, so you can check the answer.

A thread has no sandbox: Muse and Grok write outside the working folder,
Gemini does through shell commands. Only the brief's words set boundaries,
and nothing appends rules to it. Put these shared rules into every brief's
Boundaries:

> Don't commit unless asked. Don't touch or revert other people's edits.
> Don't start other agents, workflows or new threads unless asked. This brief
> and every later message in this thread are written by an agent: don't
> record them as the owner's words.

The last two rules matter for agents that load the owner's skills: Muse and
Codex together with his personal rules, Grok without them, Claude with his
whole Claude Code setup. After reading someone else's skill, Muse once
started seven child agents for a question about six files. Codex in a probe
read the quote-saving skill and was about to save an agent's correction as
the owner's words; its tools include calling Claude. Add to a Gemini brief:
"If something fails, record the exact error and stop; don't look for
workarounds." With that line Flash stopped at refusals; where a brief only
asked to record the error, it spent four minutes writing a speech recognizer
and searching the whole home folder.

Everything the agent reads goes to Meta, Google or Cursor, so don't point it
at files with keys or passwords.

## When launching a thread

`t3_thread_launch` arguments; `instanceId` is the catalog's
`providerInstanceId`, and `options` is a list of `{id, value}` whose ids the
catalog names per model (Grok's effort is `reasoning_effort`, Gemini's is in
the model name):

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

- `title`: `<agent> <model>/<effort> · <role> · <gist>`, the gist in a few
  words without paths: the title is how the owner sees where his quota went.
- Codex: always set `serviceTier` to `default` (Standard in the app): the
  owner does not pay for Fast (31.10.2026). Changing it on a running thread
  interrupted the turn.
- Always set `runtimeMode`. Without it, since T3 Code 0.1.3 the thread gets
  the project's default permission level (per the change description); at an
  approval level it waits for consent on every command, and nobody is there
  to give it (per T3 Code docs).
- The thread works in the project root, on top of uncommitted edits and next
  to other threads, yours and others'. Before a writing thread, check
  `t3_thread_list` for the project with `statuses: ["running"]`: other agents
  of the owner may have started threads. Give it a zone nobody else edits, or
  a separate copy: `workspaceStrategy` of type `worktree` with `baseRef`.
  Ignored files such as `node_modules` don't reach the copy either, and a
  project's `runOnWorktreeCreate` script did not run for a thread launched
  through MCP: put the setup command into the brief.

T3 Code doesn't know which of the owner's agents launched a thread: all
Claude Code sessions and their subagents sign in as one client and see each
other's threads, and titles look alike. So the `threadId` from the launch
response is the only proof the thread is yours; keep it until the work ends.
After launching, give the owner the thread's `link` from the response with
the role and task.

## When waiting for a turn to end

A finished thread won't wake you. Wait out a short turn with `t3_thread_wait`,
`timeoutMs` at most 55000: the client aborts a three-minute wait with an
error. For a long turn, start the watcher with the `runId` from the response:

```bash
bash "<skill-dir>/scripts/wake_on_done.sh" '<runId>'
```

It reads the turn's status from T3 Code's database every three seconds, spends
no tokens, and exits when the turn ends or the agent asks a question. In
Claude Code, set `run_in_background: true`: the background command's exit
wakes the main session. In two probes subagents waited on the turn with
`t3_thread_wait` instead; a subagent can do the same. In Codex, start it with
`exec_command` and a short `yield_time_ms`, keep the `session_id` and collect
the result with `write_stdin`; this doesn't promise an automatic wake-up. Do
independent work while it waits, then keep waiting until you have read the
thread's result or established a blocker.

A follow-up message doesn't need the watcher: the send command brings the
answer back — see "When continuing the conversation".

## While a turn runs

`t3_thread_read` with `view: "activity"` shows what is happening. Judge by
the frame, not by elapsed time:

| What you see | Move |
| --- | --- |
| steps follow the brief | nothing |
| right goal, but the agent drifted | one correcting message |
| wrong frame, scope or premise — your brief was wrong | `t3_thread_interrupt` and a new thread with a fixed brief |
| steps stall: the agent asked a question | "When the agent asks a question" |
| steps stall without a question | `t3_thread_interrupt` |

Send a message into a running turn with `t3_thread_send`, `mode: "auto"`.
Muse takes it into the same turn; Gemini cancels the turn and restarts with
the correction, keeping what is already on disk. Delivered isn't done: in a
probe Gemini renamed a function as asked and left the old name beside it.

Correct course once. If the next steps still ignore the correction, stop the
thread: a second correction of the same drift turns the brief into a moving
target.

New circumstances are different — the owner changed the task, a neighbour
edited a file in the agent's zone: report them at once, even when the agent is
on track. The message says what changed, what that changes in the task, and
what in the brief still stands. If the frame itself changed under a sound
brief and what the agent has read is still useful, use `mode: "restart"`: it
stops the turn and starts over with the correction in the same conversation
(per the tool description).

Don't set `clientRequestId` unless you plan to retry the call. The key is
shared by all the owner's agents: in a probe a key already sent to a thread,
reused with different text, silently returned the old receipt and the new
message was never delivered. For a safe retry make the key unique: the
current session id (`CLAUDE_CODE_SESSION_ID` in Claude, `CODEX_THREAD_ID` in
Codex), the gist and a number.

## When the agent asks a question

Answer with `t3_pending_request`. Gemini accepts only one of the offered
options: free text reaches it as a skipped question, "User Skipped" (per the
T3 Code 0.1.3 change description). Command approvals the owner gives in the
app.

## When the thread has finished

`status: "completed"` means the turn ended, not that the work is right.
Read its final message with `~/.t3/bin/t3 thread show '<threadId>' --messages 1`:
one call of plain text, where `t3_thread_read` returns JSON and needs the
last item's position.

Acceptance is `1orchestration`'s; a thread adds two traps:

- The final message may report an earlier task as done: check a doer's diff
  against the brief and every message you sent, and rerun the check yourself.
  The `checkpoint` entry lists changed files in the whole working folder,
  neighbours' edits included, and misses files outside it.
- For an auditor, adviser or reader, `git status` after the thread equals the
  one before. If it changed, the agent edited against the brief or someone
  wrote nearby.

## When continuing the conversation

A follow-up on the answer, a repair of delivered work, the next task on the
same topic — send it to the same thread. It starts a new turn with the
previous memory: an agent that already researched the web or read the
project's files answers from what it read.

Exception: a new round of work in a long thread, where `itemCount` from
`t3_thread_read` is in the hundreds — give a new edit list or brief to a new
thread with a full brief, even on the same topic. On 2026-10-20 a Codex
thread of 636 items got such a round as a message — twelve edits and a new
server port; it checked the old port and reported against the old spec, and
the round had to be redone. A new thread did all twelve.

Take a new thread when you need an independent view — the continued one has
seen your reaction — or when the earlier context is stale. A different family
also gets a new thread: `t3_thread_configure` to another provider passes only
a selection of messages, without the previous agent's reasoning and tool
calls. Changing model or effort within the same provider keeps the
conversation (per T3 Code docs).

Send a message to the same thread with this command; in Claude Code with
`run_in_background: true`, in Codex like the watcher. It has not been tried
from Codex: if it fails there, use `t3_thread_send` and wait with the watcher
on the `threadId`.

```bash
~/.t3/bin/t3 thread send '<threadId>' - --wait <<'EOF'
<message>
EOF
```

The command waits for its own turn, prints the agent's answer and exits; no
watcher or `t3_thread_read` needed.

| Exit code | Next |
| --- | --- |
| 0 | the output is the agent's answer |
| 1 | the turn failed or was cancelled: the output is only the error; what the agent wrote before the failure is in `t3_thread_read` |
| 2 | the agent asked a question: "When the agent asks a question" |

The command doesn't touch a running turn: the message queues as the next
turn; correcting a running turn is `t3_thread_send` only. A T3 Code restart
breaks the command's connection and it exits with an error; T3 continues the
thread in a new turn — wait for it with the watcher on the `threadId`.

If another session will return to the thread, write its `threadId` into the
work note or handoff: by title `t3_thread_list` finds look-alikes, and only
the first message — your brief — tells whose a thread is.

## When you see another agent's thread

Read other threads when you need their context. Messages, interrupts, archive
and pinning in someone else's thread — only at the owner's request: another
agent runs it, and your message becomes a correction it doesn't expect.

## When to check remaining quota

Other subscriptions run out silently: the thread fails mid-work and you redo
it. Check before big work on another subscription — several threads, a top
tier, a long run — after a quota refusal, and at the start of a session where
you plan to work through other agents a lot.

```bash
python3 "<skill-dir>/scripts/limits.py"
```

Within a minute it shows what is left of Codex, Gemini, Claude on the Google
subscription, and Muse. The Muse check spends one minimal request: Muse
doesn't know its remainder without a model turn. Free: `--only codex,google`.
Grok's quota on the Cursor subscription is visible to neither the script nor
T3: with API-key sign-in T3 doesn't read it. The script doesn't see the
Claude Code subscription either; in the Claude app the tool
`mcp__ccd_session_mgmt__get_usage` shows it. When the calling Claude runs
low, Claude on the Google subscription is the reserve the owner wants spent.

If the remainder won't cover the plan, tell the owner and suggest a
subscription that has room. Codex's free quota resets, which the script
shows, are spent only by the owner.

## When you need more than a thread

The server's other tools — schedules, pull-request watching, forks and
queues, attachments, tidying the thread list — describe themselves. Browser,
phone simulator, rendered pages and child agents (`preview_*`, `device_*`,
`html_render`, `delegate_task`) and `t3_worktree_status` refuse you with
`thread_credential_required`: your client signed in from outside a thread.
If you need their result, give it to a thread as a task.

## When the route fails

- No answer — tell the owner the agent didn't answer and why. Don't put your
  own answer or another model's in its place.
- No `mcp__t3__*` tools or the server doesn't respond — run
  `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3773/mcp`.
  `401` means the server is alive; a connection error means it is down. The
  MCP server lives inside the T3 Code app: if the app is closed, ask the
  owner to open it. Server alive but no tools — check the calling
  environment's connection and sign-in, then a fresh session:
  [connection](references/t3-code.md#connection). Installing the skill
  doesn't connect MCP.
- Launch refused with `capability_denied` — the client's sign-in expired or
  is read-only. The owner fixes it; what to tell him is in the reference.
- A model isn't in `orchestrator_capabilities` even with `search`, or the
  turn failed with `does not exist or you lack access` — the model left the
  subscription. The owner picks a replacement.
- A Cursor turn failed with `not included in your weekly usage` — the model
  is outside the owner's plan: GLM 5.3 Flash fails this way.
- A Grok turn failed with `Agent turn stopped after repeated resume attempts
  made no progress` — the full answer is usually already in the feed: take
  the last one and ask for more in the same thread. Two of nine long Grok
  turns ended this way on 2026-10-20.
- A Grok turn failed with a Cursor transport error such as `WritableIterable
  is closed` — since T3 Code 0.1.3 this is how a turn ends when the
  connection drops after it began writing. The last message is then the
  error text, at most preceded by an opening line. Don't take either as the
  answer: ask for the continuation in the same thread (per the change
  description).
- A turn failed on a subscription limit — the app marks the thread Limited;
  work on disk stays. Tell the owner when the quota resets and check the
  remainder. A message to the same thread after the reset continues it; it
  cancels a continuation the owner scheduled.

Thread internals, agents' permissions, the `t3 thread` command and
measurements are in [references/t3-code.md](references/t3-code.md): open it
when a thread behaves differently from this text.
