#!/usr/bin/env python3
"""Build the next deterministic ten-holder chronological Wiki input."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections import defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


class BatchBuildError(ValueError):
    """Raised when the frozen inputs cannot prove one exact next batch."""


MANIFEST_SCHEMA = "openviking-chat-recall/chronological-batch-input.v3"
SOURCE_MANIFEST_SCHEMA = "openviking-chat-recall/source-manifest.v1"
SOURCE_LOCK_SCHEMA = "openviking-chat-recall/source-lock.v1"
RECORD_SCHEMA = "openviking-chat-recall/evidence-record.v1"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BATCH_SIZE = 10
NAIVE_TIMEZONE = ZoneInfo("Asia/Almaty")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise BatchBuildError(f"{label} is not a regular file: {path}")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BatchBuildError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise BatchBuildError(f"{label} must contain a JSON object")
    return value, raw


def _read_records(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    if path.is_symlink() or not path.is_file():
        raise BatchBuildError(f"evidence records is not a regular file: {path}")
    raw = path.read_bytes()
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BatchBuildError(f"evidence line {number} is invalid JSON") from exc
        if not isinstance(record, dict) or record.get("schema") != RECORD_SCHEMA:
            raise BatchBuildError(f"evidence line {number} has an invalid schema")
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or record_id in seen:
            raise BatchBuildError(f"duplicate or invalid evidence record_id: {record_id!r}")
        seen.add(record_id)
        records.append(record)
    return records, raw


def _utc_timestamp(value: object, record_id: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise BatchBuildError(f"record {record_id} has no sort_timestamp")
    try:
        if len(value) == 10:
            parsed = datetime.combine(date.fromisoformat(value), time(), NAIVE_TIMEZONE)
        else:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=NAIVE_TIMEZONE)
    except ValueError as exc:
        raise BatchBuildError(
            f"record {record_id} has invalid sort_timestamp: {value!r}"
        ) from exc
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.isoformat()


def load_ordered_inventory(
    frozen_manifest_path: Path,
    records_path: Path,
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    """Return record-bearing holders in accepted order and explicit no-record paths."""

    frozen, frozen_raw = _read_json(frozen_manifest_path, "frozen source manifest")
    if frozen.get("schema") != SOURCE_MANIFEST_SCHEMA:
        raise BatchBuildError("frozen source manifest schema mismatch")
    files = frozen.get("files")
    if not isinstance(files, list) or frozen.get("count") != len(files):
        raise BatchBuildError("frozen source manifest count mismatch")
    source_root = frozen.get("source_root")
    if not isinstance(source_root, str) or not source_root:
        raise BatchBuildError("frozen source root is missing")

    source_lock_path = frozen_manifest_path.with_name("source-lock.json")
    source_lock, _ = _read_json(source_lock_path, "frozen source lock")
    if source_lock.get("schema") != SOURCE_LOCK_SCHEMA:
        raise BatchBuildError("frozen source lock schema mismatch")
    if source_lock.get("manifest_sha256") != sha256_bytes(frozen_raw):
        raise BatchBuildError("frozen source manifest SHA mismatch")
    if source_lock.get("holder_count") != len(files):
        raise BatchBuildError("frozen source lock holder count mismatch")
    corpus_commit = source_lock.get("corpus_commit")
    if not isinstance(corpus_commit, str) or not FULL_SHA_RE.fullmatch(corpus_commit):
        raise BatchBuildError("frozen source lock corpus commit is not a full SHA")

    file_by_path: dict[str, dict[str, Any]] = {}
    for item in files:
        if not isinstance(item, dict):
            raise BatchBuildError("frozen source manifest file is not an object")
        short_path = item.get("path")
        sha = item.get("sha256")
        if not isinstance(short_path, str) or not isinstance(sha, str):
            raise BatchBuildError("frozen source manifest file fields are invalid")
        source_path = f"{source_root}/{short_path}"
        if source_path in file_by_path:
            raise BatchBuildError(f"duplicate frozen holder path: {source_path}")
        file_by_path[source_path] = item

    records, records_raw = _read_records(records_path)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        record_id = record["record_id"]
        source_path = record.get("source_path")
        source_line = record.get("source_line")
        metadata = record.get("metadata")
        if (
            source_path not in file_by_path
            or not isinstance(source_line, int)
            or source_line < 1
            or not isinstance(metadata, dict)
            or not isinstance(record.get("quote"), str)
        ):
            raise BatchBuildError(f"record {record_id} has invalid source fields")
        expected_blob = file_by_path[source_path]["sha256"]
        if record.get("source_blob_sha256") != expected_blob:
            raise BatchBuildError(f"record {record_id} source blob SHA mismatch")
        record["_sort_timestamp_utc"] = _utc_timestamp(
            metadata.get("sort_timestamp"), record_id
        )
        grouped[source_path].append(record)

    holders: list[dict[str, Any]] = []
    for source_path, holder_records in grouped.items():
        ordered_records = sorted(
            holder_records, key=lambda item: (item["source_line"], item["record_id"])
        )
        timestamps = [item["_sort_timestamp_utc"] for item in ordered_records]
        holders.append(
            {
                "source_path": source_path,
                "source_blob_sha256": file_by_path[source_path]["sha256"],
                "min_timestamp_utc": _utc_text(min(timestamps)),
                "max_timestamp_utc": _utc_text(max(timestamps)),
                "record_ids": [item["record_id"] for item in ordered_records],
                "_records": ordered_records,
                "_max_timestamp": max(timestamps),
            }
        )
    holders.sort(key=lambda item: (item["_max_timestamp"], item["source_path"]))
    no_record_paths = sorted(set(file_by_path) - set(grouped))
    metadata = {
        "corpus_commit": corpus_commit,
        "frozen_manifest_sha256": sha256_bytes(frozen_raw),
        "evidence_records_sha256": sha256_bytes(records_raw),
        "frozen_holder_count": len(file_by_path),
        "record_bearing_holder_count": len(holders),
        "record_count": len(records),
    }
    return holders, no_record_paths, metadata


def _public_holder(holder: dict[str, Any]) -> dict[str, Any]:
    return {
        key: holder[key]
        for key in (
            "source_path",
            "source_blob_sha256",
            "min_timestamp_utc",
            "max_timestamp_utc",
            "record_ids",
        )
    }


def _counts(holders: list[dict[str, Any]]) -> dict[str, int]:
    records = [record for holder in holders for record in holder["_records"]]
    return {
        "holder_count": len(holders),
        "record_count": len(records),
        "diagnostic_record_count": sum(bool(record.get("diagnostics")) for record in records),
        "source_quote_chars": sum(len(record["quote"]) for record in records),
        "source_quote_utf8_bytes": sum(
            len(record["quote"].encode("utf-8")) for record in records
        ),
    }


def _relative(repo_root: Path, path: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise BatchBuildError(f"{label} escaped repository root: {path}") from exc


def _verify_committed_file(
    repo_root: Path,
    commit: str,
    path: Path,
    expected: bytes,
    label: str,
) -> None:
    if not FULL_SHA_RE.fullmatch(commit):
        raise BatchBuildError("accepted prior commit must be a full 40-character SHA")
    relative = _relative(repo_root, path, label)
    try:
        subprocess.run(
            ["git", "-C", str(repo_root), "cat-file", "-e", f"{commit}^{{commit}}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{commit}:{relative}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BatchBuildError(f"accepted prior commit cannot prove {label}") from exc
    if result.stdout != expected:
        raise BatchBuildError(f"accepted prior commit has different {label} bytes")


def build_manifest(
    *,
    repo_root: Path,
    batch_number: int,
    frozen_manifest_path: Path,
    records_path: Path,
    previous_manifest_path: Path,
    previous_receipt_path: Path,
    accepted_prior_commit: str,
    verify_git: bool = True,
) -> dict[str, Any]:
    if batch_number < 2:
        raise BatchBuildError("v3 builder starts after the existing batch-001")
    batch_id = f"batch-{batch_number:03d}"
    previous_batch_id = f"batch-{batch_number - 1:03d}"
    ordered, no_record_paths, metadata = load_ordered_inventory(
        frozen_manifest_path, records_path
    )
    start = (batch_number - 1) * BATCH_SIZE
    selected = ordered[start : start + BATCH_SIZE]
    if not selected:
        raise BatchBuildError("no record-bearing holders remain for this batch")

    previous_manifest, previous_manifest_raw = _read_json(
        previous_manifest_path, "previous batch manifest"
    )
    previous_receipt, previous_receipt_raw = _read_json(
        previous_receipt_path, "previous batch receipt"
    )
    if previous_manifest.get("batch_id") != previous_batch_id:
        raise BatchBuildError("previous manifest batch_id mismatch")
    if previous_receipt.get("batch_id") != previous_batch_id:
        raise BatchBuildError("previous receipt batch_id mismatch")
    expected_previous = ordered[max(0, start - BATCH_SIZE) : start]
    previous_paths = [item.get("source_path") for item in previous_manifest.get("holders", [])]
    if previous_paths != [item["source_path"] for item in expected_previous]:
        raise BatchBuildError("previous manifest is not the immediately preceding holder slice")
    if previous_manifest.get("corpus_commit") != metadata["corpus_commit"]:
        raise BatchBuildError("previous manifest corpus commit mismatch")
    if previous_manifest.get("evidence_records_sha256") != metadata["evidence_records_sha256"]:
        raise BatchBuildError("previous manifest evidence SHA mismatch")
    evidence_commit = previous_manifest.get("evidence_commit")
    if not isinstance(evidence_commit, str) or not FULL_SHA_RE.fullmatch(evidence_commit):
        raise BatchBuildError("previous manifest evidence commit is not a full SHA")

    after = previous_receipt.get("tree_digest", {}).get("after")
    if not isinstance(after, dict):
        raise BatchBuildError("previous receipt has no after-tree checkpoint")
    wiki_root = after.get("wiki_root")
    tree_sha = after.get("sha256")
    if not isinstance(wiki_root, str) or not re.fullmatch(r"[0-9a-f]{64}", str(tree_sha)):
        raise BatchBuildError("previous receipt after-tree checkpoint is invalid")
    coverage = previous_receipt.get("coverage", {})
    previous_record_ids = [
        record_id for holder in expected_previous for record_id in holder["record_ids"]
    ]
    if coverage.get("record_ids_in_manifest_order") != previous_record_ids:
        raise BatchBuildError("previous receipt coverage does not match previous holder slice")
    if verify_git:
        _verify_committed_file(
            repo_root,
            accepted_prior_commit,
            previous_manifest_path,
            previous_manifest_raw,
            "previous manifest",
        )
        _verify_committed_file(
            repo_root,
            accepted_prior_commit,
            previous_receipt_path,
            previous_receipt_raw,
            "previous receipt",
        )
    elif not FULL_SHA_RE.fullmatch(accepted_prior_commit):
        raise BatchBuildError("accepted prior commit must be a full 40-character SHA")

    batch_counts = _counts(selected)
    cumulative = _counts(ordered[: start + len(selected)])
    counts = dict(batch_counts)
    counts.update({f"cumulative_{key}": value for key, value in cumulative.items()})
    processed_paths = [holder["source_path"] for holder in ordered[: start + len(selected)]]
    remaining = len(ordered) - len(processed_paths)
    result = {
        "schema": MANIFEST_SCHEMA,
        "batch_id": batch_id,
        "previous_batch_id": previous_batch_id,
        "corpus_commit": metadata["corpus_commit"],
        "evidence_commit": evidence_commit,
        "evidence_records_sha256": metadata["evidence_records_sha256"],
        "source_snapshot": {
            "frozen_manifest_path": _relative(
                repo_root, frozen_manifest_path, "frozen manifest"
            ),
            "frozen_manifest_sha256": metadata["frozen_manifest_sha256"],
            "evidence_records_path": _relative(repo_root, records_path, "records"),
            "evidence_records_sha256": metadata["evidence_records_sha256"],
            "accepted_prior_commit": accepted_prior_commit,
            "previous_manifest_path": _relative(
                repo_root, previous_manifest_path, "previous manifest"
            ),
            "previous_manifest_sha256": sha256_bytes(previous_manifest_raw),
            "previous_receipt_path": _relative(
                repo_root, previous_receipt_path, "previous receipt"
            ),
            "previous_receipt_sha256": sha256_bytes(previous_receipt_raw),
        },
        "prior_checkpoint": {
            "wiki_root": wiki_root,
            "wiki_tree_sha256_target": tree_sha,
            "accepted_prior_commit": accepted_prior_commit,
        },
        "ordering": {
            "holder_key": "maximum normalized record timestamp",
            "record_key": "source_line then record_id",
            "naive_timestamp_timezone": "Asia/Almaty",
            "normalized_timezone": "UTC",
            "tie_break": "source_path",
            "holder_split": False,
            "batch_size": BATCH_SIZE,
        },
        "counts": counts,
        "run_state": {
            "frozen_holder_count": metadata["frozen_holder_count"],
            "record_bearing_holder_count": metadata["record_bearing_holder_count"],
            "no_record_holder_count": len(no_record_paths),
            "no_record_holders": no_record_paths,
            "processed_record_bearing_holder_count": len(processed_paths),
            "remaining_record_bearing_holder_count": remaining,
            "processed_holder_paths": processed_paths,
            "terminal_coverage_equation": (
                f"{metadata['record_bearing_holder_count']} record-bearing + "
                f"{len(no_record_paths)} no-record = {metadata['frozen_holder_count']} frozen"
            ),
        },
        "size_policy": {
            "page_count_limit": False,
            "file_length_limit": False,
            "total_output_limit": False,
            "compression_acceptance_gate": False,
            "compression_is_diagnostic_only": True,
        },
        "semantic_evidence_policy": {
            "paraphrase_and_synthesis_allowed": True,
            "material_claims_require_source_record_ids": True,
            "page_fit_required_per_material_claim": True,
            "project_corpus_enrichment": False,
            "full_quote_copy": False,
            "current_only_projection": True,
        },
        "time_boundary_utc": selected[-1]["max_timestamp_utc"],
        "holders": [_public_holder(holder) for holder in selected],
    }
    return result


def write_manifest(output: Path, value: dict[str, Any], *, check: bool) -> None:
    expected = json_bytes(value)
    if check:
        if not output.is_file() or output.is_symlink() or output.read_bytes() != expected:
            raise BatchBuildError(f"output is missing or stale: {output}")
        return
    if output.exists() or output.is_symlink():
        raise BatchBuildError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", dir=output.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(expected)
        os.replace(temporary_name, output)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--batch-number", type=int, required=True)
    parser.add_argument("--frozen-manifest", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--previous-manifest", type=Path, required=True)
    parser.add_argument("--previous-receipt", type=Path, required=True)
    parser.add_argument("--accepted-prior-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        value = build_manifest(
            repo_root=args.repo_root,
            batch_number=args.batch_number,
            frozen_manifest_path=args.frozen_manifest,
            records_path=args.records,
            previous_manifest_path=args.previous_manifest,
            previous_receipt_path=args.previous_receipt,
            accepted_prior_commit=args.accepted_prior_commit,
        )
        write_manifest(args.output, value, check=args.check)
    except BatchBuildError as exc:
        print(f"build_chronological_batch: {exc}", file=os.sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check" if args.check else "write",
                "batch_id": value["batch_id"],
                "holder_count": value["counts"]["holder_count"],
                "record_count": value["counts"]["record_count"],
                "time_boundary_utc": value["time_boundary_utc"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
