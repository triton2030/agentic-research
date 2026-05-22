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
from .cli_common import (
    add_auto_embed_args,
    add_cache_arg,
    add_embedding_args,
    add_json_arg,
    add_max_heading_level_arg,
)
from .filters import (
    add_path_filter_args,
    apply_path_filters_to_map,
    apply_path_filters as _apply_path_filters,
    normalize_path_filter_patterns,
    path_matches_any as _path_matches_any,
    sqlite_path_filter_sql,
)
from .folder_map import build_map
from .index import ensure_index, resolve_embed_model_for_corpus
from .lemmatize import lemmatize_text, lemmatize_token
from .rerank import (
    DEFAULT_RERANK_API_URL,
    DEFAULT_RERANK_MODEL,
    DEFAULT_RERANK_TIMEOUT,
    DEFAULT_RERANK_TOP_N,
    doc_text_for_rerank,
    rerank_documents,
)
from .sections import _should_subchunk, build_items_from_map


SEARCH_DEFAULT_LIMIT = 10
SEARCH_DEFAULT_CANDIDATES = 50
SEARCH_RRF_K = 60
SEARCH_DEFAULT_WEIGHTS = {"description": 5.0, "title": 4.0, "heading": 3.0, "body": 1.0}
SEARCH_DEFAULT_SCOPE = "sections"
SEARCH_SCOPES = ("sections", "descriptions")
# Default cap on inline embedding work during read-path commands. Mirrors
# index_build.DEFAULT_MAX_AUTO_EMBED but kept local to avoid a back-import.
_DEFAULT_MAX_AUTO_EMBED = 50


def register_search(sub) -> None:
    """Register the `search` subcommand on the parser-level subparsers
    object. Owns its own argparse so cli.py can stay thin."""
    p = sub.add_parser(
        "search",
        help=(
            "Hybrid section search: BM25F (lemmatized) + dense fusion via "
            "RRF, optional cross-encoder rerank. Outputs ranked Markdown "
            "sections, not line matches."
        ),
    )
    p.add_argument("path", help="Folder or Markdown file to search.")
    p.add_argument("query", help="Search query (natural language or keywords).")
    add_max_heading_level_arg(p)
    p.add_argument(
        "--scope",
        default=SEARCH_DEFAULT_SCOPE,
        choices=SEARCH_SCOPES,
        help=(
            f"What to rank (default: {SEARCH_DEFAULT_SCOPE}). `sections` ranks "
            "heading-bounded sections; `descriptions` ranks files by their "
            "frontmatter `description`."
        ),
    )
    p.add_argument(
        "--limit",
        type=int,
        default=SEARCH_DEFAULT_LIMIT,
        help=f"How many results to print (default: {SEARCH_DEFAULT_LIMIT}).",
    )
    p.add_argument(
        "--candidates",
        type=int,
        default=SEARCH_DEFAULT_CANDIDATES,
        help=(
            f"How many fused candidates to consider before trimming to "
            f"--limit (default: {SEARCH_DEFAULT_CANDIDATES})."
        ),
    )
    add_embedding_args(p)
    add_cache_arg(p)
    add_auto_embed_args(p, default_cap=_DEFAULT_MAX_AUTO_EMBED)
    p.add_argument(
        "--output",
        help="Write the section map (compatible with pick) to this JSON file.",
    )
    add_json_arg(p)
    p.add_argument(
        "--rerank",
        action="store_true",
        help=(
            "Apply cross-encoder rerank to top-N RRF candidates before "
            "limiting. Lifts top-1 precision on business docs by ~10-15%%. "
            "Reuses OPENROUTER_API_KEY (or `.openrouter.key` file)."
        ),
    )
    p.add_argument(
        "--rerank-model",
        default=DEFAULT_RERANK_MODEL,
        help=f"Rerank model id (default: {DEFAULT_RERANK_MODEL}).",
    )
    p.add_argument(
        "--rerank-api-url",
        default=DEFAULT_RERANK_API_URL,
        help=f"Cohere-compatible rerank endpoint (default: {DEFAULT_RERANK_API_URL}).",
    )
    p.add_argument(
        "--rerank-timeout",
        type=float,
        default=DEFAULT_RERANK_TIMEOUT,
        help=f"Rerank API timeout in seconds (default: {DEFAULT_RERANK_TIMEOUT}).",
    )
    p.add_argument(
        "--rerank-top-n",
        type=int,
        default=DEFAULT_RERANK_TOP_N,
        help=(
            f"How many RRF candidates to send for cross-encoder rerank "
            f"(default: {DEFAULT_RERANK_TOP_N}). Latency scales with N."
        ),
    )
    add_path_filter_args(p, command_name="search")
    p.set_defaults(func=lambda args: cmd_search(args))


