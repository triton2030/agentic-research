# Claude Bridge Control

Repo-contained v1 bridge for running Claude Code from Codex with visible
profiles, local logs, MCP tools, restart-tolerant run state, chat-ready relay
text, and skill-read evidence.

The server can be registered in Codex as `claude-mcp`. It does not edit
`~/.claude` or Claude skills.

Default runs are account-backed Claude Code CLI runs on the `opus` alias with
`--effort max`, stream-json logs, and permission bypass. The bridge does not
add a tool allowlist for full-power profiles, so Claude receives the current
default CLI/MCP tool surface from its settings and plugins. The bridge strips
`ANTHROPIC_API_KEY` and `CLAUDE_API_KEY` from Claude child-process
environments, so a stray shell variable cannot silently move a review onto API
credits.

Warning: `prompt.txt`, `debug.log`, `stdout.log`, `stderr.log`, and
`events.ndjson` can contain secrets copied from prompts, tool output, or Claude
debug traces. Logs are repo-local and ignored by git; use cleanup for old runs.

## Install

```bash
npm install
```

## Local Checks

```bash
npm run doctor
npm run smoke
```

## Run MCP Server

```bash
npm run mcp
```

The global Codex MCP registration points to:

```bash
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/server.js
```

Registered Codex MCP name:

```bash
claude-mcp
```

## Profiles

- `normal` — default full-power Opus run with max effort and stream-json logs.
- `no-memory` — full-power run that disables Claude auto memory with
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- `no-skills` — full-power run that disables slash-command skills.
- `read-only` — max-effort exception that uses plan permission mode and
  read-oriented tools.
- `turbo` — compatibility alias for the full-power default.
- `skill-audit` — asks Claude to read a target skill/context and records
  evidence from tool/debug/stream logs.
- `streaming-observe` — full-power verbose observation profile for long runs.

## MCP Tools

- `claude_run`
- `claude_peek`
- `claude_observe`
- `claude_wait`
- `claude_kill`
- `claude_result`
- `claude_profiles`
- `claude_doctor`
- `claude_discover_skills`
- `claude_audit_skill`
- `claude_cleanup_runs`

The v1 surface is intentionally limited to `run / peek / observe / wait / kill
/ result / profiles / doctor / discover_skills / audit_skill / cleanup_runs`.

## Human-Observable Tmux Runs

For long tasks, pass `useTmux: true` to `claude_run`. The run still writes the
same repo-local files, but Claude runs inside a saved tmux session:

- `stdout.log` / `stderr.log` keep the structured output for final relay;
- `tmux-pane.log` and `tmux_capture` show the live terminal surface;
- `claude_observe` stays a thin window over logs, capture, elapsed time,
  warnings, and stop hints;
- `claude_kill` stops only the saved `tmux_session`.

This is the natural terminal model for hour-scale work. We watch what the
agent visibly prints and which tools/files appear in the stream; we do not
claim access to private chain-of-thought. For reliable final extraction, keep
asking Claude for a clear final answer section or marker in the prompt.

## Durable State

Each run writes `state.json` with `run_id`, `pid`, `started_at`, `cwd`,
command summary, log paths, status, exit code, and signal. `peek` and `result`
can reconstruct reports after MCP server restart. A previously running process
is marked `running_orphaned` only when the saved PID is alive and `ps` still
shows this run's `debug.log` or run directory. Otherwise it is `orphaned`.

`kill` after restart is conservative: it sends SIGTERM only when that same
fingerprint check passes.

After any paid/long Claude run, confirm the final status is terminal before
closing the conversation. If `result` still reports `running`,
`running_orphaned`, or `killing`, use `kill` and re-check. If you launched the
MCP server as a direct stdio process, confirm the matching
`node .../experiments/claude-bridge/src/server.js` process exits after the
client closes. For tmux runs, confirm the saved `tmux_session` is gone. A
`server.js` process held by Codex app-server is an active MCP transport, not a
Claude model run; do not broad-kill it. Never kill broad `claude`, tmux, or
bridge processes by name; only act through the bridge run id, saved session,
server path, and fingerprint.

