from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from .embeddings import (
    _embed_texts_http,
    _vec_to_blob,
)
from .folder_map import build_map
from .index import ensure_index
from .sections import _should_subchunk, build_items_from_map


SEARCH_DEFAULT_LIMIT = 10
SEARCH_DEFAULT_CANDIDATES = 50
SEARCH_RRF_K = 60
SEARCH_DEFAULT_WEIGHTS = {"description": 5.0, "title": 4.0, "heading": 3.0, "body": 1.0}
SEARCH_DEFAULT_SCOPE = "sections"
SEARCH_SCOPES = ("sections", "descriptions")


def _fts5_query(query: str) -> str:
    """Build a safe FTS5 MATCH query: tokenize, quote each token, OR-join."""
    tokens = re.findall(r"\w+", query, re.UNICODE)
    if not tokens:
        return ""
    quoted = [f'"{t.lower()}"' for t in tokens]
    return " OR ".join(quoted)


def _search_bm25(
    conn,
    query: str,
    scope: str,
    weights: dict[str, float],
    candidates: int,
) -> list[tuple[int, float]]:
    """FTS5 match restricted to the current scope. The FTS table holds rows
    for both `sections` and `descriptions` scopes; the JOIN against
    `sections` filters down so a `--scope descriptions` query never ranks
    a heading-bounded section."""
    match_query = _fts5_query(query)
    if not match_query:
        return []
    sql = (
        "SELECT s.rowid, bm25(sections_fts, ?, ?, ?, ?) AS score "
        "FROM sections_fts JOIN sections AS s ON s.rowid = sections_fts.rowid "
        "WHERE sections_fts MATCH ? AND s.scope = ? "
        "ORDER BY score LIMIT ?"
    )
    try:
        rows = conn.execute(
            sql,
            (
                weights["description"],
                weights["title"],
                weights["heading"],
                weights["body"],
                match_query,
                scope,
                candidates,
            ),
        ).fetchall()
    except Exception as exc:
        print(f"BM25 query failed: {exc}", file=sys.stderr)
        return []
    return [(rowid, score) for (rowid, score) in rows]


def _search_dense(
    conn,
    model_name: str,
    query: str,
    scope: str,
    candidates: int,
    embedding_api_url: str,
    embedding_timeout: float,
    corpus_root: Path | None = None,
) -> list[tuple[int, float]]:
    """Dense KNN at chunk granularity, then dedupe to best chunk per section
    inside the requested scope. Over-fetches because many chunks belong to
    the same section and because we post-filter by scope."""
    q_vec_list = _embed_texts_http(
        model_name,
        [query],
        embedding_api_url,
        embedding_timeout,
        corpus_root=corpus_root,
    )
    if not q_vec_list:
        return []
    q_blob = _vec_to_blob(q_vec_list[0])
    over_fetch = max(candidates * 8, candidates + 100)
    try:
        rows = conn.execute(
            "SELECT s.rowid, vec.distance "
            "FROM sections_vec vec "
            "JOIN chunks ON chunks.chunk_id = vec.rowid "
            "JOIN sections AS s ON s.rowid = chunks.section_rowid "
            "WHERE vec.embedding MATCH ? AND vec.k = ? AND s.scope = ? "
            "ORDER BY vec.distance",
            (q_blob, over_fetch, scope),
        ).fetchall()
    except Exception as exc:
        print(f"Dense query failed: {exc}", file=sys.stderr)
        return []
    best_per_section: dict[int, float] = {}
    for section_rowid, distance in rows:
        d = float(distance)
        if section_rowid not in best_per_section or d < best_per_section[section_rowid]:
            best_per_section[section_rowid] = d
    sorted_pairs = sorted(best_per_section.items(), key=lambda x: x[1])
    return sorted_pairs[:candidates]


