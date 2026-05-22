# Architecture Lock

Phase 2 can start only when the lock tests are green.

## Invariants

- `catalog.py` has exactly 29 tool entries and matches the MCP snapshot names,
  schemas, annotations and canonical signatures.
- `md_cli.handlers.*` modules return `ToolResult`; they do not print JSON, call
  `sys.exit`, or import `md_cli.envelope`.
- `md_cli.runner` is the only owner of `envelope.wrap` and `print(json.dumps)`.
- `navigator.workflows.*` imports only navigator/library code, never `md_cli`,
  `subprocess`, or serialization.
- `navigator.*` library modules do not import `md_cli`.
- `md --help`, `md tools`, and help paths stay lazy and do not import heavy
  dependencies.

## Snapshot

`tests/golden/mcp-tool-snapshot.json` is the frozen contract. Regenerate with:

```bash
python3 scripts/generate-mcp-tool-snapshot.py
```

If the snapshot changes, update `src/md_cli/catalog.py` in the same change and
run the lock tests.

