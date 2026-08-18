"""Read exact owner quotes without turning Graphiti facts into source truth."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

ENTRY_RE = re.compile(
    r'^\*\s+(?P<timestamp>.+?)\s+—\s+"(?P<text>.*)"\s+—\s+(?P<meta>.+)$'
)
KIND_RE = re.compile(r"(?:^|\|\s*)kind:\s*(?P<kind>[\w-]+)")
FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True, slots=True)
class SourceQuote:
    """One verbatim quote plus the address and time that make it evidence."""

    text: str
    timestamp: datetime
    address: str
    session: str
    uuid: str

    @property
    def name(self) -> str:
        # Graphiti 0.29 treats add_episode(uuid=...) as reprocessing an existing
        # episode, not creating one. Keep our deterministic source identity in
        # the episode name and let Graphiti own its internal UUID.
        return f"quote:{self.uuid}"


def _frontmatter_value(markdown: str, key: str) -> str | None:
    match = FRONTMATTER_RE.match(markdown)
    if not match:
        return None
    prefix = f"{key}:"
    for line in match.group("body").splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip('"')
    return None


def _exact_timestamp(raw: str, address: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{address}: quote timestamp is not exact ISO-8601") from error
    if timestamp.tzinfo is None or "T" not in raw:
        raise ValueError(f"{address}: quote timestamp must include time and timezone")
    return timestamp


def read_quotes(path: Path, *, root: Path) -> list[SourceQuote]:
    markdown = path.read_text(encoding="utf-8")
    session = _frontmatter_value(markdown, "session") or "unknown-session"
    try:
        relative_path = path.resolve().relative_to(root.resolve())
    except ValueError:
        relative_path = path.resolve()

    quotes: list[SourceQuote] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        match = ENTRY_RE.match(line)
        if not match:
            continue
        kind_match = KIND_RE.search(match.group("meta"))
        if kind_match and kind_match.group("kind") != "quote":
            continue
        address = f"{relative_path}:{line_number}"
        timestamp = _exact_timestamp(match.group("timestamp"), address)
        text = match.group("text")
        identity = f"{session}|{timestamp.isoformat()}|{sha256(text.encode()).hexdigest()}"
        quotes.append(
            SourceQuote(
                text=text,
                timestamp=timestamp,
                address=address,
                session=session,
                uuid=str(uuid5(NAMESPACE_URL, identity)),
            )
        )
    return quotes


def load_quotes(paths: list[Path], *, root: Path, limit: int | None = None) -> list[SourceQuote]:
    quotes: list[SourceQuote] = []
    for path in paths:
        quotes.extend(read_quotes(path, root=root))
    quotes.sort(key=lambda quote: quote.timestamp)
    return quotes if limit is None else quotes[:limit]
