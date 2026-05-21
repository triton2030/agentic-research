# md-mcp

Unified MCP server for Markdown corpus tooling. Exposes the repo-owned
**md-navigator** backend (maps, search, profiles, refactor signals) and
**md-graph** backend (read-before-edit / edit-after-edit hygiene) as typed
tools over stdio.

Node owns the tool surface. Python owns backend behavior. Skill files own
workflow choices.

## Design — MCP is the API spec

`listTools` is the canonical contract. Every tool description is
**self-sufficient**: it teaches WHEN to call, WHY it beats Bash, INPUT/OUTPUT
shape, ALTernatives, and COST/RISK in one packet. An agent without skills
installed can read `listTools` and call the right tool.

Skills are **workflow overlay** — they layer interpretation, multi-tool
sequencing, and project-specific judgment on top of the MCP surface. A skill
does not duplicate MCP's input schema; it teaches when to choose composite
vs atomic and how to interpret output.

## Tool surface (27 public tools + md_ping)

### Composite (6) — bundled workflows

| Tool | Purpose |
|---|---|
| `md_orient` | New corpus orientation: status + map with link counts + importance. No embeddings. |
| `md_edit_context` | Pre-edit packet for one file. Modes: `preview`, `full`, `strict`. |
| `md_section_blast_radius` | Section rename radius: graph hard layer + semantic soft layer. |
| `md_audit` | Orchestrated corpus health audit: overlaps + repeated concepts + clusters. Slow. |
| `md_refactor_candidates` | Human-reviewed refactor proposals from section profiles. No automation. |
| `md_query_by_type` | List profiled sections by type: open-question / decision / definition / rule. |

### Atomic navigation/content (7)

| Tool | Purpose |
|---|---|
| `md_status` | Index freshness: FRESH / HEALTHY / NEEDS WARMUP / NO INDEX. |
| `md_ls` | List files with frontmatter descriptions + heading counts + optional link counts. |
| `md_toc` | Headings with stable ids for use as `md_extract` input. |
| `md_search` | Semantic + BM25 hybrid search via RRF. Ranked sections. |
| `md_extract` | Pull metadata or section bodies from a saved map (merger of old `pick` + `cat`). |
| `md_read_related` | Anchor file + linked neighborhood. `preview` / `full` modes. |
| `md_importance` | Rank files by pagerank / centrality / in/out-degree. No embeddings. |

### Atomic graph (7)

| Tool | Purpose |
|---|---|
| `md_preflight` | Pre-edit safety report. Sets `has_blockers:true` on missing-target / broken-link / cycle. |
| `md_impact` | What breaks if a `.md` file is deleted or renamed. |
| `md_deps` | Forward edges + reverse holders for one file, depth>1 walks cascade. |
| `md_health` | Repo-level summary: description coverage, hubs, orphans, cycles, broken links. |
| `md_cycles` | Edit-after-edit cycles list. Tarjan SCC. |
| `md_check` | Wikilink / anchor / markdown-link validation. |
| `md_scan` | Frontmatter form issues: missing / legacy / unknown / malformed. |

### Atomic IA probes (2)

| Tool | Purpose |
|---|---|
| `md_overlaps` | Section pairs with high semantic similarity (smeared-information detector). |
| `md_repeated_concepts` | Concept-level clustering via connected components on similarity graph. |

### Git-driven (1)

| Tool | Purpose |
|---|---|
| `md_changed` | Preflight on every `.md` file touched by git diff. `--base` / `--staged`. |

### Mutating with guards (4)

| Tool | Cost / Risk | Guard pattern |
|---|---|---|
| `md_index` | Cost: ~$0.02 per 1000 chunks via OpenRouter | `confirm:true` required; `dry_run:true` returns estimate. |
| `md_profile_sections` | Cost: heuristic free, llm ~$0.0005/section | `confirm:true` + `dry_run:true`. |
| `md_init` | Destructive: modifies `.md` files in place | `confirm:true` + `dry_run:true` lists affected files. |
| `md_strip` | Destructive: removes frontmatter fields and optionally body sections | `confirm:true` + `dry_run:true`. |

### Server (1)

| Tool | Purpose |
|---|---|
| `md_ping` | Health check: server name, version, resolved script paths. No backend call. |

## Workflow quick reference

