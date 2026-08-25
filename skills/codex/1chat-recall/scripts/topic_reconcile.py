#!/usr/bin/env python3
"""Safely apply one agent-authored update to a loaded chat-recall topic."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

LOG_DIR = Path("_ops/chat-recall")
NOOP_LEDGER = LOG_DIR / "topics" / "reconcile-noops.json"
TOPIC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
CAPTURE_ANCHOR_RE = re.compile(
    r"(?P<holder>\d{4}-\d{2}-\d{2}-\d{6}-(?:claude|codex)-"
    r"[A-Za-z0-9_-]+\.md)#L(?P<line>\d+)"
)
TOPIC_ANCHOR_RE = re.compile(
    r"(?P<holder>\d{4}-\d{2}-\d{2}-\d{6}-[^\s#\],)]+\.md)#L\d+"
)


class ReconcileError(RuntimeError):
    """Expected validation, conflict, or corpus failure."""


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scalar(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", text, re.MULTILINE)
    if match is None:
        raise ReconcileError(f"missing frontmatter scalar: {key}")
    return match.group(1)


def frontmatter(text: str, label: str) -> tuple[str, int]:
    if not text.startswith("---\n"):
        raise ReconcileError(f"{label} has no canonical frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ReconcileError(f"{label} has no closing frontmatter delimiter")
    return text[4:end], end


def topic_path(project: Path, topic: str) -> Path:
    if not TOPIC_RE.fullmatch(topic):
        raise ReconcileError("topic must be a lowercase latin-hyphen id")
    root = project.resolve()
    if not root.is_dir():
        raise ReconcileError(f"project root not found: {root}")
    path = root / LOG_DIR / "topics" / f"{topic}.md"
    if not path.is_file():
        raise ReconcileError(f"topic file not found: {path}")
    return path


def validate_topic_text(text: str, topic: str, label: str) -> str:
    if not text.strip():
        raise ReconcileError(f"{label} is empty")
    if "\x00" in text:
        raise ReconcileError(f"{label} contains a NUL byte")
    header, _ = frontmatter(text, label)
    if scalar(header, "topic") != topic:
        raise ReconcileError(f"{label} does not own topic: {topic}")
    return text if text.endswith("\n") else text + "\n"


def raw_dir(project: Path) -> Path:
    nested = project / LOG_DIR / "raw"
    return nested if nested.is_dir() else project / LOG_DIR


def locate_record(
    project: Path,
    session: str,
    record_sha256: str,
    topic: str,
) -> str:
    if not HASH_RE.fullmatch(record_sha256):
        raise ReconcileError("record-sha256 must be a full lowercase SHA-256")
    matches: list[tuple[Path, int, str]] = []
    for holder in sorted(raw_dir(project).glob("*.md")):
        text = holder.read_text(encoding="utf-8-sig")
        if (
            re.search(
                rf"^session:\s*{re.escape(session)}\s*$",
                text,
                re.MULTILINE,
            )
            is None
        ):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if digest(line) == record_sha256:
                matches.append((holder, line_number, line))
    if len(matches) != 1:
        raise ReconcileError(
            "captured record is not uniquely resolvable by session and hash: "
            f"{len(matches)} matches"
        )
    holder, line_number, line = matches[0]
    topic_match = re.search(r"\| topic: ([^|\s]+)(?:\s*\||\s*$)", line)
    if topic_match is None or topic_match.group(1) != topic:
        raise ReconcileError(
            f"captured record does not belong to topic {topic}: {holder.name}#L{line_number}"
        )
    return f"{holder.name}#L{line_number}"


def normalize_source_count(text: str) -> str:
    holders = {match.group("holder") for match in TOPIC_ANCHOR_RE.finditer(text)}
    replacement = f"sources: {len(holders)}"
    header, end = frontmatter(text, "topic")
    rendered_header, count = re.subn(
        r"^sources:\s*\d+\s*$",
        replacement,
        header,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ReconcileError("topic must contain exactly one numeric sources scalar")
    return "---\n" + rendered_header + text[end:]


def anchor_pattern(anchor: str) -> re.Pattern[str]:
    """Match an anchor as a token, not as the prefix of a larger line number."""
    return re.compile(re.escape(anchor) + r"(?!\d)")


def claim_line(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("- "):
        raise ReconcileError(f"{field} must be one Markdown claim line")
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ReconcileError(f"{field} must be one Markdown claim line")
    if not value[2:].strip():
        raise ReconcileError(f"{field} has no claim text")
    return value


def boundary_line(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReconcileError(f"{field} must be one topic-boundary paragraph")
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ReconcileError(f"{field} must be one topic-boundary paragraph")
    if value.startswith(("#", "- ", "* ")):
        raise ReconcileError(f"{field} must be prose, not Markdown structure")
    return value


def operation_schema() -> dict[str, dict[str, str]]:
    anchor = "[<receipt.anchor>]"
    return {
        "insert": {
            "kind": "insert",
            "section": "## Exact existing heading",
            "claim": f"- New claim. {anchor}",
        },
        "replace": {
            "kind": "replace",
            "before": "- Exact existing claim.",
            "after": f"- Revised claim. {anchor}",
        },
        "move": {
            "kind": "move",
            "before": "- Exact existing claim.",
            "section": "## Exact target heading",
            "after": f"- Moved or cancelled claim. {anchor}",
        },
        "replace-boundary": {
            "kind": "replace-boundary",
            "before": "Exact current intro paragraph.",
            "after": f"Revised intro paragraph. {anchor}",
        },
    }


def patch_operations(path: Path, topic: str) -> list[dict[str, str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ReconcileError(f"patch is not valid JSON: {error.msg}") from error
    required = {"version", "topic", "operations"}
    if not isinstance(payload, dict) or set(payload) not in (
        required,
        required | {"operation_schema"},
    ):
        raise ReconcileError(
            "patch must contain version, topic, operations, and optional operation_schema"
        )
    if payload["version"] != 1 or payload["topic"] != topic:
        raise ReconcileError("patch version or topic does not match the request")
    if (
        "operation_schema" in payload
        and payload["operation_schema"] != operation_schema()
    ):
        raise ReconcileError("operation_schema is generated by prepare; do not edit it")
    raw_operations = payload["operations"]
    if not isinstance(raw_operations, list) or not raw_operations:
        raise ReconcileError("patch must contain at least one operation")
    operations: list[dict[str, str]] = []
    for index, raw in enumerate(raw_operations, start=1):
        if not isinstance(raw, dict):
            raise ReconcileError(f"operation {index} must be an object")
        kind = raw.get("kind")
        if kind == "insert":
            if set(raw) != {"kind", "section", "claim"}:
                raise ReconcileError(
                    f"insert operation {index} needs only kind, section, and claim"
                )
            section = raw["section"]
            if (
                not isinstance(section, str)
                or not section.startswith("## ")
                or "\n" in section
                or "\r" in section
            ):
                raise ReconcileError(
                    f"insert operation {index} needs one exact ## section heading"
                )
            operations.append(
                {
                    "kind": "insert",
                    "section": section,
                    "claim": claim_line(raw["claim"], f"operation {index} claim"),
                }
            )
        elif kind == "replace":
            if set(raw) != {"kind", "before", "after"}:
                raise ReconcileError(
                    f"replace operation {index} needs only kind, before, and after"
                )
            operations.append(
                {
                    "kind": "replace",
                    "before": claim_line(raw["before"], f"operation {index} before"),
                    "after": claim_line(raw["after"], f"operation {index} after"),
                }
            )
        elif kind == "replace-boundary":
            if set(raw) != {"kind", "before", "after"}:
                raise ReconcileError(
                    f"replace-boundary operation {index} needs only kind, before, and after"
                )
            operations.append(
                {
                    "kind": "replace-boundary",
                    "before": boundary_line(raw["before"], f"operation {index} before"),
                    "after": boundary_line(raw["after"], f"operation {index} after"),
                }
            )
        elif kind == "move":
            if set(raw) != {"kind", "before", "section", "after"}:
                raise ReconcileError(
                    f"move operation {index} needs only kind, before, section, and after"
                )
            section = raw["section"]
            if (
                not isinstance(section, str)
                or not section.startswith("## ")
                or "\n" in section
                or "\r" in section
            ):
                raise ReconcileError(
                    f"move operation {index} needs one exact ## section heading"
                )
            operations.append(
                {
                    "kind": "move",
                    "before": claim_line(raw["before"], f"operation {index} before"),
                    "section": section,
                    "after": claim_line(raw["after"], f"operation {index} after"),
                }
            )
        else:
            raise ReconcileError(f"operation {index} has unknown kind: {kind!r}")
    return operations


def canonical_claim_anchor(
    claim: str,
    source_anchor: str,
    live_anchor: str,
    operation: int,
) -> str:
    source_pattern = anchor_pattern(source_anchor)
    live_pattern = anchor_pattern(live_anchor)
    source_count = len(source_pattern.findall(claim))
    live_count = len(live_pattern.findall(claim))
    if source_anchor == live_anchor:
        if source_count != 1:
            raise ReconcileError(
                f"operation {operation} must cite the captured record exactly once"
            )
        return claim
    if source_count == 1 and live_count == 0:
        return source_pattern.sub(live_anchor, claim, count=1)
    if source_count == 0 and live_count == 1:
        return claim
    raise ReconcileError(
        f"operation {operation} must cite exactly one capture-time or current anchor"
    )


def insert_section_claim(
    lines: list[str], section: str, claim: str, operation: int
) -> None:
    sections = [row for row, line in enumerate(lines) if line == section]
    if len(sections) != 1:
        raise ReconcileError(
            f"operation {operation} section occurs {len(sections)} times"
        )
    if claim in lines:
        raise ReconcileError(f"operation {operation} would duplicate an existing claim")
    start = sections[0] + 1
    end = next(
        (row for row in range(start, len(lines)) if lines[row].startswith("## ")),
        len(lines),
    )
    content = lines[start:end]
    while content and not content[0].strip():
        content.pop(0)
    while content and not content[-1].strip():
        content.pop()
    replacement = ["", *content, claim]
    if end < len(lines):
        replacement.append("")
    lines[start:end] = replacement


def remove_claim(lines: list[str], row: int) -> None:
    del lines[row]
    if 0 < row < len(lines) and not lines[row - 1].strip() and not lines[row].strip():
        del lines[row]


def apply_operations(
    current: str,
    operations: list[dict[str, str]],
    source_anchor: str,
    live_anchor: str,
) -> str:
    lines = current.rstrip("\n").splitlines()
    for index, operation in enumerate(operations, start=1):
        field = "claim" if operation["kind"] == "insert" else "after"
        replacement = canonical_claim_anchor(
            operation[field], source_anchor, live_anchor, index
        )
        if operation["kind"] == "move":
            before = operation["before"]
            matches = [row for row, line in enumerate(lines) if line == before]
            if len(matches) != 1:
                raise ReconcileError(
                    f"operation {index} move target occurs {len(matches)} times"
                )
            remove_claim(lines, matches[0])
            insert_section_claim(lines, operation["section"], replacement, index)
            continue
        if operation["kind"] in {"replace", "replace-boundary"}:
            before = operation["before"]
            matches = [row for row, line in enumerate(lines) if line == before]
            if len(matches) != 1:
                raise ReconcileError(
                    f"operation {index} replacement target occurs {len(matches)} times"
                )
            if operation["kind"] == "replace-boundary":
                headings = [
                    row for row, line in enumerate(lines) if line.startswith("# ")
                ]
                if len(headings) != 1:
                    raise ReconcileError("topic must contain exactly one H1 heading")
                intro = next(
                    (
                        row
                        for row in range(headings[0] + 1, len(lines))
                        if lines[row].strip()
                    ),
                    None,
                )
                if intro != matches[0] or lines[intro].startswith("## "):
                    raise ReconcileError(
                        f"operation {index} target is not the topic-boundary paragraph"
                    )
            lines[matches[0]] = replacement
            continue
        insert_section_claim(lines, operation["section"], replacement, index)
    return "\n".join(lines).rstrip("\n") + "\n"


def write_atomic(path: Path, text: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, path.stat().st_mode if path.exists() else 0o644)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


@contextlib.contextmanager
def topic_lock(project: Path, topic: str) -> Iterator[None]:
    lock_path = topic_lock_path(project, topic)
    with lock_path.open("a", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def topic_lock_path(project: Path, topic: str) -> Path:
    lock_root = Path(tempfile.gettempdir()) / f"chat-recall-topic-locks-{os.getuid()}"
    lock_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    key = digest(f"{project.resolve()}\0{topic}")
    return lock_root / f"{key}.lock"


def load_noop_ledger(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"version": 1, "records": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ReconcileError(f"no-op ledger is not valid JSON: {error.msg}") from error
    if (
        not isinstance(payload, dict)
        or set(payload) != {"version", "records"}
        or payload["version"] != 1
        or not isinstance(payload["records"], list)
        or any(not isinstance(record, dict) for record in payload["records"])
    ):
        raise ReconcileError("no-op ledger has an invalid schema")
    return payload


def acknowledge_noop(
    project: Path,
    topic: str,
    session: str,
    record_sha256: str,
    source_anchor: str,
) -> dict[str, str]:
    topic_path(project, topic)
    if CAPTURE_ANCHOR_RE.fullmatch(source_anchor) is None:
        raise ReconcileError("source-anchor is not a canonical raw holder anchor")
    root = project.resolve()
    ledger_path = root / NOOP_LEDGER
    with topic_lock(root, "reconcile-noops"):
        live_anchor = locate_record(root, session, record_sha256, topic)
        ledger = load_noop_ledger(ledger_path)
        records = ledger["records"]
        assert isinstance(records, list)
        for record in records:
            if (
                record.get("session") == session
                and record.get("record_sha256") == record_sha256
            ):
                return {
                    "status": "noop-already-acknowledged",
                    "ledger": str(ledger_path),
                    "anchor": live_anchor,
                }
        records.append(
            {
                "topic": topic,
                "session": session,
                "record_sha256": record_sha256,
                "anchor": live_anchor,
            }
        )
        write_atomic(
            ledger_path,
            json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
        )
        return {
            "status": "noop-acknowledged",
            "ledger": str(ledger_path),
            "anchor": live_anchor,
        }


def prepare(project: Path, topic: str, patch: Path) -> dict[str, str]:
    target = topic_path(project, topic)
    if patch.resolve() == target.resolve():
        raise ReconcileError("patch must not be the shared topic file")
    current = validate_topic_text(
        target.read_text(encoding="utf-8-sig"), topic, "current topic"
    )
    if patch.exists() and patch.stat().st_size:
        raise ReconcileError(f"patch already contains data: {patch}")
    patch.parent.mkdir(parents=True, exist_ok=True)
    patch.write_text(
        json.dumps(
            {"version": 1, "topic": topic, "operations": []}
            | {"operation_schema": operation_schema()},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "status": "prepared",
        "topic_file": str(target),
        "patch": str(patch.resolve()),
        "expected_sha256": digest(current),
    }


def apply(
    project: Path,
    topic: str,
    patch: Path,
    expected_sha256: str,
    session: str,
    record_sha256: str,
    source_anchor: str,
) -> dict[str, str]:
    if not HASH_RE.fullmatch(expected_sha256):
        raise ReconcileError("expected-sha256 must be a full lowercase SHA-256")
    if CAPTURE_ANCHOR_RE.fullmatch(source_anchor) is None:
        raise ReconcileError("source-anchor is not a canonical raw holder anchor")
    target = topic_path(project, topic)
    if patch.resolve() == target.resolve():
        raise ReconcileError("patch must not be the shared topic file")
    operations = patch_operations(patch, topic)
    with topic_lock(project, topic):
        current = validate_topic_text(
            target.read_text(encoding="utf-8-sig"), topic, "current topic"
        )
        current_sha256 = digest(current)
        if current_sha256 != expected_sha256:
            raise ReconcileError(
                "topic changed after prepare; no write performed "
                f"(expected {expected_sha256}, found {current_sha256})"
            )
        live_anchor = locate_record(project.resolve(), session, record_sha256, topic)
        rendered = normalize_source_count(
            apply_operations(current, operations, source_anchor, live_anchor)
        )
        if rendered == current:
            return {
                "status": "unchanged",
                "topic_file": str(target),
                "anchor": live_anchor,
                "sha256": current_sha256,
            }
        write_atomic(target, rendered)
        return {
            "status": "applied",
            "topic_file": str(target),
            "anchor": live_anchor,
            "previous_sha256": current_sha256,
            "sha256": digest(rendered),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--project", default=".")
    prepare_parser.add_argument("--topic", required=True)
    prepare_parser.add_argument("--patch", required=True, type=Path)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--project", default=".")
    apply_parser.add_argument("--topic", required=True)
    apply_parser.add_argument("--patch", required=True, type=Path)
    apply_parser.add_argument("--expected-sha256", required=True)
    apply_parser.add_argument("--session", required=True)
    apply_parser.add_argument("--record-sha256", required=True)
    apply_parser.add_argument("--source-anchor", required=True)

    noop_parser = subparsers.add_parser("acknowledge-noop")
    noop_parser.add_argument("--project", default=".")
    noop_parser.add_argument("--topic", required=True)
    noop_parser.add_argument("--session", required=True)
    noop_parser.add_argument("--record-sha256", required=True)
    noop_parser.add_argument("--source-anchor", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "prepare":
            result = prepare(Path(args.project), args.topic, args.patch)
        elif args.command == "apply":
            result = apply(
                Path(args.project),
                args.topic,
                args.patch,
                args.expected_sha256,
                args.session,
                args.record_sha256,
                args.source_anchor,
            )
        else:
            result = acknowledge_noop(
                Path(args.project),
                args.topic,
                args.session,
                args.record_sha256,
                args.source_anchor,
            )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ReconcileError) as error:
        print(f"topic-reconcile: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
