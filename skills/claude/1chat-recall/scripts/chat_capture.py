#!/usr/bin/env python3
"""Append a trimmed verbatim owner quote to the project's chat-recall log."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path


LOG_DIR = Path("_ops/chat-recall")


class CaptureError(RuntimeError):
    pass


def one_line(value: str, field: str) -> str:
    collapsed = " ".join(value.split())
    if not collapsed:
        raise CaptureError(f"{field} is empty")
    return collapsed


def day_file(root: Path, now: datetime) -> Path:
    return root / LOG_DIR / f"{now:%Y-%m-%d}.md"


def entry(quote: str, context: str | None, now: datetime) -> str:
    line = f'* {now:%H:%M} — "{quote}"'
    return f"{line} — контекст: {context}\n" if context else f"{line}\n"


def append(path: Path, text: str, header: str) -> bool:
    created = not path.exists()
    if created:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {header}\n\n", encoding="utf-8")
    existing = path.read_text(encoding="utf-8")
    if text in existing:
        return False
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quote", required=True, help="trimmed verbatim owner words")
    parser.add_argument("--context", help="short label of what it was about")
    parser.add_argument("--project", default=".", help="project root")
    args = parser.parse_args()
    try:
        quote = one_line(args.quote, "quote")
        context = one_line(args.context, "context") if args.context else None
        root = Path(args.project).resolve()
        if not root.is_dir():
            raise CaptureError(f"project root not found: {root}")
        now = datetime.now()
        path = day_file(root, now)
        written = append(path, entry(quote, context, now), f"Chat recall — {now:%Y-%m-%d}")
        print(f"{'appended to' if written else 'already present in'} {path}")
    except (OSError, CaptureError) as exc:
        print(f"chat-capture: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
