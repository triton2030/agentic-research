# md-mcp

Unified MCP server for Markdown corpus tooling. It exposes the repo-owned
**md-navigator** backend (maps, search, profiles, refactor signals) and
**md-graph** backend (read-before-edit / edit-after-edit hygiene) as typed
tools over stdio.

Node owns the tool surface. Python owns backend behavior. Skill files own
workflow choices.

## Why it exists

- **Discoverability** - models see typed tool schemas through `listTools`
  instead of remembering CLI flags.
- **Workflow packets** - composites like `md_orient` and
  `md_edit_context` bundle common agent moments into one call.
- **Cross-runtime backend** - the same server serves Claude and Codex; fewer
  divergence points than mirrored skill scripts.

CLI scripts stay live: indexing, schema mutations (`init` / `strip`),
git-driven `changed`, hooks, debugging, and direct fallback remain CLI-only.
Ordinary read-only agent workflows should use MCP first.

## Tool surface (19 tools)

### Primary composites (4)

| Tool | Purpose |
|---|---|
| `md_orient` | Cheap corpus orientation: status + map with link counts + importance. No embeddings. |
| `md_edit_context` | Pre-edit packet for one file. Modes: `preview`, `full`, `strict`. |
| `md_refactor_candidates` | Human-reviewed refactor proposals from section profiles. No automation. |
| `md_query_by_type` | List profiled sections by type: `open-question`, `decision`, `definition`, etc. |

### Hybrid (1)

| Tool | Purpose |
|---|---|
| `md_section_blast_radius` | Section rename/rewrite radius: graph hard layer + semantic soft layer. `query` is required. |

### Navigator building blocks (9)

| Tool | Purpose |
|---|---|
| `md_status` | Index freshness for a corpus. |
| `md_ls` | Folder listing: paths + frontmatter `description` + heading counts; optional link counts. |
| `md_toc` | Table of contents with stable heading ids (`1.2`, `4.3`); optional link counts. |
| `md_search` | Semantic + keyword search (BM25F + dense via RRF); ranked sections, not line matches. |
| `md_pick` | Select files/headings from a saved map; `extract: true` returns bodies. |
| `md_cat` | Heading-aware section extract from a saved map. For one file by path use built-in Read. |
| `md_read_related` | Read anchor + linked neighborhood. `mode: preview` returns descriptions/headings only; MCP default is anchor-aware for heading links. |
| `md_audit` | Orchestrated corpus health audit; slow, 300s timeout. |
| `md_importance` | Rank files by pagerank / centrality / in-degree / out-degree. No embeddings. |

### Graph building blocks (4)

| Tool | Purpose |
|---|---|
| `md_preflight` | Pre-edit safety report for a `.md` file; sets `has_blockers: true` on missing-target / broken-link / cycle / missing-frontmatter. |
| `md_impact` | What breaks if a `.md` file is deleted or renamed. |
| `md_deps` | Forward edges + reverse holders for one file, with cascade depth. |
| `md_health` | Repo-level summary: description coverage, hubs, orphans, cycles. |

### Server health (1)

| Tool | Purpose |
|---|---|
| `md_ping` | Health check: server + resolved script paths, no backend call. |

**Renamed in 0.2.0**: `md_map -> md_ls`, `md_headings -> md_toc`,
`md_read -> md_cat`.

**0.4.0 changes**:
- Graph backend now resolves to the repo-owned `scripts/md_graph.py` first.
- Tier 1: link counts in `md_ls` / `md_toc`, `md_importance`,
  `md_read_related.mode`, `md_orient`, `md_edit_context`.
- Tier 2: section profiles, `md_refactor_candidates`, `md_query_by_type`.
- Smoke coverage is now 24 assertions.

## Workflow quick reference

| Moment | Use |
|---|---|
| New Markdown corpus / folder | `md_orient` |
| Find where X is discussed | `md_search` |
| Understand one file before editing | `md_edit_context` (`preview` first, `full` if needed) |
| Check hard graph blockers | `md_preflight` or `md_edit_context mode=strict` |
| Delete or rename a file | `md_impact` |
| Rename or rewrite a section | `md_section_blast_radius` |
| Find refactor opportunities | `md_refactor_candidates` |
| Find open questions / decisions / definitions | `md_query_by_type` |
| Exact strings, regex, stale refs | `rg` / `1cli-tools`, not MCP search |

