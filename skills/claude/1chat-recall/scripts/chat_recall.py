#!/usr/bin/env python3
"""Recover user-authored input from the current Claude Code transcript."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid as uuid_module
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


class RecallError(RuntimeError):
    """Raised when provenance cannot be established without guessing."""


@dataclass(frozen=True)
class IndexedRecord:
    line: int
    data: dict[str, Any]

    @property
    def uuid(self) -> str | None:
        value = self.data.get("uuid")
        return value if isinstance(value, str) else None


@dataclass(frozen=True)
class QuestionSpec:
    question: str
    option_labels: tuple[str, ...]
    multi_select: bool


@dataclass(frozen=True)
class QuestionAnswer:
    question: str
    selections: tuple[str, ...]
    free_text: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "selections": list(self.selections),
            "free_text": list(self.free_text),
        }


@dataclass(frozen=True)
class RecallItem:
    record_id: str
    kind: str
    line: int
    timestamp: str | None
    source_uuid: str
    text: str | None = None
    answers: tuple[QuestionAnswer, ...] = ()
    omissions: tuple[str, ...] = ()

    def search_text(self) -> str:
        parts = [self.text or ""]
        for answer in self.answers:
            parts.extend((answer.question, *answer.selections, *answer.free_text))
        return "\n".join(parts)

    def as_dict(self, *, verbose: bool) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.record_id,
            "kind": self.kind,
            "timestamp": self.timestamp,
        }
        if self.kind == "message":
            result["text"] = self.text
        if self.answers:
            result["answers"] = [answer.as_dict() for answer in self.answers]
        if self.omissions:
            result["omissions"] = list(self.omissions)
        if verbose:
            result["source_uuid"] = self.source_uuid
            result["source_line"] = self.line
        return result


@dataclass(frozen=True)
class Snapshot:
    session_id: str
    transcript: Path
    anchor_uuid: str
    items: tuple[RecallItem, ...]
    warnings: tuple[str, ...] = ()


def canonical_session_id(raw: str) -> str:
    try:
        parsed = uuid_module.UUID(raw)
    except ValueError as exc:
        raise RecallError(f"invalid Claude session id: {raw!r}") from exc
    canonical = str(parsed)
    if raw != canonical:
        raise RecallError(f"session id must use canonical UUID form: {canonical}")
    return canonical


def claude_config_dir() -> Path:
    configured = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(configured).expanduser() if configured else Path.home() / ".claude"


def resolve_transcript(session_id: str) -> Path:
    projects = claude_config_dir() / "projects"
    candidates = sorted(
        path for path in projects.glob(f"*/{session_id}.jsonl") if path.is_file()
    )
    if not candidates:
        raise RecallError(
            f"no transcript found for current session {session_id} under {projects}"
        )
    if len(candidates) != 1:
        rendered = ", ".join(str(path) for path in candidates)
        raise RecallError(
            f"ambiguous current session: found {len(candidates)} transcripts: {rendered}"
        )
    return candidates[0]


def load_transcript(path: Path, session_id: str) -> tuple[IndexedRecord, ...]:
    records: list[IndexedRecord] = []
    seen_uuids: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RecallError(f"cannot read transcript {path}: {exc}") from exc

    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise RecallError(
                f"invalid JSON at {path}:{line_number}: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise RecallError(f"non-object transcript record at {path}:{line_number}")
        if value.get("sessionId") != session_id:
            raise RecallError(
                f"session mismatch at {path}:{line_number}; refusing mixed provenance"
            )

        record_uuid = value.get("uuid")
        if record_uuid is not None:
            if not isinstance(record_uuid, str) or not record_uuid:
                raise RecallError(f"invalid uuid at {path}:{line_number}")
            if record_uuid in seen_uuids:
                raise RecallError(
                    f"duplicate uuid {record_uuid!r} at {path}:{line_number}"
                )
            seen_uuids.add(record_uuid)

            parent_uuid = value.get("parentUuid")
            if parent_uuid is not None and not isinstance(parent_uuid, str):
                raise RecallError(f"invalid parentUuid at {path}:{line_number}")

        records.append(IndexedRecord(line_number, value))

    if not records:
        raise RecallError(f"empty transcript: {path}")
    return tuple(records)


def message_content(record: IndexedRecord) -> Any:
    message = record.data.get("message")
    return message.get("content") if isinstance(message, dict) else None


def is_direct_human_message(record: IndexedRecord) -> bool:
    data = record.data
    if data.get("type") != "user":
        return False
    message = data.get("message")
    if not isinstance(message, dict) or message.get("role") != "user":
        return False
    if data.get("isMeta") is True:
        return False
    if data.get("isMeta") not in (None, False):
        raise RecallError(f"unknown isMeta value at transcript line {record.line}")
    if data.get("sourceToolAssistantUUID") is not None:
        return False
    if data.get("sourceToolUseID") is not None:
        return False

    origin = data.get("origin")
    if origin is not None:
        if not isinstance(origin, dict) or not isinstance(origin.get("kind"), str):
            raise RecallError(
                f"unknown user origin schema at transcript line {record.line}"
            )
        if origin["kind"] == "task-notification":
            return False
        if origin["kind"] != "human":
            raise RecallError(
                f"unknown user origin {origin['kind']!r} at transcript line {record.line}"
            )

    content = message.get("content")
    if isinstance(content, list) and any(
        isinstance(block, dict) and block.get("type") == "tool_result"
        for block in content
    ):
        return False
    if isinstance(content, (str, list)):
        return True
    raise RecallError(
        f"unknown direct human content schema at transcript line {record.line}"
    )


def extract_direct_content(record: IndexedRecord) -> tuple[str | None, tuple[str, ...]]:
    content = message_content(record)
    if isinstance(content, str):
        if not content:
            raise RecallError(
                f"empty direct user message at transcript line {record.line}"
            )
        return content, ()
    if not isinstance(content, list) or not content:
        raise RecallError(
            f"unknown direct user content at transcript line {record.line}"
        )

    texts: list[str] = []
    image_count = 0
    for block in content:
        if not isinstance(block, dict) or not isinstance(block.get("type"), str):
            raise RecallError(
                f"unknown direct user content block at transcript line {record.line}"
            )
        if block["type"] == "image":
            image_count += 1
            continue
        if block["type"] != "text":
            raise RecallError(
                f"unsupported direct user content type {block['type']!r} "
                f"at transcript line {record.line}"
            )
        text = block.get("text")
        if not isinstance(text, str) or not text:
            raise RecallError(
                f"invalid user text block at transcript line {record.line}"
            )
        texts.append(text)
    omissions = (f"{image_count} image block(s) omitted",) if image_count else ()
    text = "\n".join(texts) if texts else None
    return text, omissions


def active_chain(
    records: Sequence[IndexedRecord], anchor: IndexedRecord
) -> tuple[IndexedRecord, ...]:
    by_uuid = {record.uuid: record for record in records if record.uuid is not None}
    if anchor.uuid is None:
        raise RecallError("current human message has no uuid")

    chain: list[IndexedRecord] = []
    seen: set[str] = set()
    current_uuid: str | None = anchor.uuid
    while current_uuid is not None:
        if current_uuid in seen:
            raise RecallError(f"cycle in transcript ancestry at uuid {current_uuid}")
        seen.add(current_uuid)
        current = by_uuid.get(current_uuid)
        if current is None:
            raise RecallError(
                f"broken transcript ancestry: missing uuid {current_uuid}"
            )
        chain.append(current)
        current_uuid = current.data.get("parentUuid")

    chain.reverse()
    return tuple(chain)


def timestamp_of(record: IndexedRecord) -> str | None:
    value = record.data.get("timestamp")
    if value is None:
        return None
    if not isinstance(value, str):
        raise RecallError(f"invalid timestamp at transcript line {record.line}")
    return value


def stable_id(session_id: str, kind: str, source: str) -> str:
    digest = hashlib.sha256(f"{session_id}:{kind}:{source}".encode()).hexdigest()[:12]
    prefix = "u" if kind == "message" else "q"
    return f"{prefix}-{digest}"


def parse_question_specs(value: Any, *, line: int) -> tuple[QuestionSpec, ...]:
    if not isinstance(value, list) or not value:
        raise RecallError(
            f"invalid AskUserQuestion questions at transcript line {line}"
        )
    specs: list[QuestionSpec] = []
    seen_questions: set[str] = set()
    for raw_question in value:
        if not isinstance(raw_question, dict):
            raise RecallError(f"invalid AskUserQuestion item at transcript line {line}")
        question = raw_question.get("question")
        if not isinstance(question, str) or not question:
            raise RecallError(f"invalid AskUserQuestion text at transcript line {line}")
        if question in seen_questions:
            raise RecallError(
                f"duplicate AskUserQuestion text at transcript line {line}"
            )
        seen_questions.add(question)

        raw_options = raw_question.get("options", [])
        if not isinstance(raw_options, list):
            raise RecallError(
                f"invalid AskUserQuestion options at transcript line {line}"
            )
        labels: list[str] = []
        for option in raw_options:
            if not isinstance(option, dict):
                raise RecallError(
                    f"invalid AskUserQuestion option at transcript line {line}"
                )
            label = option.get("label")
            if not isinstance(label, str) or not label:
                raise RecallError(
                    f"invalid AskUserQuestion label at transcript line {line}"
                )
            labels.append(label)
        if len(labels) != len(set(labels)):
            raise RecallError(
                f"duplicate AskUserQuestion label at transcript line {line}"
            )

        multi_select = raw_question.get("multiSelect", False)
        if not isinstance(multi_select, bool):
            raise RecallError(f"invalid multiSelect at transcript line {line}")
        specs.append(QuestionSpec(question, tuple(labels), multi_select))
    return tuple(specs)


def question_signature(specs: Sequence[QuestionSpec]) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (spec.question, spec.option_labels, spec.multi_select) for spec in specs
    )


def parse_answer_values(
    value: Any, *, line: int, multi_select: bool
) -> tuple[str, ...]:
    if isinstance(value, str):
        values = (value,)
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        values = tuple(value)
    else:
        raise RecallError(
            f"unknown AskUserQuestion answer schema at transcript line {line}"
        )
    if not values or any(not item for item in values):
        raise RecallError(f"empty AskUserQuestion answer at transcript line {line}")
    if not multi_select and len(values) != 1:
        raise RecallError(
            f"multiple answers for single-select question at transcript line {line}"
        )
    if len(values) != len(set(values)):
        raise RecallError(f"duplicate AskUserQuestion answer at transcript line {line}")
    return values


def parse_question_answers(
    result_record: IndexedRecord, expected: Sequence[QuestionSpec]
) -> tuple[QuestionAnswer, ...]:
    tool_result = result_record.data.get("toolUseResult")
    if isinstance(tool_result, str):
        raise RecallError(
            "legacy AskUserQuestion result has no structured provenance at transcript "
            f"line {result_record.line}; update Claude Code or recover manually"
        )
    if not isinstance(tool_result, dict):
        raise RecallError(
            f"unknown AskUserQuestion result schema at transcript line {result_record.line}"
        )

    echoed = parse_question_specs(tool_result.get("questions"), line=result_record.line)
    if question_signature(echoed) != question_signature(expected):
        raise RecallError(
            f"AskUserQuestion prompt/result mismatch at transcript line {result_record.line}"
        )

    answers = tool_result.get("answers")
    if not isinstance(answers, dict):
        raise RecallError(
            f"missing AskUserQuestion answers at transcript line {result_record.line}"
        )
    expected_keys = {spec.question for spec in expected}
    if set(answers) != expected_keys:
        raise RecallError(
            f"AskUserQuestion answer keys mismatch at transcript line {result_record.line}"
        )

    parsed: list[QuestionAnswer] = []
    for spec in expected:
        values = parse_answer_values(
            answers[spec.question],
            line=result_record.line,
            multi_select=spec.multi_select,
        )
        label_set = set(spec.option_labels)
        selections = tuple(value for value in values if value in label_set)
        free_text = tuple(value for value in values if value not in label_set)
        parsed.append(QuestionAnswer(spec.question, selections, free_text))
    return tuple(parsed)


def extract_question_items(
    chain: Sequence[IndexedRecord], session_id: str
) -> tuple[RecallItem, ...]:
    asks: dict[str, tuple[IndexedRecord, tuple[QuestionSpec, ...]]] = {}
    for record in chain:
        if record.data.get("type") != "assistant":
            continue
        content = message_content(record)
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") != "AskUserQuestion":
                continue
            tool_id = block.get("id")
            tool_input = block.get("input")
            if (
                not isinstance(tool_id, str)
                or not tool_id
                or not isinstance(tool_input, dict)
            ):
                raise RecallError(
                    f"invalid AskUserQuestion tool call at transcript line {record.line}"
                )
            if tool_id in asks:
                raise RecallError(f"duplicate AskUserQuestion tool id {tool_id!r}")
            asks[tool_id] = (
                record,
                parse_question_specs(tool_input.get("questions"), line=record.line),
            )

    matched: dict[str, IndexedRecord] = {}
    for record in chain:
        if record.data.get("type") != "user":
            continue
        content = message_content(record)
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            tool_id = block.get("tool_use_id")
            if tool_id not in asks:
                continue
            if tool_id in matched:
                raise RecallError(
                    f"duplicate result for AskUserQuestion tool id {tool_id!r}"
                )
            assistant_record, _ = asks[tool_id]
            if record.data.get("sourceToolAssistantUUID") != assistant_record.uuid:
                raise RecallError(
                    f"AskUserQuestion source mismatch at transcript line {record.line}"
                )
            matched[tool_id] = record

    items: list[RecallItem] = []
    for tool_id, (assistant_record, specs) in asks.items():
        result_record = matched.get(tool_id)
        if result_record is None:
            continue
        if result_record.uuid is None:
            raise RecallError(
                f"AskUserQuestion result has no uuid at line {result_record.line}"
            )
        items.append(
            RecallItem(
                record_id=stable_id(session_id, "question", tool_id),
                kind="question",
                line=result_record.line,
                timestamp=timestamp_of(result_record),
                source_uuid=result_record.uuid,
                answers=parse_question_answers(result_record, specs),
            )
        )
    return tuple(items)


def build_snapshot(session_id: str, *, include_current_turn: bool) -> Snapshot:
    transcript = resolve_transcript(session_id)
    records = load_transcript(transcript, session_id)
    direct_messages = [record for record in records if is_direct_human_message(record)]
    if not direct_messages:
        raise RecallError("current transcript has no direct human message anchor")
    anchor = direct_messages[-1]
    if anchor.uuid is None:
        raise RecallError("current direct human message has no uuid")
    chain = active_chain(records, anchor)

    items: list[RecallItem] = list(extract_question_items(chain, session_id))
    for record in chain:
        if not is_direct_human_message(record):
            continue
        if not include_current_turn and record.uuid == anchor.uuid:
            continue
        if record.uuid is None:
            raise RecallError(f"direct human message has no uuid at line {record.line}")
        text, omissions = extract_direct_content(record)
        items.append(
            RecallItem(
                record_id=stable_id(session_id, "message", record.uuid),
                kind="message",
                line=record.line,
                timestamp=timestamp_of(record),
                source_uuid=record.uuid,
                text=text,
                omissions=omissions,
            )
        )
    items.sort(key=lambda item: item.line)
    warnings = tuple(
        f"{item.record_id}: {omission}" for item in items for omission in item.omissions
    )
    return Snapshot(session_id, transcript, anchor.uuid, tuple(items), warnings)


def items_for_scope(items: Iterable[RecallItem], scope: str) -> list[RecallItem]:
    if scope == "messages":
        return [item for item in items if item.kind == "message"]
    if scope == "questions":
        return [item for item in items if item.kind == "question"]
    return list(items)


def parse_limit(raw: str) -> int | None:
    if raw == "all":
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "limit must be a positive integer or 'all'"
        ) from exc
    if value < 1:
        raise argparse.ArgumentTypeError("limit must be a positive integer or 'all'")
    return value


def latest(items: Sequence[RecallItem], limit: int | None) -> list[RecallItem]:
    return list(items if limit is None else items[-limit:])


def make_envelope(
    snapshot: Snapshot,
    *,
    scope: str,
    selected: Sequence[RecallItem],
    total: int,
    selection: str,
    current_turn_excluded: bool,
    verbose: bool,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "schema_version": 1,
        "verified_session": True,
        "session_id": snapshot.session_id,
        "scope": scope,
        "current_turn_excluded": current_turn_excluded,
        "selection": selection,
        "returned": len(selected),
        "total": total,
        "warnings": list(snapshot.warnings),
        "records": [item.as_dict(verbose=verbose) for item in selected],
    }
    if verbose:
        envelope["transcript"] = str(snapshot.transcript)
        envelope["active_anchor_uuid"] = snapshot.anchor_uuid
    return envelope


def render_text(envelope: dict[str, Any]) -> str:
    lines = [
        "Claude session recall",
        f"Session: {envelope['session_id']}",
        f"Scope: {envelope['scope']}",
        f"Coverage: {envelope['returned']}/{envelope['total']} ({envelope['selection']})",
        "Current turn: "
        + ("excluded" if envelope["current_turn_excluded"] else "included"),
        "Warnings: " + (", ".join(envelope["warnings"]) or "none"),
    ]
    if "transcript" in envelope:
        lines.extend(
            (
                f"Transcript: {envelope['transcript']}",
                f"Active anchor: {envelope['active_anchor_uuid']}",
            )
        )

    for record in envelope["records"]:
        lines.extend(
            (
                "",
                f"[{record['id']}] {record['kind']} · {record['timestamp'] or 'no timestamp'}",
            )
        )
        if record["kind"] == "message":
            if record["text"] is not None:
                lines.extend(("Точные текстовые блоки пользователя:", record["text"]))
            else:
                lines.append("Текстовых блоков пользователя нет.")
            for omission in record.get("omissions", []):
                lines.append(f"Omission: {omission}")
        else:
            for answer in record["answers"]:
                lines.append(f"Вопрос Claude: {answer['question']}")
                if answer["selections"]:
                    lines.append(
                        "Пользователь выбрал вариант: "
                        + ", ".join(answer["selections"])
                    )
                for free_text in answer["free_text"]:
                    lines.append(f"Ответ пользователя: {free_text}")
        if "source_uuid" in record:
            lines.append(
                f"Source: line {record['source_line']}, uuid {record['source_uuid']}"
            )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recover user-authored input from one verified Claude Code session."
    )
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--verbose", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    read = subparsers.add_parser("read", help="Read recent or exhaustive user input.")
    read.add_argument(
        "--scope", choices=("user", "messages", "questions"), default="user"
    )
    read.add_argument("--limit", type=parse_limit, default=5, metavar="N|all")
    read.add_argument("--include-current-turn", action="store_true")

    search = subparsers.add_parser(
        "search", help="Search user input by case-insensitive text."
    )
    search.add_argument("query")
    search.add_argument(
        "--scope", choices=("user", "messages", "questions"), default="user"
    )
    search.add_argument("--limit", type=parse_limit, default=None, metavar="N|all")
    search.add_argument("--include-current-turn", action="store_true")

    show = subparsers.add_parser("show", help="Show one record by stable id.")
    show.add_argument("record_id")
    show.add_argument("--include-current-turn", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    session_id = canonical_session_id(args.session_id)
    include_current_turn = bool(args.include_current_turn)
    snapshot = build_snapshot(session_id, include_current_turn=include_current_turn)
    current_turn_excluded = not include_current_turn

    if args.command == "read":
        scoped = items_for_scope(snapshot.items, args.scope)
        selected = latest(scoped, args.limit)
        selection = "all" if args.limit is None else f"latest {args.limit}"
        return make_envelope(
            snapshot,
            scope=args.scope,
            selected=selected,
            total=len(scoped),
            selection=selection,
            current_turn_excluded=current_turn_excluded,
            verbose=args.verbose,
        )

    if args.command == "search":
        scoped = items_for_scope(snapshot.items, args.scope)
        query = args.query.casefold()
        if not query:
            raise RecallError("search query must not be empty")
        matches = [item for item in scoped if query in item.search_text().casefold()]
        selected = latest(matches, args.limit)
        selection = f"search {args.query!r}"
        if args.limit is not None:
            selection += f", latest {args.limit}"
        return make_envelope(
            snapshot,
            scope=args.scope,
            selected=selected,
            total=len(matches),
            selection=selection,
            current_turn_excluded=current_turn_excluded,
            verbose=args.verbose,
        )

    matches = [item for item in snapshot.items if item.record_id == args.record_id]
    if len(matches) != 1:
        raise RecallError(
            f"record id not found in active session branch: {args.record_id}"
        )
    return make_envelope(
        snapshot,
        scope="user",
        selected=matches,
        total=len(snapshot.items),
        selection=f"record {args.record_id}",
        current_turn_excluded=current_turn_excluded,
        verbose=args.verbose,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        envelope = run(args)
    except RecallError as exc:
        print(f"chat-recall: error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(envelope, ensure_ascii=False, indent=2))
    else:
        print(render_text(envelope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
