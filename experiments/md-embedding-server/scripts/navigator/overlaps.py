from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .folder_map import build_map
from .index import ensure_index
from .sections import build_sections_from_map


def cmd_overlaps(args) -> int:
    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=False)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1

    sections = build_sections_from_map(map_data)
    if not sections:
        print(f"No sections extracted from {corpus_root}", file=sys.stderr)
        return 1

    cache_root = Path(args.cache_dir).expanduser() if args.cache_dir else None
    if args.no_cache:
        from .index import _index_dir_for_corpus

        target = _index_dir_for_corpus(corpus_root, cache_root=cache_root)
        for name in ("index.sqlite", "index.sqlite-wal", "index.sqlite-shm"):
            (target / name).unlink(missing_ok=True)

    max_auto_embed = (
        None if args.max_auto_embed == 0 else int(args.max_auto_embed)
    )

    try:
        conn, index_stats = ensure_index(
            corpus_root,
            "sections",
            sections,
            args.embed_model,
            embedding_api_url=args.embedding_api_url,
            embedding_timeout=args.embedding_timeout,
            cache_root=cache_root,
            max_auto_embed=max_auto_embed,
        )
    except ModuleNotFoundError as exc:
        print(
            f"Missing Python dependency: {exc}.\n"
            f"  This script needs uv to resolve its inline deps "
            f"(`numpy`, `sqlite-vec`, `pyyaml`).\n"
            f"  Run it via the uv shebang:\n"
            f"    chmod +x md_navigator.py && ./md_navigator.py overlaps ...\n"
            f"  Or explicitly:\n"
            f"    uv run --script md_navigator.py overlaps ...\n"
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

    if index_stats.get("delta_too_large"):
        pending = index_stats["pending_chunks"]
        added = index_stats["added_sections"]
        print(
            f"Index needs warmup before overlaps can run.\n"
            f"  {added} new sections / {pending} new chunks pending "
            f"(cap for auto-embed in `overlaps` = {max_auto_embed}).\n"
            f"\n"
            f"  Next step:\n"
            f"    md_navigator.py index '{corpus_root}'\n"
            f"\n"
            f"  Then re-run overlaps. One-time cost; subsequent runs reuse "
            f"the index on disk.\n"
            f"  Requires OPENROUTER_API_KEY env var or `.openrouter.key` file "
            f"(see SKILL.md → First-time setup).",
            file=sys.stderr,
        )
        return 4

    embedded_count = index_stats["embedded"]
    cached_count = index_stats["reused"]

    import numpy as np  # type: ignore

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
        "ORDER BY chunks.chunk_id"
    ).fetchall()

    m = len(rows)
    if m < 2:
        print("Need at least 2 chunks to compare.", file=sys.stderr)
        return 1

    threshold = float(args.threshold)
    min_tokens = int(args.min_tokens)
    include_same_file = bool(args.include_same_file)

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

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    else:
        print(render_overlaps(output), end="")
    return 0


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
