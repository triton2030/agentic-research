from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

from .config import resolve_filters_for_domain
from .markdown_io import DEFAULT_EXCLUDED_PARTS


def _list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and "," in item:
            out.extend(part.strip() for part in item.split(",") if part.strip())
        elif item:
            out.append(str(item))
    return out


def _ns(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def _default_paths(paths: Iterable[str] | str | None) -> list[str]:
    values = _list(paths)
    return values or ["."]


def _exit(payload: dict[str, Any], code: int) -> dict[str, Any]:
    payload["_exit_code"] = code
    return payload


def _index_missing(corpus: str | Path) -> bool:
    root = Path(corpus).expanduser().resolve()
    return not (root / ".md-navigator" / "index.sqlite").exists()


def _graph_args(paths: Iterable[str] | str | None = None, **kwargs: Any) -> SimpleNamespace:
    return _ns(
        paths=_default_paths(paths),
        path_include=_list(kwargs.get("path_include")),
        path_exclude=_list(kwargs.get("path_exclude")),
        no_default_excludes=bool(kwargs.get("no_default_excludes", False)),
    )


def ping() -> dict[str, object]:
    return {
        "name": "md-tools",
        "version": "0.7.0",
        "navigator_package": "navigator",
        "graph_package": "navigator.graph",
    }


def corpus_scan(root: str | Path = ".") -> dict[str, object]:
    repo_root = Path(root).expanduser().resolve()
    corpora: list[dict[str, object]] = []
    unindexed: list[dict[str, object]] = []

    for current, dirnames, filenames in __import__("os").walk(repo_root):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in DEFAULT_EXCLUDED_PARTS
            and not (name.startswith(".") and name not in {".", ".."})
        ]
        current_path = Path(current)
        index_path = current_path / ".md-navigator" / "index.sqlite"
        has_index = index_path.exists()
        if has_index:
            stat = index_path.stat()
            corpora.append(
                {
                    "root": str(current_path),
                    "index_path": str(index_path),
                    "last_touched": stat.st_mtime,
                    "index_size_bytes": stat.st_size,
                }
            )
        md_count = sum(1 for name in filenames if name.endswith((".md", ".mdx")))
        if md_count and not has_index:
            unindexed.append({"folder": str(current_path), "md_files": md_count})

    corpus_roots = [Path(str(item["root"])) for item in corpora]
    uncovered = [
        item
        for item in unindexed
        if not any(Path(str(item["folder"])).is_relative_to(corpus) for corpus in corpus_roots)
    ]
    return {
        "repo_root": str(repo_root),
        "corpora": corpora,
        "unindexed_with_md": uncovered,
        "excluded_dirs_skipped": sorted(DEFAULT_EXCLUDED_PARTS),
    }


def ls(
    path: str,
    *,
    max_heading_level: int | None = None,
    match: str | None = None,
    with_tokens: bool = False,
    with_link_counts: bool = False,
) -> dict[str, Any]:
    from .folder_map import apply_match_filter, build_map

    data = build_map(
        Path(path),
        max_heading_level or 6,
        with_tokens=with_tokens,
        with_link_counts=with_link_counts,
    )
    return apply_match_filter(data, match or "")


def toc(
    path: str,
    *,
    max_heading_level: int | None = None,
    match: str | None = None,
    with_tokens: bool = False,
    with_link_counts: bool = False,
) -> dict[str, Any]:
    return ls(
        path,
        max_heading_level=max_heading_level,
        match=match,
        with_tokens=with_tokens,
        with_link_counts=with_link_counts,
    )


def extract(
    map_data: dict[str, Any] | str,
    *,
    files: str | None = None,
    headings: str | None = None,
    extract: bool = False,
    token_budget: int | None = None,
) -> dict[str, Any]:
    from .pick import parse_csv, pick_items

    data = json.loads(map_data) if isinstance(map_data, str) else map_data
    return pick_items(
        data,
        parse_csv(files or ""),
        parse_csv(headings or ""),
        bool(extract),
        int(token_budget or 0),
    )


def read_related(
    *,
    paths: Iterable[str] | str,
    scan: str | None = None,
    include: str | None = None,
    mode: str | None = None,
    anchor_aware: bool = False,
    token_budget: int | None = None,
    semantic_radius: int | None = None,
    check_links: bool = False,
    link_distance_threshold: float | None = None,
) -> dict[str, Any]:
    from .related import collect_related_items

    args = _ns(
        paths=_list(paths),
        scan=scan or ".",
        include=include or "self,frontmatter,wikilinks,markdown-links,backlinks",
        mode=mode or "full",
        anchor_aware=anchor_aware,
        token_budget=int(token_budget or 0),
        semantic_radius=int(semantic_radius or 0),
        check_links=check_links,
        link_distance_threshold=float(link_distance_threshold or 0.4),
    )
    return collect_related_items(args)


def importance(corpus: str, *, top: int | None = None, sort_by: str | None = None) -> dict[str, Any]:
    from .importance import importance_rows

    root = Path(corpus).expanduser()
    selected_sort = sort_by or "pagerank"
    rows = importance_rows(root, top=max(1, int(top or 10)), sort_by=selected_sort)
    return {"root": str(root.resolve()), "sort_by": selected_sort, "files": rows}


