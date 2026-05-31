from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

from .api_audit import audit, cluster, overlaps, repeated_concepts
from .api_graph import (
    check,
    cycles,
    deps,
    health,
    impact,
    init,
    preflight,
    scan,
    strip,
)
from .api_index_context import DEFAULT_SEARCH_READ_TOKEN_BUDGET
from .api_profile import index, profile_sections
from .api_search import search, search_read
from .api_utils import _list, _ns
from .markdown_io import DEFAULT_EXCLUDED_PARTS


def ping() -> dict[str, object]:
    return {
        "name": "md-tools",
        "version": "0.7.0",
        "navigator_package": "navigator",
        "graph_package": "navigator.graph_core+navigator.graph_reports",
    }


def corpus_scan(root: str | Path = ".") -> dict[str, object]:
    repo_root = Path(root).expanduser().resolve()
    corpora: list[dict[str, object]] = []
    unindexed: list[dict[str, object]] = []

    for current, dirnames, filenames in os.walk(repo_root):
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


LS_DEFAULT_TOP = 50


def ls(
    path: str,
    *,
    max_heading_level: int | None = None,
    match: str | None = None,
    with_tokens: bool = False,
    with_link_counts: bool = False,
    expanded: bool = False,
) -> dict[str, Any]:
    from .folder_map import apply_match_filter, build_map, fold_by_folder

    data = build_map(
        Path(path),
        max_heading_level or 6,
        with_tokens=with_tokens,
        with_link_counts=with_link_counts,
    )
    data = apply_match_filter(data, match or "")
    files = data.get("files", [])
    data["expanded"] = bool(expanded)
    data["summary"] = {
        "file_count": data.get("file_count", len(files)),
        "description_gaps": data.get("description_gap_count", 0),
        "folders": fold_by_folder(files),
    }
    if not expanded:
        kept = files[:LS_DEFAULT_TOP]
        if len(files) > LS_DEFAULT_TOP:
            data["files_truncated"] = True
        # Bounded map: drop per-file heading trees (md extract re-derives them
        # on demand). Full headings via --expanded / md toc.
        data["files"] = [{k: v for k, v in f.items() if k != "headings"} for f in kept]
    return data


def toc(
    path: str,
    *,
    max_heading_level: int | None = None,
    match: str | None = None,
    with_tokens: bool = False,
    with_link_counts: bool = False,
) -> dict[str, Any]:
    # toc is the heading-detail view of a chosen path — keep it full (expanded),
    # the breadth cap is for corpus-wide `ls`.
    return ls(
        path,
        max_heading_level=max_heading_level,
        match=match,
        with_tokens=with_tokens,
        with_link_counts=with_link_counts,
        expanded=True,
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
    expanded: bool = False,
    anchor_aware: bool = False,
    token_budget: int | None = None,
    semantic_radius: int | None = None,
    check_links: bool = False,
    link_distance_threshold: float | None = None,
) -> dict[str, Any]:
    from .related import collect_related_items

    selected_mode = "full" if expanded or mode == "full" else "preview"
    args = _ns(
        paths=_list(paths),
        scan=scan or ".",
        include=include or "self,frontmatter,wikilinks,markdown-links,backlinks",
        mode=selected_mode,
        expanded=selected_mode == "full",
        anchor_aware=anchor_aware,
        token_budget=int(token_budget or 0),
        semantic_radius=int(semantic_radius or 0),
        check_links=check_links,
        link_distance_threshold=float(link_distance_threshold or 0.4),
    )
    return collect_related_items(args)


def coherence_audit(
    path: str,
    *,
    anchor: str | None = None,
    scan: str | None = None,
    depth: int | None = None,
    token_budget: int | None = None,
) -> dict[str, Any]:
    from .coherence_audit import coherence_audit as _coherence_audit

    return _coherence_audit(
        path,
        anchor=anchor,
        scan=scan,
        depth=depth,
        token_budget=token_budget,
    )


def walk(
    path: str,
    *,
    anchor: str,
    scan: str | None = None,
    depth: int | None = None,
    token_budget: int | None = None,
) -> dict[str, Any]:
    from .walk import walk_chain

    return walk_chain(
        path,
        anchor=anchor,
        scan=scan,
        depth=depth,
        token_budget=token_budget,
    )


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
    expanded: bool = False,
) -> dict[str, Any]:
    from .status_core import status_payload

    corpus_root = Path(corpus).expanduser().resolve()
    return status_payload(
        corpus_root,
        path_include=path_include,
        path_exclude=path_exclude,
        max_heading_level=max_heading_level,
        max_auto_embed=max_auto_embed,
        embed_model=embed_model,
        embedding_api_url=embedding_api_url,
        embedding_timeout=embedding_timeout,
        cache_dir=cache_dir,
        expanded=expanded,
    )
