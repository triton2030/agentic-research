# Migration Blast Inventory

Retired generated inventory.

This file used to be a raw line-hit dump from the md MCP to CLI migration.
It listed old command names and absolute paths from live skills, so after the
git-diff helper was removed it became more misleading than useful.

Current truth lives in:

- `src/md_cli/catalog.py`
- `docs/cli-signatures-canonical.md`
- `docs/mcp-response-snapshots.md`
- live `/Users/triton/.codex/skills/**` and `/Users/triton/.claude/skills/**`

Archived task references may still point here as provenance. Do not use this
file as command guidance.
