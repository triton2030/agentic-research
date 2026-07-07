# Gemini MCP

Small repo-contained MCP server that exposes Gemini as an explicit controlled
peer agent.

This repo-contained MCP server is registered in Codex as `gemini-mcp`. It does
not edit `~/.claude` or `~/.gemini`.

Only account-backed CLI backends are supported. API/SDK/Vertex routes are not
fallbacks for this bridge.

- Antigravity CLI backend model label: `Gemini 3.5 Flash (High)`
- legacy Gemini CLI model: `gemini-3.1-pro-preview`
- thinking level: `high`
- preferred backend in Codex: authenticated Antigravity CLI through `agy`
- legacy Gemini CLI permission mode: `--approval-mode yolo` with
  `--skip-trust`
- verified local Antigravity CLI: `/Users/triton/.local/bin/agy` `1.0.0`
- verified local legacy Gemini CLI: `/Users/triton/.local/bin/gemini`
- optional env overrides: `GEMINI_MCP_BACKEND`, `GEMINI_MODEL`,
  `GEMINI_THINKING_LEVEL`

## Tools

- `gemini_status` reports the requested/effective backend, account CLI auth
  surfaces, model, thinking level, exact CLI command/version, CLI permission defaults,
  included directories, and server CLI timeout without making a network call.
- `gemini_ask` prefers an authenticated Antigravity CLI in `auto` mode, or uses
  it explicitly with `GEMINI_MCP_BACKEND=antigravity`. This is the path for
  Gemini 3.5 Flash under Google One / individual Antigravity accounts. Empty
  `text` is treated as an error, not a successful Gemini answer.
- `gemini_run`, `gemini_peek`, `gemini_observe`, `gemini_wait`,
  `gemini_kill`, `gemini_result`, and `gemini_cleanup_runs` manage long Gemini
  CLI or Antigravity CLI runs with repo-local logs, activity summaries, stop
  control, and chat-ready relay text. Use `gemini_ask` for short calls and
  `gemini_run` when a task may need trajectory checks or manual stop.
- `gemini_run` accepts `useTmux: true` for long CLI sessions that should
  survive MCP client/server churn. `tmux` is optional for normal calls, but on
  this machine it is installed and verified with `tmux -V`.

## Managed Runs And Tmux

Normal managed runs use a child process and repo-local `runs/<run_id>/` logs.
`tmux` is opt-in and only for long Gemini CLI sessions that should survive MCP
client or server churn.

When `useTmux: true` is set:

- the server creates a detached session named `gemini-mcp-<run_id>`;
- the pane waits on a `tmux wait-for` start channel before Gemini starts;
- the server attaches `tmux pipe-pane -o` to `tmux-pane.log`, then releases the
  pane to run Gemini;
- stdout and stderr still go to `stdout.log` and `stderr.log`;
- completion writes `exit-code.txt` and signals a `tmux wait-for` done channel;
- `gemini_peek` can include a live `tmux_capture` from `capture-pane`;
- `gemini_kill` only calls `tmux kill-session` for the saved session name.

`gemini_wait.timeoutMs` waits for a report or the tmux done channel. It does not
kill Gemini, and it is separate from any MCP client timeout. If the wait times
out but the tmux session is still alive, use `gemini_observe`, `gemini_peek`, or
`gemini_kill`.
After any paid/long Gemini agent run, confirm the final status is terminal and,
for tmux runs, that `tmux has-session -t <tmux_session>` no longer finds the
saved session. If you launched the MCP server as a direct stdio process,
confirm the matching `node .../experiments/gemini-mcp/src/server.js` process
exits after the client closes. A `server.js` process held by Codex app-server is
an active MCP transport, not a Gemini model run; do not broad-kill it. Only kill
by saved run/session/server identity; never kill broad Gemini or tmux processes
by name.

`tmux` control mode and `remain-on-exit` are intentionally not used in this v1:
the server needs durable logs and conservative kill behavior, not a full
terminal-control integration or persistent dead panes.

## Long-Run Observation

`gemini_peek`, `gemini_observe`, `gemini_wait`, and `gemini_result` include an
`activity` object:

- `elapsed_seconds`, log line counts, and `next_cursor`;
- recent stdout/stderr trace and tool-like log lines;
- `tmux_capture_available` and the latest visible output when tmux is active;
- a `stop_hint` that points back to `gemini_kill` while the run is live.

This is an observable trace, not private chain-of-thought. Use it to check
whether Gemini/Antigravity is reading the right surface, looping, blocked, or
worth stopping.

## Account-Backed Setup

This is the default and preferred path. It spends the logged-in Google
One / Antigravity account quota, not `GEMINI_API_KEY` / `GOOGLE_API_KEY`.

```bash
export GEMINI_MCP_BACKEND=antigravity
export ANTIGRAVITY_CLI_PATH=/Users/triton/.local/bin/agy
```

CLI child processes strip `GEMINI_API_KEY`, `GOOGLE_API_KEY`,
`GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_GENAI_USE_VERTEXAI`,
`GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION` from their environment, so
a stray shell variable cannot silently move an account run onto paid API
credentials.

Local Gemini CLI OAuth is still available as a legacy account-backed path:

```bash
export GEMINI_MCP_BACKEND=cli
```

Antigravity shells out to `agy -p ... --print-timeout ...`.
`includeDirectories` map to repeated `--add-dir` flags. Antigravity's current
CLI exposes the model through its own configured model picker rather than a
stable per-call MCP model flag; on this machine it is verified as
`Gemini 3.5 Flash (High)`.

For read-only review, leave `approvalMode` unset. For an explicitly approved
write run, pass `approvalMode: "yolo"` and constrain `cwd` plus
`includeDirectories` to absolute allowed folders; this maps to
`--dangerously-skip-permissions` for that one Antigravity call. Do not set this
as a global default.

Optional overrides:

```bash
export GEMINI_MODEL=gemini-3.1-pro-preview
export GEMINI_THINKING_LEVEL=high
export GEMINI_CLI_PATH=/opt/homebrew/bin/gemini
export GEMINI_CLI_APPROVAL_MODE=yolo
export GEMINI_CLI_INCLUDE_DIRECTORIES=/Users/triton,/Volumes/Research
export GEMINI_CLI_TIMEOUT_MS=50000
export ANTIGRAVITY_CLI_PATH=/Users/triton/.local/bin/agy
```

`GEMINI_CLI_TIMEOUT_MS` and `gemini_ask.timeoutMs` control the server child
process. Codex or another MCP client can still have its own shorter timeout;
report which layer timed out.

For managed runs, `gemini_wait.timeoutMs` controls only how long the MCP client
waits for a report. It does not kill the underlying Gemini process or tmux
session. Use `gemini_kill` when the run is looping or should stop.

Run logs live in `runs/<run_id>/` and are ignored by git. Treat `prompt.txt`,
`command.json`, `stdout.log`, and `stderr.log` as sensitive.

## Local Checks

```bash
npm run smoke
```

The smoke test verifies MCP startup and the missing-key error path. It does not
make a live Gemini API call; it uses a fake Gemini CLI for CLI-backend,
managed-run, and tmux coverage.

## Run MCP Server

```bash
npm run mcp
```

Manual Gemini CLI registration, if you choose to test it there:

```bash
gemini mcp add gemini-ask node /Users/triton/Documents/GitHub/agentic-research/experiments/gemini-mcp/src/server.js
```

For Codex or Claude, register the same command in the relevant MCP config only
after the local smoke test passes and the use case proves useful. The Codex
registration for this workspace already uses the command above.
