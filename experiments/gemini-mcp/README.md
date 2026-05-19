# Gemini MCP

Small repo-contained MCP server that exposes Gemini as an explicit controlled
peer agent.

This repo-contained MCP server is registered in Codex as `gemini-mcp`. It does
not edit `~/.claude` or `~/.gemini`.

Defaults follow the current Google docs for the strongest Gemini reasoning
path:

- model: `gemini-3.1-pro-preview`
- thinking level: `high`
- backend: authenticated Gemini CLI when available
- CLI permission mode: `--approval-mode yolo` with `--skip-trust`
- verified local CLI: `/Users/triton/.local/bin/gemini` `0.40.0`
- optional env overrides: `GEMINI_MODEL`, `GEMINI_THINKING_LEVEL`

## Tools

- `gemini_status` reports the requested/effective backend, visible auth modes,
  model, thinking level, exact CLI command/version, CLI permission defaults,
  included directories, and server CLI timeout without making a network call.
- `gemini_ask` uses the authenticated Gemini CLI as the default full-agent
  backend when available. That CLI can read files, use `--include-directories`,
  call web tools, load extensions, use MCP servers, and run in `yolo` approval
  mode. SDK/Vertex paths stay available for intentionally bounded API calls.
  Empty `text` is treated as an error, not a successful Gemini answer.
- `gemini_run`, `gemini_peek`, `gemini_wait`, `gemini_kill`,
  `gemini_result`, and `gemini_cleanup_runs` manage long Gemini CLI runs with
  repo-local logs and chat-ready relay text. Use these when observation,
  stop/retry control, or timeout diagnosis matters.
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
out but the tmux session is still alive, use `gemini_peek` or `gemini_kill`.
After any paid/long Gemini agent run, confirm the final status is terminal and,
for tmux runs, that `tmux has-session -t <tmux_session>` no longer finds the
saved session. If you launched the MCP server as a direct stdio fallback,
confirm the matching `node .../experiments/gemini-mcp/src/server.js` process
exits after the client closes. Only kill by saved run/session/server identity;
never kill broad Gemini or tmux processes by name.

`tmux` control mode and `remain-on-exit` are intentionally not used in this v1:
the server needs durable logs and conservative kill behavior, not a full
terminal-control integration or persistent dead panes.

## Setup

Supported SDK paths:

```bash
npm install
export GEMINI_API_KEY=<your_api_key>
```

`GOOGLE_API_KEY` is also supported and takes precedence when both variables are
set, matching the Google GenAI SDK behavior.

Vertex AI without an API key:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your_project_id>
export GOOGLE_CLOUD_LOCATION=global
gcloud auth application-default login
```

Local Gemini CLI backend, for machines already authenticated with Gemini CLI:

```bash
export GEMINI_MCP_BACKEND=cli
```

`gemini_ask` auto-detects this backend whenever `~/.gemini/oauth_creds.json`
exists, before SDK/API-key backends. This path shells out to the exact CLI path
reported by `gemini_status`, with `--approval-mode yolo` and `--skip-trust`. On
this machine the server prefers `/Users/triton/.local/bin/gemini` when present;
`/opt/homebrew/bin/gemini` is older here and should be selected only by an
explicit `GEMINI_CLI_PATH`.

Optional overrides:

```bash
export GEMINI_MODEL=gemini-3.1-pro-preview
export GEMINI_THINKING_LEVEL=high
export GEMINI_CLI_PATH=/opt/homebrew/bin/gemini
export GEMINI_CLI_APPROVAL_MODE=yolo
export GEMINI_CLI_INCLUDE_DIRECTORIES=/Users/triton,/Volumes/Research
export GEMINI_CLI_TIMEOUT_MS=50000
```

For Gemini 3, prefer leaving `temperature` unset so the API default is used.
The Google docs warn that lowering temperature can degrade complex reasoning.

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
