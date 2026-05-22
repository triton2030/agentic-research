from __future__ import annotations

import json
import sys

from md_cli.catalog import from_catalog, get_tool
from md_cli.handlers._generic import _call, _load_target
from md_cli.result import ToolResult


@from_catalog('md_extract')
def run(args) -> ToolResult:
    kwargs = {
        key: value
        for key, value in vars(args).items()
        if not key.startswith("_") and key not in {"subcommand", "json"}
    }
    if kwargs.get("map_stdin") and kwargs.get("map_data"):
        return ToolResult(
            {"error": "usage_error", "detail": "--map-stdin and --map-data are mutually exclusive"},
            2,
        )
    if kwargs.pop("map_stdin", False):
        try:
            raw = sys.stdin.read()
            kwargs["map_data"] = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            return ToolResult({"error": "usage_error", "detail": f"--map-stdin received invalid JSON: {exc}"}, 2)
    elif not kwargs.get("map_data"):
        return ToolResult({"error": "usage_error", "detail": "md extract requires --map-data or --map-stdin"}, 2)
    spec = get_tool("md_extract")
    return _call(_load_target(spec.library_function), kwargs)
