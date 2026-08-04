#!/usr/bin/env python3
"""Append one owner-memory record and preserve its non-inferable context."""

from __future__ import annotations

import argparse
import os
import re
import sys
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import NamedTuple

from recall_metadata import (
    REPAIR_TOPIC,
    REPAIR_TYPE,
    TOPIC_DESCRIPTIONS,
    TOPICS,
    TYPE_DESCRIPTIONS,
    TYPES,
)

LOG_DIR = Path("_ops/chat-recall")
KINDS = ("quote", "selection", "note")
PRECISIONS = ("exact", "minute", "date", "unknown")
TIMESTAMP_SOURCES = (
    "transcript",
    "turn-context",
    "repaired",
    "raw-time",
    "filename",
    "frontmatter",
    "unknown",
)
NON_EXACT_SOURCES = {
    "turn-context",
    "raw-time",
    "filename",
    "frontmatter",
    "unknown",
}
ENV_BY_AGENT = {
    "claude": ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"),
    "codex": ("CODEX_THREAD_ID", "CODEX_SESSION_ID"),
}
HANDLE_RE = re.compile(r"^[\w.\-/]+$")
ENTRY_START_RE = re.compile(r"^\*\s+(?P<timestamp>.+?)\s+—\s+")
CONTEXT_LINK_RE = re.compile(
    r"(?:https?://|file://|www\.|\[[^\]]+\]\([^)]+\))", re.IGNORECASE
)
MAX_CONTEXT_NOTE_CHARS = 300


class CaptureError(RuntimeError):
    """Expected validation or corpus failure."""


class SourceTimestamp(NamedTuple):
    rendered: str
    precision: str
    ordering: datetime | None
    file_when: datetime


def one_line(value: str, field: str) -> str:
    collapsed = " ".join(value.split())
    if not collapsed:
        raise CaptureError(f"{field} is empty")
    return collapsed


def context_note(value: str) -> str:
    collapsed = one_line(value, "context note")
    if len(collapsed) > MAX_CONTEXT_NOTE_CHARS:
        raise CaptureError(
            f"context note must be at most {MAX_CONTEXT_NOTE_CHARS} characters"
        )
    if "|" in collapsed:
        raise CaptureError("context note cannot contain the metadata delimiter '|'")
    if CONTEXT_LINK_RE.search(collapsed):
        raise CaptureError("context note must be inline context, not a link")
    return collapsed


def handle(value: str, field: str) -> str:
    collapsed = one_line(value, field)
    if not HANDLE_RE.fullmatch(collapsed):
        raise CaptureError(
            f"{field} must be a plain handle (letters, digits, ./-_): {collapsed!r}"
        )
    return collapsed


def metadata_choice(
    value: str,
    field: str,
    allowed: tuple[str, ...],
) -> str:
    selected = handle(value, field)
    if selected not in allowed:
        raise CaptureError(
            f"{field} is outside the controlled vocabulary: {selected!r}. "
            "Run --list-metadata and choose one listed value."
        )
    return selected


def validate_metadata(type_: str, topic: str, kind: str) -> None:
    uses_repair_metadata = type_ == REPAIR_TYPE or topic == REPAIR_TOPIC
    if uses_repair_metadata and kind != "note":
        raise CaptureError(
            "repair metadata requires --kind note; classify a fresh quote instead"
        )


def render_metadata_vocabulary() -> str:
    lines = ["Types:"]
    lines.extend(f"  {name}: {meaning}" for name, meaning in TYPE_DESCRIPTIONS.items())
    lines.append(f"  {REPAIR_TYPE}: repair-only sentinel")
    lines.append("")
    lines.append("Topics:")
    lines.extend(
        f"  {name}: {meaning}" for name, meaning in TOPIC_DESCRIPTIONS.items()
    )
    lines.append(f"  {REPAIR_TOPIC}: repair-only sentinel")
    return "\n".join(lines)


class PrintMetadataAction(argparse.Action):
    """Print the controlled vocabulary without requiring capture arguments."""

    def __init__(self, option_strings: list[str], dest: str, **kwargs: object) -> None:
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: object,
        option_string: str | None = None,
    ) -> None:
        del namespace, values, option_string
        print(render_metadata_vocabulary())
        parser.exit()


def canonical_session(value: str) -> str:
    collapsed = one_line(value, "session")
    try:
        canonical = str(uuid.UUID(collapsed))
    except ValueError as error:
        raise CaptureError("session must be a canonical UUID") from error
    if collapsed != canonical:
        raise CaptureError(f"session must be canonical: {canonical}")
    return canonical


