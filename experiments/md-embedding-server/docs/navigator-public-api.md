---
description: "Importable navigator API boundary and graph wrapper contract for the md CLI."
read-before-edit: []
edit-after-edit: []
---
# Navigator public API

`navigator.api` is the importable library surface for the new `md` CLI. CLI
handlers call these functions directly and return `ToolResult`; they do not
invoke legacy argparse commands, parse stdout, or build envelopes.

Agent-facing reading functions follow the same context ladder as the CLI:
normal output is a map/preview (`expanded=False`, `content_included=False`);
full bodies or full evidence require `expanded=True` or legacy `mode="full"`
where the mode already existed.

Status and warmup payloads expose the next safe action as structured data:
`recommended_action` inside status/corpus state, and `suggested_index_args` /
`suggested_retry_args` plus `read_next` on warmup errors. Callers should
preserve those args as-is, especially when a child corpus is served by an
indexed parent via translated `path_include` / `path_exclude`. Read APIs do
not honor `no_cache` by deleting/rebuilding indexes; they return a
`cache_rebuild_requires_index` payload that points at a `md_index` dry-run.

The package root also exposes the same atomic callable names (`navigator.search`,
`navigator.preflight`, etc.) re-exported from `navigator.api`. Nine names that
also have a backing module on disk (`search`, `audit`, `index`, `overlaps`,
`repeated_concepts`, `importance`, `coherence_audit`, `corpus_scan`, `walk`)
resolve to the **real module object** made callable, so `from navigator import
search` yields the module (attributes and monkeypatching stay reachable) while
`navigator.search(...)` still calls `api.search`. See "Callable modules" below.

## Atomic functions

- `audit(corpus, **kwargs) -> dict`
- `check(paths=None, path_include=None, path_exclude=None) -> dict`
- `cluster(corpus, k=None, seed=None, path_include=None, path_exclude=None, cache_dir=None) -> dict`
- `corpus_scan(root=".") -> dict`
- `cycles(paths=None, path_include=None, path_exclude=None) -> dict`
- `deps(path, scan=None, depth=None, path_include=None, path_exclude=None) -> dict`
- `extract(map_data, files=None, headings=None, extract=False, token_budget=None) -> dict`
- `health(paths=None, path_include=None, path_exclude=None) -> dict`
- `impact(path, scan=None, path_include=None, path_exclude=None) -> dict`
- `importance(corpus, top=None, sort_by=None) -> dict`
- `index(corpus, dry_run=False, confirm=False, batch_size=None, batch_pause_ms=None, max_heading_level=None, path_include=None, path_exclude=None, **kwargs) -> dict`
- `init(paths=None, dry_run=False, confirm=False, path_include=None, path_exclude=None, **kwargs) -> dict`
- `ls(path, max_heading_level=None, match=None, with_tokens=False, with_link_counts=False) -> dict`
- `overlaps(corpus, **kwargs) -> dict`
- `ping() -> dict`
- `preflight(path, scan=None, depth=None, path_include=None, path_exclude=None) -> dict`
- `profile_sections(corpus, dry_run=False, confirm=False, limit=None, force=False, mode=None, model=None, path_include=None, path_exclude=None, **kwargs) -> dict`
- `read_related(paths, scan=None, include=None, mode=None, expanded=False, anchor_aware=False, token_budget=None, semantic_radius=None, check_links=False, link_distance_threshold=None) -> dict`
- `repeated_concepts(corpus, **kwargs) -> dict`
- `scan(paths=None, path_include=None, path_exclude=None) -> dict`
- `search(corpus, query, **kwargs) -> dict`
- `search_read(corpus, query, expanded=False, token_budget=None, **kwargs) -> dict`
- `status(corpus, path_include=None, path_exclude=None, max_heading_level=None, max_auto_embed=None, **kwargs) -> dict`
- `strip(paths=None, also_related_section=False, dry_run=False, confirm=False, path_include=None, path_exclude=None, **kwargs) -> dict`
- `toc(path, max_heading_level=None, match=None, with_tokens=False, with_link_counts=False) -> dict`

## Workflows

