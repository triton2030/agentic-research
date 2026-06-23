from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from .api_utils import _exit, _read_next
from .link_graph import iter_explicit_link_edges
from .markdown_io import (
    GRAPH_LINK_KEYS,
    approx_tokens,
    collect_headings,
    extract_section_by_anchor,
    iter_markdown,
    markdown_lookup,
    parse_frontmatter,
    relative_path,
    resolve_input_path,
)
from .pick import parse_csv


def add_related_item(
    items: dict[tuple[Path, str | None], dict[str, Any]],
    path: Path,
    root: Path,
    reason: str,
    anchor: str | None = None,
) -> None:
    """Add a related item. With anchor, content is the heading-bounded
    section instead of the whole file; each (path, anchor) tuple is a
    separate item so the same file can contribute multiple sections."""
    resolved = path.resolve()
    key = (resolved, anchor)
    if key not in items:
        text = resolved.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        frontmatter = parse_frontmatter(lines)
        headings = collect_headings(lines, max_level=3)
        title = headings[0]["text"] if headings else ""
        if anchor is not None:
            section = extract_section_by_anchor(resolved, anchor)
            if section is None:
                # Fallback to whole file when anchor doesn't match any heading.
                section = text.strip()
                anchor_status = "anchor-not-found"
            else:
                anchor_status = "section"
            content = section
            tokens = approx_tokens(section)
        else:
            content = text.strip()
            tokens = approx_tokens(text)
            anchor_status = None
        item = {
            "path": str(resolved),
            "relative_path": relative_path(resolved, root),
            "description": frontmatter.get("description", ""),
            "title": title,
            "headings": [
                {"line": h["line"], "level": h["level"], "text": h["text"]}
                for h in headings
            ],
            "reasons": [],
            "tokens": tokens,
            "content": content,
        }
        if anchor is not None:
            item["anchor"] = anchor
            item["anchor_status"] = anchor_status
        items[key] = item
    if reason not in items[key]["reasons"]:
        items[key]["reasons"].append(reason)


def _resolved_explicit_link_targets(
    anchor: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]],
) -> list[Path]:
    resolved_targets: list[Path] = []
    for edge in iter_explicit_link_edges(anchor, scan_root, lookup):
        if edge.target.resolve() != anchor.resolve():
            resolved_targets.append(edge.target)

    seen: set[Path] = set()
    unique: list[Path] = []
    for target in resolved_targets:
        resolved = target.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(target)
    return unique


def _iter_related_link_items(
    anchor: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]],
    include: set[str],
    *,
    anchor_aware: bool,
) -> Iterator[tuple[Path, str, str | None]]:
    for edge in iter_explicit_link_edges(anchor, scan_root, lookup):
        if edge.edge_type in GRAPH_LINK_KEYS:
            if "frontmatter" in include:
                yield edge.target, edge.edge_type, None
            continue
        if edge.edge_type == "wikilink":
            if "wikilinks" in include:
                yield edge.target, "wikilink", edge.anchor if anchor_aware else None
            continue
        if edge.edge_type == "markdown-link" and "markdown-links" in include:
            yield edge.target, "markdown-link", edge.anchor if anchor_aware else None


def _links_to_any_anchor(
    candidate: Path,
    scan_root: Path,
    lookup: dict[str, list[Path]],
    anchor_set: set[Path],
) -> bool:
    for edge in iter_explicit_link_edges(candidate, scan_root, lookup):
        if edge.edge_type in GRAPH_LINK_KEYS:
            continue
        if edge.target.resolve() in anchor_set:
            return True
    return False


