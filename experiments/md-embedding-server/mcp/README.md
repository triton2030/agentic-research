# md-mcp

Unified MCP server exposing **md-navigator** (semantic search, frontmatter map, hybrid retrieval) and **md-graph** (read-before-edit / edit-after-edit graph hygiene) as typed tools over stdio.

Node wrapper, subprocess to both existing Python CLIs. Skill files own workflow; this server owns the tool surface.

## Why it exists

- **Discoverability** — model sees typed tool schemas via `listTools` instead of remembering `--help` flags
- **Hybrid coordinator** — `md_section_blast_radius` runs `md_graph preflight` + `md_navigator search` in one call
- **Cross-runtime backend** — same server serves Claude (Opus 4.7) and Codex (GPT-5.5); fewer divergence points than mirrored skill scripts

CLI scripts stay live: indexing, schema mutations (init/strip), and CLI fallback all remain in `~/.claude/skills/1md-{navigator,graph}/scripts/` and `experiments/md-embedding-server/scripts/`.

## Tool surface (14 tools)

### Navigator (8)
| Tool | Purpose | Bash analogue |
|---|---|---|
| `md_ping` | Health check — server + resolved script paths, no backend call | — |
| `md_status` | Index freshness for a corpus | — |
| `md_ls` | Folder listing: paths + frontmatter `description` + heading counts | `ls -la` + manual frontmatter read |
| `md_toc` | Table of contents with stable heading ids (`1.2`, `4.3`) — pick-compatible | — |
| `md_search` | Semantic + keyword search (BM25F + dense via RRF); ranked sections, not lines | `rg` / `grep` for natural language |
| `md_pick` | Select files/headings from a saved map; `extract: true` returns bodies | — |
| `md_cat` | Heading-aware section extract from a saved map. For one file by path use built-in Read | — (map-only) |
| `md_read_related` | Read anchor + its linked neighborhood in one packet. **Anchor-aware default: `[[file#Heading]]` pulls only that section, not whole file.** Optional `semantic_radius` for dense neighbors | — |
| `md_audit` | Orchestrated corpus health audit (overlaps + repeated-concepts + cluster); slow, 300s timeout | — |

**Renamed in 0.2.0** (previously: `md_map → md_ls`, `md_headings → md_toc`, `md_read → md_cat`). Renames pick Bash-analogue names where they exist for instant recognition; domain-specific tools (preflight, impact, audit, …) keep precise terms.

**0.3.0 changes**:
- `md_read_related` now extracts **only the targeted section** for `[[file#Heading]]` and `[text](file.md#heading)` links by default (`anchor_aware: true`). Set `anchor_aware: false` to revert to whole-file packets.
- `md_cat` lost its standalone path mode — use built-in Read for that. `md_cat` is now strictly for heading-aware extract from saved maps.
- `md_search` description tightened: it's for natural-language queries; for exact strings / regex / known symbols use `rg`.

### Graph (4)
| Tool | Purpose |
|---|---|
| `md_preflight` | Pre-edit safety report for a .md file; sets `has_blockers: true` on missing-target / broken-link / cycle / missing-frontmatter |
| `md_impact` | What breaks if a .md file is deleted or renamed |
| `md_deps` | Forward edges + reverse holders for one file, with cascade depth |
| `md_health` | Repo-level summary: description coverage, hubs, orphans, cycles |

### Hybrid (1)
| Tool | Purpose |
|---|---|
| `md_section_blast_radius` | Coordinator: combines graph hard layer (preflight) with semantic soft layer (search) in one response. `query` is required |

### Excluded by design

`md_overlaps`, `md_repeated_concepts`, `md_cluster` — rolled into `md_audit`. Standalone too granular for MCP surface; the audit orchestrator already calls them.

`md_scan`, `md_check`, `md_doctor`, `md_cycles` — rolled into `md_health`.

`md_index`, `md_init`, `md_strip` — mutating; MCP has no good UX for "this costs $0.05 in OpenRouter credit, proceed?" or destructive confirmation. Stay CLI.

`md_changed` — git-driven; better as a pre-commit hook than an MCP tool.

## Registration

### Codex (`~/.codex/config.toml`)

