# MCP Registration Locations — 2026-05-22

Generated during task-000 preflight. This file tracks active registration
surfaces only; session logs, memories, task histories and caches are not active
MCP registrations.

## Search

```bash
rg -n "md-mcp|md_mcp" \
  ~/.claude/settings.json ~/.claude/settings.local.json \
  ~/.codex/config.toml ~/.claude/mcp.json ~/.codex/mcp.json \
  /Users/triton/Documents/GitHub/agentic-research/.mcp.json
```

## Active Hits

```text
/Users/triton/.codex/config.toml:360:[mcp_servers.md-mcp]
```

## Active Codex Registration

```toml
[mcp_servers.md-mcp]
command = "node"
args = ["/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/src/server.js"]
```

## Notes

- No active `md-mcp` hit was found in the checked Claude settings files.
- Removal belongs to task-401, after CLI migration and before task-501 smoke.
