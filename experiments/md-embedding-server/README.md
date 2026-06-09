---
description: Overview and development workflow for md-tools, the agent-facing Markdown
  CLI.
depends-on:
- '[[docs/architecture-lock.md]]'
- '[[docs/cli-conventions.md]]'
---
# md-tools

Unified Markdown CLI used by both the Claude and Codex `1md-navigator` /
`1md-graph` skills. Reads through an OpenAI-compatible embedding API
(default: OpenRouter / `baai/bge-m3`) — no local
embedding server, no Metal allocator pressure, no model files on disk.

The installed `md` binary is the only agent-facing entry point. The pure
backend lives in `src/navigator/`; the CLI, envelope, dispatch, transactions
and command handlers live in `src/md_cli/`.

Skill folders (`~/.claude/skills/1md-{navigator,graph}/`,
`~/.codex/skills/1md-{navigator,graph}/`) are pure declarative surfaces:
`SKILL.md`, `references/`, and optional metadata. They call `md ... --json`;
no skill-side scripts or server bridge are required.

> **Note on the folder name.** Historically this directory hosted a
> local MLX embedding server. We retired the server when we moved to
> cloud embeddings; the folder name is kept for path compatibility.
> The real runtime entry point is the `md` CLI, backed by `src/navigator/`.

## Unified backend shape

- `src/navigator/markdown_io.py` owns shared Markdown and link parsing.
- `src/navigator/graph_core.py` and `src/navigator/graph_reports.py` own
  graph loading, path filtering, dependency analysis, reports and schema
  cleanup primitives. `graph_edges.py` resolves graph edges on top of
  `markdown_io`; it must not redefine link parsing semantics. Multi-file
  graph updates use named `graph_core.DocWrite` plans so `init`/`strip` either
  apply together or restore originals.
- `src/navigator/api.py` is the thin callable facade used by `src/md_cli/`.
  Domain adapters live next to it: `api_graph.py` for graph wrappers,
  `api_search.py` for search/read output shaping, `api_audit.py` for
  semantic audit maps, and `api_profile.py` for index/profile commands.
- `src/navigator/audit.py` owns the audit detection payload. CLI routing,
  Markdown rendering and severity scoring are split into `audit_cli.py`,
  `audit_render.py` and `audit_severity.py`.
- Graph-facing wrappers build `GraphArgs` (dataclass) in `api_graph.py`, merge
  `.md-tools.toml` graph filters once, and load docs through one path.
- `src/navigator/link_graph.py` owns the explicit edge iterator used by link
  counts, centrality and `read-related --check-links`; do not re-resolve
  frontmatter/wikilink/Markdown-link families in another module.
- `src/navigator/section_profile.py`, `originality.py`,
  `owner_detector.py`, and `refactor_proposals.py` add Tier 2
  refactor signals. Section profiles support explicit OpenRouter LLM mode
  with heuristic fallback; proposals are human-reviewed and never mutate files.
- `src/navigator/workflows/` composes atomic functions into agent-facing
  workflows such as `orient`, `edit-context`, `section-blast-radius`, and
  `refactor-candidates`.
- `src/md_cli/` owns the command catalog, thin handlers, envelope wrapping,
  transaction guard and JSON serialization. Transaction and cost awareness are
  explicit `ToolSpec` fields/predicates, not ad-hoc handler-side command lists.

## Developer workflow

From the repository root:

```bash
experiments/md-embedding-server/scripts/run-tests.sh
cd experiments/md-embedding-server && uv run md selftest --json
```

Current expected signal: Python tests pass, and `md selftest --json` reports
all required CLI checks passing with expensive audit-style checks skipped
unless explicitly requested.

Choose the cheapest gate by change type:

| Change | Required check |
|---|---|
| Python parser/helper/search/profile/graph code | `experiments/md-embedding-server/scripts/run-tests.sh` |
| New or changed CLI command/catalog/envelope | `experiments/md-embedding-server/scripts/run-tests.sh` + `cd experiments/md-embedding-server && uv run md tools --json` + regenerated snapshots/catalogs |
| New or changed workflow/handler behavior | `cd experiments/md-embedding-server && uv run md selftest --json` |
| `md audit` behavior | targeted pytest + manual `md audit CORPUS --json` on a bounded corpus |
| Runtime `SKILL.md` workflow text | `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --check` if Claude/Codex sync is in scope |

`sync-skill-docs.py --check` is not a backend gate. It checks installed skill
docs and generated catalogs for stale CLI guidance.

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

## CLI (`md`)

Agent-facing commands use a context ladder. Normal output is a map: paths,
descriptions, heading handles, snippets, counts, stats and `read_next`
actions. Full bodies or large evidence lists require explicit `--expanded`
or deliberate reader flags such as `md extract --extract`.

`--compact` remains accepted on older commands as a compatibility alias for
the normal map. New docs and skills should say `--expanded` when they need
full detail.

Subcommands:

- `ls`, `toc` — folder/file index by frontmatter description and headings
- `extract` — return selected files/sections in one packet
- `read-related` — linked Markdown neighborhood as a map by default;
  `--expanded` / `--mode full` includes bodies
