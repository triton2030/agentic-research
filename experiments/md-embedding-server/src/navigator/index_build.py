"""Index build layer: counters, delta apply, embed pipeline, and the
`index` CLI command. Owns every write path against `<corpus>/.md-navigator/`.

Read paths (open-readonly, meta-readonly, sticky model resolution) live
in `index_meta`. Status reporting (`cmd_status`) lives in `index_status`.
Clustering lives in `index_cluster`."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

from .cli_common import (
    add_cache_arg,
    add_embedding_args,
    add_max_heading_level_arg,
)
from .embeddings import (
    SEARCH_DEFAULT_EMBEDDING_API_URL,
    SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
    _embed_texts_http,
    _vec_to_blob,
)
from .index_meta import (
    SCHEMA_VERSION,
    _acquire_index_write_lock,
    _index_dir_for_corpus,
    _meta_get,
    _open_index,
    _open_index_metadata_readonly,
    _release_index_write_lock,
    probe_embedding_dim,
    resolve_embed_model_for_corpus,
)
from .filters import (
    add_path_filter_args,
    apply_path_filters,
    normalize_path_filter_patterns,
    path_matches_any,
)
from .lemmatize import lemmatize_text
from .sections import (
    SUBCHUNK_MAX_TOKENS,
    _chunk_hash_for,
    _contextual_passage,
    _should_subchunk,
    _split_body_into_chunks,
)
from .section_profile import profile_unprofiled_sections


# Cloud embeddings: no Metal cap, no on-laptop heat. Bigger batches amortise
# HTTP latency, and no inter-batch pause is needed.
DEFAULT_INDEX_BATCH = 32
DEFAULT_INDEX_PAUSE_S = 0.0
# Auto-embed cap for `search` / `overlaps`. A single fresh file with a
# handful of sections plus heading renames must not derail the search flow,
# but a true new-corpus delta (hundreds of chunks) should still require an
# explicit `index` run. 50 fits a typical mid-edit session.
DEFAULT_MAX_AUTO_EMBED = 50


def register_index(sub) -> None:
    p = sub.add_parser(
        "index",
        help=(
            "Build / top up the persistent vector index for a corpus. "
            "Heavy operation: writes cloud embeddings to disk in batches. "
            "Run this once when you start working with a project; `search` "
            "and `overlaps` after that are near-instant."
        ),
    )
    p.add_argument("path", help="Folder or Markdown file to index.")
    add_max_heading_level_arg(p)
    add_embedding_args(p)
    add_cache_arg(p)
    add_path_filter_args(p, command_name="indexed sections")
    p.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_INDEX_BATCH,
        help=f"Embedding batch size (default: {DEFAULT_INDEX_BATCH}).",
    )
    p.add_argument(
        "--batch-pause-ms",
        type=int,
        default=int(DEFAULT_INDEX_PAUSE_S * 1000),
        help=(
            f"Sleep between batches in milliseconds "
            f"(default: {int(DEFAULT_INDEX_PAUSE_S * 1000)}). 0 disables the pause."
        ),
    )
    p.set_defaults(func=lambda args: cmd_index(args))


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
    from .index_meta import _meta_set

    _meta_set(conn, counter_key, str(value))


def _filter_existing_rows_by_path(
    rows: list[Any],
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> list[Any]:
    """Filter DB rows whose third column is relative_path."""
    if not include_patterns and not exclude_patterns:
        return rows
    out: list[Any] = []
    for row in rows:
        rel = str(row[2] or "")
        if include_patterns and not path_matches_any(rel, include_patterns):
            continue
        if exclude_patterns and path_matches_any(rel, exclude_patterns):
            continue
        out.append(row)
    return out


def _count_sections_in_path_scope(
    conn,
    scope: str,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> int:
    rows = conn.execute(
        "SELECT rowid, content_hash, relative_path FROM sections WHERE scope = ?",
        (scope,),
    ).fetchall()
    return len(_filter_existing_rows_by_path(rows, include_patterns, exclude_patterns))


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


def pending_files_for_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize not-yet-indexed items by file for status and partial search."""
    by_path: dict[str, dict[str, Any]] = {}
    for item in items:
        path = str(item["relative_path"])
        entry = by_path.setdefault(
            path,
            {
                "relative_path": path,
                "added_sections": 0,
                "pending_chunks": 0,
            },
        )
        entry["added_sections"] += 1
        entry["pending_chunks"] += len(_chunks_for_item(item))
    return sorted(
        by_path.values(),
        key=lambda entry: (-entry["pending_chunks"], entry["relative_path"]),
    )


