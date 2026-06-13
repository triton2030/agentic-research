from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

# 2026-06-11 live MAVO eval did not clear the default threshold; keep the
# cheapest mode until query-pack/graph/rerank prove a better clean tradeoff.
CANON_DEFAULT_MODE = "single"
CANON_RRF_K = 60
LOW_SCORE_THRESHOLD = 0.008
GRAPH_BONUS = 1.0 / 60.0


class DenseIndex:
    def __init__(self, section_rowids: list[int], vectors: Any) -> None:
        self.section_rowids = section_rowids
        self.vectors = vectors


def open_retrieval_context(
    corpus: str,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **kwargs: Any,
):
    from navigator.api_index_context import _index_context_kwargs, _sections_index_context

    return _sections_index_context(
        corpus,
        scope="sections",
        allow_partial_index=True,
        path_include=path_include,
        path_exclude=path_exclude,
        **_index_context_kwargs(kwargs),
    )


def _score(row: dict[str, Any]) -> float:
    return float(row.get("rrf_score") or row.get("fused_score") or 0.0)


def _merge_fields(existing: dict[str, Any], row: dict[str, Any]) -> None:
    fields = set(existing.get("fields_hit") or [])
    fields.update(row.get("fields_hit") or [])
    existing["fields_hit"] = sorted(fields)


def search_one(ctx, query: str, *, limit: int = 10, candidates: int = 80) -> list[dict[str, Any]]:
    return search_one_with_vector(
        ctx,
        query,
        limit=limit,
        candidates=candidates,
        query_vector=None,
    )


def search_one_with_vector(
    ctx,
    query: str,
    *,
    limit: int = 10,
    candidates: int = 80,
    query_vector: Any | None = None,
) -> list[dict[str, Any]]:
    from navigator.search import search_payload

    payload = search_payload(
        corpus_root=ctx.corpus_root,
        conn=ctx.conn,
        map_data=ctx.map_data,
        items=ctx.items,
        index_stats=ctx.index_stats,
        selected_model=ctx.selected_model,
        include_patterns=ctx.include_patterns,
        exclude_patterns=ctx.exclude_patterns,
        embedding_api_url=ctx.embedding_api_url,
        embedding_timeout=ctx.embedding_timeout,
        query=query,
        limit=limit,
        candidates=candidates,
        query_vector=query_vector,
    )
    return list(payload.get("results") or [])


def prepare_dense_index(ctx) -> DenseIndex:
    from navigator.filters import sqlite_path_filter_sql
    import numpy as np

    path_clause, path_params = sqlite_path_filter_sql(
        "s.relative_path",
        ctx.include_patterns,
        ctx.exclude_patterns,
    )
    rows = ctx.conn.execute(
        "SELECT chunks.section_rowid, vec.embedding "
        "FROM sections_vec vec "
        "JOIN chunks ON chunks.chunk_id = vec.rowid "
        "JOIN sections AS s ON s.rowid = chunks.section_rowid "
        "WHERE s.scope = ? "
        f"{path_clause}",
        ("sections", *path_params),
    ).fetchall()
    if not rows:
        return DenseIndex([], np.zeros((0, 0), dtype=np.float32))
    section_rowids = [int(rowid) for rowid, _blob in rows]
    vectors = np.stack(
        [np.frombuffer(blob, dtype=np.float32) for _rowid, blob in rows]
    ).astype(np.float32)
    return DenseIndex(section_rowids, vectors)


