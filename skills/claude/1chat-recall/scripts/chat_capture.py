#!/usr/bin/env python3
"""Append one caller-confirmed owner excerpt and preserve its non-inferable context."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import uuid
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import NamedTuple

from recall_metadata import (
    REPAIR_TOPIC,
    REPAIR_TYPE,
    RETIRED_HEADING_RE,
    TOPIC_ROW_RE,
    TYPE_DESCRIPTIONS,
    TYPES,
    TopicMap,
    corpus_topics,
    parse_topic_map,
)

LOG_DIR = Path("_ops/chat-recall")


def default_project() -> str:
    """Capture and retrieval must resolve the same corpus.

    Retrieval and integrity address the corpus as
    `${TARGET_PROJECT_ROOT:-$PWD}/_ops/chat-recall`. Capture honours the same
    variable so that a caller working on one project cannot silently write to
    the corpus of another. An explicit `--project` still wins.
    """
    return os.environ.get("TARGET_PROJECT_ROOT") or "."


def resolve_log_dir(root: Path) -> Path:
    """The corpus is one flat folder of conversation files."""
    return root / LOG_DIR


TOPIC_MAP = LOG_DIR / "topics.md"
ANCHOR_RE = re.compile(r"^(?P<file>[\w.\-]+\.md)(?:#L|:)(?P<line>\d+)$")


class FileState(NamedTuple):
    """The exact pre-operation state of one transaction file."""

    text: str | None
    mode: int | None


def read_topic_map(root: Path) -> TopicMap | None:
    """Parse the topic map, when this project keeps one."""
    return parse_topic_map(root / TOPIC_MAP)


def add_topic_row(topic_map: TopicMap, topic: str, boundary: str) -> None:
    """Record a new topic in the map, in the same turn as the quote."""
    lines = topic_map.path.read_text(encoding="utf-8-sig").splitlines()
    row = f"- `{topic}` — {boundary}"
    rows = [
        index
        for index, line in enumerate(lines)
        if TOPIC_ROW_RE.match(line) and not _after_retired(lines, index)
    ]
    if not rows:
        raise CaptureError(f"topic map has no topic rows to extend: {topic_map.path}")
    following = [
        index
        for index in rows
        if TOPIC_ROW_RE.match(lines[index])["handle"] > topic  # type: ignore[index]
    ]
    lines.insert(following[0] if following else rows[-1] + 1, row)
    write_atomic(topic_map.path, "\n".join(lines) + "\n")


def _after_retired(lines: list[str], index: int) -> bool:
    return any(RETIRED_HEADING_RE.match(line) for line in lines[:index])


def nearest_topics(topic_map: TopicMap, wanted: str, count: int = 5) -> str:
    """Show the closest topics on a miss, instead of the whole map."""
    scored = sorted(
        topic_map.live.items(),
        key=lambda row: -max(
            SequenceMatcher(None, wanted, row[0]).ratio(),
            SequenceMatcher(None, wanted, row[1].lower()).ratio(),
        ),
    )
    return "Closest topics in the map:\n" + "\n".join(
        f"  {name} — {description}" for name, description in scored[:count]
    )


def anchor(value: str, field: str) -> str:
    """A corpus address, in either form the agent has at hand.

    Search prints `file.md:21`, a capture receipt prints `file.md#L21`, and the
    same address arrives here from both. Accept both and store one.
    """
    collapsed = one_line(value, field)
    match = ANCHOR_RE.fullmatch(collapsed)
    if not match:
        raise CaptureError(
            f"{field} must address one record as <file>.md:<line> "
            f"(the form search prints): {collapsed!r}"
        )
    return f"{match['file']}:{match['line']}"


def verify_anchor(log_dir: Path, value: str, field: str) -> str:
    """Bind the address to the record's fingerprint, so it survives line drift.

    A conversation file grows while it is open, and every earlier line moves
    down with it. A bare line number would quietly stop pointing at the record
    it was written for; the fingerprint lets the reader find it again.
    """
    name, _, line_number = value.rpartition(":")
    path = log_dir / name
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as error:
        raise CaptureError(f"{field} points outside the corpus: {value}") from error
    index = int(line_number) - 1
    if not 0 <= index < len(lines) or not lines[index].startswith("* "):
        raise CaptureError(
            f"{field} does not address a record line: {value}. Addresses move "
            f"down as a conversation grows; records in {name} are now:\n"
            + current_records(name, lines)
        )
    return f"{value} sha:{fingerprint(lines[index])}"


def current_records(name: str, lines: list[str], width: int = 70) -> str:
    """The file's live addresses, so the retry needs no second read."""
    return "\n".join(
        f"  {name}:{number} {line[:width]}…"
        for number, line in enumerate(lines, start=1)
        if line.startswith("* ")
    )