- `coherence-audit` — after editing a file/section, keep inline anchored
  wikilinks in place and insert each referenced block immediately after its
  link for a coherence reread; frontmatter is ignored
- `walk` — follow anchored wikilinks from one section as a single text chain
- `importance` — graph centrality ranking (pagerank / centrality / in-degree / out-degree)
- `profile-sections` — cache section profiles in the index (`--mode llm` for OpenRouter, heuristic default for no-cost runs)
- `originality`, `owner-candidates` — embedding-cosine and graph-aware refactor signals
- `refactor-candidates`, `query-by-type` — bounded refactor/query maps by
  default; `--expanded` includes full evidence/profile detail
- `index` — cold-start (or top up) the persistent vector index for a corpus
- `status` — freshness check for an existing index; no HTTP and no writes
- `search` — hybrid section retrieval (BM25F + dense via RRF)
- `search-read` — ranked section map/snippets by default; `--expanded`
  includes section bodies under `--token-budget`
- `overlaps` — grouped semantic-overlap map by default; `--expanded`
  returns full pairs
- `cluster` — read-only K-means topic clusters from an already warm vector
  index; returns `index_warmup_required` when cold
- `repeated-concepts`, `audit` — corpus-level duplicate/topic/IA maps by
  default; `--expanded` returns full evidence
- `tools`, `ping`, `doctor`, `selftest` — runtime discovery and diagnostics

## Adding a Python CLI command

Start by choosing the owner surface:

| New behavior | Put it in |
|---|---|
| Search/index/audit-style primitive with shared flags or real logic | dedicated module in `src/navigator/` plus a thin public function or re-export in `navigator.api` |
| Agent workflow over existing primitives | `src/navigator/workflows/` plus a thin handler in `src/md_cli/handlers/`; keep domain/index/cache logic in the owning `api_*.py` adapter |
| Graph contract, frontmatter `depends-on`, rename/delete, or link-health logic | graph primitives in `src/navigator/graph_core.py` / `graph_reports.py` plus graph-facing adapters in `api_graph.py` |
| CLI/envelope/transaction behavior | `src/md_cli/` only |

Checklist:

1. Add the parser/help text and a pure helper where possible.
   For graph-facing public API, reuse `_graph_args`, `_graph_docs` and
   `_graph_scan_docs`; do not hand-build another args object or duplicate
   `.md-tools.toml` filter merging. For index-backed semantic tools, route
   through the named `IndexContext` helper instead of repeating warmup/filter
   setup. Read APIs must return a `md_index` dry-run `read_next` when cache
   rebuild is requested; they do not delete or rebuild indexes themselves.
2. Return `0` for success, `1` for empty/no-result, `2` for usage/path
   errors, `3` for dependency/API failure, and `4` for index warmup refusal.
3. If the command emits JSON, decide whether it is a stable agent-facing
   contract. Stable contracts get a schema in `navigator/schemas.py`; debug
   JSON must be documented as debug-only.
4. Ensure the command is registered in `src/md_cli/catalog.py`; the test suite
   catches catalog/signature drift. Every public input property needs a
   non-empty schema `description`, because `md --help` reads catalog schema
   descriptions directly and has no fallback help table.
5. Add tests close to the changed layer: pure helper tests, command smoke, and
   schema/manifest contract tests when applicable.
   Path-filter helpers should accept repeated/list values, generators and a
   single string without treating the string as characters.
6. If catalog signatures or descriptions changed, regenerate mirrors:
   `docs/tool-signatures-snapshot.json`,
   `tests/golden/mcp-tool-snapshot.json`, and installed tool catalogs with
   `python3 experiments/md-embedding-server/scripts/sync-skill-docs.py --regenerate`.
   Do not hand-edit generated skill `references/tool-catalog.md`.

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
md index CORPUS --dry-run --json
md index CORPUS --confirm --transaction-id <id> --json

# Later orientation — no HTTP, no writes
md status CORPUS --json

# After that — near-instant; auto-embeds tiny deltas (≤50 chunks default)
md search CORPUS --query "query" --json
md overlaps CORPUS --json

# Force full rebuild
md index CORPUS --dry-run --json

# Override location (e.g. shared cache root)
MD_NAVIGATOR_CACHE_ROOT=~/.local/share/md-navigator md index CORPUS --dry-run --json
```

Big delta refusal: if `search`/`overlaps`/`repeated-concepts` would have
to embed more than `--max-auto-embed` chunks (default 50), they refuse
with exit code 4 and ask you to run `md index CORPUS --dry-run --json`
first, then confirm with the returned transaction id. Pass
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

`md` is a Markdown-only navigator. Point `index` / `search` /
`overlaps` at the folder that actually holds your Markdown corpus
(`knowledge/`, `_ops/`, a subtree) — not at the root of a mixed monorepo.

Default exclusions (always skipped): `.git`, `.github`, `.claude`,
`.codex`, `.md-navigator`, `.cache`, `.venv`, `venv`, `__pycache__`,
`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `node_modules`, `.next`,
`.nuxt`, `dist`, `build`, `out`, `target`, `_archive`.
