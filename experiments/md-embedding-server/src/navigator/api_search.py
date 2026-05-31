from __future__ import annotations

from typing import Any

from .api_index_context import (
    DEFAULT_SEARCH_READ_TOKEN_BUDGET,
    _index_context_kwargs,
    _sections_index_context,
)
from .api_utils import _exit, _read_next, _reject_unknown_kwargs

_SEARCH_KWARGS = {
    "scope",
    "limit",
    "candidates",
    "max_heading_level",
    "max_auto_embed",
    "path_include",
    "path_exclude",
    "embed_model",
    "embedding_api_url",
    "embedding_timeout",
    "cache_dir",
    "no_cache",
    "rerank",
    "rerank_model",
    "rerank_api_url",
    "rerank_timeout",
    "rerank_top_n",
}

_SEARCH_READ_KWARGS = _SEARCH_KWARGS | {"expanded", "token_budget"}

_SEARCH_READ_NEXT_KEYS = (
    "scope",
    "candidates",
    "max_heading_level",
    "rerank",
    "path_exclude",
)


def _search_read_args(
    corpus: str,
    query: str,
    kwargs: dict[str, Any],
    *,
    limit: int,
    path_include: list[str] | None = None,
) -> dict[str, Any]:
    args = {
        "corpus": corpus,
        "query": query,
        "expanded": True,
        "limit": limit,
        "token_budget": (
            kwargs["token_budget"]
            if "token_budget" in kwargs
            else DEFAULT_SEARCH_READ_TOKEN_BUDGET
        ),
    }
    for key in _SEARCH_READ_NEXT_KEYS:
        if key in kwargs:
            args[key] = kwargs[key]
    args["path_include"] = path_include if path_include is not None else kwargs.get("path_include")
    return args