def fingerprint(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:8]


KINDS = ("quote", "selection", "note")
PRECISIONS = ("exact", "minute", "date", "unknown")
ENV_BY_AGENT = {
    "claude": ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"),
    "codex": ("CODEX_THREAD_ID", "CODEX_SESSION_ID"),
}
HANDLE_RE = re.compile(r"^[\w.\-/]+$")
ENTRY_START_RE = re.compile(r"^\*\s+(?P<timestamp>.+?)\s+—\s+")
CONTEXT_LINK_RE = re.compile(
    r"(?:https?://|file://|www\.|\[[^\]]+\]\([^)]+\))", re.IGNORECASE
)
CONTEXT_NOTE_GUIDANCE = (
    "context-note is a short set of searchable noun phrases, not prose; name "
    "stable referents and useful synonyms; never repeat or paraphrase the quote "
    "or widen a situational reply into a standing preference; if no grounded "
    "keyword exists, inspect the source context instead of inventing one"
)
CONTEXT_NOTE_REMINDER = f"remember: {CONTEXT_NOTE_GUIDANCE}"
POSITION_TYPES = frozenset(
    {"решение", "коррекция", "критерий", "правило-кандидат", "предпочтение"}
)
SUPERSESSION_GUIDANCE = (
    "a position must say what it overturns, and only you can say it: you heard "
    "the reply, and no search will find the overturned position for you — a "
    "cancellation is worded as the opposite of what it cancels and shares "
    "almost none of its words. Overturns an earlier position: pass its address, "
    "--supersedes <file>.md:<line>. Overturns none: --supersedes-none. Conflicts "
    "without a clear winner: --contested <file>.md:<line>. A wrong link hides a "
    "position that is still live, so a considered --supersedes-none is a real "
    "answer, not a way past this"
)
SESSION_CONTEXT_GUIDANCE = (
    "one-line search card for the whole session; pass the complete current card, "
    "not a delta; keep earlier major subjects when work changes; use brief "
    "task/artifact/operation/synonym fragments; do not quote or paraphrase owner "
    "speech or state decisions, conclusions, or current truth"
)


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
    if "|" in collapsed:
        raise CaptureError("context note cannot contain the metadata delimiter '|'")
    if CONTEXT_LINK_RE.search(collapsed):
        raise CaptureError("context note must be inline context, not a link")
    return collapsed


def session_context(value: str) -> str:
    return one_line(value, "session context")


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


def render_metadata_vocabulary(log_dir: Path, topic_map: TopicMap | None) -> str:
    lines = ["Types:"]
    lines.extend(f"  {name}: {meaning}" for name, meaning in TYPE_DESCRIPTIONS.items())
    lines.append(f"  {REPAIR_TYPE}: repair-only sentinel")
    lines.append("")
    counts = corpus_topics(log_dir)
    if topic_map is not None:
        lines.append(
            f"Topics (map: {topic_map.path}; conversations using each). "
            "Choose by the meaning of the subject, not by matching words:"
        )
        lines.extend(
            f"  {name} [{counts.get(name, 0)}] — {description}"
            for name, description in sorted(topic_map.live.items())
        )
        if topic_map.retired:
            lines.append(
                "Retired (do not reuse): " + ", ".join(sorted(topic_map.retired))
            )
        lines.append(f"  {REPAIR_TOPIC}: repair-only sentinel")
        lines.append(
            'No topic fits the subject? Create one: --new-topic "<one-line '
            'boundary>" adds its row to the map together with the record.'
        )
    elif counts:
        lines.append("Topics (existing in this corpus; conversations using each):")
        lines.extend(
            f"  {name}: {count}"
            for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        )
        lines.append(f"  {REPAIR_TOPIC}: repair-only sentinel")
        lines.append(
            "Reuse an existing topic when the subject is the same; name a new one "
            "only when the corpus has no topic for it yet."
        )
    else:
        lines.append(f"Topics: none recorded yet in {log_dir}")
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
        argv = sys.argv[1:]
        project = default_project()
        for index, arg in enumerate(argv):
            if arg == "--project" and index + 1 < len(argv):
                project = argv[index + 1]
            elif arg.startswith("--project="):
                project = arg.split("=", 1)[1]
        root = Path(project).resolve()
        print(render_metadata_vocabulary(resolve_log_dir(root), read_topic_map(root)))
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
    kind: str,
    context: str | None = None,
    supersedes: str | None = None,
    contested: str | None = None,
) -> str:
    fields = []
    if kind != "quote":
        fields.append(f"kind: {kind}")
    fields.extend((f"type: {type_}", f"topic: {topic}"))
    if supersedes:
        fields.append(f"supersedes: {supersedes}")
    if contested:
        fields.append(f"contested: {contested}")
    if context:
        fields.append(f"context-note: {context}")
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


