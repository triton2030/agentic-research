#!/usr/bin/env python3
"""Lossless inventory and bounded retrieval for `_ops/chat-recall`.

Every Markdown star block is a record. Broken metadata becomes diagnostics and
sentinels; it never makes the block disappear.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from recall_metadata import REPAIR_TOPIC, REPAIR_TYPE, TOPICS, TYPES

KINDS = {"quote", "selection", "note", "raw"}
PRECISIONS = {"exact", "minute", "date", "unknown"}
ENTRY_RE = re.compile(
    r"^\*\s+(?P<timestamp>.+?)\s+—\s+"
    r'(?P<text>".*?"|.*?)\s+—\s+(?P<meta>(?:kind|type|topic|source|precision|source-ref):.*)$',
    re.DOTALL,
)
META_RE = re.compile(
    r"(?:^|\s*\|\s*)(kind|type|topic|source|precision|source-ref):\s*"
    r"([^|\n]*?)(?=\s*\|\s*(?:kind|type|topic|source|precision|source-ref):|$)",
    re.MULTILINE,
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")
QUERY_TOKEN_RE = re.compile(r"[\w-]+\*?", re.UNICODE)


class CliError(RuntimeError):
    """Short, expected command-line failure."""


def _frontmatter(lines: list[str]) -> dict[str, str]:
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ": " in line and not line.startswith((" ", "\t")):
            key, value = line.split(": ", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def _star_blocks(lines: list[str]) -> list[tuple[int, str]]:
    starts = [index for index, line in enumerate(lines) if line.startswith("* ")]
    blocks: list[tuple[int, str]] = []
    for number, start in enumerate(starts):
        end = starts[number + 1] if number + 1 < len(starts) else len(lines)
        raw_lines = lines[start:end]
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()
        while raw_lines and raw_lines[-1].startswith("#"):
            raw_lines.pop()
        blocks.append((start + 1, "\n".join(raw_lines).strip()))
    return blocks


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _record_id(session: str, kind: str, text: str) -> str:
    payload = "\0".join((session, kind, _normalized_text(text))).encode("utf-8")
    return "cr-" + hashlib.sha256(payload).hexdigest()[:16]


def _timestamp(
    raw: str, file_date: str, explicit_precision: str | None
) -> tuple[str | None, str, str, list[str]]:
    diagnostics: list[str] = []
    value = raw.strip()
    inferred = "unknown"
    sortable: str | None = None
    if value.casefold() == "unknown":
        inferred = "unknown"
    elif DATE_RE.fullmatch(value):
        try:
            date.fromisoformat(value)
            inferred, sortable = "date", value
        except ValueError:
            diagnostics.append("invalid-date")
    elif TIME_RE.fullmatch(value):
        try:
            datetime.strptime(value, "%H:%M:%S" if value.count(":") == 2 else "%H:%M")
            inferred = "minute"
            sortable = f"{file_date}T{value}" if DATE_RE.fullmatch(file_date) else None
            if explicit_precision is None:
                diagnostics.append("legacy-time")
        except ValueError:
            diagnostics.append("invalid-time")
    else:
        normalized = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
        try:
            parsed = datetime.fromisoformat(normalized)
            sortable = parsed.isoformat()
            if parsed.tzinfo is not None and parsed.utcoffset() is not None:
                inferred = "exact"
            else:
                inferred = "minute"
                diagnostics.append("timezone-missing")
        except ValueError:
            diagnostics.append("invalid-timestamp")
    precision = explicit_precision or inferred
    if precision not in PRECISIONS:
        diagnostics.append("invalid-precision")
        precision = inferred
    if precision == "exact" and inferred != "exact":
        diagnostics.append("unsupported-exact-precision")
        precision = inferred
    return sortable, precision, value, diagnostics


def _parse_block(
    path: Path,
    lineno: int,
    block: str,
    header: dict[str, str],
) -> dict[str, Any]:
    diagnostics: list[str] = []
    match = ENTRY_RE.match(block)
    metadata: dict[str, str] = {}
    timestamp_raw = "unknown"
    text = block[2:].strip()
    kind = "raw"
    if match:
        timestamp_raw = match.group("timestamp").strip()
        metadata = {
            key: " ".join(value.split())
            for key, value in META_RE.findall(match.group("meta"))
        }
        raw_text = match.group("text").strip()
        quoted = len(raw_text) >= 2 and raw_text[0] == raw_text[-1] == '"'
        text = raw_text[1:-1] if quoted else raw_text
        kind = metadata.get("kind", "quote" if quoted else "note")
        if kind not in KINDS - {"raw"}:
            diagnostics.append("invalid-kind")
            kind = "note"
    else:
        diagnostics.append("unrecognized-format")

    type_raw = metadata.get("type", "")
    type_value = type_raw if type_raw in TYPES else REPAIR_TYPE
    if type_raw not in TYPES:
        diagnostics.append("missing-type" if not type_raw else "invalid-type")
    topic_raw = metadata.get("topic", "").strip()
    topic = topic_raw if topic_raw in TOPICS else REPAIR_TOPIC
    if topic_raw not in TOPICS:
        diagnostics.append("missing-topic" if not topic_raw else "invalid-topic")

    sortable, precision, timestamp_raw, timestamp_diagnostics = _timestamp(
        timestamp_raw,
        header.get("date", ""),
        metadata.get("precision"),
    )
    diagnostics.extend(timestamp_diagnostics)
    source = metadata.get("source")
    if not source:
        source = "transcript" if precision == "exact" else "legacy"
    if precision != "exact" and "precision" not in metadata:
        diagnostics.append("unmarked-approximate")

    session = header.get("session", "unknown")
    return {
        "record_id": _record_id(session, kind, text),
        "kind": kind,
        "text": text,
        "quote": text,
        "timestamp": timestamp_raw,
        "sort_timestamp": sortable,
        "date": sortable[:10] if sortable else None,
        "source": source,
        "precision": precision,
        "source_ref": metadata.get("source-ref"),
        "type": type_value,
        "type_raw": type_raw or None,
        "topic": topic,
        "topic_raw": topic_raw if topic_raw != topic else None,
        "session": session,
        "agent": header.get("agent", "unknown"),
        "model": header.get("model"),
        "project": header.get("project"),
        "file": path.name,
        "line": lineno,
        "address": f"{path.name}:{lineno}",
        "raw": block,
        "diagnostics": sorted(set(diagnostics)),
    }


def load(corpus: Path) -> tuple[list[dict[str, Any]], int]:
    """Return one record per Markdown star block; second value is diagnostic count."""
    records: list[dict[str, Any]] = []
    for path in sorted(corpus.glob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError as error:
            raise CliError(f"не удалось прочитать {path}: {error}") from error
        header = _frontmatter(lines)
        for lineno, block in _star_blocks(lines):
            records.append(_parse_block(path, lineno, block, header))
    session_holders: dict[str, set[str]] = defaultdict(set)
    id_counts: Counter[str] = Counter()
    for record in records:
        if record["session"] != "unknown":
            session_holders[record["session"]].add(record["file"])
        id_counts[record["record_id"]] += 1
    for record in records:
        diagnostics = set(record["diagnostics"])
        if len(session_holders[record["session"]]) > 1:
            diagnostics.add("duplicate-session-holder")
        if id_counts[record["record_id"]] > 1:
            diagnostics.add("duplicate-record-id")
        record["diagnostics"] = sorted(diagnostics)
    return records, sum(bool(record["diagnostics"]) for record in records)


def inventory(records: list[dict[str, Any]], diagnostic_count: int) -> str:
    topics: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"n": 0, "types": Counter(), "dates": []}
    )
    type_totals: Counter[str] = Counter()
    for record in records:
        entry = topics[record["topic"]]
        entry["n"] += 1
        entry["types"][record["type"]] += 1
        if record["date"]:
            entry["dates"].append(record["date"])
        type_totals[record["type"]] += 1
    lines: list[str] = []
    for name, entry in sorted(topics.items(), key=lambda item: (-item[1]["n"], item[0])):
        dates = entry["dates"]
        period = f"{min(dates)}…{max(dates)}" if dates else "дата неизвестна"
        mix = " ".join(f"{key}:{count}" for key, count in entry["types"].most_common())
        lines.append(f'{entry["n"]:4d}  {name:22s} {period}  {mix}')
    totals = " ".join(f"{key}:{count}" for key, count in type_totals.most_common())
    lines.append(f"---- всего {len(records)} записей / {len(topics)} topics; {totals}")
    if diagnostic_count:
        lines.append(
            f"---- REPAIR: {diagnostic_count} записей имеют diagnostics; "
            "запустите --check"
        )
    return "\n".join(lines)


def _fts_query(query: str) -> str:
    tokens = QUERY_TOKEN_RE.findall(query.casefold())
    if not tokens:
        raise CliError("query не содержит поисковых терминов")
    return " OR ".join(f'"{token[:-1]}"*' if token.endswith("*") else f'"{token}"' for token in tokens)


def search_bm25(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE recall USING fts5(text, topic, tokenize='unicode61')"
        )
        connection.executemany(
            "INSERT INTO recall(rowid, text, topic) VALUES (?, ?, ?)",
            (
                (
                    index,
                    record["text"],
                    " ".join(
                        value
                        for value in (record["topic"], record["topic_raw"])
                        if value
                    ),
                )
                for index, record in enumerate(records, 1)
            ),
        )
        rows = connection.execute(
            "SELECT rowid, bm25(recall, 1.0, 0.25) AS score "
            "FROM recall WHERE recall MATCH ? ORDER BY score, rowid",
            (_fts_query(query),),
        ).fetchall()
    except sqlite3.Error as error:
        raise CliError(f"BM25 query недопустим: {error}") from error
    finally:
        connection.close()
    result: list[dict[str, Any]] = []
    for rowid, score in rows:
        record = dict(records[rowid - 1])
        record["score"] = score
        result.append(record)
    return result


def _validate_date(value: str, name: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise CliError(f"{name}: ожидается YYYY-MM-DD") from error


def _filter(records: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    result = records
    if args.types:
        wanted = {value.strip() for value in args.types.split(",") if value.strip()}
        result = [record for record in result if record["type"] in wanted]
    if args.topics:
        wanted = {value.strip() for value in args.topics.split(",") if value.strip()}
        result = [record for record in result if record["topic"] in wanted]
    if args.agent:
        result = [record for record in result if record["agent"] == args.agent]
    if args.session:
        result = [record for record in result if record["session"] == args.session]
    if args.grep:
        try:
            pattern = re.compile(args.grep, re.IGNORECASE)
        except re.error as error:
            raise CliError(f"grep regex недопустим: {error}") from error
        result = [record for record in result if pattern.search(record["text"])]
    if args.since:
        since = _validate_date(args.since, "--since")
        result = [record for record in result if record["date"] and record["date"] >= since]
    if args.until:
        until = _validate_date(args.until, "--until")
        result = [record for record in result if record["date"] and record["date"] <= until]
    return result


def _quality(records: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "exact": sum(record["precision"] == "exact" for record in records),
        "approximate": sum(record["precision"] in {"minute", "date"} for record in records),
        "unknown": sum(record["precision"] == "unknown" for record in records),
        "with_diagnostics": sum(bool(record["diagnostics"]) for record in records),
        "raw": sum(record["kind"] == "raw" for record in records),
    }


def _summary(record: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "record_id",
        "kind",
        "text",
        "timestamp",
        "source",
        "precision",
        "source_ref",
        "type",
        "topic",
        "topic_raw",
        "session",
        "agent",
        "address",
        "diagnostics",
        "score",
    )
    return {field: record[field] for field in fields if field in record}


def _validate_bounds(limit: int, max_chars: int) -> None:
    if limit < 1:
        raise CliError("--limit должен быть положительным")
    if max_chars < 512:
        raise CliError("--max-chars должен быть не меньше 512")


def _bounded(
    records: list[dict[str, Any]], limit: int, max_chars: int
) -> tuple[list[dict[str, Any]], str | None]:
    _validate_bounds(limit, max_chars)
    result: list[dict[str, Any]] = []
    used = 0
    truncated_by: str | None = None
    for record in records[:limit]:
        estimate = len(json.dumps(_summary(record), ensure_ascii=False))
        if result and used + estimate > max_chars:
            truncated_by = "max_chars"
            break
        if not result and estimate > max_chars:
            clipped = dict(record)
            clipped["text"] = clipped["text"][: max(40, max_chars // 2)] + "…"
            clipped["quote"] = clipped["text"]
            clipped["raw"] = clipped["raw"][: max(40, max_chars // 3)] + "…"
            result.append(clipped)
            truncated_by = "max_chars"
            break
        result.append(record)
        used += estimate
    if truncated_by is None and len(result) < len(records):
        truncated_by = "limit"
    return result, truncated_by


def _digest(records: list[dict[str, Any]], head: int, *, verbose: bool) -> str:
    if head < 1:
        raise CliError("--head должен быть положительным")
    lines: list[str] = []
    for record in records:
        clipped = record["text"][:head] + ("…" if len(record["text"]) > head else "")
        score = f" score={record['score']:.4f}" if verbose and "score" in record else ""
        diagnostics = " !diagnostics" if record["diagnostics"] else ""
        lines.append(
            f"{record['record_id']} {record['date'] or 'unknown'} "
            f"{record['precision']} {record['kind']} "
            f"{record['type']}/{record['topic']}{diagnostics}{score} · {clipped}"
        )
    return "\n".join(lines)


def _show(record: dict[str, Any]) -> str:
    source = (
        f"timestamp={record['timestamp']} · precision={record['precision']} · "
        f"source={record['source']}"
    )
    if record["source_ref"]:
        source += f" · source_ref={record['source_ref']}"
    owner = (
        f"address={record['address']} · session={record['session']} · "
        f"agent={record['agent']}"
    )
    if record["project"]:
        owner += f" · project={record['project']}"
    if record["model"]:
        owner += f" · model={record['model']}"
    classification = (
        f"record={record['record_id']} · kind={record['kind']} · "
        f"type={record['type']} · topic={record['topic']}"
    )
    if record["type_raw"] and record["type_raw"] != record["type"]:
        classification += f" · type_raw={record['type_raw']}"
    if record["topic_raw"] and record["topic_raw"] != record["topic"]:
        classification += f" · topic_raw={record['topic_raw']}"
    diagnostics = ",".join(record["diagnostics"]) or "none"
    return "\n".join(
        (
            record["text"],
            classification,
            source,
            owner,
            f"diagnostics={diagnostics}",
        )
    )


def _check_report(records: list[dict[str, Any]], total: int, max_chars: int) -> str:
    issues = [record for record in records if record["diagnostics"]]
    if not issues:
        return f"OK: {total} записей без diagnostics"

    issue_lines = [
        f"{record['address']} {record['record_id']}: {','.join(record['diagnostics'])}"
        for record in issues
    ]
    visible: list[str] = []
    for line in issue_lines:
        candidate_count = len(visible) + 1
        candidate_summary = (
            f"{candidate_count}/{len(issues)} records with diagnostics shown · "
            f"{total} records · truncated"
        )
        candidate = "\n".join((candidate_summary, *visible, line))
        if len(candidate) > max_chars:
            break
        visible.append(line)

    truncated = len(visible) < len(issue_lines)
    summary = (
        f"{len(visible)}/{len(issues)} records with diagnostics shown · "
        f"{total} records · truncated"
        if truncated
        else f"{len(issues)} records with diagnostics · {total} records"
    )
    return "\n".join((summary, *visible))


def _result_status(
    returned: int, matched: int, total: int, truncated_by: str | None
) -> str:
    status = f"{returned}/{matched} matches shown · {total} records"
    if truncated_by == "limit":
        return f"{status} · truncated by --limit"
    if truncated_by == "max_chars":
        return f"{status} · truncated by --max-chars"
    return status


def _render_digest(
    records: list[dict[str, Any]],
    *,
    head: int,
    verbose: bool,
    matched: int,
    total: int,
    truncated_by: str | None,
) -> str:
    digest = _digest(records, head, verbose=verbose)
    lines = [_result_status(len(records), matched, total, truncated_by)]
    lines.append(digest or "selection=none")
    return "\n".join(lines)


def _bounded_digest(
    records: list[dict[str, Any]],
    *,
    limit: int,
    max_chars: int,
    head: int,
    verbose: bool,
    total: int,
) -> tuple[list[dict[str, Any]], str | None]:
    _validate_bounds(limit, max_chars)
    _digest([], head, verbose=verbose)
    selected: list[dict[str, Any]] = []
    truncated_by: str | None = None
    for record in records[:limit]:
        candidate = [*selected, record]
        rendered = _render_digest(
            candidate,
            head=head,
            verbose=verbose,
            matched=len(records),
            total=total,
            truncated_by=("max_chars" if len(candidate) < len(records) else None),
        )
        if len(rendered) > max_chars:
            truncated_by = "max_chars"
            break
        selected = candidate
    if records and not selected:
        raise CliError(
            "первая запись не помещается в --max-chars; "
            "уменьшите --head или увеличьте --max-chars"
        )
    if truncated_by is None and len(selected) < len(records):
        truncated_by = "limit"
    return selected, truncated_by


def _timeline(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dated = sorted(
        (
            record
            for record in records
            if record["sort_timestamp"] and record["precision"] != "unknown"
        ),
        key=lambda record: (
            record["sort_timestamp"],
            record["file"],
            record["line"],
        ),
        reverse=True,
    )
    uncertain = [
        record for record in records
        if not record["sort_timestamp"] or record["precision"] == "unknown"
    ]
    return dated + sorted(
        uncertain,
        key=lambda record: (record["file"], record["line"]),
        reverse=True,
    )


def _warnings(records: list[dict[str, Any]]) -> list[str]:
    warnings: list[str] = []
    if any(record["diagnostics"] for record in records):
        warnings.append("repair-backlog-present")
    if any(record["precision"] != "exact" for record in records):
        warnings.append("approximate-or-unknown-time-present")
    return warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--digest", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--query")
    parser.add_argument("--show")
    parser.add_argument("--timeline", action="store_true")
    parser.add_argument("--type", dest="types")
    parser.add_argument("--topic", dest="topics")
    parser.add_argument("--grep")
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--agent")
    parser.add_argument("--session")
    parser.add_argument(
        "--head",
        type=int,
        default=110,
        help="human-readable excerpt length; ignored with --json",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="maximum records to return before the --max-chars budget",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=8000,
        help="hard output cap; may return fewer records than --limit",
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        if args.strict and not args.check:
            raise CliError("--strict используется только вместе с --check")
        if not args.corpus.is_dir():
            raise CliError(f"нет папки: {args.corpus}")
        if not args.show:
            _validate_bounds(args.limit, args.max_chars)
        records, diagnostic_count = load(args.corpus)
        total = len(records)
        inventory_mode = not any(
            (
                args.digest,
                args.query,
                args.timeline,
                args.types,
                args.topics,
                args.grep,
                args.since,
                args.until,
                args.agent,
                args.session,
            )
        )

        if args.show:
            matches = [record for record in records if record["record_id"] == args.show]
            if not matches:
                raise CliError(f"record_id не найден: {args.show}")
            if len(matches) > 1:
                addresses = ", ".join(record["address"] for record in matches)
                raise CliError(
                    f"record_id неоднозначен ({addresses}); сначала почините duplicate"
                )
            selected, truncated_by = matches, None
            matched = len(selected)
        else:
            candidates = search_bm25(records, args.query) if args.query else list(records)
            candidates = _filter(candidates, args)
            if args.timeline:
                candidates = _timeline(candidates)
            matched = len(candidates)
            if args.json:
                selected, truncated_by = _bounded(
                    candidates, args.limit, args.max_chars
                )
            elif args.check or inventory_mode:
                selected, truncated_by = candidates, None
            else:
                selected, truncated_by = _bounded_digest(
                    candidates,
                    limit=args.limit,
                    max_chars=args.max_chars,
                    head=args.head,
                    verbose=args.verbose,
                    total=total,
                )
        envelope = {
            "total": total,
            "matched": matched,
            "returned": len(selected),
            "truncated": truncated_by is not None,
            "truncated_by": truncated_by,
            "selection": "none" if matched == 0 else "records",
            "quality": _quality(records),
            "warnings": _warnings(records),
            "records": selected if args.show else [_summary(record) for record in selected],
        }
        if args.timeline:
            envelope["order"] = "newest-first"

        if args.json:
            rendered = json.dumps(
                envelope, ensure_ascii=False, separators=(",", ":")
            )
            if args.show and len(rendered) > args.max_chars:
                raise CliError(
                    "полная запись превышает --max-chars; увеличьте лимит для --show"
                )
            while (
                not args.show
                and len(rendered) > args.max_chars
                and envelope["records"]
            ):
                envelope["records"].pop()
                envelope["returned"] = len(envelope["records"])
                envelope["truncated"] = True
                envelope["truncated_by"] = "max_chars"
                rendered = json.dumps(
                    envelope, ensure_ascii=False, separators=(",", ":")
                )
            if len(rendered) > args.max_chars:
                raise CliError(
                    "--max-chars слишком мал для обязательного JSON envelope"
                )
            print(rendered)
        elif args.check:
            print(_check_report(records, total, args.max_chars))
        elif args.show:
            rendered = (
                json.dumps(selected[0], ensure_ascii=False, indent=2)
                if args.verbose
                else _show(selected[0])
            )
            if len(rendered) > args.max_chars:
                raise CliError(
                    "полная запись превышает --max-chars; увеличьте лимит для --show"
                )
            print(rendered)
        elif inventory_mode:
            print(inventory(records, diagnostic_count))
        else:
            print(
                _render_digest(
                    selected,
                    head=args.head,
                    verbose=args.verbose,
                    matched=matched,
                    total=total,
                    truncated_by=truncated_by,
                )
            )
        if args.check and args.strict and diagnostic_count:
            return 1
        return 0
    except CliError as error:
        print(f"chat-digest: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
