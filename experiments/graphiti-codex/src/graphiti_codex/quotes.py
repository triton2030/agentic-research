"""Read source-bound quote records from explicitly supplied holders."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo

ENTRY_RE = re.compile(
    r'^\*\s+(?P<timestamp>.+?)\s+—\s+"(?P<text>.*)"\s+—\s+(?P<meta>.+)$'
)
METADATA_FIELD_RE = re.compile(
    r"(?:^|\|\s*)(?P<key>[\w-]+):\s*(?P<value>.*?)(?=\s+\|\s+[\w-]+:\s*|$)"
)
FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)
HOLDER_TIME_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})-(?P<clock>\d{6})-")
CORPUS_TIMEZONE = ZoneInfo("Asia/Almaty")


@dataclass(frozen=True, slots=True)
class SourceQuote:
    """One quote plus the source address and Graphiti reference time."""

    text: str
    timestamp: datetime
    address: str
    session: str
    uuid: str
    context_note: str | None = None
    timestamp_precision: str = "exact"

    @property
    def name(self) -> str:
        return f"quote:{self.uuid}"


@dataclass(frozen=True, slots=True)
class ReadDiagnostic:
    """A malformed record rejected while reading an explicit holder."""

    address: str
    reason: str


@dataclass(frozen=True, slots=True)
class _PendingQuote:
    text: str
    timestamp: datetime | None
    coarse_date: date | None
    address: str
    session: str
    context_note: str | None
    holder_index: int
    line_number: int


def _frontmatter_value(markdown: str, key: str) -> str | None:
    match = FRONTMATTER_RE.match(markdown)
    if not match:
        return None
    prefix = f"{key}:"
    for line in match.group("body").splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"')
    return None


def _relative_path(path: Path, root: Path) -> str:
    try:
        relative_path = path.resolve().relative_to(root.resolve())
    except ValueError:
        relative_path = path.resolve()
    return relative_path.as_posix()


def _source_timestamp(raw: str, address: str) -> tuple[datetime | None, date | None]:
    if "T" not in raw:
        try:
            return None, date.fromisoformat(raw)
        except ValueError as error:
            raise ValueError(f"{address}: quote timestamp is not ISO-8601") from error
    try:
        timestamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{address}: quote timestamp is not ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError(f"{address}: quote timestamp with time must include timezone")
    return timestamp, None


def _quote_identity(session: str, address: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{session}|{address}"))


def _metadata_fields(raw: str) -> dict[str, str]:
    return {
        match.group("key"): match.group("value").strip()
        for match in METADATA_FIELD_RE.finditer(raw)
    }


def _holder_timestamp(path: Path) -> datetime | None:
    match = HOLDER_TIME_RE.match(path.name)
    if match is None or match.group("clock") == "000000":
        return None
    return datetime.strptime(
        f"{match.group('day')} {match.group('clock')}",
        "%Y-%m-%d %H%M%S",
    ).replace(tzinfo=CORPUS_TIMEZONE)


def _read_holder(
    path: Path,
    *,
    root: Path,
    holder_index: int,
    strict: bool,
) -> tuple[list[_PendingQuote], list[ReadDiagnostic]]:
    markdown = path.read_text(encoding="utf-8")
    relative_path = _relative_path(path, root)
    session = _frontmatter_value(markdown, "session") or "unknown-session"
    quotes: list[_PendingQuote] = []
    diagnostics: list[ReadDiagnostic] = []

    for line_number, line in enumerate(markdown.splitlines(), start=1):
        match = ENTRY_RE.match(line)
        if not match:
            continue
        metadata = _metadata_fields(match.group("meta"))
        kind = metadata.get("kind")
        if kind and kind != "quote":
            continue
        address = f"{relative_path}:{line_number}"
        try:
            timestamp, coarse_date = _source_timestamp(match.group("timestamp"), address)
        except ValueError as error:
            if strict:
                raise
            diagnostics.append(ReadDiagnostic(address=address, reason=str(error)))
            continue
        quotes.append(
            _PendingQuote(
                text=match.group("text"),
                timestamp=timestamp,
                coarse_date=coarse_date,
                address=address,
                session=session,
                context_note=metadata.get("context-note"),
                holder_index=holder_index,
                line_number=line_number,
            )
        )

    return quotes, diagnostics


def _interpolation_bounds(
    day: date,
    holder_index: int,
    anchors: list[tuple[int, datetime]],
) -> tuple[datetime, datetime, int | None, int | None]:
    day_start = datetime.combine(day, time.min, tzinfo=CORPUS_TIMEZONE)
    day_end = day_start + timedelta(days=1)
    previous = next((item for item in reversed(anchors) if item[0] < holder_index), None)
    following = next((item for item in anchors if item[0] > holder_index), None)
    lower = max(day_start, previous[1]) if previous else day_start
    upper = min(day_end, following[1]) if following else day_end
    if lower >= upper:
        lower, upper = day_start, day_end
    return lower, upper, previous[0] if previous else None, following[0] if following else None


def _resolve_quotes(
    pending: list[_PendingQuote],
    paths: list[Path],
    *,
    record_ids: set[str] | None,
) -> list[SourceQuote]:
    anchors = [
        (holder_index, timestamp)
        for holder_index, path in enumerate(paths)
        if (timestamp := _holder_timestamp(path)) is not None
    ]
    groups: dict[
        tuple[date, datetime, datetime, int | None, int | None], list[_PendingQuote]
    ] = {}
    for quote in pending:
        if quote.coarse_date is None:
            continue
        lower, upper, previous_index, following_index = _interpolation_bounds(
            quote.coarse_date,
            quote.holder_index,
            anchors,
        )
        key = (quote.coarse_date, lower, upper, previous_index, following_index)
        groups.setdefault(key, []).append(quote)

    interpolated: dict[str, datetime] = {}
    for (_day, lower, upper, _previous, _following), group in groups.items():
        ordered = sorted(group, key=lambda item: (item.holder_index, item.line_number))
        step = (upper - lower) / (len(ordered) + 1)
        for position, quote in enumerate(ordered, start=1):
            interpolated[quote.address] = lower + step * position

    resolved: list[tuple[SourceQuote, int, int]] = []
    for quote in pending:
        timestamp = quote.timestamp or interpolated[quote.address]
        precision = "exact" if quote.timestamp is not None else "interpolated"
        source_quote = SourceQuote(
            text=quote.text,
            timestamp=timestamp,
            address=quote.address,
            session=quote.session,
            uuid=_quote_identity(quote.session, quote.address),
            context_note=quote.context_note,
            timestamp_precision=precision,
        )
        if record_ids is None or source_quote.uuid in record_ids or source_quote.name in record_ids:
            resolved.append((source_quote, quote.holder_index, quote.line_number))

    resolved.sort(key=lambda item: (item[0].timestamp, item[1], item[2]))
    return [item[0] for item in resolved]


def read_holder(
    path: Path,
    *,
    root: Path,
    record_ids: set[str] | None = None,
    strict: bool = True,
) -> tuple[list[SourceQuote], list[ReadDiagnostic]]:
    """Read one holder; date-only records are ordered inside their calendar day."""

    resolved_path = path.resolve()
    pending, diagnostics = _read_holder(
        resolved_path,
        root=root,
        holder_index=0,
        strict=strict,
    )
    return _resolve_quotes(pending, [resolved_path], record_ids=record_ids), diagnostics


def read_quotes(
    path: Path,
    *,
    root: Path,
    record_ids: set[str] | None = None,
) -> list[SourceQuote]:
    """Read one holder strictly, including deterministically ordered date-only records."""

    quotes, _diagnostics = read_holder(path, root=root, record_ids=record_ids, strict=True)
    return quotes


def load_quotes(
    paths: list[Path],
    *,
    root: Path,
    limit: int | None = None,
    record_ids: set[str] | None = None,
    strict: bool = True,
) -> tuple[list[SourceQuote], list[ReadDiagnostic]]:
    """Read holders in chronology and interpolate date-only records between sessions."""

    ordered_paths = sorted(paths, key=lambda item: _relative_path(item, root))
    pending: list[_PendingQuote] = []
    diagnostics: list[ReadDiagnostic] = []
    for holder_index, path in enumerate(ordered_paths):
        holder_quotes, holder_diagnostics = _read_holder(
            path,
            root=root,
            holder_index=holder_index,
            strict=strict,
        )
        pending.extend(holder_quotes)
        diagnostics.extend(holder_diagnostics)
    quotes = _resolve_quotes(pending, ordered_paths, record_ids=record_ids)
    if limit is not None:
        quotes = quotes[:limit]
    return quotes, diagnostics
