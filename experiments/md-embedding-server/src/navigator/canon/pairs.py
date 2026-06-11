from __future__ import annotations

from typing import Any, Callable

from .claims import Claim
from .evidence import AUTHORITY, DEPENDENT_CONTEXT, PARKING, ROLE_KEYS, role_buckets
from .retrieval import flag_row

QUOTE_CHARS = 700


def _quote(row: dict[str, Any], *, expanded: bool) -> str:
    text = str(row.get("body") or row.get("snippet") or "")
    if not expanded:
        text = str(row.get("snippet") or text)
    text = " ".join(text.split())
    return text[:QUOTE_CHARS] if expanded else text


def _quote_row(
    row: dict[str, Any],
    zone_resolver: Callable[[str], tuple[str | None, str | None]],
    *,
    expanded: bool,
) -> dict[str, Any]:
    rel = str(row.get("relative_path") or "")
    zone = row.get("zone")
    badge = row.get("badge")
    if not isinstance(zone, str) and not isinstance(badge, str):
        zone, badge = zone_resolver(rel)
    role = str(row.get("evidence_role") or "")
    item = {
        "quote": _quote(row, expanded=expanded),
        "relative_path": rel,
        "start_line": row.get("start_line"),
        "heading_chain": row.get("heading_chain"),
        "zone": zone,
        "badge": badge,
        "evidence_role": role,
        "rrf_score": row.get("rrf_score"),
        "rerank_score": row.get("rerank_score"),
        "fields_hit": row.get("fields_hit") or [],
    }
    flags = flag_row({**row, "zone": zone})
    if role == DEPENDENT_CONTEXT:
        flags.append("surface_projection")
    if role == PARKING:
        flags.extend(["future_only", "stage_misfit"])
    item["flags"] = sorted(set(flags))
    return item


def _normalize_results(rows: Any) -> dict[str, list[dict[str, Any]]]:
    if isinstance(rows, dict):
        return {
            AUTHORITY: list(rows.get(AUTHORITY) or []),
            DEPENDENT_CONTEXT: list(rows.get(DEPENDENT_CONTEXT) or []),
            PARKING: list(rows.get(PARKING) or []),
        }
    if isinstance(rows, list):
        return role_buckets(rows)
    return {AUTHORITY: [], DEPENDENT_CONTEXT: [], PARKING: []}


def build_pairs(
    claims: list[Claim],
    retrieval_results: list[Any],
    zone_resolver: Callable[[str], tuple[str | None, str | None]],
    *,
    top_quotes: int = 3,
    expanded: bool = False,
) -> tuple[list[dict[str, Any]], list[str], str]:
    pairs: list[dict[str, Any]] = []
    quality_flags: list[str] = []
    for claim, rows in zip(claims, retrieval_results):
        buckets = _normalize_results(rows)
        quote_buckets = {
            role: [
                _quote_row(row, zone_resolver, expanded=expanded)
                for row in buckets.get(role, [])[:top_quotes]
            ]
            for role in ROLE_KEYS
        }
        quotes = [
            *quote_buckets[AUTHORITY],
            *quote_buckets[DEPENDENT_CONTEXT],
            *quote_buckets[PARKING],
        ][:top_quotes]
        flags: list[str] = []
        if not quote_buckets[AUTHORITY]:
            flags.append("no_owner_found")
            quality_flags.append("no_owner_found")
        if quotes and all("low_score" in (quote.get("flags") or []) for quote in quotes):
            flags.append("low_score")
            quality_flags.append("low_score")
        if quote_buckets[DEPENDENT_CONTEXT]:
            flags.append("surface_projection")
            quality_flags.append("surface_projection")
        if quote_buckets[PARKING]:
            flags.append("future_zone_hit")
            quality_flags.append("future_zone_hit")
        pairs.append(
            {
                "claim": {
                    "text": claim.text,
                    "line": claim.line,
                    "heading_chain": claim.heading_chain,
                    "score": claim.score,
                    "signals": list(claim.signals),
                },
                "authority_quotes": quote_buckets[AUTHORITY],
                "dependent_quotes": quote_buckets[DEPENDENT_CONTEXT],
                "parking_quotes": quote_buckets[PARKING],
                "quotes": quotes,
                "flags": sorted(set(flags)),
            }
        )
    advice = _advice(sorted(set(quality_flags)))
    return pairs, sorted(set(quality_flags)), advice


def _advice(flags: list[str]) -> str:
    if "no_owner_found" in flags:
        return "Some claims have no owner quote; check wording against the canon root before editing."
    if "future_zone_hit" in flags:
        return "A claim is closest to future-layer evidence; do not promote future language into current canon without an ADR."
    if "low_score" in flags:
        return "Evidence is weak; repeat with a narrower path_include or inspect owners manually."
    return "Read the top quotes before changing the source claim; canon-check gathers evidence, not verdicts."
