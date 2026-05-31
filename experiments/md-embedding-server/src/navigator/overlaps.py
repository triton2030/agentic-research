from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .filters import (
    apply_path_filters_to_map,
    normalize_path_filter_patterns,
    path_matches_any,
    sqlite_path_filter_sql,
)
from .folder_map import build_map
from .index import ensure_index, resolve_embed_model_for_corpus
from navigator.index_guidance import (
    index_confirm_command,
    index_dry_run_command,
    scoped_rerun_command,
)
from .index_meta import (
    _index_dir_for_corpus,
    find_parent_indexed_corpus,
    path_include_for_parent_corpus,
)
from .sections import build_sections_from_map


def compute_overlaps(
    corpus_root: Path,
    conn,
    map_data: dict[str, Any],
    index_stats: dict[str, Any],
    args,
) -> dict[str, Any] | None:
    """Pure compute over an already-open index. Builds the section-pair
    overlap output dict so audit and the public `overlaps` API share one
    compute path. The
    caller is responsible for `ensure_index`, error handling, the
    `delta_too_large` warmup signal, and output routing.

    Returns the output dict, or `None` when fewer than 2 chunks are
    available to compare."""
    embedded_count = index_stats["embedded"]
    cached_count = index_stats["reused"]

    import numpy as np  # type: ignore
    path_include: list[str] = normalize_path_filter_patterns(
        getattr(args, "path_include", None),
        corpus_root,
    )
    path_exclude: list[str] = normalize_path_filter_patterns(
        getattr(args, "path_exclude", None),
        corpus_root,
    )
    path_clause, path_params = sqlite_path_filter_sql(
        "s.relative_path",
        path_include,
        path_exclude,
    )

    # Chunk-level fetch: vec table is keyed by chunk_id (one row per sub-chunk
    # of a section). Join through chunks to attach parent section metadata,
    # filter to the sections scope, then aggregate chunk-pair similarities to
    # section-pair best similarity (max across sub-chunks of A vs B).
    rows = conn.execute(
        "SELECT chunks.chunk_id, chunks.section_rowid, chunks.chunk_idx, "
        "s.section_id, s.file_id, s.relative_path, "
        "s.start_line, s.heading_text, s.heading_chain, "
        "s.token_count, vec.embedding "
        "FROM chunks "
        "JOIN sections_vec vec ON vec.rowid = chunks.chunk_id "
        "JOIN sections AS s ON s.rowid = chunks.section_rowid "
        "WHERE s.scope = 'sections' "
        f"{path_clause} "
        "ORDER BY chunks.chunk_id",
        path_params,
    ).fetchall()

    m = len(rows)
    if m < 2:
        return None

    threshold = float(args.threshold)
    min_tokens = int(args.min_tokens)
    include_same_file = bool(args.include_same_file)
    def _path_ok(rel: str) -> bool:
        if path_include and not path_matches_any(rel, path_include):
            return False
        if path_exclude and path_matches_any(rel, path_exclude):
            return False
        return True

    chunk_section = np.array([r[1] for r in rows], dtype=np.int64)
    section_meta: dict[int, dict[str, Any]] = {}
    for r in rows:
        sec_rowid = r[1]
        if sec_rowid not in section_meta:
            section_meta[sec_rowid] = {
                "section_id": r[3],
                "file_id": r[4],
                "relative_path": r[5],
                "start_line": r[6],
                "heading_text": r[7],
                "heading_chain": r[8],
                "token_count": r[9],
            }

    # Vectors are L2-normalized inside _embed_texts, so dot product == cosine.
    vecs = np.stack([np.frombuffer(r[10], dtype="float32") for r in rows])
    sim = vecs @ vecs.T

    # Pre-filter to above-threshold upper-triangle pairs.
    sim_upper = np.triu(sim, k=1)
    high_pairs = np.argwhere(sim_upper >= threshold)

    section_pair_best: dict[tuple[int, int], float] = {}
    for i, j in high_pairs:
        sec_a = int(chunk_section[i])
        sec_b = int(chunk_section[j])
        if sec_a == sec_b:
            continue  # different sub-chunks of the same section
        a_meta = section_meta[sec_a]
        b_meta = section_meta[sec_b]
        if a_meta["token_count"] < min_tokens or b_meta["token_count"] < min_tokens:
            continue
        if not include_same_file and a_meta["relative_path"] == b_meta["relative_path"]:
            continue
        # Path filters: drop pair if either side fails include/exclude.
        if not _path_ok(a_meta["relative_path"]) or not _path_ok(b_meta["relative_path"]):
            continue
        key = (sec_a, sec_b) if sec_a < sec_b else (sec_b, sec_a)
        s = float(sim[i, j])
        if key not in section_pair_best or s > section_pair_best[key]:
            section_pair_best[key] = s

    sorted_pairs = sorted(section_pair_best.items(), key=lambda x: -x[1])
    sorted_pairs = sorted_pairs[: int(args.top)]

    items_out = []
    for (sec_a, sec_b), s in sorted_pairs:
        items_out.append(
            {
                "similarity": s,
                "a": section_meta[sec_a],
                "b": section_meta[sec_b],
            }
        )

    eligible_section_count = sum(
        1 for meta in section_meta.values() if meta["token_count"] >= min_tokens
    )

    output = {
        "root": str(corpus_root),
        "threshold": threshold,
        "include_same_file": include_same_file,
        "min_tokens": min_tokens,
        "engine": {
            "embed_model": args.embed_model,
            "embedding_api_url": args.embedding_api_url,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "sections_indexed": len(section_meta),
            "sections_eligible": eligible_section_count,
            "chunks_compared": m,
            "embeddings_cached": cached_count,
            "embeddings_computed": embedded_count,
            "pairs_above_threshold": len(items_out),
        },
        "pairs": items_out,
    }

    return output


