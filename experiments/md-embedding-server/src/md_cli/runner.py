from __future__ import annotations

import json
from typing import Any, Callable

from . import envelope
from .corpus_state import quick_corpus_state
from .result import ToolResult


# Tools whose catalog `cost` declares no embedding/index dependency (pure
# filesystem or graph readers/mutations, all "Free" with no index/HTTP/LLM).
# For these the corpus index-warmup recommended_action is irrelevant noise — an
# embedding index they never query — so it is dropped from the envelope. Any
# tool that touches the index/embeddings/LLM (search, search_read, overlaps,
# repeated_concepts, audit, refactor_candidates, section_blast_radius, status,
# index, read_related, edit_context, query_by_type, profile_sections, orient)
# is intentionally absent here and keeps the hint; uncertain tools default to
# keeping it so a genuinely useful warmup hint is never hidden.
_FILESYSTEM_ONLY_TOOLS = frozenset(
    {
        "md_check",
        "md_coherence_audit",
        "md_corpus_scan",
        "md_cycles",
        "md_deps",
        "md_extract",
        "md_health",
        "md_impact",
        "md_importance",
        "md_init",
        "md_ls",
        "md_ping",
        "md_preflight",
        "md_scan",
        "md_strip",
        "md_toc",
        "md_walk",
    }
)


def run_tool(tool_name: str, handler_run: Callable[[Any], ToolResult], args: Any) -> int:
    result = handler_run(args)
    if not getattr(args, "json", False) and isinstance(result.payload, dict) and "_human" in result.payload:
        print(result.payload["_human"])
        return result.exit_code
    corpus_state = quick_corpus_state(
        envelope.resolve_corpus_root(vars(args)),
        path_include=getattr(args, "path_include", None),
        path_exclude=getattr(args, "path_exclude", None),
    )
    if tool_name in _FILESYSTEM_ONLY_TOOLS and isinstance(corpus_state, dict):
        corpus_state = {**corpus_state, "recommended_action": None}
    wrapped = envelope.wrap(
        result.payload,
        tool_name=tool_name,
        args=vars(args),
        corpus_state=corpus_state,
        lock=result.lock,
    )
    print(json.dumps(wrapped, ensure_ascii=False, separators=(",", ":")))
    return result.exit_code
