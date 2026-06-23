"""Read-only classification of persistent index readiness.

This module owns the SQLite/index fact check. It deliberately does not shape
agent-facing guidance, envelope fields, or CLI exit codes.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from .index_meta import (
    SCHEMA_VERSION,
    _index_dir_for_corpus,
    _meta_get,
    _open_index_metadata_readonly,
    _open_index_readonly,
)
from .index_store import index_integrity_summary


class IndexReadinessKind(str, Enum):
    MISSING = "missing"
    METADATA_UNREADABLE = "metadata_unreadable"
    SCHEMA_INVALID = "schema_invalid"
    METADATA_MISMATCH = "metadata_mismatch"
    SHADOWED_CONFLICT = "shadowed_conflict"
    INTEGRITY_MISMATCH = "integrity_mismatch"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    READY = "ready"


@dataclass(frozen=True)
class IndexReadiness:
    kind: IndexReadinessKind
    db_path: Path
    metadata: dict[str, str | None] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    index_exists: bool = False
    can_read_metadata: bool = False
    can_read_vectors: bool = False
    integrity: dict[str, Any] | None = None


META_KEYS = ("schema_version", "embed_model", "embedding_api_url", "vec_dim")
REQUIRED_TABLES = ("meta", "sections", "sections_fts", "chunks", "sections_vec")
ReadinessMode = Literal["metadata", "vector"]


def classify_index_readiness(
    corpus_root: Path,
    *,
    cache_root: Path | None = None,
    mode: ReadinessMode = "metadata",
    check_integrity: bool = False,
    check_shadowed: bool = False,
    expected_embed_model: str | None = None,
    expected_embedding_api_url: str | None = None,
    expected_vec_dim: int | str | None = None,
) -> IndexReadiness:
    db_path = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite"
    if not db_path.exists():
        return IndexReadiness(
            kind=IndexReadinessKind.MISSING,
            db_path=db_path,
            index_exists=False,
        )

    try:
        conn = _open_index_metadata_readonly(corpus_root, cache_root=cache_root)
    except sqlite3.Error as exc:
        return IndexReadiness(
            kind=IndexReadinessKind.METADATA_UNREADABLE,
            db_path=db_path,
            issues=[f"metadata_unreadable:{type(exc).__name__}:{exc}"],
            index_exists=True,
        )

    try:
        try:
            metadata = {key: _meta_get(conn, key) for key in META_KEYS}
        except sqlite3.Error as exc:
            return IndexReadiness(
                kind=IndexReadinessKind.METADATA_UNREADABLE,
                db_path=db_path,
                issues=[f"metadata_unreadable:{type(exc).__name__}:{exc}"],
                index_exists=True,
            )

        schema_issues = _schema_issues(conn)
        if schema_issues:
            return IndexReadiness(
                kind=IndexReadinessKind.SCHEMA_INVALID,
                db_path=db_path,
                metadata=metadata,
                issues=schema_issues,
                index_exists=True,
                can_read_metadata=True,
            )
    finally:
        conn.close()

    mismatch_issues = _metadata_mismatch_issues(
        metadata,
        expected_embed_model=expected_embed_model,
        expected_embedding_api_url=expected_embedding_api_url,
        expected_vec_dim=expected_vec_dim,
    )
    if mismatch_issues:
        return IndexReadiness(
            kind=IndexReadinessKind.METADATA_MISMATCH,
            db_path=db_path,
            metadata=metadata,
            issues=mismatch_issues,
            index_exists=True,
            can_read_metadata=True,
        )

    if check_shadowed:
        conflicts = _shadowed_conflicts(corpus_root, cache_root=cache_root)
        if conflicts:
            return IndexReadiness(
                kind=IndexReadinessKind.SHADOWED_CONFLICT,
                db_path=db_path,
                metadata=metadata,
                conflicts=conflicts,
                issues=["shadowed_conflict"],
                index_exists=True,
                can_read_metadata=True,
            )

    integrity_payload: dict[str, Any] | None = None
    if mode == "vector" or check_integrity:
        try:
            vec_conn = _open_index_readonly(corpus_root, cache_root=cache_root)
        except ModuleNotFoundError as exc:
            return IndexReadiness(
                kind=IndexReadinessKind.DEPENDENCY_UNAVAILABLE,
                db_path=db_path,
                metadata=metadata,
                issues=[f"dependency_unavailable:{type(exc).__name__}:{exc}"],
                index_exists=True,
                can_read_metadata=True,
            )
        except RuntimeError as exc:
            return IndexReadiness(
                kind=IndexReadinessKind.DEPENDENCY_UNAVAILABLE,
                db_path=db_path,
                metadata=metadata,
                issues=[f"dependency_unavailable:{type(exc).__name__}:{exc}"],
                index_exists=True,
                can_read_metadata=True,
            )
        except sqlite3.Error as exc:
            return IndexReadiness(
                kind=IndexReadinessKind.SCHEMA_INVALID,
                db_path=db_path,
                metadata=metadata,
                issues=[f"vector_open_failed:{type(exc).__name__}:{exc}"],
                index_exists=True,
                can_read_metadata=True,
            )
        try:
            if check_integrity:
                try:
                    integrity_payload = index_integrity_summary(vec_conn)
                except sqlite3.Error as exc:
                    return IndexReadiness(
                        kind=IndexReadinessKind.INTEGRITY_MISMATCH,
                        db_path=db_path,
                        metadata=metadata,
                        issues=[f"integrity_query_failed:{type(exc).__name__}:{exc}"],
                        index_exists=True,
                        can_read_metadata=True,
                        can_read_vectors=True,
                        integrity=_integrity_error_payload(exc),
                    )
                if integrity_payload is not None and not integrity_payload["ok"]:
                    return IndexReadiness(
                        kind=IndexReadinessKind.INTEGRITY_MISMATCH,
                        db_path=db_path,
                        metadata=metadata,
                        issues=list(integrity_payload.get("issues") or []),
                        index_exists=True,
                        can_read_metadata=True,
                        can_read_vectors=True,
                        integrity=integrity_payload,
                    )
        finally:
            vec_conn.close()

    return IndexReadiness(
        kind=IndexReadinessKind.READY,
        db_path=db_path,
        metadata=metadata,
        index_exists=True,
        can_read_metadata=True,
        can_read_vectors=mode == "vector" or check_integrity,
        integrity=integrity_payload,
    )


def _schema_issues(conn) -> list[str]:
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        ).fetchall()
    except sqlite3.Error as exc:
        return [f"schema_unreadable:{type(exc).__name__}:{exc}"]
    existing = {str(row[0]) for row in rows}
    missing = [name for name in REQUIRED_TABLES if name not in existing]
    return [f"missing_table:{name}" for name in missing]


def _metadata_mismatch_issues(
    metadata: dict[str, str | None],
    *,
    expected_embed_model: str | None,
    expected_embedding_api_url: str | None,
    expected_vec_dim: int | str | None,
) -> list[str]:
    issues: list[str] = []
    if metadata.get("schema_version") != str(SCHEMA_VERSION):
        issues.append("schema_version_mismatch")
    if expected_embed_model is not None and metadata.get("embed_model") != expected_embed_model:
        issues.append("embed_model_mismatch")
    if (
        expected_embedding_api_url is not None
        and metadata.get("embedding_api_url") != expected_embedding_api_url
    ):
        issues.append("embedding_api_url_mismatch")
    if expected_vec_dim is not None and metadata.get("vec_dim") != str(expected_vec_dim):
        issues.append("vec_dim_mismatch")
    return issues


def _shadowed_conflicts(
    corpus_root: Path,
    *,
    cache_root: Path | None,
) -> list[dict[str, Any]]:
    if cache_root is not None:
        return []
    from .index_resolution import shadowed_indexes

    return [
        entry
        for entry in shadowed_indexes(corpus_root, cache_root=cache_root)
        if entry.get("conflicting")
    ]


def _integrity_error_payload(exc: sqlite3.Error) -> dict[str, Any]:
    return {
        "ok": False,
        "counts": {"sections": 0, "chunks": 0, "sections_fts": 0, "sections_vec": 0},
        "issues": [f"integrity_query_failed:{type(exc).__name__}"],
    }
