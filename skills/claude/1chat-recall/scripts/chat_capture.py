#!/usr/bin/env python3
"""Append a trimmed, classified owner quote to this conversation's recall file.

One file per conversation: _ops/chat-recall/<date>-<hhmmss>-<agent>-<session8>.md.
The frontmatter keeps an inventory of the types and topics used inside, so a
scanning agent can decide from the header alone whether to open the body.

Design invariant: one conversation has exactly one writing agent (subagents
never capture), so each file has a single writer and no locking is needed.
Writes are still atomic (temp file + os.replace) to survive crashes.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import uuid
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
# Each agent may run inside the other's environment (Codex spawned from a
# Claude session and vice versa), so env lookup is scoped per agent.
ENV_BY_AGENT = {
    "claude": ("CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID"),
    "codex": ("CODEX_THREAD_ID", "CODEX_SESSION_ID"),
}
# Handles land in YAML scalars and file names; keep them to word chars plus ./-
HANDLE_RE = re.compile(r"^[\w.\-/]+$")


class CaptureError(RuntimeError):
    pass


def one_line(value: str, field: str) -> str:
    collapsed = " ".join(value.split())
    if not collapsed:
        raise CaptureError(f"{field} is empty")
    return collapsed


def handle(value: str, field: str) -> str:
    collapsed = one_line(value, field)
    if not HANDLE_RE.match(collapsed):
        raise CaptureError(
            f"{field} must be a plain handle (letters, digits, ./-_): {collapsed!r}"
        )
    return collapsed


def canonical_session(value: str) -> str:
    collapsed = one_line(value, "session")
    try:
        canonical = str(uuid.UUID(collapsed))
    except ValueError as error:
        raise CaptureError("session must be a canonical UUID") from error
    if collapsed != canonical:
        raise CaptureError(f"session must be canonical: {canonical}")
    return canonical


def resolve_session(explicit: str | None, agent: str) -> str | None:
    if explicit and explicit.strip():
        return canonical_session(explicit)
    for name in ENV_BY_AGENT.get(agent, ()):
        value = os.environ.get(name, "").strip()
        if value:
            return canonical_session(value)
    return None


def short_session(session: str) -> str:
    return session.split("-")[0][:8]


def frontmatter_end(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        raise CaptureError(
            "recall file has no frontmatter — foreign file? refuse to edit it"
        )
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index
    raise CaptureError("recall file frontmatter is not closed")


def file_session(path: Path) -> str | None:
    """Full session id from a recall file's frontmatter; None if unreadable."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        end = frontmatter_end(lines)
    except (OSError, CaptureError):
        return None
    for line in lines[1:end]:
        if line.startswith("session: "):
            return line[len("session: "):].strip()
    return None


def find_session_file(log_dir: Path, agent: str, session: str, now: datetime) -> Path:
    """Existing file of this exact conversation, or a fresh non-colliding path.

    Codex thread ids are time-ordered (UUIDv7), so the 8-char prefix collides
    between near-simultaneous conversations — a glob match counts only after
    the full `session:` in its frontmatter matches.
    """
    suffix = short_session(session)
    for candidate in sorted(log_dir.glob(f"*-{agent}-{suffix}*.md")):
        if file_session(candidate) == session:
            return candidate
    path = log_dir / f"{now:%Y-%m-%d}-{now:%H%M%S}-{agent}-{suffix}.md"
    if path.exists():
        path = path.with_name(f"{path.stem}-{os.getpid()}.md")
    return path


def entry_line(quote: str, type_: str, topic: str, now: datetime) -> str:
    return f'* {now:%H:%M:%S} — "{quote}" — type: {type_} | topic: {topic}\n'


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


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    os.replace(temp, path)


def create_file(
    path: Path,
    project: str,
    agent: str,
    model: str | None,
    session: str,
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
    lines += [
        f"session: {session}",
        "types:",
        f"  - {type_}",
        "topics:",
        f"  - {topic}",
        "---",
        "",
        f"# Chat recall — {now:%Y-%m-%d} — {agent} {short_session(session)}",
        "",
    ]
    write_atomic(path, "\n".join(lines) + "\n" + entry_line(quote, type_, topic, now))


def append_entry(path: Path, type_: str, topic: str, quote: str, now: datetime) -> bool:
    text = path.read_text(encoding="utf-8-sig")
    if f'"{quote}"' in text:
        return False
    lines = text.splitlines()
    ensure_inventory(lines, "types", type_)
    ensure_inventory(lines, "topics", topic)
    write_atomic(path, "\n".join(lines) + "\n" + entry_line(quote, type_, topic, now))
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
        topic = handle(args.topic, "topic")
        agent = handle(args.agent, "agent")
        model = handle(args.model, "model") if args.model else None
        root = Path(args.project).resolve()
        if not root.is_dir():
            raise CaptureError(f"project root not found: {root}")
        session = resolve_session(args.session, agent)
        if not session:
            checked = ", ".join(ENV_BY_AGENT.get(agent, ())) or "none for this agent"
            raise CaptureError(
                f"session id unknown for agent '{agent}' (env checked: {checked}); "
                "pass --session — a shared day file would mix conversations"
            )
        now = datetime.now()
        path = find_session_file(root / LOG_DIR, agent, session, now)
        if path.exists():
            written = append_entry(path, args.type_, topic, quote, now)
        else:
            create_file(path, root.name, agent, model, session, args.type_, topic, quote, now)
            written = True
        print(f"{'appended to' if written else 'already present in'} {path}")
    except (OSError, CaptureError) as exc:
        print(f"chat-capture: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
