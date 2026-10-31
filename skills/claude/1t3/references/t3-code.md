# T3 Code under the skill

Measurements below come from T3 Code 0.0.46-nightly (2026-10-14) through
0.1.3-nightly (2026-10-24); on 2026-10-31 the server is 0.1.6-nightly and
they were not rechecked on it. "Per the docs" or "per the tool description"
means no live check. Since 0.1.3 (change #22732) a thread launched from
outside takes the project's default model and permission level, within the
sign-in level: set `runtimeMode` and `modelSelection` explicitly.

## Connection

The MCP server lives inside the app: `http://127.0.0.1:3773/mcp`. Claude Code
and Codex have it at user scope as `t3`. Their sign-ins are independent;
installing `1t3` doesn't register MCP. Without a running T3 Code there are no
tools. A session started before the server was connected may not get them:
check in a fresh session.

The owner approves each client's sign-in and picks its level. At read-only,
launching a thread is refused: `capability_denied … approved for read-only
access`. The owner signs in again from the calling environment
(`claude mcp login t3` or `codex mcp login t3`) and picks the needed level.
A thread gets no more than the sign-in level. Per the docs a sign-in lasts
30 days.

### Codex as the caller

Checked on 2026-10-18 on `codex-cli 0.163.0`:

```bash
codex mcp add t3 --url http://127.0.0.1:3773/mcp
```

The command saved the server and started OAuth itself; a separate
`codex mcp login t3` is needed only to finish or repeat the sign-in. On the
`Connect Codex` page the owner chose `Full access`, entered the Pairing code
from T3 → Settings → Connections and confirmed. The already open chat got no
tools; a fresh Codex process launched a `scratch` thread on
`gpt-6.1-sol/medium`, waited for `completed` and read the answer, without
Claude in between.

The first non-interactive `codex exec` stopped before launching:
`MCP tool call requires approval, but approval policy is never`. That is the
calling Codex refusing, not T3; `codex exec --approve-for-me` passed. Keep the
normal approval mode; signing in to T3 again doesn't fix this error.

### The Cursor provider

Grok reaches T3 through the `cursor` provider. The owner's account is Cursor
under the Grok brand, managed on grok.com; the Premium plan covers only Grok
models. A separate `grok` provider (model Grok Build) is in the catalog but
disabled and untested.

Checked on 2026-10-20 on T3 Code 0.1.1-nightly.20261020.3411:

- Sign-in works only through the "Cursor API key" field in the provider
  settings. Browser sign-in for an account without email isn't saved: "Could
  not save the Cursor sign-in" — the Cursor SDK sends `email: undefined` and
  T3's schema rejects it.
- `grok-4.7` answered correctly in a `scratch` thread, turn 8.5 s.
- `glm-5p3-flash` failed: "not included in your weekly usage. Buy credits or
  switch to a Grok model".

## The `t3 thread` command

Added in T3 Code 0.1.3 (change #22732). The app writes `~/.t3/bin/t3`, a
wrapper around the CLI inside the app; it isn't on PATH. Subcommands: `list`,
`start`, `send`, `show`. Per the change description, the command finds the
running server, signs in as a short-lived local MCP client revoked at exit,
and calls the same `t3_thread_launch`, `_send`, `_wait`, `_read`.

Measured on 2026-10-24 on 0.1.3-nightly.20261024.3604:

- `t3 thread list` from the project folder listed its threads in 2.6 s, with
  no key or owner approval.
- A Gemini Flash thread was launched through MCP, and while its first turn
  ran, `t3 thread send <id> "…" --wait` sent a second message. It queued; the
  command waited for exactly that turn and printed only its answer — 10 s,
  exit 0.
- A message via stdin (`-` and a heredoc with quotes and `$HOME`) arrived
  verbatim, exit 0.
- A fresh subagent following the skill sent its follow-up this way and read
  the answer from the output. The background command's exit didn't wake the
  subagent; it waited on the same turn with `t3_thread_wait`.

From the CLI code and help, not measured:

- `--wait` polls `t3_thread_wait` in 15 s slices with no overall limit. If a
  slice times out and the thread has an open agent question
  (`pendingRequestCount`), it exits 2. Any outcome other than `completed` is
  exit 1 with the turn's error text; the agent's answer is printed only for a
  completed turn (`finishRun`). A turn cancelled by a T3 restart is skipped
  by the server's `t3_thread_wait`, which waits for the continuation
  (`latestRestartContinuation`); but while T3 restarts the command's calls
  fail and it ends with an error, exit code unchecked.
- `send` only queues: it doesn't steer or interrupt a running turn, and it
  passes no `clientRequestId`.
- `start` has no effort, permission-level or `scratch` flags — only
  `--provider`, `--model`, `--title`, `--worktree`, `--branch`. Launching
  with effort and `full-access` stays with MCP.

## Server tools

On 2026-10-31 the server has 66 tools, and they describe themselves. Some act
as the calling thread and refuse an outside client with
`thread_credential_required`: measured that day for `device_list`,
`preview_status` and `t3_worktree_status`; `delegate_task`, `create_threads`
and `task_*` refused in earlier probes. An agent inside a thread gets the same
server as `t3-code` and can use all of them.

- `t3_thread_search` for an existing title returned nothing; `t3_thread_list`
  with `titleContains` found it.
- Watching a pull request polls it every two minutes.

## Several agents on one T3 Code

Measured on 2026-10-14:

- A Claude Code session and its subagent signed in as one client: their
  command ids share `client:02f7fbf2-…`. A thread launched by either gets
  `createdBy: "agent"` and `creationSource: "mcp"`; the thread doesn't store
  its author.
- `t3_thread_list` shows every agent's threads in the project. A subagent
  read a thread it hadn't launched to take its acceptance criteria.
- `clientRequestId` is shared. The same key on another thread is refused:
  `Command … was already handled for thread <A> and cannot be replayed for
  <B>`. The same key on the same thread with different text silently returns
  the old receipt with the old `messageId`; the new message isn't delivered.
  The `t3 thread` command signs in as its own client and passes no key.

Per tool descriptions, messages, interrupts and archive work on any thread in
the environment; an outside caller is limited only by its sign-in level.

## Codex in a thread

Measured on 2026-10-14, `gpt-6.1-sol` + `medium`, `full-access`:

- T3 Code runs Codex from `/opt/homebrew/bin/codex` (`codex-cli 0.162.1`);
  the Claude bridge `experiments/codex-bridge` runs it from the ChatGPT app (`0.162.0-alpha.17.2`).
  Different engines, updated by different routes.
- The Codex session log shows `model_context_window: 475000`. The T3 catalog
  has no window option.
- A mid-turn correction entered the same turn (`delivery: "steered"`) and was
  fully done. A task with an edit, tests and two images took four minutes.
- Images come from the built-in `image_gen.imagegen`: PNG 1254×1254 with
  alpha, saved to `~/.codex/generated_images/`; Codex copies it where told.
- Writing outside the working folder works.
- Codex loaded the owner's personal instructions and skills from `~/.codex`
  and the `t3-code` and `claude-mcp` servers' tools. It was about to save an
  agent's correction through `1chat-recall` as the owner's words; nothing was
  written only because the probe project had no quote corpus.
- A message to a finished thread started a new turn with memory: Codex named
  its own function without opening files. It parsed a Claude Code session
  transcript by path with `jq` and found the owner's first and last messages
  correctly — 35 seconds.
- T3 Code has no native diff review.

## Claude in a thread

For a calling Codex. From Claude Code, Claude isn't called as a T3 thread:
Claude Code uses its own subagents.

Provider `claudeAgent` (`"instanceId": "claudeAgent"`): Opus 5.5, Fable 5.1,
Sonnet 5.5, Haiku 5.5. Effort
goes in an option named differently from Codex and Muse:
`{"id": "effort", "value": "high"}`. Levels include `ultracode` — xhigh with
a multi-agent workflow.

Probe on 2026-10-19 from another project, `claude-opus-5-5` + `high`,
23-second turn:

- By the thread's answer, quoting instruction lines before reading files, it
  got the owner's whole Claude Code setup: `~/.claude/CLAUDE.md`, the
  project's root `AGENTS.md`, `MEMORY.md`, personal and plugin skills via the
  `Skill` tool, the project's agents.
- A folder's `AGENTS.md` arrived only with reading a file from that folder:
  the project's hook sends it, not T3 Code.
- A plugin skill is called by its full name: `mattpocock-skills:tdd`, not
  `tdd`.

## Grok in a thread

Provider `cursor`, model `grok-4.7`. Options: `reasoning_effort` — `low`,
`medium`, `high`, `xhigh`, default `high`; `fastMode` — on by default, effect
unknown; `contextWindow` — `256k` or `500k`, default `500k`.

Probe on 2026-10-20 in `agentic-research`, `high`; context facts come from
the thread's answer taken before any tool call:

- In context: Cursor's system prompt with a T3 block "you are running in T3
  Code through the Cursor harness, as grok-4.7"; the project's root
  `AGENTS.md`; four Cursor user rules, among them "commit only when asked".
  No `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md`.
- 138 skills, as paths; texts read on demand. Sources: `~/.claude/skills`
  (plus eight old snapshots from its `_backups/`), `~/.codex/skills`,
  `~/.agents/skills`, `~/.cursor/skills`, `~/.cursor/skills-cursor`.
- Tools: `Shell`, `Read`, `Write`, `StrReplace`, `Grep`, `Glob`; the `cursor`
  namespace with, among others, `Task` (child agents), `GenerateImage`,
  `WebSearch`, `WebFetch`; the `t3-code` MCP server with `delegate_task` and
  `t3_thread_launch`. No X search.
- `Write` wrote a file to `~/Library/Caches/`, `Read` read `/etc/shells`:
  reading and writing outside the working folder work. Shell outside the
  folder is unchecked: Grok ran `Write` and `Shell` in parallel, the command
  ran before the folder existed and failed; per the brief it didn't retry or
  work around.
- The turn listing its context took 112 s. A message to the finished thread
  started a new turn with memory; one web search took 31 s and gave two dated
  CoinDesk articles; both open, dates match.

Long turns on 2026-10-20 — nine reviewer threads of another session, 6–20
minutes each, per the T3 database:

- In seven of nine turns Grok wrote two to five full answers in a row, each
  17–26 thousand characters. The answer is the last one.
- Two turns ended `failed` with `provider_error`: "Agent turn stopped after
  repeated resume attempts made no progress"; the full answers were already
  in the feed. The Cursor SDK throws it when the connection dropped and the
  turn resumed twice without a new checkpoint. A message to the same thread
  ended `completed`. That the extra answers in successful turns come from the
  same resumes is an inference, not a measurement.
- With API-key sign-in T3 doesn't read the quota: in 0.1.1 code the answer is
  `unsupported` and "Cursor usage requires a CLI login or CURSOR_AUTH_TOKEN".

In T3 Code 0.1.3, per change descriptions, not measured:

- A Cursor turn whose connection drops after it wrote text ends `failed` with
  class `transport_error`. Before, it counted as finished and the answer was
  error text such as `Error: RetriableError: WritableIterable is closed`.
  Both messages stay in the feed — the opening line and the error (#23273).
- A Grok background command no longer holds the turn open when Grok never
  reports its completion (#22709).

## Project and working folder

- An outside caller must pass `projectId` or `scratch: true`.
- `t3_project_create` with `title` and `workspaceRoot` registers an existing
  folder without touching its files. With only `title`, T3 Code creates a git
  repository in `~/.t3/projects/<title>`.
- `scratch: true` gives the thread its own empty folder in `~/.t3/scratch/`.
- Without `workspaceStrategy` the thread works in the project root. Strategy
  `worktree` creates a separate worktree; uncommitted edits aren't copied.
  Measured 2026-10-30 on ten Codex threads: `{"type": "worktree", "baseRef":
  "<local branch>", "branch": "<new branch>", "startFromOrigin": false}` checks
  out the new branch from the local ref in
  `~/.t3/worktrees/<project>/<branch with / as ->`. Ignored files such as
  `node_modules` are absent. A project script with `runOnWorktreeCreate`
  (`t3_project_update`, `scripts`) did not run for a thread launched through
  MCP (measured once); put the setup command into the brief.
- Per the docs, T3 Code marks a thread settled after three idle days or a
  merged pull request. It leaves the normal `t3_thread_list` and is found
  with `settled: true`. Cleanup may delete such a thread's worktree; it keeps
  uncommitted edits by default but not ignored files like `.env`.

## Agents' permissions and context

| What | Muse | Gemini | Grok |
| --- | --- | --- | --- |
| permission levels | `full-access` and `approval-required` | all four | catalog doesn't limit; `full-access` checked |
| tool writes outside the working folder | allowed | refused: `Access to path … is denied. It is outside the workspace` | allowed |
| tool reads outside the working folder | not measured in a thread; under `muse exec` reads any file | refused: `Access to path … is denied. It is outside the allowed workspace directories` | allowed |
| shell commands outside the working folder | not measured | write and read | not measured |
| owner's personal rules and skills from Claude Code and Codex | loaded: 95 skills and personal instruction headers | not loaded | skills loaded, personal instructions not |
| project `AGENTS.md` | followed | not followed; whether loaded is unknown | loaded; following unchecked |
| commit unasked | didn't | didn't | didn't |

Per Muse Code docs, Muse can write a workflow itself and run up to eight
child agents; per T3 Code docs it also gets T3 Code's tools. Under
`muse exec` with others' skills in context it started seven child agents for
a question about six files.

Per Muse Code docs a user setting disables others' personal skills; the docs
don't name it and it wasn't tested. Antigravity takes its own shared skills
from `~/.gemini/config/skills` — per T3 Code docs.

## Model and effort

The catalog is `orchestrator_capabilities`; `search` finds models beyond its
short list. Older Gemini, Codex and Claude models are hidden in T3 Code
settings (`providerModelPreferences.*.hiddenModels`); Gemini 4 Argon came
later and is visible because it isn't hidden. Probe on 2026-10-20:
`gemini-4-argon-high` answered in a `scratch` thread in 18 seconds, 9 of them
thread setup.

| Muse tier | Measured |
| --- | --- |
| `muse-wonder-full-1.0` + `xhigh` | five-step task with an edit and tests — 130 s in a thread; audit of three files running scripts — 519 s under `muse exec` |
| `muse-wonder-1.0` + `high` | a question about one file — 15–40 s under `muse exec` |

A model name in the thread's reply only repeats the request; it doesn't
confirm the model. The launch doesn't validate the model name either: a thread
with a made-up model was created, and its first turn failed within two seconds
with `model … does not exist or you lack access`.

## Messages and continuation

- `mode: "auto"` starts an idle thread, steers a running turn or queues.
  `steer` is refused with `thread_not_sendable` while the thread prepares.
- Muse takes a message into the same turn: `delivery: "steered"`.
- Gemini cancels the turn — the feed shows `The request was cancelled by the
  client` — and restarts with the correction. In a probe it did the first
  correction halfway: renamed a function and kept the old name as an alias,
  which Muse's audit found. It did the second.
- A message to a finished thread starts a new turn with the previous memory
  and the same model: `delivery: "started"`.
- `t3_thread_configure` changes provider, model and options between turns.
  Per the docs, switching provider drops the previous agent's reasoning, tool
  calls and attachments: the new one gets a selection of messages. Changing
  model within a provider usually continues its session.
- A turn stopped by a subscription limit ends `status: "failed"` with error
  class `usage_limit`; the app marks the thread Limited — per 0.1.1 server
  code. The owner sets a continuation at reset with the Resume at reset
  button or the Auto-resume setting; a new message, archive or settled
  cancels it — per the docs.
- Archive: `t3_thread_organize` with `action: "archive"`, back with
  `"unarchive"`. An archived thread leaves `t3_thread_list` but reads in full
  by `threadId` (`archived: true`) — measured 2026-10-14.

## Waiting and reading

- `t3_thread_wait` with `timeoutMs` 58000 passes; the client aborts 180000
  with `The operation timed out`. That doesn't stop the thread.
- The watcher `scripts/wake_on_done.sh` reads `~/.t3/userdata/statev2.sqlite`
  read-only: turn status from `orchestration_v2_projection_runs`, agent
  questions from `orchestration_v2_projection_runtime_requests` (what
  `t3_pending_request` with `list` returns). Its `run_id` is the one launch and send
  return. Measured 2026-10-15: a Gemini turn ended 54 seconds after launch,
  the watcher woke the session 52 seconds into its wait. The schema is
  internal and may change with a nightly build; then the watcher exits with a
  message after a minute instead of hanging. Fallback: a background subagent
  repeating `t3_thread_wait` — 65 thousand `haiku` tokens for four minutes.
  A `t3 auth session issue` key isn't accepted by the MCP server:
  `invalid_mcp_credential`, measured 2026-10-15.
- Status `waiting` isn't an agent question. In 0.1.1 code it marks a turn
  whose provider finished while the checkpoint is still being saved:
  "`waiting` is provider-finished with checkpoint capture still pending". The
  watcher waits up to a minute for `completed`.
- During a T3 Code restart the database won't open for reading for a few
  seconds: `unable to open database file (14)`. The database is in WAL mode;
  a read-only connection didn't open a copy without its `-shm` file — that
  `-shm` disappears while T3 is closed is an inference. A restart cancels
  running turns (`cancelled`), and 9–13 s later T3 continues each in a new
  turn with the next `ordinal` and a `restartContinuationOfRunId` field; the
  setting `continueThreadsAfterServerUpdate` enables it — per the database
  and server code. The watcher waits up to a minute for the database and the
  continuation and follows the new turn.
- In an unattended session (`claude -p`, cloud) a background command without
  its own `timeout` lives 30 minutes — measured by the Claude bridge `experiments/codex-bridge`.
- `t3_thread_read` with `view: "messages"` returns messages; with `view:
  "activity"`, steps: commands with output, file reads and edits, reasoning.
  Long text is cut; the rest comes from the same call with `itemId` and
  `textOffset`.
- The `checkpoint` entry at the end of a turn lists changed files in the
  whole working folder with line counts. It doesn't tell authors apart and
  doesn't see files outside the folder.
- Per the docs, an agent question with fixed options holds the thread even at
  `full-access`; `t3_pending_request` `list` shows it,
  `respond` answers.
- A Gemini question accepts only one of its options. Since 0.1.3 (#22019) the
  server shows their values and `allowCustomAnswer: false`, but
  `t3_pending_request` `respond` doesn't validate the answer: free text reaches
  the agent as cancelled, "User Skipped". The answer is matched first against
  an option's value, then against a unique label. Per the change
  description, not measured.

## Media in a thread

Gemini: its read tool returned raw bytes for MP3 and MP4. It got a frame's
colours by parsing with `ffmpeg`, but not the speech. The script over `agy`
transcribed the same files verbatim in 29 seconds. Per T3 Code docs, an
attachment other than an image reaches the agent as a file path.

Muse under `muse exec`: PNG opens by reading the file; PDF, MP3, WAV and M4A
give `file is not valid UTF-8`; MP4 gives `the selected model does not
support video input`.

## Reading and web in a thread

Gemini in a project thread summarized seven files in 84 seconds: all seven
`path:line` addresses and quotes matched the files, and the working folder
didn't change. A second message asked for a file outside the project: Gemini
didn't open it, stopped per "don't look for workarounds" and answered in ten
seconds. Another thread took four minutes for six files: Flash reread file
endings to count lines.

It read a page with `read_url_content` and found another with `search_web`:
two items in 37 seconds, quotes with addresses.

## Data and quotas

Requests and files read go to Meta, Google and Cursor. Per the docs, the Meta
subscription has Contributor mode on by default: Meta may train on the
content; the owner changes the mode.

`scripts/limits.py` prints all remainders at once. Sources, measured
2026-10-14:

| Subscription | Where the script reads the remainder | Cost |
| --- | --- | --- |
| Codex | `account/rateLimits/read` of the `codex app-server` engine: windows, credits, free quota resets | free |
| Google: Gemini, Claude and GPT | `agy -p /usage`: week and five hours, separate for Gemini and for Claude with GPT; Gemini 4 Argon has its own week — since 2026-10-20 | free |
| Meta: Muse | `usage/read` of the `muse serve` protocol | one minimal request |
| Cursor: Grok | invisible to the script and to T3 with API-key sign-in; by GLM's refusal text the plan's quota is weekly | — |

For the owner, T3 Code shows Codex and Gemini remainders per the docs: Usage
→ Limits, or `/usage-limits` in a thread. Muse isn't there, in the docs or in
its driver. The Codex engine method `account/rateLimitResetCredit/consume`
spends a free reset; the script never calls it.

Muse's `usage/read` without a model turn in the same process returns an
empty `{}`: Muse reports the last thing it saw from the provider. So the
script makes a short turn on `muse-wonder-1.0` at `minimal`.

Claude Opus 5.5 and Sonnet 5.5 on the Google subscription are available only
through `agy`: the Antigravity provider in T3 Code doesn't show them. Probe
2026-10-14: answer in 6 seconds, spent from the "Claude and GPT models" line
of `agy -p /usage`.

## Not measured

The `approval-required` level, attachments, PDF in a
Gemini thread, creating a schedule, watching a pull request, thread branches,
`mode: "restart"` of `t3_thread_send`, switching provider in a thread,
continuing after a limit. For Grok: a mid-turn correction, shell outside the
working folder, PDF, what `fastMode` changes, a turn on an exhausted quota,
and audit quality on a real task. The `t3 thread` command from Codex.

T3 Code docs are in the `pingdotgg/t3code` repository, folder `docs/`:
`user/outside-agents.md`, `user/providers-muse.md`,
`user/providers-antigravity.md`, `orchestration-v2/orchestrator-mcp-server.md`.
