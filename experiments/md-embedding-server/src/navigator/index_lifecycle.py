"""Persistent index lifecycle cleanup and explicit compaction.

This module owns stale-row cleanup that is not part of ordinary content
diffing. `index_build.ensure_index` reconciles current scoped content;
this layer reconciles persistent DB rows against the canonical corpus scope
from `.md-tools.toml`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .filters import path_matches_any
from .index_meta import (
    _acquire_index_write_lock,
    _index_dir_for_corpus,
    _open_index,
    _open_index_metadata_readonly,
    _release_index_write_lock,
)
from .index_store import chunk_counts_by_section, delete_section_rowids, sqlite_stats

REASON_CONFIG_EXCLUDED = "config_excluded"
REASON_CONFIG_NOT_INCLUDED = "config_not_included"


@dataclass
class CleanupPlan:
    enabled: bool
    rowids: list[int] = field(default_factory=list)
    sections: int = 0
    chunks: int = 0
    files: list[dict[str, Any]] = field(default_factory=list)
    reasons: dict[str, int] = field(default_factory=dict)
    disabled_reason: str | None = None

    def public_payload(self) -> dict[str, Any]:
        return {
            "cleanup_enabled": self.enabled,
            "cleanup_sections": self.sections,
            "cleanup_chunks": self.chunks,
            "cleanup_files": self.files,
            "cleanup_reasons": self.reasons,
            "cleanup_disabled_reason": self.disabled_reason,
        }


def cleanup_enabled_for_operation(
    operation_include: list[str],
    operation_exclude: list[str],
) -> bool:
    return not operation_include and not operation_exclude


def empty_cleanup_plan(
    *,
    enabled: bool,
    disabled_reason: str | None = None,
) -> CleanupPlan:
    return CleanupPlan(enabled=enabled, disabled_reason=disabled_reason)


def plan_cleanup_from_connection(
    conn,
    corpus_root: Path,
    *,
    config_include: list[str],
    config_exclude: list[str],
    enabled: bool,
    disabled_reason: str | None = None,
) -> CleanupPlan:
    if not enabled:
        return empty_cleanup_plan(enabled=False, disabled_reason=disabled_reason)

    rows = conn.execute(
        "SELECT rowid, relative_path FROM sections ORDER BY rowid"
    ).fetchall()
    if not rows:
        return empty_cleanup_plan(enabled=True)

    rowids: list[int] = []
    relative_path_by_rowid: dict[int, str] = {}
    by_path: dict[str, dict[str, Any]] = {}
    reason_counts: dict[str, int] = {}

    for rowid, relative_path in rows:
        rel = str(relative_path)
        reason = _cleanup_reason(
            corpus_root,
            rel,
            config_include=config_include,
            config_exclude=config_exclude,
        )
        if reason is None:
            continue
        rid = int(rowid)
        rowids.append(rid)
        relative_path_by_rowid[rid] = rel
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        entry = by_path.setdefault(
            rel,
            {
                "relative_path": rel,
                "cleanup_sections": 0,
                "cleanup_chunks": 0,
                "cleanup_reasons": {},
            },
        )
        entry["cleanup_sections"] += 1
        path_reasons = entry["cleanup_reasons"]
        path_reasons[reason] = int(path_reasons.get(reason, 0)) + 1

    if not rowids:
        return empty_cleanup_plan(enabled=True)

    chunks_by_section = chunk_counts_by_section(conn, rowids)
    for rid in rowids:
        chunks = chunks_by_section.get(rid, 0)
        rel = relative_path_by_rowid[rid]
        by_path[rel]["cleanup_chunks"] += chunks

    files = sorted(
        by_path.values(),
        key=lambda item: (-int(item["cleanup_sections"]), item["relative_path"]),
    )
    return CleanupPlan(
        enabled=True,
        rowids=rowids,
        sections=len(rowids),
        chunks=sum(chunks_by_section.get(rid, 0) for rid in rowids),
        files=files,
        reasons=reason_counts,
    )


def plan_cleanup(
    corpus_root: Path,
    *,
    cache_root: Path | None,
    config_include: list[str],
    config_exclude: list[str],
    enabled: bool,
    disabled_reason: str | None = None,
) -> CleanupPlan:
    db_path = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite"
    if not db_path.exists():
        return empty_cleanup_plan(enabled=enabled, disabled_reason=disabled_reason)
    conn = _open_index_metadata_readonly(corpus_root, cache_root=cache_root)
    try:
        return plan_cleanup_from_connection(
            conn,
            corpus_root,
            config_include=config_include,
            config_exclude=config_exclude,
            enabled=enabled,
            disabled_reason=disabled_reason,
        )
    finally:
        conn.close()


def apply_cleanup(
    corpus_root: Path,
    *,
    cache_root: Path | None,
    embed_model: str,
    embedding_api_url: str,
    config_include: list[str],
    config_exclude: list[str],
    enabled: bool,
    disabled_reason: str | None = None,
) -> CleanupPlan:
    db_path = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite"
    if not db_path.exists():
        return empty_cleanup_plan(enabled=enabled, disabled_reason=disabled_reason)

    lock_handle = _acquire_index_write_lock(corpus_root, cache_root=cache_root)
    try:
        conn = _open_index(
            cache_root,
            corpus_root,
            embed_model,
            embedding_api_url,
            vec_dim=None,
        )
        try:
            plan = plan_cleanup_from_connection(
                conn,
                corpus_root,
                config_include=config_include,
                config_exclude=config_exclude,
                enabled=enabled,
                disabled_reason=disabled_reason,
            )
            if plan.rowids:
                delete_section_rowids(conn, plan.rowids)
                conn.commit()
            return plan
        finally:
            conn.close()
    finally:
        _release_index_write_lock(lock_handle)


def vacuum_preview(corpus_root: Path, *, cache_root: Path | None) -> dict[str, Any]:
    db_path = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite"
    if not db_path.exists():
        return {"requested": True, "would_run": False, "reason": "no_index"}
    stats = sqlite_stats(db_path)
    return {"requested": True, "would_run": True, "before": stats}


def vacuum_index(corpus_root: Path, *, cache_root: Path | None) -> dict[str, Any]:
    db_path = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite"
    if not db_path.exists():
        return {"requested": True, "ran": False, "reason": "no_index"}

    before = sqlite_stats(db_path)
    lock_handle = _acquire_index_write_lock(corpus_root, cache_root=cache_root)
    try:
        import sqlite3
        import sqlite_vec  # type: ignore[import-not-found]

        conn = sqlite3.connect(db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA busy_timeout = 30000")
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            conn.execute("VACUUM")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            conn.close()
    finally:
        _release_index_write_lock(lock_handle)
    after = sqlite_stats(db_path)
    return {
        "requested": True,
        "ran": True,
        "before": before,
        "after": after,
        "reclaimed_bytes": max(0, int(before["bytes"]) - int(after["bytes"])),
    }


def _cleanup_reason(
    corpus_root: Path,
    relative_path: str,
    *,
    config_include: list[str],
    config_exclude: list[str],
) -> str | None:
    if config_exclude and path_matches_any(relative_path, config_exclude):
        return REASON_CONFIG_EXCLUDED
    if config_include and not path_matches_any(relative_path, config_include):
        return REASON_CONFIG_NOT_INCLUDED
    if not (corpus_root / relative_path).is_file():
        return None
    return None
