from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable

from .api_index_context import _index_context_kwargs, _index_missing, _index_warmup, _sections_index_context
from .api_utils import _exit, _list, _ns, _read_next, _reject_unknown_kwargs

_INDEX_BACKED_KWARGS = {
    "max_heading_level",
    "max_auto_embed",
    "path_include",
    "path_exclude",
    "embed_model",
    "embedding_api_url",
    "embedding_timeout",
    "cache_dir",
    "no_cache",
}

_OVERLAPS_KWARGS = _INDEX_BACKED_KWARGS | {
    "threshold",
    "top",
    "min_tokens",
    "include_same_file",
    "expanded",
}

_REPEATED_CONCEPTS_KWARGS = _INDEX_BACKED_KWARGS | {
    "threshold",
    "top",
    "min_tokens",
    "min_files",
    "min_sections",
    "top_members",
    "expanded",
}

_AUDIT_KWARGS = _INDEX_BACKED_KWARGS | {
    "expanded",
    "top_findings",
    "threshold_smear",
    "threshold_drift",
    "threshold_inter",
    "threshold_template",
    "threshold_heading_diversity",
    "min_files_in_family",
    "min_sections_per_file",
    "max_concepts",
    "cluster_k",
    "discovery_gap_warn",
    "discovery_gap_crit",
}

def _section_ref(section: dict[str, Any]) -> dict[str, Any]:
    return {
        key: section.get(key)
        for key in ("section_id", "file_id", "relative_path", "start_line", "heading_chain", "heading_text", "token_count")
        if section.get(key) is not None
    }

def _expand_action(tool: str, corpus: str, kwargs: dict[str, Any], reason: str) -> dict[str, Any]:
    args = {
        "corpus": corpus,
        "expanded": True,
        "threshold": kwargs.get("threshold"),
        "top": kwargs.get("top"),
        "min_tokens": kwargs.get("min_tokens"),
        "min_files": kwargs.get("min_files"),
        "min_sections": kwargs.get("min_sections"),
        "top_members": kwargs.get("top_members"),
        "include_same_file": kwargs.get("include_same_file"),
        "path_include": kwargs.get("path_include"),
        "path_exclude": kwargs.get("path_exclude"),
    }
    return _read_next(tool, args, reason)

def cluster(
    corpus: str,
    *,
    k: int | None = None,
    seed: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    cache_dir: str | None = None,
) -> dict[str, Any]:
    from .index_cluster import cluster_sections

    corpus_root = Path(corpus).expanduser().resolve()
    if not corpus_root.exists():
        return _exit({"command": "cluster", "error": "path_not_found", "corpus": str(corpus_root)}, 2)
    selected_k = int(k or 8)
    if selected_k < 1:
        return _exit({"command": "cluster", "error": "k_must_be_positive", "k": selected_k}, 2)
    cache_root = Path(cache_dir).expanduser() if cache_dir else None
    try:
        result = cluster_sections(
            corpus_root,
            k=selected_k,
            cache_root=cache_root,
            seed=int(seed or 42),
            path_include=_list(path_include),
            path_exclude=_list(path_exclude),
        )
    except FileNotFoundError:
        return _index_warmup(
            corpus_root,
            path_include=path_include,
            path_exclude=path_exclude,
            cache_root=cache_root,
        ) | {"command": "cluster"}
    except (ModuleNotFoundError, RuntimeError) as exc:
        return _exit({"command": "cluster", "error": "dependency_failed", "detail": str(exc)}, 3)

    for item in result.get("clusters", []):
        item["top_files"] = [list(pair) for pair in item.get("top_files", [])]
    return {"command": "cluster", "root": str(corpus_root), **result}

