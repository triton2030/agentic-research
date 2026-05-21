from __future__ import annotations

from pathlib import Path
from typing import Any

from .originality import originality_for_section
from .owner_detector import owner_candidates
from .section_profile import profile_unprofiled_sections


def refactor_candidates(
    conn,
    corpus_root: Path | None = None,
    top: int = 10,
    uniqueness_threshold: float = 0.35,
    owner_confidence_threshold: float = 0.45,
) -> dict[str, Any]:
    profile_unprofiled_sections(conn, corpus_root=corpus_root)
    rows = conn.execute(
        "SELECT section_id, relative_path, start_line, heading_text, profile_type, "
        "profile_subject, profile_confidence FROM sections WHERE scope='sections' "
        "AND profile_type IN ('uses','example','external-citation') "
        "ORDER BY token_count DESC LIMIT ?",
        (max(top * 6, top),),
    ).fetchall()

    proposals: list[dict[str, Any]] = []
    for row in rows:
        section_id = row[0]
        originality = originality_for_section(conn, section_id)
        uniqueness = float(originality["uniqueness"])
        if uniqueness >= uniqueness_threshold:
            continue
        owners = owner_candidates(conn, corpus_root=corpus_root, section_id=section_id, limit=3)
        if not owners:
            continue
        target = owners[0]
        if float(target["score"]) < owner_confidence_threshold:
            continue
        target_type = target["profile"]["type"]
        proposal_type = "replace_with_wikilink" if target_type in {"definition", "rule"} else "merge_with_X"
        proposals.append(
            {
                "proposal_type": proposal_type,
                "affected_section": {
                    "path": row[1],
                    "heading_id": section_id,
                    "line_range": [row[2], None],
                    "heading_text": row[3],
                    "profile": {
                        "type": row[4],
                        "subject": row[5],
                        "confidence": row[6],
                    },
                },
                "target_owner": {
                    "path": target["relative_path"],
                    "heading_id": target["section_id"],
                    "heading_text": target["heading_text"],
                    "profile": target["profile"],
                },
                "evidence": {
                    "cosine": target["evidence"].get("cosine_similarity"),
                    "uniqueness": uniqueness,
                    "owner_composite_score": target["score"],
                    "in_degree_target": target["evidence"].get("in_degree"),
                    "pagerank_target": target["evidence"].get("pagerank"),
                    "centrality_target": target["evidence"].get("centrality"),
                    "profile": {"type": row[4], "confidence": row[6]},
                    "owner_evidence": target["evidence"],
                    "originality": originality,
                },
                "confidence": round(min(1.0, float(target["score"])), 3),
                "why": (
                    f"Section is type={row[4]}, low uniqueness ({uniqueness:.2f}) "
                    f"suggests duplicate/context material. Best owner candidate "
                    f"{target['relative_path']} has score {target['score']:.2f}."
                ),
                "no_automation": True,
            }
        )
        if len(proposals) >= top:
            break

    proposals.sort(key=lambda item: -float(item["confidence"]))
    return {
        "proposals": proposals[:top],
        "method": "section_profile_plus_embedding_originality_plus_graph_owner_score",
        "thresholds": {
            "uniqueness": uniqueness_threshold,
            "owner_confidence": owner_confidence_threshold,
        },
        "no_automation": True,
    }
