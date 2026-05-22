from __future__ import annotations

from md_cli.catalog import from_catalog, get_tool
from md_cli.handlers._extract_input import process_extract_input
from md_cli.handlers._generic import _call, _load_target
from md_cli.result import ToolResult


@from_catalog('md_extract')
def run(args) -> ToolResult:
    kwargs = {
        key: value
        for key, value in vars(args).items()
        if not key.startswith("_") and key not in {"subcommand", "json", "brief"}
    }
    kwargs, error = process_extract_input(kwargs)
    if error is not None:
        return ToolResult(error, 2)
    spec = get_tool("md_extract")
    return _call(_load_target(spec.library_function), kwargs)
