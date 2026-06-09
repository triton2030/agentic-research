#!/usr/bin/env python3
"""Migrate graph frontmatter from read/edit pair to depends-on.

The migration is intentionally narrow:
- rename top-level ``read-before-edit`` to ``depends-on``;
- remove top-level ``edit-after-edit``;
- preserve every other frontmatter key and the Markdown body.

Use ``--config-domain graph`` from a corpus root to apply project-level
``.md-tools.toml`` graph filters before selecting files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required for graph frontmatter migration") from exc

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from navigator.config import resolve_filters_for_domain  # noqa: E402
from navigator.graph_core import iter_markdown, safe_rel, split_frontmatter  # noqa: E402
from navigator.markdown_io import parse_frontmatter as parse_frontmatter_tolerant  # noqa: E402


OLD_READ = "read-before-edit"
OLD_EDIT = "edit-after-edit"
NEW_EDGE = "depends-on"


def normalize_links(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        out: list[str] = []
        for item in value:
            out.extend(normalize_links(item))
        return out
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    return [str(value)]


def merge_links(primary: Any, extra: Any) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for item in [*normalize_links(primary), *normalize_links(extra)]:
        if item in seen:
            continue
        seen.add(item)
        merged.append(item)
    return merged


def parse_frontmatter(raw_lines: list[str], path: Path) -> dict[str, Any]:
    text = "\n".join(raw_lines)
    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        loaded = parse_frontmatter_tolerant(["---", *raw_lines, "---"])
        if not loaded:
            raise SystemExit(f"{path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(loaded, dict):
        raise SystemExit(f"{path}: frontmatter must be a YAML mapping")
    return dict(loaded)


def migrate_data(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    changed = False
    actions: dict[str, Any] = {
        "renamed_read_before_edit": False,
        "removed_edit_after_edit": False,
        "merged_existing_depends_on": False,
    }
    read_values = data.get(OLD_READ)
    has_old_read = OLD_READ in data
    has_new_edge = NEW_EDGE in data
    new_data: dict[str, Any] = {}

    for key, value in data.items():
        if key == OLD_READ:
            changed = True
            actions["renamed_read_before_edit"] = True
            if not has_new_edge:
                new_data[NEW_EDGE] = normalize_links(value)
            continue
        if key == OLD_EDIT:
            changed = True
            actions["removed_edit_after_edit"] = True
            continue
        if key == NEW_EDGE and has_old_read:
            merged = merge_links(value, read_values)
            new_data[key] = merged
            if merged != normalize_links(value):
                changed = True
                actions["merged_existing_depends_on"] = True
            continue
        new_data[key] = value

    actions["changed"] = changed
    return new_data, actions


def render_doc(frontmatter: dict[str, Any], body: str) -> str:
    dumped = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    text = f"---\n{dumped}\n---\n"
    if body:
        text += body if body.startswith("\n") else body
    return text


def atomic_write(path: Path, text: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        tmp_path = Path(handle.name)
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)


def migrate_file(path: Path) -> tuple[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    has_frontmatter, raw_frontmatter, body = split_frontmatter(text)
    if not has_frontmatter:
        return text, {"changed": False, "no_frontmatter": True}
    data = parse_frontmatter(raw_frontmatter, path)
    migrated, actions = migrate_data(data)
    if not actions["changed"]:
        return text, {**actions, "no_frontmatter": False}
    return render_doc(migrated, body), {**actions, "no_frontmatter": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="Markdown files or directories")
    parser.add_argument("--root", default=".", help="Corpus root for relative paths and config filters")
    parser.add_argument(
        "--config-domain",
        choices=("none", "graph", "index"),
        default="none",
        help="Apply .md-tools.toml filters for this domain before selecting files",
    )
    parser.add_argument("--path-include", action="append", default=[], help="Additional include glob")
    parser.add_argument("--path-exclude", action="append", default=[], help="Additional exclude glob")
    parser.add_argument("--confirm", action="store_true", help="Write changes. Without this, dry-run only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    include = list(args.path_include)
    exclude = list(args.path_exclude)
    if args.config_domain != "none":
        include, exclude = resolve_filters_for_domain(
            root,
            domain=args.config_domain,
            path_include=include,
            path_exclude=exclude,
        )

    files = iter_markdown(args.paths, root, include=include, exclude=exclude)
    rows: list[dict[str, Any]] = []
    changed_payloads: list[tuple[Path, str]] = []
    counts = {
        "scanned": len(files),
        "changed": 0,
        "no_frontmatter": 0,
        "renamed_read_before_edit": 0,
        "removed_edit_after_edit": 0,
        "merged_existing_depends_on": 0,
    }
    for path in files:
        new_text, actions = migrate_file(path)
        rel = str(safe_rel(path, root))
        if actions.get("no_frontmatter"):
            counts["no_frontmatter"] += 1
        if actions.get("changed"):
            counts["changed"] += 1
            changed_payloads.append((path, new_text))
            for key in ("renamed_read_before_edit", "removed_edit_after_edit", "merged_existing_depends_on"):
                if actions.get(key):
                    counts[key] += 1
            rows.append({"path": rel, **actions})

    if args.confirm:
        for path, new_text in changed_payloads:
            atomic_write(path, new_text)

    summary = {
        "command": "migrate-graph-frontmatter",
        "dry_run": not args.confirm,
        "root": str(root),
        "config_domain": args.config_domain,
        "counts": counts,
        "files": rows,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        mode = "DRY-RUN" if not args.confirm else "WROTE"
        print(f"{mode} graph frontmatter migration")
        print(json.dumps(counts, ensure_ascii=False, indent=2))
        for row in rows:
            print(row["path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
