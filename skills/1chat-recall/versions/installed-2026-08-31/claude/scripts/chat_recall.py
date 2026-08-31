#!/usr/bin/env python3
"""Print prior user input from the current Claude Code session."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_LIMIT = 10


class RecallError(RuntimeError):
    pass


@dataclass(frozen=True)
class Item:
    label: str
    body: str | None
    source_timestamp: str
    note: str | None = None


def record_timestamp(record: dict[str, Any]) -> str:
    raw = record.get("timestamp")
    if not isinstance(raw, str) or not raw:
        raise RecallError("user evidence has no source timestamp")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise RecallError("user evidence has an invalid source timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RecallError("user evidence source timestamp has no timezone")
    return parsed.isoformat()


def canonical_session_id(raw: str) -> str:
    try:
        canonical = str(uuid.UUID(raw))
    except ValueError as exc:
        raise RecallError(f"invalid session id: {raw!r}") from exc
    if raw != canonical:
        raise RecallError(f"session id must be canonical: {canonical}")
    return canonical


def resolve_transcript(session_id: str) -> Path:
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    matches = sorted(
        path
        for path in (root / "projects").glob(f"*/{session_id}.jsonl")
        if path.is_file()
    )
    if len(matches) != 1:
        raise RecallError(
            f"expected one transcript for {session_id}, found {len(matches)}"
        )
    return matches[0]


def load_records(path: Path, session_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RecallError(f"invalid JSON at line {line_number}") from exc
        if not isinstance(record, dict) or record.get("sessionId") != session_id:
            raise RecallError(f"session mismatch at line {line_number}")
        records.append(record)
    if not records:
        raise RecallError("empty transcript")
    return records


def content(record: dict[str, Any]) -> Any:
    message = record.get("message")
    return message.get("content") if isinstance(message, dict) else None


def is_direct_user(record: dict[str, Any]) -> bool:
    message = record.get("message")
    if record.get("type") != "user" or not isinstance(message, dict):
        return False
    if message.get("role") != "user":
        return False
    if record.get("isMeta") is True:
        return False
    if record.get("isMeta") not in (None, False):
        raise RecallError("unknown isMeta schema")
    if record.get("sourceToolAssistantUUID") is not None:
        return False
    if record.get("sourceToolUseID") is not None:
        return False

    origin = record.get("origin")
    if origin is not None:
        if not isinstance(origin, dict) or origin.get("kind") not in (
            "human",
            "task-notification",
        ):
            raise RecallError("unknown user origin schema")
        if origin["kind"] == "task-notification":
            return False

    value = message.get("content")
    if isinstance(value, list) and any(
        isinstance(block, dict) and block.get("type") == "tool_result"
        for block in value
    ):
        return False
    if not isinstance(value, (str, list)):
        raise RecallError("unknown direct user content schema")
    return True


def active_chain(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    direct = [record for record in records if is_direct_user(record)]
    if not direct or not isinstance(direct[-1].get("uuid"), str):
        raise RecallError("current user turn not found")
    anchor = direct[-1]["uuid"]

    by_uuid: dict[str, dict[str, Any]] = {}
    for record in records:
        record_uuid = record.get("uuid")
        if record_uuid is None:
            continue
        if not isinstance(record_uuid, str) or record_uuid in by_uuid:
            raise RecallError("invalid or duplicate record uuid")
        parent = record.get("parentUuid")
        if parent is not None and not isinstance(parent, str):
            raise RecallError("invalid parent uuid")
        by_uuid[record_uuid] = record

    chain: list[dict[str, Any]] = []
    seen: set[str] = set()
    cursor: str | None = anchor
    while cursor is not None:
        if cursor in seen or cursor not in by_uuid:
            raise RecallError("broken active ancestry")
        seen.add(cursor)
        record = by_uuid[cursor]
        chain.append(record)
        cursor = record.get("parentUuid")
    chain.reverse()
    return chain, anchor


def direct_item(record: dict[str, Any]) -> Item:
    value = content(record)
    timestamp = record_timestamp(record)
    if isinstance(value, str):
        if not value:
            raise RecallError("empty user message")
        return Item("User message", value, timestamp)
    if not isinstance(value, list) or not value:
        raise RecallError("invalid user message")

    texts: list[str] = []
    images = 0
    for block in value:
        if not isinstance(block, dict) or not isinstance(block.get("type"), str):
            raise RecallError("unknown user content block")
        if block["type"] == "image":
            images += 1
        elif block["type"] == "text":
            text = block.get("text")
            if not isinstance(text, str) or not text:
                raise RecallError("invalid user text block")
            texts.append(text)
        else:
            raise RecallError(f"unsupported user content: {block['type']}")
    note = f"{images} image block(s) omitted" if images else None
    return Item("User message", "\n".join(texts) or None, timestamp, note)


def ask_sources(chain: list[dict[str, Any]]) -> dict[str, str]:
    sources: dict[str, str] = {}
    for record in chain:
        if record.get("type") != "assistant" or not isinstance(content(record), list):
            continue
        for block in content(record):
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") != "AskUserQuestion":
                continue
            tool_id = block.get("id")
            source_uuid = record.get("uuid")
            if (
                not isinstance(tool_id, str)
                or not isinstance(source_uuid, str)
                or tool_id in sources
            ):
                raise RecallError("invalid AskUserQuestion call")
            sources[tool_id] = source_uuid
    return sources


def answer_item(record: dict[str, Any], sources: dict[str, str]) -> Item | None:
    value = content(record)
    if record.get("type") != "user" or not isinstance(value, list):
        return None
    matched = [
        block.get("tool_use_id")
        for block in value
        if isinstance(block, dict)
        and block.get("type") == "tool_result"
        and block.get("tool_use_id") in sources
    ]
    if not matched:
        return None
    if len(matched) != 1:
        raise RecallError("ambiguous AskUserQuestion result")
    tool_id = matched[0]
    if record.get("sourceToolAssistantUUID") != sources[tool_id]:
        raise RecallError("AskUserQuestion source mismatch")

    result = record.get("toolUseResult")
    answers = result.get("answers") if isinstance(result, dict) else None
    if not isinstance(answers, dict) or not answers:
        raise RecallError("AskUserQuestion answer is not structured")

    lines: list[str] = []
    for question, raw_answer in answers.items():
        if not isinstance(question, str):
            raise RecallError("invalid AskUserQuestion prompt")
        values = [raw_answer] if isinstance(raw_answer, str) else raw_answer
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(answer, str) and answer for answer in values)
        ):
            raise RecallError("invalid AskUserQuestion answer")
        lines.extend(
            (
                f"Question from Claude: {question}",
                f"Recorded answer: {', '.join(values)}",
            )
        )
    return Item(
        "AskUserQuestion response",
        "\n".join(lines),
        record_timestamp(record),
    )


def recall(
    records: list[dict[str, Any]],
    *,
    include_current_turn: bool,
) -> list[Item]:
    chain, anchor = active_chain(records)
    sources = ask_sources(chain)
    items: list[Item] = []
    for record in chain:
        if is_direct_user(record):
            if include_current_turn or record.get("uuid") != anchor:
                items.append(direct_item(record))
            continue
        answer = answer_item(record, sources)
        if answer is not None:
            items.append(answer)
    return items


def render(
    items: list[Item],
    *,
    show_all: bool,
    include_current_turn: bool,
) -> str:
    selected = items if show_all else items[-DEFAULT_LIMIT:]
    current_state = "included" if include_current_turn else "excluded"
    label = "User input" if include_current_turn else "Prior user input"
    lines = [
        f"{label}: {len(selected)}/{len(items)}; current turn {current_state}"
    ]
    for item in selected:
        header = (
            f"{item.label} · source_timestamp: {item.source_timestamp}"
        )
        lines.extend(("", f"--- {header} ---"))
        lines.append(item.body or "[no text; image content omitted]")
        if item.note:
            lines.append(f"Note: {item.note}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--all", action="store_true", dest="show_all")
    parser.add_argument("--include-current-turn", action="store_true")
    args = parser.parse_args()
    try:
        session_id = canonical_session_id(args.session_id)
        records = load_records(resolve_transcript(session_id), session_id)
        items = recall(
            records,
            include_current_turn=args.include_current_turn,
        )
        print(
            render(
                items,
                show_all=args.show_all,
                include_current_turn=args.include_current_turn,
            )
        )
    except (OSError, RecallError) as exc:
        print(f"chat-recall: error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
