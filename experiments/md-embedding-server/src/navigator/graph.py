#!/usr/bin/env python3
"""Command surface for md_graph: argparse + cmd_* dispatchers.

Heavy logic lives in graph_core (I/O + classes), graph_edges (link parsing +
resolution), and graph_reports (analysis report builders). This module is the
thin orchestration layer that maps CLI subcommands to those primitives.

Public names are re-exported here so existing importers (`navigator.graph.X`)
keep working without source changes.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .filters import add_path_filter_args
from .graph_core import (
    ALLOWED_FIELDS,
    Doc,
    Edge,
    Finding,
    GRAPH_FIELDS,
    LEGACY_FIELDS,
    NAVIGATOR_SCRIPT,
    RELATED_SECTION_RE,
    REQUIRED_FIELDS,
    dump_frontmatter,
    iter_markdown,
    load_doc,
    load_docs,
    load_target_doc,
    repo_root,
    safe_rel,
    split_frontmatter,
    write_doc,
)
from .graph_edges import (
    description_for,
    doc_data,
    doc_index,
    edge_data,
    emit_json,
    finding_data,
    format_anchors,
    graph_values,
    headings,
    is_empty,
    is_wikilink,
    markdown_links,
    normalize_anchor,
    parse_wikilink,
    render_audit_link,
    render_edge,
    render_edge_data,
    resolve_graph_edge,
    resolve_markdown_link,
    resolve_target,
    scan_doc,
    target_candidates,
    wikilinks_from_text,
)
from .graph_reports import (
    PREFLIGHT_BLOCKERS,
    canonical_cycle,
    changed_markdown_paths,
    check_graph,
    cycles_for_doc,
    dependency_report,
    edit_after_edit_adjacency,
    edit_after_edit_cascade,
    find_edit_after_edit_cycles,
    health_report,
    impact_report,
    inbound_anchors_by_heading,
    navigator_read_related_command,
    preflight_deferred_notes,
    preflight_report,
    render_preflight_report,
    report_has_blockers,
    reverse_body_markdown_link_holders,
    reverse_body_wikilink_holders,
    reverse_edit_after_edit,
    reverse_field_holders,
)


__all__ = [
    "ALLOWED_FIELDS",
    "Doc",
    "Edge",
    "Finding",
    "GRAPH_FIELDS",
    "LEGACY_FIELDS",
    "NAVIGATOR_SCRIPT",
    "PREFLIGHT_BLOCKERS",
    "RELATED_SECTION_RE",
    "REQUIRED_FIELDS",
    "build_parser",
    "canonical_cycle",
    "changed_markdown_paths",
    "check_graph",
    "cycles_for_doc",
    "dependency_report",
    "description_for",
    "doc_data",
    "doc_index",
    "dump_frontmatter",
    "edge_data",
    "edit_after_edit_adjacency",
    "edit_after_edit_cascade",
    "emit_json",
    "find_edit_after_edit_cycles",
    "finding_data",
    "format_anchors",
    "graph_values",
    "headings",
    "health_report",
    "impact_report",
    "inbound_anchors_by_heading",
    "is_empty",
    "is_wikilink",
    "iter_markdown",
    "load_doc",
    "load_docs",
    "load_target_doc",
    "main",
    "markdown_links",
    "navigator_read_related_command",
    "normalize_anchor",
    "parse_wikilink",
    "preflight_deferred_notes",
    "preflight_report",
    "render_audit_link",
    "render_edge",
    "render_edge_data",
    "render_preflight_report",
    "repo_root",
    "report_has_blockers",
    "resolve_graph_edge",
    "resolve_markdown_link",
    "resolve_target",
    "reverse_body_markdown_link_holders",
    "reverse_body_wikilink_holders",
    "reverse_edit_after_edit",
    "reverse_field_holders",
    "safe_rel",
    "scan_doc",
    "split_frontmatter",
    "strip_related_section",
    "target_candidates",
    "wikilinks_from_text",
    "write_doc",
]


def print_summary(name: str, targets: int, findings: list[Finding]) -> None:
    print(f"{name} | targets={targets} issues={len(findings)}")
    if not findings:
        print("OK")
        return
    for finding in findings:
        print(finding.render())


def strip_related_section(body: str) -> tuple[str, bool]:
    new_body, count = RELATED_SECTION_RE.subn("", body)
    if count == 0:
        return body, False
    new_body = new_body.rstrip() + ("\n" if body.endswith("\n") else "")
    return new_body, True


def cmd_scan(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    findings = [finding for doc in docs for finding in scan_doc(doc)]
    if args.json:
        emit_json(
            {
                "command": "scan",
                "targets": len(docs),
                "issues": [finding_data(finding) for finding in findings],
            }
        )
        return 1 if findings else 0
    print_summary("SCAN", len(docs), findings)
    return 1 if findings else 0


def cmd_init(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    json_output = getattr(args, "json", False)
    changed = 0
    modified: list[str] = []
    template = {
        "description": "TODO",
        "read-before-edit": [],
        "edit-after-edit": [],
    }
    for doc in docs:
        if doc.has_frontmatter:
            continue
        write_doc(doc, template, doc.body)
        changed += 1
        modified.append(str(doc.rel))
        if not json_output:
            print(f"INIT | {doc.rel}")
    if json_output:
        emit_json(
            {
                "command": "init",
                "targets": len(docs),
                "changed": changed,
                "unchanged": len(docs) - changed,
                "modified": modified,
            }
        )
        return 0
    print(f"SUMMARY | targets={len(docs)} changed={changed} unchanged={len(docs) - changed}")
    return 0


def cmd_strip(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    json_output = getattr(args, "json", False)
    changed = 0
    modified: list[str] = []
    changes: list[dict[str, Any]] = []
    for doc in docs:
        if not doc.has_frontmatter:
            if not args.also_related_section:
                continue
            new_body, section_removed = strip_related_section(doc.body)
            if not section_removed:
                continue
            doc.path.write_text(new_body, encoding="utf-8")
            changed += 1
            modified.append(str(doc.rel))
            changes.append(
                {
                    "path": str(doc.rel),
                    "removed_fields": [],
                    "related_section_removed": True,
                }
            )
            if not json_output:
                print(f"STRIP | {doc.rel} | (no frontmatter)+related-section")
            continue
        removed_fields = [key for key in doc.frontmatter if key not in ALLOWED_FIELDS]
        new_data = {
            key: value
            for key, value in doc.frontmatter.items()
            if key in ALLOWED_FIELDS
        }
        new_body = doc.body
        section_removed = False
        if args.also_related_section:
            new_body, section_removed = strip_related_section(doc.body)
        if new_data == doc.frontmatter and not section_removed:
            continue
        write_doc(doc, new_data, new_body)
        changed += 1
        modified.append(str(doc.rel))
        changes.append(
            {
                "path": str(doc.rel),
                "removed_fields": removed_fields,
                "related_section_removed": section_removed,
            }
        )
        marker = ",".join(removed_fields) or "(no legacy/unknown fields)"
        if section_removed:
            marker = f"{marker}+related-section"
        if not json_output:
            print(f"STRIP | {doc.rel} | {marker}")
    if json_output:
        emit_json(
            {
                "command": "strip",
                "targets": len(docs),
                "changed": changed,
                "unchanged": len(docs) - changed,
                "modified": modified,
                "changes": changes,
            }
        )
        return 0
    print(f"SUMMARY | targets={len(docs)} changed={changed} unchanged={len(docs) - changed}")
    return 0


def cmd_deps(args: argparse.Namespace) -> int:
    if args.depth < 1:
        raise SystemExit("--depth must be >= 1")
    root = repo_root()
    target_path = (root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    if not target_path.exists():
        raise SystemExit(f"Path not found: {args.path}")
    doc = load_doc(target_path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    report = dependency_report(doc, all_docs, root, args.depth)
    if args.json:
        emit_json({"command": "deps", "depth": args.depth, **report})
        return 0
    print(f"FILE | {doc.rel} | {description_for(doc)}")
    for field in GRAPH_FIELDS:
        values = report["fields"][field]
        print(f"\n{field} ({len(values)})")
        if not values:
            print("OK")
            continue
        for value in values:
            if value["status"] == "missing":
                print(f"- {value['raw']} -> MISSING_TARGET")
            else:
                print(f"- {value['raw']} -> {value['path']} | {value['description']}")
    holders = report["reverse_edit_after_edit"]
    print(f"\nreverse edit-after-edit ({len(holders)})")
    if not holders:
        print("OK")
    for holder in holders:
        print(f"- {holder['path']} | {holder['description']}")
    if args.depth > 1:
        cascade = report["edit_after_edit_cascade"]
        print(f"\nedit-after-edit cascade depth<={args.depth} ({len(cascade)})")
        if not cascade:
            print("OK")
        for item in cascade:
            marker = " | CYCLE" if item["cycle"] else ""
            if item["status"] == "missing":
                print(f"- depth {item['depth']}: {item['from']} -> MISSING_TARGET {item['raw']}{marker}")
            else:
                print(f"- depth {item['depth']}: {item['from']} -> {item['path']} | {item['description']}{marker}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    root = repo_root()
    target_path = (root / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
    if not target_path.exists():
        raise SystemExit(f"Path not found: {args.path}")
    doc = load_doc(target_path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    index = doc_index(all_docs, root)
    index[doc.path.resolve()] = doc
    if args.json:
        emit_json({"command": "audit", **dependency_report(doc, all_docs, root, 1)})
        return 0

    print(f"FILE | {doc.rel} | {description_for(doc)}")
    for field in GRAPH_FIELDS:
        values = graph_values(doc, field)
        print(f"\n{field} ({len(values)})")
        if not values:
            print("OK")
            continue
        for value in values:
            print(render_audit_link(value, doc, index, root))

    holders = reverse_edit_after_edit(doc, all_docs, root)
    print(f"\nreverse edit-after-edit ({len(holders)})")
    if not holders:
        print("OK")
        return 0
    for holder in holders:
        print(f"- {holder.rel} | {description_for(holder)}")
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    root = repo_root()
    doc = load_target_doc(args.path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    report = impact_report(doc, all_docs, root, args.scan)
    if args.json:
        emit_json({"command": "impact", **report})
        return 0

    print(f"IMPACT | {report['file']['path']} | {report['file']['description']}")
    sections = (
        ("cascade breaks (reverse edit-after-edit)", report["cascade_breaks"]),
        ("reference breaks (reverse read-before-edit)", report["reference_breaks"]),
        ("body wikilink references", report["body_wikilink_refs"]),
        ("body markdown link references", report["body_markdown_refs"]),
    )
    for label, rows in sections:
        print(f"\n{label} ({len(rows)})")
        if not rows:
            print("OK")
            continue
        for row in rows:
            anchor_suffix = format_anchors(row.get("anchors", [])) if "anchors" in row else ""
            print(f"- {row['path']}{anchor_suffix} | {row['description']}")
    print("\nrelated reading")
    print(report["related_reading_command"])
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    findings = check_graph(docs, root)
    if args.json:
        emit_json(
            {
                "command": "check",
                "targets": len(docs),
                "issues": [finding_data(finding) for finding in findings],
            }
        )
        return 1 if findings else 0
    print_summary("CHECK", len(docs), findings)
    return 1 if findings else 0


def cmd_doctor(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    command_name = getattr(args, "command", "doctor")
    findings = [finding for doc in docs for finding in scan_doc(doc)]
    findings.extend(check_graph(docs, root))
    groups = {
        "critical": {"MISSING_TARGET", "BROKEN_WIKILINK", "BROKEN_MARKDOWN_LINK", "MISSING_FRONTMATTER"},
        "cleanup": {
            "LEGACY_FIELD",
            "UNKNOWN_FIELD",
            "GRAPH_FIELD_NOT_LIST",
            "GRAPH_LINK_NOT_WIKILINK",
            "RELATED_SECTION_PRESENT",
        },
        "optional": {"EMPTY_DESCRIPTION", "MISSING_GRAPH_FIELD", "MISSING_ANCHOR"},
    }
    grouped = {
        label: [finding for finding in findings if finding.code in codes]
        for label, codes in groups.items()
    }
    if args.json:
        emit_json(
            {
                "command": command_name,
                "targets": len(docs),
                "issues": [finding_data(finding) for finding in findings],
                "groups": {
                    label: [finding_data(finding) for finding in selected]
                    for label, selected in grouped.items()
                },
            }
        )
        return 1 if findings else 0
    print(f"{command_name.upper()} | targets={len(docs)} issues={len(findings)}")
    for label, selected in grouped.items():
        print(f"\n{label.upper()} ({len(selected)})")
        if not selected:
            print("OK")
            continue
        for finding in selected:
            print(finding.render())
    return 1 if findings else 0


def cmd_health(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    report = health_report(docs, root)
    if args.json:
        emit_json({"command": "health", **report})
        return 0

    coverage = report["description_coverage"]
    print(f"HEALTH | targets={report['targets']}")
    print(
        "description coverage: "
        f"{coverage['with_description']}/{report['targets']} ({coverage['percent']}%)"
    )
    print(f"missing descriptions: {coverage['missing']}")
    print(f"description TODO: {coverage['todo']}")
    print(f"no frontmatter: {coverage['no_frontmatter']}")
    print(f"broken graph links: {report['broken_graph_links']}")
    print(f"cycles in edit-after-edit: {len(report['cycles'])}")

    print(f"\norphans (no in/out graph edges) ({len(report['orphans'])})")
    if not report["orphans"]:
        print("OK")
    for row in report["orphans"]:
        print(f"- {row['path']} | {row['description']}")

    print(f"\ntop hubs (incoming graph edges) ({len(report['hubs'])})")
    if not report["hubs"]:
        print("OK")
    for row in report["hubs"]:
        print(f"- {row['incoming']} <- {row['path']} | {row['description']}")

    return 0


def cmd_cycles(args: argparse.Namespace) -> int:
    root = repo_root()
    docs = load_docs(args.paths, root, args)
    cycles = find_edit_after_edit_cycles(docs, root)
    if args.json:
        emit_json(
            {
                "command": "cycles",
                "targets": len(docs),
                "cycles": [
                    [doc_data(doc) for doc in cycle]
                    for cycle in cycles
                ],
            }
        )
        return 1 if cycles else 0
    print(f"CYCLES | targets={len(docs)} cycles={len(cycles)}")
    if not cycles:
        print("OK")
        return 0
    for cycle in cycles:
        print("- " + " -> ".join(str(doc.rel) for doc in cycle))
    return 1


def cmd_preflight(args: argparse.Namespace) -> int:
    if args.depth < 1:
        raise SystemExit("--depth must be >= 1")
    root = repo_root()
    doc = load_target_doc(args.path, root)
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    report = preflight_report(doc, all_docs, root, args.depth, args.scan)
    if args.json:
        emit_json({"command": "preflight", "depth": args.depth, **report})
    else:
        print(render_preflight_report(report))
    return 1 if report_has_blockers(report) else 0


def cmd_changed(args: argparse.Namespace) -> int:
    if args.depth < 1:
        raise SystemExit("--depth must be >= 1")
    if args.base and args.since:
        raise SystemExit("Use either --base or --since, not both.")
    if args.staged and (args.base or args.since):
        raise SystemExit("Use --staged without --base or --since.")
    root = repo_root()
    scan_root = (root / args.scan).resolve() if args.scan else root
    all_docs = load_docs([str(scan_root)], root, args)
    reports: list[dict[str, Any]] = []
    deleted: list[str] = []
    for path in changed_markdown_paths(root, args):
        if not path.exists():
            deleted.append(str(safe_rel(path, root)))
            continue
        reports.append(preflight_report(load_doc(path, root), all_docs, root, args.depth, args.scan))

    if args.json:
        emit_json(
            {
                "command": "changed",
                "since": "STAGED" if args.staged else (args.since or args.base or "HEAD"),
                "depth": args.depth,
                "reports": reports,
                "deleted": deleted,
            }
        )
    else:
        since = "STAGED" if args.staged else (args.since or args.base or "HEAD")
        print(f"CHANGED | since={since} markdown_files={len(reports)} deleted={len(deleted)}")
        for path in deleted:
            print(f"\nDELETED | {path} | downstream unknown; search references before finalizing")
        for report in reports:
            print()
            print(render_preflight_report(report, title="CHANGED-FILE"))
    return 1 if any(report_has_blockers(report) for report in reports) or deleted else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable Markdown frontmatter graph helper.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, func, help_text in (
        ("scan", cmd_scan, "Find frontmatter schema issues."),
        ("init", cmd_init, "Add graph frontmatter template where missing."),
        ("check", cmd_check, "Validate graph links."),
        ("doctor", cmd_doctor, "Group graph findings by severity."),
        ("health", cmd_health, "Summarize graph description coverage, links, hubs, orphans, and cycles."),
        ("cycles", cmd_cycles, "Find edit-after-edit cycles."),
    ):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("paths", nargs="*", help="Markdown files or directories. Defaults to current directory.")
        cmd.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
        add_path_filter_args(cmd, command_name="graph", with_no_default_excludes=True)
        cmd.set_defaults(func=func)

    strip = sub.add_parser("strip", help="Remove legacy graph fields and optionally related-docs sections.")
    strip.add_argument("paths", nargs="*", help="Markdown files or directories. Defaults to current directory.")
    strip.add_argument(
        "--also-related-section",
        action="store_true",
        help="Also remove '## Связанные документы' / '## Related documents' sections from body.",
    )
    strip.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(strip, command_name="graph", with_no_default_excludes=True)
    strip.set_defaults(func=cmd_strip)

    deps = sub.add_parser(
        "deps",
        help="Show graph fields and reverse edit-after-edit holders for one Markdown file.",
    )
    deps.add_argument("path", help="Markdown file path.")
    deps.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan (default: repo root).",
    )
    deps.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Maximum edit-after-edit cascade depth to show (default: 1).",
    )
    deps.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(deps, command_name="graph", with_no_default_excludes=True)
    deps.set_defaults(func=cmd_deps)

    audit = sub.add_parser(
        "audit",
        help="Show one Markdown file, its description, and graph links with linked descriptions.",
    )
    audit.add_argument("path", help="Markdown file path.")
    audit.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan and cached descriptions (default: repo root).",
    )
    audit.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(audit, command_name="graph", with_no_default_excludes=True)
    audit.set_defaults(func=cmd_audit)

    impact = sub.add_parser(
        "impact",
        help="Show what breaks if a Markdown file is deleted or renamed.",
    )
    impact.add_argument("path", help="Markdown file path.")
    impact.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan (default: repo root).",
    )
    impact.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(impact, command_name="graph", with_no_default_excludes=True)
    impact.set_defaults(func=cmd_impact)

    preflight = sub.add_parser(
        "preflight",
        help="One pre-edit safety report for a Markdown graph file.",
    )
    preflight.add_argument("path", help="Markdown file path.")
    preflight.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan and cycle checks (default: repo root).",
    )
    preflight.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum edit-after-edit cascade depth to show (default: 2).",
    )
    preflight.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(preflight, command_name="graph", with_no_default_excludes=True)
    preflight.set_defaults(func=cmd_preflight)

    changed = sub.add_parser(
        "changed",
        help="Report Markdown graph downstream checks for files touched by git diff.",
    )
    changed.add_argument(
        "--scan",
        default=None,
        help="Scope for reverse-scan and cycle checks (default: repo root).",
    )
    changed.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum edit-after-edit cascade depth to show (default: 2).",
    )
    changed.add_argument(
        "--base",
        default=None,
        help="Compare against a git base ref. Prefer --since in new workflows.",
    )
    changed.add_argument(
        "--since",
        default=None,
        help="Git ref to diff against (default: HEAD, including staged and unstaged changes).",
    )
    changed.add_argument(
        "--staged",
        action="store_true",
        help="Use staged changes from git diff --cached.",
    )
    changed.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    add_path_filter_args(changed, command_name="graph", with_no_default_excludes=True)
    changed.set_defaults(func=cmd_changed)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
