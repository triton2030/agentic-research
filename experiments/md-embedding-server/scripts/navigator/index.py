from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

from .embeddings import (
    SEARCH_DEFAULT_EMBEDDING_API_URL,
    SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
    _embed_texts_http,
    _vec_to_blob,
)
from .sections import (
    SUBCHUNK_MAX_TOKENS,
    _chunk_hash_for,
    _contextual_passage,
    _should_subchunk,
    _split_body_into_chunks,
)


SCHEMA_VERSION = 3
# Legacy cache root, kept for the --cache-dir override path. The default index
# location is now inside the corpus itself (see `_index_dir_for_corpus`) so a
# user's system-wide cache cleaner cannot wipe a multi-hour cold-index run.
SEARCH_CACHE_ROOT = Path.home() / ".cache" / "md-navigator"
INDEX_DIRNAME = ".md-navigator"
GITIGNORE_BANNER = "# md-navigator persistent index — do not commit\n*\n"


# --- Cache layout --------------------------------------------------------


def _index_dir_for_corpus(
    corpus_root: Path,
    cache_root: Path | None = None,
    create: bool = True,
) -> Path:
    """Default: `<corpus_root>/.md-navigator/`. Override: a per-corpus
    subdirectory inside `cache_root` (sha256-of-corpus-path subdir, same
    layout the legacy `~/.cache/md-navigator/` used). The in-corpus layout
    survives `~/.cache` cleanup; the override is kept for tests and for
    users who want a single shared root."""
    if cache_root is not None:
        digest = hashlib.sha256(str(corpus_root).encode("utf-8")).hexdigest()[:16]
        d = Path(cache_root) / digest
    else:
        anchor = corpus_root if corpus_root.is_dir() else corpus_root.parent
        d = anchor / INDEX_DIRNAME
    if create:
        d.mkdir(parents=True, exist_ok=True)
        # Auto-write .gitignore on first create so the index never ends up in a
        # commit when the corpus is a git working tree.
        gi = d / ".gitignore"
        if not gi.exists():
            gi.write_text(GITIGNORE_BANNER, encoding="utf-8")
    return d


# Backwards-compat alias: callers used to call `_cache_dir_for_root(cache_root, corpus_root)`.
def _cache_dir_for_root(cache_root: Path, corpus_root: Path) -> Path:
    return _index_dir_for_corpus(corpus_root, cache_root=cache_root)


def _acquire_index_write_lock(corpus_root: Path, cache_root: Path | None = None):
    """Serialise writers for one corpus index across parallel agent sessions."""
    import fcntl

    lock_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=True)
    handle = (lock_dir / "index.lock").open("a+", encoding="utf-8")
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    return handle


def _release_index_write_lock(handle) -> None:
    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


# --- Meta helpers --------------------------------------------------------


