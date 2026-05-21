from __future__ import annotations

from pathlib import Path
from typing import Any

from .markdown_io import (
    GRAPH_LINK_KEYS,
    approx_tokens,
    collect_headings,
    extract_section_by_anchor,
    iter_markdown,
    markdown_links_from_text,
    markdown_links_with_anchors_from_text,
    markdown_lookup,
    normalize_frontmatter_links,
    parse_frontmatter,
    relative_path,
    resolve_input_path,
    resolve_markdown_target,
    wikilinks_from_text,
    wikilinks_with_anchors_from_text,
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
        headings = collect_headings(lines, max_level=1)
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


def collect_related_items(args) -> dict[str, Any]:
    scan_root = Path(args.scan).expanduser().resolve()
    if not scan_root.exists():
        raise SystemExit(f"Scan root does not exist: {scan_root}")

    include = parse_csv(args.include)
    if not include:
        include = {"self", "frontmatter", "wikilinks", "markdown-links", "backlinks"}

    anchor_aware = bool(getattr(args, "anchor_aware", False))
    lookup = markdown_lookup(scan_root)
    anchors = [resolve_input_path(path, scan_root) for path in args.paths]
    anchor_set = {path.resolve() for path in anchors}
    items: dict[tuple[Path, str | None], dict[str, Any]] = {}

    for anchor in anchors:
        text = anchor.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        frontmatter = parse_frontmatter(lines)

        if "self" in include:
            add_related_item(items, anchor, scan_root, "self")

        if "frontmatter" in include:
            for key in GRAPH_LINK_KEYS:
                for target in normalize_frontmatter_links(frontmatter.get(key)):
                    resolved = resolve_markdown_target(target, anchor, scan_root, lookup)
                    if resolved:
                        add_related_item(items, resolved, scan_root, key)

        if "wikilinks" in include:
            if anchor_aware:
                for target, link_anchor in wikilinks_with_anchors_from_text(text):
                    resolved = resolve_markdown_target(target, anchor, scan_root, lookup)
                    if resolved:
                        add_related_item(items, resolved, scan_root, "wikilink", anchor=link_anchor)
            else:
                for target in wikilinks_from_text(text):
                    resolved = resolve_markdown_target(target, anchor, scan_root, lookup)
                    if resolved:
                        add_related_item(items, resolved, scan_root, "wikilink")

        if "markdown-links" in include:
            if anchor_aware:
                for target, link_anchor in markdown_links_with_anchors_from_text(text):
                    resolved = resolve_markdown_target(target, anchor, scan_root, lookup)
                    if resolved:
                        add_related_item(items, resolved, scan_root, "markdown-link", anchor=link_anchor)
            else:
                for target in markdown_links_from_text(text):
                    resolved = resolve_markdown_target(target, anchor, scan_root, lookup)
                    if resolved:
                        add_related_item(items, resolved, scan_root, "markdown-link")

    if "backlinks" in include:
        for candidate in iter_markdown(scan_root):
            resolved_candidate = candidate.resolve()
            if resolved_candidate in anchor_set:
                continue
            try:
                text = resolved_candidate.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            targets = wikilinks_from_text(text) + markdown_links_from_text(text)
            for target in targets:
                resolved = resolve_markdown_target(
                    target, resolved_candidate, scan_root, lookup
                )
                if resolved and resolved in anchor_set:
                    add_related_item(items, resolved_candidate, scan_root, "backlink")
                    break

    ordered = list(items.values())
    reason_rank = {
        "self": 0,
        "read-before-edit": 1,
        "edit-after-edit": 2,
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

    semantic_radius = int(getattr(args, "semantic_radius", 0) or 0)
    check_links = bool(getattr(args, "check_links", False))
    semantic_neighbors: list[dict[str, Any]] = []
    suspicious_links: list[dict[str, Any]] = []

    if semantic_radius > 0 or check_links:
        # Local-import: these helpers pull in sqlite_vec, which is a heavy
        # uv-shebang dep. read-related stays import-light unless one of
        # the semantic flags is on.
        from .index import (
            check_explicit_link_coherence,
            find_corpus_root_for,
            find_semantic_neighbors,
        )

        corpus_root = find_corpus_root_for(anchors[0])
        if corpus_root is not None:
            already_linked = {
                relative_path(Path(item["path"]), corpus_root)
                for item in items.values()
            }
            anchor_rel_set = {
                relative_path(anchor.resolve(), corpus_root) for anchor in anchors
            }
            excluded = already_linked | anchor_rel_set

            if semantic_radius > 0:
                semantic_neighbors = find_semantic_neighbors(
                    corpus_root=corpus_root,
                    anchor_paths=anchors,
                    k=semantic_radius,
                    excluded_relative_paths=excluded,
                )

            if check_links:
                # Resolve explicit link targets again (frontmatter +
                # wikilinks + markdown-links) — same logic as above but
                # we only need the resolved paths, not full items.
                threshold = float(getattr(args, "link_distance_threshold", 0.4))
                for anchor in anchors:
                    text = anchor.read_text(encoding="utf-8", errors="replace")
                    lines = text.splitlines()
                    frontmatter = parse_frontmatter(lines)
                    targets: list[Path] = []
                    for key in GRAPH_LINK_KEYS:
                        for tgt in normalize_frontmatter_links(frontmatter.get(key)):
                            r = resolve_markdown_target(tgt, anchor, scan_root, lookup)
                            if r and r.resolve() != anchor.resolve():
                                targets.append(r)
                    for tgt in wikilinks_from_text(text):
                        r = resolve_markdown_target(tgt, anchor, scan_root, lookup)
                        if r and r.resolve() != anchor.resolve():
                            targets.append(r)
                    for tgt in markdown_links_from_text(text):
                        r = resolve_markdown_target(tgt, anchor, scan_root, lookup)
                        if r and r.resolve() != anchor.resolve():
                            targets.append(r)
                    # Dedupe while preserving order.
                    seen: set[Path] = set()
                    uniq: list[Path] = []
                    for t in targets:
                        rk = t.resolve()
                        if rk not in seen:
                            seen.add(rk)
                            uniq.append(t)
                    suspicious_links.extend(
                        check_explicit_link_coherence(
                            corpus_root=corpus_root,
                            anchor=anchor,
                            linked_targets=uniq,
                            threshold=threshold,
                        )
                    )

    return {
        "root": str(scan_root),
        "anchors": [str(path) for path in anchors],
        "include": sorted(include),
        "token_budget": budget,
        "token_total": running,
        "items": kept,
        "dropped_by_budget": dropped,
        "semantic_neighbors": semantic_neighbors,
        "suspicious_links": suspicious_links,
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