def _dense_matrix_search(
    dense_index: DenseIndex,
    query_vector: Any,
    *,
    candidates: int,
) -> list[tuple[int, float]]:
    if query_vector is None or not dense_index.section_rowids:
        return []
    import numpy as np

    q = np.asarray(query_vector, dtype=np.float32)
    if q.ndim != 1 or dense_index.vectors.shape[1] != q.shape[0]:
        return []
    scores = dense_index.vectors @ q
    over_fetch = min(len(scores), max(candidates * 8, candidates + 100))
    if over_fetch <= 0:
        return []
    idx = np.argpartition(-scores, over_fetch - 1)[:over_fetch]
    idx = idx[np.argsort(-scores[idx])]
    best_per_section: dict[int, float] = {}
    for pos in idx:
        rowid = dense_index.section_rowids[int(pos)]
        score = float(scores[int(pos)])
        if rowid not in best_per_section or score > best_per_section[rowid]:
            best_per_section[rowid] = score
    ordered = sorted(best_per_section.items(), key=lambda item: -item[1])[:candidates]
    return [(rowid, 2.0 - 2.0 * score) for rowid, score in ordered]


def search_one_matrix(
    ctx,
    query: str,
    *,
    query_vector: Any,
    dense_index: DenseIndex,
    limit: int = 10,
    candidates: int = 80,
) -> list[dict[str, Any]]:
    from navigator.search import (
        SEARCH_DEFAULT_WEIGHTS,
        SEARCH_RRF_K,
        _fields_hit,
        _hydrate_rows,
        _rrf_merge,
        _search_bm25,
        _snippet_for,
    )

    bm25_results = _search_bm25(
        ctx.conn,
        query,
        "sections",
        dict(SEARCH_DEFAULT_WEIGHTS),
        candidates,
        path_include=ctx.include_patterns,
        path_exclude=ctx.exclude_patterns,
    )
    dense_results = _dense_matrix_search(
        dense_index,
        query_vector,
        candidates=candidates,
    )
    rrf_scores = _rrf_merge(bm25_results, dense_results, k=SEARCH_RRF_K)
    rowids = [rid for rid, _score in sorted(rrf_scores.items(), key=lambda item: -item[1])[:limit]]
    rows = _hydrate_rows(ctx.conn, rowids)
    fresh_file_id_by_path = {file["relative_path"]: file["id"] for file in ctx.map_data["files"]}
    bm25_map = dict(bm25_results)
    dense_map = dict(dense_results)
    out: list[dict[str, Any]] = []
    for row in rows:
        path = row["relative_path"]
        fresh_fid = fresh_file_id_by_path.get(path)
        if fresh_fid is None:
            continue
        rid = int(row["rowid"])
        item = dict(row)
        item["file_id"] = fresh_fid
        old_sid = str(item.get("section_id") or "")
        item["section_id"] = f"{fresh_fid}.{old_sid.split('.', 1)[1]}" if "." in old_sid else str(fresh_fid)
        item["bm25_score"] = bm25_map.get(rid)
        item["dense_distance"] = dense_map.get(rid)
        item["rrf_score"] = rrf_scores.get(rid, 0.0)
        item["rerank_score"] = None
        item["fields_hit"] = _fields_hit(ctx.conn, rid, query)
        item["snippet"] = _snippet_for(str(item.get("body") or ""), query)
        out.append(item)
    return out


def prepare_query_vectors(ctx, queries: list[str]) -> tuple[dict[str, Any], dict[str, int]]:
    from navigator.query_vectors import get_query_vectors

    batch = get_query_vectors(
        ctx.conn,
        ctx.selected_model,
        queries,
        ctx.embedding_api_url,
        ctx.embedding_timeout,
        corpus_root=ctx.corpus_root,
    )
    stats = {"cached": batch.cached, "computed": batch.computed}
    return batch.vectors, stats