def collect_related_items(args) -> dict[str, Any]:
    scan_root = Path(args.scan).expanduser().resolve()
    if not scan_root.exists():
        return _exit({"command": "read-related", "error": "path_not_found", "scan": str(scan_root)}, 2)

    include = parse_csv(args.include)
    if not include:
        include = {"self", "frontmatter", "wikilinks", "markdown-links", "backlinks"}

    anchor_aware = bool(getattr(args, "anchor_aware", False))
    lookup = markdown_lookup(scan_root)
    try:
        anchors = [resolve_input_path(path, scan_root) for path in args.paths]
    except FileNotFoundError as exc:
        return _exit({"command": "read-related", "error": "path_not_found", "detail": str(exc)}, 2)
    anchor_set = {path.resolve() for path in anchors}
    items: dict[tuple[Path, str | None], dict[str, Any]] = {}
    semantic_radius = int(getattr(args, "semantic_radius", 0) or 0)
    if semantic_radius > 0:
        return _exit(
            {
                "command": "read-related",
                "error": "semantic_radius_retired",
                "reason": "read-related is graph/link context only; target-based semantic candidates live in md semantic-neighbors.",
                "anchors": [str(path) for path in anchors],
                "read_next": [
                    _read_next(
                        "md_semantic_neighbors",
                        {
                            "target": str(anchors[0]),
                            "corpus": str(scan_root),
                            "limit": semantic_radius,
                        },
                        "Use the single target-based semantic-neighbors tool for external semantic candidate blocks.",
                    )
                ],
            },
            2,
        )

    for anchor in anchors:
        if "self" in include:
            add_related_item(items, anchor, scan_root, "self")

        for target, reason, target_anchor in _iter_related_link_items(
            anchor,
            scan_root,
            lookup,
            include,
            anchor_aware=anchor_aware,
        ):
            add_related_item(items, target, scan_root, reason, anchor=target_anchor)

    if "backlinks" in include:
        for candidate in iter_markdown(scan_root):
            resolved_candidate = candidate.resolve()
            if resolved_candidate in anchor_set:
                continue
            if _links_to_any_anchor(resolved_candidate, scan_root, lookup, anchor_set):
                add_related_item(items, resolved_candidate, scan_root, "backlink")

    ordered = list(items.values())
    content_included = getattr(args, "mode", "preview") == "full"
    if not content_included:
        for item in ordered:
            preview_text = "\n".join(
                [
                    item.get("description") or "",
                    item.get("title") or "",
                    *[h.get("text", "") for h in item.get("headings", [])],
                ]
            )
            item["tokens"] = approx_tokens(preview_text)
            item.pop("content", None)
    reason_rank = {
        "self": 0,
        "depends-on": 1,
        "wikilink": 3,
        "markdown-link": 4,
        "backlink": 5,
    }
    ordered.sort(
        key=lambda item: (
            min(reason_rank.get(reason, 9) for reason in item["reasons"]),
            item["relative_path"],
        )
    )

    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    running = 0
    budget = int(args.token_budget)
    for item in ordered:
        cost = int(item.get("tokens", 0))
        if budget <= 0 or running + cost <= budget or (not kept and "self" in item["reasons"]):
            kept.append(item)
            running += cost
        else:
            dropped.append(
                {
                    "path": item["path"],
                    "relative_path": item["relative_path"],
                    "reasons": item["reasons"],
                    "tokens": cost,
                }
            )

    check_links = bool(getattr(args, "check_links", False))
    semantic_neighbors: list[dict[str, Any]] = []
    suspicious_links: list[dict[str, Any]] = []
    semantic_status = "not_requested"

    if check_links:
        # Local-import: these helpers pull in sqlite_vec, which is a heavy
        # uv-shebang dep. read-related stays import-light unless one of
        # the semantic flags is on.
        from .semantic_neighbors import _check_explicit_link_coherence
        from .status_core import find_corpus_root_for

        corpus_root = find_corpus_root_for(anchors[0])
        if corpus_root is not None:
            semantic_status = "ok"
            threshold = float(getattr(args, "link_distance_threshold", 0.4))
            for anchor in anchors:
                suspicious_links.extend(
                    _check_explicit_link_coherence(
                        corpus_root=corpus_root,
                        anchor=anchor,
                        linked_targets=_resolved_explicit_link_targets(anchor, scan_root, lookup),
                        threshold=threshold,
                    )
                )
        else:
            semantic_status = "no_index"

    return {
        "root": str(scan_root),
        "anchors": [str(path) for path in anchors],
        "include": sorted(include),
        "mode": getattr(args, "mode", "preview"),
        "expanded": bool(getattr(args, "expanded", content_included)),
        "map_only": not content_included,
        "content_included": content_included,
        "token_budget": budget,
        "token_total": running,
        "items": kept,
        "dropped_by_budget": dropped,
        "semantic_status": semantic_status,
        "semantic_neighbors": semantic_neighbors,
        "suspicious_links": suspicious_links,
        "read_next": [] if content_included else [
            {
                "tool": "md_read_related",
                "args": {
                    "paths": [str(path) for path in anchors],
                    "scan": str(scan_root),
                    "expanded": True,
                },
                "reason": "Read selected related context with content bodies.",
            }
        ],
        "note": "Reading context only; graph obligations belong to 1md-graph.",
    }


def render_related_packet(packet: dict[str, Any]) -> str:
    lines = [
        "# Markdown related reading",
        "",
        f"Root: {packet['root']}",
        f"Anchors: {', '.join(packet['anchors'])}",
        f"Tokens (approx): {packet['token_total']}"
        + (f" / {packet['token_budget']} budget" if packet["token_budget"] else ""),
        "Reading context only; graph obligations stay in `1md-graph`.",
        "",
    ]
    if packet["dropped_by_budget"]:
        lines.append("## Dropped by token budget")
        for item in packet["dropped_by_budget"]:
            lines.append(
                f"- {item['relative_path']} ({','.join(item['reasons'])}, {item['tokens']}t)"
            )
        lines.append("")

    lines.append("## Files")
    if not packet["items"]:
        lines.append("(no related Markdown files found)")
        return "\n".join(lines).rstrip() + "\n"

    for index, item in enumerate(packet["items"], start=1):
        desc = item["description"] or "TODO description"
        title = f" | title: {item['title']}" if item.get("title") else ""
        lines.append(
            f"{index}. {item['relative_path']} - {desc}{title} "
            f"| reasons: {','.join(item['reasons'])} | {item['tokens']}t"
        )
        if item.get("content"):
            lines.append("")
            lines.append("```md")
            lines.append(item["content"])
            lines.append("```")
            lines.append("")

    semantic = packet.get("semantic_neighbors") or []
    if semantic:
        lines.append("")
        lines.append("## Semantic neighbors (not linked yet)")
        lines.append(
            "Dense-similarity candidates that are NOT in any explicit link. "
            "Hint for `1ia-audit` and authoring; not graph obligations."
        )
        for n in semantic:
            lines.append(
                f"- {n['relative_path']} [{n['section_id']}] "
                f"{n.get('heading_chain', '')} | distance={n['distance']:.3f} "
                f"| matched anchor section: {n['matched_anchor_section']}"
            )

    suspicious = packet.get("suspicious_links") or []
    if suspicious:
        lines.append("")
        lines.append("## Suspicious explicit links (distance > threshold)")
        lines.append(
            "Linked targets that look semantically far from this file. "
            "Owner of the verdict is `1md-graph` — surface only."
        )
        for s in suspicious:
            lines.append(
                f"- {s['target_relative_path']} | distance={s['best_distance']:.3f} "
                f"| anchor [{s['anchor_section']}] ↔ target [{s['target_section']}]"
            )

    return "\n".join(lines).rstrip() + "\n"