def _fts5_query(query: str) -> str:
    """Build a safe FTS5 MATCH query: tokenize, lemmatize Russian, quote
    each token, OR-join. Stored body/heading_chain were lemmatized at
    index time, so query tokens must travel through the same normalizer
    or BM25 will never connect inflected forms."""
    tokens = re.findall(r"\w+", query, re.UNICODE)
    if not tokens:
        return ""
    quoted = [f'"{lemmatize_token(t.lower())}"' for t in tokens]
    return " OR ".join(quoted)


def _search_bm25(
    conn,
    query: str,
    scope: str,
    weights: dict[str, float],
    candidates: int,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> list[tuple[int, float]]:
    """FTS5 match restricted to the current scope. The FTS table holds rows
    for both `sections` and `descriptions` scopes; the JOIN against
    `sections` filters down so a `--scope descriptions` query never ranks
    a heading-bounded section."""
    match_query = _fts5_query(query)
    if not match_query:
        return []
    path_clause, path_params = sqlite_path_filter_sql(
        "s.relative_path",
        list(path_include or []),
        list(path_exclude or []),
    )
    sql = (
        "SELECT s.rowid, bm25(sections_fts, ?, ?, ?, ?) AS score "
        "FROM sections_fts JOIN sections AS s ON s.rowid = sections_fts.rowid "
        "WHERE sections_fts MATCH ? AND s.scope = ? "
        f"{path_clause} "
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
                *path_params,
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
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
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
    path_clause, path_params = sqlite_path_filter_sql(
        "s.relative_path",
        list(path_include or []),
        list(path_exclude or []),
    )
    try:
        rows = conn.execute(
            "SELECT s.rowid, vec.distance "
            "FROM sections_vec vec "
            "JOIN chunks ON chunks.chunk_id = vec.rowid "
            "JOIN sections AS s ON s.rowid = chunks.section_rowid "
            "WHERE vec.embedding MATCH ? AND vec.k = ? AND s.scope = ? "
            f"{path_clause} "
            "ORDER BY vec.distance",
            (q_blob, over_fetch, scope, *path_params),
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
        start, end = 0, min(len(text), width)
    else:
        start = max(0, pos - width // 3)
        end = min(len(text), start + width)
    if start > 0:
        m = re.search(r"\s", text[start : start + 30])
        if m:
            start = start + m.start() + 1
    if end < len(text):
        m = re.search(r"\s", text[end : end + 30])
        if m:
            end = end + m.start()
    snippet = text[start:end].replace("\n", " ").strip()
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + snippet + suffix


def _fields_hit(conn, rowid: int, query: str) -> list[str]:
    """Annotate which surface(s) of the row carry the query.

    Both sides go through lemmatization so a query like `критериев` hits a
    section that literally stores `критерии`. Description/title are also
    lemmatized for symmetry — frontmatter description is often Russian
    prose and benefits from the same normalization."""
    raw_tokens = [t.lower() for t in re.findall(r"\w+", query, re.UNICODE)]
    if not raw_tokens:
        return []
    tokens = [lemmatize_token(t) for t in raw_tokens]
    row = conn.execute(
        "SELECT file_description, file_title, heading_chain, heading_text, body "
        "FROM sections WHERE rowid = ?",
        (rowid,),
    ).fetchone()
    if not row:
        return []
    desc, title, chain, heading, body = (lemmatize_text(str(x).lower()) for x in row)
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
    files surfaced by search. Compatible with `pick --headings`.

    Filters by `relative_path` (stable) rather than `file_id` (positional from
    `iter_markdown` order). file_id alignment between index and a fresh map
    is enforced by the remap step in cmd_search; this path-based filter is
    defense in depth in case that remap is bypassed or regresses."""
    paths_kept = {r["relative_path"] for r in final_results}
    files_kept = [f for f in map_data["files"] if f["relative_path"] in paths_kept]
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

    include_patterns = normalize_path_filter_patterns(
        getattr(args, "path_include", None),
        corpus_root,
    )
    exclude_patterns = normalize_path_filter_patterns(
        getattr(args, "path_exclude", None),
        corpus_root,
    )

    map_data = build_map(corpus_root, args.max_heading_level, with_tokens=True)
    if not map_data["files"]:
        print(f"No Markdown files under {corpus_root}", file=sys.stderr)
        return 1

    scoped_map_data = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    if not scoped_map_data["files"]:
        print(
            f"Path filters matched no Markdown files under {corpus_root}",
            file=sys.stderr,
        )
        return 1

    items = build_items_from_map(scoped_map_data, scope=scope)
    if not items:
        gap = "no frontmatter descriptions" if scope == "descriptions" else "no sections"
        print(f"No items to index under selected path scope ({gap})", file=sys.stderr)
        return 1

    cache_root = Path(args.cache_dir).expanduser() if args.cache_dir else None
    args.embed_model = resolve_embed_model_for_corpus(
        corpus_root, args.embed_model, cache_root=cache_root
    )

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
            f"    md index '{corpus_root}'\n"
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
    bm25_results = _search_bm25(
        conn,
        args.query,
        scope,
        weights,
        args.candidates,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )

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
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
    except RuntimeError as exc:
        print(f"Dense query failed: {exc}", file=sys.stderr)
        return 3

    rrf_scores = _rrf_merge(bm25_results, dense_results, k=SEARCH_RRF_K)
    fused_sorted = sorted(rrf_scores.items(), key=lambda x: -x[1])
    fused_rowids = [rid for rid, _ in fused_sorted[: args.candidates]]
    # If `--rerank` is set, hydrate more candidates than the final limit so
    # the cross-encoder has a real reordering pool. Path filters might
    # also drop candidates, so hydrate from the full fused pool before
    # filtering — we don't know which paths will pass until we look.
    rerank_on = bool(getattr(args, "rerank", False))
    filter_on = bool(include_patterns or exclude_patterns)
    if rerank_on or filter_on:
        # Pull the whole candidates pool — filters / rerank shrink it.
        hydrate_n = len(fused_rowids)
    else:
        hydrate_n = args.limit
    hydrated = _hydrate_rows(conn, fused_rowids)[:hydrate_n]

    # Apply path filters BEFORE rerank so the cross-encoder budget isn't
    # spent on candidates the user is going to drop anyway.
    if filter_on:
        before = len(hydrated)
        hydrated = _apply_path_filters(hydrated, include_patterns, exclude_patterns)
        if not hydrated:
            print(
                f"Path filters excluded all {before} candidates "
                f"(include={include_patterns or '∅'}, exclude={exclude_patterns or '∅'}).",
                file=sys.stderr,
            )
    if rerank_on:
        # After filter; cap to rerank_top_n.
        hydrated = hydrated[: getattr(args, "rerank_top_n", args.limit)]
    else:
        hydrated = hydrated[: args.limit]

    rerank_scores: dict[int, float] = {}
    rerank_applied = False
    if rerank_on and hydrated:
        docs = [
            doc_text_for_rerank(r["relative_path"], r["heading_chain"], r["body"])
            for r in hydrated
        ]
        try:
            ordered = rerank_documents(
                args.query,
                docs,
                model=args.rerank_model,
                api_url=args.rerank_api_url,
                timeout=args.rerank_timeout,
                corpus_root=corpus_root,
            )
        except RuntimeError as exc:
            print(
                f"Rerank failed: {exc}\n  Falling back to RRF order.",
                file=sys.stderr,
            )
            ordered = []
        if ordered:
            new_order: list[dict[str, Any]] = []
            for idx, score in ordered:
                if 0 <= idx < len(hydrated):
                    r = hydrated[idx]
                    rerank_scores[r["rowid"]] = score
                    new_order.append(r)
            if new_order:
                hydrated = new_order
                rerank_applied = True

    # Final trim to user's requested limit (rerank may have reordered).
    hydrated = hydrated[: args.limit]

    # Remap hydrated rows from index-time positional ids to fresh map ids.
    # file_id is positional from `iter_markdown` order at index time; corpus
    # reorders since then drift it away from a fresh build_map. Downstream
    # `pick` resolves against a fresh map, so we must hand it fresh ids.
    #
    # section_id has shape "<file_id>.<suffix>" where suffix is heading_idx,
    # "0" (no-headings file), or "desc". The suffix is stable for surviving
    # rows: _section_hash(rel, start_line, body) is the diff key, so any
    # within-file reshuffle (heading add/remove, line shift) rewrites the
    # hash and reindexes the row. Surviving rows match their fresh-map
    # counterpart at the same heading_idx; we rebuild the full id with the
    # fresh prefix and keep the original suffix.
    fresh_file_id_by_path = {f["relative_path"]: f["id"] for f in map_data["files"]}

    final_results: list[dict[str, Any]] = []
    dropped_stale_path = 0
    for r in hydrated:
        path = r["relative_path"]
        fresh_fid = fresh_file_id_by_path.get(path)
        if fresh_fid is None:
            dropped_stale_path += 1
            continue
        r["file_id"] = fresh_fid
        old_sid = str(r.get("section_id") or "")
        if "." in old_sid:
            suffix = old_sid.split(".", 1)[1]
            r["section_id"] = f"{fresh_fid}.{suffix}"
        else:
            r["section_id"] = str(fresh_fid)
        final_results.append(r)

    bm25_map = dict(bm25_results)
    dense_map = dict(dense_results)
    for r in final_results:
        rid = r["rowid"]
        r["bm25_score"] = bm25_map.get(rid)
        r["dense_distance"] = dense_map.get(rid)
        r["rrf_score"] = rrf_scores.get(rid, 0.0)
        r["rerank_score"] = rerank_scores.get(rid)
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
            "rerank": rerank_applied,
            "rerank_model": getattr(args, "rerank_model", None) if rerank_applied else None,
            "rerank_top_n": getattr(args, "rerank_top_n", None) if rerank_applied else None,
            "rerank_api_url": getattr(args, "rerank_api_url", None) if rerank_applied else None,
            "path_include": include_patterns,
            "path_exclude": exclude_patterns,
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
            "dropped_stale_path": dropped_stale_path,
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


def _signal_label(r: dict[str, Any]) -> str:
    """Channel diagnosis for one result. Surfaces `Dense only` explicitly —
    on this corpus it almost always means BM25 failed on Russian morphology
    (unicode61 tokenizer does not stem). Rerank tag is added separately
    in render_search to keep this label compact."""
    fields_hit = r.get("fields_hit") or []
    has_bm25 = r.get("bm25_score") is not None
    has_dense = r.get("dense_distance") is not None
    if fields_hit and has_dense:
        return f"BM25+Dense ({','.join(fields_hit)})"
    if fields_hit and has_bm25:
        return f"BM25 only ({','.join(fields_hit)})"
    if has_dense:
        return "Dense only ⚠ morphology miss likely"
    return "graph-only"


def _top_lead(results: list[dict[str, Any]]) -> bool:
    """True when #1 RRF dominates #2 by >25%. Promotes a single-hit `read`
    over the multi-section `pick` chain when the leader is clear."""
    if len(results) < 2:
        return bool(results)
    top = results[0].get("rrf_score", 0) or 0
    nxt = results[1].get("rrf_score", 0) or 0
    if nxt <= 0:
        return top > 0
    return (top - nxt) / nxt > 0.25


def render_search(out: dict[str, Any], output_path: str | None = None) -> str:
    stats = out["stats"]
    eng = out.get("engine") or {}
    scope = out.get("scope", SEARCH_DEFAULT_SCOPE)
    unit_word = "descriptions" if scope == "descriptions" else "sections"
    subchunk_note = ""
    if scope == "sections" and stats.get("sections_subchunked"):
        subchunk_note = f", {stats['sections_subchunked']} sub-chunked"
    rerank_note = ""
    if eng.get("rerank"):
        rerank_note = f", rerank: {eng.get('rerank_model') or 'on'}"
    me = _script_invocation_path()
    lines = [
        f"# search: {out['query']}  ({scope}, "
        f"{stats['files_indexed']} files / {stats['items_indexed']} {unit_word}{subchunk_note}{rerank_note})",
        "",
    ]
    dropped_path = stats.get("dropped_stale_path", 0)
    if dropped_path:
        lines.append(
            f"Note: dropped {dropped_path} result(s) for stale paths — run `index` to prune."
        )
        lines.append("")
    results = out.get("results") or []
    if not results:
        lines.append("(no results)")
        lines.append("")
    for i, r in enumerate(results, start=1):
        chain = r["heading_chain"]
        if scope == "descriptions":
            heading_str = "(frontmatter description)"
        elif not chain:
            heading_str = "(file, no heading)"
        else:
            heading_str = f"## {chain}"
        lines.append(
            f"{i}. [{r['section_id']}] {r['relative_path']}:L{r['start_line']}  ~{r['token_count']}t"
        )
        lines.append(f"   {heading_str}")
        signal_line = f"   signals: {_signal_label(r)}  rrf {r['rrf_score']:.3f}"
        if r.get("rerank_score") is not None:
            signal_line += f"  rerank {r['rerank_score']:.3f}"
        lines.append(signal_line)
        if r.get("snippet"):
            lines.append(f"   {r['snippet']}")
        lines.append("")
    # Low-confidence diagnostic: when rerank was applied and the top
    # rerank score is in the noise floor, surface a hint so the agent
    # knows to broaden query or scope rather than trust top-1 blindly.
    if eng.get("rerank") and results:
        top_rerank = results[0].get("rerank_score")
        if top_rerank is not None and top_rerank < 0.1:
            lines.append(
                f"Note: low-confidence rerank (top score {top_rerank:.3f} < 0.10). "
                f"No section strongly matches — try a broader query, drop "
                f"--path-include filters, or raise --candidates."
            )
            lines.append("")

    if results:
        if scope == "descriptions":
            file_ids = ",".join(str(r["file_id"]) for r in results)
            lines.append(
                f"Drill: {me} headings '{out['root']}' --output /tmp/md-map.json"
            )
            lines.append(f"       {me} pick /tmp/md-map.json --files {file_ids}")
        else:
            ids = ",".join(r["section_id"] for r in results)
            if _top_lead(results):
                top = results[0]
                lines.append(
                    f"Read top: {me} read '{top['relative_path']}' "
                    f"--offset {top['start_line']} --limit 80"
                )
            if output_path:
                lines.append(f"Pick batch: {me} pick {output_path} --headings {ids} --extract")
            else:
                lines.append(
                    f"Pick batch: {me} headings '{out['root']}' --output /tmp/md-map.json"
                )
                lines.append(
                    f"            {me} pick /tmp/md-map.json --headings {ids} --extract"
                )
    return "\n".join(lines).rstrip() + "\n"
