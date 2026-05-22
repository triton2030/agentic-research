# md-mcp to CLI refactor closeout — 2026-05-22

## Verdict

complete-with-observed-limits

## Closed

- Removed Node MCP server directory `experiments/md-embedding-server/mcp/`.
- Removed Codex registration `[mcp_servers.md-mcp]` from
  `/Users/triton/.codex/config.toml`.
- Installed `md-tools 0.7.0` as global `md` CLI via `uv tool install --editable`.
- Implemented library/CLI split:
  - `src/navigator/` — importable backend and workflows.
  - `src/md_cli/` — catalog, handlers, runner, envelope, transactions.
- Preserved 29 agent-facing tools as `md <subcommand>` commands.
- Migrated Claude and Codex skill surfaces to CLI syntax and generated mirrored
  `tool-catalog.md` files.
- Removed legacy Claude user-level `md-mcp` registration from
  `/Users/triton/.claude.json` after explicit user authorization.
- Installed Claude `PreToolUse` code-locality hook for future writes to
  Claude/Codex skill folders.
- Archived 24 task files into `_ops/plans/md-mcp-to-cli-refactor/_archive/`.
- Updated `_ops/PROJECT-ROADMAP.md`, `_ops/project-graph.md`, and
  `experiments/md-embedding-server/README.md`.

## Evidence

- `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check`
  → Claude/Codex skill docs and catalogs fresh.
- `rg --pcre2 '<stale md tool-id / MCP / invalid md command pattern>' ~/.claude/skills ~/.codex/skills`
  → 0 matches.
- Clean install from `/tmp` with temp `HOME`:
  `md --version`, `md ping`, `md status .`, `md tools`, `md selftest` all pass.
- Cross-project CLI smoke:
  - agentic-research: `md orient knowledge`, `md status _ops`,
    `md query-by-type _ops`.
  - civicchain: `md orient .`.
- Mutating smoke: `md init --dry-run` → `transaction_id` →
  `md init --confirm --transaction-id <id>` changed 1 file in tmp corpus.
- Post-removal tests:
  - `uv run pytest tests/ -q` → 175 passed.
  - `bash scripts/run-tests.sh -q` → 175 passed.
  - `md selftest --json` → `{pass: 28, fail: 0, skip: 1, total: 29}`.
  - `md doctor` → no FAIL.
- Runtime/config cleanup:
  - `python3 -m json.tool /Users/triton/.claude.json` → ok.
  - `python3 -m json.tool /Users/triton/.claude/settings.json` → ok.
  - `rg 'md-mcp|md_mcp|mcp__md-mcp|experiments/md-embedding-server/mcp'`
    across active Claude/Codex config files → no active config hits.
  - No `node .../experiments/md-embedding-server/mcp/src/server.js` process.
- Code-locality hook:
  `_ops/findings/2026-05-22-code-locality-hook.md` documents install and
  positive/negative simulated hook checks.
- Final removal tag: `mcp-removed-2026-05-22`.

## Diff Snapshot

- Removed tracked MCP files: 15 files, 4577 deleted lines.
- Current Python/package/test/README delta after the final symlink fix:
  about 298 additions / 111 deletions outside the removed MCP directory
  in the checked md-tools scope. Full repo diff also includes moved task
  capsules and installed skill docs outside the repo.

## Known Limits

- Fresh Claude/Codex UI sessions were not directly observable from this Codex
  thread. The verified substitute is clean install + installed CLI smoke +
  migrated skill docs + active config removal + no matching md-mcp node process.
- Already-running Claude app sessions may still show the old `--mcp-config`
  command-line argument until they are restarted. The persistent Claude/Codex
  config files no longer register `md-mcp`.
- Existing non-md helper scripts in skill folders, such as
  `1cli-tools/scripts/probe-tools.sh`, were not removed because task-305 scopes
  existing non-md scripts out of this refactor. The new hook blocks future
  non-whitelisted writes.
- Deferred cleanup: `navigator.__init__` still keeps callable module proxies for
  compatibility; future cleanup can move users to `navigator.api` only.

## Rollback

Backup tag remains: `pre-mcp-refactor-2026-05-22`.

Removal tag: `mcp-removed-2026-05-22`.

Earliest safe deletion of `pre-mcp-refactor-2026-05-22`: 2026-06-22 (one month
after `mcp-removed-2026-05-22`). Recommend retention until 2026-07-22 if a fresh
Claude UI session smoke run was not performed personally by the user.

If an issue appears, restore the removed server with:

```bash
git checkout pre-mcp-refactor-2026-05-22 -- experiments/md-embedding-server/mcp
```
