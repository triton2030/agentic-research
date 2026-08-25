#!/usr/bin/env python3
"""Stable identities shared by live chat-recall batch tools."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SESSION = re.compile(r"^session:\s*(\S+)\s*$")
SHA256 = re.compile(r"[0-9a-f]{64}")

RecordIdentity = tuple[str, str]


def session_from_lines(lines: list[str]) -> str | None:
    for line in lines:
        match = SESSION.fullmatch(line)
        if match:
            return match.group(1)
    return None


def record_sha256(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def record_identity(session: str | None, line: str) -> RecordIdentity | None:
    if session is None:
        return None
    return session, record_sha256(line)


def load_noop_identities(path: str | Path) -> set[RecordIdentity]:
    ledger = Path(path)
    if not ledger.exists():
        return set()
    payload = json.loads(ledger.read_text(encoding="utf-8-sig"))
    if payload.get("version") != 1 or not isinstance(payload.get("records"), list):
        raise ValueError(f"invalid no-op ledger: {ledger}")

    identities: set[RecordIdentity] = set()
    for record in payload["records"]:
        if not isinstance(record, dict):
            raise ValueError(f"invalid no-op ledger record: {ledger}")
        session = record.get("session")
        fingerprint = record.get("record_sha256")
        if not isinstance(session, str) or not isinstance(fingerprint, str):
            raise ValueError(f"invalid no-op ledger record: {ledger}")
        if SHA256.fullmatch(fingerprint) is None:
            raise ValueError(f"invalid no-op record fingerprint: {ledger}")
        identities.add((session, fingerprint))
    return identities
