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
`suggested_retry_args` on warmup errors. Callers should preserve those args
as-is, especially when a child corpus is served by an indexed parent via
translated `path_include` / `path_exclude`.

The package root also exposes the same callable names (`navigator.search`,
`navigator.preflight`, etc.). Because old tests and scripts still import
modules like `navigator.search`, the root uses callable module proxies during
the transition: module attributes stay reachable, while the package-level name
is callable.

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
return dictionaries, and never depend on the CLI package.

- `workflows.orient(corpus, top=None, max_heading_level=None, compact=False, expanded=False) -> dict`
- `workflows.edit_context(path, mode=None, expanded=False, scan=None, depth=None, query=None, corpus=None) -> dict`
- `workflows.refactor_candidates(corpus, **kwargs) -> dict`
- `workflows.query_by_type(corpus, types, **kwargs) -> dict`
- `workflows.section_blast_radius(path, corpus, query, heading_id=None, scan=None, depth=None, limit=None, path_include=None, path_exclude=None) -> dict`

## Boundary

- `src/md_cli/handlers/*.py` imports catalog targets and returns `ToolResult`.
- `src/md_cli/runner.py` is the single JSON + envelope writer.
- `navigator.api` and `navigator.workflows` never import `md_cli`.
- Legacy `navigator.*.cmd_*` argparse functions remain only for
  `scripts/md_navigator.py` / `scripts/md_graph.py` compatibility during the
  big-bang migration window.

## Graph Wrapper Contract

Graph-facing public functions in `navigator.api`
(`scan`, `check`, `health`, `cycles`, `deps`, `impact`, `preflight`,
`init`, `strip`) are the installed `md` path. They build an
`argparse.Namespace` with `_graph_args`, then load documents through
`_graph_docs` or `_graph_scan_docs`.

`navigator.api` imports graph primitives from `graph_core`, `graph_edges`, and
`graph_reports`; it does not import legacy `navigator.graph`. Git-diff file
selection is not owned by `md`.

That facade is also where `.md-tools.toml` `[graph]` filters merge with direct
`path_include` / `path_exclude` API inputs. Callers may pass a list, other
iterable, generator or single string; `normalize_path_filter_patterns` keeps a
single string as one pattern instead of iterating over characters.

Do not bypass this path through legacy `navigator.graph.cmd_*`, and do not pass
`types.SimpleNamespace` to graph helpers typed for `argparse.Namespace`.

## Proxy magic: rationale & limits

`navigator/__init__.py` installs `_CallableModuleProxy` + `_NavigatorPackage`
so that every public name behaves as **both** a callable and a module.

**Dual contract obtained:**

- `navigator.search(corpus, query, …)` → calls `api.search` (function form,
  used by handlers and most tests).
- `navigator.search.X` → resolves attributes on the `navigator/search.py`
  module (constants, helpers, things to monkeypatch).

**Why it is load-bearing:**

`tests/test_rerank.py` and `tests/test_contract_fixes.py` install
``monkeypatch.setattr(search_mod, "rerank_documents", fake)`` after
``from navigator import search as search_mod``. The proxy's
``__setattr__`` forwards the assignment to the underlying
``navigator.search`` module so the patched symbol is visible to the real
search code path. Without the proxy, ``search_mod`` would be a function
object and ``setattr`` would silently attach a noop attribute.

**Known limits:**

- `mypy` may not infer attribute access through the proxy correctly;
  prefer explicit `from navigator.search import X` for type-checked code.
- Pickling proxy instances is not supported (function + module composite
  has no portable representation).
- `inspect.getmembers(navigator.search)` returns proxy attributes, not
  the underlying module attributes — beware in introspection tooling.

**When safe to remove:**

The proxy can be deleted once **all** callers migrate to explicit forms:

- callable: `from navigator.api import X` (for `X(...)`).
- module access: `from navigator import X` then `X.helper(...)` — note
  that after removal, `from navigator import X` will resolve to the
  module on disk because the function-form alias in `__init__.py` will
  be gone.

Once monkeypatch fixtures and downstream callers are migrated, drop
`_CallableModuleProxy` / `_NavigatorPackage`, replace the api re-exports
in `__init__.py` with `from . import <module>` lines, and remove this
section.
