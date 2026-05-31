---
description: "Architecture invariants for md CLI catalog, handler, runner, and library boundaries."
read-before-edit: []
edit-after-edit: []
---
# Architecture Lock

Phase 2 can start only when the lock tests are green.

Решения, стоящие за этими инвариантами, и их история — в [`docs/adr/`](adr/README.md).

## Invariants

- `catalog.py` matches the MCP snapshot names, schemas, annotations and
  canonical signatures. Current generated snapshot count is 32 tools; the
  executable invariant is the catalog/snapshot test, not a hand-maintained
  prose count. Runtime import must not patch `ToolSpec` values; cleanup and
  fingerprint fields belong in the generated snapshot/source data.
- `catalog.py` input schemas are the only source for generated CLI `--help`
  descriptions. Every public `input_schema.properties.*` entry must have a
  non-empty `description`; `md_cli.main` must not keep fallback help tables.
- `md_cli.handlers.*` modules return `ToolResult`; they do not print JSON, call
  `sys.exit`, or import `md_cli.envelope`.
- `md_cli.runner` is the only owner of `envelope.wrap` and `print(json.dumps)`.
- `md_cli.next_steps` owns executable `_envelope.next_step` action policy;
  `md_cli.envelope` only normalizes args, estimates size and wraps payloads.
- `md_cli.catalog.ToolSpec` owns explicit safety fields and predicates.
  Transaction gating reads `ToolSpec.transaction_required`; cost-bearing
  awareness reads `ToolSpec.cost_bearing`. Derived reporting sets may exist,
  but handlers must not recreate broad `MUTATING_TOOLS` checks or infer safety
  only from category labels.
- Agent-facing broad outputs use the context ladder: normal mode returns a
  bounded map/preview tagged `expanded:false` + `view:"map"`; full content or
  evidence is explicit `--expanded` (or a `read_next` hop). Everything the
  bounded default hides MUST stay reachable via `--expanded`/`read_next` — no
  dead ends. Legacy `map_only` / `content_included` / `--compact` are retired in
  favour of the single `view` flag.
- `md_cli.envelope.project_payload` is the single agent-view projection, applied
  inside `wrap()` before the size estimate: it drops `INTERNAL_FIELDS`
  (`rowid`, `content_hash`) everywhere except `_envelope`, relativizes
  non-anchor paths against `corpus_root`, and collapses `map_only`/
  `content_included` into `view`. Tools shape their own rows (field selection +
  fold); the central pass only does the generic scrub. `read_next` is one
  payload-level channel — never attached per item.
- `navigator.api.search` returns lean rows: locators + `snippet` + `rrf_score`
  (the one kept ranking signal) + `fields_hit`. No `body`, no raw
  `bm25_score`/`dense_distance` in agent rows; full bodies are
  `search_read --expanded`. `md status` returns the headline (state +
  `recommended_action` + counts) by default; `scopes`/`pending_files`/
  `folder_breakdown` move behind `--expanded`. `navigator.pick` re-derives
  per-file headings from disk when a map omits them, so `md ls` can drop heading
  trees from its bounded default while `md extract` still works on any map.
- `navigator.status_core` owns status facts/state/deltas and config merge;
  `navigator.status_render` owns human text; `navigator.index_status` is a
  legacy adapter only and must not re-export private core helpers.
- `navigator.index_guidance` owns agent-facing index warmup command strings:
  dry-run, confirm and scoped re-run examples. Human guidance must preserve
  parent-corpus scope plus `path_include` / `path_exclude`; do not hand-build
  parallel `md index ...` strings in feature modules.
- `navigator.index_build.ensure_index(dry_run=True)` is the only readonly
  index estimate path. `_ensure_index_unlocked` is a write-path helper and must
  not grow a second dry-run branch.
- Read APIs never delete or rebuild vector indexes. If a caller asks for
  `no_cache`, the public API returns a structured `md_index` dry-run
  `read_next` instead of mutating cache state inside a read path.
- `navigator.workflows.*` imports only navigator/library code, never `md_cli`,
  `subprocess`, or serialization. Workflow modules may compose public
  primitives or delegate to a domain adapter, but they must not lazy-write
  profile caches or import backend internals directly.
- `navigator.*` library modules do not import `md_cli`.
- `navigator.api` is the installed `md` callable facade for atomic tools, not a
  second backend owner. Domain adapters live in focused modules
  (`api_graph.py`, `api_search.py`, `api_audit.py`, `api_profile.py`) and
  `api.py` re-exports the stable atomic public call surface.
- Audit detection lives in `navigator.audit`. CLI routing, Markdown rendering
  and severity scoring stay split into `audit_cli.py`, `audit_render.py` and
  `audit_severity.py`; do not grow `audit.py` back into a 1000-line catch-all.
- `navigator.markdown_io` is the canonical Markdown/link parser. Graph modules
  may resolve graph-specific edges, but must not maintain a second wikilink or
  markdown-link parser.
- `navigator.link_graph.iter_explicit_link_edges` is the canonical explicit
  Markdown edge iterator for frontmatter links, wikilinks and Markdown links.
  `read-related --check-links` reuses it instead of resolving the same edge
  families again.
- Graph-facing wrappers live in `navigator.api_graph` and must use the shared
  graph helpers (`_graph_args`, `_graph_docs`, `_graph_scan_docs`, or their
  direct successor) so `.md-tools.toml` graph filters and direct API filters
  merge in one place. Graph helpers typed for `GraphArgs` must not receive
  `types.SimpleNamespace` or other ad-hoc namespaces; construct `GraphArgs`
  explicitly.
- Graph writes use named `navigator.graph_core.DocWrite` entries and
  `write_doc_plan`, which stages all target documents before replacing them
  and restores originals on failure. `api_graph` mutators must not grow
  per-file write loops for related graph updates.
- `md --help`, `md tools`, and help paths stay lazy and do not import heavy
  dependencies.
- Agent-facing response snapshots cover every `TOOLS_BY_ID` entry and must not
  suggest legacy `md_navigator.py` commands outside explicit diagnostics such
  as `md_ping.navigator_script`.

## Snapshot

`tests/golden/mcp-tool-snapshot.json` is the frozen contract. Regenerate with:

```bash
python3 scripts/generate-mcp-tool-snapshot.py
```

If the snapshot changes, update `src/md_cli/catalog.py` in the same change and
run the lock tests.
