#!/usr/bin/env python3
"""Recover exact user evidence from the current Codex thread transcript."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


THREAD_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
AUTO_MAX_CHARS = 16_000
AUTO_LATEST_COUNT = 5


class RecallError(RuntimeError):
    """The transcript cannot support an exact recall result."""


@dataclass(frozen=True)
class RawMessage:
    turn_id: str
    timestamp: str
    text: str
    sequence: int
    ordinal: int


@dataclass(frozen=True)
class RawPlanCall:
    turn_id: str
    timestamp: str
    call_id: str
    arguments: str
    sequence: int


@dataclass(frozen=True)
class RawPlanOutput:
    turn_id: str
    timestamp: str
    call_id: str
    output: Any
    sequence: int


@dataclass(frozen=True)
class Option:
    label: str
    description: str


@dataclass(frozen=True)
class Question:
    question_id: str
    header: str
    text: str
    options: tuple[Option, ...]


@dataclass(frozen=True)
class RecallRecord:
    record_id: str
    kind: str
    timestamp: str
    turn_id: str
    sequence: int
    text: str | None = None
    question_id: str | None = None
    question: str | None = None
    answers: tuple[str, ...] = ()
    selected_options: tuple[Option, ...] = ()

    def search_text(self) -> str:
        parts = [self.text or "", self.question or "", *self.answers]
        parts.extend(option.description for option in self.selected_options)
        return "\n".join(parts).casefold()


@dataclass(frozen=True)
class TranscriptSnapshot:
    thread_id: str
    transcript_name: str
    records: tuple[RecallRecord, ...]
    active_turn_ids: tuple[str, ...]
    current_turn_id: str | None
    compactions: int
    warnings: tuple[str, ...]


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def codex_root() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def session_id_from_file(path: Path) -> str | None:
    with path.open("r", encoding="utf-8") as stream:
        for _ in range(40):
            line = stream.readline()
            if not line:
                return None
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise RecallError(
                    f"Invalid JSON near the start of {path.name}: {error}"
                ) from error
            if record.get("type") == "session_meta":
                session_id = record.get("payload", {}).get("id")
                return session_id if isinstance(session_id, str) else None
    return None


def resolve_current_transcript(thread_id: str, *, repair: bool = False) -> Path:
    sessions_root = codex_root() / "sessions"
    if not sessions_root.is_dir():
        raise RecallError(f"Codex sessions directory is missing: {sessions_root}")

    candidates = sorted(sessions_root.rglob(f"*{thread_id}*.jsonl"))
    matches = [path for path in candidates if session_id_from_file(path) == thread_id]
    if not matches:
        scope = "repair session" if repair else "live CODEX_THREAD_ID"
        raise RecallError(f"No transcript matches the {scope}")
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise RecallError(
            f"Multiple transcripts match the requested session: {names}"
        )
    return matches[0]


def reject_duplicate_repair_holders(thread_id: str) -> None:
    corpus = Path.cwd() / "_ops" / "chat-recall"
    holders = []
    if corpus.is_dir():
        marker = f"session: {thread_id}"
        for path in corpus.glob("*.md"):
            lines = path.read_text(encoding="utf-8-sig").splitlines()
            if not lines or lines[0].strip() != "---":
                continue
            try:
                end = next(
                    index
                    for index, line in enumerate(lines[1:], start=1)
                    if line.strip() == "---"
                )
            except StopIteration:
                continue
            if marker in (line.strip() for line in lines[1:end]):
                holders.append(path)
    if len(holders) > 1:
        names = ", ".join(path.name for path in holders)
        raise RecallError(f"repair session has duplicate holders: {names}")


def load_jsonl_snapshot(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    data = path.read_bytes()
    has_complete_last_line = data.endswith(b"\n")
    raw_lines = data.splitlines()
    records: list[dict[str, Any]] = []
    warnings: list[str] = []

    for index, raw_line in enumerate(raw_lines, start=1):
        try:
            decoded = raw_line.decode("utf-8")
            record = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            is_partial_tail = index == len(raw_lines) and not has_complete_last_line
            if is_partial_tail:
                warnings.append("Ignored one partial trailing transcript line")
                break
            raise RecallError(
                f"Invalid transcript JSON at line {index}: {error}"
            ) from error
        if not isinstance(record, dict):
            raise RecallError(f"Transcript line {index} is not a JSON object")
        records.append(record)
    return records, warnings


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise RecallError(f"Expected string for {label}")
    return value


def require_timestamp(value: Any, label: str) -> str:
    raw = require_string(value, label)
    normalized = f"{raw[:-1]}+00:00" if raw.endswith(("Z", "z")) else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise RecallError(f"Invalid source timestamp for {label}") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RecallError(f"Source timestamp for {label} has no timezone")
    return raw


def parse_questions(raw_arguments: str, call_id: str) -> tuple[Question, ...]:
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as error:
        raise RecallError(
            f"Invalid request_user_input arguments for {call_id}: {error}"
        ) from error
    raw_questions = arguments.get("questions") if isinstance(arguments, dict) else None
    if not isinstance(raw_questions, list):
        raise RecallError(f"request_user_input {call_id} has no questions list")

    questions: list[Question] = []
    seen_ids: set[str] = set()
    for raw_question in raw_questions:
        if not isinstance(raw_question, dict):
            raise RecallError(
                f"request_user_input {call_id} contains a non-object question"
            )
        question_id = require_string(raw_question.get("id"), f"{call_id}.question.id")
        if question_id in seen_ids:
            raise RecallError(
                f"request_user_input {call_id} repeats question id {question_id}"
            )
        seen_ids.add(question_id)

        raw_options = raw_question.get("options", [])
        if not isinstance(raw_options, list):
            raise RecallError(f"Question {question_id} has a non-list options value")
        options: list[Option] = []
        for raw_option in raw_options:
            if not isinstance(raw_option, dict):
                raise RecallError(
                    f"Question {question_id} contains a non-object option"
                )
            options.append(
                Option(
                    label=require_string(
                        raw_option.get("label"), f"{question_id}.option.label"
                    ),
                    description=require_string(
                        raw_option.get("description", ""),
                        f"{question_id}.option.description",
                    ),
                )
            )
        questions.append(
            Question(
                question_id=question_id,
                header=require_string(
                    raw_question.get("header", ""), f"{question_id}.header"
                ),
                text=require_string(
                    raw_question.get("question"), f"{question_id}.question"
                ),
                options=tuple(options),
            )
        )
    return tuple(questions)


def parse_answers(raw_output: str, call_id: str) -> dict[str, tuple[str, ...]]:
    try:
        output = json.loads(raw_output)
    except json.JSONDecodeError as error:
        raise RecallError(
            f"Invalid request_user_input output for {call_id}: {error}"
        ) from error
    raw_answers = output.get("answers") if isinstance(output, dict) else None
    if not isinstance(raw_answers, dict):
        raise RecallError(f"request_user_input output {call_id} has no answers object")

    answers: dict[str, tuple[str, ...]] = {}
    for question_id, raw_answer in raw_answers.items():
        if not isinstance(question_id, str) or not isinstance(raw_answer, dict):
            raise RecallError(
                f"request_user_input output {call_id} has malformed answers"
            )
        values = raw_answer.get("answers")
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise RecallError(f"Answer {question_id} in {call_id} is not a string list")
        answers[question_id] = tuple(values)
    return answers


def build_snapshot(thread_id: str, transcript_path: Path) -> TranscriptSnapshot:
    jsonl_records, warnings = load_jsonl_snapshot(transcript_path)
    session_ids = {
        record.get("payload", {}).get("id")
        for record in jsonl_records
        if record.get("type") == "session_meta"
    }
    if thread_id not in session_ids:
        raise RecallError("Transcript session_meta does not match CODEX_THREAD_ID")

    active_turns: list[str] = []
    current_turn: str | None = None
    running_turns: set[str] = set()
    message_ordinals: defaultdict[str, int] = defaultdict(int)
    raw_messages: list[RawMessage] = []
    raw_calls: list[RawPlanCall] = []
    raw_outputs: list[RawPlanOutput] = []
    compactions = 0

    for sequence, record in enumerate(jsonl_records, start=1):
        record_type = record.get("type")
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue

        if record_type == "event_msg":
            event_type = payload.get("type")
            if event_type == "task_started":
                turn_id = require_string(payload.get("turn_id"), "task_started.turn_id")
                if turn_id not in active_turns:
                    active_turns.append(turn_id)
                current_turn = turn_id
                running_turns.add(turn_id)
                continue
            if event_type == "thread_rolled_back":
                count = payload.get("num_turns")
                if not isinstance(count, int) or count < 0 or count > len(active_turns):
                    raise RecallError(f"Invalid thread_rolled_back count: {count!r}")
                removed = active_turns[-count:] if count else []
                if count:
                    del active_turns[-count:]
                running_turns.difference_update(removed)
                if current_turn in removed:
                    current_turn = None
                continue
            if event_type == "user_message":
                if current_turn is None:
                    warnings.append("Ignored a user_message outside a task turn")
                    continue
                text = payload.get("message")
                if not isinstance(text, str):
                    warnings.append(
                        f"Ignored a non-text user_message in turn {current_turn}"
                    )
                    continue
                message_ordinals[current_turn] += 1
                raw_messages.append(
                    RawMessage(
                        turn_id=current_turn,
                        timestamp=require_timestamp(
                            record.get("timestamp", ""), "user_message.timestamp"
                        ),
                        text=text,
                        sequence=sequence,
                        ordinal=message_ordinals[current_turn],
                    )
                )
                continue
            if event_type == "context_compacted":
                compactions += 1
                continue
            if event_type in {"task_complete", "turn_aborted"}:
                turn_id = payload.get("turn_id")
                if isinstance(turn_id, str):
                    running_turns.discard(turn_id)
                    if current_turn == turn_id:
                        current_turn = None
                continue

        if record_type != "response_item" or current_turn is None:
            continue
        item_type = payload.get("type")
        if item_type == "function_call" and payload.get("name") == "request_user_input":
            raw_calls.append(
                RawPlanCall(
                    turn_id=current_turn,
                    timestamp=require_timestamp(
                        record.get("timestamp", ""), "plan_call.timestamp"
                    ),
                    call_id=require_string(
                        payload.get("call_id"), "request_user_input.call_id"
                    ),
                    arguments=require_string(
                        payload.get("arguments"), "request_user_input.arguments"
                    ),
                    sequence=sequence,
                )
            )
        elif item_type == "function_call_output":
            call_id = payload.get("call_id")
            if isinstance(call_id, str):
                raw_outputs.append(
                    RawPlanOutput(
                        turn_id=current_turn,
                        timestamp=require_timestamp(
                            record.get("timestamp", ""), "plan_output.timestamp"
                        ),
                        call_id=call_id,
                        output=payload.get("output"),
                        sequence=sequence,
                    )
                )

    active_set = set(active_turns)
    records: list[RecallRecord] = []
    for message in raw_messages:
        if message.turn_id not in active_set:
            continue
        records.append(
            RecallRecord(
                record_id=stable_id(
                    "msg",
                    thread_id,
                    message.turn_id,
                    str(message.ordinal),
                ),
                kind="chat_message",
                timestamp=message.timestamp,
                turn_id=message.turn_id,
                sequence=message.sequence * 100,
                text=message.text,
            )
        )

    active_outputs: dict[str, RawPlanOutput] = {}
    for output in raw_outputs:
        if output.turn_id not in active_set:
            continue
        if output.call_id in active_outputs:
            raise RecallError(f"Duplicate function_call_output for {output.call_id}")
        active_outputs[output.call_id] = output

    active_call_ids: set[str] = set()
    for call in raw_calls:
        if call.turn_id not in active_set:
            continue
        if call.call_id in active_call_ids:
            raise RecallError(f"Duplicate request_user_input call id {call.call_id}")
        active_call_ids.add(call.call_id)
        output = active_outputs.get(call.call_id)
        if output is None:
            warnings.append(
                f"No user answer recorded for request_user_input {call.call_id}"
            )
            continue
        if output.turn_id != call.turn_id:
            raise RecallError(f"Plan call/output turn mismatch for {call.call_id}")

        questions = parse_questions(call.arguments, call.call_id)
        answers = parse_answers(
            require_string(output.output, f"request_user_input.output.{call.call_id}"),
            call.call_id,
        )
        known_question_ids = {question.question_id for question in questions}
        unknown_answer_ids = set(answers) - known_question_ids
        if unknown_answer_ids:
            unknown = ", ".join(sorted(unknown_answer_ids))
            warnings.append(f"Ignored unknown answer ids in {call.call_id}: {unknown}")

        for question_index, question in enumerate(questions, start=1):
            answer_values = answers.get(question.question_id)
            if not answer_values:
                warnings.append(
                    f"No answer recorded for question {question.question_id} in {call.call_id}"
                )
                continue
            option_by_label = {option.label: option for option in question.options}
            is_selection = all(value in option_by_label for value in answer_values)
            selected_options = (
                tuple(option_by_label[value] for value in answer_values)
                if is_selection
                else ()
            )
            records.append(
                RecallRecord(
                    record_id=stable_id(
                        "plan",
                        thread_id,
                        call.call_id,
                        question.question_id,
                    ),
                    kind="planning_selection" if is_selection else "planning_free_text",
                    timestamp=output.timestamp,
                    turn_id=call.turn_id,
                    sequence=output.sequence * 100 + question_index,
                    question_id=question.question_id,
                    question=question.text,
                    answers=answer_values,
                    selected_options=selected_options,
                )
            )

    current_candidates = [
        turn_id for turn_id in active_turns if turn_id in running_turns
    ]
    current_turn_id = current_candidates[-1] if current_candidates else None
    records.sort(key=lambda record: record.sequence)
    return TranscriptSnapshot(
        thread_id=thread_id,
        transcript_name=transcript_path.name,
        records=tuple(records),
        active_turn_ids=tuple(active_turns),
        current_turn_id=current_turn_id,
        compactions=compactions,
        warnings=tuple(warnings),
    )


def records_for_scope(
    records: tuple[RecallRecord, ...], scope: str
) -> list[RecallRecord]:
    if scope == "messages":
        return [record for record in records if record.kind == "chat_message"]
    if scope == "planning":
        return [record for record in records if record.kind.startswith("planning_")]
    return list(records)


def render_verbose_record(record: RecallRecord) -> str:
    lines = [
        f"[{record.record_id}] {record.kind}",
        f"timestamp: {record.timestamp}",
        f"turn_id: {record.turn_id}",
    ]
    if record.kind == "chat_message":
        lines.extend(["user_message_verbatim:", record.text or ""])
        return "\n".join(lines)

    lines.extend(
        [
            f"question_id: {record.question_id}",
            "question:",
            record.question or "",
        ]
    )
    if record.kind == "planning_selection":
        for index, answer in enumerate(record.answers, start=1):
            lines.extend([f"user_selected[{index}]:", answer])
            option = record.selected_options[index - 1]
            if option.description:
                lines.extend(
                    [f"selected_option_description[{index}]:", option.description]
                )
    else:
        for index, answer in enumerate(record.answers, start=1):
            lines.extend([f"user_answer_verbatim[{index}]:", answer])
    return "\n".join(lines)


def render_compact_record(record: RecallRecord, label: str) -> str:
    suffix = " · Plan" if record.kind.startswith("planning_") else ""
    lines = [f"[{label}{suffix}]"]
    if record.kind == "chat_message":
        lines.append((record.text or "").rstrip())
        return "\n".join(lines)

    lines.append(f"Вопрос: {record.question or ''}")
    answer_label = "Выбрано" if record.kind == "planning_selection" else "Ответ"
    if len(record.answers) == 1:
        lines.append(f"{answer_label}: {record.answers[0]}")
    else:
        lines.append(f"{answer_label}:")
        lines.extend(f"- {answer}" for answer in record.answers)
    return "\n".join(lines)


def render_compact_meta(meta: dict[str, Any]) -> str:
    parts = [f"Показано {meta['returned']}/{meta['total']}"]
    selection = str(meta["selection"])
    if "latest-" in selection and meta["returned"] < meta["total"]:
        parts.append(f"последние {meta['returned']}")

    order_labels = {
        "chronological": "хронологически",
        "newest-first": "сначала новые",
    }
    order_label = order_labels.get(str(meta["order"]))
    if order_label:
        parts.append(order_label)
    if meta["current_turn_excluded"]:
        parts.append("текущий ход исключён")
    parts.append(f"предупреждений: {len(meta['warnings'])}")
    return " · ".join(parts)


def record_as_json(record: RecallRecord) -> dict[str, Any]:
    payload = asdict(record)
    payload.pop("sequence", None)
    return payload


def emit_json(meta: dict[str, Any], records: list[RecallRecord]) -> None:
    json.dump(
        {"meta": meta, "records": [record_as_json(record) for record in records]},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")


def emit_verbose(meta: dict[str, Any], records: list[RecallRecord]) -> None:
    for key, value in meta.items():
        if key == "warnings":
            print(f"warnings: {len(value)}")
            for warning in value:
                print(f"warning: {warning}")
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}: {rendered}")
    if records:
        print()
        print("\n\n---\n\n".join(render_verbose_record(record) for record in records))


def emit_compact(
    meta: dict[str, Any],
    records: list[RecallRecord],
    *,
    include_record_ids: bool,
) -> None:
    print(render_compact_meta(meta))
    for warning in meta["warnings"]:
        print(f"Предупреждение: {warning}")
    if not records:
        return

    print()
    rendered_records = []
    for index, record in enumerate(records, start=1):
        label = record.record_id if include_record_ids else str(index)
        rendered_records.append(render_compact_record(record, label))
    print("\n\n".join(rendered_records))


def emit(
    snapshot: TranscriptSnapshot,
    records: list[RecallRecord],
    *,
    scope: str,
    total: int,
    selection: str,
    order: str,
    json_output: bool,
    current_turn_excluded: bool,
    verbose: bool,
    include_record_ids: bool,
) -> None:
    meta = {
        "thread_id": snapshot.thread_id,
        "transcript": snapshot.transcript_name,
        "current_thread_only": True,
        "scope": scope,
        "returned": len(records),
        "total": total,
        "selection": selection,
        "order": order,
        "current_turn_excluded": current_turn_excluded,
        "compactions": snapshot.compactions,
        "warnings": list(snapshot.warnings),
    }
    if json_output:
        emit_json(meta, records)
        return
    if verbose:
        emit_verbose(meta, records)
        return
    emit_compact(meta, records, include_record_ids=include_record_ids)


def visible_records(
    snapshot: TranscriptSnapshot, include_current_turn: bool
) -> tuple[list[RecallRecord], bool]:
    if include_current_turn or snapshot.current_turn_id is None:
        return list(snapshot.records), False
    visible = [
        record
        for record in snapshot.records
        if record.turn_id != snapshot.current_turn_id
    ]
    return visible, True


def parse_read_limit(value: str) -> str | int:
    if value in {"auto", "all"}:
        return value
    try:
        count = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "limit must be auto, all, or a positive integer"
        ) from error
    if count <= 0:
        raise argparse.ArgumentTypeError("limit must be positive")
    return count


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="emit detailed human-readable metadata; ignored with --json",
    )
    parser.add_argument(
        "--include-current-turn",
        action="store_true",
        help="include the currently running turn",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Recover user messages and Plan answers from the current Codex thread"
    )
    parser.add_argument(
        "--repair-session",
        metavar="UUID",
        help=(
            "explicit historical session for repair or owner-requested "
            "backfill"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    read_parser = subparsers.add_parser(
        "read", help="read user evidence chronologically"
    )
    read_parser.add_argument(
        "--scope",
        choices=("user", "messages", "planning"),
        default="user",
    )
    read_parser.add_argument("--limit", type=parse_read_limit, default="auto")
    add_output_options(read_parser)

    search_parser = subparsers.add_parser(
        "search", help="search exact transcript evidence"
    )
    search_parser.add_argument("query")
    search_parser.add_argument(
        "--scope",
        choices=("user", "messages", "planning"),
        default="user",
    )
    search_parser.add_argument("--limit", type=int, default=10)
    add_output_options(search_parser)

    show_parser = subparsers.add_parser("show", help="show one complete record")
    show_parser.add_argument("record_id")
    add_output_options(show_parser)
    return parser


def run(args: argparse.Namespace, snapshot: TranscriptSnapshot) -> None:
    visible, current_turn_excluded = visible_records(
        snapshot, args.include_current_turn
    )

    if args.command == "read":
        scoped = records_for_scope(tuple(visible), args.scope)
        total = len(scoped)
        selection: str
        if args.limit == "all":
            selected = scoped
            selection = "all"
        elif isinstance(args.limit, int):
            selected = scoped[-args.limit :]
            selection = f"latest-{args.limit}"
        else:
            rendered_chars = sum(
                len(render_verbose_record(record)) for record in scoped
            )
            if rendered_chars <= AUTO_MAX_CHARS:
                selected = scoped
                selection = f"auto:all-under-{AUTO_MAX_CHARS}-chars"
            else:
                selected = scoped[-AUTO_LATEST_COUNT:]
                selection = (
                    f"auto:latest-{AUTO_LATEST_COUNT}-over-{AUTO_MAX_CHARS}-chars"
                )
        emit(
            snapshot,
            selected,
            scope=args.scope,
            total=total,
            selection=selection,
            order="chronological",
            json_output=args.json,
            current_turn_excluded=current_turn_excluded,
            verbose=args.verbose,
            include_record_ids=False,
        )
        return

    if args.command == "search":
        if args.limit <= 0:
            raise RecallError("search --limit must be positive")
        scoped = records_for_scope(tuple(visible), args.scope)
        query = args.query.casefold()
        matches = [
            record for record in reversed(scoped) if query in record.search_text()
        ]
        selected = matches[: args.limit]
        emit(
            snapshot,
            selected,
            scope=args.scope,
            total=len(matches),
            selection=f"search:{args.query}",
            order="newest-first",
            json_output=args.json,
            current_turn_excluded=current_turn_excluded,
            verbose=args.verbose,
            include_record_ids=True,
        )
        return

    matching = [record for record in visible if record.record_id == args.record_id]
    if not matching:
        raise RecallError(f"Record not found in the current thread: {args.record_id}")
    emit(
        snapshot,
        matching,
        scope="record",
        total=1,
        selection=f"show:{args.record_id}",
        order="single",
        json_output=args.json,
        current_turn_excluded=current_turn_excluded,
        verbose=args.verbose,
        include_record_ids=True,
    )


def main() -> int:
    args = build_parser().parse_args()
    thread_id = args.repair_session or os.environ.get("CODEX_THREAD_ID", "")
    if not THREAD_ID_RE.fullmatch(thread_id):
        source = "--repair-session" if args.repair_session else "live CODEX_THREAD_ID"
        print(f"error: {source} is missing or invalid", file=sys.stderr)
        return 2
    try:
        if args.repair_session:
            reject_duplicate_repair_holders(thread_id)
        transcript_path = resolve_current_transcript(
            thread_id, repair=bool(args.repair_session)
        )
        snapshot = build_snapshot(thread_id, transcript_path)
        run(args, snapshot)
    except RecallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
