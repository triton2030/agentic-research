"""Compact human-readable rendering for `--brief` output.

Mirror of the `_human` payload-key pattern but centralised: handlers stay
unchanged and renderers live in one module. Each renderer takes the raw
payload returned by the handler and produces one string. Falls back to JSON
when no renderer is registered for a tool.
"""

from __future__ import annotations

from typing import Any


def render(tool_name: str | None, payload: Any) -> str | None:
    if not tool_name or not isinstance(payload, dict):
        return None
    renderer = _RENDERERS.get(tool_name)
    if renderer is None:
        return None
    try:
        return renderer(payload)
    except (KeyError, TypeError, ValueError):
        return None


def _trim(value: Any, limit: int) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", " ").replace("\r", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _render_search(payload: dict[str, Any]) -> str:
    results = payload.get("results", [])
    if not results:
        return "(no results)"
    lines = []
    for row in results:
        section_id = row.get("section_id", "?")
        path = row.get("relative_path", "?")
        line = row.get("start_line", 0)
        heading = row.get("heading_chain") or row.get("heading_text") or ""
        score = row.get("rerank_score") if row.get("rerank_score") is not None else row.get("rrf_score", 0.0)
        snippet = row.get("snippet") or row.get("body") or ""
        lines.append(
            f"[{section_id}] {path}:L{line} | {_trim(heading, 60)} | "
            f"score={float(score):.3f} | {_trim(snippet, 80)}"
        )
    return "\n".join(lines)


def _render_overlaps(payload: dict[str, Any]) -> str:
    pairs = payload.get("pairs", [])
    if not pairs:
        return "(no overlap pairs above threshold)"
    lines = []
    for pair in pairs:
        sim = pair.get("similarity", 0.0)
        a = pair.get("a", {})
        b = pair.get("b", {})
        lines.append(
            f"sim={float(sim):.3f} | {a.get('relative_path','?')}:L{a.get('start_line',0)}"
            f" ↔ {b.get('relative_path','?')}:L{b.get('start_line',0)}"
            f" | {_trim(a.get('heading_text',''), 50)}"
        )
    return "\n".join(lines)


def _render_concepts(payload: dict[str, Any]) -> str:
    concepts = payload.get("concepts", [])
    if not concepts:
        return "(no recurring concepts)"
    lines = []
    for concept in concepts:
        label = concept.get("label", "?")
        unique_files = concept.get("unique_files", 0)
        section_count = concept.get("section_count", 0)
        cohesion = concept.get("mean_cohesion", 0.0)
        medoid = concept.get("medoid", {}).get("relative_path", "?")
        lines.append(
            f"files={unique_files:>3} sections={section_count:>3} cohesion={float(cohesion):.2f}"
            f" | {_trim(label, 60)} | medoid: {medoid}"
        )
    return "\n".join(lines)


def _render_extract(payload: dict[str, Any]) -> str:
    files = payload.get("files", [])
    headings = payload.get("headings", [])
    missing_h = payload.get("missing_heading_ids") or []
    missing_f = payload.get("missing_file_ids") or []
    lines: list[str] = []
    if missing_h:
        lines.append("MISSING headings: " + ", ".join(str(x) for x in missing_h))
    if missing_f:
        lines.append("MISSING files: " + ", ".join(str(x) for x in missing_f))
    if files:
        lines.append("# Files")
        for item in files:
            desc = item.get("description") or "TODO description"
            lines.append(f"[{item.get('id','?')}] {item.get('relative_path','?')} — {_trim(desc, 60)}")
    if headings:
        lines.append("# Headings")
        for heading in headings:
            content = heading.get("content")
            lines.append(
                f"[{heading.get('id','?')}] {heading.get('relative_path','?')}"
                f":L{heading.get('line',0)} | {_trim(heading.get('text',''), 70)}"
            )
            if isinstance(content, str) and content.strip():
                lines.append("```")
                lines.append(content)
                lines.append("```")
    if not lines:
        return "(no items selected)"
    return "\n".join(lines)


def _render_refactor_candidates(payload: dict[str, Any]) -> str:
    proposals = payload.get("proposals", [])
    if not proposals:
        return "(no refactor proposals)"
    lines = []
    for proposal in proposals:
        kind = proposal.get("kind", "?")
        target = proposal.get("target", "?")
        confidence = proposal.get("confidence", 0.0)
        why = proposal.get("why", "")
        lines.append(f"{kind:>10} | conf={float(confidence):.2f} | {target} | {_trim(why, 60)}")
    return "\n".join(lines)


_RENDERERS = {
    "md_search": _render_search,
    "md_overlaps": _render_overlaps,
    "md_repeated_concepts": _render_concepts,
    "md_extract": _render_extract,
    "md_refactor_candidates": _render_refactor_candidates,
}
