from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .api_utils import _exit, _list, _read_next
from .config import CONFIG_FILENAME, resolve_filter_layers_for_domain, resolve_filters_for_domain

def index(
    corpus: str,
    *,
    dry_run: bool = False,
    confirm: bool = False,
    allow_nested_corpus: bool = False,
    batch_size: int | None = None,
    batch_pause_ms: int | None = None,
    max_heading_level: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    vacuum: bool = False,
    cleanup_shadowed: bool = False,
    embed_model: str | None = None,
    embedding_api_url: str | None = None,
    embedding_timeout: float | None = None,
    cache_dir: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    from .cli_common import SEARCH_DEFAULT_EMBEDDING_TIMEOUT
    from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
    from .folder_map import build_map
    from .index_lifecycle import (
        apply_cleanup,
        cleanup_enabled_for_operation,
        plan_cleanup,
        vacuum_index,
        vacuum_preview,
    )
    from .index_resolution import cleanup_shadowed_indexes
    from .index_build import _chunks_for_item, ensure_index
    from .index_meta import (
        _index_dir_for_corpus,
        find_parent_indexed_corpus,
        nested_corpus_refusal,
        resolve_embedding_api_url_for_corpus,
        resolve_embed_model_for_corpus,
    )
    from .index_readiness import IndexReadinessKind, classify_index_readiness
    from .sections import build_items_from_map

    corpus_root = Path(corpus).expanduser().resolve()
    if not corpus_root.exists():
        return _exit({"error": "path_not_found", "corpus": str(corpus_root)}, 2)
    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    if cleanup_shadowed:
        return cleanup_shadowed_indexes(
            corpus_root,
            dry_run=dry_run,
            confirm=confirm,
            cache_root=cache_root,
        )
    filter_layers = resolve_filter_layers_for_domain(
        corpus_root, domain="index",
        path_include=path_include, path_exclude=path_exclude,
    )
    include_values = _list(filter_layers.effective_include)
    exclude_values = _list(filter_layers.effective_exclude)
    parent_corpus = find_parent_indexed_corpus(corpus_root, cache_root=cache_root)
    if parent_corpus is not None and not allow_nested_corpus:
        return _exit(
            nested_corpus_refusal(
                corpus_root,
                parent_corpus,
                path_include=include_values,
                path_exclude=exclude_values,
            ),
            1,
        )
    map_data = build_map(corpus_root, max_heading_level or 6, with_tokens=True)
    include_patterns = normalize_path_filter_patterns(filter_layers.effective_include, corpus_root)
    exclude_patterns = normalize_path_filter_patterns(filter_layers.effective_exclude, corpus_root)
    config_include_patterns = normalize_path_filter_patterns(filter_layers.config_include, corpus_root)
    config_exclude_patterns = normalize_path_filter_patterns(filter_layers.config_exclude, corpus_root)
    cleanup_enabled = cleanup_enabled_for_operation(
        filter_layers.operation_include,
        filter_layers.operation_exclude,
    )
    cleanup_disabled_reason = None if cleanup_enabled else "operation_scope"
    scoped = apply_path_filters_to_map(map_data, include_patterns, exclude_patterns)
    items_by_scope = {scope: build_items_from_map(scoped, scope=scope) for scope in ("sections", "descriptions")}
    pending_chunks = sum(len(_chunks_for_item(item)) for items in items_by_scope.values() for item in items)
    affected_files = _index_affected_files(scoped, corpus_root)
    index_exists = (_index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite").exists()
    cleanup_plan = plan_cleanup(
        corpus_root,
        cache_root=cache_root,
        config_include=config_include_patterns,
        config_exclude=config_exclude_patterns,
        enabled=cleanup_enabled,
        disabled_reason=cleanup_disabled_reason,
    )
    selected_model = resolve_embed_model_for_corpus(corpus_root, embed_model, cache_root=cache_root)
    selected_api_url = resolve_embedding_api_url_for_corpus(
        corpus_root,
        embedding_api_url,
        cache_root=cache_root,
    )
    readiness = classify_index_readiness(
        corpus_root,
        cache_root=cache_root,
        expected_embed_model=selected_model,
        expected_embedding_api_url=selected_api_url,
        check_integrity=True,
    )
    if (dry_run or not confirm) and index_exists:
        if readiness.kind is not IndexReadinessKind.READY:
            payload = {
                "command": "index",
                "dry_run": bool(dry_run),
                "pending_chunks": pending_chunks,
                "added_sections": sum(len(items) for items in items_by_scope.values()),
                "removed_sections": 0,
                "estimated_cost_usd": round(pending_chunks * 0.00002, 4),
                "affected_files": affected_files,
                "index_readiness": readiness.kind.value,
                "metadata_mismatch": readiness.kind is not IndexReadinessKind.INTEGRITY_MISMATCH,
                **cleanup_plan.public_payload(),
            }
            if readiness.integrity is not None or readiness.issues:
                payload["index_integrity"] = {
                    "ok": False,
                    "counts": {"sections": 0, "chunks": 0, "sections_fts": 0, "sections_vec": 0},
                    "issues": readiness.issues,
                    **(readiness.integrity or {}),
                }
            if vacuum:
                payload["vacuum"] = vacuum_preview(corpus_root, cache_root=cache_root)
            return payload
        totals = {"pending_chunks": 0, "added_sections": 0, "removed_sections": 0}
        for scope, items in items_by_scope.items():
            conn, stats = ensure_index(
                corpus_root,
                scope,
                items,
                selected_model,
                embedding_api_url=selected_api_url,
                embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
                cache_root=cache_root,
                max_auto_embed=None,
                dry_run=True,
                path_include=include_patterns,
                path_exclude=exclude_patterns,
                skip_existing_rowids=cleanup_plan.rowids,
            )
            conn.close()
            totals["pending_chunks"] += stats.get("pending_chunks", 0)
            totals["added_sections"] += stats.get("added_sections", 0)
            totals["removed_sections"] += stats.get("removed_sections", 0)
        payload = {
            "command": "index",
            "dry_run": bool(dry_run),
            **totals,
            "estimated_cost_usd": round(totals["pending_chunks"] * 0.00002, 4),
            "affected_files": affected_files,
            **cleanup_plan.public_payload(),
        }
        if vacuum:
            payload["vacuum"] = vacuum_preview(corpus_root, cache_root=cache_root)
        return payload
    if dry_run or not confirm:
        payload = {
            "command": "index",
            "dry_run": bool(dry_run),
            "pending_chunks": pending_chunks,
            "added_sections": sum(len(items) for items in items_by_scope.values()),
            "estimated_cost_usd": round(pending_chunks * 0.00002, 4),
            "affected_files": affected_files,
            **cleanup_plan.public_payload(),
        }
        if vacuum:
            payload["vacuum"] = vacuum_preview(corpus_root, cache_root=cache_root)
        return payload
    cleanup_result = apply_cleanup(
        corpus_root,
        cache_root=cache_root,
        embed_model=selected_model,
        embedding_api_url=selected_api_url,
        config_include=config_include_patterns,
        config_exclude=config_exclude_patterns,
        enabled=cleanup_enabled,
        disabled_reason=cleanup_disabled_reason,
    )
    totals = {"embedded": 0, "reused": 0, "removed_sections": 0}
    for scope, items in items_by_scope.items():
        conn, stats = ensure_index(
            corpus_root,
            scope,
            items,
            selected_model,
            embedding_api_url=selected_api_url,
            embedding_timeout=float(embedding_timeout or SEARCH_DEFAULT_EMBEDDING_TIMEOUT),
            cache_root=cache_root,
            max_auto_embed=None,
            batch_size=int(batch_size or 64),
            batch_pause_s=int(batch_pause_ms or 0) / 1000.0,
            path_include=include_patterns,
            path_exclude=exclude_patterns,
        )
        conn.close()
        totals["embedded"] += stats.get("embedded", 0)
        totals["reused"] += stats.get("reused", 0)
        totals["removed_sections"] += stats.get("removed_sections", 0)
    payload = {
        "command": "index",
        "corpus": str(corpus_root),
        **totals,
        **cleanup_result.public_payload(),
    }
    if vacuum:
        payload["vacuum"] = vacuum_index(corpus_root, cache_root=cache_root)
    return payload


def _index_affected_files(scoped_map: dict[str, Any], corpus_root: Path) -> list[str]:
    files = {str(Path(file["path"]).resolve()) for file in scoped_map.get("files", [])}
    # Include the config path even when missing so adding it between dry-run and
    # confirm is caught by the transaction fingerprint.
    files.add(str((corpus_root / CONFIG_FILENAME).resolve()))
    return sorted(files)

def profile_sections(
    corpus: str,
    *,
    dry_run: bool = False,
    confirm: bool = False,
    limit: int | None = None,
    force: bool = False,
    mode: str | None = None,
    model: str | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **_: Any,
) -> dict[str, Any]:
    from .filters import apply_path_filters_to_map, normalize_path_filter_patterns
    from .folder_map import build_map
    from .section_profile import open_profile_db, profile_corpus, profile_rows

    root = Path(corpus).expanduser().resolve()
    path_include, path_exclude = resolve_filters_for_domain(
        root, domain="index",
        path_include=path_include, path_exclude=path_exclude,
    )
    include_patterns = normalize_path_filter_patterns(path_include, root)
    exclude_patterns = normalize_path_filter_patterns(path_exclude, root)
    if dry_run or not confirm:
        map_data = apply_path_filters_to_map(
            build_map(root, 6, with_tokens=False),
            include_patterns,
            exclude_patterns,
        )
        section_count = sum(len(file.get("headings", [])) for file in map_data.get("files", []))
        per_unit = 0.0005 if mode in {"llm", "auto"} else 0
        return {
            "command": "profile-sections",
            "dry_run": bool(dry_run),
            "sections_to_profile_estimate": section_count,
            "mode": mode or "heuristic",
            "estimated_cost_usd": round(section_count * per_unit, 4),
            "affected_files": [str(Path(file["path"]).resolve()) for file in map_data.get("files", [])],
        }
    try:
        conn = open_profile_db(root)
    except RuntimeError as exc:
        return _exit({"command": "profile-sections", "error": str(exc)}, 2)
    stats = profile_corpus(
        conn,
        limit=limit,
        corpus_root=root,
        force=force,
        mode=mode,
        model=model,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    rows = profile_rows(conn, limit=10, corpus_root=root, path_include=include_patterns, path_exclude=exclude_patterns)
    return {"command": "profile-sections", "root": str(root), **stats, "sample": rows}


def _profile_required(
    root: Path,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    args: dict[str, Any] = {"corpus": str(root), "dry_run": True}
    if path_include:
        args["path_include"] = path_include
    if path_exclude:
        args["path_exclude"] = path_exclude
    return _exit(
        {
            "error": "profile_required",
            "corpus": str(root),
            "suggested_profile_args": args,
            "read_next": [
                _read_next(
                    "md_profile_sections",
                    args,
                    "Profile sections before running profile-backed queries.",
                )
            ],
        },
        4,
    )


def _profiled_section_count(
    conn: Any,
    *,
    corpus_root: Path,
    path_include: list[str] | None = None,
    path_exclude: list[str] | None = None,
) -> int:
    from .filters import sqlite_path_filter_sql

    columns = {row[1] for row in conn.execute("PRAGMA table_info(sections)").fetchall()}
    if "profile_type" not in columns:
        return 0
    path_clause, path_params = sqlite_path_filter_sql(
        "relative_path",
        path_include or [],
        path_exclude or [],
    )
    row = conn.execute(
        "SELECT COUNT(*) FROM sections WHERE scope='sections' "
        "AND profile_type IS NOT NULL "
        f"{path_clause}",
        path_params,
    ).fetchone()
    return int(row[0] if row else 0)


def query_by_type(
    corpus: str,
    types: Iterable[str] | str,
    *,
    filter: str | None = None,
    limit: int | None = None,
    compact: bool = False,
    expanded: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    from .filters import normalize_path_filter_patterns
    from .section_profile import open_profile_db, profile_rows

    root = Path(corpus).expanduser().resolve()
    merged_include, merged_exclude = resolve_filters_for_domain(
        root,
        domain="index",
        path_include=path_include,
        path_exclude=path_exclude,
    )
    try:
        conn = open_profile_db(root)
    except RuntimeError as exc:
        return _exit({"error": "index_warmup_required", "corpus": str(root), "detail": str(exc)}, 4)

    include_patterns = normalize_path_filter_patterns(merged_include, root)
    exclude_patterns = normalize_path_filter_patterns(merged_exclude, root)
    if not _profiled_section_count(
        conn,
        corpus_root=root,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    ):
        return _profile_required(root, path_include=path_include, path_exclude=path_exclude)

    selected_types = _list(types)
    rows = profile_rows(
        conn,
        types=selected_types,
        filter_text=filter,
        limit=int(limit or 50) if expanded else min(int(limit or 50), 10),
        corpus_root=root,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    if not expanded:
        rows = [
            {
                "section_id": row["section_id"],
                "path": row["relative_path"],
                "start_line": row["start_line"],
                "heading_chain": row["heading_chain"],
                "heading_text": row["heading_text"],
                "type": row["profile"]["type"],
                "subject": row["profile"]["subject"],
                "confidence": row["profile"]["confidence"],
            }
            for row in rows
        ]
    return {
        "types": selected_types,
        "path_include": include_patterns,
        "path_exclude": exclude_patterns,
        "sections": rows,
        "expanded": bool(expanded),
        "map_only": not expanded,
        "content_included": False,
        "read_next": [] if expanded else [
            _read_next(
                "md_query_by_type",
                {
                    "corpus": corpus,
                    "types": selected_types,
                    "expanded": True,
                    "filter": filter,
                    "limit": limit,
                    "path_include": path_include,
                    "path_exclude": path_exclude,
                },
                "Return full section profile detail.",
            )
        ],
    }


def _refactor_proposal_map(item: dict[str, Any]) -> dict[str, Any]:
    affected = item.get("affected_section") or {}
    target = item.get("target_owner") or {}
    evidence = item.get("evidence") or {}
    return {
        "proposal_type": item.get("proposal_type"),
        "confidence": item.get("confidence"),
        "why": item.get("why"),
        "affected_section": {
            "path": affected.get("path"),
            "heading_id": affected.get("heading_id"),
            "line_range": affected.get("line_range"),
            "heading_text": affected.get("heading_text"),
            "profile": affected.get("profile"),
        },
        "target_owner": {
            "path": target.get("path"),
            "heading_id": target.get("heading_id"),
            "heading_text": target.get("heading_text"),
            "profile": target.get("profile"),
        },
        "evidence_summary": {
            "cosine": evidence.get("cosine"),
            "uniqueness": evidence.get("uniqueness"),
            "owner_composite_score": evidence.get("owner_composite_score"),
        },
        "no_automation": item.get("no_automation", True),
    }


def refactor_candidates(
    corpus: str,
    *,
    compact: bool = False,
    expanded: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    from .filters import normalize_path_filter_patterns
    from .refactor_proposals import refactor_candidates as compute
    from .section_profile import open_profile_db

    root = Path(corpus).expanduser().resolve()
    merged_include, merged_exclude = resolve_filters_for_domain(
        root,
        domain="index",
        path_include=kwargs.get("path_include"),
        path_exclude=kwargs.get("path_exclude"),
    )
    try:
        conn = open_profile_db(root)
    except RuntimeError as exc:
        return _exit({"error": "index_warmup_required", "corpus": str(root), "detail": str(exc)}, 4)

    include_patterns = normalize_path_filter_patterns(merged_include, root)
    exclude_patterns = normalize_path_filter_patterns(merged_exclude, root)
    if not _profiled_section_count(
        conn,
        corpus_root=root,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    ):
        return _profile_required(
            root,
            path_include=kwargs.get("path_include"),
            path_exclude=kwargs.get("path_exclude"),
        )

    top = int(kwargs.get("top") or (10 if expanded else 3))
    uniqueness_threshold = float(kwargs.get("uniqueness_threshold") or 0.35)
    owner_confidence_threshold = float(kwargs.get("owner_confidence_threshold") or 0.45)
    payload = compute(
        conn,
        corpus_root=root,
        top=top,
        uniqueness_threshold=uniqueness_threshold,
        owner_confidence_threshold=owner_confidence_threshold,
        path_include=include_patterns,
        path_exclude=exclude_patterns,
    )
    payload["expanded"] = bool(expanded)
    payload["content_included"] = False
    if not expanded:
        payload["map_only"] = True
        payload["proposals"] = [_refactor_proposal_map(item) for item in payload.get("proposals", [])]
        payload["read_next"] = [
            _read_next(
                "md_refactor_candidates",
                {
                    "corpus": corpus,
                    "expanded": True,
                    "top": kwargs.get("top") or 10,
                    "uniqueness_threshold": uniqueness_threshold,
                    "owner_confidence_threshold": owner_confidence_threshold,
                    "path_include": kwargs.get("path_include"),
                    "path_exclude": kwargs.get("path_exclude"),
                },
                "Return full proposal evidence.",
            )
        ]
    else:
        payload["map_only"] = False
    return payload
