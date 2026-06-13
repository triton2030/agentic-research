from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

from navigator.api_utils import _exit, _read_next

from .claims import extract_claims
from .evidence import (
    AUTHORITY,
    DEPENDENT_CONTEXT,
    PARKING,
    annotate_rows,
    build_evidence_scope,
    merge_buckets,
    role_buckets,
)
from .pairs import build_pairs
from .query_pack import build_query_pack, morphology_available
from .retrieval import (
    CANON_DEFAULT_MODE,
    apply_graph_bonus,
    apply_rerank,
    fused_search,
    flag_row,
    open_retrieval_context,
    prepare_dense_index,
    prepare_query_vectors,
)
from .zones import build_zone_map, load_zone_config, make_zone_resolver

VALID_MODES = ("single", "pack", "pack-graph", "pack-graph-rerank")


def _search_rows(
    *,
    context,
    claim_text: str,
    queries: list[str],
    corpus_root: Path,
    source: Path,
    mode: str,
    limit: int,
    use_graph: bool,
    use_rerank: bool,
    query_vectors: dict[str, Any] | None = None,
    dense_index=None,
) -> tuple[list[dict[str, Any]], bool]:
    rows = fused_search(
        context,
        queries,
        limit=limit,
        candidates=max(40, limit * 8),
        query_vectors=query_vectors,
        dense_index=dense_index,
    )
    if use_graph:
        rows = apply_graph_bonus(corpus_root, source, rows)
    rerank_applied = False
    if use_rerank:
        rows, rerank_applied = apply_rerank(claim_text, rows, corpus_root=corpus_root)
    return rows, rerank_applied


def _split_rows(
    rows: list[dict[str, Any]],
    zone_resolver,
    *,
    has_canon_config: bool,
) -> dict[str, list[dict[str, Any]]]:
    return role_buckets(
        annotate_rows(rows, zone_resolver, has_canon_config=has_canon_config)
    )


def _needs_discovery(
    buckets: dict[str, list[dict[str, Any]]],
    *,
    expanded: bool,
    top_quotes: int = 3,
) -> bool:
    if expanded:
        return True
    authority_rows = buckets.get(AUTHORITY) or []
    if not authority_rows:
        return True
    head = authority_rows[:top_quotes]
    return bool(head) and all("low_score" in flag_row(row) for row in head)


