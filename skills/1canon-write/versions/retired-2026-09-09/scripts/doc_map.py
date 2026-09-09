#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Print a read-only Markdown map of a documentation directory."""

import argparse
import html
from pathlib import Path
import sys

import yaml


def metadata(path):
    """Read only YAML frontmatter; never infer metadata from the body."""
    with path.open(encoding="utf-8-sig") as stream:
        if stream.readline().strip() != "---":
            return {}
        lines = []
        for line in stream:
            if line.strip() in ("---", "..."):
                result = yaml.safe_load("".join(lines))
                if result is None:
                    return {}
                if not isinstance(result, dict):
                    raise ValueError("frontmatter must be a mapping")
                return result
            lines.append(line)
    raise ValueError("unclosed frontmatter")


def cell(text):
    """Keep arbitrary metadata inside one literal Markdown table cell."""
    text = html.escape(" ".join(text.split()))
    for character in ("\\", "|", "`", "*", "_", "[", "]"):
        text = text.replace(character, "\\" + character)
    return text


def entries(root):
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        yield path
        if path.is_dir() and not path.is_symlink():
            yield from entries(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Includes hidden entries and empty directories; symlinks are listed, "
        "not followed. Markdown (.md/.markdown) metadata only. "
        "Exit codes: 0 complete, 1 metadata gaps/read errors, 2 invalid root. "
        "Writes only stdout/stderr; no map file or source edits."
    ))
    parser.add_argument("root", type=Path, help="Documentation directory, e.g. _canon or _docs")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    print(f"# Map: {cell(root.name)}\n")
    print("| Path | Description | Aliases |")
    print("| --- | --- | --- |")
    problems = 0
    count = 0
    try:
        for path in entries(root):
            relative = path.relative_to(root).as_posix()
            description, aliases = "—", "—"
            if path.is_symlink():
                description = "[symlink; not followed]"
            elif path.is_dir():
                relative += "/"
            elif path.suffix.lower() in (".md", ".markdown"):
                try:
                    fields = metadata(path)
                    description = fields.get("description")
                    if not isinstance(description, str) or not description.strip():
                        description = "[missing/invalid description]"
                        problems += 1
                    values = fields.get("aliases")
                    if not isinstance(values, list) or any(
                        not isinstance(value, str) or not value.strip() for value in values
                    ):
                        aliases = "[missing/invalid aliases]"
                        problems += 1
                    else:
                        aliases = "; ".join(values) if values else "[]"
                except (OSError, UnicodeError, ValueError, yaml.YAMLError) as exc:
                    description, aliases = "[metadata unreadable]", "—"
                    print(f"{relative}: {exc}", file=sys.stderr)
                    problems += 1
            else:
                description = "[non-Markdown]"
            print(f"| {cell(relative)} | {cell(description)} | {cell(aliases)} |")
            count += 1
    except OSError as exc:
        print(f"Incomplete traversal: {exc}", file=sys.stderr)
        problems += 1

    print(f"\nEntries: {count}. Issues: {problems}.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
