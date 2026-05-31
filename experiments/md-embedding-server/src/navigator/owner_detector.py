from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .importance import importance_rows
from .originality import nearest_neighbors
from .section_profile import classify_section_heuristic

OWNER_TYPES = {"definition", "rule", "decision"}


def _section_text(conn, section_id: str) -> str:
    row = conn.execute(
        "SELECT heading_text, heading_chain, body FROM sections "
        "WHERE scope='sections' AND (section_id=? OR rowid=?)",
        (section_id, section_id if str(section_id).isdigit() else -1),
    ).fetchone()
    if row is None:
        raise RuntimeError(f"Section not found: {section_id}")
    return "\n".join(str(part or "") for part in row)


def _fallback_text_candidates(conn, text: str, limit: int) -> list[dict[str, Any]]:
    probe = classify_section_heuristic({"heading_text": "", "heading_chain": "", "body": text})
    probe_terms = {term.lower() for term in probe["mentions"]}
    rows = conn.execute(
        "SELECT section_id, relative_path, start_line, heading_text, profile_type, "
        "profile_subject, profile_owns_terms, profile_mentions, profile_confidence, token_count "
        "FROM sections WHERE scope='sections' AND profile_type IS NOT NULL"
    ).fetchall()
    scored: list[dict[str, Any]] = []
    for row in rows:
        owns_terms = json.loads(row[6] or "[]")
        mentions = json.loads(row[7] or "[]")
        candidate_terms = {term.lower() for term in [*owns_terms, *mentions]}
        overlap = sorted(probe_terms & candidate_terms)
        type_bonus = 0.35 if row[4] in OWNER_TYPES else 0.0
        score = round(type_bonus + min(0.45, len(overlap) * 0.09) + float(row[8] or 0.0) * 0.1, 3)
        if score <= 0.1:
            continue
        scored.append(
            {
                "section_id": row[0],
                "relative_path": row[1],
                "start_line": row[2],
                "heading_text": row[3],
                "profile": {
                    "type": row[4],
                    "subject": row[5],
                    "owns_terms": owns_terms,
                    "mentions": mentions,
                    "confidence": row[8],
                },
                "score": score,
                "evidence": {"term_overlap": overlap, "method": "text_overlap_fallback"},
            }
        )
    scored.sort(key=lambda item: (-item["score"], item["relative_path"], item["start_line"]))
    return scored[:limit]


def owner_candidates(
    conn,
    corpus_root: Path | None = None,
    text: str | None = None,
    section_id: str | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    if text is not None:
        return _fallback_text_candidates(conn, text, limit)
    if not section_id:
        raise RuntimeError("owner-candidates requires text or section_id")

    graph_importance = {
        row["relative_path"]: row
        for row in importance_rows(corpus_root, top=10000)
    } if corpus_root is not None else {}
    neighbors = nearest_neighbors(conn, section_id, top_k=max(limit * 4, 12))
    scored: list[dict[str, Any]] = []
    for item in neighbors:
        profile_type = item.get("profile_type")
        owns_terms = json.loads(item.get("profile_owns_terms") or "[]")
        confidence_prior = float(item.get("profile_confidence") or 0.5)
        imp = graph_importance.get(item["relative_path"], {})
        cosine = float(item["cosine_similarity"])
        is_owner = 1.0 if profile_type == "definition" else 0.65 if profile_type in {"rule", "decision"} else 0.0
        pagerank = min(1.0, float(imp.get("pagerank", 0.0)) * 50)
        in_degree_norm = min(1.0, float(imp.get("in_degree", 0)) / 10.0)
        uniqueness_prior = min(1.0, float(item.get("token_count") or 0) / 2500)
        score = round(
            0.35 * cosine
            + 0.30 * is_owner
            + 0.15 * pagerank
            + 0.10 * in_degree_norm
            + 0.05 * confidence_prior
            + 0.05 * uniqueness_prior,
            3,
        )
        if score <= 0.1:
            continue
        scored.append(
            {
                "section_id": item["section_id"],
                "rowid": item["rowid"],
                "relative_path": item["relative_path"],
                "start_line": item["start_line"],
                "heading_text": item["heading_text"],
                "heading_chain": item["heading_chain"],
                "profile": {
                    "type": profile_type,
                    "subject": item.get("profile_subject"),
                    "owns_terms": owns_terms,
                    "confidence": confidence_prior,
                },
                "score": score,
                "evidence": {
                    "cosine_similarity": cosine,
                    "is_definition_boost": is_owner,
                    "pagerank": round(float(imp.get("pagerank", 0.0)), 4),
                    "centrality": round(float(imp.get("centrality", 0.0)), 4),
                    "in_degree": int(imp.get("in_degree", 0)),
                    "profile_confidence": confidence_prior,
                },
            }
        )
    scored.sort(key=lambda item: (-item["score"], item["relative_path"], item["start_line"]))
    return scored[:limit]