def run_canon_check(
    file: str,
    corpus: str,
    *,
    mode: str | None = None,
    limit: int | None = None,
    max_claims: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    rerank: bool = False,
    expanded: bool = False,
) -> dict[str, Any]:
    selected_mode = mode or CANON_DEFAULT_MODE
    if selected_mode not in VALID_MODES:
        return _exit({"error": "invalid_mode", "mode": selected_mode, "valid_modes": list(VALID_MODES)}, 2)

    corpus_root = Path(corpus).expanduser().resolve()
    source = Path(file).expanduser().resolve()
    if not source.exists():
        return _exit({"error": "path_not_found", "file": file}, 2)
    try:
        source_rel = source.relative_to(corpus_root).as_posix()
    except ValueError:
        return _exit({"error": "file_outside_corpus", "file": str(source), "corpus": str(corpus_root)}, 2)

    text = source.read_text(encoding="utf-8", errors="replace")
    claim_result = extract_claims(text, max_claims=max_claims)
    if not claim_result.claims:
        return {
            "workflow": "md_canon_check",
            "file": source_rel,
            "mode": selected_mode,
            "stats": {"claims_total": 0, "claims_checked": 0, "queries_run": 0, "elapsed_ms": 0},
            "pairs": [],
            "quality_flags": ["no_normative_claims"],
            "advice": "No normative claims found; canon-check has no evidence to gather.",
            "read_next": [],
        }

    cfg = load_zone_config(corpus_root)
    scope = build_evidence_scope(
        cfg,
        source_rel=source_rel,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    error, _code, context = open_retrieval_context(
        str(corpus_root),
        path_include=scope.authority_include,
        path_exclude=scope.path_exclude,
    )
    if error is not None:
        if not (scope.discovery_enabled and error.get("error") == "empty"):
            return error
        context = None
    discovery_context = None

    started = perf_counter()
    per_claim: list[dict[str, list[dict[str, Any]]]] = []
    queries_run = 0
    authority_queries_run = 0
    discovery_queries_run = 0
    rerank_unavailable = False
    use_pack = selected_mode in {"pack", "pack-graph", "pack-graph-rerank"}
    use_graph = selected_mode in {"pack-graph", "pack-graph-rerank"}
    use_rerank = bool(rerank or selected_mode == "pack-graph-rerank")
    claim_queries = [
        build_query_pack(claim.text, claim.heading_chain) if use_pack else [claim.text]
        for claim in claim_result.claims
    ]
    query_vectors: dict[str, Any] = {}
    query_embedding_cached = 0
    query_embedding_computed = 0
    authority_dense_index = None
    if context is not None:
        query_vectors, query_stats = prepare_query_vectors(
            context,
            [query for queries in claim_queries for query in queries],
        )
        query_embedding_cached += query_stats["cached"]
        query_embedding_computed += query_stats["computed"]
        authority_dense_index = prepare_dense_index(context)
    discovery_dense_index = None
    zone_map = build_zone_map(corpus_root)
    zone_resolver = make_zone_resolver(corpus_root, zone_map, cfg)

    for claim, queries in zip(claim_result.claims, claim_queries):
        query_count = len(queries)
        claim_limit = int(limit or 10)
        authority_rows: list[dict[str, Any]] = []
        if context is not None:
            authority_rows, rerank_applied = _search_rows(
                context=context,
                claim_text=claim.text,
                queries=queries,
                corpus_root=corpus_root,
                source=source,
                mode=selected_mode,
                limit=claim_limit,
                use_graph=use_graph,
                use_rerank=use_rerank,
                query_vectors=query_vectors,
                dense_index=authority_dense_index,
            )
            authority_queries_run += query_count
            rerank_unavailable = rerank_unavailable or (use_rerank and bool(authority_rows) and not rerank_applied)
        authority_buckets = _split_rows(
            authority_rows[:claim_limit],
            zone_resolver,
            has_canon_config=scope.has_canon_config,
        )
        discovery_buckets = {AUTHORITY: [], DEPENDENT_CONTEXT: [], PARKING: []}
        if scope.discovery_enabled and _needs_discovery(authority_buckets, expanded=expanded):
            if discovery_context is None:
                error, _code, discovery_context = open_retrieval_context(
                    str(corpus_root),
                    path_include=scope.discovery_include,
                    path_exclude=scope.path_exclude,
                )
                if error is not None:
                    return error
                if not query_vectors:
                    query_vectors, query_stats = prepare_query_vectors(
                        discovery_context,
                        [query for items in claim_queries for query in items],
                    )
                    query_embedding_cached += query_stats["cached"]
                    query_embedding_computed += query_stats["computed"]
                discovery_dense_index = prepare_dense_index(discovery_context)
            discovery_rows, discovery_rerank_applied = _search_rows(
                context=discovery_context,
                claim_text=claim.text,
                queries=queries,
                corpus_root=corpus_root,
                source=source,
                mode=selected_mode,
                limit=max(claim_limit * 3, 20),
                use_graph=use_graph,
                use_rerank=use_rerank,
                query_vectors=query_vectors,
                dense_index=discovery_dense_index,
            )
            discovery_queries_run += query_count
            rerank_unavailable = rerank_unavailable or (
                use_rerank and bool(discovery_rows) and not discovery_rerank_applied
            )
            discovery_buckets = _split_rows(
                discovery_rows,
                zone_resolver,
                has_canon_config=scope.has_canon_config,
            )
            discovery_buckets[AUTHORITY] = []
        per_claim.append(merge_buckets(authority_buckets, discovery_buckets))
    queries_run = authority_queries_run + discovery_queries_run

    pairs, quality_flags, advice = build_pairs(
        claim_result.claims,
        per_claim,
        zone_resolver,
        top_quotes=3,
        expanded=expanded,
    )
    if not cfg.root and not cfg.future:
        quality_flags.append("no_canon_config")
    if claim_result.truncated:
        quality_flags.append("claims_truncated")
    stats_context = context or discovery_context
    if stats_context is not None and stats_context.index_stats.get("delta_too_large"):
        quality_flags.append("partial_index")
    if rerank_unavailable:
        quality_flags.append("rerank_unavailable")
    if not morphology_available():
        quality_flags.append("morphology_unavailable")

    read_next = []
    first_quote = next(
        (
            quote
            for pair in pairs
            for quote in pair.get("quotes", [])
            if isinstance(quote, dict) and quote.get("relative_path")
        ),
        None,
    )
    if isinstance(first_quote, dict):
        read_next.append(
            _read_next(
                "md_search_read",
                {
                    "corpus": str(corpus_root),
                    "query": claim_result.claims[0].text,
                    "path_include": [first_quote["relative_path"]],
                    "expanded": True,
                },
                "Expand the strongest canon-check quote before editing the source claim.",
            )
        )

    return {
        "workflow": "md_canon_check",
        "file": source_rel,
        "mode": selected_mode,
        "owner_scope_defaulted": scope.default_scope_applied,
        "scope_policy": scope.policy,
        "stats": {
            "claims_total": len(claim_result.claims),
            "claims_checked": len(per_claim),
            "queries_run": queries_run,
            "authority_queries_run": authority_queries_run,
            "discovery_queries_run": discovery_queries_run,
            "query_embeddings_cached": query_embedding_cached,
            "query_embeddings_computed": query_embedding_computed,
            "elapsed_ms": int((perf_counter() - started) * 1000),
        },
        "pairs": pairs,
        "quality_flags": sorted(set(quality_flags)),
        "advice": advice,
        "read_next": read_next,
    }
