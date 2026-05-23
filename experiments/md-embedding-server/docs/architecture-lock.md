---
description: "Architecture invariants for md CLI catalog, handler, runner, and library boundaries."
read-before-edit: []
edit-after-edit: []
---
# Architecture Lock

Phase 2 can start only when the lock tests are green.

## Invariants

- `catalog.py` matches the MCP snapshot names, schemas, annotations and
  canonical signatures. Current generated snapshot count is 30 tools; the
  executable invariant is the catalog/snapshot test, not a hand-maintained
  prose count. Runtime import must not patch `ToolSpec` values; cleanup and
  fingerprint fields belong in the generated snapshot/source data.
- `md_cli.handlers.*` modules return `ToolResult`; they do not print JSON, call
  `sys.exit`, or import `md_cli.envelope`.
- `md_cli.runner` is the only owner of `envelope.wrap` and `print(json.dumps)`.
- `md_cli.next_steps` owns executable `_envelope.next_step` action policy;
  `md_cli.envelope` only normalizes args, estimates size and wraps payloads.
- `navigator.status_core` owns status facts/state/deltas and config merge;
  `navigator.status_render` owns human text; `navigator.index_status` is a
  legacy adapter only and must not re-export private core helpers.
- `navigator.workflows.*` imports only navigator/library code, never `md_cli`,
  `subprocess`, or serialization.
- `navigator.*` library modules do not import `md_cli`.
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
