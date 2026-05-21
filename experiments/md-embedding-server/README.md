# md_navigator

Unified Markdown navigator client used by both the Claude and Codex
`1md-navigator` skills. Reads through an OpenAI-compatible embedding API
(default: OpenRouter / `baai/bge-m3`) — no local
embedding server, no Metal allocator pressure, no model files on disk.

The scripts in `scripts/md_navigator.py` and `scripts/md_graph.py` are
the repo-owned backend entry points. `md_navigator.py` is the shared
navigation/search/profile client; `md_graph.py` is the graph hygiene
wrapper around `navigator/graph.py`.

Runtime skill folders should point to these entry points:

```text
~/.claude/skills/1md-navigator/scripts/md_navigator.py -> experiments/md-embedding-server/scripts/md_navigator.py
~/.codex/skills/1md-navigator/scripts/md_navigator.py  -> experiments/md-embedding-server/scripts/md_navigator.py
~/.codex/skills/1md-graph/scripts/md_graph.py          -> experiments/md-embedding-server/scripts/md_graph.py
```

Edit backend code here. Before assuming a runtime wrapper has picked it up,
verify the live links:

```bash
ls -l ~/.claude/skills/1md-navigator/scripts/md_navigator.py \
      ~/.codex/skills/1md-navigator/scripts/md_navigator.py \
      ~/.claude/skills/1md-graph/scripts/md_graph.py \
      ~/.codex/skills/1md-graph/scripts/md_graph.py
```

Current repo-owned source of truth is `experiments/md-embedding-server/scripts/`.
Codex may update Codex-side wrappers; Claude-side skill files and scripts are
read-only from Codex sessions and need a Claude/user-owned sync pass when they
drift.

> **Note on the folder name.** Historically this directory hosted a
> local MLX embedding server. We retired the server when we moved to
> cloud embeddings; the folder name is kept for the symlink path
> compatibility. The real entry point is the `navigator/` package.

## Unified backend shape

- `navigator/markdown_io.py` owns shared Markdown parsing.
- `navigator/graph.py` owns graph commands: `preflight`, `impact`,
  `deps`, `health`, `check`, `changed`, and schema cleanup.
- `navigator/link_graph.py` and `navigator/importance.py` add link
  counts and centrality without embeddings.
- `navigator/section_profile.py`, `originality.py`,
  `owner_detector.py`, and `refactor_proposals.py` add Tier 2
  refactor signals. Section profiles support explicit OpenRouter LLM mode
  with heuristic fallback; proposals are human-reviewed and never mutate files.
- `mcp/` exposes read-only typed tools. Mutating and cost-bearing work
  stays CLI-only.

## Developer workflow

From the repository root:

```bash
experiments/md-embedding-server/scripts/run-tests.sh
cd experiments/md-embedding-server/mcp && npm run smoke
```

Current expected signal: Python tests pass, and MCP smoke reports all tools
passing with `md_audit` skipped unless `SMOKE_AUDIT=1` is set.

Choose the cheapest gate by change type:

| Change | Required check |
|---|---|
| Python parser/helper/search/profile/graph code | `experiments/md-embedding-server/scripts/run-tests.sh` |
| New or changed Python CLI command | `experiments/md-embedding-server/scripts/run-tests.sh` + `uv run --script experiments/md-embedding-server/scripts/md_navigator.py manifest` |
| New or changed MCP tool/schema/description | `cd experiments/md-embedding-server/mcp && npm run smoke` |
| `md_audit` behavior | `SMOKE_AUDIT=1 npm run smoke` |
| Runtime `SKILL.md` workflow text | `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check` if Claude/Codex sync is in scope |

`sync-skill-docs.py --check` is not a backend gate. It checks installed skill
docs, may fail on intentional Claude/Codex drift, and Codex must not repair
Claude-side files directly.

## Embedding backend

Default endpoint:

```text
https://openrouter.ai/api/v1/embeddings
model: baai/bge-m3  (1024-dim, 8192 max_seq, multilingual, $0.01/MTok)
```

The model default switched from `openai/text-embedding-3-small` to
`baai/bge-m3` on 2026-05-20 after an A/B replay on a RU+EN corpus showed
BGE-M3 wins on multilingual retrieval, ties on English (after corpus
hygiene), is 2× cheaper, and uses smaller 1024-dim vectors. Evidence:
`_ops/findings/_archive/2026-05-18-md-navigator-bm25-russian-stemming.md`.

**Sticky model behavior.** When `--embed-model` is omitted, the navigator
reads the recorded model from the existing index meta and uses that.
This prevents accidental drop+reindex when a corpus was indexed on a
non-default model. The fallback (no meta yet) is the global default
above. Explicit `--embed-model X` always wins and triggers reindex on
mismatch.

API key lookup order:

1. `OPENROUTER_API_KEY` env var
2. `MD_EMBEDDING_API_KEY` env var
3. `<corpus>/.openrouter.key`, then every parent directory upward
4. `.openrouter.key` in the current working directory
5. `~/.openrouter.key`
6. `$XDG_CONFIG_HOME/md-navigator/openrouter.key`

The file is a single line, mode `0600`. Add `.openrouter.key` to
`.gitignore` of any project where you place one. When a file key is used,
the client prints the path to stderr so the active credential source is
visible without exposing the key.