Already wired:

```toml
[mcp_servers.md-mcp]
command = "node"
args = ["/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/src/server.js"]
```

Restart Codex to pick up the new server.

### Claude Code

Wired via CLI (user scope — available in all projects):

```bash
claude mcp add md-mcp --scope user -- node /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/src/server.js
```

Verify:

```bash
claude mcp list | grep md-mcp
# expected: md-mcp: node /.../mcp/src/server.js - ✓ Connected
```

## OpenRouter key

The Python script (`md_navigator.py`) discovers `OPENROUTER_API_KEY` through its own chain:

1. `OPENROUTER_API_KEY` env var
2. `MD_EMBEDDING_API_KEY` env var
3. `<corpus>/.openrouter.key`, then every parent directory upward
4. `.openrouter.key` in CWD
5. `~/.openrouter.key`
6. `$XDG_CONFIG_HOME/md-navigator/openrouter.key`

The MCP server inherits its parent env and the Python subprocess walks the filesystem — so no extra config needed in `config.toml` env block.

## Script path resolution

`src/paths.js`:

| Script | Resolution order |
|---|---|
| `md_navigator.py` | `MD_NAVIGATOR_SCRIPT` env → `../scripts/md_navigator.py` (in-repo) → `~/.claude/skills/1md-navigator/scripts/md_navigator.py` |
| `md_graph.py` | `MD_GRAPH_SCRIPT` env → `~/.claude/skills/1md-graph/scripts/md_graph.py` → `~/.codex/skills/1md-graph/scripts/md_graph.py` |

## Exit-code mapping

`src/subprocess.js` maps Python exit codes:

| Script | Exit code | MCP result |
|---|---|---|
| navigator | 4 | `{ error: "index_warmup_required", hint: "Run md_navigator.py index <corpus>" }` |
| navigator | 1 | `{ empty: true, stderr: ... }` (no markdown / no indexed vectors) |
| navigator | 2 | thrown — usage error |
| navigator | 3 | thrown — dependency / API failure |
| graph | 1 | result with `has_blockers: true` (preflight/changed) or `findings` listed (others) |
| graph | 2 | thrown — usage error |

## Smoke test

```bash
cd experiments/md-embedding-server/mcp
npm install   # one-time
npm run smoke
# 15 passed, 0 failed (md_audit skipped by default)
SMOKE_AUDIT=1 npm run smoke   # include md_audit (slow)
```

The fixture corpus is the local `agentic-research/knowledge/` folder — relies on a warm index at `<corpus>/.md-navigator/index.sqlite` (run `md_navigator.py index knowledge` once if absent).

## Adding a new tool

1. Identify which family (navigator / graph / hybrid).
2. Add a `registerTool(...)` block in the corresponding `src/tools/*.js` with:
   - Zod input schema (plain object — keys to Zod values, **not** `z.object({...})`)
   - Handler that calls `runNavigator(args, opts)` or `runGraph(args, opts)`
3. Add a `npm run smoke` assertion in `test/smoke.js`.
4. Update this README's tool table and bump `package.json` version.

## Troubleshooting

**`md_ping` works but other tools throw "spawn failed"** — `MD_NAVIGATOR_SCRIPT` / `MD_GRAPH_SCRIPT` resolution failed. Run `md_ping` and inspect `navigator_error` / `graph_error` fields.

**`md_search` returns `{ error: "index_warmup_required" }`** — first-time index for that corpus exceeds `--max-auto-embed`. Run CLI: `~/.claude/skills/1md-navigator/scripts/md_navigator.py index <corpus>` once. Restart MCP server isn't needed; subsequent searches will succeed.

**Codex sees the server but tools don't appear** — verify Codex started a new session after editing `config.toml`. Codex reads MCP config at session start.

**Claude Code says "✓ Connected" but no tools** — check `claude mcp list` shows the server. If yes, restart the Claude Code session (tool list is cached at session start).

**Server exits immediately** — `exitOnClosedStdio` fires when stdin closes. Both Claude and Codex keep stdin open during the session. If you're testing manually, pipe a placeholder: `node src/server.js < /dev/null` will exit cleanly with code 0.
