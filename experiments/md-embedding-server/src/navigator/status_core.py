"""Shared status state machine for public API and legacy CLI adapter."""

from __future__ import annotations

import datetime
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .cli_common import SEARCH_DEFAULT_EMBEDDING_API_URL, SEARCH_DEFAULT_EMBEDDING_TIMEOUT
from .config import resolve_filters_for_domain
from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
from .folder_map import build_map
from .index_build import (
    DEFAULT_MAX_AUTO_EMBED,
    _chunks_for_item,
    ensure_index,
    pending_files_for_items,
)
from .index_meta import (
    _index_dir_for_corpus,
    _open_index_readonly,
    resolve_embed_model_for_corpus,
)
from .sections import build_items_from_map


def status_payload(
    corpus: str | Path,
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
    corpus_root = Path(corpus).expanduser().resolve()
    if not corpus_root.exists():
        return _exit(
            {
                "command": "status",
                "error": f"Path does not exist: {corpus_root}",
                "state": "ERROR",
            },
            2,
        )
    path_include, path_exclude = resolve_filters_for_domain(
        corpus_root,
        domain="index",
        path_include=path_include,
        path_exclude=path_exclude,
    )

    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    selected_model = resolve_embed_model_for_corpus(
        corpus_root,
        embed_model,
        cache_root=cache_root,
    )
    index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = index_dir / "index.sqlite"
    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)

    map_data = build_map(corpus_root, max_heading_level or 6, with_tokens=False)
    if not map_data["files"]:
        return _exit(
            {
                "command": "status",
                "corpus": str(corpus_root),
                "error": f"No Markdown files under {corpus_root}",
                "state": "EMPTY",
            },
            1,
        )
    scoped = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    if not scoped["files"]:
        return _exit(
            {
                "command": "status",
                "corpus": str(corpus_root),
                "error": f"Path filters matched no Markdown files under {corpus_root}",
                "state": "EMPTY",
            },
            1,
        )

    raw_cap = DEFAULT_MAX_AUTO_EMBED if max_auto_embed is None else int(max_auto_embed)
    ensure_cap = None if raw_cap == 0 else raw_cap

    if not db_path.exists():
        scopes_payload = _scopes_for_missing_index(scoped)
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
            "excluded": _excluded_payload(corpus_root, include_patterns, exclude_patterns),
            "added_sections": sum(int(scope["added_sections"]) for scope in scopes_payload),
            "removed_sections": 0,
            "pending_chunks": sum(int(scope["pending_chunks"]) for scope in scopes_payload),
            "pending_files": _combine_file_delta(
                scopes_payload,
                "pending_files",
                ("added_sections", "pending_chunks"),
            ),
            "removed_files": [],
            "drift_count": 0,
            "metadata_mismatch": False,
            "delta_too_large": False,
            "max_auto_embed": raw_cap,
            "state": state,
            **_state_payload(
                state,
                corpus_root,
                cache_root=cache_root,
                path_include=include_patterns,
                path_exclude=exclude_patterns,
            ),
        }

    scopes_payload: list[dict[str, Any]] = []
    totals = {
        "added_sections": 0,
        "removed_sections": 0,
        "pending_chunks": 0,
        "reused": 0,
        "metadata_mismatch": False,
        "delta_too_large": False,
    }
    for scope in ("sections", "descriptions"):
        items = build_items_from_map(scoped, scope=scope)
        if not items:
            continue
        try:
            _, stats = ensure_index(
                corpus_root,
                scope,
                items,
                selected_model,
                embedding_api_url=embedding_api_url or SEARCH_DEFAULT_EMBEDDING_API_URL,
                embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
                cache_root=cache_root,
                max_auto_embed=ensure_cap,
                dry_run=True,
                path_include=include_patterns,
                path_exclude=exclude_patterns,
            )
        except ModuleNotFoundError as exc:
            return _exit(
                {
                    "command": "status",
                    "corpus": str(corpus_root),
                    "error": f"Missing Python dependency: {exc}",
                    "state": "DEPENDENCY_ERROR",
                },
                3,
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
        totals["reused"] += stats["reused"]
        totals["metadata_mismatch"] = totals["metadata_mismatch"] or bool(
            stats.get("metadata_mismatch", False)
        )
        totals["delta_too_large"] = totals["delta_too_large"] or bool(
            stats.get("delta_too_large", False)
        )

    if totals["metadata_mismatch"]:
        state = "NEEDS_REBUILD"
    elif totals["added_sections"] == 0 and totals["removed_sections"] == 0:
        state = "FRESH"
    elif totals["delta_too_large"]:
        state = "NEEDS_WARMUP"
    else:
        state = "HEALTHY"

    return {
        "command": "status",
        "corpus": str(corpus_root),
        "index_path": str(db_path),
        "index_exists": True,
        "last_touched": datetime.datetime.fromtimestamp(db_path.stat().st_mtime).isoformat(
            timespec="seconds"
        ),
        "model": selected_model,
        "path_scope": {"include": include_patterns or None, "exclude": exclude_patterns or None},
        "scopes": scopes_payload,
        "folder_breakdown": _build_folder_breakdown(scoped, corpus_root, db_path, cache_root),
        "excluded": _excluded_payload(corpus_root, include_patterns, exclude_patterns),
        "added_sections": totals["added_sections"],
        "removed_sections": totals["removed_sections"],
        "pending_chunks": totals["pending_chunks"],
        "pending_files": _combine_file_delta(
            scopes_payload,
            "pending_files",
            ("added_sections", "pending_chunks"),
        ),
        "removed_files": _combine_file_delta(
            scopes_payload,
            "removed_files",
            ("removed_sections",),
        ),
        "reused": totals["reused"],
        "drift_count": _file_id_drift_count(scoped, corpus_root, cache_root),
        "metadata_mismatch": totals["metadata_mismatch"],
        "delta_too_large": totals["delta_too_large"],
        "max_auto_embed": raw_cap,
        "state": state,
        **_state_payload(
            state,
            corpus_root,
            cache_root=cache_root,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        ),
    }


def _exit(payload: dict[str, Any], code: int) -> dict[str, Any]:
    payload["_exit_code"] = code
    return payload


def _scopes_for_missing_index(scoped_map_data: dict[str, Any]) -> list[dict[str, Any]]:
    scopes_payload: list[dict[str, Any]] = []
    for scope in ("sections", "descriptions"):
        items = build_items_from_map(scoped_map_data, scope=scope)
        if not items:
            continue
        pending = sum(len(_chunks_for_item(item)) for item in items)
        scopes_payload.append(
            {
                "scope": scope,
                "added_sections": len(items),
                "removed_sections": 0,
                "pending_files": pending_files_for_items(items),
                "removed_files": [],
                "reused": 0,
                "pending_chunks": pending,
                "total_sections_in_scope": 0,
            }
        )
    return scopes_payload


def _build_folder_breakdown(
    scoped_map_data: dict[str, Any],
    corpus_root: Path,
    db_path: Path,
    cache_root: Path | None,
) -> list[dict[str, Any]]:
    breakdown: dict[str, dict[str, Any]] = {}
    for file_entry in scoped_map_data["files"]:
        rel = file_entry["relative_path"]
        parts = rel.split("/")
        folder = parts[0] if len(parts) > 1 else "(root)"
        entry = breakdown.setdefault(
            folder,
            {"folder": folder, "files": 0, "indexed_sections": 0, "has_corpus": False},
        )
        entry["files"] += 1
        if (corpus_root / folder / ".md-navigator" / "index.sqlite").exists():
            entry["has_corpus"] = True

    if db_path.exists():
        try:
            conn = _open_index_readonly(corpus_root, cache_root=cache_root)
            try:
                rows = conn.execute(
                    "SELECT relative_path, COUNT(*) FROM sections "
                    "WHERE scope='sections' GROUP BY relative_path"
                ).fetchall()
            finally:
                conn.close()
            for path, count in rows:
                folder = path.split("/")[0] if "/" in path else "(root)"
                if folder in breakdown:
                    breakdown[folder]["indexed_sections"] += int(count)
        except (FileNotFoundError, sqlite3.OperationalError):
            pass

    for entry in breakdown.values():
        files = entry["files"]
        sections = entry["indexed_sections"]
        entry["avg_sections_per_file"] = round(sections / files, 1) if files and sections else 0.0

    return sorted(breakdown.values(), key=lambda entry: (-entry["files"], entry["folder"]))


def _detect_excluded(corpus_root: Path) -> list[str]:
    from .markdown_io import DEFAULT_EXCLUDED_PARTS

    present = []
    try:
        for child in corpus_root.iterdir():
            if child.is_dir() and child.name in DEFAULT_EXCLUDED_PARTS:
                present.append(child.name)
    except (PermissionError, OSError):
        pass
    return sorted(present)


def _excluded_payload(
    corpus_root: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> dict[str, Any]:
    return {
        "by_default_present": _detect_excluded(corpus_root),
        "by_path_exclude": exclude_patterns or [],
        "by_path_include": include_patterns or [],
    }


def _combine_file_delta(
    scopes_payload: list[dict[str, Any]],
    key: str,
    count_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for scope_payload in scopes_payload:
        for item in scope_payload.get(key) or []:
            path = str(item["relative_path"])
            entry = by_path.setdefault(path, {"relative_path": path})
            for field in count_fields:
                entry[field] = int(entry.get(field, 0)) + int(item.get(field, 0))
    return sorted(
        by_path.values(),
        key=lambda entry: (
            -sum(int(entry.get(field, 0)) for field in count_fields),
            entry["relative_path"],
        ),
    )


def _state_payload(
    state: str,
    corpus_root: Path,
    *,
    cache_root: Path | None = None,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> dict[str, Any]:
    from .index_meta import find_parent_indexed_corpus, path_include_for_parent_corpus

    if state == "FRESH":
        return {"recommended_action": None}
    action_args: dict[str, Any] = {"corpus": str(corpus_root), "dry_run": True}
    if path_include:
        action_args["path_include"] = path_include
    if path_exclude:
        action_args["path_exclude"] = path_exclude
    parent_corpus = find_parent_indexed_corpus(corpus_root, cache_root=cache_root)
    if parent_corpus is not None:
        action_args["corpus"] = str(parent_corpus)
        action_args["path_include"] = path_include_for_parent_corpus(
            corpus_root,
            parent_corpus,
            path_include,
        )
        if path_exclude:
            action_args["path_exclude"] = path_include_for_parent_corpus(
                corpus_root,
                parent_corpus,
                path_exclude,
            )
    if state == "HEALTHY":
        return {
            "recommended_action": {
                "tool": "md_index",
                "args": action_args,
                "reason": "Optional eager warmup; dry-run previews cost before embedding the small delta.",
            }
        }
    if state in ("NEEDS_WARMUP", "NEEDS_REBUILD", "NO_INDEX"):
        return {
            "recommended_action": {
                "tool": "md_index",
                "args": action_args,
                "reason": {
                    "NEEDS_WARMUP": "Pending delta exceeds auto-embed cap; dry-run index before search.",
                    "NEEDS_REBUILD": "Index metadata/schema mismatch; dry-run rebuild before confirming.",
                    "NO_INDEX": "Index does not exist; dry-run warmup before search.",
                }[state],
            }
        }
    return {"recommended_action": None}


def _file_id_drift_count(
    scoped_map_data: dict[str, Any],
    corpus_root: Path,
    cache_root: Path | None,
) -> int:
    fresh_file_id_by_path = {
        file_entry["relative_path"]: file_entry["id"]
        for file_entry in scoped_map_data["files"]
    }
    drift_count = 0
    try:
        conn = _open_index_readonly(corpus_root, cache_root=cache_root)
        try:
            rows = conn.execute("SELECT DISTINCT relative_path, file_id FROM sections").fetchall()
        finally:
            conn.close()
        for path, idx_fid in rows:
            fresh_fid = fresh_file_id_by_path.get(path)
            if fresh_fid is not None and int(fresh_fid) != int(idx_fid):
                drift_count += 1
    except (FileNotFoundError, sqlite3.OperationalError):
        pass
    return drift_count


def find_corpus_root_for(anchor: Path) -> Path | None:
    for parent in [anchor.parent, *anchor.parent.parents]:
        if (parent / ".md-navigator" / "index.sqlite").exists():
            return parent
    return None
