from __future__ import annotations

import json
from typing import Any, Callable

from . import envelope
from .corpus_state import quick_corpus_state
from .result import ToolResult


def run_tool(tool_name: str, handler_run: Callable[[Any], ToolResult], args: Any) -> int:
    result = handler_run(args)
    if not getattr(args, "json", False) and isinstance(result.payload, dict) and "_human" in result.payload:
        print(result.payload["_human"])
        return result.exit_code
    wrapped = envelope.wrap(
        result.payload,
        tool_name=tool_name,
        args=vars(args),
        corpus_state=quick_corpus_state(
            envelope.resolve_corpus_root(vars(args)),
            path_include=getattr(args, "path_include", None),
            path_exclude=getattr(args, "path_exclude", None),
        ),
        lock=result.lock,
    )
    print(json.dumps(wrapped, ensure_ascii=False, separators=(",", ":")))
    return result.exit_code