| Moment | Use |
|---|---|
| New Markdown corpus / folder | `md_orient` |
| Find where X is discussed | `md_search` |
| Understand one file before editing | `md_edit_context` (`preview` first, `full` if needed) |
| Check hard graph blockers | `md_preflight` or `md_edit_context mode=strict` |
| Delete or rename a file | `md_impact` |
| Rename or rewrite a section | `md_section_blast_radius` |
| Find duplicate / smeared sections | `md_overlaps` |
| Find recurring concepts across files | `md_repeated_concepts` |
| Find refactor opportunities | `md_refactor_candidates` |
| Find open questions / decisions / definitions | `md_query_by_type` |
| Repo-level graph hygiene | `md_health` (rollup) or `md_cycles` / `md_check` / `md_scan` (individual) |
| Pre-commit graph check | `md_changed` |
| Cold-start embedding index | `md_index` (with `dry_run:true` first) |
| Profile sections for type classification | `md_profile_sections` |
| Add graph frontmatter to new files | `md_init` |
| Remove legacy graph fields | `md_strip` |
| Exact strings, regex, stale refs | `rg` / Bash — not MCP |

## Self-sufficient description contract

Every tool description follows:

```
<one-line action>

WHEN: trigger phrases / typical situations / which user question
WHY OURS: what we add vs Bash ls/grep/find
INPUT: main params and defaults
OUTPUT: shape preview — key fields, when array vs object
ALT: when to prefer composite tool / another tool
COST/RISK: cost / what changes on disk (for mutating)
```

Skills must not duplicate input schemas — point at MCP. Skills teach
interpretation and multi-tool sequencing.

## Mutating-tool guard pattern

Mutating tools (`md_index`, `md_profile_sections`, `md_init`, `md_strip`)
require explicit confirmation:

```javascript
{ corpus, confirm: true }           // proceeds
{ corpus, dry_run: true }           // returns estimate, no side-effect
{ corpus }                          // returns { error: "confirm_required" }
```

`dry_run` returns:
- `md_index` — `{ pending_chunks, estimated_cost_usd, status_text }`
- `md_profile_sections` — `{ sections_to_profile_estimate, mode, estimated_cost_usd }`
- `md_init` / `md_strip` — `{ files_to_modify, file_count }`

## Tool contracts and backend mapping

Zod input schemas live next to each `registerTool(...)` call in
`src/tools/*.js`.

| Tool | Required args | Python command(s) | Notes |
|---|---|---|---|
| `md_ping` | - | none | Server/path health only. |
| `md_orient` | `corpus` | `status`, `map --with-link-counts`, `importance` | Cheap, no embeddings. |
| `md_edit_context` | `path` | `preflight`, `read-related`, optional `search` | `strict` mode skips context body. |
| `md_section_blast_radius` | `path`, `corpus`, `query` | `preflight` + `search` | Hard graph + soft semantic candidates. |
| `md_audit` | `corpus` | `audit --json` | Slow, 300s timeout. |
| `md_refactor_candidates` | `corpus` | `refactor-candidates` | Needs warm index + profiles. |
| `md_query_by_type` | `corpus`, `types` | `query-by-type` | Profiles are created lazily when missing. |
| `md_status` | `corpus` | `status` | No HTTP, no writes. |
| `md_ls` | `path` | `map --json` | Optional tokens/link counts. |
| `md_toc` | `path` | `headings --json` | Stable heading ids for later extract. |
| `md_search` | `corpus`, `query` | `search --json` | May return `index_warmup_required`. |
| `md_extract` | `map_data` | `pick --json` or `read --json` | `extract:false`→pick metadata; `true`→read bodies. |
| `md_read_related` | `paths` | `read-related --json` | Linked context; `preview` omits content. |
| `md_importance` | `corpus` | `importance --json` | Link graph only, no embeddings. |
| `md_overlaps` | `corpus` | `overlaps --json` | Needs warm index. Section-pair similarity. |
| `md_repeated_concepts` | `corpus` | `repeated-concepts --json` | Needs warm index. Writes `.md-navigator/repeated-concepts.md`. |
| `md_preflight` | `path` | `preflight --json` | `has_blockers` reflects graph blockers. |
| `md_impact` | `path` | `impact --json` | Delete/rename blast radius for explicit links. |
| `md_deps` | `path` | `deps --json` | Forward/reverse graph edges. |
| `md_health` | - | `health --json` | Optional `paths`; graph summary. |
| `md_cycles` | - | `cycles --json` | Edit-after-edit cycle list. |
| `md_check` | - | `check --json` | Wikilink/anchor/markdown-link validation. |
| `md_scan` | - | `scan --json` | Frontmatter schema issues. |
| `md_changed` | - | `changed --json` | Git diff → preflight each `.md`. |
| `md_index` (mutating) | `corpus`, `confirm` | `index` | `dry_run:true` returns estimate. |
| `md_profile_sections` (mutating) | `corpus`, `confirm` | `profile-sections --json` | Heuristic free; LLM mode ~$0.0005/section. |
| `md_init` (mutating) | `confirm` | `init --json` | Adds frontmatter template. `dry_run:true` lists files. |
| `md_strip` (mutating) | `confirm` | `strip` | Removes legacy fields. `also_related_section` for body. |

