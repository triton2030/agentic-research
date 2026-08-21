#!/usr/bin/env python3
"""Build a frozen source inventory and a deterministic representative subset."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--stage-dir", type=Path, required=True)
    return parser.parse_args()


def frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    return match.group(1).strip().strip('"') if match else ""


def file_record(path: Path, source_dir: Path) -> dict[str, object]:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    match = FRONTMATTER_RE.match(text)
    frontmatter = match.group(1) if match else ""
    date_match = DATE_RE.search(path.name) or DATE_RE.search(frontmatter)
    return {
        "path": path.relative_to(source_dir).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "lines": text.count("\n") + (0 if text.endswith("\n") else 1),
        "date": date_match.group(1) if date_match else None,
        "types": frontmatter_value(frontmatter, "types"),
        "topics": frontmatter_value(frontmatter, "topics"),
    }


def select(records: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, list[str]]]:
    """Select stable stress cases from the frozen corpus by content fingerprints."""
    selected: dict[str, dict[str, object]] = {}
    reasons: dict[str, list[str]] = {}

    def add(reason: str, record: dict[str, object]) -> None:
        path = str(record["path"])
        selected[path] = record
        reasons.setdefault(path, []).append(reason)

    for record in records:
        path = str(record["path"])
        lower = path.lower()
        if "2026-08-21-133152" in lower:
            add("recurring-position-and-change", record)
        elif "2026-08-21-010201" in lower:
            add("later-position-check", record)
        elif "2026-08-20-222832" in lower:
            add("contradiction-or-boundary", record)
        elif "2026-08-14-124028" in lower:
            add("method-and-process-preference", record)
        elif "2026-08-11-163847" in lower:
            add("earlier-position-for-chronology", record)
        elif "2026-07-22-105500" in lower:
            add("stable-preference", record)

    required = {
        "recurring-position-and-change",
        "later-position-check",
        "contradiction-or-boundary",
        "method-and-process-preference",
        "earlier-position-for-chronology",
        "stable-preference",
    }
    found = {reason for values in reasons.values() for reason in values}
    missing = sorted(required - found)
    if missing:
        raise SystemExit(f"selection criteria missing from frozen source: {', '.join(missing)}")

    result = []
    for record in records:
        path = str(record["path"])
        if path in selected:
            result.append({**record, "reasons": reasons[path]})
    return result, {str(record["path"]): reasons[str(record["path"])] for record in result}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    source_dir = args.source_dir.resolve()
    files = sorted(
        path for path in source_dir.glob("*.md") if path.name != "README.md"
    )
    if not files:
        raise SystemExit(f"no holder Markdown files found under {source_dir}")
    records = [file_record(path, source_dir) for path in files]
    selected, reasons = select(records)
    source_bytes = sum(int(record["bytes"]) for record in records)
    inventory_digest = hashlib.sha256(
        "\n".join(
            f"{record['path']}\t{record['sha256']}" for record in records
        ).encode("utf-8")
    ).hexdigest()
    inventory = {
        "schema": "openviking-chat-recall/source-inventory.v1",
        "source_dir": str(source_dir),
        "source_rule": "top-level *.md excluding README.md; sorted by relative path",
        "count": len(records),
        "bytes": source_bytes,
        "inventory_sha256": inventory_digest,
        "files": records,
    }
    selection = {
        "schema": "openviking-chat-recall/pilot-selection.v1",
        "rule": "explicit frozen holder fingerprints selected for recurrence, chronology, contradiction, method and preference",
        "source_inventory_sha256": inventory_digest,
        "count": len(selected),
        "files": selected,
        "reasons": reasons,
    }
    write_json(args.inventory, inventory)
    write_json(args.selection, selection)
    if args.stage_dir.exists():
        for child in args.stage_dir.iterdir():
            if child.is_file() or child.is_symlink():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)
    args.stage_dir.mkdir(parents=True, exist_ok=True)
    for record in selected:
        source = source_dir / str(record["path"])
        target = args.stage_dir / str(record["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    print(json.dumps({"inventory": len(records), "selected": len(selected), "inventory_sha256": inventory_digest}))


if __name__ == "__main__":
    main()
