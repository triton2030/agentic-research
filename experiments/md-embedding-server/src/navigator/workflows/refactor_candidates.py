from __future__ import annotations

from typing import Any

from ..api_profile import refactor_candidates as _refactor_candidates


def refactor_candidates(
    corpus: str,
    *,
    compact: bool = False,
    expanded: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    return _refactor_candidates(
        corpus,
        compact=compact,
        expanded=expanded,
        **kwargs,
    )
