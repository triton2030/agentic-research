from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

# 2026-06-11 live MAVO eval did not clear the default threshold; keep the
# cheapest mode until query-pack/graph/rerank prove a better clean tradeoff.
CANON_DEFAULT_MODE = "single"
CANON_RRF_K = 60
LOW_SCORE_THRESHOLD = 0.008
GRAPH_BONUS = 1.0 / 60.0


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
    )
    return list(payload.get("results") or [])


def fused_search(ctx, queries: list[str], *, limit: int = 10, candidates: int = 80) -> list[dict[str, Any]]:
    rows_by_id: dict[int, dict[str, Any]] = {}
    fused: dict[int, float] = {}
    ranks: dict[int, list[dict[str, Any]]] = {}
    for query in queries:
        rows = search_one(ctx, query, limit=candidates, candidates=candidates)
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
