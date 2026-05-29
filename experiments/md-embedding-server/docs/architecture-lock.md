---
description: "Architecture invariants for md CLI catalog, handler, runner, and library boundaries."
read-before-edit: []
edit-after-edit: []
---
# Architecture Lock

Phase 2 can start only when the lock tests are green.

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
- Agent-facing broad outputs use the context ladder: normal mode returns
  maps/previews with `expanded:false` and `content_included:false`; full
  content or evidence is explicit `--expanded`. Legacy `--compact` must not
  become the documented default language.
- `navigator.status_core` owns status facts/state/deltas and config merge;
  `navigator.status_render` owns human text; `navigator.index_status` is a
  legacy adapter only and must not re-export private core helpers.
- `navigator.index_guidance` owns agent-facing index warmup command strings:
  dry-run, confirm and scoped re-run examples. Human guidance must preserve
  parent-corpus scope plus `path_include` / `path_exclude`; do not hand-build
  parallel `md index ...` strings in feature modules.
- `navigator.workflows.*` imports only navigator/library code, never `md_cli`,
  `subprocess`, or serialization.
- `navigator.*` library modules do not import `md_cli`.
- `navigator.api` is the installed `md` callable facade. Graph-facing wrappers
  must use the shared graph helpers (`_graph_args`, `_graph_docs`,
  `_graph_scan_docs`, or their direct successor) so `.md-tools.toml` graph
  filters and direct API filters merge in one place. Graph helpers typed for
  `argparse.Namespace` must not receive `types.SimpleNamespace`.
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