def _search_read_next(
    corpus: str,
    query: str,
    row: dict[str, Any],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    return _read_next(
        "md_search_read",
        _search_read_args(
            corpus,
            query,
            kwargs,
            limit=1,
            path_include=[row["relative_path"]] if row.get("relative_path") else None,
        ),
        "Read the body for this selected section.",
    )

def _search_map_row(
    corpus: str,
    query: str,
    row: dict[str, Any],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    mapped = {
        "section_id": row.get("section_id"),
        "file_id": row.get("file_id"),
        "relative_path": row.get("relative_path"),
        "start_line": row.get("start_line"),
        "heading_chain": row.get("heading_chain"),
        "heading_text": row.get("heading_text"),
        "token_count": int(row.get("token_count") or 0),
        "rrf_score": row.get("rrf_score"),
        "rerank_score": row.get("rerank_score"),
        "snippet": row.get("snippet"),
        "description": row.get("file_description"),
    }
    mapped["read_next"] = [_search_read_next(corpus, query, mapped, kwargs)]
    return mapped

def search(corpus: str, query: str, **kwargs: Any) -> dict[str, Any]:
    from .search import (
        DEFAULT_RERANK_API_URL,
        DEFAULT_RERANK_MODEL,
        DEFAULT_RERANK_TIMEOUT,
        DEFAULT_RERANK_TOP_N,
        SEARCH_DEFAULT_CANDIDATES,
        SEARCH_DEFAULT_LIMIT,
        SEARCH_DEFAULT_SCOPE,
        search_payload,
    )

    _reject_unknown_kwargs("search", kwargs, _SEARCH_KWARGS)
    scope = kwargs.get("scope") or SEARCH_DEFAULT_SCOPE
    limit = int(kwargs.get("limit") or SEARCH_DEFAULT_LIMIT)
    candidates = int(kwargs.get("candidates") or SEARCH_DEFAULT_CANDIDATES)
    error, _code, context = _sections_index_context(
        corpus,
        scope=scope,
        allow_partial_index=True,
        **_index_context_kwargs(kwargs),
    )
    if error is not None:
        return error
    assert context is not None
    try:
        return search_payload(
            corpus_root=context.corpus_root,
            conn=context.conn,
            map_data=context.map_data,
            items=context.items,
            index_stats=context.index_stats,
            selected_model=context.selected_model,
            include_patterns=context.include_patterns,
            exclude_patterns=context.exclude_patterns,
            embedding_api_url=context.embedding_api_url,
            embedding_timeout=context.embedding_timeout,
            query=query,
            scope=scope,
            limit=limit,
            candidates=candidates,
            rerank=bool(kwargs.get("rerank", False)),
            rerank_model=kwargs.get("rerank_model") or DEFAULT_RERANK_MODEL,
            rerank_api_url=kwargs.get("rerank_api_url") or DEFAULT_RERANK_API_URL,
            rerank_timeout=float(kwargs.get("rerank_timeout") or DEFAULT_RERANK_TIMEOUT),
            rerank_top_n=int(kwargs.get("rerank_top_n") or DEFAULT_RERANK_TOP_N),
            max_auto_embed=int(kwargs.get("max_auto_embed") or 50),
        )
    except RuntimeError as exc:
        return _exit({"error": "dependency_failed", "detail": str(exc)}, 3)

def search_read(corpus: str, query: str, **kwargs: Any) -> dict[str, Any]:
    _reject_unknown_kwargs("search_read", kwargs, _SEARCH_READ_KWARGS)
    search_kwargs = {key: value for key, value in kwargs.items() if key in _SEARCH_KWARGS}
    result = search(corpus, query, **search_kwargs)
    if result.get("error"):
        return result

    expanded = bool(kwargs.get("expanded", False))
    if not expanded:
        sections = [
            _search_map_row(corpus, query, row, kwargs)
            for row in result.get("results", [])
        ]
        payload = {
            "root": result.get("root"),
            "query": result.get("query"),
            "scope": result.get("scope"),
            "expanded": False,
            "map_only": True,
            "content_included": False,
            "engine": result.get("engine"),
            "stats": result.get("stats"),
            "partial_index": result.get("partial_index"),
            "sections": sections,
            "candidate_token_total": sum(int(row.get("token_count") or 0) for row in sections),
            "token_total": 0,
            "token_budget": 0,
            "token_budget_defaulted": False,
            "dropped_by_budget": [],
            "read_next": [
                _read_next(
                    "md_search_read",
                    _search_read_args(
                        corpus,
                        query,
                        kwargs,
                        limit=int(kwargs.get("limit") or len(sections) or 1),
                    ),
                    "Expand selected search results into section bodies.",
                )
            ],
        }
        if not sections:
            return _exit({**payload, "empty": True}, 1)
        return payload

    raw_budget = kwargs.get("token_budget")
    budget_defaulted = raw_budget is None
    budget = DEFAULT_SEARCH_READ_TOKEN_BUDGET if budget_defaulted else int(raw_budget or 0)
    sections: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    running_tokens = 0
    for row in result.get("results", []):
        tokens = int(row.get("token_count") or 0)
        if budget and running_tokens + tokens > budget:
            remaining = max(budget - running_tokens, 0)
            if remaining > 0:
                content = row.get("body") or ""
                truncated = content[: remaining * 4].rstrip()
                running_tokens += remaining
                sections.append(
                    {
                        "section_id": row.get("section_id"),
                        "file_id": row.get("file_id"),
                        "relative_path": row.get("relative_path"),
                        "start_line": row.get("start_line"),
                        "heading_chain": row.get("heading_chain"),
                        "heading_text": row.get("heading_text"),
                        "token_count": tokens,
                        "included_token_count": remaining,
                        "truncated_by_budget": True,
                        "rrf_score": row.get("rrf_score"),
                        "rerank_score": row.get("rerank_score"),
                        "snippet": row.get("snippet"),
                        "content": f"{truncated}\n\n...[truncated to ~{budget} approx tokens]\n",
                    }
                )
                dropped.append(
                    {
                        "section_id": row.get("section_id"),
                        "relative_path": row.get("relative_path"),
                        "tokens": tokens,
                        "included_tokens": remaining,
                        "reason": "truncated",
                    }
                )
                continue
            dropped.append(
                {
                    "section_id": row.get("section_id"),
                    "relative_path": row.get("relative_path"),
                    "tokens": tokens,
                    "reason": "over_budget",
                }
            )
            continue
        running_tokens += tokens
        sections.append(
            {
                "section_id": row.get("section_id"),
                "file_id": row.get("file_id"),
                "relative_path": row.get("relative_path"),
                "start_line": row.get("start_line"),
                "heading_chain": row.get("heading_chain"),
                "heading_text": row.get("heading_text"),
                "token_count": tokens,
                "rrf_score": row.get("rrf_score"),
                "rerank_score": row.get("rerank_score"),
                "snippet": row.get("snippet"),
                "content": row.get("body") or "",
            }
        )

    payload = {
        "root": result.get("root"),
        "query": result.get("query"),
        "scope": result.get("scope"),
        "expanded": True,
        "map_only": False,
        "content_included": True,
        "engine": result.get("engine"),
        "stats": result.get("stats"),
        "partial_index": result.get("partial_index"),
        "sections": sections,
        "token_total": running_tokens,
        "token_budget": budget,
        "token_budget_defaulted": budget_defaulted,
        "dropped_by_budget": dropped,
    }
    if not sections:
        return _exit({**payload, "empty": True}, 1)
    return payload