## Chat Relay

MCP cannot push messages into the Codex chat by itself. It can only return tool
results to Codex. To make Claude's answer easy to paste into chat, `wait` and
`result` include:

- `chat_relay.text` — the final Claude answer without raw JSON.
- `chat_relay.markdown` — a chat-ready block prefixed with `Claude:`.
- `chat_relay.truncated` — true when the answer was shortened for chat.

`peek` supports incremental relay:

```bash
node src/cli.js peek --run-id "<run_id>" --cursor 0
```

It returns `next_cursor`, `relay_updates`, and `chat_relay.text`. Codex should
store the returned `next_cursor` and pass it into the next `peek` call to avoid
repeating already-relayed Claude text.

## Long-Run Observation

`claude_peek`, `claude_observe`, `claude_wait`, and `claude_result` include an
`activity` object for long runs:

- `elapsed_seconds`, `event_count`, and `last_event_at`;
- `recent_tool_trace` with observed tool/file/command events when Claude emits
  them;
- `recent_paths` and `recent_text` for trajectory checks;
- `tmux_capture_available` and `last_tmux_output` for tmux-backed runs;
- a `stop_hint` that points back to `claude_kill` when the run is still active.

This is an observable trace, not private chain-of-thought. Use it to decide
whether the run is reading the right files, looping, blocked, rate-limited, or
worth stopping.

## Cleanup

Dry-run by default:

```bash
node src/cli.js cleanup --days 14
```

Delete eligible old run directories only with confirmation:

```bash
node src/cli.js cleanup --days 14 --confirm
```

## Evidence Rule

The bridge does not treat Claude self-report as proof that a skill was read.
`claude_audit_skill` marks evidence as `passed` only when a tool/debug/stream
event points to the target path. Plain answer text without a read/tool signal is
reported as `unknown`.

## Official-Docs Controls

The runner exposes first-class fields for the current Claude Code CLI controls
that matter to bridge work:

- system prompt: `systemPrompt`, `systemPromptFile`, `appendSystemPrompt`,
  `appendSystemPromptFile`
- memory: `disableAutoMemory` or the `no-memory` profile
- MCP: `mcpConfig`, `strictMcpConfig`, `mcpTimeout`, `maxMcpOutputTokens`,
  `permissionPromptTool`
- model/effort: full-power profiles request `--model opus --effort max`
- permissions/tools: `tools`, `allowedTools`, `disallowedTools`,
  `permissionMode`, `allowDangerouslySkipPermissions`
- structured/agent controls: `jsonSchema`, `agent`, `agents`, `brief`,
  `inputFormat`, `replayUserMessages`
- context roots and startup resources: `addDir`, `pluginDir`, `pluginUrl`,
  `file`, `settingSources`, `settings`
- run control: `maxTurns`, `maxBudgetUsd`, `name`, `sessionId`, `resume`,
  `forkSession`, `noSessionPersistence`

Some official-doc flags can be ahead of the installed local CLI. Before a run,
the bridge checks support for version-sensitive fields such as `maxTurns`,
`systemPromptFile`, `appendSystemPromptFile`, `permissionPromptTool`,
`jsonSchema`, `agent`, `agents`, `pluginUrl`, `file`, and `inputFormat`; if the
installed `claude --help` does not advertise the flag, the run fails early with
a clear error.

`--dangerously-skip-permissions` is equivalent to Claude Code
`bypassPermissions`. Claude still applies its own protected-directory rules;
this bridge v1 does not add OS-level sandboxing.

Local baseline checked on this machine: native Claude Code CLI
`/Users/triton/.local/bin/claude` `2.1.144`. A lower-priority Homebrew cask
install may still exist and trigger Claude's multiple-install warning, but this
bridge resolves the native binary first unless `CLAUDE_BRIDGE_CLAUDE_BIN` is
set.
