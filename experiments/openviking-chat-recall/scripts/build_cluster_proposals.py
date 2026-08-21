#!/usr/bin/env python3
"""Build stable, source-backed semantic partition proposals from F2 evidence.

This stage is deliberately deterministic.  It reads only the accepted F2
artifacts, keeps each evidence record byte-for-byte equivalent after JSON
serialization, and never reads live holder files or calls a model.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ClusterError(ValueError):
    """Raised when F2 input or generated-root ownership cannot be trusted."""


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RECORDS_PATH = EXPERIMENT_ROOT / "artifacts/full-build/evidence/records.jsonl"
DEFAULT_COVERAGE_PATH = EXPERIMENT_ROOT / "artifacts/full-build/evidence/coverage-input.json"
DEFAULT_OUTPUT_DIR = EXPERIMENT_ROOT / "artifacts/full-build/clusters"

RECORDS_ARTIFACT = "artifacts/full-build/evidence/records.jsonl"
COVERAGE_ARTIFACT = "artifacts/full-build/evidence/coverage-input.json"
MANIFEST_NAME = "partition-manifest.json"
PART_INPUT_NAME = "input.jsonl"
PART_COUNT = 8
SOURCE_ROOT = "_ops/chat-recall"
CORPUS_COMMIT = "6f98fcccdbf4b4de45ef787239ad101f70d106e2"
EVIDENCE_SCHEMA = "openviking-chat-recall/evidence-record.v1"
COVERAGE_SCHEMA = "openviking-chat-recall/coverage-input.v1"
MANIFEST_SCHEMA = "openviking-chat-recall/partition-manifest.v1"
RULE_ID = "topic-first-session-bounded-lpt.v1"

EXPECTED_RECORD_COUNT = 1101
EXPECTED_USED_COUNT = 1067
EXPECTED_REJECTED_COUNT = 34
EXPECTED_TOPIC_COUNT = 16
EXPECTED_SESSION_COUNT = 179
EXPECTED_RECORDS_SHA256 = "868ffff05768e4ebac6893436141e99493e0582b6738845350b2aa805e99d69d"
EXPECTED_COVERAGE_SHA256 = "cbe369994c643fa3f0fddcdea6f107705360b3a6afbd4a6bade4698d4b9d32d2"
EXPECTED_F2_WRITER_SHA256 = "467d4247538fa06182d059118f049483bf872c25f414922933a55d31bda52f12"

RECORD_ID_RE = re.compile(r"^cr-[0-9a-f]{16}$")
PART_ID_RE = re.compile(r"^part-[0-9]{3}$")
PART_PATH_RE = re.compile(r"^(part-[0-9]{3})/input\.jsonl$")
SYSTEM_PATH_ALIASES = (Path("/tmp"), Path("/var"))

EXPECTED_RECORD_KEYS = {
    "address",
    "content_sha256",
    "diagnostics",
    "disposition",
    "disposition_reason",
    "metadata",
    "quote",
    "record_id",
    "schema",
    "source_address",
    "source_blob_oid",
    "source_blob_sha256",
    "source_commit",
    "source_line",
    "source_path",
    "text",
}
EXPECTED_METADATA_KEYS = {
    "agent",
    "context_note",
    "date",
    "kind",
    "model",
    "precision",
    "project",
    "session",
    "session_context",
    "sort_timestamp",
    "source",
    "source_ref",
    "timestamp",
    "topic",
    "topic_raw",
    "type",
    "type_raw",
}
EXPECTED_COVERAGE_ITEM_KEYS = {
    "diagnostics",
    "disposition",
    "reason",
    "record_id",
    "source_address",
    "source_line",
    "source_path",
}
DISPOSITION_NAMES = ("used", "rejected", "skipped")

ALGORITHM = {
    "primary_unit": "normalized_topic",
    "topic_atomicity": "whole_topic_when_record_count_lte_target",
    "oversized_topic_unit": "normalized_topic_and_session_group",
    "oversized_topic_group_order": ["session", "record_id"],
    "oversized_topic_shard_capacity": "target_records_per_part",
    "oversized_session_fallback": "record_id_chunks_when_group_exceeds_capacity",
    "assignment": "largest_first_to_currently_lightest_part",
    "assignment_tiebreak": ["part_index", "topic", "shard_index"],
    "row_order": ["metadata.topic", "metadata.session", "record_id"],
    "input_order": "ignored_after_f2_canonicalization",
}


@dataclass(frozen=True)
class Shard:
    topic: str
    index: int
    records: tuple[dict[str, Any], ...]
    reason: str
    session_split: bool

    @property
    def record_count(self) -> int:
        return len(self.records)

    @property
    def session_count(self) -> int:
        return len({record["metadata"]["session"] for record in self.records})

    @property
    def text_bytes(self) -> int:
        return sum(len(record["text"].encode("utf-8")) for record in self.records)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_digest(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _records_bytes(records: list[dict[str, Any]]) -> bytes:
    return b"".join(_record_bytes(record) for record in records)


def _record_order_key(record: dict[str, Any]) -> tuple[str, int, str]:
    return (record["source_path"], record["source_line"], record["record_id"])


def _partition_row_key(record: dict[str, Any]) -> tuple[str, str, str]:
    metadata = record["metadata"]
    return (metadata["topic"], metadata["session"], record["record_id"])


def _read_regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ClusterError(f"{label} is not a regular file")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ClusterError(f"cannot read {label}") from exc


def _validate_record(record: object, line_number: int) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != EXPECTED_RECORD_KEYS:
        raise ClusterError(f"F2 record schema drift at line {line_number}")
    if record["schema"] != EVIDENCE_SCHEMA:
        raise ClusterError(f"F2 record schema mismatch at line {line_number}")
    record_id = record["record_id"]
    if not isinstance(record_id, str) or not RECORD_ID_RE.fullmatch(record_id):
        raise ClusterError(f"F2 record ID drift at line {line_number}")
    if record["source_commit"] != CORPUS_COMMIT:
        raise ClusterError(f"F2 source commit drift for {record_id}")
    if not isinstance(record["source_path"], str) or not record["source_path"].startswith(
        SOURCE_ROOT + "/"
    ):
        raise ClusterError(f"F2 source path drift for {record_id}")
    if not isinstance(record["source_line"], int) or record["source_line"] < 1:
        raise ClusterError(f"F2 source line drift for {record_id}")
    if record["source_address"] != f'{record["source_path"]}:{record["source_line"]}':
        raise ClusterError(f"F2 source address drift for {record_id}")
    if not isinstance(record["quote"], str) or record["text"] != record["quote"]:
        raise ClusterError(f"F2 evidence text drift for {record_id}")
    if record["content_sha256"] != sha256_bytes(record["quote"].encode("utf-8")):
        raise ClusterError(f"F2 evidence digest drift for {record_id}")
    if record["disposition"] not in ("used", "rejected"):
        raise ClusterError(f"F2 disposition drift for {record_id}")
    if not isinstance(record["disposition_reason"], str) or not record["disposition_reason"]:
        raise ClusterError(f"F2 disposition reason drift for {record_id}")
    diagnostics = record["diagnostics"]
    if not isinstance(diagnostics, list) or any(not isinstance(item, str) for item in diagnostics):
        raise ClusterError(f"F2 diagnostics drift for {record_id}")
    if record["disposition"] == "rejected" and not diagnostics:
        raise ClusterError(f"rejected F2 record has no diagnostic for {record_id}")
    metadata = record["metadata"]
    if not isinstance(metadata, dict) or set(metadata) != EXPECTED_METADATA_KEYS:
        raise ClusterError(f"F2 metadata schema drift for {record_id}")
    for field in ("topic", "session"):
        if not isinstance(metadata[field], str) or not metadata[field]:
            raise ClusterError(f"F2 normalized {field} drift for {record_id}")
    return record


def _load_records(path: Path) -> list[dict[str, Any]]:
    raw = _read_regular_bytes(path, "F2 records.jsonl")
    lines = raw.splitlines()
    if len(lines) != EXPECTED_RECORD_COUNT or any(not line for line in lines):
        raise ClusterError("F2 records count drift")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ClusterError(f"F2 records.jsonl is not canonical JSON at line {line_number}") from exc
        validated = _validate_record(record, line_number)
        if _record_bytes(validated).rstrip(b"\n") != line:
            raise ClusterError("F2 records.jsonl line serialization drift")
        if validated["record_id"] in seen:
            raise ClusterError("F2 record ID duplicate")
        seen.add(validated["record_id"])
        records.append(validated)

    records.sort(key=_record_order_key)
    if sha256_bytes(_records_bytes(records)) != EXPECTED_RECORDS_SHA256:
        raise ClusterError("F2 records evidence hash drift")
    if len({record["metadata"]["topic"] for record in records}) != EXPECTED_TOPIC_COUNT:
        raise ClusterError("F2 normalized topic count drift")
    if len({record["metadata"]["session"] for record in records}) != EXPECTED_SESSION_COUNT:
        raise ClusterError("F2 session count drift")
    return records


def _coverage_order_key(item: dict[str, Any]) -> tuple[str, int, str]:
    return (item["source_path"], item["source_line"], item["record_id"])


def _load_coverage(path: Path) -> dict[str, Any]:
    raw = _read_regular_bytes(path, "F2 coverage-input.json")
    try:
        coverage = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClusterError("F2 coverage-input.json is not canonical JSON") from exc
    if not isinstance(coverage, dict) or coverage.get("schema") != COVERAGE_SCHEMA:
        raise ClusterError("F2 coverage schema drift")
    items = coverage.get("records")
    if not isinstance(items, list) or len(items) != EXPECTED_RECORD_COUNT:
        raise ClusterError("F2 coverage count drift")
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != EXPECTED_COVERAGE_ITEM_KEYS:
            raise ClusterError("F2 coverage item schema drift")
        record_id = item["record_id"]
        if not isinstance(record_id, str) or not RECORD_ID_RE.fullmatch(record_id):
            raise ClusterError("F2 coverage record ID drift")
        if record_id in seen:
            raise ClusterError("F2 coverage record ID duplicate")
        seen.add(record_id)
        if not isinstance(item["diagnostics"], list) or any(
            not isinstance(value, str) for value in item["diagnostics"]
        ):
            raise ClusterError("F2 coverage diagnostics drift")
    normalized = dict(coverage)
    normalized["records"] = sorted(items, key=_coverage_order_key)
    if sha256_bytes(json_bytes(normalized)) != EXPECTED_COVERAGE_SHA256:
        raise ClusterError("F2 coverage hash drift")
    digests = coverage.get("digests")
    if not isinstance(digests, dict) or digests.get("records_sha256") != EXPECTED_RECORDS_SHA256:
        raise ClusterError("F2 coverage records digest drift")
    if digests.get("code_sha256") != EXPECTED_F2_WRITER_SHA256:
        raise ClusterError("F2 writer digest drift")
    source = coverage.get("source")
    if not isinstance(source, dict) or source.get("commit") != CORPUS_COMMIT:
        raise ClusterError("F2 coverage source provenance drift")
    return normalized


def _validate_coverage_matches(
    records: list[dict[str, Any]], coverage: dict[str, Any]
) -> None:
    coverage_by_id = {item["record_id"]: item for item in coverage["records"]}
    record_ids = {record["record_id"] for record in records}
    if set(coverage_by_id) != record_ids:
        raise ClusterError("F2 records and coverage ID sets differ")
    for record in records:
        item = coverage_by_id[record["record_id"]]
        expected = {
            "record_id": record["record_id"],
            "source_address": record["source_address"],
            "source_line": record["source_line"],
            "source_path": record["source_path"],
            "disposition": record["disposition"],
            "reason": record["disposition_reason"],
            "diagnostics": record["diagnostics"],
        }
        if item != expected:
            raise ClusterError(f"F2 coverage/evidence drift for {record['record_id']}")


def _load_inputs(
    repo_root: Path, records_path: Path, coverage_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    del repo_root  # The accepted F2 files, not a live holder root, are the input.
    records = _load_records(records_path)
    coverage = _load_coverage(coverage_path)
    _validate_coverage_matches(records, coverage)
    return records, coverage


def _make_shards(records: list[dict[str, Any]], target: int) -> list[Shard]:
    by_topic: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        by_topic[record["metadata"]["topic"]].append(record)

    shards: list[Shard] = []
    for topic in sorted(by_topic):
        topic_records = sorted(by_topic[topic], key=lambda record: record["record_id"])
        if len(topic_records) <= target:
            shards.append(
                Shard(topic, 0, tuple(topic_records), "topic_atomic", False)
            )
            continue

        by_session: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
        for record in topic_records:
            by_session[record["metadata"]["session"]].append(record)

        current: list[dict[str, Any]] = []
        shard_index = 0

        def flush_current() -> None:
            nonlocal current, shard_index
            if current:
                shards.append(
                    Shard(
                        topic,
                        shard_index,
                        tuple(current),
                        "oversized_topic_session_bounded_shard",
                        False,
                    )
                )
                shard_index += 1
                current = []

        for session in sorted(by_session):
            session_records = sorted(by_session[session], key=lambda record: record["record_id"])
            if len(session_records) > target:
                flush_current()
                for offset in range(0, len(session_records), target):
                    chunk = session_records[offset : offset + target]
                    shards.append(
                        Shard(
                            topic,
                            shard_index,
                            tuple(chunk),
                            "oversized_topic_session_overflow_chunk",
                            True,
                        )
                    )
                    shard_index += 1
                continue
            if current and len(current) + len(session_records) > target:
                flush_current()
            current.extend(session_records)
        flush_current()

    return shards


def _assign_shards(
    shards: list[Shard], part_count: int
) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = [
        {
            "part_id": f"part-{index:03d}",
            "records": [],
            "shards": [],
            "record_count": 0,
        }
        for index in range(1, part_count + 1)
    ]
    ordered_shards = sorted(
        shards,
        key=lambda shard: (-shard.record_count, shard.topic, shard.index),
    )
    for shard in ordered_shards:
        destination = min(
            range(part_count),
            key=lambda index: (parts[index]["record_count"], index),
        )
        parts[destination]["records"].extend(shard.records)
        parts[destination]["shards"].append(shard)
        parts[destination]["record_count"] += shard.record_count
    for part in parts:
        part["records"].sort(key=_partition_row_key)
        part["shards"].sort(key=lambda shard: (shard.topic, shard.index))
    return parts


def _counter_dict(values: list[str], names: tuple[str, ...] = ()) -> dict[str, int]:
    counter = collections.Counter(values)
    for name in names:
        counter.setdefault(name, 0)
    return {key: counter[key] for key in sorted(counter)}


def _record_ids_digest(records: list[dict[str, Any]]) -> str:
    return stable_digest(sorted(record["record_id"] for record in records))


def _parts_digest(parts: list[dict[str, Any]]) -> str:
    return stable_digest(
        [
            {
                "part_id": part["part_id"],
                "path": part["path"],
                "input_sha256": part["input_sha256"],
            }
            for part in parts
        ]
    )


def _part_descriptor(part: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    records = part["records"]
    part_bytes = _records_bytes(records)
    descriptor = {
        "part_id": part["part_id"],
        "path": f'{part["part_id"]}/{PART_INPUT_NAME}',
        "row_order": ALGORITHM["row_order"],
        "record_count": len(records),
        "record_ids_sha256": _record_ids_digest(records),
        "input_sha256": sha256_bytes(part_bytes),
        "text_bytes": sum(len(record["text"].encode("utf-8")) for record in records),
        "disposition_counts": _counter_dict(
            [record["disposition"] for record in records], DISPOSITION_NAMES
        ),
        "diagnostic_counts": _counter_dict(
            [diagnostic for record in records for diagnostic in record["diagnostics"]]
        ),
        "diagnostic_record_count": sum(bool(record["diagnostics"]) for record in records),
        "topic_counts": _counter_dict(
            [record["metadata"]["topic"] for record in records]
        ),
        "session_counts": _counter_dict(
            [record["metadata"]["session"] for record in records]
        ),
        "topic_count": len({record["metadata"]["topic"] for record in records}),
        "session_count": len({record["metadata"]["session"] for record in records}),
        "shards": [
            {
                "topic": shard.topic,
                "shard_index": shard.index,
                "record_count": shard.record_count,
                "session_count": shard.session_count,
                "text_bytes": shard.text_bytes,
                "reason": shard.reason,
                "session_split": shard.session_split,
            }
            for shard in part["shards"]
        ],
    }
    return descriptor, part_bytes


def _build_artifacts(
    records: list[dict[str, Any]], coverage: dict[str, Any]
) -> tuple[dict[str, bytes], dict[str, Any]]:
    target = math.ceil(len(records) / PART_COUNT)
    shards = _make_shards(records, target)
    assigned_parts = _assign_shards(shards, PART_COUNT)
    assigned_ids = [
        record["record_id"]
        for part in assigned_parts
        for record in part["records"]
    ]
    expected_ids = [record["record_id"] for record in records]
    if len(assigned_ids) != EXPECTED_RECORD_COUNT or len(set(assigned_ids)) != EXPECTED_RECORD_COUNT:
        raise ClusterError("partition membership is missing or duplicate")
    if set(assigned_ids) != set(expected_ids):
        raise ClusterError("partition membership differs from F2 record IDs")

    part_descriptors: list[dict[str, Any]] = []
    artifacts: dict[str, bytes] = {}
    for part in assigned_parts:
        descriptor, part_bytes = _part_descriptor(part)
        part_descriptors.append(descriptor)
        artifacts[descriptor["path"]] = part_bytes

    topic_counts = _counter_dict([record["metadata"]["topic"] for record in records])
    session_counts = _counter_dict([record["metadata"]["session"] for record in records])
    diagnostic_counts = _counter_dict(
        [diagnostic for record in records for diagnostic in record["diagnostics"]]
    )
    diagnostic_record_count = sum(bool(record["diagnostics"]) for record in records)
    disposition_counts = _counter_dict(
        [record["disposition"] for record in records], DISPOSITION_NAMES
    )
    config = {
        "part_count": PART_COUNT,
        "target_records_per_part": target,
        "max_shard_records": target,
        "topic_count": len(topic_counts),
        "session_count": len(session_counts),
        "oversized_topic_threshold": target,
        "normalized_topic_field": "metadata.topic",
        "normalized_session_field": "metadata.session",
        "record_id_field": "record_id",
    }
    rule_payload = {"rule_id": RULE_ID, "algorithm": ALGORITHM, "config": config}
    code_sha256 = sha256_bytes(Path(__file__).read_bytes())
    oversized_topics = []
    for topic, count in topic_counts.items():
        if count > target:
            oversized_topics.append(
                {
                    "topic": topic,
                    "record_count": count,
                    "shard_count": sum(1 for shard in shards if shard.topic == topic),
                    "reason": "topic exceeds target; split only at (topic,session) boundaries",
                }
            )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "owned_files": [MANIFEST_NAME, "part-*/input.jsonl"],
        "input": {
            "records": {
                "artifact": RECORDS_ARTIFACT,
                "schema": EVIDENCE_SCHEMA,
                "sha256": EXPECTED_RECORDS_SHA256,
                "record_count": len(records),
                "order": "source_path,source_line,record_id",
            },
            "coverage": {
                "artifact": COVERAGE_ARTIFACT,
                "schema": COVERAGE_SCHEMA,
                "sha256": EXPECTED_COVERAGE_SHA256,
                "record_count": len(coverage["records"]),
                "order": "source_path,source_line,record_id",
            },
            "source_commit": CORPUS_COMMIT,
            "source_root": SOURCE_ROOT,
            "f2_writer_sha256": EXPECTED_F2_WRITER_SHA256,
            "f2_digests": dict(sorted(coverage["digests"].items())),
        },
        "rule": {
            "id": RULE_ID,
            "algorithm": ALGORITHM,
            "config": config,
            "config_sha256": stable_digest(config),
            "rule_sha256": stable_digest(rule_payload),
            "writer_sha256": code_sha256,
            "oversized_topics": oversized_topics,
            "session_boundary": {
                "unit": "topic_session_group",
                "cross_part_allowed": True,
                "cross_part_reason": "a session may have multiple normalized topics; each topic boundary is atomic",
                "session_split_allowed": True,
                "session_split_reason": "only when one topic_session_group exceeds max_shard_records",
            },
        },
        "coverage": {
            "record_count": len(records),
            "part_count": len(part_descriptors),
            "part_record_count_sum": sum(part["record_count"] for part in part_descriptors),
            "unique_record_id_count": len(set(assigned_ids)),
            "record_ids_sha256": _record_ids_digest(records),
            "disposition_counts": disposition_counts,
            "diagnostic_counts": diagnostic_counts,
            "diagnostic_record_count": diagnostic_record_count,
            "topic_counts": topic_counts,
            "session_counts": session_counts,
            "topic_count": len(topic_counts),
            "session_count": len(session_counts),
            "rejected_records_visible_in_parts": True,
        },
        "parts": part_descriptors,
        "outputs": {
            "part_count": len(part_descriptors),
            "parts_sha256": _parts_digest(part_descriptors),
            "part_input_bytes": sum(
                len(artifacts[part["path"]]) for part in part_descriptors
            ),
        },
    }
    manifest_raw = json_bytes(manifest)
    artifacts[MANIFEST_NAME] = manifest_raw
    sizes = [part["record_count"] for part in part_descriptors]
    summary = {
        "status": "built",
        "part_count": len(part_descriptors),
        "record_count": len(records),
        "used_count": disposition_counts["used"],
        "rejected_count": disposition_counts["rejected"],
        "min_part_records": min(sizes),
        "max_part_records": max(sizes),
        "median_part_records": statistics.median(sizes),
        "records_sha256": EXPECTED_RECORDS_SHA256,
        "coverage_sha256": EXPECTED_COVERAGE_SHA256,
        "manifest_sha256": sha256_bytes(manifest_raw),
        "part_input_sha256": {
            part["part_id"]: part["input_sha256"] for part in part_descriptors
        },
        "topic_counts": topic_counts,
        "session_count": len(session_counts),
        "diagnostic_counts": diagnostic_counts,
    }
    return artifacts, summary


def _reject_symlink_components(path: Path, label: str) -> None:
    absolute = path.absolute()
    for component in (absolute, *absolute.parents):
        try:
            is_symlink = component.is_symlink()
        except OSError as exc:
            raise ClusterError(f"cannot inspect {label} path") from exc
        if is_symlink and component not in SYSTEM_PATH_ALIASES:
            raise ClusterError(f"{label} path contains a symlink: {component.name}")


def _resolve_output_root(repo_root: Path, output_dir: Path) -> Path:
    raw = output_dir if output_dir.is_absolute() else repo_root / output_dir
    absolute = raw.absolute()
    _reject_symlink_components(absolute, "clusters output")
    try:
        output_root = absolute.resolve(strict=False)
        source_root = (repo_root / SOURCE_ROOT).resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ClusterError("cannot resolve clusters output containment") from exc
    if output_root == source_root or output_root.is_relative_to(source_root):
        raise ClusterError("clusters output overlaps live source root")
    if source_root.is_relative_to(output_root):
        raise ClusterError("clusters output contains live source root")
    return output_root


def _contained_destination(root: Path, relative: str) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute() or not relative_path.parts or ".." in relative_path.parts:
        raise ClusterError(f"owned destination escapes generated root: {relative!r}")
    destination = root / relative_path
    try:
        resolved_root = root.resolve()
        resolved_destination = destination.resolve(strict=False)
        if not resolved_destination.is_relative_to(resolved_root):
            raise ClusterError(f"owned destination escapes generated root: {relative!r}")
    except (OSError, RuntimeError) as exc:
        raise ClusterError(f"cannot resolve owned destination: {relative!r}") from exc
    for component in (destination, *destination.parents):
        if component == root:
            break
        try:
            if component.is_symlink():
                raise ClusterError(f"owned destination contains a symlink: {relative!r}")
        except OSError as exc:
            raise ClusterError(f"cannot inspect owned destination: {relative!r}") from exc
    return destination


def _validate_existing_owned_manifest(root: Path) -> list[tuple[Path, Path]]:
    manifest_path = _contained_destination(root, MANIFEST_NAME)
    matching_part_names = {
        child.name
        for child in root.iterdir()
        if PART_ID_RE.fullmatch(child.name)
    }
    if not manifest_path.exists():
        if matching_part_names:
            raise ClusterError("clusters output ownership is unproven: part directory without manifest")
        return []
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ClusterError("clusters manifest is not a regular file")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClusterError("clusters output ownership is unproven: invalid manifest") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != MANIFEST_SCHEMA:
        raise ClusterError("clusters output ownership is unproven: schema mismatch")
    if manifest.get("owned_files") != [MANIFEST_NAME, "part-*/input.jsonl"]:
        raise ClusterError("clusters output ownership is unproven: owned-file mismatch")
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise ClusterError("clusters output ownership is unproven: parts missing")
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict) or outputs.get("parts_sha256") != _parts_digest(parts):
        raise ClusterError("clusters output ownership is unproven: parts digest mismatch")
    listed_names: set[str] = set()
    deletions: list[tuple[Path, Path]] = []
    for part in parts:
        if not isinstance(part, dict):
            raise ClusterError("clusters output ownership is unproven: malformed part")
        part_id = part.get("part_id")
        relative = part.get("path")
        if not isinstance(part_id, str) or not PART_ID_RE.fullmatch(part_id):
            raise ClusterError("clusters output ownership is unproven: malformed part ID")
        if not isinstance(relative, str) or PART_PATH_RE.fullmatch(relative) is None:
            raise ClusterError("clusters output ownership is unproven: escaping part path")
        match = PART_PATH_RE.fullmatch(relative)
        assert match is not None
        if match.group(1) != part_id or part_id in listed_names:
            raise ClusterError("clusters output ownership is unproven: duplicate part")
        listed_names.add(part_id)
        input_path = _contained_destination(root, relative)
        part_dir = _contained_destination(root, part_id)
        if not part_dir.is_dir() or part_dir.is_symlink():
            raise ClusterError("clusters output ownership is unproven: part directory")
        try:
            entries = list(part_dir.iterdir())
        except OSError as exc:
            raise ClusterError("clusters output ownership is unproven: unreadable part") from exc
        if {entry.name for entry in entries} != {PART_INPUT_NAME}:
            raise ClusterError("clusters output ownership is unproven: part contains unrelated files")
        if input_path.is_symlink() or not input_path.is_file():
            raise ClusterError("clusters output ownership is unproven: input is not a regular file")
        if part.get("input_sha256") != sha256_bytes(input_path.read_bytes()):
            raise ClusterError("clusters output ownership is unproven: input digest mismatch")
        deletions.append((input_path, part_dir))
    if matching_part_names != listed_names:
        raise ClusterError("clusters output ownership is unproven: unlisted part directory")
    return deletions


def _prepare_output_root(repo_root: Path, output_dir: Path) -> Path:
    output_root = _resolve_output_root(repo_root, output_dir)
    try:
        output_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ClusterError("cannot create clusters output root") from exc
    if output_root.is_symlink() or not output_root.is_dir():
        raise ClusterError("clusters output root is not a real directory")
    deletions = _validate_existing_owned_manifest(output_root)
    for input_path, part_dir in deletions:
        input_path.unlink()
        part_dir.rmdir()
    manifest_path = _contained_destination(output_root, MANIFEST_NAME)
    if manifest_path.exists():
        manifest_path.unlink()
    return output_root


def _write_artifacts(output_root: Path, artifacts: dict[str, bytes]) -> None:
    for relative, payload in sorted(artifacts.items()):
        destination = _contained_destination(output_root, relative)
        if relative == MANIFEST_NAME:
            continue
        part_id = relative.split("/", 1)[0]
        part_dir = _contained_destination(output_root, part_id)
        if part_dir.exists():
            if part_dir.is_symlink() or not part_dir.is_dir():
                raise ClusterError("owned part path is not a real directory")
        else:
            part_dir.mkdir()
        destination.write_bytes(payload)
    manifest_path = _contained_destination(output_root, MANIFEST_NAME)
    manifest_path.write_bytes(artifacts[MANIFEST_NAME])


def _assert_expected_outputs(output_root: Path, artifacts: dict[str, bytes]) -> None:
    if output_root.is_symlink() or not output_root.is_dir():
        raise ClusterError("clusters output root is missing or not a real directory")
    for relative, expected in sorted(artifacts.items()):
        destination = _contained_destination(output_root, relative)
        if destination.is_symlink() or not destination.is_file():
            raise ClusterError(f"clusters output is missing or symlinked: {relative}")
        try:
            actual = destination.read_bytes()
        except OSError as exc:
            raise ClusterError(f"cannot read clusters output: {relative}") from exc
        if actual != expected:
            raise ClusterError(f"clusters output differs from current writer: {relative}")


def _resolve_input(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def build(
    repo_root: Path = DEFAULT_REPO_ROOT,
    records_path: Path = DEFAULT_RECORDS_PATH,
    coverage_path: Path = DEFAULT_COVERAGE_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    records, coverage = _load_inputs(
        repo_root,
        _resolve_input(repo_root, records_path),
        _resolve_input(repo_root, coverage_path),
    )
    artifacts, summary = _build_artifacts(records, coverage)
    output_root = _prepare_output_root(repo_root, output_dir)
    _write_artifacts(output_root, artifacts)
    return {**summary, "output_dir": str(output_root)}


def check(
    repo_root: Path = DEFAULT_REPO_ROOT,
    records_path: Path = DEFAULT_RECORDS_PATH,
    coverage_path: Path = DEFAULT_COVERAGE_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    records, coverage = _load_inputs(
        repo_root,
        _resolve_input(repo_root, records_path),
        _resolve_input(repo_root, coverage_path),
    )
    artifacts, summary = _build_artifacts(records, coverage)
    output_root = _resolve_output_root(repo_root, output_dir)
    _assert_expected_outputs(output_root, artifacts)
    return {**summary, "status": "pass", "output_dir": str(output_root)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic topic-first F3 partition proposals from accepted F2 evidence."
    )
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS_PATH)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="verify outputs without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = (
            check(args.repo_root, args.records, args.coverage, args.output_dir)
            if args.check
            else build(args.repo_root, args.records, args.coverage, args.output_dir)
        )
    except ClusterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
