#!/usr/bin/env python3
"""Append a trimmed, classified owner quote to this conversation's recall file.

One file per conversation: _ops/chat-recall/<date>-<hhmmss>-<agent>-<session8>.md.
The frontmatter keeps an inventory of the types and topics used inside, so a
scanning agent can decide from the header alone whether to open the body.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


LOG_DIR = Path("_ops/chat-recall")
TYPES = (
    "решение",
    "коррекция",
    "предпочтение",
    "идея",
    "критерий",
    "правило-кандидат",
    "обо-мне",
    "факт",
)
SESSION_ENV_VARS = (
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "CODEX_THREAD_ID",
    "CODEX_SESSION_ID",
)


class CaptureError(RuntimeError):
    pass


def one_line(value: str, field: str) -> str:
    collapsed = " ".join(value.split())
    if not collapsed:
        raise CaptureError(f"{field} is empty")
    return collapsed


def resolve_session(explicit: str | None) -> str | None:
    if explicit and explicit.strip():
        return explicit.strip()
    for name in SESSION_ENV_VARS:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def short_session(session: str | None) -> str:
    return session.split("-")[0][:8] if session else "nosession"


def find_session_file(log_dir: Path, agent: str, session: str | None, now: datetime) -> Path:
    suffix = short_session(session)
    if session:
        pattern = f"*-{agent}-{suffix}.md"
    else:
        # Without a session id the best stable unit is one file per agent per day.
        pattern = f"{now:%Y-%m-%d}-*-{agent}-{suffix}.md"
    existing = sorted(log_dir.glob(pattern))
    if existing:
        return existing[0]
    return log_dir / f"{now:%Y-%m-%d}-{now:%H%M%S}-{agent}-{suffix}.md"


def entry_line(quote: str, type_: str, topic: str, now: datetime) -> str:
    return f'* {now:%H:%M:%S} — "{quote}" — тип: {type_} | тема: {topic}\n'


def frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0] != "---":
        raise CaptureError("recall file has no frontmatter")
    for index in range(1, len(lines)):
        if lines[index] == "---":
            return index
    raise CaptureError("recall file frontmatter is not closed")


def ensure_inventory(lines: list[str], key: str, value: str) -> None:
    """Add value to the frontmatter list `key`, creating the key if missing."""
    end = frontmatter_end(lines)
    header = f"{key}:"
    if header not in lines[:end]:
        lines.insert(end, header)
        end += 1
    index = lines.index(header) + 1
    while index < end and lines[index].startswith("  - "):
        if lines[index][4:].strip() == value:
            return
        index += 1
    lines.insert(index, f"  - {value}")


def create_file(
    path: Path,
    project: str,
    agent: str,
    model: str | None,
    session: str | None,
    type_: str,
    topic: str,
    quote: str,
    now: datetime,
) -> None:
    lines = [
        "---",
        f"project: {project}",
        f"date: {now:%Y-%m-%d}",
        f"agent: {agent}",
    ]
    if model:
        lines.append(f"model: {model}")
    if session:
        lines.append(f"session: {session}")
    lines += [
        "types:",
        f"  - {type_}",
        "topics:",
        f"  - {topic}",
        "---",
        "",
        f"# Chat recall — {now:%Y-%m-%d} — {agent} {short_session(session)}",
        "",
    ]
    text = "\n".join(lines) + "\n" + entry_line(quote, type_, topic, now)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_entry(path: Path, type_: str, topic: str, quote: str, now: datetime) -> bool:
    text = path.read_text(encoding="utf-8")
    if f'"{quote}"' in text:
        return False
    lines = text.splitlines()
    ensure_inventory(lines, "types", type_)
    ensure_inventory(lines, "topics", topic)
    rebuilt = "\n".join(lines) + "\n" + entry_line(quote, type_, topic, now)
    path.write_text(rebuilt, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quote", required=True, help="trimmed verbatim owner words")
    parser.add_argument(
        "--type", required=True, dest="type_", choices=TYPES,
        help="classification from the closed list",
    )
    parser.add_argument(
        "--topic", required=True,
        help="existing handle: skill/project/folder name, or мой-workflow",
    )
    parser.add_argument("--project", default=".", help="project root")
    parser.add_argument("--agent", default="claude", help="engine writing the file")
    parser.add_argument("--model", help="model id if known, e.g. claude-fable-5")
    parser.add_argument("--session", help="conversation id; defaults to session env vars")
    args = parser.parse_args()
    try:
        quote = one_line(args.quote, "quote")
        topic = one_line(args.topic, "topic")
        root = Path(args.project).resolve()
        if not root.is_dir():
            raise CaptureError(f"project root not found: {root}")
        session = resolve_session(args.session)
        now = datetime.now()
        path = find_session_file(root / LOG_DIR, args.agent, session, now)
        if path.exists():
            written = append_entry(path, args.type_, topic, quote, now)
        else:
            create_file(
                path, root.name, args.agent, args.model, session,
                args.type_, topic, quote, now,
            )
            written = True
        print(f"{'appended to' if written else 'already present in'} {path}")
    except (OSError, CaptureError) as exc:
        print(f"chat-capture: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