def _rrf_merge(
    bm25_results: list[tuple[int, float]],
    dense_results: list[tuple[int, float]],
    k: int = SEARCH_RRF_K,
) -> dict[int, float]:
    rrf: dict[int, float] = {}
    for rank, (rowid, _) in enumerate(bm25_results, start=1):
        rrf[rowid] = rrf.get(rowid, 0.0) + 1.0 / (k + rank)
    for rank, (rowid, _) in enumerate(dense_results, start=1):
        rrf[rowid] = rrf.get(rowid, 0.0) + 1.0 / (k + rank)
    return rrf


def _hydrate_rows(conn, rowids: list[int]) -> list[dict[str, Any]]:
    if not rowids:
        return []
    placeholders = ",".join("?" * len(rowids))
    rows = conn.execute(
        f"SELECT rowid, section_id, file_id, relative_path, start_line, level, "
        f"heading_text, heading_chain, body, file_description, file_title, "
        f"content_hash, token_count "
        f"FROM sections WHERE rowid IN ({placeholders})",
        rowids,
    ).fetchall()
    by_id = {
        r[0]: {
            "rowid": r[0],
            "section_id": r[1],
            "file_id": r[2],
            "relative_path": r[3],
            "start_line": r[4],
            "level": r[5],
            "heading_text": r[6],
            "heading_chain": r[7],
            "body": r[8],
            "file_description": r[9],
            "file_title": r[10],
            "content_hash": r[11],
            "token_count": r[12],
        }
        for r in rows
    }
    return [by_id[r] for r in rowids if r in by_id]


