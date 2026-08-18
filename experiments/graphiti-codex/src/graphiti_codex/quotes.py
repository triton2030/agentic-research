"""Read exact source-bound quote records from explicitly supplied holders."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ENTRY_RE = re.compile(
    r'^\*\s+(?P<timestamp>.+?)\s+—\s+"(?P<text>.*)"\s+—\s+(?P<meta>.+)$'
)
METADATA_FIELD_RE = re.compile(
    r"(?:^|\|\s*)(?P<key>[\w-]+):\s*(?P<value>.*?)(?=\s+\|\s+[\w-]+:\s*|$)"
)
FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True, slots=True)
class SourceQuote:
    """One exact quote plus the address and timestamp required by Graphiti."""

    text: str
    timestamp: datetime
    address: str
    session: str
    uuid: str
    context_note: str | None = None

    @property
    def name(self) -> str:
        # Graphiti owns the internal episode UUID. This stable source identity
        # is placed in episode.name for idempotent re-ingest.
        return f"quote:{self.uuid}"


@dataclass(frozen=True, slots=True)
class ReadDiagnostic:
    """A non-exact record rejected while reading an explicit holder."""

    address: str
    reason: str


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


def _exact_timestamp(raw: str, address: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{address}: quote timestamp is not exact ISO-8601") from error
    if timestamp.tzinfo is None or "T" not in raw:
        raise ValueError(f"{address}: quote timestamp must include time and timezone")
    return timestamp


def _quote_identity(session: str, timestamp: datetime, address: str) -> str:
    identity = f"{session}|{timestamp.isoformat()}|{address}"
    return str(uuid5(NAMESPACE_URL, identity))


def _metadata_fields(raw: str) -> dict[str, str]:
    return {
        match.group("key"): match.group("value").strip()
        for match in METADATA_FIELD_RE.finditer(raw)
    }


def _read_holder(
    path: Path,
    *,
    root: Path,
    record_ids: set[str] | None = None,
    strict: bool = True,
) -> tuple[list[SourceQuote], list[ReadDiagnostic]]:
    markdown = path.read_text(encoding="utf-8")
    relative_path = _relative_path(path, root)
    session = _frontmatter_value(markdown, "session") or "unknown-session"
    quotes: list[SourceQuote] = []
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
            timestamp = _exact_timestamp(match.group("timestamp"), address)
        except ValueError as error:
            if strict:
                raise
            diagnostics.append(ReadDiagnostic(address=address, reason=str(error)))
            continue
        quote = SourceQuote(
            text=match.group("text"),
            timestamp=timestamp,
            address=address,
            session=session,
            uuid=_quote_identity(session, timestamp, address),
            context_note=metadata.get("context-note"),
        )
        if record_ids is None or quote.uuid in record_ids or quote.name in record_ids:
            quotes.append(quote)

    quotes.sort(key=lambda quote: quote.timestamp)
    return quotes, diagnostics


def read_holder(
    path: Path,
    *,
    root: Path,
    record_ids: set[str] | None = None,
    strict: bool = True,
) -> tuple[list[SourceQuote], list[ReadDiagnostic]]:
    """Read one explicitly supplied holder and optional stable record IDs."""

    return _read_holder(path, root=root, record_ids=record_ids, strict=strict)


def read_quotes(
    path: Path,
    *,
    root: Path,
    record_ids: set[str] | None = None,
) -> list[SourceQuote]:
    """Read one holder strictly, accepting only exact timestamps and quote records."""

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
    """Read explicitly supplied holders in timestamp order."""

    quotes: list[SourceQuote] = []
    diagnostics: list[ReadDiagnostic] = []
    for path in sorted(paths, key=lambda item: _relative_path(item, root)):
        holder_quotes, holder_diagnostics = read_holder(
            path,
            root=root,
            record_ids=record_ids,
            strict=strict,
        )
        quotes.extend(holder_quotes)
        diagnostics.extend(holder_diagnostics)
    quotes.sort(key=lambda quote: quote.timestamp)
    if limit is not None:
        quotes = quotes[:limit]
    return quotes, diagnostics