def set_frontmatter_scalar(lines: list[str], key: str, value: str) -> bool:
    """Create or replace one JSON-quoted YAML scalar; report whether it changed."""
    end = frontmatter_end(lines)
    rendered = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    prefix = f"{key}:"
    for index in range(1, end):
        if lines[index].startswith(prefix):
            if lines[index] == rendered:
                return False
            lines[index] = rendered
            return True
    for index in range(1, end):
        if lines[index].startswith("session: "):
            lines.insert(index + 1, rendered)
            return True
    lines.insert(end, rendered)
    return True


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
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            os.fchmod(
                stream.fileno(),
                stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644,
            )
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def snapshot_files(paths: set[Path]) -> dict[Path, FileState]:
    return {
        path: FileState(
            path.read_text(encoding="utf-8-sig"),
            stat.S_IMODE(path.stat().st_mode),
        )
        if path.exists()
        else FileState(None, None)
        for path in paths
    }


def restore_files(states: dict[Path, FileState]) -> None:
    for path, before in states.items():
        if before.text is None:
            path.unlink(missing_ok=True)
            continue
        write_atomic(path, before.text)
        if before.mode is not None:
            path.chmod(before.mode)


def record_receipt(
    path: Path,
    quote: str,
    topic: str,
    session: str,
    status: str,
) -> dict[str, object]:
    """Return a stable record identity plus its current human-readable anchor."""
    marker = f'— "{quote}" —'
    matches = [
        (number, line)
        for number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), start=1
        )
        if marker in line
    ]
    if len(matches) != 1:
        raise CaptureError(
            f"cannot address captured record uniquely in {path}: {len(matches)} matches"
        )
    line_number, line = matches[0]
    return {
        "status": status,
        "path": str(path),
        "topic": topic,
        "session": session,
        "anchor": f"{path.name}#L{line_number}",
        "record_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
    }


def _earliest_known(text: str, incoming: SourceTimestamp) -> datetime:
    known = [
        item.ordering
        for item in _entry_times(text, _frontmatter_date(text))
        if item.ordering is not None
    ]
    if incoming.ordering is not None:
        known.append(incoming.ordering)
    return min(known) if known else incoming.file_when