def _snippet_for(text: str, query: str, width: int = 200) -> str:
    if not text:
        return ""
    tokens = re.findall(r"\w+", query.lower(), re.UNICODE)
    text_lower = text.lower()
    pos = -1
    for tok in tokens:
        p = text_lower.find(tok)
        if p >= 0 and (pos < 0 or p < pos):
            pos = p
    if pos < 0:
        snippet = text[:width].replace("\n", " ")
        return snippet + ("..." if len(text) > width else "")
    start = max(0, pos - width // 3)
    end = min(len(text), start + width)
    snippet = text[start:end].replace("\n", " ")
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + snippet + suffix


def _fields_hit(conn, rowid: int, query: str) -> list[str]:
    tokens = [t.lower() for t in re.findall(r"\w+", query, re.UNICODE)]
    if not tokens:
        return []
    row = conn.execute(
        "SELECT file_description, file_title, heading_chain, heading_text, body "
        "FROM sections WHERE rowid = ?",
        (rowid,),
    ).fetchone()
    if not row:
        return []
    desc, title, chain, heading, body = (str(x).lower() for x in row)
    hits: list[str] = []
    if any(t in desc for t in tokens):
        hits.append("description")
    if any(t in title for t in tokens):
        hits.append("title")
    if any(t in chain or t in heading for t in tokens):
        hits.append("heading")
    if any(t in body for t in tokens):
        hits.append("body")
    return hits


def _sections_to_pick_map(
    corpus_root: Path,
    map_data: dict[str, Any],
    final_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a JSON map shaped exactly like build_map output, restricted to the
    files surfaced by search. Compatible with `pick --headings`."""
    file_ids_kept = {r["file_id"] for r in final_results}
    files_kept = [f for f in map_data["files"] if f["id"] in file_ids_kept]
    return {
        "root": map_data["root"],
        "file_count": len(files_kept),
        "description_gap_count": sum(1 for f in files_kept if not f["description"]),
        "heading_count": sum(f["heading_count"] for f in files_kept),
        "files": files_kept,
    }


def cmd_search(args) -> int:
    corpus_root = Path(args.path).expanduser().resolve()
    if not corpus_root.exists():
        print(f"Path does not exist: {corpus_root}", file=sys.stderr)
        return 2

    scope = getattr(args, "scope", SEARCH_DEFAULT_SCOPE)
    if scope not in SEARCH_SCOPES:
        print(
            f"Unknown --scope '{scope}'. Choices: {', '.join(SEARCH_SCOPES)}",
            file=sys.stderr,
        )
        return 2

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=True)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1

    items = build_items_from_map(map_data, scope=scope)
    if not items:
        gap = "no frontmatter descriptions" if scope == "descriptions" else "no sections"
        print(f"No items to index under {corpus_root} ({gap})", file=sys.stderr)
        return 1

    cache_root = Path(args.cache_dir).expanduser() if args.cache_dir else None

    if args.no_cache:
        # User explicitly asked to recompute. Wipe the on-disk index file for
        # this corpus so `ensure_index` builds from scratch.
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
            scope,
            items,
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
            f"(`sqlite-vec`, `pyyaml`).\n"
            f"  Run it via the uv shebang:\n"
            f"    chmod +x md_navigator.py && ./md_navigator.py search ...\n"
            f"  Or explicitly:\n"
            f"    uv run --script md_navigator.py search ...\n"
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
        cap = max_auto_embed
        print(
            f"Index needs warmup before search can run.\n"
            f"  {added} new sections / {pending} new chunks pending "
            f"(cap for auto-embed in `search` = {cap}).\n"
            f"\n"
            f"  Next step:\n"
            f"    md_navigator.py index '{corpus_root}'\n"
            f"\n"
            f"  Then re-run your search. One-time cost; subsequent searches "
            f"reuse the index on disk.\n"
            f"  Requires OPENROUTER_API_KEY env var or `.openrouter.key` file "
            f"(see SKILL.md → First-time setup).",
            file=sys.stderr,
        )
        return 4

    embedded_count = index_stats["embedded"]
    cached_count = index_stats["reused"]
    removed_count = index_stats["removed_sections"]

    # For descriptions scope, only description column carries content; collapse
    # the other field weights so BM25 ranks on the right signal.
    if scope == "descriptions":
        weights = {"description": 5.0, "title": 0.0, "heading": 0.0, "body": 1.0}
    else:
        weights = dict(SEARCH_DEFAULT_WEIGHTS)
    bm25_results = _search_bm25(conn, args.query, scope, weights, args.candidates)

    try:
        dense_results = _search_dense(
            conn,
            args.embed_model,
            args.query,
            scope,
            args.candidates,
            args.embedding_api_url,
            args.embedding_timeout,
            corpus_root=corpus_root,
        )
    except RuntimeError as exc:
        print(f"Dense query failed: {exc}", file=sys.stderr)
        return 3

    rrf_scores = _rrf_merge(bm25_results, dense_results, k=SEARCH_RRF_K)
    fused_sorted = sorted(rrf_scores.items(), key=lambda x: -x[1])
    fused_rowids = [rid for rid, _ in fused_sorted[: args.candidates]]
    final_results = _hydrate_rows(conn, fused_rowids)[: args.limit]

    bm25_map = dict(bm25_results)
    dense_map = dict(dense_results)
    for r in final_results:
        rid = r["rowid"]
        r["bm25_score"] = bm25_map.get(rid)
        r["dense_distance"] = dense_map.get(rid)
        r["rrf_score"] = rrf_scores.get(rid, 0.0)
        r["fields_hit"] = _fields_hit(conn, rid, args.query)
        r["snippet"] = _snippet_for(r["body"], args.query)

    subchunked_count = sum(
        1 for s in items if scope == "sections" and _should_subchunk(s["body"] or "")
    )

    output = {
        "root": str(corpus_root),
        "query": args.query,
        "scope": scope,
        "engine": {
            "bm25f": True,
            "dense": True,
            "embed_model": args.embed_model,
            "embedding_api_url": args.embedding_api_url,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "items_indexed": len(items),
            "sections_subchunked": subchunked_count,
            "embeddings_cached": cached_count,
            "embeddings_computed": embedded_count,
            "sections_removed": removed_count,
            "bm25_hits": len(bm25_results),
            "dense_hits": len(dense_results),
        },
        "weights": weights,
        "results": final_results,
    }

    if args.output and scope == "sections":
        pick_map = _sections_to_pick_map(corpus_root, map_data, final_results)
        Path(args.output).write_text(
            json.dumps(pick_map, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    else:
        print(render_search(output, output_path=args.output), end="")
    return 0


def _script_invocation_path() -> str:
    """Return the path the user invoked us with — so output hand-off commands
    look natural whether called via the Claude or Codex skill symlink."""
    p = sys.argv[0] if sys.argv and sys.argv[0] else __file__
    try:
        return str(Path(p).expanduser())
    except Exception:
        return p


def render_search(out: dict[str, Any], output_path: str | None = None) -> str:
    eng = out["engine"]
    stats = out["stats"]
    scope = out.get("scope", SEARCH_DEFAULT_SCOPE)
    engine_parts = ["FTS5 BM25F"]
    if eng.get("dense"):
        engine_parts.append(f"dense ({eng['embed_model']})")
    unit_word = "descriptions" if scope == "descriptions" else "sections"
    subchunk_note = ""
    if scope == "sections" and stats.get("sections_subchunked"):
        subchunk_note = f" ({stats['sections_subchunked']} sub-chunked)"
    me = _script_invocation_path()
    lines = [
        f"# Markdown search: {out['query']}",
        "",
        f"Root: {out['root']}",
        f"Scope: {scope}",
        f"Engine: {' + '.join(engine_parts)}",
        f"Indexed: {stats['files_indexed']} files / {stats['items_indexed']} {unit_word}{subchunk_note} "
        f"| reused: {stats['embeddings_cached']} | computed: {stats['embeddings_computed']}"
        f"{' | pruned: ' + str(stats['sections_removed']) if stats.get('sections_removed') else ''}",
        "Reading router: ranked items, not exhaustive proof.",
        "",
    ]
    if scope == "descriptions":
        lines.append("## Files (ranked by description)")
    else:
        lines.append("## Sections (ranked)")
    if not out["results"]:
        lines.append("(no results)")
        lines.append("")
    for i, r in enumerate(out["results"], start=1):
        chain = r["heading_chain"]
        if scope == "descriptions":
            heading_str = "(frontmatter description)"
        elif not chain:
            heading_str = "(file, no heading)"
        else:
            heading_str = f"## {chain}"
        scores = []
        if r.get("bm25_score") is not None:
            scores.append(f"BM25: {r['bm25_score']:.2f}")
        if r.get("dense_distance") is not None:
            scores.append(f"Dense: {r['dense_distance']:.3f}")
        scores.append(f"RRF: {r['rrf_score']:.4f}")
        fields = ",".join(r["fields_hit"]) or "(graph-only)"
        lines.append(
            f"{i}. [{r['section_id']}] {r['relative_path']}:L{r['start_line']} {heading_str}"
        )
        lines.append(f"   Fields hit: {fields} | {' | '.join(scores)} | ~{r['token_count']}t")
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        lines.append("")
    lines.append("## Hand off")
    lines.append("- Exact strings / regex / code symbols → Grep / `1cli-tools` rg")
    lines.append("- What breaks if I edit this → `1md-graph preflight <file>`")
    if scope == "descriptions":
        lines.append(
            "- Drill down into specific sections of a file → "
            "`headings <path> --output /tmp/md-map.json`, then `pick --files <file_id>`"
        )
    lines.append("")
    if out["results"]:
        if scope == "descriptions":
            file_ids = ",".join(str(r["file_id"]) for r in out["results"])
            lines.append("Command (drill down into the selected files):")
            lines.append(f"  {me} headings '{out['root']}' --output /tmp/md-map.json")
            lines.append(f"  {me} pick /tmp/md-map.json --files {file_ids}")
        else:
            ids = ",".join(r["section_id"] for r in out["results"])
            if output_path:
                lines.append("Command (read sections via pick):")
                lines.append(f"  {me} pick {output_path} --headings {ids} --extract")
            else:
                lines.append("Command (read sections via pick — save the map first):")
                lines.append(f"  {me} headings '{out['root']}' --output /tmp/md-map.json")
                lines.append(f"  {me} pick /tmp/md-map.json --headings {ids} --extract")
    return "\n".join(lines).rstrip() + "\n"