## Tool contracts and backend mapping

Zod input schemas live next to each `registerTool(...)` call in
`src/tools/*.js`. There is no separate shared schema source; if a common arg
helper is introduced later, it must be imported by the tool files and covered
by smoke.

| Tool | Required args | Python command(s) | Notes |
|---|---|---|---|
| `md_ping` | - | none | Server/path health only. |
| `md_orient` | `corpus` | `status`, `map --with-link-counts`, `importance` | Cheap, no embeddings. |
| `md_edit_context` | `path` | `preflight`, `read-related`, optional `search` | `strict` mode skips context body. |
| `md_refactor_candidates` | `corpus` | `refactor-candidates` | Needs warm index + profiles. |
| `md_query_by_type` | `corpus`, `types` | `query-by-type` | Profiles are created lazily when missing. |
| `md_section_blast_radius` | `path`, `corpus`, `query` | `preflight` + `search` | Hard graph + soft semantic candidates. |
| `md_status` | `corpus` | `status` | No HTTP, no writes. |
| `md_ls` | `path` | `map --json` | Optional tokens/link counts. |
| `md_toc` | `path` | `headings --json` | Stable heading ids for later pick/cat. |
| `md_search` | `corpus`, `query` | `search --json` | May return `index_warmup_required`. |
| `md_pick` | `map_data` | `pick --json` via temp map | Selects files/headings from map output. |
| `md_cat` | `map_data` | `pick --extract --json` via temp map | For direct whole-file reads use built-in Read. |
| `md_read_related` | `paths` | `read-related --json` | Linked context; `preview` omits content. |
| `md_audit` | `corpus` | `audit --json` | Slow, 300s timeout; skipped in default smoke. |
| `md_importance` | `corpus` | `importance --json` | Link graph only, no embeddings. |
| `md_preflight` | `path` | `preflight --json` | `has_blockers` reflects graph blockers. |
| `md_impact` | `path` | `impact --json` | Delete/rename blast radius for explicit links. |
| `md_deps` | `path` | `deps --json` | Forward/reverse graph edges. |
| `md_health` | - | `health --json` | Optional `paths`; graph summary. |

## Excluded by design

`md_overlaps`, `md_repeated_concepts`, `md_cluster` - rolled into
`md_audit`. Standalone tools are too granular for the MCP surface.

`md_scan`, `md_check`, `md_doctor`, `md_cycles` - rolled into `md_health`.

`md_index`, `profile-sections`, `md_init`, `md_strip` - mutating or
cost-bearing; MCP has no good UX for cost or destructive confirmation. Stay CLI.

`md_originality`, `md_owner_candidates` - advanced internals used by refactor
proposals. Kept out of MCP until real usage proves they are useful directly.

`md_changed` - git-driven; better as a pre-commit hook than an MCP tool.

## Registration

### Codex (`~/.codex/config.toml`)

Already wired:

```toml
[mcp_servers.md-mcp]
command = "node"
args = ["/Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/src/server.js"]
```

Restart Codex to pick up MCP config changes.

### Claude Code

Wired via CLI (user scope - available in all projects):

```bash
claude mcp add md-mcp --scope user -- node /Users/triton/Documents/GitHub/agentic-research/experiments/md-embedding-server/mcp/src/server.js
```

Verify:

```bash
claude mcp list | grep md-mcp
# expected: md-mcp: node /.../mcp/src/server.js - Connected
```

## OpenRouter key

The Python script (`md_navigator.py`) discovers `OPENROUTER_API_KEY` through
its own chain:

1. `OPENROUTER_API_KEY` env var
2. `MD_EMBEDDING_API_KEY` env var
3. `<corpus>/.openrouter.key`, then every parent directory upward
4. `.openrouter.key` in CWD
5. `~/.openrouter.key`
6. `$XDG_CONFIG_HOME/md-navigator/openrouter.key`