def removed_files_for_rows(rows: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for row in rows:
        path = str(row[2])
        entry = by_path.setdefault(
            path,
            {"relative_path": path, "removed_sections": 0},
        )
        entry["removed_sections"] += 1
    return sorted(
        by_path.values(),
        key=lambda entry: (-entry["removed_sections"], entry["relative_path"]),
    )


def _index_delta_stats_readonly(
    conn,
    scope: str,
    items: list[dict[str, Any]],
    embed_model: str,
    embedding_api_url: str,
    max_auto_embed: int | None,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> dict[str, Any]:
    """Compute freshness stats without schema creation, meta writes, or pruning."""
    include_patterns = list(path_include or [])
    exclude_patterns = list(path_exclude or [])
    items = apply_path_filters(items, include_patterns, exclude_patterns)
    stats: dict[str, Any] = {
        "embedded": 0,
        "reused": 0,
        "removed": 0,
        "added_sections": 0,
        "removed_sections": 0,
        "pending_files": [],
        "removed_files": [],
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
            "SELECT rowid, content_hash, relative_path FROM sections WHERE scope = ?",
            (scope,),
        ).fetchall()
    except Exception:
        stats["metadata_mismatch"] = True
        return stats

    existing_rows = _filter_existing_rows_by_path(
        existing_rows,
        include_patterns,
        exclude_patterns,
    )
    existing_hash_to_rowid: dict[str, int] = {h: rid for rid, h, _ in existing_rows}
    existing_hash_to_row = {h: (rid, h, path) for rid, h, path in existing_rows}
    current_hash_to_item: dict[str, dict[str, Any]] = {it["content_hash"]: it for it in items}
    added_hashes = [h for h in current_hash_to_item if h not in existing_hash_to_rowid]
    removed_hashes = [h for h in existing_hash_to_rowid if h not in current_hash_to_item]
    pending_items = [current_hash_to_item[h] for h in added_hashes]
    removed_rows = [existing_hash_to_row[h] for h in removed_hashes]
    pending_chunks = sum(len(_chunks_for_item(current_hash_to_item[h])) for h in added_hashes)

    stats["reused"] = len(existing_hash_to_rowid) - len(removed_hashes)
    stats["added_sections"] = len(added_hashes)
    stats["removed_sections"] = len(removed_hashes)
    stats["pending_files"] = pending_files_for_items(pending_items)
    stats["removed_files"] = removed_files_for_rows(removed_rows)
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
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> tuple[Any, dict[str, Any]]:
    """Public index entrypoint. Write paths are serialised by a lock file.

    `dry_run=True` is strictly read-only: no directory creation, no schema
    creation, no meta writes. It is used by `status`.
    """
    if dry_run:
        include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
        exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
        conn = _open_index_metadata_readonly(corpus_root, cache_root=cache_root)
        stats = _index_delta_stats_readonly(
            conn,
            scope,
            items,
            embed_model,
            embedding_api_url,
            max_auto_embed,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
        return conn, stats

    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
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
            path_include=include_patterns,
            path_exclude=exclude_patterns,
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
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
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

    include_patterns = normalize_path_filter_patterns(path_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, corpus_root)
    items = apply_path_filters(items, include_patterns, exclude_patterns)

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
        "SELECT rowid, content_hash, relative_path FROM sections WHERE scope = ?",
        (scope,),
    ).fetchall()
    existing_rows = _filter_existing_rows_by_path(
        existing_rows,
        include_patterns,
        exclude_patterns,
    )
    existing_hash_to_rowid: dict[str, int] = {h: rid for rid, h, _ in existing_rows}
    current_hash_to_item: dict[str, dict[str, Any]] = {it["content_hash"]: it for it in items}

    added_hashes = [h for h in current_hash_to_item if h not in existing_hash_to_rowid]
    removed_hashes = [h for h in existing_hash_to_rowid if h not in current_hash_to_item]
    removed_rowids = [existing_hash_to_rowid[h] for h in removed_hashes]
    existing_hash_to_row = {h: (rid, h, path) for rid, h, path in existing_rows}
    pending_items = [current_hash_to_item[h] for h in added_hashes]
    removed_rows = [existing_hash_to_row[h] for h in removed_hashes]

    stats: dict[str, Any] = {
        "embedded": 0,
        "reused": len(existing_hash_to_rowid) - len(removed_hashes),
        "removed": 0,
        "added_sections": len(added_hashes),
        "removed_sections": len(removed_hashes),
        "pending_files": pending_files_for_items(pending_items),
        "removed_files": removed_files_for_rows(removed_rows),
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
                        lemmatize_text(chain_for_fts),
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
                    lemmatize_text(chain_for_fts),
                    lemmatize_text(item["body"]),
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
                _count_sections_in_path_scope(conn, scope, include_patterns, exclude_patterns)
            )
            return conn, stats

        if max_auto_embed is not None and len(plan) > max_auto_embed:
            stats["delta_too_large"] = True
            stats["total_sections_in_scope"] = int(
                _count_sections_in_path_scope(conn, scope, include_patterns, exclude_patterns)
            )
            return conn, stats

        # 5. Commit section + FTS rows up front. Chunks/vec are written
        #    batch-by-batch so interrupt is bounded. The interrupt heal
        #    pass at the top of the next run will sweep any sections left
        #    without chunks.
        conn.executemany(
            "INSERT INTO sections ("
            "rowid, section_id, scope, file_id, relative_path, start_line, "
            "level, heading_text, heading_chain, body, file_description, "
            "file_title, content_hash, token_count"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    f"    md index '{corpus_root}'\n"
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
        _count_sections_in_path_scope(conn, scope, include_patterns, exclude_patterns)
    )
    if not dry_run and scope == "sections":
        profiled = profile_unprofiled_sections(
            conn,
            corpus_root=corpus_root,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
        if profiled:
            stats["profiled_sections"] = profiled
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
    args.embed_model = resolve_embed_model_for_corpus(
        corpus_root, args.embed_model, cache_root=cache_root
    )

    totals = {"embedded": 0, "reused": 0, "removed": 0}
    include_patterns: list[str] = list(getattr(args, "path_include", None) or [])
    exclude_patterns: list[str] = list(getattr(args, "path_exclude", None) or [])
    if include_patterns or exclude_patterns:
        print(
            f"Path scope: include={include_patterns or '∅'} "
            f"exclude={exclude_patterns or '∅'}",
            file=sys.stderr,
        )
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
                path_include=include_patterns,
                path_exclude=exclude_patterns,
            )
        except ModuleNotFoundError as exc:
            print(
                f"Missing Python dependency: {exc}.\n"
                f"  This script needs uv to resolve its inline deps "
                f"(`numpy`, `sqlite-vec`, `pyyaml`).\n"
                f"  Verify the installed CLI with:\n"
                f"    md --version && md tools --json\n"
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
