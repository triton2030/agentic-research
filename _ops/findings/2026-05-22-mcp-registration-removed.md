# MCP registration removed — 2026-05-22

## Changed

- Removed `[mcp_servers.md-mcp]` from `/Users/triton/.codex/config.toml`.
- Did not edit Claude settings: checked live settings files had no `md-mcp`
  registration, and current repo rules require separate explicit permission for
  Claude runtime configs.

## Checks

- `python3 -c "import tomllib; tomllib.loads(open('/Users/triton/.codex/config.toml').read()); print('ok')"` → `ok`.
- Checked `/Users/triton/.codex/config.toml`,
  `/Users/triton/.claude/settings.json`,
  `/Users/triton/.claude/settings.local.json`, and repo `.mcp.json` for
  `md-mcp|md_mcp|mcp__md-mcp` → 0 active hits.
- Stopped running `node .../experiments/md-embedding-server/mcp/src/server.js`
  processes and verified no matching `node` process remained.

## Notes

- Other MCP servers (`claude-mcp`, `gemini-mcp`, `node_repl`, etc.) were not
  touched.
- Current Codex session may still list already-loaded deferred md-mcp tools
  until restart; config removal affects new sessions.