## Registration

### Codex (`~/.codex/config.toml`)

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
| `md_navigator.py` | `MD_NAVIGATOR_SCRIPT` env -> `../scripts/md_navigator.py` (in-repo) |
| `md_graph.py` | `MD_GRAPH_SCRIPT` env -> `../scripts/md_graph.py` (in-repo) |

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
# 37 passed, 0 failed (md_audit skipped by default)
SMOKE_AUDIT=1 npm run smoke   # include md_audit (slow)
```

The fixture corpus defaults to this repo's `knowledge/` folder. Override with:

```bash
MD_MCP_SMOKE_REPO=/path/to/agentic-research npm run smoke
```

Semantic tools rely on a warm index at `<corpus>/.md-navigator/index.sqlite`;
run `md_index` (with `dry_run:true` first to see cost, then `confirm:true`) if
absent. Or run CLI directly: `md_navigator.py index knowledge`.

Smoke proves the stdio server starts, the exact documented tool list is
registered, representative output shapes parse, mutating-tool guards work,
and Python script resolution works.

## Adding a new tool

1. Identify the family: navigator, graph, hybrid, or composite.
2. Confirm the backend command exists. Decide read-only vs mutating vs cost-bearing.
3. Add a `registerTool(...)` block in the matching `src/tools/*.js`, with Zod
   schema inline near the handler.
4. Write self-sufficient description (WHEN / WHY / INPUT / OUTPUT / ALT / COST).
5. Pick timeout intentionally: 30s for cheap map/status, 60s for graph/context,
   120s for search/profile/refactor, 300s for audit, 600s for index.
6. Use `runNavigator` or `runGraph` so exit-code mapping stays consistent.
7. For mutating tools, add `dry_run` + `confirm` guards.
8. Add `npm run smoke` assertion. Update `EXPECTED_TOOLS` if total changed.
9. Update this README's tool tables and version bump in `package.json`,
   `src/server.js`, and `md_ping`.

## Version history

**0.6.0** (2026-05-21):
- Expanded surface from 19 → 27 public tools (+ `md_ping`).
- New read-only atomic tools: `md_overlaps`, `md_repeated_concepts`,
  `md_cycles`, `md_check`, `md_scan`, `md_changed`.
- New mutating tools with `confirm` / `dry_run` guards: `md_index`,
  `md_init`, `md_strip`, `md_profile_sections`.
- Merged `md_pick` + `md_cat` → `md_extract` (`extract:true` toggles bodies).
- All descriptions rewritten to self-sufficient format.
- Smoke coverage: 37 assertions.

**0.5.x** (2026-05-21):
- `scripts/` folders removed from `~/.claude/skills/1md-{navigator,graph}/`
  and `~/.codex/skills/1md-{navigator,graph}/`. Backend lives only in
  `experiments/md-embedding-server/scripts/`.
- `paths.js` fallback paths to skill folders removed.

**0.4.0**:
- Graph backend now resolves to the repo-owned `scripts/md_graph.py` first.
- Tier 1 + Tier 2 composites: `md_orient`, `md_edit_context`,
  `md_refactor_candidates`, `md_query_by_type`.

## Troubleshooting

**`md_ping` works but other tools throw "spawn failed"** - script resolution
failed. Run `md_ping` and inspect `navigator_error` / `graph_error` fields.

**`md_search` returns `{ error: "index_warmup_required" }`** - first-time index
for that corpus exceeds `--max-auto-embed`. Call `md_index` with
`dry_run:true` for cost estimate, then `confirm:true` to run.

**Codex sees the server but tools do not appear** - verify Codex started a new
session after editing `config.toml`. Codex reads MCP config at session start.

**Claude Code says connected but no tools** - check `claude mcp list` shows the
server, then restart the Claude Code session because tool lists are cached at
session start.

**Mutating tool returns `confirm_required`** - by design. Pass `dry_run:true`
first to see scope, then `confirm:true` to execute.

**Server exits immediately** - `exitOnClosedStdio` fires when stdin closes.
Both Claude and Codex keep stdin open during a real session.
