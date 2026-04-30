---
name: claude-mcp
description: Use when Codex should delegate to Claude Code through the Claude Bridge MCP/server with run/peek/wait/kill controls, profiles, logs, streaming observation, memory/skill/system-prompt control, or skill-read evidence; skip ordinary inline answers and one-off raw `claude` commands that do not need bridge control.
---

# Claude MCP

Use the Claude Bridge MCP/server instead of calling `claude` ad hoc when the
user needs repeatable Claude delegation, profile control, logs, streaming
milestones, kill/wait/peek control, skill-audit evidence, or MCP-compatible
operation. When the user wants Claude's answer, relay Claude's actual answer in
chat from `chat_relay` instead of summarizing raw JSON.

## Locate Bridge

- Bridge root:
  `/Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge`
- Registered Codex MCP name: `claude-mcp`.
- Prefer callable MCP tools when this server is available in the current Codex
  session.
- If the MCP tools are not available, use the repo-local CLI fallback:
  `node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js`.
- Do not edit global MCP config, `~/.claude`, or `~/.codex` unless the user
  explicitly asks.
- Treat bridge logs as sensitive: `prompt.txt`, `debug.log`, `stdout.log`,
  `stderr.log`, and `events.ndjson` may contain secrets.

## Default Flow

1. Run `claude_doctor` when the session is fresh, flags are uncertain, or the
   user asks about capability.
2. Run `claude_profiles` before choosing a non-default profile.
3. Start work with `claude_run`.
4. For long/risky work, use `claude_peek` with `cursor` instead of waiting
   blindly, and post `chat_relay.text` as concise chat updates when it contains
   new Claude answer text.
5. Finish with `claude_wait` or `claude_result`, then paste
   `chat_relay.text` into the chat when the user asked to see Claude's answer.
6. Use `claude_kill` if the run is looping, clearly wrong, or the user asks to
   stop it.
7. Use `claude_cleanup_runs` for old logs; dry-run first, delete only with
   confirmation.

CLI fallback equivalents:

```bash
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js doctor
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js profiles
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js run --profile normal --cwd "$PWD" --prompt "..."
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js peek --run-id "<run_id>" --cursor 0
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js wait --run-id "<run_id>"
node /Users/triton/Documents/GitHub/agentic-research/experiments/claude-bridge/src/cli.js cleanup --days 14
```

## Profiles

- `normal`: default Opus run.
- `clean`: minimal mode with `--bare`; may be limited by auth.
- `no-memory`: disables Claude auto memory.
- `no-skills`: disables Claude slash-command skills.
- `read-only`: planning/read profile.
- `turbo`: full-power Opus run with dangerous permission skip.
- `skill-audit`: checks whether Claude read the target skill/context.
- `streaming-observe`: verbose long-run observation.

Say the selected profile and why in one short sentence before starting a
non-trivial run. Prefer the user's natural task language; only require explicit
profile names when the user overrides the default.

## Controls

When the Claude prompt itself matters, read
`references/opus-4-7-prompting.md` before composing `prompt`,
`systemPrompt`, `appendSystemPrompt`, or `skill-audit` instructions.

Use first-class bridge fields instead of raw flags:

- system prompt: `systemPrompt`, `appendSystemPrompt`, and supported file
  variants;
- memory: `disableAutoMemory` or profile `no-memory`;
- skills: profile `no-skills`, `clean`, or `skill-audit`;
- MCP: `mcpConfig`, `strictMcpConfig`, `mcpTimeout`,
  `maxMcpOutputTokens`;
- permissions/tools: `tools`, `allowedTools`, `disallowedTools`;
- context roots: `cwd`, `addDir`, `pluginDir`, `settingSources`, `settings`;
- run control: `maxBudgetUsd`, `sessionId`, `resume`, `forkSession`,
  `noSessionPersistence`;
- cleanup: `claude_cleanup_runs` or CLI `cleanup --days 14 --confirm` after a
  dry-run.

Budget note: for tiny smoke tests on Opus, do not use very low
`maxBudgetUsd` values such as `0.05`. Claude may produce the expected
`chat_relay.text` and still exit with `error_max_budget_usd`, which means the
budget gate failed, not that the MCP bridge or Claude answer failed. If that
happens, report it precisely and rerun with a higher budget or no budget before
calling the bridge broken.

## Chat Relay

MCP cannot write directly into the Codex chat. Only Codex can do that. The
bridge therefore returns chat-ready fields:

- `chat_relay.text`: Claude's answer/update without raw JSON;
- `chat_relay.markdown`: the same text with a `Claude:` prefix;
- `chat_relay.truncated`: whether the text was shortened;
- `next_cursor`: for the next `claude_peek` call.

When observing a run, keep the latest `next_cursor`. On each `claude_peek`, if
`chat_relay.text` is non-empty, write it to the user as a short Claude update
and call the next `peek` with the returned cursor. At completion, include
`chat_relay.text` as Claude's answer unless the user only wanted a summary.

The v1 tool set is intentionally limited to run observation, result control,
profiles, doctor checks, skill discovery/audit, and cleanup.

The bridge checks local `claude --help` before using version-sensitive flags.
If a flag is missing, report the bridge error instead of inventing a workaround.

## Evidence

For skill or context work, do not accept Claude self-report as proof of
reading. Use `claude_audit_skill` or inspect bridge logs. Evidence passes only
when tool, debug, or stream logs mention the target path.

Report the result with:

- profile and cwd;
- run_id and log_dir;
- status, managed, and orphan_reason when present;
- warnings from `peek`, `wait`, or `result`;
- `error_max_budget_usd` separately from bridge/auth failure when
  `chat_relay.text` or `final_output_summary` exists;
- milestones, not raw stream-json;
- `chat_relay.text` when the user needs Claude's answer in chat;
- final summary if you are summarizing rather than relaying;
- evidence status when the task depends on reading a skill/context.

## Stop Rule

If the bridge MCP tools are unavailable and the CLI fallback also fails, stop
and report exactly what is missing: MCP registration, Node package install,
`claude` CLI, auth, or unsupported local flag. Do not silently fall back to an
uncontrolled raw `claude` command for work that needs observation or evidence.
