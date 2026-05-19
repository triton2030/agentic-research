# md_navigator

Unified Markdown navigator client used by both the Claude and Codex
`1md-navigator` skills. Reads through an OpenAI-compatible embedding API
(default: OpenRouter / `openai/text-embedding-3-small`) — no local
embedding server, no Metal allocator pressure, no model files on disk.

The script in `scripts/md_navigator.py` is the **single source of truth**
for both runtimes. Both skill folders symlink to it:

```text
~/.claude/skills/1md-navigator/scripts/md_navigator.py -> experiments/md-embedding-server/scripts/md_navigator.py
~/.codex/skills/1md-navigator/scripts/md_navigator.py  -> experiments/md-embedding-server/scripts/md_navigator.py
```

Edit the script here; both runtimes pick up changes immediately.

> **Note on the folder name.** Historically this directory hosted a
> local MLX embedding server. We retired the server when we moved to
> cloud embeddings; the folder name is kept for the symlink path
> compatibility. The real entry point is the `navigator/` package.

## Embedding backend

Default endpoint:

```text
https://openrouter.ai/api/v1/embeddings
model: openai/text-embedding-3-small  (1536-dim, 8192 max_seq)
```

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
- `index` — cold-start (or top up) the persistent vector index for a corpus
- `status` — freshness check for an existing index; no HTTP and no writes
- `search` — hybrid section retrieval (BM25F + dense via RRF)
- `overlaps` — semantic similarity pair detector for IA smells
- `repeated-concepts`, `cluster` — corpus-level duplicate/topic probes
- `manifest` — machine-readable command/default contract for docs/skill sync

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
