from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from navigator.filters import path_matches_any

from .evidence import (
    AUTHORITY,
    DEPENDENT_CONTEXT,
    PARKING,
    annotate_rows,
    build_evidence_scope,
    merge_buckets,
    role_buckets,
)
from .query_pack import build_query_pack
from .retrieval import apply_graph_bonus, apply_rerank, fused_search, open_retrieval_context
from .zones import build_zone_map, load_zone_config, make_zone_resolver

MODES = ("A", "B", "C", "D")
MODE_LABELS = {
    "A": "single",
    "B": "pack",
    "C": "pack-graph",
    "D": "pack-graph-rerank",
}


@dataclass(frozen=True)
class EvalCase:
    id: str
    source_file: str
    claim_text: str
    expected_owner_file: str
    expected_line_hint: int | None
    kind: str
    owner_role: str
    why_this_owner: str
    source_last_verified: str
    expected_owner_glob: str | None


@dataclass(frozen=True)
class CaseResult:
    case: EvalCase
    mode: str
    rows: list[dict]
    elapsed_ms: int
    buckets: dict[str, list[dict]] | None = None
    queries_run: int = 0
    scope_policy: str = ""


def load_cases(path: str | Path) -> list[EvalCase]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("canon eval cases must be a JSON list")
    cases: list[EvalCase] = []
    required = {"id", "source_file", "claim_text", "expected_owner_file", "kind"}
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"case {idx} must be an object")
        missing = required - set(item)
        if missing:
            raise ValueError(f"case {idx} missing keys: {sorted(missing)}")
        kind = str(item["kind"])
        if kind not in {"conflict", "clean"}:
            raise ValueError(f"case {item['id']} kind must be conflict|clean")
        hint = item.get("expected_line_hint")
        expected_owner = str(item["expected_owner_file"])
        cases.append(
            EvalCase(
                id=str(item["id"]),
                source_file=str(item["source_file"]),
                claim_text=str(item["claim_text"]),
                expected_owner_file=expected_owner,
                expected_line_hint=int(hint) if hint is not None else None,
                kind=kind,
                owner_role=str(item.get("owner_role") or _default_owner_role(expected_owner)),
                why_this_owner=str(item.get("why_this_owner") or "legacy_probe_case"),
                source_last_verified=str(item.get("source_last_verified") or ""),
                expected_owner_glob=(
                    str(item["expected_owner_glob"])
                    if item.get("expected_owner_glob") is not None
                    else None
                ),
            )
        )
    return cases


def run_case(corpus_root: Path, case: EvalCase, mode: str, *, limit: int = 10) -> CaseResult:
    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode}")
    queries = [case.claim_text] if mode == "A" else build_query_pack(case.claim_text)
    cfg = load_zone_config(corpus_root)
    scope = build_evidence_scope(
        cfg,
        source_rel=case.source_file,
        path_include=None,
        path_exclude=None,
    )
    error, _code, ctx = open_retrieval_context(
        str(corpus_root),
        path_include=scope.authority_include,
        path_exclude=scope.path_exclude,
    )
    if error is not None:
        raise RuntimeError(str(error))
    assert ctx is not None
    discovery_ctx = None
    if scope.discovery_enabled:
        error, _code, discovery_ctx = open_retrieval_context(
            str(corpus_root),
            path_include=scope.discovery_include,
            path_exclude=scope.path_exclude,
        )
        if error is not None:
            raise RuntimeError(str(error))
    started = perf_counter()
    zone_resolver = make_zone_resolver(corpus_root, build_zone_map(corpus_root), cfg)
    authority_rows, _rerank_applied = _search_rows(ctx, corpus_root, case, queries, mode, limit=limit)
    authority_buckets = role_buckets(
        annotate_rows(authority_rows, zone_resolver, has_canon_config=scope.has_canon_config)
    )
    discovery_buckets = {AUTHORITY: [], DEPENDENT_CONTEXT: [], PARKING: []}
    discovery_queries = 0
    if discovery_ctx is not None:
        discovery_rows, _discovery_rerank = _search_rows(
            discovery_ctx,
            corpus_root,
            case,
            queries,
            mode,
            limit=max(limit * 3, 20),
        )
        discovery_queries = len(queries)
        discovery_buckets = role_buckets(
            annotate_rows(discovery_rows, zone_resolver, has_canon_config=scope.has_canon_config)
        )
        discovery_buckets[AUTHORITY] = []
        discovery_buckets[PARKING] = []
    buckets = merge_buckets(authority_buckets, discovery_buckets)
    rows = [*buckets[AUTHORITY], *buckets[DEPENDENT_CONTEXT], *buckets[PARKING]]
    return CaseResult(
        case=case,
        mode=mode,
        rows=rows[:limit],
        elapsed_ms=int((perf_counter() - started) * 1000),
        buckets=buckets,
        queries_run=len(queries) + discovery_queries,
        scope_policy=scope.policy,
    )


def _search_rows(
    ctx,
    corpus_root: Path,
    case: EvalCase,
    queries: list[str],
    mode: str,
    *,
    limit: int,
) -> tuple[list[dict], bool]:
    rows = fused_search(ctx, queries, limit=limit, candidates=max(80, limit * 8))
    if mode in {"C", "D"}:
        rows = apply_graph_bonus(corpus_root, corpus_root / case.source_file, rows)
    rerank_applied = False
    if mode == "D":
        rows, rerank_applied = apply_rerank(case.claim_text, rows, corpus_root=corpus_root)
    return rows[:limit], rerank_applied


