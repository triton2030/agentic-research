from __future__ import annotations

from typing import Any, Iterable

from ..api_profile import query_by_type as _query_by_type


def query_by_type(
    corpus: str,
    types: Iterable[str] | str,
    *,
    filter: str | None = None,
    limit: int | None = None,
    compact: bool = False,
    expanded: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    return _query_by_type(
        corpus,
        types,
        filter=filter,
        limit=limit,
        compact=compact,
        expanded=expanded,
        path_include=path_include,
        path_exclude=path_exclude,
    )
