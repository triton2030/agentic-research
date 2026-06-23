from __future__ import annotations

import sqlite3
from pathlib import Path

from navigator.api import index
from navigator.index_readiness import IndexReadinessKind, classify_index_readiness


def _write_doc(corpus: Path) -> None:
    corpus.mkdir(parents=True, exist_ok=True)
    (corpus / "doc.md").write_text("# Doc\n\n## Topic\n\nBody.\n", encoding="utf-8")


def _minimal_index(corpus: Path, *, schema_version: str = "4") -> Path:
    index_dir = corpus / ".md-navigator"
    index_dir.mkdir(parents=True)
    db_path = index_dir / "index.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        for key, value in {
            "schema_version": schema_version,
            "embed_model": "test/root",
            "embedding_api_url": "http://test.local/v1",
            "vec_dim": "16",
        }.items():
            conn.execute("INSERT INTO meta (key, value) VALUES (?, ?)", (key, value))
        for table in ("sections", "sections_fts", "chunks", "sections_vec"):
            conn.execute(f"CREATE TABLE {table} (rowid INTEGER PRIMARY KEY)")
        conn.commit()
    finally:
        conn.close()
    return db_path


def test_index_readiness_missing_index(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    _write_doc(corpus)

    readiness = classify_index_readiness(corpus)

    assert readiness.kind is IndexReadinessKind.MISSING
    assert readiness.index_exists is False


def test_index_readiness_zero_byte_metadata_unreadable(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    _write_doc(corpus)
    (corpus / ".md-navigator").mkdir()
    (corpus / ".md-navigator" / "index.sqlite").write_bytes(b"")

    readiness = classify_index_readiness(corpus)

    assert readiness.kind is IndexReadinessKind.METADATA_UNREADABLE
    assert readiness.index_exists is True
    assert readiness.can_read_metadata is False


def test_index_readiness_missing_tables_schema_invalid(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    _write_doc(corpus)
    index_dir = corpus / ".md-navigator"
    index_dir.mkdir()
    conn = sqlite3.connect(index_dir / "index.sqlite")
    try:
        conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("INSERT INTO meta (key, value) VALUES ('schema_version', '4')")
        conn.commit()
    finally:
        conn.close()

    readiness = classify_index_readiness(corpus)

    assert readiness.kind is IndexReadinessKind.SCHEMA_INVALID
    assert "missing_table:sections" in readiness.issues


def test_index_readiness_metadata_mismatch(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    _write_doc(corpus)
    _minimal_index(corpus, schema_version="3")

    readiness = classify_index_readiness(corpus)

    assert readiness.kind is IndexReadinessKind.METADATA_MISMATCH
    assert "schema_version_mismatch" in readiness.issues


def test_index_readiness_integrity_mismatch(tmp_path: Path, mock_embed) -> None:
    corpus = tmp_path / "corpus"
    _write_doc(corpus)
    built = index(
        str(corpus),
        confirm=True,
        embed_model="test/root",
        embedding_api_url="http://test.local/v1",
        batch_pause_ms=0,
    )
    assert built.get("_exit_code", 0) == 0

    import sqlite_vec  # type: ignore[import-not-found]

    conn = sqlite3.connect(corpus / ".md-navigator" / "index.sqlite")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    try:
        rowid = conn.execute("SELECT MIN(chunk_id) FROM chunks").fetchone()[0]
        conn.execute("DELETE FROM sections_vec WHERE rowid = ?", (rowid,))
        conn.commit()
    finally:
        conn.close()

    readiness = classify_index_readiness(
        corpus,
        expected_embed_model="test/root",
        expected_embedding_api_url="http://test.local/v1",
        check_integrity=True,
    )

    assert readiness.kind is IndexReadinessKind.INTEGRITY_MISMATCH
    assert "sections_vec_count_mismatch" in readiness.issues


def test_index_readiness_shadowed_conflict(tmp_path: Path, mock_embed) -> None:
    corpus = tmp_path / "corpus"
    child = corpus / "child"
    _write_doc(corpus)
    _write_doc(child)
    assert index(str(corpus), confirm=True, embed_model="test/root").get("_exit_code", 0) == 0
    assert index(
        str(child),
        confirm=True,
        allow_nested_corpus=True,
        embed_model="test/nested",
    ).get("_exit_code", 0) == 0

    readiness = classify_index_readiness(corpus, check_shadowed=True)

    assert readiness.kind is IndexReadinessKind.SHADOWED_CONFLICT
    assert readiness.conflicts
    assert "embed_model_mismatch" in readiness.conflicts[0]["conflict_reasons"]
