from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection
from typing import Any, Iterable

from .api_utils import _exit, _list, _read_next
from .config import resolve_filters_for_domain


def _index_missing(corpus: str | Path, *, cache_root: Path | None = None) -> bool:
    from .index import _index_dir_for_corpus

    root = Path(corpus).expanduser().resolve()
    return not (_index_dir_for_corpus(root, cache_root=cache_root, create=False) / "index.sqlite").exists()


def _index_warmup(
    corpus: str | Path,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    cache_root: Path | None = None,
) -> dict[str, Any]:
    from .index_meta import find_parent_indexed_corpus, path_include_for_parent_corpus

    root = Path(corpus).expanduser().resolve()
    parent = find_parent_indexed_corpus(root, cache_root=cache_root)
    suggested_index_args: dict[str, Any] = {"corpus": str(root), "dry_run": True}
    suggested_retry_args: dict[str, Any] = {"corpus": str(root)}
    if parent is not None:
        parent_include = path_include_for_parent_corpus(root, parent, _list(path_include))
        parent_exclude = (
            path_include_for_parent_corpus(root, parent, _list(path_exclude))
            if path_exclude
            else []
        )
        suggested_index_args = {
            "corpus": str(parent),
            "path_include": parent_include,
            "dry_run": True,
        }
        suggested_retry_args = {
            "corpus": str(parent),
            "path_include": parent_include,
        }
        if parent_exclude:
            suggested_index_args["path_exclude"] = parent_exclude
            suggested_retry_args["path_exclude"] = parent_exclude
    return _exit(
        {
            "error": "index_warmup_required",
            "corpus": str(root),
            "suggested_index_args": suggested_index_args,
            "suggested_retry_args": suggested_retry_args,
            "read_next": [
                _read_next(
                    "md_index",
                    suggested_index_args,
                    "Warm the semantic index before retrying this read.",
                )
            ],
        },
        4,
    )


def _index_busy(
    corpus: str | Path,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    cache_root: Path | None = None,
) -> dict[str, Any]:
    from .index_meta import _index_dir_for_corpus

    root = Path(corpus).expanduser().resolve()
    lock_path = _index_dir_for_corpus(root, cache_root=cache_root, create=False) / "index.lock"
    status_args: dict[str, Any] = {"corpus": str(root)}
    index_args: dict[str, Any] = {"corpus": str(root), "dry_run": True}
    include_values = _list(path_include)
    exclude_values = _list(path_exclude)
    if include_values:
        status_args["path_include"] = include_values
        index_args["path_include"] = include_values
    if exclude_values:
        status_args["path_exclude"] = exclude_values
        index_args["path_exclude"] = exclude_values
    return _exit(
        {
            "error": "index_busy",
            "corpus": str(root),
            "lock_path": str(lock_path),
            "reason": "Another md index writer holds the corpus index lock; retry after it finishes.",
            "suggested_status_args": status_args,
            "suggested_index_args": index_args,
            "read_next": [
                _read_next(
                    "md_status",
                    status_args,
                    "Check whether the current index writer has finished.",
                ),
                _read_next(
                    "md_index",
                    index_args,
                    "Preview remaining index warmup work after the lock clears.",
                ),
            ],
        },
        4,
    )


_INDEX_CONTEXT_KWARGS = {
    "max_heading_level",
    "max_auto_embed",
    "path_include",
    "path_exclude",
    "embed_model",
    "embedding_api_url",
    "embedding_timeout",
    "cache_dir",
    "no_cache",
}

DEFAULT_SEARCH_READ_TOKEN_BUDGET = 3000


@dataclass(frozen=True)
class IndexContext:
    corpus_root: Path
    conn: Connection
    map_data: dict[str, object]
    items: list[dict[str, object]]
    index_stats: dict[str, object]
    selected_model: str
    include_patterns: list[str]
    exclude_patterns: list[str]
    embedding_api_url: str
    embedding_timeout: float


def _index_context_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in kwargs.items() if key in _INDEX_CONTEXT_KWARGS and value is not None}