def _meta_get(conn, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row[0] if row else None


def _meta_set(conn, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


# --- Schema --------------------------------------------------------------


def _create_schema(conn, dim: int) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS meta ("
        "  key TEXT PRIMARY KEY,"
        "  value TEXT NOT NULL"
        ")"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sections ("
        "  rowid INTEGER PRIMARY KEY,"
        "  section_id TEXT NOT NULL,"
        "  scope TEXT NOT NULL,"
        "  file_id INTEGER NOT NULL,"
        "  relative_path TEXT NOT NULL,"
        "  start_line INTEGER NOT NULL,"
        "  level INTEGER NOT NULL,"
        "  heading_text TEXT NOT NULL,"
        "  heading_chain TEXT NOT NULL,"
        "  body TEXT NOT NULL,"
        "  file_description TEXT NOT NULL,"
        "  file_title TEXT NOT NULL,"
        "  content_hash TEXT NOT NULL,"
        "  token_count INTEGER NOT NULL,"
        "  UNIQUE(scope, content_hash)"
        ")"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS sections_scope_path ON sections(scope, relative_path)"
    )
    conn.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5("
        "  description, title, heading_chain, body,"
        "  tokenize='unicode61 remove_diacritics 2'"
        ")"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chunks ("
        "  chunk_id INTEGER PRIMARY KEY,"
        "  section_rowid INTEGER NOT NULL,"
        "  chunk_idx INTEGER NOT NULL,"
        "  chunk_hash TEXT NOT NULL UNIQUE,"
        "  chunk_body TEXT NOT NULL"
        ")"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS chunks_section_rowid ON chunks(section_rowid)"
    )
    conn.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS sections_vec USING vec0(embedding float[{dim}])"
    )


# --- Open / probe --------------------------------------------------------


def probe_embedding_dim(
    embed_model: str,
    embedding_api_url: str = SEARCH_DEFAULT_EMBEDDING_API_URL,
    embedding_timeout: float = SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
    corpus_root: Path | None = None,
) -> int:
    """One round-trip to the embedding server to discover the vector
    dimension. Used on the cold-start path before we know the schema."""
    vecs = _embed_texts_http(
        embed_model,
        ["dim probe"],
        embedding_api_url,
        embedding_timeout,
        corpus_root=corpus_root,
    )
    if not vecs:
        raise RuntimeError("Embedding server returned no vectors on dim probe")
    return int(len(vecs[0]))


def _open_index(
    cache_root: Path | None,
    corpus_root: Path,
    embed_model: str,
    embedding_api_url: str,
    vec_dim: int | None,
):
    """Open (or create) the persistent on-disk index for `corpus_root`. If
    the recorded `embed_model`, `embedding_api_url`, or `vec_dim` no longer
    match the current server, drop the on-disk store and start fresh —
    vectors from a different model live in a different geometry.

    `cache_root=None` (default in normal use) means the index lives inside
    the corpus at `<corpus>/.md-navigator/`. A non-None `cache_root` lays
    out per-corpus subfolders inside that root (legacy and test path)."""
    import sqlite3
    import sqlite_vec

    cache_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=True)
    db_path = cache_dir / "index.sqlite"
    needs_fresh = False
    if db_path.exists():
        probe = sqlite3.connect(db_path)
        probe.enable_load_extension(True)
        sqlite_vec.load(probe)
        probe.enable_load_extension(False)
        try:
            recorded_version = _meta_get(probe, "schema_version")
            recorded_model = _meta_get(probe, "embed_model")
            recorded_dim = _meta_get(probe, "vec_dim")
            recorded_api = _meta_get(probe, "embedding_api_url")
        except sqlite3.OperationalError:
            recorded_version = None
            recorded_model = None
            recorded_dim = None
            recorded_api = None
        probe.close()
        if (
            recorded_version != str(SCHEMA_VERSION)
            or recorded_model != embed_model
            or recorded_api != embedding_api_url
            or (vec_dim is not None and recorded_dim != str(vec_dim))
        ):
            needs_fresh = True
    if needs_fresh:
        # Drop the whole index file and any WAL/SHM siblings.
        for suffix in ("", "-wal", "-shm"):
            p = db_path.with_name(db_path.name + suffix)
            p.unlink(missing_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    if vec_dim is None:
        existing_dim = _meta_get(conn, "vec_dim")
        if existing_dim is None:
            conn.close()
            raise RuntimeError(
                "Persistent index has no recorded vec_dim and caller did not supply one. "
                "First call must pass a probed dim from the embedding server."
            )
        dim_for_schema = int(existing_dim)
    else:
        dim_for_schema = vec_dim

    _create_schema(conn, dim_for_schema)
    _meta_set(conn, "schema_version", str(SCHEMA_VERSION))
    _meta_set(conn, "embed_model", embed_model)
    _meta_set(conn, "vec_dim", str(dim_for_schema))
    _meta_set(conn, "embedding_api_url", embedding_api_url)
    conn.commit()
    return conn


def _open_index_metadata_readonly(corpus_root: Path, cache_root: Path | None = None):
    """Open existing index metadata read-only. Does not create directories."""
    import sqlite3

    cache_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = cache_dir / "index.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def _index_delta_stats_readonly(
    conn,
    scope: str,
    items: list[dict[str, Any]],
    embed_model: str,
    embedding_api_url: str,
    max_auto_embed: int | None,
) -> dict[str, Any]:
    """Compute freshness stats without schema creation, meta writes, or pruning."""
    stats: dict[str, Any] = {
        "embedded": 0,
        "reused": 0,
        "removed": 0,
        "added_sections": 0,
        "removed_sections": 0,
        "total_sections_in_scope": 0,
        "subchunked_sections": 0,
        "delta_too_large": False,
        "pending_chunks": 0,
        "metadata_mismatch": False,
    }
    try:
        recorded_version = _meta_get(conn, "schema_version")
        recorded_model = _meta_get(conn, "embed_model")
        recorded_api = _meta_get(conn, "embedding_api_url")
    except Exception:
        stats["metadata_mismatch"] = True
        return stats

    if (
        recorded_version != str(SCHEMA_VERSION)
        or recorded_model != embed_model
        or recorded_api != embedding_api_url
    ):
        stats["metadata_mismatch"] = True
        return stats

    try:
        existing_rows = conn.execute(
            "SELECT rowid, content_hash FROM sections WHERE scope = ?",
            (scope,),
        ).fetchall()
    except Exception:
        stats["metadata_mismatch"] = True
        return stats

    existing_hash_to_rowid: dict[str, int] = {h: rid for rid, h in existing_rows}
    current_hash_to_item: dict[str, dict[str, Any]] = {it["content_hash"]: it for it in items}
    added_hashes = [h for h in current_hash_to_item if h not in existing_hash_to_rowid]
    removed_hashes = [h for h in existing_hash_to_rowid if h not in current_hash_to_item]
    pending_chunks = sum(len(_chunks_for_item(current_hash_to_item[h])) for h in added_hashes)

    stats["reused"] = len(existing_hash_to_rowid) - len(removed_hashes)
    stats["added_sections"] = len(added_hashes)
    stats["removed_sections"] = len(removed_hashes)
    stats["pending_chunks"] = pending_chunks
    stats["delta_too_large"] = max_auto_embed is not None and pending_chunks > max_auto_embed
    stats["total_sections_in_scope"] = len(existing_hash_to_rowid)
    stats["subchunked_sections"] = sum(
        1
        for h in added_hashes
        if scope == "sections"
        and len(_chunks_for_item(current_hash_to_item[h])) > 1
    )
    return stats


# --- Monotonic counters ---------------------------------------------------


def _next_id(conn, counter_key: str, fallback_max_sql: str) -> int:
    """Return the next monotonic id for a counter stored in meta. Initialises
    from `MAX(rowid)+1` of the live table on first use so existing data
    survives a counter reset."""
    raw = _meta_get(conn, counter_key)
    if raw is None:
        row = conn.execute(fallback_max_sql).fetchone()
        current = int(row[0] or 0)
        nxt = current + 1
    else:
        nxt = int(raw)
    return nxt


def _set_counter(conn, counter_key: str, value: int) -> None:
    _meta_set(conn, counter_key, str(value))


# --- Delta apply ---------------------------------------------------------


def _chunks_for_item(item: dict[str, Any]) -> list[tuple[int, str, str, str]]:
    """Return (chunk_idx, chunk_body, chunk_hash, passage) per sub-chunk of
    this item. Description-scope items and short sections produce one chunk;
    long sections are split."""
    body = item["body"] or ""
    scope = item.get("scope", "sections")
    if scope == "descriptions" or not _should_subchunk(body):
        chunk_hash = _chunk_hash_for(item["content_hash"], 0)
        passage = _contextual_passage(item)
        return [(0, body, chunk_hash, passage)]
    pieces = _split_body_into_chunks(body, SUBCHUNK_MAX_TOKENS)
    out: list[tuple[int, str, str, str]] = []
    for ci, piece in enumerate(pieces):
        chunk_hash = _chunk_hash_for(item["content_hash"], ci)
        passage = _contextual_passage(item, body_override=piece)
        out.append((ci, piece, chunk_hash, passage))
    return out


def _delete_section_rowids(conn, rowids: list[int]) -> int:
    """Drop sections + their FTS + chunks + vec rows. Returns number of vec
    rows removed."""
    if not rowids:
        return 0
    # Walk in batches to stay clear of SQLite variable limits.
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


# Cloud embeddings: no Metal cap, no on-laptop heat. Bigger batches amortise
# HTTP latency, and no inter-batch pause is needed.
DEFAULT_INDEX_BATCH = 32
DEFAULT_INDEX_PAUSE_S = 0.0
# Auto-embed cap for `search` / `overlaps`. A single fresh file with a
# handful of sections plus heading renames must not derail the search flow,
# but a true new-corpus delta (hundreds of chunks) should still require an
# explicit `index` run. 50 fits a typical mid-edit session.
DEFAULT_MAX_AUTO_EMBED = 50


def _clean_incomplete_sections(conn, scope: str) -> int:
    """Drop sections in this scope that have no chunks/vectors yet. This
    happens when a previous indexing run was interrupted between INSERT-ing
    sections rows and writing the matching chunks + sections_vec rows.
    Returns the number of sections removed."""
    rows = conn.execute(
        "SELECT s.rowid FROM sections s "
        "LEFT JOIN chunks c ON c.section_rowid = s.rowid "
        "WHERE c.section_rowid IS NULL AND s.scope = ?",
        (scope,),
    ).fetchall()
    if not rows:
        return 0
    _delete_section_rowids(conn, [r[0] for r in rows])
    return len(rows)


def ensure_index(
    corpus_root: Path,
    scope: str,
    items: list[dict[str, Any]],
    embed_model: str,
    embedding_api_url: str = SEARCH_DEFAULT_EMBEDDING_API_URL,
    embedding_timeout: float = SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
    cache_root: Path | None = None,
    progress: Callable[[str], None] | None = None,
    max_auto_embed: int | None = DEFAULT_MAX_AUTO_EMBED,
    batch_size: int = DEFAULT_INDEX_BATCH,
    batch_pause_s: float = DEFAULT_INDEX_PAUSE_S,
    dry_run: bool = False,
) -> tuple[Any, dict[str, Any]]:
    """Public index entrypoint. Write paths are serialised by a lock file.

    `dry_run=True` is strictly read-only: no directory creation, no schema
    creation, no meta writes. It is used by `status`.
    """
    if dry_run:
        conn = _open_index_metadata_readonly(corpus_root, cache_root=cache_root)
        stats = _index_delta_stats_readonly(
            conn,
            scope,
            items,
            embed_model,
            embedding_api_url,
            max_auto_embed,
        )
        return conn, stats

    lock_handle = _acquire_index_write_lock(corpus_root, cache_root=cache_root)
    try:
        return _ensure_index_unlocked(
            corpus_root,
            scope,
            items,
            embed_model,
            embedding_api_url=embedding_api_url,
            embedding_timeout=embedding_timeout,
            cache_root=cache_root,
            progress=progress,
            max_auto_embed=max_auto_embed,
            batch_size=batch_size,
            batch_pause_s=batch_pause_s,
            dry_run=False,
        )
    finally:
        _release_index_write_lock(lock_handle)


def _ensure_index_unlocked(
    corpus_root: Path,
    scope: str,
    items: list[dict[str, Any]],
    embed_model: str,
    embedding_api_url: str = SEARCH_DEFAULT_EMBEDDING_API_URL,
    embedding_timeout: float = SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
    cache_root: Path | None = None,
    progress: Callable[[str], None] | None = None,
    max_auto_embed: int | None = DEFAULT_MAX_AUTO_EMBED,
    batch_size: int = DEFAULT_INDEX_BATCH,
    batch_pause_s: float = DEFAULT_INDEX_PAUSE_S,
    dry_run: bool = False,
) -> tuple[Any, dict[str, Any]]:
    """Open the persistent index for `corpus_root` and reconcile against
    `items` for the given `scope`. Only new sections cost embedding work;
    removed ones are pruned; unchanged ones are reused.

    Embedding runs in batches (`batch_size`, default 32) with no pause by
    default (`batch_pause_s`, default 0s) because vectors now come from a
    cloud API instead of a local Metal allocator. The DB is committed after
    every batch, so Ctrl+C only loses the current in-flight batch and any
    sections in it are auto-cleaned on the next run.

    If `max_auto_embed` is not None and the new-section delta would
    require more than that many chunks of embedding work, the function
    returns *without* embedding and sets `stats["delta_too_large"] = True`
    plus `stats["pending_chunks"]`. Callers like `cmd_search` use that to
    nudge the user to run `index` explicitly. Pass `max_auto_embed=None`
    from `cmd_index` to force a full run.

    `cache_root=None` puts the index inside the corpus at
    `<corpus>/.md-navigator/` (default). Pass a Path to override (legacy
    `~/.cache/md-navigator/` location uses this)."""
    import time

    def _say(msg: str) -> None:
        if progress is not None:
            progress(msg)
        else:
            print(msg, file=sys.stderr)

    # 1. Decide vec_dim. Re-open path: read recorded dim from meta. Cold
    #    path: probe the server (skipped in dry_run — no embedding work).
    cache_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=True)
    db_path = cache_dir / "index.sqlite"
    if db_path.exists():
        vec_dim = None  # _open_index will recover from meta
    elif dry_run:
        # No on-disk index yet and we are not going to embed. Use a
        # placeholder dim — the only thing we touch is meta + sections
        # bookkeeping for the count, vectors will never be written.
        vec_dim = 1
    else:
        vec_dim = probe_embedding_dim(
            embed_model,
            embedding_api_url,
            embedding_timeout,
            corpus_root=corpus_root,
        )

    conn = _open_index(cache_root, corpus_root, embed_model, embedding_api_url, vec_dim)

    # 2. Heal anything a previous interrupted run left half-written.
    #    Skipped in dry_run — we report state without mutating it.
    if not dry_run:
        healed = _clean_incomplete_sections(conn, scope)
        if healed:
            _say(f"Healed {healed} incomplete sections from a prior interrupted run (scope={scope}).")
            conn.commit()

    # 3. Build (scope, content_hash) → rowid map for existing sections.
    existing_rows = conn.execute(
        "SELECT rowid, content_hash FROM sections WHERE scope = ?",
        (scope,),
    ).fetchall()
    existing_hash_to_rowid: dict[str, int] = {h: rid for rid, h in existing_rows}
    current_hash_to_item: dict[str, dict[str, Any]] = {it["content_hash"]: it for it in items}

    added_hashes = [h for h in current_hash_to_item if h not in existing_hash_to_rowid]
    removed_hashes = [h for h in existing_hash_to_rowid if h not in current_hash_to_item]
    removed_rowids = [existing_hash_to_rowid[h] for h in removed_hashes]

    stats: dict[str, Any] = {
        "embedded": 0,
        "reused": len(existing_hash_to_rowid) - len(removed_hashes),
        "removed": 0,
        "added_sections": len(added_hashes),
        "removed_sections": len(removed_hashes),
        "total_sections_in_scope": 0,
        "subchunked_sections": 0,
        "delta_too_large": False,
        "pending_chunks": 0,
    }

    if removed_rowids and not dry_run:
        _say(f"Pruning {len(removed_rowids)} stale sections (scope={scope})...")
        stats["removed"] = _delete_section_rowids(conn, removed_rowids)
        conn.commit()

    # Refresh metadata on surviving rows. content_hash (= rel + start_line +
    # body) is the diff key, but file_id is positional from iter_markdown
    # order and section_id depends on it; file_description / file_title
    # change with frontmatter or H1 edits that don't touch this section's
    # body. Without this refresh those fields stay at index-time values and
    # downstream consumers that resolve against a fresh map see drift.
    if not dry_run:
        surviving_hashes = [
            h for h in current_hash_to_item if h in existing_hash_to_rowid
        ]
        if surviving_hashes:
            section_updates = []
            fts_updates = []
            for h in surviving_hashes:
                it = current_hash_to_item[h]
                rowid = existing_hash_to_rowid[h]
                section_updates.append(
                    (
                        it["section_id"],
                        it["file_id"],
                        it["file_description"],
                        it["file_title"],
                        rowid,
                    )
                )
                chain = (
                    " > ".join(it["heading_chain"]) if it["heading_chain"] else ""
                )
                chain_for_fts = (chain + " " + it["heading_text"]).strip()
                fts_updates.append(
                    (
                        it["file_description"],
                        it["file_title"],
                        chain_for_fts,
                        rowid,
                    )
                )
            conn.executemany(
                "UPDATE sections SET section_id=?, file_id=?, "
                "file_description=?, file_title=? WHERE rowid=?",
                section_updates,
            )
            conn.executemany(
                "UPDATE sections_fts SET description=?, title=?, "
                "heading_chain=? WHERE rowid=?",
                fts_updates,
            )
            conn.commit()

    # 4. Build a chunk plan for added sections so we can decide whether the
    #    delta is small enough to embed inline, or too large and should
    #    require an explicit `index` run.
    if added_hashes:
        section_next = _next_id(
            conn, "next_section_rowid", "SELECT MAX(rowid) FROM sections"
        )
        chunk_next = _next_id(
            conn, "next_chunk_id", "SELECT MAX(chunk_id) FROM chunks"
        )

        section_rows: list[tuple[Any, ...]] = []
        fts_rows: list[tuple[Any, ...]] = []
        # (section_rowid, chunk_idx, chunk_body, chunk_hash, passage)
        plan: list[tuple[int, int, str, str, str]] = []
        subchunked_count = 0

        for content_hash in added_hashes:
            item = current_hash_to_item[content_hash]
            section_rowid = section_next
            section_next += 1
            chain_str = " > ".join(item["heading_chain"]) if item["heading_chain"] else ""
            section_rows.append(
                (
                    section_rowid,
                    item["section_id"],
                    scope,
                    item["file_id"],
                    item["relative_path"],
                    item["start_line"],
                    item["level"],
                    item["heading_text"],
                    chain_str,
                    item["body"],
                    item["file_description"],
                    item["file_title"],
                    item["content_hash"],
                    item["token_count"],
                )
            )
            chain_for_fts = (chain_str + " " + item["heading_text"]).strip()
            fts_rows.append(
                (
                    section_rowid,
                    item["file_description"],
                    item["file_title"],
                    chain_for_fts,
                    item["body"],
                )
            )
            unit_chunks = _chunks_for_item(item)
            if scope == "sections" and len(unit_chunks) > 1:
                subchunked_count += 1
            for chunk_idx, chunk_body, chunk_hash, passage in unit_chunks:
                plan.append((section_rowid, chunk_idx, chunk_body, chunk_hash, passage))

        stats["subchunked_sections"] = subchunked_count
        stats["pending_chunks"] = len(plan)

        if dry_run:
            # Report-only path used by `cmd_status`. Compute counts above,
            # then return without touching the DB. `delta_too_large` is
            # still set so callers can show the same NEEDS-WARMUP message.
            stats["delta_too_large"] = (
                max_auto_embed is not None and len(plan) > max_auto_embed
            )
            stats["total_sections_in_scope"] = int(
                conn.execute(
                    "SELECT COUNT(*) FROM sections WHERE scope = ?", (scope,)
                ).fetchone()[0]
            )
            return conn, stats

        if max_auto_embed is not None and len(plan) > max_auto_embed:
            stats["delta_too_large"] = True
            stats["total_sections_in_scope"] = int(
                conn.execute(
                    "SELECT COUNT(*) FROM sections WHERE scope = ?", (scope,)
                ).fetchone()[0]
            )
            return conn, stats

        # 5. Commit section + FTS rows up front. Chunks/vec are written
        #    batch-by-batch so interrupt is bounded. The interrupt heal
        #    pass at the top of the next run will sweep any sections left
        #    without chunks.
        conn.executemany(
            "INSERT INTO sections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            section_rows,
        )
        conn.executemany(
            "INSERT INTO sections_fts (rowid, description, title, heading_chain, body) "
            "VALUES (?, ?, ?, ?, ?)",
            fts_rows,
        )
        conn.commit()

        passages = [p[4] for p in plan]
        total = len(passages)
        if total:
            _say(
                f"Indexing {total} new chunks "
                f"({len(added_hashes)} sections, {subchunked_count} sub-chunked, "
                f"scope={scope}) — batch={batch_size}, pause={int(batch_pause_s * 1000)}ms"
            )

        done = 0
        for batch_start in range(0, total, max(1, batch_size)):
            batch = passages[batch_start : batch_start + max(1, batch_size)]
            batch_plan = plan[batch_start : batch_start + max(1, batch_size)]
            try:
                batch_vecs = _embed_texts_http(
                    embed_model,
                    batch,
                    embedding_api_url,
                    embedding_timeout,
                    corpus_root=corpus_root,
                )
            except RuntimeError as exc:
                # Mid-batch failure. Sections + FTS rows for the whole plan
                # are already on disk; chunks/vec rows for already-committed
                # batches are persisted (one commit per batch). The next run
                # heals incomplete sections and resumes from where we stopped.
                _say(
                    f"\nIndexing interrupted after {done}/{total} chunks "
                    f"(scope={scope}). Already-embedded chunks are on disk."
                )
                _say(
                    f"To resume, re-run:\n"
                    f"    md_navigator.py index '{corpus_root}'\n"
                )
                raise

            chunk_rows: list[tuple[Any, ...]] = []
            vec_rows: list[tuple[int, bytes]] = []
            for (section_rowid, chunk_idx, chunk_body, chunk_hash, _passage), vec in zip(
                batch_plan, batch_vecs
            ):
                chunk_id = chunk_next
                chunk_next += 1
                chunk_rows.append(
                    (chunk_id, section_rowid, chunk_idx, chunk_hash, chunk_body)
                )
                vec_rows.append((chunk_id, _vec_to_blob(vec)))
            conn.executemany(
                "INSERT INTO chunks (chunk_id, section_rowid, chunk_idx, chunk_hash, chunk_body) "
                "VALUES (?, ?, ?, ?, ?)",
                chunk_rows,
            )
            conn.executemany(
                "INSERT INTO sections_vec (rowid, embedding) VALUES (?, ?)",
                vec_rows,
            )
            _set_counter(conn, "next_section_rowid", section_next)
            _set_counter(conn, "next_chunk_id", chunk_next)
            conn.commit()
            stats["embedded"] += len(batch_vecs)
            done += len(batch_vecs)

            # Tail of the last section in this batch — useful breadcrumb so
            # the user can see *what* is being processed when scrolls go by.
            tail_section_rowid = batch_plan[-1][0]
            tail = conn.execute(
                "SELECT relative_path, start_line FROM sections WHERE rowid = ?",
                (tail_section_rowid,),
            ).fetchone()
            if tail:
                rel, ln = tail
                pct = int(done / total * 100) if total else 100
                _say(f"  [{done}/{total} {pct}%] {rel}:L{ln}")

            if batch_pause_s > 0 and batch_start + batch_size < total:
                time.sleep(batch_pause_s)

    stats["total_sections_in_scope"] = int(
        conn.execute(
            "SELECT COUNT(*) FROM sections WHERE scope = ?", (scope,)
        ).fetchone()[0]
    )
    return conn, stats


# --- Warmup command ------------------------------------------------------


def cmd_index(args) -> int:
    """Cold-start (or top-up) the persistent index for a corpus across both
    scopes (`sections` and `descriptions`). Heavy operation — the user
    triggers it explicitly when they have time. `search` and `overlaps`
    afterwards are near-instant on the same corpus."""
    from .folder_map import build_map
    from .sections import build_items_from_map

    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=True)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1

    cache_root = (
        Path(args.cache_dir).expanduser() if getattr(args, "cache_dir", None) else None
    )

    totals = {"embedded": 0, "reused": 0, "removed": 0}
    for scope in ("sections", "descriptions"):
        items = build_items_from_map(map_data, scope=scope)
        if not items:
            print(f"(no items for scope={scope}; skipping)", file=sys.stderr)
            continue
        try:
            _, stats = ensure_index(
                corpus_root,
                scope,
                items,
                args.embed_model,
                embedding_api_url=args.embedding_api_url,
                embedding_timeout=args.embedding_timeout,
                cache_root=cache_root,
                max_auto_embed=None,  # explicit warmup: no cap
                batch_size=args.batch_size,
                batch_pause_s=args.batch_pause_ms / 1000.0,
            )
        except ModuleNotFoundError as exc:
            print(
                f"Missing Python dependency: {exc}.\n"
                f"  This script needs uv to resolve its inline deps "
                f"(`numpy`, `sqlite-vec`, `pyyaml`).\n"
                f"  Run it via the uv shebang:\n"
                f"    chmod +x md_navigator.py && ./md_navigator.py index ...\n"
                f"  Or explicitly:\n"
                f"    uv run --script md_navigator.py index ...\n"
                f"  Install uv if missing: `brew install uv` (macOS) or "
                f"https://docs.astral.sh/uv.",
                file=sys.stderr,
            )
            return 3
        except RuntimeError as exc:
            print(
                f"Embedding API call failed: {exc}\n"
                f"  Check OPENROUTER_API_KEY env var or `.openrouter.key` file "
                f"(see SKILL.md → First-time setup).",
                file=sys.stderr,
            )
            return 3
        print(
            f"[{scope}] embedded={stats['embedded']} reused={stats['reused']} "
            f"removed={stats['removed_sections']} "
            f"total_in_scope={stats['total_sections_in_scope']}",
            file=sys.stderr,
        )
        totals["embedded"] += stats["embedded"]
        totals["reused"] += stats["reused"]
        totals["removed"] += stats["removed_sections"]

    index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    print(
        f"Index ready at {index_dir / 'index.sqlite'}\n"
        f"  embedded: {totals['embedded']} (newly computed this run)\n"
        f"  reused:   {totals['reused']} (already on disk, unchanged)\n"
        f"  removed:  {totals['removed']} (deleted or rewritten files)"
    )
    return 0


