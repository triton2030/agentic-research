"""Graph analysis report builders: dependency / impact / preflight / health / cycles / check.

This module owns the analysis layer of the graph backend. It takes Doc lists
and produces structured reports for CLI commands. No I/O beyond what graph_core
already loaded; no argparse; no top-level commands.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path
from typing import Any

from .markdown_io import collect_headings

from .graph_core import (
    Doc,
    Finding,
    GRAPH_FIELDS,
    RELATED_SECTION_RE,
    load_doc,
    safe_rel,
)
from .graph_edges import (
    description_for,
    doc_data,
    doc_index,
    edge_data,
    finding_data,
    format_anchors,
    graph_values,
    headings,
    is_empty,
    markdown_links,
    normalize_anchor,
    parse_wikilink,
    render_edge_data,
    resolve_graph_edge,
    resolve_markdown_link,
    resolve_target,
    scan_doc,
    wikilinks_from_text,
)


PREFLIGHT_BLOCKERS = {
    "MISSING_TARGET",
    "BROKEN_WIKILINK",
    "BROKEN_MARKDOWN_LINK",
    "MISSING_FRONTMATTER",
    "GRAPH_FIELD_NOT_LIST",
    "GRAPH_LINK_NOT_WIKILINK",
}


def reverse_field_holders(target_doc: Doc, all_docs: list[Doc], root: Path, field: str) -> list[Doc]:
    target_path = target_doc.path.resolve()
    holders: list[Doc] = []
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        for raw_link in graph_values(doc, field):
            target_raw, _anchor = parse_wikilink(raw_link)
            resolved = resolve_target(target_raw, doc.path, root)
            if resolved and resolved.resolve() == target_path:
                holders.append(doc)
                break
    return holders


def reverse_edit_after_edit(target_doc: Doc, all_docs: list[Doc], root: Path) -> list[Doc]:
    return reverse_field_holders(target_doc, all_docs, root, "edit-after-edit")


def reverse_body_wikilink_holders(
    target_doc: Doc, all_docs: list[Doc], root: Path
) -> list[tuple[Doc, list[str | None]]]:
    target_path = target_doc.path.resolve()
    results: list[tuple[Doc, list[str | None]]] = []
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        anchors_used: list[str | None] = []
        for raw_link in wikilinks_from_text(doc.body):
            target_raw, anchor = parse_wikilink(raw_link)
            resolved = resolve_target(target_raw, doc.path, root)
            if resolved and resolved.resolve() == target_path:
                anchors_used.append(anchor)
        if anchors_used:
            results.append((doc, anchors_used))
    return results


def inbound_anchors_by_heading(
    target_doc: Doc, all_docs: list[Doc], root: Path
) -> dict[str, list[dict[str, Any]]]:
    target_path = target_doc.path.resolve()
    heading_lookup: dict[str, str] = {}
    for heading in collect_headings(target_doc.body.splitlines(), max_level=6):
        original = str(heading["text"]).strip()
        heading_lookup[normalize_anchor(original)] = original
    by_heading: dict[str, list[dict[str, Any]]] = {}
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        for raw_link in wikilinks_from_text(doc.body):
            target_raw, anchor = parse_wikilink(raw_link)
            if not anchor:
                continue
            resolved = resolve_target(target_raw, doc.path, root)
            if not resolved or resolved.resolve() != target_path:
                continue
            heading_text = heading_lookup.get(normalize_anchor(anchor))
            if heading_text is None:
                continue
            by_heading.setdefault(heading_text, []).append(
                {
                    "holder": str(safe_rel(doc.path, root)),
                    "description": description_for(doc),
                    "raw_anchor": anchor,
                }
            )
    return by_heading


def reverse_body_markdown_link_holders(target_doc: Doc, all_docs: list[Doc], root: Path) -> list[Doc]:
    target_path = target_doc.path.resolve()
    holders: list[Doc] = []
    for doc in all_docs:
        if doc.path.resolve() == target_path:
            continue
        for target in markdown_links(doc.body):
            resolved = resolve_markdown_link(target, doc.path, root)
            if resolved and resolved.resolve() == target_path:
                holders.append(doc)
                break
    return holders


def edit_after_edit_cascade(doc: Doc, index: dict[Path, Doc], root: Path, max_depth: int) -> list[dict[str, Any]]:
    if max_depth < 1:
        return []
    cascade: list[dict[str, Any]] = []
    start = doc.path.resolve()
    queue: list[tuple[Doc, int, list[Path]]] = [(doc, 0, [start])]
    expanded: set[Path] = {start}
    while queue:
        current, depth, path_stack = queue.pop(0)
        if depth >= max_depth:
            continue
        next_depth = depth + 1
        for raw_link in graph_values(current, "edit-after-edit"):
            edge = resolve_graph_edge(raw_link, current, index, root)
            target_path = edge.target.path.resolve() if edge.target is not None else None
            is_cycle = target_path in path_stack if target_path else False
            item = edge_data(edge)
            item.update(
                {
                    "depth": next_depth,
                    "from": str(current.rel),
                    "cycle": is_cycle,
                }
            )
            cascade.append(item)
            if edge.target is None or target_path is None or is_cycle:
                continue
            if next_depth < max_depth and target_path not in expanded:
                expanded.add(target_path)
                queue.append((edge.target, next_depth, [*path_stack, target_path]))
    return cascade


def dependency_report(doc: Doc, all_docs: list[Doc], root: Path, depth: int) -> dict[str, Any]:
    index = doc_index(all_docs, root)
    index[doc.path.resolve()] = doc
    fields: dict[str, list[dict[str, Any]]] = {}
    for field in GRAPH_FIELDS:
        fields[field] = [
            edge_data(resolve_graph_edge(raw_link, doc, index, root))
            for raw_link in graph_values(doc, field)
        ]
    holders = reverse_edit_after_edit(doc, all_docs, root)
    return {
        "file": doc_data(doc),
        "fields": fields,
        "reverse_edit_after_edit": [doc_data(holder) for holder in holders],
        "edit_after_edit_cascade": edit_after_edit_cascade(doc, index, root, depth),
    }


def navigator_read_related_command(path: str, token_budget: int = 3000, scan: str | None = None) -> str:
    scan_arg = f" --scan {shlex.quote(scan)}" if scan else ""
    return (
        f"md read-related --paths {shlex.quote(path)}"
        f"{scan_arg} --token-budget {token_budget} --expanded"
    )


def impact_report(doc: Doc, all_docs: list[Doc], root: Path, scan: str | None = None) -> dict[str, Any]:
    return {
        "file": doc_data(doc),
        "related_reading_command": navigator_read_related_command(str(doc.rel), scan=scan),
        "cascade_breaks": [
            doc_data(holder)
            for holder in reverse_field_holders(doc, all_docs, root, "edit-after-edit")
        ],
        "reference_breaks": [
            doc_data(holder)
            for holder in reverse_field_holders(doc, all_docs, root, "read-before-edit")
        ],
        "body_wikilink_refs": [
            {**doc_data(holder), "anchors": anchors}
            for holder, anchors in reverse_body_wikilink_holders(doc, all_docs, root)
        ],
        "body_markdown_refs": [
            doc_data(holder)
            for holder in reverse_body_markdown_link_holders(doc, all_docs, root)
        ],
    }


def check_graph(docs: list[Doc], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    index = doc_index(docs, root)
    for doc in docs:
        if not doc.has_frontmatter:
            continue
        for field in GRAPH_FIELDS:
            for raw_link in graph_values(doc, field):
                target_raw, anchor = parse_wikilink(raw_link)
                target_path = resolve_target(target_raw, doc.path, root)
                if not target_path:
                    findings.append(Finding("MISSING_TARGET", doc.rel, f"{field}: {raw_link}"))
                    continue
                target_doc = index.get(target_path.resolve())
                if target_doc is None:
                    target_doc = load_doc(target_path, root)
                    index[target_path.resolve()] = target_doc
                if anchor and normalize_anchor(anchor) not in headings(target_doc.body):
                    findings.append(Finding("MISSING_ANCHOR", doc.rel, f"{raw_link}"))
        for raw_link in wikilinks_from_text(doc.body):
            target_raw, anchor = parse_wikilink(raw_link)
            target_path = resolve_target(target_raw, doc.path, root)
            if not target_path:
                findings.append(Finding("BROKEN_WIKILINK", doc.rel, raw_link))
                continue
            if anchor:
                target_doc = index.get(target_path.resolve()) or load_doc(target_path, root)
                if normalize_anchor(anchor) not in headings(target_doc.body):
                    findings.append(Finding("MISSING_ANCHOR", doc.rel, raw_link))
        for markdown_target in markdown_links(doc.body):
            target_path = resolve_markdown_link(markdown_target, doc.path, root)
            if target_path is None:
                findings.append(Finding("BROKEN_MARKDOWN_LINK", doc.rel, markdown_target))
        if RELATED_SECTION_RE.search(doc.body):
            findings.append(Finding("RELATED_SECTION_PRESENT", doc.rel, "remove with strip --also-related-section"))
    return findings


def edit_after_edit_adjacency(docs: list[Doc], root: Path) -> dict[Path, list]:
    index = doc_index(docs, root)
    scope = {doc.path.resolve() for doc in docs}
    adjacency: dict[Path, list] = {}
    for doc in docs:
        edges = []
        for raw_link in graph_values(doc, "edit-after-edit"):
            edge = resolve_graph_edge(raw_link, doc, index, root)
            if edge.target is not None and edge.target.path.resolve() in scope:
                edges.append(edge)
        adjacency[doc.path.resolve()] = edges
    return adjacency


def canonical_cycle(paths: list[Path], index: dict[Path, Doc]) -> tuple[str, ...]:
    labels = [str(index[path].rel) for path in paths]
    body = labels[:-1]
    if not body:
        return tuple(labels)
    rotations = [body[index:] + body[:index] for index in range(len(body))]
    best = min(rotations)
    return tuple([*best, best[0]])


def find_edit_after_edit_cycles(docs: list[Doc], root: Path) -> list[list[Doc]]:
    index = doc_index(docs, root)
    docs_by_rel = {str(doc.rel): doc for doc in docs}
    adjacency = edit_after_edit_adjacency(docs, root)
    found: dict[tuple[str, ...], list[Doc]] = {}

    def visit(node: Path, stack: list[Path], active: set[Path]) -> None:
        active.add(node)
        stack.append(node)
        for edge in adjacency.get(node, []):
            if edge.target is None:
                continue
            target_path = edge.target.path.resolve()
            if target_path in active:
                start = stack.index(target_path)
                cycle_paths = [*stack[start:], target_path]
                key = canonical_cycle(cycle_paths, index)
                found[key] = [docs_by_rel[label] for label in key]
            elif target_path not in stack:
                visit(target_path, stack, active)
        stack.pop()
        active.remove(node)

    for doc in docs:
        visit(doc.path.resolve(), [], set())
    return [found[key] for key in sorted(found)]


def cycles_for_doc(doc: Doc, docs: list[Doc], root: Path) -> list[list[Doc]]:
    target = doc.path.resolve()
    return [
        cycle
        for cycle in find_edit_after_edit_cycles(docs, root)
        if any(item.path.resolve() == target for item in cycle)
    ]


def health_report(docs: list[Doc], root: Path) -> dict[str, Any]:
    total = len(docs)
    with_description = 0
    missing_description = 0
    description_todo = 0
    no_frontmatter = 0
    broken_graph_links = 0
    incoming: dict[Path, int] = {}
    outgoing: dict[Path, int] = {}

    for doc in docs:
        if not doc.has_frontmatter:
            no_frontmatter += 1
        description = doc.frontmatter.get("description") if doc.has_frontmatter else None
        if is_empty(description):
            missing_description += 1
            if str(description).strip() == "TODO":
                description_todo += 1
        else:
            with_description += 1

        for field in GRAPH_FIELDS:
            for raw_link in graph_values(doc, field):
                target_raw, _anchor = parse_wikilink(raw_link)
                target_path = resolve_target(target_raw, doc.path, root)
                if target_path is None:
                    broken_graph_links += 1
                    continue
                source_path = doc.path.resolve()
                resolved_target = target_path.resolve()
                outgoing[source_path] = outgoing.get(source_path, 0) + 1
                incoming[resolved_target] = incoming.get(resolved_target, 0) + 1

    orphans = [
        doc_data(doc)
        for doc in docs
        if incoming.get(doc.path.resolve(), 0) == 0 and outgoing.get(doc.path.resolve(), 0) == 0
    ]
    hubs: list[dict[str, Any]] = []
    for path, count in sorted(incoming.items(), key=lambda item: (-item[1], str(safe_rel(item[0], root))))[:10]:
        try:
            doc = load_doc(path, root)
            hubs.append({"incoming": count, **doc_data(doc)})
        except OSError:
            hubs.append(
                {
                    "incoming": count,
                    "path": str(safe_rel(path, root)),
                    "description": "(unreadable)",
                    "has_frontmatter": False,
                }
            )

    cycles = [[doc_data(item) for item in cycle] for cycle in find_edit_after_edit_cycles(docs, root)]
    percent = round(100 * with_description / total) if total else 0
    return {
        "targets": total,
        "description_coverage": {
            "with_description": with_description,
            "missing": missing_description,
            "todo": description_todo,
            "no_frontmatter": no_frontmatter,
            "percent": percent,
        },
        "broken_graph_links": broken_graph_links,
        "orphans": orphans,
        "hubs": hubs,
        "cycles": cycles,
        "cycles_count": len(cycles),
    }


def preflight_deferred_notes(doc: Doc) -> list[str]:
    notes = [
        "Semantic completeness is not machine-proven; classify candidate edges in the owning skill.",
    ]
    if not doc.has_frontmatter:
        notes.append("No graph frontmatter: read/update obligations are unknown.")
    elif not graph_values(doc, "edit-after-edit"):
        notes.append("No edit-after-edit edges declared; treat this as a positive claim only after semantic audit.")
    return notes


def preflight_report(
    doc: Doc,
    all_docs: list[Doc],
    root: Path,
    depth: int,
    scan: str | None = None,
) -> dict[str, Any]:
    deps = dependency_report(doc, all_docs, root, depth)
    findings = [*scan_doc(doc), *check_graph([doc], root)]
    cycles = cycles_for_doc(doc, all_docs, root)
    check_only_references = {
        "reverse_edit_after_edit": deps["reverse_edit_after_edit"],
        "reverse_read_before_edit": [
            doc_data(holder)
            for holder in reverse_field_holders(doc, all_docs, root, "read-before-edit")
        ],
        "body_wikilinks": [
            {**doc_data(holder), "anchors": anchors}
            for holder, anchors in reverse_body_wikilink_holders(doc, all_docs, root)
        ],
        "body_markdown_links": [
            doc_data(holder)
            for holder in reverse_body_markdown_link_holders(doc, all_docs, root)
        ],
    }
    anchor_drift = inbound_anchors_by_heading(doc, all_docs, root)
    return {
        "file": doc_data(doc),
        "related_reading_command": navigator_read_related_command(str(doc.rel), scan=scan),
        "must_read": deps["fields"]["read-before-edit"],
        "must_update": deps["fields"]["edit-after-edit"],
        "update_cascade": deps["edit_after_edit_cascade"],
        "reverse_holders": deps["reverse_edit_after_edit"],
        "check_only_references": check_only_references,
        "check_only": [finding_data(finding) for finding in findings],
        "cycles": [[doc_data(item) for item in cycle] for cycle in cycles],
        "anchor_drift_risk": anchor_drift,
        "deferred": preflight_deferred_notes(doc),
    }


def report_has_blockers(report: dict[str, Any]) -> bool:
    issue_codes = {item["code"] for item in report.get("check_only", [])}
    return bool(issue_codes & PREFLIGHT_BLOCKERS) or bool(report.get("cycles"))


def render_preflight_report(report: dict[str, Any], title: str = "PREFLIGHT") -> str:
    lines = [f"{title} | {report['file']['path']} | {report['file']['description']}"]

    lines.append(f"\nmust-read ({len(report['must_read'])})")
    lines.extend(render_edge_data(item) for item in report["must_read"])
    if not report["must_read"]:
        lines.append("OK")

    lines.append(f"\nmust-update ({len(report['must_update'])})")
    lines.extend(render_edge_data(item) for item in report["must_update"])
    if not report["must_update"]:
        lines.append("OK")

    cascade = report["update_cascade"]
    lines.append(f"\nupdate-cascade ({len(cascade)})")
    if not cascade:
        lines.append("OK")
    for item in cascade:
        marker = " | CYCLE" if item.get("cycle") else ""
        if item.get("status") == "missing":
            lines.append(f"- depth {item['depth']}: {item['from']} -> MISSING_TARGET {item['raw']}{marker}")
        else:
            lines.append(f"- depth {item['depth']}: {item['from']} -> {item['path']} | {item['description']}{marker}")

    holders = report["reverse_holders"]
    lines.append(f"\ncheck-only reverse edit-after-edit ({len(holders)})")
    if not holders:
        lines.append("OK")
    for holder in holders:
        lines.append(f"- {holder['path']} | {holder['description']}")

    references = report.get("check_only_references", {})
    reference_sections = (
        ("reverse read-before-edit", references.get("reverse_read_before_edit", [])),
        ("body wikilinks", references.get("body_wikilinks", [])),
        ("body markdown links", references.get("body_markdown_links", [])),
    )
    total_references = sum(len(rows) for _label, rows in reference_sections)
    lines.append(f"\ncheck-only references ({total_references})")
    if not total_references:
        lines.append("OK")
    for label, rows in reference_sections:
        for row in rows:
            anchor_suffix = format_anchors(row.get("anchors", [])) if "anchors" in row else ""
            lines.append(f"- {label}: {row['path']}{anchor_suffix} | {row['description']}")

    drift = report.get("anchor_drift_risk") or {}
    total_anchored = sum(len(holders) for holders in drift.values())
    lines.append(f"\nanchor-drift risk ({len(drift)} headings, {total_anchored} inbound)")
    if not drift:
        lines.append("OK")
    for heading, holders in drift.items():
        lines.append(f"- ## {heading} ({len(holders)} inbound, rename = silent break)")
        for holder in holders[:3]:
            lines.append(f"  - {holder['holder']} | {holder['description']}")
        if len(holders) > 3:
            lines.append(f"  - ... (+{len(holders) - 3} more)")

    checks = report["check_only"]
    lines.append(f"\ncheck-only issues ({len(checks)})")
    if not checks:
        lines.append("OK")
    for issue in checks:
        lines.append(f"- {issue['code']} | {issue['path']} | {issue['detail']}")

    cycles = report["cycles"]
    lines.append(f"\ncycles ({len(cycles)})")
    if not cycles:
        lines.append("OK")
    for cycle in cycles:
        lines.append("- " + " -> ".join(item["path"] for item in cycle))

    lines.append(f"\ndeferred ({len(report['deferred'])})")
    for note in report["deferred"]:
        lines.append(f"- {note}")

    lines.append("\nrelated reading")
    lines.append(report["related_reading_command"])

    return "\n".join(lines)


def changed_markdown_paths(root: Path, args: argparse.Namespace) -> list[Path]:
    if args.staged:
        command = ["git", "diff", "--cached", "--name-only", "--"]
    else:
        ref = args.since or args.base or "HEAD"
        command = ["git", "diff", "--name-only", ref, "--"]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "git diff failed")
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = (root / line.strip()).resolve()
        if path.suffix.lower() == ".md":
            paths.append(path)
    # Apply the same filter contract as load_docs/iter_markdown so
    # --path-include / --path-exclude / --no-default-excludes (and the
    # .md-tools.toml baseline appended into them via navigator.api.changed)
    # actually narrow the report set. Without this, git diff alone decided
    # the report scope and the flags silently no-op'd.
    from .graph_core import _path_passes
    include = list(getattr(args, "path_include", []) or [])
    exclude = list(getattr(args, "path_exclude", []) or [])
    use_defaults = not getattr(args, "no_default_excludes", False)
    return [
        p for p in paths
        if _path_passes(p, root, include, exclude, use_defaults)
    ]
