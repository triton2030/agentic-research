from __future__ import annotations

from pathlib import Path
from typing import Iterable


def canon_check(
    file: str,
    corpus: str | None = None,
    *,
    mode: str | None = None,
    limit: int | None = None,
    max_claims: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    rerank: bool = False,
    expanded: bool = False,
) -> dict[str, object]:
    from navigator.canon import run_canon_check

    selected_corpus = corpus or str(Path(file).expanduser().resolve().parent)
    return run_canon_check(
        file,
        selected_corpus,
        mode=mode,
        limit=limit,
        max_claims=max_claims,
        path_include=path_include,
        path_exclude=path_exclude,
        rerank=rerank,
        expanded=expanded,
    )