def _sections_index_context(
    corpus: str,
    *,
    scope: str = "sections",
    max_heading_level: int | None = None,
    max_auto_embed: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    embed_model: str | None = None,
    embedding_api_url: str | None = None,
    embedding_timeout: float | None = None,
    cache_dir: str | None = None,
    no_cache: bool = False,
    allow_partial_index: bool = False,
    wait_for_index_lock: bool = False,
) -> tuple[dict[str, Any] | None, int, IndexContext | None]:
    from .cli_common import SEARCH_DEFAULT_EMBEDDING_API_URL, SEARCH_DEFAULT_EMBEDDING_TIMEOUT
    from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
    from .folder_map import build_map
    from .index import ensure_index
    from .index_meta import IndexLockBusy, resolve_embed_model_for_corpus
    from .sections import build_items_from_map, build_sections_from_map

    corpus_root = Path(corpus).expanduser().resolve()
    if not corpus_root.exists():
        return _exit({"error": "path_not_found", "corpus": str(corpus_root)}, 2), 2, None
    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    path_include, path_exclude = resolve_filters_for_domain(
        corpus_root,
        domain="index",
        path_include=path_include,
        path_exclude=path_exclude,
    )
    if no_cache:
        payload = _index_warmup(
            corpus_root,
            path_include=path_include,
            path_exclude=path_exclude,
            cache_root=cache_root,
        )
        payload.update(
            {
                "error": "cache_rebuild_requires_index",
                "reason": "Read APIs do not delete or rebuild indexes; run md_index as a mutating dry-run/confirm flow.",
            }
        )
        return payload, 4, None
    if _index_missing(corpus_root, cache_root=cache_root) and not no_cache:
        return (
            _index_warmup(
                corpus_root,
                path_include=path_include,
                path_exclude=path_exclude,
                cache_root=cache_root,
            ),
            4,
            None,
        )

    include_patterns = normalize_path_filter_patterns(_list(path_include), corpus_root)
    exclude_patterns = normalize_path_filter_patterns(_list(path_exclude), corpus_root)
    map_data = build_map(corpus_root, max_heading_level or 6, with_tokens=scope != "descriptions")
    scoped_map = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    if not scoped_map["files"]:
        return _exit({"error": "empty", "reason": "Path filters matched no Markdown files.", "corpus": str(corpus_root)}, 1), 1, None
    if scope == "sections":
        items = build_sections_from_map(scoped_map)
    else:
        items = build_items_from_map(scoped_map, scope=scope)
    if not items:
        return _exit({"error": "empty", "reason": "No sections to index.", "corpus": str(corpus_root)}, 1), 1, None

    selected_model = resolve_embed_model_for_corpus(corpus_root, embed_model, cache_root=cache_root)
    cap = 50 if max_auto_embed is None else int(max_auto_embed)
    try:
        conn, index_stats = ensure_index(
            corpus_root,
            scope,
            items,
            selected_model,
            embedding_api_url=embedding_api_url or SEARCH_DEFAULT_EMBEDDING_API_URL,
            embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
            cache_root=cache_root,
            max_auto_embed=None if cap == 0 else cap,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
            wait_for_lock=wait_for_index_lock,
        )
    except IndexLockBusy:
        return (
            _index_busy(
                corpus_root,
                path_include=include_patterns,
                path_exclude=exclude_patterns,
                cache_root=cache_root,
            ),
            4,
            None,
        )
    except (ModuleNotFoundError, RuntimeError) as exc:
        return _exit({"error": "dependency_failed", "detail": str(exc)}, 3), 3, None
    if index_stats.get("delta_too_large") and not allow_partial_index:
        return _index_warmup(corpus_root), 4, None
    return None, 0, IndexContext(
        corpus_root=corpus_root,
        conn=conn,
        map_data=scoped_map,
        items=items,
        index_stats=index_stats,
        selected_model=selected_model,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        embedding_api_url=embedding_api_url or SEARCH_DEFAULT_EMBEDDING_API_URL,
        embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
    )