OpenRouter attribution defaults to the detected runtime:
`md-navigator/codex`, `md-navigator/claude`, or `md-navigator/direct`.
Override it with `MD_NAVIGATOR_RUNTIME`, `MD_NAVIGATOR_HTTP_REFERER`, or
`MD_NAVIGATOR_TITLE`.

Override the endpoint for any OpenAI-compatible service:

```bash
--embedding-api-url https://example.com/v1
--embed-model some-other-embedding-model
--embedding-timeout 60
```

## Client (md_navigator.py)

Subcommands:

- `map`, `headings` — folder index by frontmatter description + headings
- `pick` — select files/sections by stable id from a saved JSON map
- `pick --extract` (or `read`) — return text of selected sections in one packet
- `read-related` — linked Markdown neighborhood for context
- `importance` — graph centrality ranking (pagerank / centrality / in-degree / out-degree)
- `profile-sections` — cache section profiles in the index (`--mode llm` for OpenRouter, heuristic default for no-cost runs)
- `originality`, `owner-candidates` — embedding-cosine and graph-aware refactor signals
- `refactor-candidates`, `query-by-type` — human-reviewed refactor/query helpers
- `index` — cold-start (or top up) the persistent vector index for a corpus
- `status` — freshness check for an existing index; no HTTP and no writes
- `search` — hybrid section retrieval (BM25F + dense via RRF)
- `overlaps` — semantic similarity pair detector for IA smells
- `repeated-concepts`, `cluster` — corpus-level duplicate/topic probes
- `manifest` — machine-readable command/default contract for docs/skill sync

## Adding a Python CLI command

Start by choosing the owner surface:

| New behavior | Put it in |
|---|---|
| Search/index/audit-style command with shared flags or real logic | dedicated `navigator/<name>.py` with `register_<name>(sub)` and `cmd_<name>` |
| Tiny map/read/pick-style command with one-off argparse shape | inline block in `navigator/cli.py` |
| Graph contract, frontmatter, `read-before-edit`, `edit-after-edit`, rename/delete, or link-health logic | `navigator/graph.py` / `scripts/md_graph.py` |
| Agent workflow over existing primitives | MCP composite/hybrid tool first; add Python only if a backend primitive is missing |

Checklist:

1. Add the parser/help text and a pure helper where possible.
2. Return `0` for success, `1` for empty/no-result, `2` for usage/path
   errors, `3` for dependency/API failure, and `4` for index warmup refusal.
3. If the command emits JSON, decide whether it is a stable agent-facing
   contract. Stable contracts get a schema in `navigator/schemas.py`; debug
   JSON must be documented as debug-only.
4. Ensure the command is registered on the argparse surface; `manifest` is
   generated from that parser and the test suite catches parser/manifest drift.
5. Add tests close to the changed layer: pure helper tests, command smoke, and
   schema/manifest contract tests when applicable.
6. Update this README. If the command should be used by agents directly, also
   update the MCP README/tool surface; if it changes workflow choices, update
   the relevant runtime `SKILL.md` through the proper runtime owner.

## Persistent index

One sqlite file per corpus, stored next to the corpus itself:

```text
<corpus>/.md-navigator/index.sqlite
```

A `.gitignore` is auto-written in the same folder so the index file does
not end up in git. The location survives `~/.cache` cleanup.

Tables:

- `meta` (key/value): `schema_version`, `embed_model`, `embedding_api_url`,
  `vec_dim`. A change in any of those wipes the file and rebuilds.
- `sections`: one row per heading-bounded section or description, keyed
  by `(scope, content_hash)`.
- `sections_fts`: FTS5 mirror for BM25F.
- `chunks`: sub-chunks of long sections; one row per embedded passage.
- `sections_vec`: `vec0(embedding float[<dim>])`, rowid matches `chunks.chunk_id`.

Lifecycle commands:

```bash
# First-time warmup for a corpus
md_navigator.py index <corpus>

# Later orientation — no HTTP, no writes
md_navigator.py status  <corpus>

# After that — near-instant; auto-embeds tiny deltas (≤50 chunks default)
md_navigator.py search   <corpus> "query"
md_navigator.py overlaps <corpus>

# Force full rebuild
md_navigator.py search   <corpus> "query" --no-cache

# Override location (e.g. shared cache root)
md_navigator.py index    <corpus> --cache-dir ~/.local/share/md-navigator
```

Big delta refusal: if `search`/`overlaps`/`repeated-concepts` would have
to embed more than `--max-auto-embed` chunks (default 50), they refuse
with exit code 4 and ask you to run `index` first. Pass
`--max-auto-embed 0` to disable the cap.

Indexing tunables:

```bash
--batch-size 32       # items per HTTP request
--batch-pause-ms 0    # sleep between batches; raise to throttle
```

The DB is committed after every batch, so Ctrl+C only loses the current
in-flight batch. The next run heals incomplete sections automatically
before continuing.

Index writers are serialized by `<corpus>/.md-navigator/index.lock`, so
parallel Claude/Codex sessions do not race the same SQLite counters.

## Indexing scope

`md_navigator` is a Markdown-only navigator. Point `index` / `search` /
`overlaps` at the folder that actually holds your Markdown corpus
(`knowledge/`, `_ops/`, a subtree) — not at the root of a mixed monorepo.

Default exclusions (always skipped): `.git`, `.github`, `.claude`,
`.codex`, `.md-navigator`, `.cache`, `.venv`, `venv`, `__pycache__`,
`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `node_modules`, `.next`,
`.nuxt`, `dist`, `build`, `out`, `target`, `_archive`.