def _overlap_map(corpus: str, output: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for pair in output.get("pairs", []):
        left = pair.get("a") or {}
        right = pair.get("b") or {}
        left_path = str(left.get("relative_path") or "")
        right_path = str(right.get("relative_path") or "")
        paths = (left_path, right_path) if left_path <= right_path else (right_path, left_path)
        group = groups.setdefault(
            paths,
            {"paths": list(paths), "count": 0, "best_score": 0.0, "score_total": 0.0, "top_handles": []},
        )
        score = float(pair.get("similarity") or 0.0)
        group["count"] += 1
        group["score_total"] += score
        group["best_score"] = max(float(group["best_score"]), score)
        if len(group["top_handles"]) < 3:
            group["top_handles"].append(
                {
                    "similarity": score,
                    "a": _section_ref(left),
                    "b": _section_ref(right),
                }
            )
    overlap_map = []
    for group in groups.values():
        count = int(group["count"])
        group["mean_score"] = group.pop("score_total") / count if count else 0.0
        overlap_map.append(group)
    overlap_map.sort(key=lambda item: (-float(item["best_score"]), -int(item["count"])))
    return {
        "root": output.get("root"),
        "threshold": output.get("threshold"),
        "include_same_file": output.get("include_same_file"),
        "min_tokens": output.get("min_tokens"),
        "expanded": False,
        "map_only": True,
        "content_included": False,
        "engine": output.get("engine"),
        "stats": output.get("stats"),
        "pair_groups": overlap_map,
        "pairs_total": len(output.get("pairs", [])),
        "read_next": [
            _expand_action("md_overlaps", corpus, kwargs, "Return full overlap pair details.")
        ],
    }

def _concept_map(corpus: str, output: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    concepts = []
    for item in output.get("concepts", []):
        top_handles = []
        for member in item.get("top_members", []):
            top_handles.append(
                {
                    "similarity": member.get("similarity"),
                    "section": _section_ref(member.get("section") or {}),
                }
            )
        concepts.append(
            {
                "label": item.get("label"),
                "representative": _section_ref(item.get("medoid") or {}),
                "unique_files": item.get("unique_files"),
                "section_count": item.get("section_count"),
                "mean_cohesion": item.get("mean_cohesion"),
                "files": [
                    {"path": file.get("path"), "section_count": file.get("section_count")}
                    for file in item.get("file_breakdown", [])
                ],
                "top_handles": top_handles,
            }
        )
    return {
        "root": output.get("root"),
        "threshold": output.get("threshold"),
        "min_tokens": output.get("min_tokens"),
        "min_files": output.get("min_files"),
        "min_sections": output.get("min_sections"),
        "expanded": False,
        "map_only": True,
        "content_included": False,
        "engine": output.get("engine"),
        "stats": output.get("stats"),
        "concepts": concepts,
        "read_next": [
            _expand_action("md_repeated_concepts", corpus, kwargs, "Return full concept members and file breakdown.")
        ],
    }

def _evidence_summary(evidence: Any) -> dict[str, Any]:
    if not isinstance(evidence, dict):
        return {"value": evidence}
    summary: dict[str, Any] = {}
    for key, value in evidence.items():
        if isinstance(value, list):
            summary[key] = {"count": len(value), "sample": value[:2]}
        elif isinstance(value, dict):
            summary[key] = {"keys": sorted(str(item) for item in value.keys())[:8]}
        else:
            summary[key] = value
        if len(summary) >= 5:
            break
    return summary

def _audit_map(corpus: str, output: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    findings = output.get("findings", [])
    top_findings = [
        {
            "class": item.get("class"),
            "severity": item.get("severity"),
            "label": item.get("label"),
            "next_step": item.get("next_step"),
            "evidence_summary": _evidence_summary(item.get("evidence")),
        }
        for item in findings[: int(kwargs.get("top_findings") or 10)]
    ]
    return {
        "root": output.get("root"),
        "health": output.get("health"),
        "severity_counts": output.get("severity_counts"),
        "thresholds": output.get("thresholds"),
        "stats": output.get("stats"),
        "engine": output.get("engine"),
        "expanded": False,
        "map_only": True,
        "content_included": False,
        "findings": top_findings,
        "findings_total": len(findings),
        "findings_returned": len(top_findings),
        "read_next": [
            _expand_action("md_audit", corpus, kwargs, "Return full audit evidence.")
        ],
    }

def overlaps(corpus: str, **kwargs: Any) -> dict[str, Any]:
    from .overlaps import compute_overlaps

    _reject_unknown_kwargs("overlaps", kwargs, _OVERLAPS_KWARGS)
    error, _code, context = _sections_index_context(corpus, scope="sections", **_index_context_kwargs(kwargs))
    if error is not None:
        return error
    assert context is not None
    args = _ns(
        threshold=float(kwargs.get("threshold") or 0.85),
        top=int(kwargs.get("top") or 20),
        min_tokens=int(kwargs.get("min_tokens") or 30),
        include_same_file=bool(kwargs.get("include_same_file", False)),
        embed_model=context.selected_model,
        embedding_api_url=context.embedding_api_url,
        cache_dir=kwargs.get("cache_dir"),
        path_include=context.include_patterns,
        path_exclude=context.exclude_patterns,
    )
    output = compute_overlaps(context.corpus_root, context.conn, context.map_data, context.index_stats, args)
    if output is None:
        return _exit({"empty": True, "reason": "Need at least 2 chunks to compare."}, 1)
    if bool(kwargs.get("expanded", False)):
        output["expanded"] = True
        output["map_only"] = False
        output["content_included"] = False
        return output
    return _overlap_map(corpus, output, kwargs)

def repeated_concepts(corpus: str, **kwargs: Any) -> dict[str, Any]:
    from .repeated_concepts import compute_repeated_concepts

    _reject_unknown_kwargs("repeated_concepts", kwargs, _REPEATED_CONCEPTS_KWARGS)
    error, _code, context = _sections_index_context(corpus, scope="sections", **_index_context_kwargs(kwargs))
    if error is not None:
        return error
    assert context is not None
    args = _ns(
        threshold=float(kwargs.get("threshold") or 0.80),
        top=int(kwargs.get("top") or 30),
        min_tokens=int(kwargs.get("min_tokens") or 30),
        min_files=int(kwargs.get("min_files") or 2),
        min_sections=int(kwargs.get("min_sections") or 2),
        top_members=int(kwargs.get("top_members") or 5),
        embed_model=context.selected_model,
        embedding_api_url=context.embedding_api_url,
        path_include=context.include_patterns,
        path_exclude=context.exclude_patterns,
    )
    output = compute_repeated_concepts(context.corpus_root, context.conn, context.map_data, context.index_stats, args)
    if output is None:
        return _exit({"empty": True, "reason": "Need at least 2 chunks to compare."}, 1)
    if bool(kwargs.get("expanded", False)):
        output["expanded"] = True
        output["map_only"] = False
        output["content_included"] = False
        return output
    return _concept_map(corpus, output, kwargs)

def audit(corpus: str, **kwargs: Any) -> dict[str, Any]:
    from .audit import audit_payload

    _reject_unknown_kwargs("audit", kwargs, _AUDIT_KWARGS)
    error, _code, context = _sections_index_context(corpus, scope="sections", **_index_context_kwargs(kwargs))
    if error is not None:
        return error
    assert context is not None
    args = _ns(
        threshold_smear=float(kwargs.get("threshold_smear") or 0.85),
        threshold_drift=float(kwargs.get("threshold_drift") or 0.65),
        threshold_inter=float(kwargs.get("threshold_inter") or 0.40),
        threshold_template=float(kwargs.get("threshold_template") or 0.70),
        threshold_heading_diversity=float(kwargs.get("threshold_heading_diversity") or 0.85),
        min_files_in_family=int(kwargs.get("min_files_in_family") or 3),
        min_sections_per_file=int(kwargs.get("min_sections_per_file") or 5),
        max_concepts=int(kwargs.get("max_concepts") or 10),
        cluster_k=int(kwargs.get("cluster_k") or 8),
        discovery_gap_warn=float(kwargs.get("discovery_gap_warn") or 0.25),
        discovery_gap_crit=float(kwargs.get("discovery_gap_crit") or 0.50),
        embed_model=context.selected_model,
        embedding_api_url=context.embedding_api_url,
        cache_dir=kwargs.get("cache_dir"),
        path_include=context.include_patterns,
        path_exclude=context.exclude_patterns,
    )
    output = audit_payload(
        corpus_root=context.corpus_root,
        conn=context.conn,
        map_data=context.map_data,
        sections=context.items,
        index_stats=context.index_stats,
        args=args,
    )
    if bool(kwargs.get("expanded", False)):
        output["expanded"] = True
        output["map_only"] = False
        output["content_included"] = False
        return output
    return _audit_map(corpus, output, kwargs)
