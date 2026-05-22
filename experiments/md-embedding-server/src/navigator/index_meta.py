"""Index metadata layer: schema, on-disk layout, meta key/value, sticky
model resolution, and the three flavours of `open` (write, readonly,
metadata-only-readonly).

This module has no knowledge of the embed pipeline (`index_build.py`),
clustering (`index_cluster.py`), or status reporting (`index_status.py`).
Every other index_* module imports from here; this module imports only
from `embeddings` (for the dim probe)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .embeddings import (
    SEARCH_DEFAULT_EMBEDDING_API_URL,
    SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
    _embed_texts_http,
)


SCHEMA_VERSION = 4
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
        "  profile_type TEXT,"
        "  profile_subject TEXT,"
        "  profile_owns_terms TEXT,"
        "  profile_mentions TEXT,"
        "  profile_evidence TEXT,"
        "  profile_confidence REAL,"
        "  profile_version TEXT,"
        "  profile_model TEXT,"
        "  profile_classified_at TEXT,"
        "  profile_source_mtime REAL,"
        "  profile_method TEXT,"
        "  UNIQUE(scope, content_hash)"
        ")"
    )
    _ensure_profile_columns(conn)
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


def _ensure_profile_columns(conn) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(sections)").fetchall()}
    columns = {
        "profile_type": "TEXT",
        "profile_subject": "TEXT",
        "profile_owns_terms": "TEXT",
        "profile_mentions": "TEXT",
        "profile_evidence": "TEXT",
        "profile_confidence": "REAL",
        "profile_version": "TEXT",
        "profile_model": "TEXT",
        "profile_classified_at": "TEXT",
        "profile_source_mtime": "REAL",
        "profile_method": "TEXT",
    }
    for name, ddl in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE sections ADD COLUMN {name} {ddl}")


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
        probe = sqlite3.connect(db_path, timeout=30.0)
        probe.execute("PRAGMA busy_timeout = 30000")
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
        # Caller's vec_dim assumption ("recover from meta") is now stale —
        # meta lived in the dropped file. Re-probe so the fresh schema gets
        # the right dimension instead of crashing on a missing `meta` table.
        if vec_dim is None:
            vec_dim = probe_embedding_dim(
                embed_model, embedding_api_url, corpus_root=corpus_root
            )

    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout = 30000")
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
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=30.0)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def _open_index_readonly(corpus_root: Path, cache_root: Path | None = None):
    """Open the persistent index without running migrations or writing
    meta. Caller must check it exists; raises FileNotFoundError otherwise.

    Unlike `_open_index_metadata_readonly`, this loads `sqlite_vec` so the
    caller can run vector queries on `sections_vec`."""
    import sqlite3
    import sqlite_vec

    cache_dir = _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False)
    db_path = cache_dir / "index.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=30.0)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def resolve_embed_model_for_corpus(
    corpus_root: Path,
    cli_value: str | None,
    cache_root: Path | None = None,
) -> str:
    """Pick the embed model for this invocation. Priority:

    1. Explicit CLI flag (`--embed-model X`) — always wins, may trigger
       drop+reindex on mismatch with stored.
    2. **Sticky** — recorded `embed_model` from existing index meta. Lets a
       corpus indexed on a non-default model stay on it without forcing the
       agent to remember the flag every invocation.
    3. Fallback: `SEARCH_DEFAULT_EMBED_MODEL` for a fresh corpus (no index
       yet) or when meta can't be read.
    """
    from .embeddings import SEARCH_DEFAULT_EMBED_MODEL

    if cli_value:
        return cli_value
    try:
        conn = _open_index_metadata_readonly(corpus_root, cache_root=cache_root)
    except Exception:
        return SEARCH_DEFAULT_EMBED_MODEL
    try:
        recorded = _meta_get(conn, "embed_model")
        return recorded or SEARCH_DEFAULT_EMBED_MODEL
    except Exception:
        return SEARCH_DEFAULT_EMBED_MODEL
    finally:
        conn.close()
