from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .api_utils import _default_paths, _exit, _list
from .config import resolve_filters_for_domain
from .graph_core import (
    ALLOWED_FIELDS,
    Doc,
    DocWrite,
    GraphArgs,
    PathNotFound,
    load_docs,
    load_target_doc,
    repo_root,
    root_for_scan,
    scan_scope_path,
    strip_related_section,
    write_doc_plan,
)
from .graph_edges import doc_data, finding_data, scan_doc
from .graph_reports import (
    check_graph,
    dependency_report,
    find_depends_on_cycles,
    health_report,
    impact_report,
    preflight_report,
    report_has_blockers,
)


def _graph_args(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    no_default_excludes: bool = False,
) -> GraphArgs:
    return GraphArgs(
        paths=_default_paths(paths),
        path_include=_list(path_include),
        path_exclude=_list(path_exclude),
        no_default_excludes=bool(no_default_excludes),
    )


def _resolved_graph_args(
    root: Path,
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    no_default_excludes: bool = False,
) -> GraphArgs:
    resolved_include, resolved_exclude = resolve_filters_for_domain(
        root,
        domain="graph",
        path_include=path_include,
        path_exclude=path_exclude,
    )
    return _graph_args(
        paths,
        path_include=resolved_include,
        path_exclude=resolved_exclude,
        no_default_excludes=no_default_excludes,
    )


def _graph_docs(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    no_default_excludes: bool = False,
) -> tuple[Path, GraphArgs, list[Any]]:
    root = repo_root()
    args = _resolved_graph_args(
        root,
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
        no_default_excludes=no_default_excludes,
    )
    return root, args, load_docs(args.paths, root, args)


def _graph_scan_docs(
    root: Path,
    scan: str | None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    no_default_excludes: bool = False,
) -> tuple[GraphArgs, list[Any]]:
    args = _resolved_graph_args(
        root,
        scan or ".",
        path_include=path_include,
        path_exclude=path_exclude,
        no_default_excludes=no_default_excludes,
    )
    scan_root = scan_scope_path(scan, root)
    return args, load_docs([str(scan_root)], root, args)


def _target_or_error(command: str, path: str, root: Path) -> tuple[Doc | None, dict[str, Any] | None]:
    """Load the focus doc for deps/impact/preflight, or return a uniform
    ``path_not_found`` error payload (exit code 2). Centralizes the handling
    so all three commands react to a missing path the same way instead of one
    catching and the others letting it escape to the runner fence.
    """
    try:
        return load_target_doc(path, root), None
    except PathNotFound:
        return None, _exit({"command": command, "error": "path_not_found", "path": path}, 2)