# --- Status / freshness report -------------------------------------------


def cmd_status(args) -> int:
    """Print the freshness of the on-disk index for a corpus without
    touching it. Counts pending added / removed sections vs the current
    Markdown tree, classifies overall state, and recommends a next action.

    Cheap operation — runs `ensure_index(..., dry_run=True)` which skips
    the embedding probe, the prune, and the embed loop. No HTTP calls.
    No DB writes. Use it before `search` on a corpus you have been
    editing, to know whether `index` is needed first."""
    from .folder_map import build_map
    from .sections import build_items_from_map

    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    cache_root = (
        Path(args.cache_dir).expanduser() if getattr(args, "cache_dir", None) else None
    )
    index_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = index_dir / "index.sqlite"

    print(f"Corpus: {corpus_root}")
    print(f"Index:  {db_path}")

    if not db_path.exists():
        print("Status: NO INDEX")
        print(f"  Run: md_navigator.py index '{corpus_root}'")
        return 0

    import datetime

    mtime = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)
    print(f"Last touched: {mtime.isoformat(timespec='seconds')}")

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=False)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1

    max_auto_embed = (
        None
        if getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED) == 0
        else int(getattr(args, "max_auto_embed", DEFAULT_MAX_AUTO_EMBED))
    )

    totals = {
        "added_sections": 0,
        "removed_sections": 0,
        "reused": 0,
        "pending_chunks": 0,
        "in_scope": 0,
        "delta_too_large": False,
        "metadata_mismatch": False,
    }
    for scope in ("sections", "descriptions"):
        items = build_items_from_map(map_data, scope=scope)
        if not items:
            continue
        try:
            _, stats = ensure_index(
                corpus_root,
                scope,
                items,
                args.embed_model,
                embedding_api_url=args.embedding_api_url,
                embedding_timeout=args.embedding_timeout,
                cache_root=cache_root,
                max_auto_embed=max_auto_embed,
                dry_run=True,
            )
        except ModuleNotFoundError as exc:
            print(
                f"Missing Python dependency: {exc}.\n"
                f"  Run via the uv shebang or `uv run --script md_navigator.py status ...`",
                file=sys.stderr,
            )
            return 3
        print(
            f"[{scope}] added={stats['added_sections']} "
            f"removed={stats['removed_sections']} "
            f"reused={stats['reused']} "
            f"pending_chunks={stats['pending_chunks']} "
            f"total={stats['total_sections_in_scope']}"
            f"{' metadata=MISMATCH' if stats.get('metadata_mismatch') else ''}"
        )
        totals["added_sections"] += stats["added_sections"]
        totals["removed_sections"] += stats["removed_sections"]
        totals["reused"] += stats["reused"]
        totals["pending_chunks"] += stats["pending_chunks"]
        totals["in_scope"] += stats["total_sections_in_scope"]
        if stats.get("delta_too_large"):
            totals["delta_too_large"] = True
        if stats.get("metadata_mismatch"):
            totals["metadata_mismatch"] = True

    pending = totals["pending_chunks"]
    removed = totals["removed_sections"]
    added = totals["added_sections"]

    # ID drift check: positional file_id stored at index time stays put while
    # corpus reorders shift the fresh-map positional id. Content-hash diff
    # doesn't see this — same body at same line keeps the same row. Without
    # the check, `status` says FRESH but a downstream `pick` resolving stale
    # ids against a fresh map pulls the wrong file. search.cmd_search now
    # remaps to fresh ids, so drift is benign there; this stays as visible
    # signal so other consumers and humans know to reindex for clean state.
    import sqlite3

    fresh_file_id_by_path = {f["relative_path"]: f["id"] for f in map_data["files"]}
    drift_count = 0
    try:
        conn_ro = _open_index_readonly(corpus_root, cache_root=cache_root)
        try:
            rows = conn_ro.execute(
                "SELECT DISTINCT relative_path, file_id FROM sections"
            ).fetchall()
        finally:
            conn_ro.close()
        for path, idx_fid in rows:
            fresh_fid = fresh_file_id_by_path.get(path)
            if fresh_fid is not None and int(fresh_fid) != int(idx_fid):
                drift_count += 1
    except (FileNotFoundError, sqlite3.OperationalError):
        pass

    if totals["metadata_mismatch"]:
        print(
            "Status: NEEDS REBUILD — index metadata/schema does not match the "
            "current model, API URL, or schema version."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
    elif added == 0 and removed == 0:
        print("Status: FRESH — no pending changes; `search` is instant.")
    elif totals["delta_too_large"]:
        print(
            f"Status: NEEDS WARMUP — {added} new sections / {pending} chunks "
            f"pending (cap {max_auto_embed})."
        )
        print(f"  Run: md_navigator.py index '{corpus_root}'")
    else:
        print(
            f"Status: HEALTHY — {added} new / {removed} removed sections, "
            f"{pending} chunks pending. `search` will auto-handle the delta."
        )
        print(
            f"  Optional: md_navigator.py index '{corpus_root}'  "
            f"(eagerly warm the index instead of paying inside search)"
        )
    if drift_count:
        print(
            f"  ID drift: {drift_count} files have shifted positional ids "
            f"since indexed. `search` auto-remaps to fresh ids; `index` "
            f"prunes the stale rows."
        )
    return 0


# --- Semantic neighbours / link coherence --------------------------------


def find_corpus_root_for(anchor: Path) -> Path | None:
    """Walk upward from `anchor` looking for `.md-navigator/index.sqlite`.
    Returns the corpus root that owns the index, or None."""
    for parent in [anchor.parent, *anchor.parent.parents]:
        if (parent / ".md-navigator" / "index.sqlite").exists():
            return parent
    return None


def _open_index_readonly(corpus_root: Path, cache_root: Path | None = None):
    """Open the persistent index without running migrations or writing
    meta. Caller must check it exists; raises FileNotFoundError otherwise."""
    import sqlite3
    import sqlite_vec

    cache_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = cache_dir / "index.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def find_semantic_neighbors(
    corpus_root: Path,
    anchor_paths: list[Path],
    k: int,
    excluded_relative_paths: set[str],
    cache_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Top-K dense neighbours of the anchor files' sections, restricted to
    other files and the `sections` scope. Reuses vectors already on disk —
    no HTTP calls, no embedding work. Returns empty list when:

    - the corpus has no on-disk index;
    - none of the anchor paths are in the index (e.g. file added after
      the last `index` run).

    `excluded_relative_paths` filters out files that are already part of
    the linked neighbourhood (so the semantic block adds unobvious files,
    not duplicates of wikilinks/backlinks). Anchor files themselves are
    always excluded.

    Each returned entry: {relative_path, section_id, heading_chain,
    distance (lower=closer), matched_anchor_section}. Aggregated by file:
    the best (lowest-distance) section per other-file is kept."""
    try:
        conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    except (FileNotFoundError, Exception):
        return []

    try:
        # Anchor sections, identified by relative_path. Compute relative
        # paths the same way the indexer did.
        anchor_rels: list[str] = []
        for anchor in anchor_paths:
            try:
                anchor_rels.append(str(anchor.resolve().relative_to(corpus_root.resolve())))
            except ValueError:
                # Anchor outside corpus root — skip it.
                pass
        if not anchor_rels:
            return []

        placeholders = ",".join("?" * len(anchor_rels))
        anchor_chunks = conn.execute(
            f"SELECT chunks.chunk_id, chunks.section_rowid, "
            f"sections.section_id, sections.relative_path "
            f"FROM chunks "
            f"JOIN sections ON sections.rowid = chunks.section_rowid "
            f"WHERE sections.scope = 'sections' "
            f"  AND sections.relative_path IN ({placeholders})",
            anchor_rels,
        ).fetchall()
        if not anchor_chunks:
            return []

        anchor_rel_set = set(anchor_rels)
        exclude = set(excluded_relative_paths) | anchor_rel_set

        # KNN per anchor chunk. Over-fetch to survive the exclude filter
        # — we typically want top-K *files*, not top-K rows.
        over_fetch = max(50, k * 8)

        import numpy as np  # type: ignore

        # Aggregate: per other-file, best (lowest) distance + which anchor
        # section matched.
        best_per_file: dict[str, dict[str, Any]] = {}

        for chunk_id, _section_rowid, anchor_section_id, _anchor_rel in anchor_chunks:
            vec_row = conn.execute(
                "SELECT embedding FROM sections_vec WHERE rowid = ?",
                (chunk_id,),
            ).fetchone()
            if not vec_row:
                continue
            q_blob = vec_row[0]

            try:
                rows = conn.execute(
                    "SELECT s.rowid, s.relative_path, s.section_id, "
                    "s.heading_chain, vec.distance "
                    "FROM sections_vec vec "
                    "JOIN chunks c ON c.chunk_id = vec.rowid "
                    "JOIN sections s ON s.rowid = c.section_rowid "
                    "WHERE vec.embedding MATCH ? AND vec.k = ? "
                    "  AND s.scope = 'sections' "
                    "ORDER BY vec.distance",
                    (q_blob, over_fetch),
                ).fetchall()
            except Exception:
                continue

            for _rowid, rel, section_id, heading_chain, distance in rows:
                if rel in exclude:
                    continue
                d = float(distance)
                prev = best_per_file.get(rel)
                if prev is None or d < prev["distance"]:
                    best_per_file[rel] = {
                        "relative_path": rel,
                        "section_id": section_id,
                        "heading_chain": heading_chain,
                        "distance": d,
                        "matched_anchor_section": anchor_section_id,
                    }

        sorted_files = sorted(best_per_file.values(), key=lambda x: x["distance"])
        return sorted_files[: max(0, k)]
    finally:
        conn.close()


def check_explicit_link_coherence(
    corpus_root: Path,
    anchor: Path,
    linked_targets: list[Path],
    threshold: float = 0.4,
    cache_root: Path | None = None,
) -> list[dict[str, Any]]:
    """For each explicit link from `anchor` to a `linked_target`, compute
    the **best** dense distance between any anchor section and any target
    section. Returns links where best distance exceeds `threshold`
    (= semantically far). These are candidates for "off-topic link"
    review — owner is `1md-graph`, not navigator.

    `threshold` is on the L2 distance scale used by sections_vec
    (lower=closer). Default 0.4 ≈ cos similarity ≈ 0.92 — fires only on
    genuinely distant pairs.

    Returns [] if no index or anchor not indexed.
    Each entry: {target_relative_path, best_distance, anchor_section,
    target_section}."""
    try:
        conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    except (FileNotFoundError, Exception):
        return []

    try:
        try:
            anchor_rel = str(anchor.resolve().relative_to(corpus_root.resolve()))
        except ValueError:
            return []

        anchor_chunks = conn.execute(
            "SELECT chunks.chunk_id, sections.section_id "
            "FROM chunks "
            "JOIN sections ON sections.rowid = chunks.section_rowid "
            "WHERE sections.scope = 'sections' AND sections.relative_path = ?",
            (anchor_rel,),
        ).fetchall()
        if not anchor_chunks:
            return []

        suspicious: list[dict[str, Any]] = []
        for target in linked_targets:
            try:
                target_rel = str(target.resolve().relative_to(corpus_root.resolve()))
            except ValueError:
                continue

            target_chunks = conn.execute(
                "SELECT chunks.chunk_id, sections.section_id "
                "FROM chunks "
                "JOIN sections ON sections.rowid = chunks.section_rowid "
                "WHERE sections.scope = 'sections' AND sections.relative_path = ?",
                (target_rel,),
            ).fetchall()
            if not target_chunks:
                continue

            best = None
            best_pair: tuple[str, str] | None = None
            for a_chunk_id, a_section_id in anchor_chunks:
                vec_row = conn.execute(
                    "SELECT embedding FROM sections_vec WHERE rowid = ?",
                    (a_chunk_id,),
                ).fetchone()
                if not vec_row:
                    continue
                q_blob = vec_row[0]
                rows = conn.execute(
                    "SELECT vec.distance, sections.section_id "
                    "FROM sections_vec vec "
                    "JOIN chunks c ON c.chunk_id = vec.rowid "
                    "JOIN sections ON sections.rowid = c.section_rowid "
                    "WHERE vec.embedding MATCH ? AND vec.k = ? "
                    "  AND sections.scope = 'sections' "
                    "  AND sections.relative_path = ? "
                    "ORDER BY vec.distance LIMIT 1",
                    (q_blob, max(5, len(target_chunks)), target_rel),
                ).fetchall()
                for distance, t_section_id in rows:
                    d = float(distance)
                    if best is None or d < best:
                        best = d
                        best_pair = (a_section_id, t_section_id)

            if best is not None and best > threshold:
                suspicious.append(
                    {
                        "target_relative_path": target_rel,
                        "best_distance": best,
                        "anchor_section": best_pair[0] if best_pair else "",
                        "target_section": best_pair[1] if best_pair else "",
                    }
                )

        return suspicious
    finally:
        conn.close()


# --- Clustering (folder-structure suggestion) ----------------------------


def _kmeans_pp_init(X, k: int, rng) -> Any:
    """K-means++ seeding: first centroid random, each next sampled by
    distance² from the closest existing centroid. Better than uniform
    random init at avoiding empty / degenerate clusters."""
    import numpy as np  # type: ignore

    n = len(X)
    idxs = [int(rng.integers(n))]
    for _ in range(k - 1):
        # Min squared distance from each point to the existing centroid set.
        diff = X[:, None, :] - X[idxs][None, :, :]
        sq = np.sum(diff * diff, axis=2)
        min_sq = sq.min(axis=1)
        total = float(min_sq.sum())
        if total <= 1e-12:
            idxs.append(int(rng.integers(n)))
            continue
        probs = min_sq / total
        idxs.append(int(rng.choice(n, p=probs)))
    return X[idxs].copy()


def _kmeans(X, k: int, max_iter: int = 50, seed: int = 42):
    """Plain Lloyd's K-means in NumPy. Inputs are expected to be
    L2-normalized — Euclidean distance on the unit sphere is monotone
    with cosine similarity, so this is effectively spherical K-means."""
    import numpy as np  # type: ignore

    rng = np.random.default_rng(seed)
    centroids = _kmeans_pp_init(X, k, rng)
    assignments = np.zeros(len(X), dtype=np.int64)
    for _ in range(max_iter):
        # Vectorised distance: (N, K) matrix of squared L2 distances.
        diff = X[:, None, :] - centroids[None, :, :]
        sq = np.sum(diff * diff, axis=2)
        new_assignments = np.argmin(sq, axis=1)
        if np.array_equal(new_assignments, assignments):
            break
        assignments = new_assignments
        new_centroids = np.zeros_like(centroids)
        for j in range(k):
            mask = assignments == j
            if mask.any():
                new_centroids[j] = X[mask].mean(axis=0)
            else:
                # Empty cluster — reseed to a random point.
                new_centroids[j] = X[int(rng.integers(len(X)))]
        # Re-normalise centroids onto the unit sphere — keeps the
        # spherical-K-means invariant intact for cosine-style data.
        norms = np.linalg.norm(new_centroids, axis=1, keepdims=True)
        new_centroids = new_centroids / np.maximum(norms, 1e-12)
        if np.allclose(new_centroids, centroids, atol=1e-6):
            centroids = new_centroids
            break
        centroids = new_centroids
    return assignments, centroids


def cluster_sections(
    corpus_root: Path,
    k: int,
    cache_root: Path | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Group all `sections`-scope chunks of the corpus into `k` semantic
    clusters using K-means on L2-normalised dense vectors. Aggregates
    chunks → sections by majority, then summarises each cluster: top
    files by section count, centroid section (nearest to cluster mean),
    internal cohesion (mean cosine within the cluster).

    Returns:
        {
            "k": int,
            "n_sections": int,
            "n_chunks": int,
            "clusters": [
                {
                    "id": int,
                    "size": int,
                    "cohesion": float,
                    "centroid_section": str,
                    "centroid_path": str,
                    "centroid_heading_chain": str,
                    "top_files": [(relative_path, section_count), ...],
                    "common_parent": str,  # longest shared path prefix
                    "section_ids": [str, ...],
                }
            ]
        }
    Raises FileNotFoundError if the corpus has no on-disk index."""
    import numpy as np  # type: ignore

    conn = _open_index_readonly(corpus_root, cache_root=cache_root)
    try:
        rows = conn.execute(
            "SELECT chunks.chunk_id, chunks.section_rowid, "
            "sections.section_id, sections.relative_path, "
            "sections.heading_chain, sections.token_count, vec.embedding "
            "FROM chunks "
            "JOIN sections_vec vec ON vec.rowid = chunks.chunk_id "
            "JOIN sections ON sections.rowid = chunks.section_rowid "
            "WHERE sections.scope = 'sections' "
            "ORDER BY chunks.chunk_id"
        ).fetchall()
        if not rows:
            return {"k": 0, "n_sections": 0, "n_chunks": 0, "clusters": []}

        vectors = np.stack([np.frombuffer(r[6], dtype="float32") for r in rows])
        chunk_section_rowid = np.array([r[1] for r in rows], dtype=np.int64)
        section_meta: dict[int, dict[str, Any]] = {}
        for r in rows:
            rowid = r[1]
            if rowid not in section_meta:
                section_meta[rowid] = {
                    "section_id": r[2],
                    "relative_path": r[3],
                    "heading_chain": r[4] or "",
                    "token_count": int(r[5]),
                }

        n_sections = len(section_meta)
        k_actual = max(1, min(int(k), n_sections))

        assignments, centroids = _kmeans(vectors, k_actual, seed=seed)

        # Aggregate chunk → section by majority vote.
        from collections import Counter

        section_to_chunks: dict[int, list[int]] = {}
        for i, sec_rowid in enumerate(chunk_section_rowid):
            section_to_chunks.setdefault(int(sec_rowid), []).append(i)
        section_cluster: dict[int, int] = {}
        for sec_rowid, chunk_idxs in section_to_chunks.items():
            votes = Counter(int(assignments[i]) for i in chunk_idxs)
            section_cluster[sec_rowid] = votes.most_common(1)[0][0]

        clusters: list[dict[str, Any]] = []
        for cid in range(k_actual):
            section_rowids = [s for s, c in section_cluster.items() if c == cid]
            if not section_rowids:
                continue
            chunk_idxs = [i for s in section_rowids for i in section_to_chunks[s]]
            cluster_vecs = vectors[chunk_idxs]
            mean_vec = cluster_vecs.mean(axis=0)
            mean_norm = float(np.linalg.norm(mean_vec))
            if mean_norm > 1e-12:
                mean_vec = mean_vec / mean_norm
            # Cohesion = mean cosine to cluster centroid.
            cohesion = float(np.mean(cluster_vecs @ mean_vec))
            # Centroid section: section whose mean vector is closest to mean_vec.
            section_mean_vecs: dict[int, Any] = {}
            for s in section_rowids:
                mv = vectors[section_to_chunks[s]].mean(axis=0)
                nrm = float(np.linalg.norm(mv))
                section_mean_vecs[s] = mv / nrm if nrm > 1e-12 else mv
            best = max(section_rowids, key=lambda s: float(section_mean_vecs[s] @ mean_vec))
            best_meta = section_meta[best]
            # Top files by section count.
            path_counts = Counter(section_meta[s]["relative_path"] for s in section_rowids)
            top_files = path_counts.most_common(5)
            # Common parent dir (longest shared path prefix segment).
            paths = [section_meta[s]["relative_path"] for s in section_rowids]
            common_parent = _longest_common_parent(paths)
            clusters.append(
                {
                    "id": cid,
                    "size": len(section_rowids),
                    "cohesion": cohesion,
                    "centroid_section": best_meta["section_id"],
                    "centroid_path": best_meta["relative_path"],
                    "centroid_heading_chain": best_meta["heading_chain"],
                    "top_files": top_files,
                    "common_parent": common_parent,
                    "section_ids": [section_meta[s]["section_id"] for s in section_rowids],
                }
            )

        clusters.sort(key=lambda c: -c["cohesion"])
        return {
            "k": k_actual,
            "n_sections": n_sections,
            "n_chunks": len(rows),
            "clusters": clusters,
        }
    finally:
        conn.close()


def _longest_common_parent(paths: list[str]) -> str:
    """Longest path prefix shared by all input paths, at directory
    granularity. '_ops/criteria/foo.md' + '_ops/criteria/bar.md' →
    '_ops/criteria'; mixed paths → ''."""
    if not paths:
        return ""
    parts = [p.split("/") for p in paths]
    out: list[str] = []
    for chunk in zip(*parts):
        if len(set(chunk)) == 1 and chunk[0]:
            out.append(chunk[0])
        else:
            break
    if out and out[-1].endswith(".md"):
        out.pop()
    return "/".join(out)


def cmd_cluster(args) -> int:
    """Group all sections of a corpus into K semantic clusters. Useful
    for IA-audit: each cluster suggests a coherent topic; the
    `common_parent` field hints at whether the existing folder layout
    matches the embedding-based topology. Read-only — no embedding work,
    just K-means on vectors already on disk."""
    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    cache_root = (
        Path(args.cache_dir).expanduser() if getattr(args, "cache_dir", None) else None
    )

    try:
        result = cluster_sections(
            corpus_root,
            k=args.k,
            cache_root=cache_root,
            seed=args.seed,
        )
    except FileNotFoundError:
        print(
            f"No index for {corpus_root}.\n"
            f"  Run: md_navigator.py index '{corpus_root}'",
            file=sys.stderr,
        )
        return 4
    except ModuleNotFoundError as exc:
        print(
            f"Missing Python dependency: {exc}.\n"
            f"  Run via the uv shebang or `uv run --script md_navigator.py cluster ...`.",
            file=sys.stderr,
        )
        return 3

    if getattr(args, "json", False):
        # Counter tuples → lists for JSON.
        for c in result["clusters"]:
            c["top_files"] = [list(t) for t in c["top_files"]]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"# Markdown clusters: {corpus_root}")
    print(f"K = {result['k']}, sections = {result['n_sections']}, chunks = {result['n_chunks']}")
    print(
        "Read-only clustering of on-disk vectors. Each cluster suggests one "
        "topic; mismatched common_parent vs centroid_path is an IA signal."
    )
    print()
    for c in result["clusters"]:
        head_chain = c["centroid_heading_chain"]
        print(f"## Cluster {c['id'] + 1} — {c['size']} sections (cohesion {c['cohesion']:.3f})")
        if c["common_parent"]:
            print(f"  common_parent: {c['common_parent']}/")
        print(f"  centroid:      [{c['centroid_section']}] {c['centroid_path']}")
        if head_chain:
            print(f"                 {head_chain}")
        print("  top files:")
        for path, count in c["top_files"]:
            print(f"    - {path} ({count} sections)")
        print()
    return 0