def append_target(
    path: Path,
    agent: str,
    session: str,
    source: SourceTimestamp,
    text: str,
) -> Path:
    if source.precision not in ("exact", "minute"):
        return path
    earliest = _earliest_known(text, source)
    return dated_path(
        path.parent,
        agent,
        session,
        SourceTimestamp(earliest.isoformat(), "exact", earliest, earliest),
        current=path,
    )


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
    kind: str,
    context: str | None = None,
    session_card: str | None = None,
    supersedes: str | None = None,
    contested: str | None = None,
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
    ]
    if session_card:
        lines.append(
            f"session-context: {json.dumps(session_card, ensure_ascii=False)}"
        )
    lines += [
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
            kind,
            context,
            supersedes,
            contested,
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
    kind: str = "quote",
    context: str | None = None,
    session_card: str | None = None,
    supersedes: str | None = None,
    contested: str | None = None,
) -> tuple[bool, bool, Path]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    context_updated = bool(
        session_card is not None
        and set_frontmatter_scalar(lines, "session-context", session_card)
    )
    if f'"{quote}"' in text:
        if context_updated:
            write_atomic(path, "\n".join(lines) + "\n")
        return False, context_updated, path
    ensure_inventory(lines, "types", type_)
    ensure_inventory(lines, "topics", topic)
    target = append_target(path, agent, session, source, text)
    if target != path:
        earliest = _earliest_known(text, source)
        _set_file_date(lines, earliest)
    rendered = "\n".join(lines) + "\n" + _entry_line(
        quote,
        type_,
        topic,
        source,
        kind,
        context,
        supersedes,
        contested,
    )
    write_atomic(target, rendered)
    if target != path:
        path.unlink()
    return True, context_updated, target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list-metadata",
        action=PrintMetadataAction,
        help=(
            "print canonical types and the topic map with one-line boundaries, "
            "with the number of conversations behind each"
        ),
    )
    parser.add_argument(
        "--quote",
        required=True,
        help=(
            "caller-confirmed owner excerpt; shorten only by deletion while "
            "preserving wording and order; exclude pasted documents, quoted "
            "conversations, and other people's or agents' words"
        ),
    )
    parser.add_argument("--type", required=True, dest="type_")
    parser.add_argument("--topic", required=True)
    parser.add_argument(
        "--new-topic",
        metavar="BOUNDARY",
        help=(
            "the subject fits no topic in the map: add its row — a one-line "
            "boundary — together with this record"
        ),
    )
    parser.add_argument("--kind", choices=KINDS, default="quote")
    parser.add_argument(
        "--supersedes",
        metavar="ANCHOR",
        help=(
            "address <file>.md#L<line> of the earlier record this reply cancels; "
            "only when both cannot be true at once in the same scope"
        ),
    )
    parser.add_argument(
        "--contested",
        metavar="ANCHOR",
        help=(
            "address <file>.md#L<line> this reply conflicts with when the winner "
            "is unclear; marks the conflict instead of choosing silently"
        ),
    )
    parser.add_argument(
        "--source-timestamp",
        help=(
            "when the owner said it; omit only when writing in the same turn — "
            "the write time is then the right mark. For backfill pass it explicitly"
        ),
    )
    parser.add_argument(
        "--context-note",
        help=(
            "required for --kind quote and --kind selection; "
            f"{CONTEXT_NOTE_GUIDANCE}; links rejected"
        ),
    )
    parser.add_argument(
        "--session-context",
        help=(
            "required for --kind quote and --kind selection; "
            + SESSION_CONTEXT_GUIDANCE
        ),
    )
    parser.add_argument(
        "--supersedes-none",
        action="store_true",
        help=(
            "this reply overturns no earlier position — the answer required of "
            "every position when it cancels nothing"
        ),
    )
    parser.add_argument("--project", default=default_project())
    parser.add_argument("--agent", required=True)
    parser.add_argument("--model")
    parser.add_argument("--session")
    parser.add_argument(
        "--json",
        action="store_true",
        help="print one machine-readable capture receipt",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        quote = one_line(args.quote, "quote")
        type_ = metadata_choice(args.type_, "type", TYPES)
        topic = handle(args.topic, "topic")
        validate_metadata(type_, topic, args.kind)
        agent = handle(args.agent, "agent")
        model = handle(args.model, "model") if args.model else None
        context = (
            context_note(args.context_note)
            if args.context_note is not None
            else None
        )
        session_card = (
            session_context(args.session_context)
            if args.session_context is not None
            else None
        )
        if args.kind in ("quote", "selection") and context is None:
            raise CaptureError(
                "--context-note is required for --kind quote and --kind selection; "
                + CONTEXT_NOTE_GUIDANCE
            )
        if args.supersedes_none and (args.supersedes or args.contested):
            raise CaptureError(
                "--supersedes-none contradicts --supersedes and --contested; "
                "pass exactly one answer"
            )
        if (
            args.kind in ("quote", "selection")
            and type_ in POSITION_TYPES
            and topic != REPAIR_TOPIC
            and not args.supersedes
            and not args.contested
            and not args.supersedes_none
        ):
            raise CaptureError(
                "--supersedes, --contested or --supersedes-none is required for "
                "a position; " + SUPERSESSION_GUIDANCE
            )
        if args.kind in ("quote", "selection") and session_card is None:
            raise CaptureError(
                "--session-context is required for --kind quote and "
                "--kind selection; "
                + SESSION_CONTEXT_GUIDANCE
            )
        if context and args.kind == "note":
            raise CaptureError("--context-note cannot be attached to --kind note")
        implicit_now = args.source_timestamp is None
        source = source_timestamp(
            args.source_timestamp
            if not implicit_now
            else datetime.now().astimezone().replace(microsecond=0).isoformat()
        )
        if source.precision == "unknown" and args.kind != "note":
            raise CaptureError(
                "unknown timestamp is repair-only; capture must pass at least a "
                "YYYY-MM-DD date, preferably ISO with timezone"
            )
        root = Path(args.project).resolve()
        if not root.is_dir():
            raise CaptureError(f"project root not found: {root}")
        log_dir = resolve_log_dir(root)
        topic_map = read_topic_map(root)
        if topic_map is None and topic != REPAIR_TOPIC:
            raise CaptureError(
                f"topic map not found: {root / TOPIC_MAP}. Read or repair the "
                "target project's complete topic map before capture"
            )
        new_topic_row = None
        if topic_map is not None and topic != REPAIR_TOPIC:
            if topic in topic_map.retired:
                raise CaptureError(
                    f"topic {topic!r} is retired in {topic_map.path}: "
                    f"{topic_map.retired[topic]}"
                )
            if topic not in topic_map.live:
                if not args.new_topic:
                    raise CaptureError(
                        f"topic {topic!r} is not in {topic_map.path}.\n"
                        + nearest_topics(topic_map, topic)
                        + "\nPick the one whose subject this reply belongs to, or "
                        'create a topic deliberately: --new-topic "<boundary>".'
                    )
                new_topic_row = one_line(args.new_topic, "new topic boundary")
        supersedes = (
            verify_anchor(log_dir, anchor(args.supersedes, "supersedes"), "supersedes")
            if args.supersedes
            else None
        )
        contested = (
            verify_anchor(log_dir, anchor(args.contested, "contested"), "contested")
            if args.contested
            else None
        )
        session = resolve_session(args.session, agent)
        if not session:
            checked = ", ".join(ENV_BY_AGENT.get(agent, ())) or "none"
            raise CaptureError(
                f"session id unknown for agent '{agent}' (env checked: {checked})"
            )
        path = find_session_file(log_dir, agent, session, source)
        already_present = path.exists() and f'"{quote}"' in path.read_text(
            encoding="utf-8-sig"
        )
        topic_transaction = bool(
            not already_present and new_topic_row is not None and topic_map is not None
        )
        planned_path = (
            append_target(
                path,
                agent,
                session,
                source,
                path.read_text(encoding="utf-8-sig"),
            )
            if path.exists()
            else path
        )
        transaction_paths = {path, planned_path}
        if topic_transaction and topic_map is not None:
            transaction_paths.add(topic_map.path)
        before = snapshot_files(transaction_paths)
        try:
            if topic_transaction and topic_map is not None and new_topic_row is not None:
                # Validate and commit the dictionary row first. A later holder failure
                # rolls it back, so a failed operation never leaves only one side.
                add_topic_row(topic_map, topic, new_topic_row)
            if path.exists():
                written, context_updated, path = append_entry(
                    path,
                    agent,
                    session,
                    type_,
                    topic,
                    quote,
                    source,
                    args.kind,
                    context,
                    session_card,
                    supersedes,
                    contested,
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
                    args.kind,
                    context,
                    session_card,
                    supersedes,
                    contested,
                )
                written = True
                context_updated = session_card is not None
            if topic_transaction and not written and topic_map is not None:
                restore_files({topic_map.path: before[topic_map.path]})
            receipt = record_receipt(
                path,
                quote,
                topic,
                session,
                "written"
                if written
                else "context-updated"
                if context_updated
                else "already-present",
            )
        except (CaptureError, OSError) as error:
            try:
                restore_files(before)
            except OSError as rollback_error:
                raise CaptureError(
                    f"capture failed and transaction rollback failed: {rollback_error}"
                ) from error
            raise
        if args.json:
            print(json.dumps(receipt, ensure_ascii=False))
        else:
            if written:
                print(f"appended to {path}")
            elif context_updated:
                print(f"quote already present; session-context updated in {path}")
            else:
                print(f"already present in {path}")
            if written and implicit_now:
                print(
                    "note: source-timestamp not given — used the write time "
                    f"({source.rendered}). Correct for a same-turn capture; "
                    "for backfill pass --source-timestamp explicitly"
                )
            if written and args.kind == "quote":
                print(CONTEXT_NOTE_REMINDER)
        return 0
    except (CaptureError, OSError) as error:
        print(f"chat-capture: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