def status(
    corpus: str,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    max_heading_level: int | None = None,
    max_auto_embed: int | None = None,
    embed_model: str | None = None,
    embedding_api_url: str | None = None,
    embedding_timeout: float | None = None,
    cache_dir: str | None = None,
) -> dict[str, Any]:
    from .cli_common import SEARCH_DEFAULT_EMBEDDING_API_URL, SEARCH_DEFAULT_EMBEDDING_TIMEOUT
    from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
    from .folder_map import build_map
    from .index_build import (
        DEFAULT_MAX_AUTO_EMBED,
        _chunks_for_item,
        ensure_index,
        pending_files_for_items,
    )
    from .index_meta import _index_dir_for_corpus, resolve_embed_model_for_corpus
    from .index_status import _build_folder_breakdown, _combine_file_delta, _detect_excluded, _state_payload
    from .sections import build_items_from_map

    corpus_root = Path(corpus).expanduser().resolve()
    if not corpus_root.exists():
        return _exit({"command": "status", "error": f"Path does not exist: {corpus_root}", "state": "ERROR"}, 2)
    path_include, path_exclude = resolve_filters_for_domain(
        corpus_root, domain="index",
        path_include=path_include, path_exclude=path_exclude,
    )
    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    selected_model = resolve_embed_model_for_corpus(corpus_root, embed_model, cache_root=cache_root)
    index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = index_dir / "index.sqlite"
    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
    map_data = build_map(corpus_root, max_heading_level or 6, with_tokens=False)
    if not map_data["files"]:
        return _exit({"command": "status", "corpus": str(corpus_root), "error": "No Markdown files", "state": "EMPTY"}, 1)
    scoped = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    if not scoped["files"]:
        return _exit({"command": "status", "corpus": str(corpus_root), "error": "Path filters matched no Markdown files", "state": "EMPTY"}, 1)

    cap = DEFAULT_MAX_AUTO_EMBED if max_auto_embed is None else int(max_auto_embed)
    scopes_payload: list[dict[str, Any]] = []
    totals = {"added_sections": 0, "removed_sections": 0, "pending_chunks": 0, "drift_count": 0}

    if not db_path.exists():
        for scope in ("sections", "descriptions"):
            items = build_items_from_map(scoped, scope=scope)
            pending = sum(len(_chunks_for_item(item)) for item in items)
            pending_files = pending_files_for_items(items)
            totals["added_sections"] += len(items)
            totals["pending_chunks"] += pending
            scopes_payload.append(
                {
                    "scope": scope,
                    "added_sections": len(items),
                    "removed_sections": 0,
                    "pending_files": pending_files,
                    "removed_files": [],
                    "reused": 0,
                    "pending_chunks": pending,
                    "total_sections_in_scope": 0,
                }
            )
        state = "NO_INDEX"
        return {
            "command": "status",
            "corpus": str(corpus_root),
            "index_path": str(db_path),
            "index_exists": False,
            "last_touched": None,
            "model": selected_model,
            "path_scope": {"include": include_patterns or None, "exclude": exclude_patterns or None},
            "scopes": scopes_payload,
            "folder_breakdown": _build_folder_breakdown(scoped, corpus_root, db_path, cache_root),
            "excluded": {
                "by_default_present": _detect_excluded(corpus_root),
                "by_path_exclude": exclude_patterns or [],
                "by_path_include": include_patterns or [],
            },
            **totals,
            "pending_files": _combine_file_delta(scopes_payload, "pending_files", ("added_sections", "pending_chunks")),
            "removed_files": [],
            "metadata_mismatch": False,
            "delta_too_large": False,
            "max_auto_embed": cap,
            "state": state,
            **_state_payload(state, corpus_root),
        }

    import datetime

    metadata_mismatch = False
    delta_too_large = False
    reused = 0
    for scope in ("sections", "descriptions"):
        items = build_items_from_map(scoped, scope=scope)
        _, stats = ensure_index(
            corpus_root,
            scope,
            items,
            selected_model,
            embedding_api_url=embedding_api_url or SEARCH_DEFAULT_EMBEDDING_API_URL,
            embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
            cache_root=cache_root,
            max_auto_embed=None if cap == 0 else cap,
            dry_run=True,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
        scopes_payload.append(
            {
                "scope": scope,
                "added_sections": stats["added_sections"],
                "removed_sections": stats["removed_sections"],
                "pending_files": stats.get("pending_files", []),
                "removed_files": stats.get("removed_files", []),
                "reused": stats["reused"],
                "pending_chunks": stats["pending_chunks"],
                "total_sections_in_scope": stats["total_sections_in_scope"],
                "metadata_mismatch": stats.get("metadata_mismatch", False),
                "delta_too_large": stats.get("delta_too_large", False),
            }
        )
        totals["added_sections"] += stats["added_sections"]
        totals["removed_sections"] += stats["removed_sections"]
        totals["pending_chunks"] += stats["pending_chunks"]
        reused += stats["reused"]
        metadata_mismatch = metadata_mismatch or bool(stats.get("metadata_mismatch", False))
        delta_too_large = delta_too_large or bool(stats.get("delta_too_large", False))

    if metadata_mismatch:
        state = "NEEDS_REBUILD"
    elif totals["added_sections"] == 0 and totals["removed_sections"] == 0:
        state = "FRESH"
    elif delta_too_large:
        state = "NEEDS_WARMUP"
    else:
        state = "HEALTHY"
    return {
        "command": "status",
        "corpus": str(corpus_root),
        "index_path": str(db_path),
        "index_exists": True,
        "last_touched": datetime.datetime.fromtimestamp(db_path.stat().st_mtime).isoformat(),
        "model": selected_model,
        "path_scope": {"include": include_patterns or None, "exclude": exclude_patterns or None},
        "scopes": scopes_payload,
        "folder_breakdown": _build_folder_breakdown(scoped, corpus_root, db_path, cache_root),
        "excluded": {
            "by_default_present": _detect_excluded(corpus_root),
            "by_path_exclude": exclude_patterns or [],
            "by_path_include": include_patterns or [],
        },
        **totals,
        "pending_files": _combine_file_delta(scopes_payload, "pending_files", ("added_sections", "pending_chunks")),
        "removed_files": _combine_file_delta(scopes_payload, "removed_files", ("removed_sections",)),
        "reused": reused,
        "metadata_mismatch": metadata_mismatch,
        "delta_too_large": delta_too_large,
        "max_auto_embed": cap,
        "state": state,
        **_state_payload(state, corpus_root),
    }


def scan(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(paths, path_include=path_include, path_exclude=path_exclude)
    docs = graph_mod.load_docs(args.paths, root, args)
    findings = [finding for doc in docs for finding in graph_mod.scan_doc(doc)]
    return _exit(
        {"command": "scan", "targets": len(docs), "issues": [graph_mod.finding_data(f) for f in findings]},
        1 if findings else 0,
    )


def check(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(paths, path_include=path_include, path_exclude=path_exclude)
    docs = graph_mod.load_docs(args.paths, root, args)
    findings = graph_mod.check_graph(docs, root)
    return _exit(
        {"command": "check", "targets": len(docs), "issues": [graph_mod.finding_data(f) for f in findings]},
        1 if findings else 0,
    )


def health(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(paths, path_include=path_include, path_exclude=path_exclude)
    docs = graph_mod.load_docs(args.paths, root, args)
    return {"command": "health", **graph_mod.health_report(docs, root)}


def cycles(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(paths, path_include=path_include, path_exclude=path_exclude)
    docs = graph_mod.load_docs(args.paths, root, args)
    found = graph_mod.find_edit_after_edit_cycles(docs, root)
    return _exit(
        {"command": "cycles", "targets": len(docs), "cycles": [[graph_mod.doc_data(doc) for doc in cycle] for cycle in found]},
        1 if found else 0,
    )


def deps(
    path: str,
    *,
    scan: str | None = None,
    depth: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    selected_depth = int(depth or 1)
    if selected_depth < 1:
        return _exit({"command": "deps", "error": "depth_must_be_positive"}, 2)
    root = graph_mod.repo_root()
    target = (root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not target.exists():
        return _exit({"command": "deps", "error": "path_not_found", "path": path}, 2)
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(scan or ".", path_include=path_include, path_exclude=path_exclude)
    doc = graph_mod.load_doc(target, root)
    scan_root = (root / scan).resolve() if scan else root
    all_docs = graph_mod.load_docs([str(scan_root)], root, args)
    return {"command": "deps", "depth": selected_depth, **graph_mod.dependency_report(doc, all_docs, root, selected_depth)}


def impact(
    path: str,
    *,
    scan: str | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(scan or ".", path_include=path_include, path_exclude=path_exclude)
    doc = graph_mod.load_target_doc(path, root)
    scan_root = (root / scan).resolve() if scan else root
    all_docs = graph_mod.load_docs([str(scan_root)], root, args)
    return {"command": "impact", **graph_mod.impact_report(doc, all_docs, root, scan)}


def preflight(
    path: str,
    *,
    scan: str | None = None,
    depth: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    selected_depth = int(depth or 2)
    if selected_depth < 1:
        return _exit({"command": "preflight", "error": "depth_must_be_positive"}, 2)
    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(scan or ".", path_include=path_include, path_exclude=path_exclude)
    doc = graph_mod.load_target_doc(path, root)
    scan_root = (root / scan).resolve() if scan else root
    all_docs = graph_mod.load_docs([str(scan_root)], root, args)
    report = graph_mod.preflight_report(doc, all_docs, root, selected_depth, scan)
    return _exit(
        {"command": "preflight", "depth": selected_depth, **report},
        1 if graph_mod.report_has_blockers(report) else 0,
    )


def changed(
    *,
    scan: str | None = None,
    depth: int | None = None,
    base: str | None = None,
    since: str | None = None,
    staged: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from . import graph as graph_mod

    selected_depth = int(depth or 2)
    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(scan or ".", path_include=path_include, path_exclude=path_exclude)
    args.depth = selected_depth
    args.base = base
    args.since = since
    args.staged = staged
    all_docs = graph_mod.load_docs([str((root / scan).resolve() if scan else root)], root, args)
    reports: list[dict[str, Any]] = []
    deleted: list[str] = []
    for changed_path in graph_mod.changed_markdown_paths(root, args):
        if not changed_path.exists():
            deleted.append(str(graph_mod.safe_rel(changed_path, root)))
            continue
        reports.append(graph_mod.preflight_report(graph_mod.load_doc(changed_path, root), all_docs, root, selected_depth, scan))
    return _exit(
        {
            "command": "changed",
            "since": "STAGED" if staged else (since or base or "HEAD"),
            "depth": selected_depth,
            "reports": reports,
            "deleted": deleted,
        },
        1 if any(graph_mod.report_has_blockers(report) for report in reports) or deleted else 0,
    )


def _index_warmup(corpus: str | Path) -> dict[str, Any]:
    return _exit(
        {
            "error": "index_warmup_required",
            "corpus": str(Path(corpus).expanduser().resolve()),
            "self_repair": "Run md index --dry-run, review cost, then confirm.",
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
) -> tuple[dict[str, Any] | None, int, tuple[Any, ...] | None]:
    from .cli_common import SEARCH_DEFAULT_EMBEDDING_API_URL, SEARCH_DEFAULT_EMBEDDING_TIMEOUT
    from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
    from .folder_map import build_map
    from .index import _index_dir_for_corpus, ensure_index
    from .index_meta import resolve_embed_model_for_corpus
    from .sections import build_items_from_map, build_sections_from_map

    corpus_root = Path(corpus).expanduser().resolve()
    if not corpus_root.exists():
        return _exit({"error": "path_not_found", "corpus": str(corpus_root)}, 2), 2, None
    if _index_missing(corpus_root):
        return _index_warmup(corpus_root), 4, None

    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
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

    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    selected_model = resolve_embed_model_for_corpus(corpus_root, embed_model, cache_root=cache_root)
    if no_cache:
        target = _index_dir_for_corpus(corpus_root, cache_root=cache_root)
        for name in ("index.sqlite", "index.sqlite-wal", "index.sqlite-shm"):
            (target / name).unlink(missing_ok=True)
        return _index_warmup(corpus_root), 4, None
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
        )
    except (ModuleNotFoundError, RuntimeError) as exc:
        return _exit({"error": "dependency_failed", "detail": str(exc)}, 3), 3, None
    if index_stats.get("delta_too_large") and not allow_partial_index:
        return _index_warmup(corpus_root), 4, None
    return None, 0, (
        corpus_root,
        conn,
        scoped_map,
        items,
        index_stats,
        selected_model,
        include_patterns,
        exclude_patterns,
        embedding_api_url or SEARCH_DEFAULT_EMBEDDING_API_URL,
        float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
    )


def search(corpus: str, query: str, **kwargs: Any) -> dict[str, Any]:
    if _index_missing(corpus):
        return _index_warmup(corpus)
    search_mod = importlib.import_module("navigator.search")
    from .filters import apply_path_filters as apply_row_filters
    from .rerank import DEFAULT_RERANK_API_URL, DEFAULT_RERANK_MODEL, DEFAULT_RERANK_TIMEOUT, DEFAULT_RERANK_TOP_N
    from .rerank import doc_text_for_rerank, rerank_documents
    from .sections import _should_subchunk

    _corpus_root_for_filters = Path(corpus).expanduser().resolve()
    kwargs["path_include"], kwargs["path_exclude"] = resolve_filters_for_domain(
        _corpus_root_for_filters, domain="index",
        path_include=kwargs.get("path_include"),
        path_exclude=kwargs.get("path_exclude"),
    )
    scope = kwargs.get("scope") or search_mod.SEARCH_DEFAULT_SCOPE
    limit = int(kwargs.get("limit") or search_mod.SEARCH_DEFAULT_LIMIT)
    candidates = int(kwargs.get("candidates") or search_mod.SEARCH_DEFAULT_CANDIDATES)
    error, _code, context = _sections_index_context(
        corpus,
        scope=scope,
        allow_partial_index=True,
        **_index_context_kwargs(kwargs),
    )
    if error is not None:
        return error
    assert context is not None
    (
        corpus_root,
        conn,
        map_data,
        items,
        index_stats,
        selected_model,
        include_patterns,
        exclude_patterns,
        embedding_api_url,
        embedding_timeout,
    ) = context
    weights = {"description": 5.0, "title": 0.0, "heading": 0.0, "body": 1.0} if scope == "descriptions" else dict(search_mod.SEARCH_DEFAULT_WEIGHTS)
    bm25_results = search_mod._search_bm25(
        conn,
        query,
        scope,
        weights,
        candidates,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    try:
        dense_results = search_mod._search_dense(
            conn,
            selected_model,
            query,
            scope,
            candidates,
            embedding_api_url,
            embedding_timeout,
            corpus_root=corpus_root,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
    except RuntimeError as exc:
        return _exit({"error": "dependency_failed", "detail": str(exc)}, 3)
    rrf_scores = search_mod._rrf_merge(bm25_results, dense_results, k=search_mod.SEARCH_RRF_K)
    fused_rowids = [rid for rid, _ in sorted(rrf_scores.items(), key=lambda item: -item[1])[:candidates]]
    rerank_on = bool(kwargs.get("rerank", False))
    filter_on = bool(include_patterns or exclude_patterns)
    hydrate_n = len(fused_rowids) if rerank_on or filter_on else limit
    hydrated = search_mod._hydrate_rows(conn, fused_rowids)[:hydrate_n]
    if filter_on:
        hydrated = apply_row_filters(hydrated, include_patterns, exclude_patterns)
    if rerank_on:
        hydrated = hydrated[: int(kwargs.get("rerank_top_n") or DEFAULT_RERANK_TOP_N)]
    else:
        hydrated = hydrated[:limit]
    rerank_scores: dict[int, float] = {}
    rerank_applied = False
    if rerank_on and hydrated:
        docs = [doc_text_for_rerank(row["relative_path"], row["heading_chain"], row["body"]) for row in hydrated]
        try:
            ordered = rerank_documents(
                query,
                docs,
                model=kwargs.get("rerank_model") or DEFAULT_RERANK_MODEL,
                api_url=kwargs.get("rerank_api_url") or DEFAULT_RERANK_API_URL,
                timeout=float(kwargs.get("rerank_timeout") or DEFAULT_RERANK_TIMEOUT),
                corpus_root=corpus_root,
            )
        except RuntimeError:
            ordered = []
        if ordered:
            reordered: list[dict[str, Any]] = []
            for idx, score in ordered:
                if 0 <= idx < len(hydrated):
                    row = hydrated[idx]
                    rerank_scores[row["rowid"]] = score
                    reordered.append(row)
            if reordered:
                hydrated = reordered
                rerank_applied = True
    hydrated = hydrated[:limit]
    fresh_file_id_by_path = {file["relative_path"]: file["id"] for file in map_data["files"]}
    final_results = []
    dropped_stale_path = 0
    for row in hydrated:
        path = row["relative_path"]
        fresh_fid = fresh_file_id_by_path.get(path)
        if fresh_fid is None:
            dropped_stale_path += 1
            continue
        row["file_id"] = fresh_fid
        old_sid = str(row.get("section_id") or "")
        row["section_id"] = f"{fresh_fid}.{old_sid.split('.', 1)[1]}" if "." in old_sid else str(fresh_fid)
        final_results.append(row)
    bm25_map = dict(bm25_results)
    dense_map = dict(dense_results)
    for row in final_results:
        rid = row["rowid"]
        row["bm25_score"] = bm25_map.get(rid)
        row["dense_distance"] = dense_map.get(rid)
        row["rrf_score"] = rrf_scores.get(rid, 0.0)
        row["rerank_score"] = rerank_scores.get(rid)
        row["fields_hit"] = search_mod._fields_hit(conn, rid, query)
        row["snippet"] = search_mod._snippet_for(row["body"], query)
    subchunked_count = sum(1 for item in items if scope == "sections" and _should_subchunk(item["body"] or ""))
    output = {
        "root": str(corpus_root),
        "query": query,
        "scope": scope,
        "engine": {
            "bm25f": True,
            "dense": True,
            "embed_model": selected_model,
            "embedding_api_url": embedding_api_url,
            "rerank": rerank_applied,
            "rerank_model": (kwargs.get("rerank_model") or DEFAULT_RERANK_MODEL) if rerank_applied else None,
            "rerank_top_n": (kwargs.get("rerank_top_n") or DEFAULT_RERANK_TOP_N) if rerank_applied else None,
            "rerank_api_url": (kwargs.get("rerank_api_url") or DEFAULT_RERANK_API_URL) if rerank_applied else None,
            "path_include": include_patterns,
            "path_exclude": exclude_patterns,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "items_indexed": len(items),
            "sections_subchunked": subchunked_count,
            "embeddings_cached": index_stats["reused"],
            "embeddings_computed": index_stats["embedded"],
            "sections_removed": index_stats["removed_sections"],
            "bm25_hits": len(bm25_results),
            "dense_hits": len(dense_results),
            "dropped_stale_path": dropped_stale_path,
        },
        "weights": weights,
        "results": final_results,
    }
    partial_index = search_mod._partial_index_payload(index_stats, int(kwargs.get("max_auto_embed") or 50))
    if partial_index:
        output["partial_index"] = partial_index
    return output


def search_read(corpus: str, query: str, **kwargs: Any) -> dict[str, Any]:
    result = search(corpus, query, **kwargs)
    if result.get("error"):
        return result

    budget = int(kwargs.get("token_budget") or 0)
    sections: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    running_tokens = 0
    for row in result.get("results", []):
        tokens = int(row.get("token_count") or 0)
        if budget and running_tokens + tokens > budget:
            dropped.append(
                {
                    "section_id": row.get("section_id"),
                    "relative_path": row.get("relative_path"),
                    "tokens": tokens,
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
        "engine": result.get("engine"),
        "stats": result.get("stats"),
        "partial_index": result.get("partial_index"),
        "sections": sections,
        "token_total": running_tokens,
        "token_budget": budget,
        "dropped_by_budget": dropped,
    }
    if not sections:
        return _exit({**payload, "empty": True}, 1)
    return payload


def overlaps(corpus: str, **kwargs: Any) -> dict[str, Any]:
    if _index_missing(corpus):
        return _index_warmup(corpus)
    from .overlaps import compute_overlaps

    _corpus_root_for_filters = Path(corpus).expanduser().resolve()
    kwargs["path_include"], kwargs["path_exclude"] = resolve_filters_for_domain(
        _corpus_root_for_filters, domain="index",
        path_include=kwargs.get("path_include"),
        path_exclude=kwargs.get("path_exclude"),
    )
    error, _code, context = _sections_index_context(corpus, scope="sections", **_index_context_kwargs(kwargs))
    if error is not None:
        return error
    assert context is not None
    corpus_root, conn, map_data, _items, index_stats, selected_model, include_patterns, exclude_patterns, embedding_api_url, _timeout = context
    args = _ns(
        threshold=float(kwargs.get("threshold") or 0.85),
        top=int(kwargs.get("top") or 20),
        min_tokens=int(kwargs.get("min_tokens") or 30),
        include_same_file=bool(kwargs.get("include_same_file", False)),
        embed_model=selected_model,
        embedding_api_url=embedding_api_url,
        cache_dir=kwargs.get("cache_dir"),
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    output = compute_overlaps(corpus_root, conn, map_data, index_stats, args)
    if output is None:
        return _exit({"empty": True, "reason": "Need at least 2 chunks to compare."}, 1)
    return output


def repeated_concepts(corpus: str, **kwargs: Any) -> dict[str, Any]:
    if _index_missing(corpus):
        return _index_warmup(corpus)
    from .repeated_concepts import compute_repeated_concepts

    _corpus_root_for_filters = Path(corpus).expanduser().resolve()
    kwargs["path_include"], kwargs["path_exclude"] = resolve_filters_for_domain(
        _corpus_root_for_filters, domain="index",
        path_include=kwargs.get("path_include"),
        path_exclude=kwargs.get("path_exclude"),
    )
    error, _code, context = _sections_index_context(corpus, scope="sections", **_index_context_kwargs(kwargs))
    if error is not None:
        return error
    assert context is not None
    corpus_root, conn, map_data, _items, index_stats, selected_model, include_patterns, exclude_patterns, embedding_api_url, _timeout = context
    args = _ns(
        threshold=float(kwargs.get("threshold") or 0.80),
        top=int(kwargs.get("top") or 30),
        min_tokens=int(kwargs.get("min_tokens") or 30),
        min_files=int(kwargs.get("min_files") or 2),
        min_sections=int(kwargs.get("min_sections") or 2),
        top_members=int(kwargs.get("top_members") or 5),
        embed_model=selected_model,
        embedding_api_url=embedding_api_url,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    output = compute_repeated_concepts(corpus_root, conn, map_data, index_stats, args)
    if output is None:
        return _exit({"empty": True, "reason": "Need at least 2 chunks to compare."}, 1)
    return output


def audit(corpus: str, **kwargs: Any) -> dict[str, Any]:
    if _index_missing(corpus):
        return _index_warmup(corpus)
    audit_mod = importlib.import_module("navigator.audit")

    _corpus_root_for_filters = Path(corpus).expanduser().resolve()
    kwargs["path_include"], kwargs["path_exclude"] = resolve_filters_for_domain(
        _corpus_root_for_filters, domain="index",
        path_include=kwargs.get("path_include"),
        path_exclude=kwargs.get("path_exclude"),
    )
    error, _code, context = _sections_index_context(corpus, scope="sections", **_index_context_kwargs(kwargs))
    if error is not None:
        return error
    assert context is not None
    corpus_root, conn, map_data, sections, index_stats, selected_model, include_patterns, exclude_patterns, embedding_api_url, _timeout = context
    args = _ns(
        threshold_smear=float(kwargs.get("threshold_smear") or 0.85),
        threshold_drift=float(kwargs.get("threshold_drift") or 0.65),
        threshold_inter=float(kwargs.get("threshold_inter") or 0.40),
        threshold_template=float(kwargs.get("threshold_template") or 0.70),
        threshold_heading_diversity=float(kwargs.get("threshold_heading_diversity") or 0.85),
        min_files_in_family=int(kwargs.get("min_files_in_family") or 3),
        min_sections_per_file=int(kwargs.get("min_sections_per_file") or 5),
        max_concepts=int(kwargs.get("max_concepts") or 10),
        cluster_k=int(kwargs.get("cluster_k") or 8),
        discovery_gap_warn=float(kwargs.get("discovery_gap_warn") or 0.25),
        discovery_gap_crit=float(kwargs.get("discovery_gap_crit") or 0.50),
        embed_model=selected_model,
        embedding_api_url=embedding_api_url,
        cache_dir=kwargs.get("cache_dir"),
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    findings: list[dict[str, Any]] = []
    findings.extend(audit_mod._check_discovery_gaps(map_data, args))
    findings.extend(audit_mod._check_smeared_owner_truth(corpus_root, conn, map_data, index_stats, args))
    findings.extend(audit_mod._check_tight_duplicates(corpus_root, conn, map_data, index_stats, args))
    findings.extend(audit_mod._check_template_family(map_data, args))
    findings.extend(audit_mod._check_intra_file_drift(conn, map_data, args))
    findings.extend(audit_mod._check_cluster_folder_mismatch(corpus_root, args))
    order = {audit_mod.SEVERITY_CRITICAL: 0, audit_mod.SEVERITY_WARNING: 1, audit_mod.SEVERITY_INFO: 2}
    findings.sort(key=lambda item: (order.get(item["severity"], 3), item["class"]))
    return {
        "root": str(corpus_root),
        "health": audit_mod.compute_health(findings),
        "severity_counts": audit_mod.severity_counts(findings),
        "thresholds": {
            "smear": args.threshold_smear,
            "drift_cohesion": args.threshold_drift,
            "drift_inter": args.threshold_inter,
            "template_jaccard": args.threshold_template,
            "heading_diversity": args.threshold_heading_diversity,
            "min_files_in_family": args.min_files_in_family,
            "discovery_gap_warn": args.discovery_gap_warn,
            "discovery_gap_crit": args.discovery_gap_crit,
            "min_sections_per_file": args.min_sections_per_file,
            "cluster_k": args.cluster_k,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "sections_indexed": len(sections),
            "embeddings_cached": index_stats["reused"],
            "embeddings_computed": index_stats["embedded"],
        },
        "engine": {"embed_model": selected_model, "embedding_api_url": embedding_api_url},
        "findings": findings,
    }


def init(
    paths: Iterable[str] | str | None = None,
    *,
    dry_run: bool = False,
    confirm: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **_: Any,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(paths, path_include=path_include, path_exclude=path_exclude)
    docs = graph_mod.load_docs(args.paths, root, args)
    targets = [doc for doc in docs if not doc.has_frontmatter]
    target_paths = [str(doc.path) for doc in targets]
    if dry_run or not confirm:
        return {
            "command": "init",
            "dry_run": bool(dry_run),
            "files_to_modify": target_paths,
            "file_count": len(targets),
            "targets": len(docs),
        }
    template = {"description": "TODO", "read-before-edit": [], "edit-after-edit": []}
    for doc in targets:
        graph_mod.write_doc(doc, template, doc.body)
    return {
        "command": "init",
        "targets": len(docs),
        "changed": len(targets),
        "unchanged": len(docs) - len(targets),
        "modified": [str(doc.rel) for doc in targets],
    }


def strip(
    paths: Iterable[str] | str | None = None,
    *,
    also_related_section: bool = False,
    dry_run: bool = False,
    confirm: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **_: Any,
) -> dict[str, Any]:
    from . import graph as graph_mod

    root = graph_mod.repo_root()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="graph",
        path_include=path_include, path_exclude=path_exclude,
    )
    args = _graph_args(paths, path_include=path_include, path_exclude=path_exclude)
    docs = graph_mod.load_docs(args.paths, root, args)
    targets: list[Any] = []
    changes: list[dict[str, Any]] = []
    for doc in docs:
        removed_fields = [key for key in doc.frontmatter if key not in graph_mod.ALLOWED_FIELDS] if doc.has_frontmatter else []
        new_body = doc.body
        section_removed = False
        if also_related_section:
            new_body, section_removed = graph_mod.strip_related_section(doc.body)
        if removed_fields or section_removed:
            targets.append((doc, removed_fields, new_body, section_removed))
            changes.append(
                {
                    "path": str(doc.rel),
                    "removed_fields": removed_fields,
                    "related_section_removed": section_removed,
                }
            )
    target_paths = [str(doc.path) for doc, *_ in targets]
    if dry_run or not confirm:
        return {
            "command": "strip",
            "dry_run": bool(dry_run),
            "files_to_modify": target_paths,
            "file_count": len(targets),
            "also_related_section": also_related_section,
            "changes": changes,
        }
    for doc, _removed_fields, new_body, _section_removed in targets:
        new_data = {key: value for key, value in doc.frontmatter.items() if key in graph_mod.ALLOWED_FIELDS}
        if doc.has_frontmatter:
            graph_mod.write_doc(doc, new_data, new_body)
        else:
            doc.path.write_text(new_body, encoding="utf-8")
    return {
        "command": "strip",
        "targets": len(docs),
        "changed": len(targets),
        "unchanged": len(docs) - len(targets),
        "modified": [str(doc.rel) for doc, *_ in targets],
        "changes": changes,
    }


def index(
    corpus: str,
    *,
    dry_run: bool = False,
    confirm: bool = False,
    batch_size: int | None = None,
    batch_pause_ms: int | None = None,
    max_heading_level: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    embed_model: str | None = None,
    embedding_api_url: str | None = None,
    embedding_timeout: float | None = None,
    cache_dir: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    from .cli_common import SEARCH_DEFAULT_EMBEDDING_API_URL, SEARCH_DEFAULT_EMBEDDING_TIMEOUT
    from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
    from .folder_map import build_map
    from .index_build import _chunks_for_item, ensure_index
    from .index_meta import resolve_embed_model_for_corpus
    from .sections import build_items_from_map

    corpus_root = Path(corpus).expanduser().resolve()
    path_include, path_exclude = resolve_filters_for_domain(
        corpus_root, domain="index",
        path_include=path_include, path_exclude=path_exclude,
    )
    map_data = build_map(corpus_root, max_heading_level or 6, with_tokens=True)
    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
    scoped = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    items_by_scope = {scope: build_items_from_map(scoped, scope=scope) for scope in ("sections", "descriptions")}
    pending_chunks = sum(len(_chunks_for_item(item)) for items in items_by_scope.values() for item in items)
    affected_files = [str(Path(file["path"]).resolve()) for file in scoped.get("files", [])]
    if dry_run or not confirm:
        return {
            "command": "index",
            "dry_run": bool(dry_run),
            "pending_chunks": pending_chunks,
            "added_sections": sum(len(items) for items in items_by_scope.values()),
            "estimated_cost_usd": round(pending_chunks * 0.00002, 4),
            "affected_files": affected_files,
        }
    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    selected_model = resolve_embed_model_for_corpus(corpus_root, embed_model, cache_root=cache_root)
    totals = {"embedded": 0, "reused": 0, "removed_sections": 0}
    for scope, items in items_by_scope.items():
        _, stats = ensure_index(
            corpus_root,
            scope,
            items,
            selected_model,
            embedding_api_url=embedding_api_url or SEARCH_DEFAULT_EMBEDDING_API_URL,
            embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
            cache_root=cache_root,
            max_auto_embed=None,
            batch_size=int(batch_size or 64),
            batch_pause_s=int(batch_pause_ms or 0) / 1000.0,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
        totals["embedded"] += stats.get("embedded", 0)
        totals["reused"] += stats.get("reused", 0)
        totals["removed_sections"] += stats.get("removed_sections", 0)
    return {"command": "index", "corpus": str(corpus_root), **totals}


def profile_sections(
    corpus: str,
    *,
    dry_run: bool = False,
    confirm: bool = False,
    limit: int | None = None,
    force: bool = False,
    mode: str | None = None,
    model: str | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **_: Any,
) -> dict[str, Any]:
    from .filters import normalize_path_filter_patterns
    from .folder_map import build_map
    from .section_profile import open_profile_db, profile_corpus, profile_rows

    root = Path(corpus).expanduser().resolve()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="index",
        path_include=path_include, path_exclude=path_exclude,
    )
    include_patterns = normalize_path_filter_patterns(path_include, root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, root)
    if dry_run or (mode in {"llm", "auto"} and not confirm):
        map_data = build_map(root, 6, with_tokens=False)
        section_count = sum(len(file.get("headings", [])) for file in map_data.get("files", []))
        per_unit = 0.0005 if mode in {"llm", "auto"} else 0
        return {
            "command": "profile-sections",
            "dry_run": bool(dry_run),
            "sections_to_profile_estimate": section_count,
            "mode": mode or "heuristic",
            "estimated_cost_usd": round(section_count * per_unit, 4),
            "affected_files": [str(Path(file["path"]).resolve()) for file in map_data.get("files", [])],
        }
    try:
        conn = open_profile_db(root)
    except RuntimeError as exc:
        return _exit({"command": "profile-sections", "error": str(exc)}, 2)
    stats = profile_corpus(
        conn,
        limit=limit,
        corpus_root=root,
        force=force,
        mode=mode,
        model=model,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    rows = profile_rows(conn, limit=10, corpus_root=root, path_include=include_patterns, path_exclude=exclude_patterns)
    return {"command": "profile-sections", "root": str(root), **stats, "sample": rows}


def refactor_candidates(corpus: str, *, compact: bool = False, **kwargs: Any) -> dict[str, Any]:
    from .filters import normalize_path_filter_patterns
    from .refactor_proposals import refactor_candidates as compute
    from .section_profile import open_profile_db

    root = Path(corpus).expanduser().resolve()
    merged_include, merged_exclude = resolve_filters_for_domain(
        root, domain="index",
        path_include=kwargs.get("path_include"),
        path_exclude=kwargs.get("path_exclude"),
    )
    try:
        conn = open_profile_db(root)
    except RuntimeError as exc:
        return _exit({"error": "index_warmup_required", "corpus": str(root), "detail": str(exc)}, 4)
    payload = compute(
        conn,
        corpus_root=root,
        top=3 if compact else int(kwargs.get("top") or 10),
        uniqueness_threshold=float(kwargs.get("uniqueness_threshold") or 0.35),
        owner_confidence_threshold=float(kwargs.get("owner_confidence_threshold") or 0.45),
        path_include=normalize_path_filter_patterns(merged_include, root),
        path_exclude=normalize_path_filter_patterns(merged_exclude, root),
    )
    if compact:
        payload["compact"] = True
        payload["proposals"] = [
            {"proposal_type": item.get("proposal_type"), "confidence": item.get("confidence"), "why": item.get("why")}
            for item in payload.get("proposals", [])
        ]
    return payload


def query_by_type(
    corpus: str,
    types: Iterable[str] | str,
    *,
    filter: str | None = None,
    limit: int | None = None,
    compact: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from .filters import normalize_path_filter_patterns
    from .section_profile import open_profile_db, profile_rows, profile_unprofiled_sections

    root = Path(corpus).expanduser().resolve()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="index",
        path_include=path_include, path_exclude=path_exclude,
    )
    selected_types = _list(types)
    try:
        conn = open_profile_db(root)
    except RuntimeError as exc:
        return _exit({"error": "index_warmup_required", "corpus": str(root), "detail": str(exc)}, 4)
    include_patterns = normalize_path_filter_patterns(path_include, root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, root)
    profile_unprofiled_sections(conn, corpus_root=root, path_include=include_patterns, path_exclude=exclude_patterns)
    rows = profile_rows(
        conn,
        types=selected_types,
        filter_text=filter,
        limit=min(int(limit or 50), 10) if compact else int(limit or 50),
        corpus_root=root,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    if compact:
        rows = [
            {"path": row["relative_path"], "subject": row["profile"]["subject"], "type": row["profile"]["type"]}
            for row in rows
        ]
    return {
        "types": selected_types,
        "path_include": include_patterns,
        "path_exclude": exclude_patterns,
        "sections": rows,
        "compact": compact,
    }