def fused_search(
    ctx,
    queries: list[str],
    *,
    limit: int = 10,
    candidates: int = 80,
    query_vectors: dict[str, Any] | None = None,
    dense_index: DenseIndex | None = None,
) -> list[dict[str, Any]]:
    rows_by_id: dict[int, dict[str, Any]] = {}
    fused: dict[int, float] = {}
    ranks: dict[int, list[dict[str, Any]]] = {}
    for query in queries:
        if query_vectors is None:
            rows = search_one(ctx, query, limit=candidates, candidates=candidates)
        elif dense_index is not None:
            rows = search_one_matrix(
                ctx,
                query,
                query_vector=query_vectors.get(query),
                dense_index=dense_index,
                limit=candidates,
                candidates=candidates,
            )
        else:
            rows = search_one_with_vector(
                ctx,
                query,
                limit=candidates,
                candidates=candidates,
                query_vector=query_vectors.get(query),
            )
        for rank, row in enumerate(rows, start=1):
            rowid = int(row["rowid"])
            fused[rowid] = fused.get(rowid, 0.0) + 1.0 / (CANON_RRF_K + rank)
            ranks.setdefault(rowid, []).append({"query": query, "rank": rank})
            if rowid not in rows_by_id:
                rows_by_id[rowid] = dict(row)
            else:
                _merge_fields(rows_by_id[rowid], row)
    ordered = sorted(fused, key=lambda rid: (-fused[rid], str(rows_by_id[rid].get("relative_path") or "")))
    out: list[dict[str, Any]] = []
    for rowid in ordered[:limit]:
        row = dict(rows_by_id[rowid])
        row["rrf_score"] = fused[rowid]
        row["query_ranks"] = ranks.get(rowid, [])
        out.append(row)
    return out


def _neighbor_paths(graph, path: Path) -> set[str]:
    resolved = path.resolve()
    neighbors: set[str] = set()
    if resolved not in graph:
        return neighbors
    for _src, dst in graph.out_edges(resolved):
        rel = graph.nodes[dst].get("relative_path")
        if rel:
            neighbors.add(str(rel))
    for src, _dst in graph.in_edges(resolved):
        rel = graph.nodes[src].get("relative_path")
        if rel:
            neighbors.add(str(rel))
    return neighbors


def apply_graph_bonus(
    corpus_root: Path,
    source_file: Path,
    rows: list[dict[str, Any]],
    *,
    top_files: int = 3,
    bonus: float = GRAPH_BONUS,
) -> list[dict[str, Any]]:
    if not rows:
        return rows
    from navigator.link_graph import build_link_graph

    graph = build_link_graph(corpus_root)
    related = _neighbor_paths(graph, source_file)
    for row in rows[:top_files]:
        rel = row.get("relative_path")
        if isinstance(rel, str):
            related.update(_neighbor_paths(graph, corpus_root / rel))
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        if item.get("relative_path") in related:
            item["graph_bonus"] = bonus
            item["rrf_score"] = _score(item) + bonus
        else:
            item["graph_bonus"] = 0.0
        out.append(item)
    return sorted(out, key=lambda item: (-_score(item), str(item.get("relative_path") or "")))


def apply_rerank(
    claim_text: str,
    rows: list[dict[str, Any]],
    *,
    top_n: int = 20,
    corpus_root: Path | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    if not rows:
        return rows, False
    from navigator.rerank import doc_text_for_rerank, rerank_documents

    head = rows[:top_n]
    tail = rows[top_n:]
    docs = [
        doc_text_for_rerank(str(row.get("relative_path") or ""), str(row.get("heading_chain") or ""), str(row.get("body") or ""))
        for row in head
    ]
    try:
        ordered = rerank_documents(claim_text, docs, corpus_root=corpus_root)
    except RuntimeError:
        return rows, False
    if not ordered:
        return rows, False
    reranked: list[dict[str, Any]] = []
    seen: set[int] = set()
    for idx, score in ordered:
        if 0 <= idx < len(head):
            item = dict(head[idx])
            item["rerank_score"] = score
            reranked.append(item)
            seen.add(idx)
    reranked.extend(row for idx, row in enumerate(head) if idx not in seen)
    reranked.extend(tail)
    return reranked, True


def flag_row(row: dict[str, Any], *, low_score_threshold: float = LOW_SCORE_THRESHOLD) -> list[str]:
    flags: list[str] = []
    if _score(row) < low_score_threshold:
        flags.append("low_score")
    if row.get("zone") == "future":
        flags.append("future_zone")
    return flags
