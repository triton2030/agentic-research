from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import embeddings


@dataclass(frozen=True)
class QueryVectorBatch:
    vectors: dict[str, Any]
    cached: int
    computed: int
    cache_error: str | None = None


def _query_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _unique_texts(texts: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for text in texts:
        cleaned = str(text)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        out.append(cleaned)
    return out


def _ensure_query_vector_cache(conn) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS query_vectors ("
        "  model TEXT NOT NULL,"
        "  embedding_api_url TEXT NOT NULL,"
        "  query_sha256 TEXT NOT NULL,"
        "  query_text TEXT NOT NULL,"
        "  dim INTEGER NOT NULL,"
        "  vector BLOB NOT NULL,"
        "  created_at INTEGER NOT NULL,"
        "  PRIMARY KEY(model, embedding_api_url, query_sha256)"
        ")"
    )


def get_query_vectors(
    conn,
    model_name: str,
    texts: list[str],
    api_url: str,
    timeout: float,
    *,
    corpus_root: Path | None = None,
) -> QueryVectorBatch:
    unique = _unique_texts(texts)
    if not unique:
        return QueryVectorBatch({}, cached=0, computed=0)

    vectors: dict[str, Any] = {}
    misses: list[str] = []
    cache_error: str | None = None
    try:
        _ensure_query_vector_cache(conn)
        keys = [_query_hash(text) for text in unique]
        placeholders = ",".join("?" * len(keys))
        rows = conn.execute(
            "SELECT query_sha256, dim, vector FROM query_vectors "
            "WHERE model = ? AND embedding_api_url = ? "
            f"AND query_sha256 IN ({placeholders})",
            (model_name, api_url, *keys),
        ).fetchall()
        found = {
            str(query_hash): embeddings._blob_to_vec(blob, int(dim))
            for query_hash, dim, blob in rows
        }
        for text, key in zip(unique, keys):
            vec = found.get(key)
            if vec is None:
                misses.append(text)
            else:
                vectors[text] = vec
    except Exception as exc:  # cache is an optimisation; embedding must still work.
        cache_error = f"{type(exc).__name__}: {exc}"
        misses = unique
        vectors = {}

    computed = (
        embeddings._embed_texts_http(
            model_name,
            misses,
            api_url,
            timeout,
            corpus_root=corpus_root,
        )
        if misses
        else []
    )
    for text, vector in zip(misses, computed):
        vectors[text] = vector

    if computed and cache_error is None:
        now = int(time.time())
        try:
            conn.executemany(
                "INSERT INTO query_vectors "
                "(model, embedding_api_url, query_sha256, query_text, dim, vector, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(model, embedding_api_url, query_sha256) DO UPDATE SET "
                "query_text = excluded.query_text, "
                "dim = excluded.dim, "
                "vector = excluded.vector, "
                "created_at = excluded.created_at",
                [
                    (
                        model_name,
                        api_url,
                        _query_hash(text),
                        text,
                        len(vector),
                        embeddings._vec_to_blob(vector),
                        now,
                    )
                    for text, vector in zip(misses, computed)
                ],
            )
            conn.commit()
        except Exception as exc:
            cache_error = f"{type(exc).__name__}: {exc}"

    return QueryVectorBatch(
        vectors=vectors,
        cached=len(unique) - len(misses),
        computed=len(computed),
        cache_error=cache_error,
    )
