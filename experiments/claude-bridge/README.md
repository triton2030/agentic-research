# Claude Bridge Control

Repo-contained v1 bridge for running Claude Code from Codex with visible
profiles, local logs, MCP tools, restart-tolerant run state, chat-ready relay
text, and skill-read evidence.

The server can be registered in Codex as `claude-mcp`. It does not edit
`~/.claude` or Claude skills.

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

- `normal` — default Opus run with stream-json logs.
- `clean` — tries Claude `--bare` with no slash commands and no session
  persistence; may be unsupported if local auth relies on keychain/OAuth.
- `no-memory` — disables Claude auto memory with
  `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- `no-skills` — disables slash-command skills.
- `read-only` — uses plan permission mode and read-oriented tools.
- `turbo` — full-power Opus run with dangerous permission skip.
- `skill-audit` — asks Claude to read a target skill/context and records
  evidence from tool/debug/stream logs.
- `streaming-observe` — verbose observation profile for long runs.

## MCP Tools

- `claude_run`
- `claude_peek`
- `claude_wait`
- `claude_kill`
- `claude_result`
- `claude_profiles`
- `claude_doctor`
- `claude_discover_skills`
- `claude_audit_skill`
- `claude_cleanup_runs`

The v1 surface is intentionally limited to `run / peek / wait / kill / result /
profiles / doctor / discover_skills / audit_skill / cleanup_runs`.

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
MCP server as a direct stdio fallback, confirm the matching
`node .../experiments/claude-bridge/src/server.js` process exits after the
client closes. Never kill broad `claude` or bridge processes by name; only act
through the bridge run id, server path, and fingerprint.

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
- memory: `disableAutoMemory` or the `no-memory` / `clean` profiles
- MCP: `mcpConfig`, `strictMcpConfig`, `mcpTimeout`, `maxMcpOutputTokens`,
  `permissionPromptTool`
- permissions/tools: `tools`, `allowedTools`, `disallowedTools`
- context roots: `addDir`, `pluginDir`, `settingSources`, `settings`
- run control: `maxTurns`, `maxBudgetUsd`, `name`, `sessionId`, `resume`,
  `forkSession`, `noSessionPersistence`

Some official-doc flags can be ahead of the installed local CLI. Before a run,
the bridge checks support for version-sensitive fields such as `maxTurns`,
`systemPromptFile`, `appendSystemPromptFile`, and `permissionPromptTool`; if
the installed `claude --help` does not advertise the flag, the run fails early
with a clear error.

`--dangerously-skip-permissions` is equivalent to Claude Code
`bypassPermissions`. Claude still applies its own protected-directory rules;
this bridge v1 does not add OS-level sandboxing.