def source_timestamp(value: str, precision: str | None = None) -> SourceTimestamp:
    raw = one_line(value, "source timestamp")
    now = datetime.now().astimezone()
    inferred: str
    ordering: datetime | None
    rendered: str
    if raw.casefold() == "unknown":
        inferred, ordering, rendered = "unknown", None, "unknown"
    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        try:
            parsed_date = date.fromisoformat(raw)
        except ValueError as error:
            raise CaptureError("source timestamp has an invalid date") from error
        inferred = "date"
        ordering = datetime.combine(parsed_date, datetime.min.time()).astimezone()
        rendered = raw
    else:
        normalized = raw[:-1] + "+00:00" if raw.endswith(("Z", "z")) else raw
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as error:
            raise CaptureError(
                "source timestamp must be ISO 8601, a date, or unknown"
            ) from error
        ordering = parsed
        rendered = parsed.isoformat()
        if parsed.tzinfo is not None and parsed.utcoffset() is not None:
            inferred = "exact"
        else:
            inferred = "minute"
            ordering = parsed.astimezone()
    resolved = precision or inferred
    if resolved not in PRECISIONS:
        raise CaptureError(f"timestamp precision must be one of: {', '.join(PRECISIONS)}")
    if resolved == "exact" and inferred != "exact":
        raise CaptureError("exact precision requires a timezone-aware ISO timestamp")
    if inferred == "unknown" and resolved != "unknown":
        raise CaptureError("unknown timestamp requires unknown precision")
    return SourceTimestamp(
        rendered=rendered,
        precision=resolved,
        ordering=ordering,
        file_when=ordering or now,
    )


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
        raise CaptureError("recall file has no frontmatter — foreign file? refuse to edit it")
    for index, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return index
    raise CaptureError("recall file frontmatter is not closed")


def file_session(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        end = frontmatter_end(lines)
    except (OSError, CaptureError):
        return None
    for line in lines[1:end]:
        if line.startswith("session: "):
            return line.removeprefix("session: ").strip()
    return None


def _entry_times(text: str, file_date: str) -> list[SourceTimestamp]:
    result: list[SourceTimestamp] = []
    for line in text.splitlines():
        match = ENTRY_START_RE.match(line)
        if not match:
            continue
        raw = match.group("timestamp")
        try:
            result.append(source_timestamp(raw))
        except CaptureError:
            if re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?", raw) and file_date:
                result.append(source_timestamp(file_date, "minute"))
            else:
                result.append(source_timestamp("unknown"))
    return result


def _frontmatter_date(text: str) -> str:
    match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.MULTILINE)
    return match.group(1) if match else ""


def dated_path(
    log_dir: Path,
    agent: str,
    session: str,
    source: SourceTimestamp,
    *,
    current: Path | None = None,
) -> Path:
    local_when = source.file_when.astimezone()
    base = log_dir / f"{local_when:%Y-%m-%d-%H%M%S}-{agent}-{short_session(session)}.md"
    if current and current.parent == log_dir and current.name.startswith(base.stem + "-"):
        return current
    if not base.exists() or base == current:
        return base
    if file_session(base) == session:
        return base
    return base.with_name(f"{base.stem}-{os.getpid()}.md")


def find_session_file(
    log_dir: Path, agent: str, session: str, source: SourceTimestamp
) -> Path:
    matches = [
        path
        for path in sorted(log_dir.glob(f"*-{agent}-{short_session(session)}*.md"))
        if file_session(path) == session
    ]
    if len(matches) > 1:
        raise CaptureError(f"multiple recall files for session {session}; repair first")
    return matches[0] if matches else dated_path(log_dir, agent, session, source)


def _entry_line(
    quote: str,
    type_: str,
    topic: str,
    source: SourceTimestamp,
    timestamp_source: str,
    source_ref: str | None,
    kind: str,
    context: str | None = None,
) -> str:
    fields = []
    if kind != "quote":
        fields.append(f"kind: {kind}")
    fields.extend((f"type: {type_}", f"topic: {topic}"))
    if context:
        fields.append(f"context-note: {context}")
    if source.precision != "exact" or timestamp_source != "transcript":
        fields.extend(
            (f"source: {timestamp_source}", f"precision: {source.precision}")
        )
        if source_ref:
            fields.append(f"source-ref: {source_ref}")
    return f'* {source.rendered} — "{quote}" — ' + " | ".join(fields) + "\n"


def ensure_inventory(lines: list[str], key: str, value: str) -> None:
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


def _set_file_date(lines: list[str], source_start: datetime) -> None:
    local = source_start.astimezone()
    end = frontmatter_end(lines)
    for index in range(1, end):
        if lines[index].startswith("date: "):
            lines[index] = f"date: {local:%Y-%m-%d}"
            break
    for index, line in enumerate(lines):
        if line.startswith("# Chat recall — "):
            pieces = line.split(" — ", 2)
            if len(pieces) == 3:
                lines[index] = f"{pieces[0]} — {local:%Y-%m-%d} — {pieces[2]}"
            break


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _earliest_known(text: str, incoming: SourceTimestamp) -> datetime:
    known = [
        item.ordering
        for item in _entry_times(text, _frontmatter_date(text))
        if item.ordering is not None
    ]
    if incoming.ordering is not None:
        known.append(incoming.ordering)
    return min(known) if known else incoming.file_when


