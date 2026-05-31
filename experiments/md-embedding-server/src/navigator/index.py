"""Façade module for the index layer.

The implementation lives in focused modules; this file re-exports their
public symbols so existing callers (`search.py`, `overlaps.py`,
`repeated_concepts.py`) keep working with no edits:

  - `index_meta`   — schema, meta, layout, open / probe / sticky model
  - `index_build`  — counters, delta apply, embed pipeline
  - `status_core`  — shared status state machine and corpus root discovery
  - `index_cluster` — K-means clustering primitives, `cluster_sections`

In addition, two semantic-neighbour utilities live here because they
are used only by `related.py` (read-related feature) and don't fit
cluster / status / build cleanly: `find_semantic_neighbors` and
`check_explicit_link_coherence`.

New code should prefer importing directly from the focused modules.
This shim exists only for backward compatibility."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

# --- Backwards-compat re-exports ----------------------------------------

from .index_meta import (  # noqa: F401
    GITIGNORE_BANNER,
    INDEX_DIRNAME,
    SCHEMA_VERSION,
    SEARCH_CACHE_ROOT,
    _acquire_index_write_lock,
    _cache_dir_for_root,
    _create_schema,
    _index_dir_for_corpus,
    _meta_get,
    _meta_set,
    _open_index,
    _open_index_metadata_readonly,
    _open_index_readonly,
    _release_index_write_lock,
    probe_embedding_dim,
    resolve_embed_model_for_corpus,
)
from .index_build import (  # noqa: F401
    DEFAULT_INDEX_BATCH,
    DEFAULT_INDEX_PAUSE_S,
    DEFAULT_MAX_AUTO_EMBED,
    _chunks_for_item,
    _clean_incomplete_sections,
    _delete_section_rowids,
    _ensure_index_unlocked,
    _index_delta_stats_readonly,
    _next_id,
    _set_counter,
    ensure_index,
)
from .status_core import find_corpus_root_for  # noqa: F401
from .index_cluster import (  # noqa: F401
    _kmeans,
    _kmeans_pp_init,
    _longest_common_parent,
    cluster_sections,
)


# --- Semantic neighbour utilities (read-only, used by related.py) -------


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
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError, sqlite3.Error):
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
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError, sqlite3.Error):
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
