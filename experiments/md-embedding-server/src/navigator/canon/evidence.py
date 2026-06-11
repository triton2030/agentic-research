from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from navigator.config import CanonConfig

AUTHORITY = "authority"
DEPENDENT_CONTEXT = "dependent_context"
PARKING = "parking"
UNKNOWN = "unknown"

ROLE_KEYS = {
    AUTHORITY: "authority_quotes",
    DEPENDENT_CONTEXT: "dependent_quotes",
    PARKING: "parking_quotes",
}

DEFAULT_EVIDENCE_EXCLUDES = (
    "AGENTS.md",
    "**/AGENTS.md",
    "CLAUDE.md",
    "**/CLAUDE.md",
)


@dataclass(frozen=True)
class EvidenceScope:
    authority_include: list[str]
    discovery_include: list[str] | None
    discovery_enabled: bool
    default_scope_applied: bool
    has_canon_config: bool
    path_exclude: list[str]
    policy: str


def list_filter(value: Iterable[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return [str(item) for item in value if str(item)]


def build_evidence_scope(
    cfg: CanonConfig,
    *,
    source_rel: str,
    path_include: Iterable[str] | str | None,
    path_exclude: Iterable[str] | str | None,
) -> EvidenceScope:
    explicit_include = list_filter(path_include)
    exclude = [*list_filter(path_exclude), source_rel, *DEFAULT_EVIDENCE_EXCLUDES]
    has_config = bool(cfg.root or cfg.future)
    if explicit_include:
        return EvidenceScope(
            authority_include=explicit_include,
            discovery_include=None,
            discovery_enabled=False,
            default_scope_applied=False,
            has_canon_config=has_config,
            path_exclude=exclude,
            policy="explicit_authority_scope",
        )
    if has_config:
        return EvidenceScope(
            authority_include=[*cfg.root, *cfg.future],
            discovery_include=None,
            discovery_enabled=True,
            default_scope_applied=True,
            has_canon_config=True,
            path_exclude=exclude,
            policy="authority_first_broad_discovery",
        )
    return EvidenceScope(
        authority_include=[],
        discovery_include=None,
        discovery_enabled=False,
        default_scope_applied=False,
        has_canon_config=False,
        path_exclude=exclude,
        policy="unscoped_no_canon_config",
    )


def evidence_role_for_zone(zone: str | None, *, has_canon_config: bool) -> str:
    if zone == "canon":
        return AUTHORITY
    if zone == "product":
        return DEPENDENT_CONTEXT
    if zone == "future":
        return PARKING
    return UNKNOWN if has_canon_config else AUTHORITY


def annotate_rows(
    rows: list[dict[str, Any]],
    zone_resolver,
    *,
    has_canon_config: bool,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        rel = str(row.get("relative_path") or "")
        zone, badge = zone_resolver(rel)
        item = dict(row)
        item["zone"] = zone
        item["badge"] = badge
        item["evidence_role"] = evidence_role_for_zone(zone, has_canon_config=has_canon_config)
        out.append(item)
    return out


def role_buckets(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets = {AUTHORITY: [], DEPENDENT_CONTEXT: [], PARKING: []}
    for row in rows:
        role = str(row.get("evidence_role") or UNKNOWN)
        if role in buckets:
            buckets[role].append(row)
    return buckets


def merge_buckets(*items: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    merged = {AUTHORITY: [], DEPENDENT_CONTEXT: [], PARKING: []}
    seen: set[tuple[str, Any]] = set()
    for item in items:
        for role, rows in item.items():
            if role not in merged:
                continue
            for row in rows:
                key = (str(row.get("relative_path") or ""), row.get("start_line"))
                if key in seen:
                    continue
                seen.add(key)
                merged[role].append(row)
    return merged