def render_overlaps(out: dict[str, Any]) -> str:
    stats = out["stats"]
    eng = out["engine"]
    lines = [
        f"# Markdown overlaps: {out['root']}",
        "",
        f"Engine: dense similarity ({eng['embed_model']})",
        f"Indexed: {stats['files_indexed']} files / {stats['sections_indexed']} sections "
        f"({stats['sections_eligible']} eligible, {stats.get('chunks_compared', stats['sections_indexed'])} chunks) "
        f"| cached: {stats['embeddings_cached']} | computed: {stats['embeddings_computed']}",
        f"Threshold: {out['threshold']} | min tokens: {out['min_tokens']} | "
        f"include same file: {out['include_same_file']}",
        f"Pairs surfaced: {stats['pairs_above_threshold']}",
        "",
        "## Overlapping section pairs (ranked by cosine similarity)",
    ]
    if not out["pairs"]:
        lines.append("(no pairs above threshold — try lowering --threshold or --min-tokens)")
        lines.append("")
    for i, p in enumerate(out["pairs"], start=1):
        a, b = p["a"], p["b"]
        a_chain = a["heading_chain"] if a["heading_chain"] else "(file)"
        b_chain = b["heading_chain"] if b["heading_chain"] else "(file)"
        lines.append(f"{i}. sim={p['similarity']:.3f}")
        lines.append(
            f"   A: [{a['section_id']}] {a['relative_path']}:L{a['start_line']} "
            f"## {a_chain} (~{a['token_count']}t)"
        )
        lines.append(
            f"   B: [{b['section_id']}] {b['relative_path']}:L{b['start_line']} "
            f"## {b_chain} (~{b['token_count']}t)"
        )
        lines.append("")
    lines.append("## Hand off")
    lines.append(
        "- Confirmed smell → `1ia-audit` (owner truth / function split / smeared information)"
    )
    lines.append("- Before merge / move / rename → `1md-graph impact <file>`")
    lines.append(
        "- Read either section inline → `pick --headings <id> --extract` "
        "after `headings` on the same root"
    )
    return "\n".join(lines).rstrip() + "\n"