def create_file(
    path: Path,
    project: str,
    agent: str,
    model: str | None,
    session: str,
    type_: str,
    topic: str,
    quote: str,
    source: SourceTimestamp,
    timestamp_source: str,
    source_ref: str | None,
    kind: str,
    context: str | None = None,
) -> None:
    local = source.file_when.astimezone()
    lines = [
        "---",
        f"project: {project}",
        f"date: {local:%Y-%m-%d}",
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
        f"# Chat recall — {local:%Y-%m-%d} — {agent} {short_session(session)}",
        "",
        _entry_line(
            quote,
            type_,
            topic,
            source,
            timestamp_source,
            source_ref,
            kind,
            context,
        ).rstrip(),
    ]
    write_atomic(path, "\n".join(lines) + "\n")


def append_entry(
    path: Path,
    agent: str,
    session: str,
    type_: str,
    topic: str,
    quote: str,
    source: SourceTimestamp,
    timestamp_source: str = "transcript",
    source_ref: str | None = None,
    kind: str = "quote",
    context: str | None = None,
) -> tuple[bool, Path]:
    text = path.read_text(encoding="utf-8-sig")
    if f'"{quote}"' in text:
        return False, path
    lines = text.splitlines()
    ensure_inventory(lines, "types", type_)
    ensure_inventory(lines, "topics", topic)
    earliest = _earliest_known(text, source)
    _set_file_date(lines, earliest)
    target = dated_path(
        path.parent,
        agent,
        session,
        SourceTimestamp(earliest.isoformat(), "exact", earliest, earliest),
        current=path,
    )
    rendered = "\n".join(lines) + "\n" + _entry_line(
        quote,
        type_,
        topic,
        source,
        timestamp_source,
        source_ref,
        kind,
        context,
    )
    write_atomic(target, rendered)
    if target != path:
        path.unlink()
    return True, target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-metadata",
        action=PrintMetadataAction,
    )
    parser.add_argument("--quote", required=True)
    parser.add_argument("--type", required=True, dest="type_")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--kind", choices=KINDS, default="quote")
    parser.add_argument("--source-timestamp", required=True)
    parser.add_argument(
        "--timestamp-source", choices=TIMESTAMP_SOURCES, default="transcript"
    )
    parser.add_argument("--timestamp-precision", choices=PRECISIONS)
    parser.add_argument("--source-ref")
    parser.add_argument(
        "--context-note",
        help=(
            "capture a useful non-inferable context delta; omit only when "
            "quote plus type/topic is self-contained; links rejected"
        ),
    )
    parser.add_argument("--project", default=".")
    parser.add_argument("--agent", default="claude")
    parser.add_argument("--model")
    parser.add_argument("--session")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        quote = one_line(args.quote, "quote")
        type_ = metadata_choice(args.type_, "type", TYPES)
        topic = metadata_choice(args.topic, "topic", TOPICS)
        validate_metadata(type_, topic, args.kind)
        agent = handle(args.agent, "agent")
        model = handle(args.model, "model") if args.model else None
        timestamp_source = handle(args.timestamp_source, "timestamp source")
        source_ref = one_line(args.source_ref, "source ref") if args.source_ref else None
        context = context_note(args.context_note) if args.context_note else None
        if context and args.kind == "note":
            raise CaptureError("--context-note cannot be attached to --kind note")
        source = source_timestamp(args.source_timestamp, args.timestamp_precision)
        if source.precision != "exact" and timestamp_source == "transcript":
            raise CaptureError(
                "approximate/unknown timestamp requires --timestamp-source"
            )
        if timestamp_source in NON_EXACT_SOURCES and source.precision == "exact":
            raise CaptureError(
                f"{timestamp_source} cannot be source-exact; "
                "pass --timestamp-precision minute or date"
            )
        root = Path(args.project).resolve()
        if not root.is_dir():
            raise CaptureError(f"project root not found: {root}")
        session = resolve_session(args.session, agent)
        if not session:
            checked = ", ".join(ENV_BY_AGENT.get(agent, ())) or "none"
            raise CaptureError(
                f"session id unknown for agent '{agent}' (env checked: {checked})"
            )
        path = find_session_file(root / LOG_DIR, agent, session, source)
        if path.exists():
            written, path = append_entry(
                path,
                agent,
                session,
                type_,
                topic,
                quote,
                source,
                timestamp_source,
                source_ref,
                args.kind,
                context,
            )
        else:
            create_file(
                path,
                root.name,
                agent,
                model,
                session,
                type_,
                topic,
                quote,
                source,
                timestamp_source,
                source_ref,
                args.kind,
                context,
            )
            written = True
        print(f"{'appended to' if written else 'already present in'} {path}")
        return 0
    except (CaptureError, OSError) as error:
        print(f"chat-capture: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
