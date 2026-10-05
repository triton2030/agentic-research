#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Print a read-only Markdown map of a documentation directory."""

import argparse
import fnmatch
import html
from pathlib import Path
import sys

import yaml


INSTRUCTIONS = frozenset({"AGENTS.md", "CLAUDE.md"})
MARKDOWN_SUFFIXES = frozenset({".md", ".markdown"})


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


def children(folder, root, excludes):
    """Filter before recursion; match case-sensitive names and POSIX root paths."""
    for path in sorted(folder.iterdir(), key=lambda item: item.name):
        relative = path.relative_to(root).as_posix()
        if not any(
            fnmatch.fnmatchcase(path.name, pattern)
            or fnmatch.fnmatchcase(relative, pattern)
            for pattern in excludes
        ):
            yield path


def entries(root, excludes=(), folder=None):
    for path in children(folder if folder is not None else root, root, excludes):
        yield path
        if path.is_dir() and not path.is_symlink():
            yield from entries(root, excludes, path)


def folder_summary(folder, root, excludes):
    """Count immediate Markdown files and directories, excluding instructions/links."""
    files = folders = 0
    for path in children(folder, root, excludes):
        if path.is_symlink():
            continue
        if path.is_dir():
            folders += 1
        elif (
            path.is_file()
            and path.suffix.lower() in MARKDOWN_SUFFIXES
            and path.name not in INSTRUCTIONS
        ):
            files += 1
    mixed = "; mixed" if files and folders else ""
    return f"files: {files}; dirs: {folders}{mixed}"


def character_count(path):
    """Unicode code points, without initial BOM; CRLF and CR normalize to LF."""
    return len(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        "Includes hidden entries and empty directories; symlinks are listed, "
        "not followed. Markdown (.md/.markdown) metadata only unless --chars. "
        "AGENTS.md and CLAUDE.md are instructions; no metadata required. "
        "Exit codes: 0 complete, 1 metadata gaps/read errors, 2 invalid root. "
        "Writes only stdout/stderr; no map file or source edits."
    ))
    parser.add_argument("root", type=Path, help="Documentation directory, e.g. _docs")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB", help=(
        "Repeatable case-sensitive glob matched against entry name and root-relative "
        "POSIX path (without trailing slash); matching directories are pruned before "
        "traversal. Quote globs to prevent shell expansion. Hidden entries remain "
        "visible unless explicitly excluded. Uses fnmatch: * crosses /, [abc] is "
        "a character class; a trailing / in the glob never matches."
    ))
    parser.add_argument("--chars", action="store_true", help=(
        "Add Chars for Markdown files, including instructions: Unicode code points "
        "in the entire UTF-8 text, not bytes or graphemes; initial BOM is removed, "
        "CRLF and CR normalize to one LF. Symlinks are never read."
    ))
    parser.add_argument("--folder-summary", action="store_true", help=(
        "Add Folder summary, including ./ for the root: immediate product files "
        "(regular .md/.markdown files except AGENTS.md/CLAUDE.md) and directories; both means "
        "mixed, an observation, not a validation issue. Excluded entries and "
        "symlinks do not count."
    ))
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    print(f"# Map: {cell(root.name)}\n")
    columns = ["Path", "Description", "Aliases"]
    if args.chars:
        columns.append("Chars")
    if args.folder_summary:
        columns.append("Folder summary")
    print("| " + " | ".join(columns) + " |")
    print("| " + " | ".join("---" for _ in columns) + " |")
    problems = 0
    count = 0
    try:
        if args.folder_summary:
            row = ["./", "—", "—"]
            if args.chars:
                row.append("—")
            try:
                row.append(folder_summary(root, root, args.exclude))
            except OSError:
                row.append("[summary unreadable]")
                print("| " + " | ".join(cell(value) for value in row) + " |")
                raise
            print("| " + " | ".join(cell(value) for value in row) + " |")
        for path in entries(root, args.exclude):
            relative = path.relative_to(root).as_posix()
            description, aliases = "—", "—"
            if path.is_symlink():
                description = "[symlink; not followed]"
            elif path.is_dir():
                relative += "/"
            elif path.name in INSTRUCTIONS:
                description = "[instruction]"
                try:
                    value = metadata(path).get("description")
                    if isinstance(value, str) and value.strip():
                        description = value
                except (OSError, UnicodeError, ValueError, yaml.YAMLError):
                    pass
            elif path.suffix.lower() in MARKDOWN_SUFFIXES:
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
            row = [relative, description, aliases]
            if args.chars:
                chars = "—"
                if not path.is_symlink() and path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES:
                    try:
                        chars = str(character_count(path))
                    except (OSError, UnicodeError) as exc:
                        chars = "[text unreadable]"
                        print(f"{relative}: {exc}", file=sys.stderr)
                        problems += 1
                row.append(chars)
            if args.folder_summary:
                summary = "—"
                if path.is_dir() and not path.is_symlink():
                    try:
                        summary = folder_summary(path, root, args.exclude)
                    except OSError:
                        row.append("[summary unreadable]")
                        print("| " + " | ".join(cell(value) for value in row) + " |")
                        count += 1
                        raise
                row.append(summary)
            print("| " + " | ".join(cell(value) for value in row) + " |")
            count += 1
    except OSError as exc:
        print(f"Incomplete traversal: {exc}", file=sys.stderr)
        problems += 1

    print(f"\nEntries: {count}. Issues: {problems}.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
