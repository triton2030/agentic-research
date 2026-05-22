from __future__ import annotations

import json
from typing import Any, Callable

from . import brief as brief_module
from . import envelope
from .corpus_state import quick_corpus_state
from .result import ToolResult


def run_tool(tool_name: str, handler_run: Callable[[Any], ToolResult], args: Any) -> int:
    result = handler_run(args)
    if not getattr(args, "json", False) and isinstance(result.payload, dict) and "_human" in result.payload:
        print(result.payload["_human"])
        return result.exit_code
    brief_text: str | None = None
    if isinstance(result.payload, dict):
        embedded = result.payload.pop("_brief", None)
        if isinstance(embedded, str):
            brief_text = embedded
        else:
            brief_text = brief_module.render(tool_name, result.payload)
    wrapped = envelope.wrap(
        result.payload,
        tool_name=tool_name,
        args=vars(args),
        corpus_state=quick_corpus_state(envelope.resolve_corpus_root(vars(args))),
        lock=result.lock,
    )
    if getattr(args, "brief", False) and brief_text is not None:
        print(brief_text)
        for step in wrapped.get("_envelope", {}).get("next_step", []):
            cmd = step.get("command")
            if cmd:
                print(f"\nNext: {cmd}")
        return result.exit_code
    print(json.dumps(wrapped, ensure_ascii=False, separators=(",", ":")))
    return result.exit_code
