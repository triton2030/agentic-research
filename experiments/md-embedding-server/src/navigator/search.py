from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

from .embeddings import (
    _embed_texts_http,
    _vec_to_blob,
)
from .filters import (
    apply_path_filters_to_map,
    apply_path_filters as _apply_path_filters,
    normalize_path_filter_patterns,
    path_matches_any as _path_matches_any,
    sqlite_path_filter_sql,
)
from .folder_map import build_map
from .index import ensure_index, resolve_embed_model_for_corpus
from navigator.index_guidance import index_dry_run_command
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


def _partial_index_payload(
    index_stats: dict[str, Any],
    max_auto_embed: int | None,
) -> dict[str, Any] | None:
    if not index_stats.get("delta_too_large"):
        return None
    return {
        "active": True,
        "reason": "pending_delta_exceeds_auto_embed_cap",
        "max_auto_embed": max_auto_embed,
        "added_sections": index_stats.get("added_sections", 0),
        "pending_chunks": index_stats.get("pending_chunks", 0),
        "pending_files": (index_stats.get("pending_files", []) or [])[:10],
        "pending_files_total": len(index_stats.get("pending_files", []) or []),
        "pending_files_truncated": len(index_stats.get("pending_files", []) or []) > 10,
        "message": (
            "Search ran against the already indexed subset; pending files "
            "were not searched."
        ),
    }


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
    is enforced by the remap step in `search_payload`; this path-based filter
    is defense in depth in case that remap is bypassed or regresses."""
    paths_kept = {r["relative_path"] for r in final_results}
    files_kept = [f for f in map_data["files"] if f["relative_path"] in paths_kept]
    return {
        "root": map_data["root"],
        "file_count": len(files_kept),
        "description_gap_count": sum(1 for f in files_kept if not f["description"]),
        "heading_count": sum(f["heading_count"] for f in files_kept),
        "files": files_kept,
    }


def search_payload(
    *,
    corpus_root: Path,
    conn,
    map_data: dict[str, Any],
    items: list[dict[str, Any]],
    index_stats: dict[str, Any],
    selected_model: str,
    include_patterns: list[str],
    exclude_patterns: list[str],
    embedding_api_url: str,
    embedding_timeout: float,
    query: str,
    scope: str = SEARCH_DEFAULT_SCOPE,
    limit: int = SEARCH_DEFAULT_LIMIT,
    candidates: int = SEARCH_DEFAULT_CANDIDATES,
    rerank: bool = False,
    rerank_model: str = DEFAULT_RERANK_MODEL,
    rerank_api_url: str = DEFAULT_RERANK_API_URL,
    rerank_timeout: float = DEFAULT_RERANK_TIMEOUT,
    rerank_top_n: int = DEFAULT_RERANK_TOP_N,
    max_auto_embed: int | None = _DEFAULT_MAX_AUTO_EMBED,
    rerank_error_handler: Callable[[RuntimeError], None] | None = None,
) -> dict[str, Any]:
    weights = (
        {"description": 5.0, "title": 0.0, "heading": 0.0, "body": 1.0}
        if scope == "descriptions"
        else dict(SEARCH_DEFAULT_WEIGHTS)
    )
    bm25_results = _search_bm25(
        conn,
        query,
        scope,
        weights,
        candidates,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    dense_results = _search_dense(
        conn,
        selected_model,
        query,
        scope,
        candidates,
        embedding_api_url,
        embedding_timeout,
        corpus_root=corpus_root,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    rrf_scores = _rrf_merge(bm25_results, dense_results, k=SEARCH_RRF_K)
    fused_rowids = [rid for rid, _ in sorted(rrf_scores.items(), key=lambda item: -item[1])[:candidates]]
    filter_on = bool(include_patterns or exclude_patterns)
    hydrate_n = len(fused_rowids) if rerank or filter_on else limit
    hydrated = _hydrate_rows(conn, fused_rowids)[:hydrate_n]
    if filter_on:
        hydrated = _apply_path_filters(hydrated, include_patterns, exclude_patterns)
    hydrated = hydrated[:rerank_top_n] if rerank else hydrated[:limit]

    rerank_scores: dict[int, float] = {}
    rerank_applied = False
    if rerank and hydrated:
        docs = [
            doc_text_for_rerank(row["relative_path"], row["heading_chain"], row["body"])
            for row in hydrated
        ]
        try:
            ordered = rerank_documents(
                query,
                docs,
                model=rerank_model,
                api_url=rerank_api_url,
                timeout=rerank_timeout,
                corpus_root=corpus_root,
            )
        except RuntimeError as exc:
            if rerank_error_handler is not None:
                rerank_error_handler(exc)
            ordered = []
        if ordered:
            reordered: list[dict[str, Any]] = []
            for idx, score in ordered:
                if 0 <= idx < len(hydrated):
                    row = hydrated[idx]
                    rerank_scores[row["rowid"]] = score
                    reordered.append(row)
            if reordered:
                hydrated = reordered
                rerank_applied = True
    hydrated = hydrated[:limit]

    fresh_file_id_by_path = {file["relative_path"]: file["id"] for file in map_data["files"]}
    final_results: list[dict[str, Any]] = []
    dropped_stale_path = 0
    for row in hydrated:
        path = row["relative_path"]
        fresh_fid = fresh_file_id_by_path.get(path)
        if fresh_fid is None:
            dropped_stale_path += 1
            continue
        row["file_id"] = fresh_fid
        old_sid = str(row.get("section_id") or "")
        row["section_id"] = f"{fresh_fid}.{old_sid.split('.', 1)[1]}" if "." in old_sid else str(fresh_fid)
        final_results.append(row)

    bm25_map = dict(bm25_results)
    dense_map = dict(dense_results)
    for row in final_results:
        rid = row["rowid"]
        row["bm25_score"] = bm25_map.get(rid)
        row["dense_distance"] = dense_map.get(rid)
        row["rrf_score"] = rrf_scores.get(rid, 0.0)
        row["rerank_score"] = rerank_scores.get(rid)
        row["fields_hit"] = _fields_hit(conn, rid, query)
        row["snippet"] = _snippet_for(row["body"], query)

    subchunked_count = sum(
        1 for item in items if scope == "sections" and _should_subchunk(item["body"] or "")
    )
    output = {
        "root": str(corpus_root),
        "query": query,
        "scope": scope,
        "engine": {
            "bm25f": True,
            "dense": True,
            "embed_model": selected_model,
            "embedding_api_url": embedding_api_url,
            "rerank": rerank_applied,
            "rerank_model": rerank_model if rerank_applied else None,
            "rerank_top_n": rerank_top_n if rerank_applied else None,
            "rerank_api_url": rerank_api_url if rerank_applied else None,
            "path_include": include_patterns,
            "path_exclude": exclude_patterns,
        },
        "stats": {
            "files_indexed": map_data["file_count"],
            "items_indexed": len(items),
            "sections_subchunked": subchunked_count,
            "embeddings_cached": index_stats["reused"],
            "embeddings_computed": index_stats["embedded"],
            "sections_removed": index_stats["removed_sections"],
            "bm25_hits": len(bm25_results),
            "dense_hits": len(dense_results),
            "dropped_stale_path": dropped_stale_path,
        },
        "weights": weights,
        "results": final_results,
    }
    partial_index = _partial_index_payload(index_stats, max_auto_embed)
    if partial_index:
        output["partial_index"] = partial_index
    return output


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
            f"Note: dropped {dropped_path} result(s) for stale paths — "
            f"preview `{index_dry_run_command(out['root'])}` before pruning."
        )
        lines.append("")
    partial_index = out.get("partial_index") or {}
    if partial_index.get("active"):
        lines.append(
            "Warning: partial index — search skipped pending files "
            f"({partial_index.get('added_sections', 0)} sections / "
            f"{partial_index.get('pending_chunks', 0)} chunks)."
        )
        for item in partial_index.get("pending_files") or []:
            lines.append(
                f"- {item['relative_path']} "
                f"(sections={item['added_sections']}, chunks={item['pending_chunks']})"
            )
        lines.append(f"Next: {index_dry_run_command(out['root'])}")
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