Workflow modules live in `navigator.workflows`, compose atomic public functions,
return dictionaries, and never depend on the CLI package. Profile-backed
workflows are thin aliases over the profile domain adapter; they return
`profile_required` instead of lazily writing profile cache rows.

- `workflows.orient(corpus, top=None, max_heading_level=None, compact=False, expanded=False) -> dict`
- `workflows.edit_context(path, mode=None, expanded=False, scan=None, depth=None, query=None, corpus=None) -> dict`
- `workflows.refactor_candidates(corpus, **kwargs) -> dict`
- `workflows.query_by_type(corpus, types, **kwargs) -> dict`
- `workflows.section_blast_radius(path, corpus, query, heading_id=None, scan=None, depth=None, limit=None, path_include=None, path_exclude=None) -> dict`

## Boundary

- `src/md_cli/handlers/*.py` imports catalog targets and returns `ToolResult`.
- `src/md_cli/runner.py` is the single JSON + envelope writer.
- `navigator.api` and `navigator.workflows` never import `md_cli`.

## Graph Wrapper Contract

Graph-facing public functions in `navigator.api`
(`scan`, `check`, `health`, `cycles`, `deps`, `impact`, `preflight`,
`init`, `strip`) are the installed `md` path. The public names are re-exported
through `navigator.api`, while implementation lives in `navigator.api_graph`.
They build a `GraphArgs` dataclass with `_graph_args`, then load documents
through `_graph_docs` or `_graph_scan_docs`.

`navigator.api_graph` imports graph primitives from `graph_core`,
`graph_edges`, and `graph_reports`. Git-diff file selection is not owned by `md`.

That adapter is also where `.md-tools.toml` `[graph]` filters merge with
direct `path_include` / `path_exclude` API inputs. Callers may pass a list,
other iterable, generator or single string; `normalize_path_filter_patterns`
keeps a single string as one pattern instead of iterating over characters.

Graph mutators (`init`, `strip`) write through
`navigator.graph_core.write_doc_plan`, not per-file write loops. The plan
stages every target first and restores originals if any replacement fails.

Graph mutators route through `navigator.api` / `api_graph` and `write_doc_plan`,
not per-file write loops. Do not pass `types.SimpleNamespace` or other ad-hoc
namespaces to graph helpers typed for `GraphArgs`; construct `GraphArgs`
explicitly.

## Callable modules: rationale & limits

`navigator/__init__.py` keeps most public names as plain callables re-exported
from `navigator.api`. Nine names that also have a backing module on disk
(`search`, `audit`, `index`, `overlaps`, `repeated_concepts`, `importance`,
`coherence_audit`, `corpus_scan`, `walk`) are bound via `_bind_callable_module`,
which swaps the real module's `__class__` to a `_CallableModule` subclass whose
`__call__` delegates to the matching `navigator.api` function.

**Dual contract obtained:**

- `navigator.search(corpus, query, …)` → calls `api.search` (function form,
  used by handlers and most tests).
- `from navigator import search as search_mod` → yields the actual
  `navigator/search.py` module; `search_mod.X` resolves real module attributes
  (constants, helpers, symbols to monkeypatch).

**Why it is load-bearing:**

`tests/test_rerank.py`, `tests/test_contract_fixes.py` and `tests/conftest.py`
install ``monkeypatch.setattr(search_mod, "rerank_documents", fake)`` after
``from navigator import search as search_mod``. Because the public name *is* the
on-disk module (only its `__class__` is swapped), the patched symbol is the one
the real search code path reads. The callable `__class__` is the only addition;
module-attribute access, monkeypatching and introspection otherwise behave like
a normal module — no proxy object stands in between.

**Known limits:**

- `mypy` may not infer the callable signature through the swapped `__class__`;
  prefer explicit `from navigator.api import X` for type-checked call sites.
- Pickling a callable-module public name is not supported.

**When safe to remove:**

The `_CallableModule` mechanism can be dropped once all callers use explicit
forms — callable: `from navigator.api import X`; module access: `from navigator
import X` (which, after removal, resolves to the on-disk module directly because
the `__class__` swap is gone). Then delete `_CallableModule` /
`_bind_callable_module` and the binding loop in `__init__.py`, and this section.