The MCP server inherits its parent env and Python walks the filesystem, so no
extra `config.toml` env block is needed.

## Script path resolution

`src/paths.js`:

| Script | Resolution order |
|---|---|
| `md_navigator.py` | `MD_NAVIGATOR_SCRIPT` env -> `../scripts/md_navigator.py` (in-repo) -> `~/.claude/skills/1md-navigator/scripts/md_navigator.py` |
| `md_graph.py` | `MD_GRAPH_SCRIPT` env -> `../scripts/md_graph.py` (in-repo) -> `~/.claude/skills/1md-graph/scripts/md_graph.py` -> `~/.codex/skills/1md-graph/scripts/md_graph.py` |

## Exit-code mapping

`src/subprocess.js` maps Python exit codes:

| Script | Exit code | MCP result |
|---|---|---|
| navigator | 4 | `{ error: "index_warmup_required", self_repair, stderr }` |
| navigator | 1 | `{ empty: true, self_repair, stderr }` (no markdown / no indexed vectors) |
| navigator | 2 | thrown: usage error |
| navigator | 3 | thrown: dependency / API failure |
| graph | 1 | result with `has_blockers: true` (preflight/changed) or `findings` listed (others) |
| graph | 2 | thrown: usage error |

## Smoke test

```bash
cd experiments/md-embedding-server/mcp
npm install   # one-time
npm run smoke
# 24 passed, 0 failed (md_audit skipped by default)
SMOKE_AUDIT=1 npm run smoke   # include md_audit (slow)
```

The fixture corpus defaults to this repo's `knowledge/` folder, derived from
the smoke script location. Override it with:

```bash
MD_MCP_SMOKE_REPO=/path/to/agentic-research npm run smoke
```

Semantic tools rely on a warm index at `<corpus>/.md-navigator/index.sqlite`;
run `md_navigator.py index knowledge` once if absent.

Smoke proves that the stdio server starts, the exact documented tool list is
registered, representative output shapes parse, and Python script resolution
works. It does not prove editorial quality of `md_refactor_candidates`, full
`md_audit` behavior unless `SMOKE_AUDIT=1`, or real-world usefulness of a new
workflow.

## Adding a new tool

1. Identify the family: navigator, graph, hybrid, or composite.
2. Confirm the backend command exists and decide whether the tool is read-only,
   mutating, or cost-bearing. Mutating/cost-bearing commands stay CLI-only.
3. Add a `registerTool(...)` block in the matching `src/tools/*.js`, with Zod
   schema inline near the handler.
4. Pick timeout intentionally: 30s for cheap map/status, 60s for graph/context,
   120s for search/profile/refactor, 300s for audit.
5. Use `runNavigator` or `runGraph` so exit-code mapping stays consistent.
6. Decide the result envelope: parsed JSON, `{ text }`, or self-repair error.
7. Add or update a `npm run smoke` assertion. If the tool list changes, update
   the exact expected names in `test/smoke.js`.
8. Update this README's tool table, contract/mapping table, workflow reference,
   and excluded-tools section if relevant.
9. For versioned MCP surface changes, update `package.json`,
   `package-lock.json`, and `src/server.js` / `md_ping` version together.

## Troubleshooting

**`md_ping` works but other tools throw "spawn failed"** - script resolution
failed. Run `md_ping` and inspect `navigator_error` / `graph_error` fields.

**`md_search` returns `{ error: "index_warmup_required" }`** - first-time index
for that corpus exceeds `--max-auto-embed`. Run CLI:
`md_navigator.py index <corpus>` once. Restarting MCP is not needed.

**Codex sees the server but tools do not appear** - verify Codex started a new
session after editing `config.toml`. Codex reads MCP config at session start.

**Claude Code says connected but no tools** - check `claude mcp list` shows the
server, then restart the Claude Code session because tool lists are cached at
session start.

**Server exits immediately** - `exitOnClosedStdio` fires when stdin closes.
Both Claude and Codex keep stdin open during a real session.
