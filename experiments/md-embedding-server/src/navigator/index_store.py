"""Connection-level storage primitives for the persistent index.

This module owns table-coherence operations that are shared by indexing,
lifecycle cleanup, and status health checks. Higher layers decide *why* rows
should change; this layer keeps SQLite tables moving together.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


INDEX_COUNT_TABLES = ("sections", "chunks", "sections_fts", "sections_vec")


def delete_section_rowids(conn, rowids: list[int]) -> int:
    """Drop sections plus their FTS, chunks, and vector rows.

    Returns the number of vector rows removed.
    """
    if not rowids:
        return 0
    batch = 400
    removed_vecs = 0
    for start in range(0, len(rowids), batch):
        sub = rowids[start : start + batch]
        placeholders = ",".join("?" * len(sub))
        chunk_ids = [
            r[0]
            for r in conn.execute(
                f"SELECT chunk_id FROM chunks WHERE section_rowid IN ({placeholders})",
                sub,
            ).fetchall()
        ]
        if chunk_ids:
            cb = 400
            for s2 in range(0, len(chunk_ids), cb):
                sub2 = chunk_ids[s2 : s2 + cb]
                ph2 = ",".join("?" * len(sub2))
                conn.execute(f"DELETE FROM sections_vec WHERE rowid IN ({ph2})", sub2)
                conn.execute(f"DELETE FROM chunks WHERE chunk_id IN ({ph2})", sub2)
                removed_vecs += len(sub2)
        conn.execute(f"DELETE FROM sections_fts WHERE rowid IN ({placeholders})", sub)
        conn.execute(f"DELETE FROM sections WHERE rowid IN ({placeholders})", sub)
    return removed_vecs


def chunk_counts_by_section(conn, rowids: list[int]) -> dict[int, int]:
    out: dict[int, int] = {}
    batch = 400
    for start in range(0, len(rowids), batch):
        sub = rowids[start : start + batch]
        placeholders = ",".join("?" * len(sub))
        rows = conn.execute(
            "SELECT section_rowid, COUNT(*) FROM chunks "
            f"WHERE section_rowid IN ({placeholders}) GROUP BY section_rowid",
            sub,
        ).fetchall()
        out.update({int(section_rowid): int(count) for section_rowid, count in rows})
    return out


def sqlite_stats(db_path: Path) -> dict[str, int]:
    import sqlite3

    conn = sqlite3.connect(db_path, timeout=30.0)
    try:
        page_size = int(conn.execute("PRAGMA page_size").fetchone()[0])
        page_count = int(conn.execute("PRAGMA page_count").fetchone()[0])
        freelist_count = int(conn.execute("PRAGMA freelist_count").fetchone()[0])
    finally:
        conn.close()
    return {
        "bytes": int(db_path.stat().st_size),
        "page_size": page_size,
        "page_count": page_count,
        "freelist_count": freelist_count,
        "freelist_bytes": freelist_count * page_size,
    }


def index_integrity_summary(conn) -> dict[str, Any]:
    counts = {table: _count_table(conn, table) for table in INDEX_COUNT_TABLES}
    issues: list[str] = []

    if counts["sections"] != counts["sections_fts"]:
        issues.append("sections_fts_count_mismatch")
    if counts["chunks"] != counts["sections_vec"]:
        issues.append("sections_vec_count_mismatch")

    relation_checks = {
        "chunks_without_section": (
            "SELECT COUNT(*) FROM chunks c "
            "LEFT JOIN sections s ON s.rowid = c.section_rowid "
            "WHERE s.rowid IS NULL"
        ),
        "sections_without_fts": (
            "SELECT COUNT(*) FROM sections s "
            "LEFT JOIN sections_fts f ON f.rowid = s.rowid "
            "WHERE f.rowid IS NULL"
        ),
        "fts_without_section": (
            "SELECT COUNT(*) FROM sections_fts f "
            "LEFT JOIN sections s ON s.rowid = f.rowid "
            "WHERE s.rowid IS NULL"
        ),
        "chunks_without_vector": (
            "SELECT COUNT(*) FROM chunks c "
            "LEFT JOIN sections_vec v ON v.rowid = c.chunk_id "
            "WHERE v.rowid IS NULL"
        ),
        "vectors_without_chunk": (
            "SELECT COUNT(*) FROM sections_vec v "
            "LEFT JOIN chunks c ON c.chunk_id = v.rowid "
            "WHERE c.chunk_id IS NULL"
        ),
    }
    for name, sql in relation_checks.items():
        count = _count_query(conn, sql)
        if count:
            issues.append(f"{name}:{count}")

    return {"ok": not issues, "counts": counts, "issues": issues}


def _count_table(conn, table: str) -> int:
    return _count_query(conn, f"SELECT COUNT(*) FROM {table}")


def _count_query(conn, sql: str) -> int:
    row = conn.execute(sql).fetchone()
    return int(row[0] or 0)