def scan(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    _root, _args, docs = _graph_docs(
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    findings = [finding for doc in docs for finding in scan_doc(doc)]
    return _exit(
        {"command": "scan", "targets": len(docs), "issues": [finding_data(f) for f in findings]},
        1 if findings else 0,
    )


def check(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    root, _args, docs = _graph_docs(
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    findings = check_graph(docs, root)
    return _exit(
        {"command": "check", "targets": len(docs), "issues": [finding_data(f) for f in findings]},
        1 if findings else 0,
    )

def health(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    root, _args, docs = _graph_docs(
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    return {"command": "health", **health_report(docs, root)}

def cycles(
    paths: Iterable[str] | str | None = None,
    *,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    root, _args, docs = _graph_docs(
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    found = find_depends_on_cycles(docs, root)
    return _exit(
        {"command": "cycles", "targets": len(docs), "cycles": [[doc_data(doc) for doc in cycle] for cycle in found]},
        1 if found else 0,
    )

def deps(
    path: str,
    *,
    scan: str | None = None,
    depth: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    selected_depth = int(depth or 1)
    if selected_depth < 1:
        return _exit({"command": "deps", "error": "depth_must_be_positive"}, 2)
    root = root_for_scan(scan)
    target, error = _target_or_error("deps", path, root)
    if error is not None:
        return error
    _args, all_docs = _graph_scan_docs(
        root,
        scan,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    return {"command": "deps", "depth": selected_depth, **dependency_report(target, all_docs, root, selected_depth)}

def impact(
    path: str,
    *,
    scan: str | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    root = root_for_scan(scan)
    doc, error = _target_or_error("impact", path, root)
    if error is not None:
        return error
    _args, all_docs = _graph_scan_docs(
        root,
        scan,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    return {"command": "impact", **impact_report(doc, all_docs, root, scan)}

def preflight(
    path: str,
    *,
    scan: str | None = None,
    depth: int | None = None,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
) -> dict[str, Any]:
    selected_depth = int(depth or 2)
    if selected_depth < 1:
        return _exit({"command": "preflight", "error": "depth_must_be_positive"}, 2)
    root = root_for_scan(scan)
    doc, error = _target_or_error("preflight", path, root)
    if error is not None:
        return error
    _args, all_docs = _graph_scan_docs(
        root,
        scan,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    report = preflight_report(doc, all_docs, root, selected_depth, scan)
    return _exit(
        {"command": "preflight", "depth": selected_depth, **report},
        1 if report_has_blockers(report) else 0,
    )

def init(
    paths: Iterable[str] | str | None = None,
    *,
    dry_run: bool = False,
    confirm: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **_: Any,
) -> dict[str, Any]:
    _root, _args, docs = _graph_docs(
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    targets = [doc for doc in docs if not doc.has_frontmatter]
    target_paths = [str(doc.path) for doc in targets]
    if dry_run or not confirm:
        return {
            "command": "init",
            "dry_run": bool(dry_run),
            "files_to_modify": target_paths,
            "file_count": len(targets),
            "targets": len(docs),
        }
    template = {"description": "TODO", "depends-on": []}
    write_doc_plan([DocWrite.from_frontmatter(doc, template, doc.body) for doc in targets])
    return {
        "command": "init",
        "targets": len(docs),
        "changed": len(targets),
        "unchanged": len(docs) - len(targets),
        "modified": [str(doc.rel) for doc in targets],
    }

def strip(
    paths: Iterable[str] | str | None = None,
    *,
    also_related_section: bool = False,
    dry_run: bool = False,
    confirm: bool = False,
    path_include: Iterable[str] | str | None = None,
    path_exclude: Iterable[str] | str | None = None,
    **_: Any,
) -> dict[str, Any]:
    _root, _args, docs = _graph_docs(
        paths,
        path_include=path_include,
        path_exclude=path_exclude,
    )
    targets: list[Any] = []
    changes: list[dict[str, Any]] = []
    for doc in docs:
        removed_fields = [key for key in doc.frontmatter if key not in ALLOWED_FIELDS] if doc.has_frontmatter else []
        new_body = doc.body
        section_removed = False
        if also_related_section:
            new_body, section_removed = strip_related_section(doc.body)
        if removed_fields or section_removed:
            targets.append((doc, removed_fields, new_body, section_removed))
            changes.append(
                {
                    "path": str(doc.rel),
                    "removed_fields": removed_fields,
                    "related_section_removed": section_removed,
                }
            )
    target_paths = [str(doc.path) for doc, *_ in targets]
    if dry_run or not confirm:
        return {
            "command": "strip",
            "dry_run": bool(dry_run),
            "files_to_modify": target_paths,
            "file_count": len(targets),
            "also_related_section": also_related_section,
            "changes": changes,
        }
    plan: list[DocWrite] = []
    for doc, _removed_fields, new_body, _section_removed in targets:
        new_data = {key: value for key, value in doc.frontmatter.items() if key in ALLOWED_FIELDS}
        if doc.has_frontmatter:
            plan.append(DocWrite.from_frontmatter(doc, new_data, new_body))
        else:
            plan.append(DocWrite.from_text(doc, new_body))
    write_doc_plan(plan)
    return {
        "command": "strip",
        "targets": len(docs),
        "changed": len(targets),
        "unchanged": len(docs) - len(targets),
        "modified": [str(doc.rel) for doc, *_ in targets],
        "changes": changes,
    }
