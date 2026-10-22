"""Stable Markdown record identities and the cooperating-writer corpus lock."""
from contextlib import contextmanager
import fcntl
import hashlib
from pathlib import Path
import re

HEADING_RE = re.compile(r"^### (recall-[0-9a-f]{32})$")
ADDRESS_RE = re.compile(r"^(?P<file>[^/\\]+\.md)(?:#(?P<id>recall-[0-9a-f]{32})|(?:#L|:)(?P<line>[1-9][0-9]*))(?: sha:(?P<sha>[0-9a-f]{8,64}))?$")


@contextmanager
def corpus_lock(log_dir: Path):
    """Serialize capture/repair snapshots, topic updates, writes and rollback.

    Lock the persistent sidecar, never a holder inode replaced by atomic writes.
    Manual editors and older helpers must be stopped before a repair operation.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / ".capture.lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def record_blocks(lines):
    """Read star blocks and their optional immediately preceding identity heading."""
    starts = [i for i, line in enumerate(lines) if line.startswith("* ")]
    for ordinal, start in enumerate(starts):
        end = starts[ordinal + 1] if ordinal + 1 < len(starts) else len(lines)
        block = lines[start:end]
        while block and (not block[-1].strip() or block[-1].startswith("#")):
            block.pop()
        before = start - 1
        while before >= 0 and not lines[before].strip():
            before -= 1
        match = HEADING_RE.fullmatch(lines[before]) if before >= 0 else None
        yield start + 1, "\n".join(block).strip(), match[1] if match else None


def record_hash(raw):
    # Historical relation fingerprints hashed the first record line.
    return hashlib.sha256(raw.split("\n", 1)[0].encode("utf-8")).hexdigest()


def resolve_record(log_dir: Path, address: str):
    """Resolve identity only; a bare line is a location hint, never evidence."""
    match = ADDRESS_RE.fullmatch(address)
    if not match or match["file"] in (".", ".."):
        raise ValueError("address must be <file>.md#recall-<id> or <file>.md:<line> sha:<verified-hash>")
    if not match["id"] and not match["sha"]:
        raise ValueError("unverified line address: supply the record's previously verified sha or stable heading")
    path = log_dir / match["file"]
    if path.resolve().parent != log_dir.resolve():
        raise ValueError("address points outside corpus")
    rows = list(record_blocks(path.read_text(encoding="utf-8-sig").splitlines()))
    candidates = [row for row in rows if (row[2] == match["id"] if match["id"] else record_hash(row[1]).startswith(match["sha"]))]
    if len(candidates) != 1:
        raise ValueError(f"record identity resolved to {len(candidates)} records in {path.name}; repair from source evidence")
    number, raw, identity = candidates[0]
    if match["sha"] and not record_hash(raw).startswith(match["sha"]):
        raise ValueError("stable heading and verified hash disagree")
    return path, number, raw, identity