def owner_rank(result: CaseResult) -> int | None:
    for idx, row in enumerate(_role_rows(result), start=1):
        if _matches_expected_owner(result.case, str(row.get("relative_path") or "")):
            return idx
    return None


def owner_hit_at(result: CaseResult, k: int) -> bool:
    rank = owner_rank(result)
    return rank is not None and rank <= k


def false_alarm(result: CaseResult) -> bool:
    if result.case.kind != "clean":
        return False
    return not owner_hit_at(result, 5)


def summarize(results: list[CaseResult]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for mode in MODES:
        rows = [r for r in results if r.mode == mode]
        conflicts = [r for r in rows if r.case.kind == "conflict"]
        clean = [r for r in rows if r.case.kind == "clean"]
        summary[mode] = {
            "owner_hit_at_5": _ratio(conflicts, lambda r: owner_hit_at(r, 5)),
            "owner_hit_at_10": _ratio(conflicts, lambda r: owner_hit_at(r, 10)),
            "false_alarm": _ratio(clean, false_alarm),
            "median_ms": statistics.median([r.elapsed_ms for r in rows]) if rows else 0,
            "p95_ms": _p95([r.elapsed_ms for r in rows]),
            "median_queries": statistics.median([r.queries_run for r in rows]) if rows else 0,
            "agents_excluded": _ratio(rows, no_instruction_quotes),
            "role_hit_at_10": _ratio(conflicts + clean, lambda r: owner_hit_at(r, 10)),
        }
    return summary


def render_markdown(results: list[CaseResult], *, command: str | None = None) -> str:
    summary = summarize(results)
    lines = [
        "# Canon Eval",
        "",
        "## Acceptance Matrix",
        "",
        "- Default mode may change only if conflict owner-hit@10 >= 0.80 and clean false-alarm == 0.",
        "- Must-pass scenarios: owner role hit, instruction files excluded, future evidence stays parking.",
        "- Latency is evidence: total seconds, median/p95 ms, and query counts are reported before default changes.",
        "",
    ]
    if command:
        lines.extend(["## Command", "", f"`{command}`", ""])
    lines.extend([
        "## Summary",
        "",
        "| Mode | owner-hit@5 | owner-hit@10 | clean-miss | role-hit@10 | AGENTS/CLAUDE excluded | median ms | p95 ms | median queries |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for mode in MODES:
        row = summary.get(mode, {})
        lines.append(
            f"| {mode} ({MODE_LABELS[mode]}) | {row.get('owner_hit_at_5', 0):.2f} | "
            f"{row.get('owner_hit_at_10', 0):.2f} | {row.get('false_alarm', 0):.2f} | "
            f"{row.get('role_hit_at_10', 0):.2f} | {row.get('agents_excluded', 0):.2f} | "
            f"{row.get('median_ms', 0):.0f} | {row.get('p95_ms', 0):.0f} | "
            f"{row.get('median_queries', 0):.0f} |"
        )
    lines.extend(["", "## Must-Pass Scenarios", "", "| Scenario | Pass |", "|---|---:|"])
    for key, passed in _must_pass(results).items():
        lines.append(f"| {key} | {'yes' if passed else 'no'} |")
    lines.extend([
        "",
        "## Cases",
        "",
        "| Case | Mode | Expected role | Expected rank | Top authority | Top dependent | Top parking | ms | queries |",
        "|---|---|---|---:|---|---|---|---:|---:|",
    ])
    for result in results:
        buckets = result.buckets or {}
        rank = owner_rank(result)
        lines.append(
            f"| {result.case.id} | {result.mode} | {result.case.owner_role} | {rank or ''} | "
            f"{_top_path(buckets.get(AUTHORITY) or result.rows)} | "
            f"{_top_path(buckets.get(DEPENDENT_CONTEXT) or [])} | "
            f"{_top_path(buckets.get(PARKING) or [])} | {result.elapsed_ms} | {result.queries_run} |"
        )
    return "\n".join(lines) + "\n"


def _default_owner_role(expected_owner_file: str) -> str:
    if expected_owner_file.startswith("05_"):
        return PARKING
    return AUTHORITY


def _role_rows(result: CaseResult) -> list[dict]:
    if result.buckets and result.case.owner_role in result.buckets:
        return result.buckets[result.case.owner_role]
    return result.rows


def _matches_expected_owner(case: EvalCase, rel_path: str) -> bool:
    if rel_path == case.expected_owner_file:
        return True
    if case.expected_owner_glob:
        return path_matches_any(rel_path, [case.expected_owner_glob])
    return False


def _ratio(rows: list[CaseResult], pred: Callable[[CaseResult], bool]) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if pred(row)) / len(rows)


def _p95(values: list[int]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return float(values[0])
    return float(statistics.quantiles(values, n=20)[18])


def no_instruction_quotes(result: CaseResult) -> bool:
    return all(
        not str(row.get("relative_path") or "").endswith(("AGENTS.md", "CLAUDE.md"))
        for row in result.rows
    )


def _must_pass(results: list[CaseResult]) -> dict[str, bool]:
    conflicts = [r for r in results if r.case.kind == "conflict"]
    future = [r for r in results if r.case.owner_role == PARKING]
    return {
        "conflict_owner_role_hit_at_10": all(owner_hit_at(r, 10) for r in conflicts),
        "instruction_files_excluded": all(no_instruction_quotes(r) for r in results),
        "future_cases_stay_parking": all(owner_hit_at(r, 10) for r in future),
    }


def _top_path(rows: list[dict]) -> str:
    return str(rows[0].get("relative_path") or "") if rows else ""
