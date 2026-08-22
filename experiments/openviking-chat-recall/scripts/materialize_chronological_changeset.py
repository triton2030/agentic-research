#!/usr/bin/env python3
"""Materialize one accepted chronological Wiki changeset without an LLM.

The semantic writer owns the proposed claims and Markdown.  This module owns
only the deterministic boundary: input hashes, page containment, prior state,
exact bytes, coverage, link guards, staged replacement, and the machine
receipt.  A successful receipt is therefore a materialization claim, not a
semantic acceptance verdict.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Any


class MaterializationError(ValueError):
    """Raised before an untrusted changeset can mutate the current Wiki."""


CHANGESET_SCHEMA_V3 = "openviking-chat-recall/chronological-wiki-changeset.v3"
CHANGESET_SCHEMA_V4 = "openviking-chat-recall/chronological-wiki-changeset.v4"
CHANGESET_SCHEMA_V5 = "openviking-chat-recall/chronological-wiki-changeset.v5"
RECEIPT_SCHEMA_V3 = "openviking-chat-recall/chronological-wiki-receipt.v3"
RECEIPT_SCHEMA_V4 = "openviking-chat-recall/chronological-wiki-receipt.v4"
RECEIPT_SCHEMA_V5 = "openviking-chat-recall/chronological-wiki-receipt.v5"
ALLOCATION_SCHEMA = "openviking-chat-recall/chronological-wiki-allocation.v1"
# Backward-compatible v3 names for callers that imported the original constants.
CHANGESET_SCHEMA = CHANGESET_SCHEMA_V3
RECEIPT_SCHEMA = RECEIPT_SCHEMA_V3
MANIFEST_SCHEMA_V3 = "openviking-chat-recall/chronological-batch-input.v3"
MANIFEST_SCHEMA_V4 = "openviking-chat-recall/chronological-batch-input.v4"
PREFLIGHT_SCHEMA_V1 = "openviking-chat-recall/wiki-writer-preflight.v1"
MANIFEST_SCHEMA = MANIFEST_SCHEMA_V3
ALLOWED_OPERATIONS = {"create", "update", "supersede", "no-change", "reject"}
MUTATING_OPERATIONS = {"create", "update", "supersede"}
CONTENT_OPERATIONS = {"create", "update"}
SEMANTIC_PAGE_OPERATIONS = {"create", "update", "supersede", "no-change"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RECORD_ID_RE = re.compile(r"^cr-[0-9a-f]{16}$")
LINK_RE = re.compile(r"\]\(([^)]+)\)")
H1_RE = re.compile(r"(?m)^# ([^\n]+)$")
FRONTMATTER_TYPE_RE = re.compile(r"(?m)^type: ([a-z][a-z0-9-]*)$")
FRONTMATTER_TITLE_RE = re.compile(r"(?m)^title: ([^\n]+)$")
FRONTMATTER_DESCRIPTION_RE = re.compile(r"(?m)^description: ([^\n]+)$")
SOURCES_HEADING_RE = re.compile(r"(?m)^## Источники\s*$")
SOURCE_ANCHOR_RE = re.compile(r"^L([1-9][0-9]*)$")
EXTERNAL_LINK_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
TREE_ALGORITHM = "sha256 of sorted relative-UTF-8-path\\0file-sha256\\n entries"
QUOTE_COPY_MIN_CHARS = 80


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _require_sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise MaterializationError(f"{label} must be a lowercase SHA-256")
    return value


def _read_regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise MaterializationError(f"{label} is not a regular file: {path}")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise MaterializationError(f"cannot read {label}: {path}") from exc


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = _read_regular_bytes(path, label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaterializationError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise MaterializationError(f"{label} must contain a JSON object")
    return value, raw


def _read_records(path: Path) -> tuple[dict[str, dict[str, Any]], bytes]:
    raw = _read_regular_bytes(path, "evidence records")
    records: dict[str, dict[str, Any]] = {}
    for number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MaterializationError(
                f"evidence records line {number} is not valid UTF-8 JSON"
            ) from exc
        if not isinstance(record, dict):
            raise MaterializationError(f"evidence records line {number} is not an object")
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not RECORD_ID_RE.fullmatch(record_id):
            raise MaterializationError(f"evidence record {number} has invalid record_id")
        if record_id in records:
            raise MaterializationError(f"duplicate evidence record_id: {record_id}")
        source_path = record.get("source_path")
        source_line = record.get("source_line")
        source_address = record.get("source_address")
        quote = record.get("quote")
        if (
            not isinstance(source_path, str)
            or not source_path.startswith("_ops/chat-recall/")
            or not isinstance(source_line, int)
            or source_line < 1
            or source_address != f"{source_path}:{source_line}"
            or not isinstance(quote, str)
        ):
            raise MaterializationError(f"evidence record {record_id} has invalid source fields")
        records[record_id] = record
    return records, raw


def _inside(root: Path, path: Path, label: str) -> Path:
    root_resolved = root.resolve()
    path_resolved = path.resolve(strict=False)
    try:
        path_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise MaterializationError(f"{label} escaped repository root: {path}") from exc
    return path_resolved


def _assert_existing_components_not_symlinks(root: Path, path: Path, label: str) -> None:
    root_lexical = Path(os.path.abspath(root))
    lexical = Path(os.path.abspath(path))
    try:
        relative = lexical.relative_to(root_lexical)
    except ValueError as exc:
        raise MaterializationError(f"{label} escaped repository root: {path}") from exc
    current = root_lexical
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise MaterializationError(f"{label} contains a symlink component: {current}")
    _inside(root, path, label)


def tree_digest(root: Path) -> tuple[str, list[dict[str, Any]]]:
    """Return the accepted chronological Wiki tree digest and entries."""

    if root.is_symlink() or not root.is_dir():
        raise MaterializationError(f"Wiki root is not a regular directory: {root}")
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise MaterializationError(f"Wiki tree contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file() or path.suffix != ".md":
            raise MaterializationError(f"Wiki tree contains a non-Markdown file: {path}")
        raw = path.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MaterializationError(f"Wiki page is not UTF-8: {path}") from exc
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_bytes(raw),
                "utf8_bytes": len(raw),
            }
        )
    payload = b"".join(
        f"{entry['path']}\0{entry['sha256']}\n".encode("utf-8")
        for entry in entries
    )
    return sha256_bytes(payload), entries


def _tree_from_files(files: dict[str, bytes]) -> tuple[str, list[dict[str, Any]]]:
    entries = [
        {"path": path, "sha256": sha256_bytes(raw), "utf8_bytes": len(raw)}
        for path, raw in sorted(files.items())
    ]
    payload = b"".join(
        f"{entry['path']}\0{entry['sha256']}\n".encode("utf-8")
        for entry in entries
    )
    return sha256_bytes(payload), entries


def _wiki_files(root: Path) -> dict[str, bytes]:
    tree_digest(root)
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*.md"))
    }


def _page_relative_path(value: object) -> str:
    if not isinstance(value, str):
        raise MaterializationError("page path must be a string")
    candidate = PurePosixPath(value)
    prefix = PurePosixPath("current/wiki")
    if candidate.is_absolute() or ".." in candidate.parts:
        raise MaterializationError(f"page path escaped current/wiki: {value!r}")
    try:
        relative = candidate.relative_to(prefix)
    except ValueError as exc:
        raise MaterializationError(f"page path must be under current/wiki: {value!r}") from exc
    if not relative.parts or relative.suffix != ".md" or "." in relative.parts:
        raise MaterializationError(f"invalid Markdown page path: {value!r}")
    return relative.as_posix()


def _page_h1(content: str, page_path: str) -> str:
    headings = H1_RE.findall(content)
    if len(headings) != 1:
        raise MaterializationError(f"page {page_path} must contain exactly one H1")
    return headings[0].strip()


def _validate_page_type(content: str, expected: object, page_path: str) -> None:
    match = FRONTMATTER_TYPE_RE.search(content)
    if not isinstance(expected, str) or match is None or match.group(1) != expected:
        raise MaterializationError(f"page type mismatch for {page_path}")


def _validate_claims(
    operation: dict[str, Any],
    h1: str,
    evidence: dict[str, dict[str, Any]],
    *,
    strict_v5: bool = False,
) -> None:
    claims = operation.get("material_claims")
    if not isinstance(claims, list):
        raise MaterializationError("material_claims must be a list")
    claim_ids: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise MaterializationError("material claim must be an object")
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id or claim_id in claim_ids:
            raise MaterializationError("material claim_id is missing or duplicated")
        claim_ids.add(claim_id)
        if not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
            raise MaterializationError(f"material claim {claim_id} has no statement")
        if claim.get("epistemic_kind") not in {
            "source-backed",
            "inference",
            "uncertainty",
        }:
            raise MaterializationError(f"material claim {claim_id} has invalid epistemic kind")
        support = claim.get("supporting_record_ids")
        if not isinstance(support, list) or not support or len(set(support)) != len(support):
            raise MaterializationError(f"material claim {claim_id} has invalid support")
        if any(record_id not in evidence for record_id in support):
            raise MaterializationError(f"material claim {claim_id} cites unknown evidence")
        if not set(support).issubset(set(operation["record_ids"])):
            raise MaterializationError(
                f"material claim {claim_id} support is outside operation record_ids"
            )
        page_fit = claim.get("page_fit")
        if not isinstance(page_fit, dict):
            raise MaterializationError(f"material claim {claim_id} is missing page_fit")
        if page_fit.get("page_question") != h1:
            raise MaterializationError(f"material claim {claim_id} page_fit H1 mismatch")
        answering = page_fit.get("answering_record_ids")
        answering_is_invalid = (
            not isinstance(answering, list)
            or not answering
            or len(set(answering)) != len(answering)
        )
        if strict_v5:
            answering_is_invalid = answering_is_invalid or answering != support
        else:
            answering_is_invalid = answering_is_invalid or not set(answering).issubset(
                support
            )
        if answering_is_invalid:
            raise MaterializationError(
                f"material claim {claim_id} page_fit answering_record_ids are invalid"
            )
        if strict_v5:
            alignment = page_fit.get("source_alignment")
            if not isinstance(alignment, list) or len(alignment) != len(answering):
                raise MaterializationError(
                    f"material claim {claim_id} page_fit source_alignment is invalid"
                )
            alignment_ids: list[str] = []
            for item in alignment:
                if not isinstance(item, dict):
                    raise MaterializationError(
                        f"material claim {claim_id} source alignment must be an object"
                    )
                record_id = item.get("record_id")
                if not isinstance(record_id, str):
                    raise MaterializationError(
                        f"material claim {claim_id} source alignment has no record ID"
                    )
                alignment_ids.append(record_id)
                for field in (
                    "named_subject",
                    "scope",
                    "modality",
                    "supporting_words",
                ):
                    value = item.get(field)
                    if not isinstance(value, str) or not value.strip():
                        raise MaterializationError(
                            f"material claim {claim_id} source alignment has no {field}"
                        )
                if len(item["supporting_words"]) > 120:
                    raise MaterializationError(
                        f"material claim {claim_id} source alignment quote is too long"
                    )
                quote = evidence[record_id].get("quote")
                if (
                    not isinstance(quote, str)
                    or item["supporting_words"] not in quote
                ):
                    raise MaterializationError(
                        f"material claim {claim_id} source alignment words "
                        "are not in the exact quote"
                    )
            if alignment_ids != answering:
                raise MaterializationError(
                    f"material claim {claim_id} source alignment order mismatch"
                )
        if not isinstance(page_fit.get("reason"), str) or not page_fit["reason"].strip():
            raise MaterializationError(f"material claim {claim_id} page_fit has no reason")


def _manifest_record_ids(manifest: dict[str, Any]) -> list[str]:
    if manifest.get("schema") not in {MANIFEST_SCHEMA_V3, MANIFEST_SCHEMA_V4}:
        raise MaterializationError("manifest schema mismatch")
    holders = manifest.get("holders")
    if not isinstance(holders, list) or not holders:
        raise MaterializationError("manifest holders must be a non-empty list")
    record_ids: list[str] = []
    holder_paths: set[str] = set()
    for holder in holders:
        if not isinstance(holder, dict):
            raise MaterializationError("manifest holder must be an object")
        source_path = holder.get("source_path")
        holder_records = holder.get("record_ids")
        if (
            not isinstance(source_path, str)
            or not source_path.startswith("_ops/chat-recall/")
            or source_path in holder_paths
            or not isinstance(holder_records, list)
            or not holder_records
        ):
            raise MaterializationError("manifest holder fields are invalid")
        holder_paths.add(source_path)
        for record_id in holder_records:
            if not isinstance(record_id, str) or not RECORD_ID_RE.fullmatch(record_id):
                raise MaterializationError("manifest contains an invalid record_id")
            record_ids.append(record_id)
    if len(set(record_ids)) != len(record_ids):
        raise MaterializationError("manifest record IDs are duplicated")
    counts = manifest.get("counts")
    if (
        not isinstance(counts, dict)
        or counts.get("holder_count") != len(holders)
        or counts.get("record_count") != len(record_ids)
    ):
        raise MaterializationError("manifest counts do not match holders and records")
    return record_ids


def _validate_input_binding(
    repo_root: Path,
    changeset: dict[str, Any],
    manifest_path: Path,
    manifest_raw: bytes,
    evidence_records_path: Path,
    evidence_raw: bytes,
) -> None:
    input_value = changeset.get("input")
    if not isinstance(input_value, dict):
        raise MaterializationError("changeset input is missing")
    actual_manifest = _inside(repo_root, manifest_path, "manifest path")
    actual_evidence = _inside(repo_root, evidence_records_path, "evidence path")
    expected_manifest = _inside(
        repo_root, repo_root / str(input_value.get("manifest_path", "")), "manifest path"
    )
    expected_evidence = _inside(
        repo_root,
        repo_root / str(input_value.get("evidence_records_path", "")),
        "evidence path",
    )
    if actual_manifest != expected_manifest:
        raise MaterializationError("manifest path does not match changeset input")
    if actual_evidence != expected_evidence:
        raise MaterializationError("evidence path does not match changeset input")
    if sha256_bytes(manifest_raw) != _require_sha(
        input_value.get("manifest_sha256"), "manifest SHA"
    ):
        raise MaterializationError("manifest SHA mismatch")
    if sha256_bytes(evidence_raw) != _require_sha(
        input_value.get("evidence_records_sha256"), "evidence records SHA"
    ):
        raise MaterializationError("evidence records SHA mismatch")


def _repo_relative_path(repo_root: Path, path: Path, label: str) -> str:
    resolved = _inside(repo_root, path, label)
    return resolved.relative_to(repo_root.resolve()).as_posix()


def _validate_v5_page_shape(content: str, page_type: str, page_path: str) -> None:
    """Validate the mechanical OpenViking page envelope for the v1 clean chain."""

    relative = PurePosixPath(_page_relative_path(page_path))
    title = FRONTMATTER_TITLE_RE.search(content)
    description = FRONTMATTER_DESCRIPTION_RE.search(content)
    if title is None or not title.group(1).strip():
        raise MaterializationError(f"page title is missing for {page_path}")
    if description is None or not description.group(1).strip():
        raise MaterializationError(f"page description is missing for {page_path}")
    if _page_h1(content, page_path) != title.group(1).strip():
        raise MaterializationError(f"page H1 does not equal title for {page_path}")
    if page_type == "index":
        if relative.as_posix() != "index.md":
            raise MaterializationError("v5 index must be current/wiki/index.md")
        if SOURCES_HEADING_RE.search(content):
            raise MaterializationError("v5 index cannot contain an Источники section")
        return
    if len(relative.parts) != 2 or relative.parts[0] != page_type:
        raise MaterializationError(
            f"v5 knowledge page path must be <type>/<page>.md: {page_path}"
        )
    if len(SOURCES_HEADING_RE.findall(content)) != 1:
        raise MaterializationError(
            f"v5 knowledge page must contain exactly one ## Источники: {page_path}"
        )


def _validate_v5_bindings(
    *,
    repo_root: Path,
    changeset: dict[str, Any],
    changeset_path: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
    manifest_raw: bytes,
    before_sha: str,
) -> dict[str, str]:
    """Validate the prompt/output/preflight boundary and return exact source targets."""

    if manifest.get("schema") != MANIFEST_SCHEMA_V4:
        raise MaterializationError("v5 changeset requires a v4 batch manifest")
    prompt = manifest.get("prompt")
    materializer = manifest.get("materializer")
    output = manifest.get("output")
    if not all(isinstance(item, dict) for item in (prompt, materializer, output)):
        raise MaterializationError("v4 manifest prompt/materializer/output binding is missing")

    prompt_path = _inside(
        repo_root, repo_root / str(prompt.get("path", "")), "prompt path"
    )
    prompt_raw = _read_regular_bytes(prompt_path, "writer prompt")
    prompt_sha = _require_sha(prompt.get("sha256"), "manifest prompt SHA")
    if sha256_bytes(prompt_raw) != prompt_sha:
        raise MaterializationError("manifest prompt SHA mismatch")

    materializer_path = _inside(
        repo_root,
        repo_root / str(materializer.get("path", "")),
        "materializer path",
    )
    if materializer_path != Path(__file__).resolve():
        raise MaterializationError("manifest materializer path mismatch")
    materializer_raw = _read_regular_bytes(materializer_path, "materializer")
    materializer_sha = _require_sha(
        materializer.get("sha256"), "manifest materializer SHA"
    )
    if sha256_bytes(materializer_raw) != materializer_sha:
        raise MaterializationError("manifest materializer SHA mismatch")

    expected_changeset_path = _inside(
        repo_root,
        repo_root / str(output.get("changeset_path", "")),
        "changeset path",
    )
    if changeset_path.resolve() != expected_changeset_path:
        raise MaterializationError("manifest changeset path mismatch")
    if output.get("changeset_schema") != CHANGESET_SCHEMA_V5:
        raise MaterializationError("manifest changeset schema mismatch")
    contract = output.get("output_contract")
    if not isinstance(contract, dict):
        raise MaterializationError("manifest output contract is missing")
    contract_sha = _require_sha(
        output.get("output_contract_sha256"), "output contract SHA"
    )
    if sha256_bytes(json_bytes(contract)) != contract_sha:
        raise MaterializationError("manifest output contract SHA mismatch")

    input_value = changeset.get("input")
    expected_echoes = {
        "prompt_path": prompt.get("path"),
        "prompt_sha256": prompt_sha,
        "materializer_path": materializer.get("path"),
        "materializer_sha256": materializer_sha,
        "output_contract_sha256": contract_sha,
    }
    if not isinstance(input_value, dict) or any(
        input_value.get(key) != value for key, value in expected_echoes.items()
    ):
        raise MaterializationError("v5 changeset does not echo exact prompt/output bindings")

    preflight_path = _inside(
        repo_root,
        repo_root / str(manifest.get("preflight_receipt_path", "")),
        "preflight receipt path",
    )
    preflight, _ = _read_json(preflight_path, "preflight receipt")
    expected_preflight = {
        "schema": PREFLIGHT_SCHEMA_V1,
        "status": "pass",
        "manifest_path": _repo_relative_path(repo_root, manifest_path, "manifest path"),
        "manifest_sha256": sha256_bytes(manifest_raw),
        "prompt_sha256": prompt_sha,
        "materializer_sha256": materializer_sha,
        "prior_wiki_tree_sha256": before_sha,
    }
    if any(preflight.get(key) != value for key, value in expected_preflight.items()):
        raise MaterializationError("preflight receipt does not match frozen v5 bindings")

    bindings = manifest.get("record_bindings")
    manifest_ids = _manifest_record_ids(manifest)
    if not isinstance(bindings, list) or len(bindings) != len(manifest_ids):
        raise MaterializationError("manifest record bindings do not match records")
    source_targets: dict[str, str] = {}
    for record_id, binding in zip(manifest_ids, bindings, strict=True):
        if not isinstance(binding, dict) or binding.get("record_id") != record_id:
            raise MaterializationError("manifest record bindings are out of order")
        target = binding.get("source_link_target")
        if not isinstance(target, str) or not target:
            raise MaterializationError(f"source target is missing for {record_id}")
        source_targets[record_id] = target
    return source_targets


def _validate_v5_evidence_metadata(
    changeset: dict[str, Any], evidence: dict[str, dict[str, Any]]
) -> None:
    metadata = changeset.get("evidence_metadata")
    if not isinstance(metadata, dict):
        raise MaterializationError("v5 evidence_metadata is missing")
    groups = metadata.get("repetition_groups")
    conflicts = metadata.get("unresolved_conflicts")
    if not isinstance(groups, list) or not isinstance(conflicts, list):
        raise MaterializationError("v5 repetition/conflict metadata must be lists")
    manifest_ids = changeset.get("frozen_record_ids_in_manifest_order")
    if not isinstance(manifest_ids, list) or len(manifest_ids) != len(set(manifest_ids)):
        raise MaterializationError("v5 frozen record order is invalid")
    manifest_set = set(manifest_ids)
    group_ids: set[str] = set()
    for group in groups:
        if not isinstance(group, dict):
            raise MaterializationError("repetition group must be an object")
        group_id = group.get("group_id")
        statement = group.get("statement")
        record_ids = group.get("record_ids")
        if (
            not isinstance(group_id, str)
            or not group_id
            or group_id in group_ids
            or not isinstance(statement, str)
            or not statement.strip()
            or not isinstance(record_ids, list)
            or len(record_ids) < 2
            or len(record_ids) != len(set(record_ids))
            or any(record_id not in evidence for record_id in record_ids)
            or not set(record_ids).issubset(manifest_set)
        ):
            raise MaterializationError("repetition group is invalid")
        group_ids.add(group_id)
        if group.get("occurrence_count") != len(record_ids):
            raise MaterializationError("repetition occurrence_count mismatch")
        record_id_set = set(record_ids)
        manifest_group_order = [
            record_id for record_id in manifest_ids if record_id in record_id_set
        ]
        if record_ids != manifest_group_order:
            raise MaterializationError("repetition record IDs are not in manifest order")
        if (
            group.get("first_record_id") != record_ids[0]
            or group.get("latest_record_id") != record_ids[-1]
        ):
            raise MaterializationError("repetition first/latest record mismatch")
    for conflict in conflicts:
        if not isinstance(conflict, dict):
            raise MaterializationError("unresolved conflict must be an object")
        record_ids = conflict.get("record_ids")
        if (
            not isinstance(conflict.get("statement"), str)
            or not conflict["statement"].strip()
            or not isinstance(record_ids, list)
            or len(record_ids) < 2
            or len(record_ids) != len(set(record_ids))
            or any(record_id not in evidence for record_id in record_ids)
        ):
            raise MaterializationError("unresolved conflict is invalid")


def _validate_allocation_binding(
    *,
    repo_root: Path,
    changeset: dict[str, Any],
    allocation: dict[str, Any],
    allocation_path: Path,
    allocation_raw: bytes,
    accepted_allocation_sha256: str,
    manifest_path: Path,
    manifest_raw: bytes,
    evidence_raw: bytes,
    manifest_ids: list[str],
    evidence: dict[str, dict[str, Any]],
    prior_wiki_tree_sha256: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if allocation.get("schema") != ALLOCATION_SCHEMA:
        raise MaterializationError("allocation schema mismatch")
    if allocation.get("status") != "accepted":
        raise MaterializationError("allocation status must be accepted")

    actual_allocation_sha = sha256_bytes(allocation_raw)
    accepted_allocation_sha = _require_sha(
        accepted_allocation_sha256, "accepted allocation SHA"
    )
    if actual_allocation_sha != accepted_allocation_sha:
        raise MaterializationError("accepted allocation SHA mismatch")

    input_value = changeset["input"]
    allocation_repo_path = _repo_relative_path(
        repo_root, allocation_path, "allocation path"
    )
    if input_value.get("allocation_path") != allocation_repo_path:
        raise MaterializationError("allocation path does not match changeset input")
    if _require_sha(
        input_value.get("allocation_sha256"), "changeset allocation SHA"
    ) != actual_allocation_sha:
        raise MaterializationError("allocation SHA does not match changeset input")

    manifest_repo_path = _repo_relative_path(repo_root, manifest_path, "manifest path")
    manifest_sha = sha256_bytes(manifest_raw)
    evidence_sha = sha256_bytes(evidence_raw)
    if allocation.get("batch_id") != changeset.get("batch_id"):
        raise MaterializationError("allocation and changeset batch_id mismatch")
    if allocation.get("manifest_path") != manifest_repo_path:
        raise MaterializationError("allocation manifest path mismatch")
    if _require_sha(allocation.get("manifest_sha256"), "allocation manifest SHA") != manifest_sha:
        raise MaterializationError("allocation manifest SHA mismatch")
    if _require_sha(
        allocation.get("evidence_records_sha256"), "allocation evidence records SHA"
    ) != evidence_sha:
        raise MaterializationError("allocation evidence records SHA mismatch")
    if _require_sha(
        allocation.get("prior_wiki_tree_sha256"), "allocation prior Wiki tree SHA"
    ) != prior_wiki_tree_sha256:
        raise MaterializationError("allocation prior Wiki tree SHA mismatch")

    pages = allocation.get("pages")
    if not isinstance(pages, list):
        raise MaterializationError("allocation pages must be a list")
    page_map: dict[str, dict[str, Any]] = {}
    for page in pages:
        if not isinstance(page, dict):
            raise MaterializationError("allocation page must be an object")
        operation = page.get("operation")
        if operation not in SEMANTIC_PAGE_OPERATIONS:
            raise MaterializationError("allocation page operation is invalid")
        page_path = page.get("page_path")
        relative = _page_relative_path(page_path)
        canonical_path = f"current/wiki/{relative}"
        if page_path != canonical_path:
            raise MaterializationError("allocation page path is not canonical")
        page_type = page.get("page_type")
        if (
            not isinstance(page_type, str)
            or not page_type.strip()
            or page_type == "index"
            or relative == "index.md"
        ):
            raise MaterializationError("allocation cannot contain index pages")
        h1 = page.get("h1")
        if not isinstance(h1, str) or not h1.strip():
            raise MaterializationError("allocation page H1 must be non-empty")
        split_group_id = page.get("split_group_id")
        if split_group_id is not None and (
            not isinstance(split_group_id, str) or not split_group_id.strip()
        ):
            raise MaterializationError("allocation split_group_id must be non-empty")
        if canonical_path in page_map:
            raise MaterializationError(f"duplicate allocation page path: {canonical_path}")
        page_map[canonical_path] = {
            "operation": operation,
            "page_path": canonical_path,
            "page_type": page_type,
            "h1": h1,
            "split_group_id": split_group_id,
        }

    records = allocation.get("records")
    if not isinstance(records, list) or len(records) != len(manifest_ids):
        raise MaterializationError("allocation record count does not match manifest records")
    record_map: dict[str, dict[str, Any]] = {}
    for expected_record_id, record in zip(manifest_ids, records, strict=True):
        if not isinstance(record, dict):
            raise MaterializationError("allocation record must be an object")
        record_id = record.get("record_id")
        if record_id != expected_record_id:
            raise MaterializationError("allocation records are not in exact manifest order")
        if record.get("source_address") != evidence[record_id]["source_address"]:
            raise MaterializationError(f"allocation source address mismatch for {record_id}")
        for field in ("source_owner", "source_scope", "reason"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise MaterializationError(
                    f"allocation {field} is missing for {record_id}"
                )
        disposition = record.get("disposition")
        target_page_path = record.get("target_page_path")
        if disposition not in {"used", "reject", "skipped"}:
            raise MaterializationError(
                f"allocation disposition is invalid for {record_id}"
            )
        if disposition == "used":
            if not isinstance(target_page_path, str) or target_page_path not in page_map:
                raise MaterializationError(
                    f"allocation used target is invalid for {record_id}"
                )
        elif target_page_path is not None:
            raise MaterializationError(
                f"allocation {disposition} record cannot have a target page"
            )
        record_map[record_id] = record
    return page_map, record_map


def _operation_page_contract(
    operation: dict[str, Any],
    before: dict[str, bytes],
    evidence: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    kind = operation.get("operation")
    page_path = operation.get("page_path")
    relative = _page_relative_path(page_path)
    canonical_path = f"current/wiki/{relative}"
    if page_path != canonical_path:
        raise MaterializationError("changeset page path is not canonical")
    page_type = operation.get("page_type")
    if not isinstance(page_type, str) or not page_type.strip() or page_type == "index":
        raise MaterializationError(f"semantic page type is invalid for {canonical_path}")
    if kind in CONTENT_OPERATIONS:
        content = operation.get("proposed_content")
        if not isinstance(content, str):  # pragma: no cover - checked by apply
            raise MaterializationError(f"proposed content is missing for {relative}")
    else:
        if relative not in before:
            raise MaterializationError(f"{kind} target does not exist: {relative}")
        content = before[relative].decode("utf-8")
    h1 = _page_h1(content, relative)
    _validate_page_type(content, page_type, relative)
    if kind not in CONTENT_OPERATIONS:
        _validate_claims(operation, h1, evidence)
    return {
        "operation": kind,
        "page_path": canonical_path,
        "page_type": page_type,
        "h1": h1,
        "split_group_id": operation.get("split_group_id"),
    }


def _validate_allocation_against_changeset(
    *,
    page_map: dict[str, dict[str, Any]],
    record_map: dict[str, dict[str, Any]],
    operations: list[dict[str, Any]],
    coverage: list[dict[str, Any]],
    before: dict[str, bytes],
    evidence: dict[str, dict[str, Any]],
) -> None:
    operation_page_map: dict[str, dict[str, Any]] = {}
    semantic_occurrences: dict[str, list[str]] = collections.defaultdict(list)
    reject_occurrences: collections.Counter[str] = collections.Counter()
    claim_support_by_page: dict[str, set[str]] = collections.defaultdict(set)

    for operation in operations:
        kind = operation.get("operation")
        if kind == "reject":
            reject_occurrences.update(operation.get("record_ids", []))
            continue
        if kind not in SEMANTIC_PAGE_OPERATIONS:
            continue
        page_type = operation.get("page_type")
        page_path = operation.get("page_path")
        relative = _page_relative_path(page_path)
        canonical_path = f"current/wiki/{relative}"
        for record_id in operation.get("record_ids", []):
            if record_id in record_map:
                semantic_occurrences[record_id].append(canonical_path)
        for claim in operation.get("material_claims", []):
            for record_id in claim.get("supporting_record_ids", []):
                if record_id in record_map:
                    claim_support_by_page[canonical_path].add(record_id)
        if page_type == "index":
            continue
        contract = _operation_page_contract(operation, before, evidence)
        if canonical_path in operation_page_map:
            raise MaterializationError(
                f"duplicate semantic changeset page path: {canonical_path}"
            )
        operation_page_map[canonical_path] = contract

    if operation_page_map != page_map:
        raise MaterializationError("allocation page map does not match changeset operations")

    coverage_by_id = {item["record_id"]: item for item in coverage}
    for record_id, allocation_record in record_map.items():
        disposition = allocation_record["disposition"]
        target = allocation_record["target_page_path"]
        coverage_item = coverage_by_id[record_id]
        if coverage_item.get("disposition") != disposition:
            raise MaterializationError(
                f"allocation disposition does not match coverage for {record_id}"
            )
        coverage_path = coverage_item.get("page_path")
        if disposition == "used":
            if coverage_path != target:
                raise MaterializationError(
                    f"allocation target mismatch in coverage for {record_id}"
                )
            if semantic_occurrences[record_id] != [target]:
                raise MaterializationError(
                    f"allocation target mismatch for {record_id}"
                )
            if reject_occurrences[record_id] != 0:
                raise MaterializationError(
                    f"allocated used record appears in reject operation: {record_id}"
                )
            if record_id not in claim_support_by_page[target]:
                raise MaterializationError(
                    f"allocated used record has no material claim on target: {record_id}"
                )
        else:
            if coverage_path is not None:
                raise MaterializationError(
                    f"{disposition} coverage cannot have a page path for {record_id}"
                )
            if semantic_occurrences[record_id]:
                raise MaterializationError(
                    f"allocated {disposition} record appears in a semantic operation: {record_id}"
                )
            expected_reject_occurrences = 1 if disposition == "reject" else 0
            if reject_occurrences[record_id] != expected_reject_occurrences:
                raise MaterializationError(
                    f"allocation {disposition} operation mismatch for {record_id}"
                )


def _validate_coverage(
    changeset: dict[str, Any],
    manifest_ids: list[str],
    evidence: dict[str, dict[str, Any]],
    operations: list[dict[str, Any]],
    prior_cited_ids: set[str],
) -> tuple[list[dict[str, Any]], collections.Counter[str]]:
    frozen_ids = changeset.get("frozen_record_ids_in_manifest_order")
    if frozen_ids != manifest_ids:
        raise MaterializationError("frozen record IDs are not in exact manifest order")
    if any(record_id not in evidence for record_id in manifest_ids):
        raise MaterializationError("manifest record is missing from frozen evidence")
    coverage = changeset.get("coverage")
    if not isinstance(coverage, list) or len(coverage) != len(manifest_ids):
        raise MaterializationError("coverage count does not match manifest records")
    coverage_ids: list[str] = []
    counts: collections.Counter[str] = collections.Counter()
    manifest_set = set(manifest_ids)
    semantic_ids: set[str] = set()
    claim_supported_ids: set[str] = set()
    rejected_ids: set[str] = set()
    for operation in operations:
        operation_ids = set(operation.get("record_ids", []))
        extra_ids = operation_ids - manifest_set
        if extra_ids - prior_cited_ids:
            raise MaterializationError(
                "operation uses evidence outside the batch and accepted prior Wiki"
            )
        kind = operation.get("operation")
        if kind in {"create", "update", "supersede", "no-change"}:
            semantic_ids.update(operation_ids & manifest_set)
            for claim in operation.get("material_claims", []):
                claim_supported_ids.update(
                    set(claim.get("supporting_record_ids", [])) & manifest_set
                )
        elif kind == "reject":
            if extra_ids:
                raise MaterializationError("reject operation cannot cite prior evidence")
            rejected_ids.update(operation_ids)

    if claim_supported_ids != semantic_ids:
        raise MaterializationError(
            "semantic operation record_ids do not exactly match material claim support"
        )

    used_ids: set[str] = set()
    coverage_rejected_ids: set[str] = set()
    skipped_ids: set[str] = set()
    for item in coverage:
        if not isinstance(item, dict):
            raise MaterializationError("coverage item must be an object")
        record_id = item.get("record_id")
        disposition = item.get("disposition")
        reason = item.get("reason")
        if record_id not in manifest_ids or disposition not in {"used", "reject", "skipped"}:
            raise MaterializationError("coverage item has invalid record or disposition")
        if not isinstance(reason, str) or not reason.strip():
            raise MaterializationError(f"coverage reason is missing for {record_id}")
        if disposition == "used":
            used_ids.add(record_id)
        elif disposition == "reject":
            coverage_rejected_ids.add(record_id)
        else:
            skipped_ids.add(record_id)
        coverage_ids.append(record_id)
        counts[disposition] += 1
    if coverage_ids != manifest_ids:
        raise MaterializationError("coverage is not in exact manifest order")
    if semantic_ids != used_ids:
        raise MaterializationError(
            "used coverage does not exactly match semantic operation record_ids"
        )
    if rejected_ids != coverage_rejected_ids:
        raise MaterializationError(
            "reject coverage does not exactly match reject operation record_ids"
        )
    if skipped_ids & (semantic_ids | rejected_ids):  # pragma: no cover - exact sets guard it
        raise MaterializationError("skipped coverage record appears in an operation")
    return coverage, counts


def _validate_split_groups(operations: list[dict[str, Any]]) -> list[str]:
    groups: dict[str, list[str]] = collections.defaultdict(list)
    for operation in operations:
        group = operation.get("split_group_id")
        if group is None:
            continue
        if not isinstance(group, str) or not group.strip():
            raise MaterializationError("split_group_id must be a non-empty string")
        kind = operation.get("operation")
        if kind not in {"create", "update", "supersede"}:
            raise MaterializationError("split_group_id is allowed only on mutating page operations")
        groups[group].append(kind)
    for group, kinds in groups.items():
        sources = sum(kind in {"update", "supersede"} for kind in kinds)
        creates = kinds.count("create")
        if sources != 1 or creates < 1:
            raise MaterializationError(
                f"split_group_id {group!r} requires exactly one update|supersede and at least one create"
            )
    return sorted(groups)


def _apply_operations(
    before: dict[str, bytes],
    operations: list[dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    *,
    strict_v5: bool = False,
) -> tuple[dict[str, bytes], list[dict[str, Any]], collections.Counter[str]]:
    after = dict(before)
    targets: set[str] = set()
    materialized: list[dict[str, Any]] = []
    counts: collections.Counter[str] = collections.Counter()
    for operation in operations:
        if not isinstance(operation, dict):
            raise MaterializationError("operation must be an object")
        kind = operation.get("operation")
        if kind not in ALLOWED_OPERATIONS:
            raise MaterializationError(f"unsupported operation: {kind!r}")
        record_ids = operation.get("record_ids")
        if (
            not isinstance(record_ids, list)
            or len(record_ids) != len(set(record_ids))
            or any(record_id not in evidence for record_id in record_ids)
        ):
            raise MaterializationError(f"{kind} operation has invalid record_ids")
        counts[kind] += 1
        if kind not in MUTATING_OPERATIONS:
            if operation.get("proposed_content") is not None or operation.get("proposed_sha256") is not None:
                raise MaterializationError(f"{kind} operation cannot contain proposed content")
            if strict_v5 and kind == "no-change":
                relative = _page_relative_path(operation.get("page_path"))
                if relative not in before:
                    raise MaterializationError(
                        f"no-change target does not exist: {relative}"
                    )
                prior_sha = _require_sha(
                    operation.get("prior_sha256"), f"prior SHA for {relative}"
                )
                if sha256_bytes(before[relative]) != prior_sha:
                    raise MaterializationError(
                        f"prior SHA mismatch for {relative}"
                    )
                text = before[relative].decode("utf-8")
                page_type = operation.get("page_type")
                _validate_page_type(text, page_type, relative)
                _validate_v5_page_shape(text, str(page_type), str(operation.get("page_path")))
                _validate_claims(
                    operation,
                    _page_h1(text, relative),
                    evidence,
                    strict_v5=True,
                )
            continue

        relative = _page_relative_path(operation.get("page_path"))
        if relative in targets:
            raise MaterializationError(f"duplicate mutating page path: {relative}")
        targets.add(relative)
        prior_sha = operation.get("prior_sha256")
        if kind == "create":
            if relative in before or prior_sha is not None:
                raise MaterializationError(f"create target already exists or has prior SHA: {relative}")
        else:
            if relative not in before:
                raise MaterializationError(f"{kind} target does not exist: {relative}")
            expected_prior = _require_sha(prior_sha, f"prior SHA for {relative}")
            if sha256_bytes(before[relative]) != expected_prior:
                raise MaterializationError(f"prior SHA mismatch for {relative}")

        if kind == "supersede":
            if operation.get("proposed_content") is not None or operation.get("proposed_sha256") is not None:
                raise MaterializationError(f"supersede must delete without proposed content: {relative}")
            after.pop(relative)
            materialized.append(
                {
                    "operation": kind,
                    "page_path": f"current/wiki/{relative}",
                    "prior_sha256": prior_sha,
                    "materialized_sha256": None,
                    "utf8_bytes": 0,
                    "equal": True,
                }
            )
            continue

        content = operation.get("proposed_content")
        if not isinstance(content, str):
            raise MaterializationError(f"proposed content is missing for {relative}")
        try:
            raw = content.encode("utf-8")
        except UnicodeEncodeError as exc:  # pragma: no cover - Python strings are Unicode
            raise MaterializationError(f"proposed content is not UTF-8 for {relative}") from exc
        proposed_sha = _require_sha(operation.get("proposed_sha256"), f"proposed SHA for {relative}")
        if sha256_bytes(raw) != proposed_sha:
            raise MaterializationError(f"proposed SHA mismatch for {relative}")
        h1 = _page_h1(content, relative)
        _validate_page_type(content, operation.get("page_type"), relative)
        if strict_v5:
            _validate_v5_page_shape(
                content, str(operation.get("page_type")), str(operation.get("page_path"))
            )
        if operation.get("page_type") == "index":
            if operation.get("material_claims") != [] or record_ids != []:
                raise MaterializationError(
                    "index operation cannot contain material claims or record_ids"
                )
        else:
            _validate_claims(operation, h1, evidence, strict_v5=strict_v5)
        after[relative] = raw
        materialized.append(
            {
                "operation": kind,
                "page_path": f"current/wiki/{relative}",
                "prior_sha256": prior_sha,
                "proposed_sha256": proposed_sha,
                "materialized_sha256": proposed_sha,
                "utf8_bytes": len(raw),
                "equal": True,
            }
        )
    return after, materialized, counts


def _prior_cited_record_ids(
    repo_root: Path,
    wiki_root: Path,
    files: dict[str, bytes],
    evidence: dict[str, dict[str, Any]],
) -> set[str]:
    evidence_by_address = {
        record["source_address"]: record_id for record_id, record in evidence.items()
    }
    cited: set[str] = set()
    repo_root_resolved = repo_root.resolve()
    wiki_root_resolved = wiki_root.resolve(strict=False)
    for relative, raw in files.items():
        text = raw.decode("utf-8")
        for target in LINK_RE.findall(text):
            target_path, separator, anchor = target.partition("#")
            if not target_path or EXTERNAL_LINK_RE.match(target):
                continue
            final_page = wiki_root_resolved / relative
            normalized = Path(os.path.normpath(str(final_page.parent / target_path)))
            try:
                normalized.relative_to(wiki_root_resolved)
                continue
            except ValueError:
                pass
            try:
                repo_relative = normalized.relative_to(repo_root_resolved).as_posix()
            except ValueError:
                continue
            match = SOURCE_ANCHOR_RE.fullmatch(anchor) if separator else None
            if match is None:
                continue
            record_id = evidence_by_address.get(f"{repo_relative}:{match.group(1)}")
            if record_id is not None:
                cited.add(record_id)
    return cited


def _validate_links_and_content(
    repo_root: Path,
    wiki_root: Path,
    files: dict[str, bytes],
    evidence: dict[str, dict[str, Any]],
    operations: list[dict[str, Any]],
    source_targets: dict[str, str] | None = None,
) -> None:
    evidence_by_address = {
        record["source_address"]: record_id for record_id, record in evidence.items()
    }
    source_paths = {record["source_path"] for record in evidence.values()}
    operation_by_page = {
        _page_relative_path(operation["page_path"]): operation
        for operation in operations
        if operation.get("operation") in CONTENT_OPERATIONS
    }
    texts: dict[str, str] = {}
    internal_links_by_page: dict[str, list[str]] = {}
    repo_root_resolved = repo_root.resolve()
    wiki_root_resolved = wiki_root.resolve(strict=False)
    for relative, raw in files.items():
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MaterializationError(f"materialized page is not UTF-8: {relative}") from exc
        texts[relative] = text
        if "\\u0060" in text:
            raise MaterializationError(f"literal \\u0060 escape in {relative}")
        if re.search(r"(?m)^\s*>", text):
            raise MaterializationError(f"block quote is forbidden in {relative}")
        internal_links: list[str] = []
        source_record_ids: set[str] = set()
        for target in LINK_RE.findall(text):
            if EXTERNAL_LINK_RE.match(target) or target.startswith("www."):
                raise MaterializationError(f"external link is forbidden in {relative}: {target}")
            if any(character.isspace() for character in target.split("#", 1)[0]):
                raise MaterializationError(f"unsupported Markdown link target in {relative}: {target}")
            target_path, separator, anchor = target.partition("#")
            if not target_path:
                continue
            final_page = wiki_root_resolved / relative
            normalized = Path(os.path.normpath(str(final_page.parent / target_path)))
            try:
                wiki_relative = normalized.relative_to(wiki_root_resolved).as_posix()
            except ValueError:
                try:
                    repo_relative = normalized.relative_to(repo_root_resolved).as_posix()
                except ValueError as exc:
                    raise MaterializationError(
                        f"link escaped repository root in {relative}: {target}"
                    ) from exc
                if repo_relative not in source_paths:
                    raise MaterializationError(
                        f"project-corpus link is forbidden in {relative}: {target}"
                    )
                match = SOURCE_ANCHOR_RE.fullmatch(anchor) if separator else None
                address = f"{repo_relative}:{match.group(1)}" if match else None
                record_id = evidence_by_address.get(address) if address else None
                if record_id is None:
                    raise MaterializationError(
                        f"source link is not an exact evidence address in {relative}: {target}"
                    )
                if (
                    source_targets is not None
                    and record_id in source_targets
                    and source_targets[record_id] != target
                ):
                    raise MaterializationError(
                        f"source link does not match frozen manifest target in {relative}: {target}"
                    )
                source_record_ids.add(record_id)
                continue
            if wiki_relative not in files:
                raise MaterializationError(f"broken internal Wiki link in {relative}: {target}")
            internal_links.append(wiki_relative)
        internal_links_by_page[relative] = internal_links
        operation = operation_by_page.get(relative)
        if operation is not None:
            expected_source_ids = set(operation["record_ids"])
            if source_record_ids != expected_source_ids:
                raise MaterializationError(
                    f"source links do not exactly match operation record_ids for {relative}"
                )

    if "index.md" not in files:
        raise MaterializationError("current Wiki has no index.md")
    expected_routes = sorted(path for path in files if path != "index.md")
    actual_routes = internal_links_by_page.get("index.md", [])
    if sorted(actual_routes) != expected_routes or len(actual_routes) != len(set(actual_routes)):
        raise MaterializationError("index routes do not exactly cover active Wiki pages")

    wiki_blob = "\n".join(texts.values())
    for record in evidence.values():
        quote = record["quote"]
        if len(quote) >= QUOTE_COPY_MIN_CHARS and quote in wiki_blob:
            raise MaterializationError(
                f"full quote copy is forbidden: {record['record_id']}"
            )


def _build_receipt(
    *,
    changeset: dict[str, Any],
    changeset_path: Path,
    changeset_sha: str,
    manifest: dict[str, Any],
    manifest_path: Path,
    manifest_sha: str,
    evidence_sha: str,
    evidence: dict[str, dict[str, Any]],
    manifest_ids: list[str],
    before_sha: str,
    before_entries: list[dict[str, Any]],
    after_sha: str,
    after_entries: list[dict[str, Any]],
    materialized: list[dict[str, Any]],
    operation_counts: collections.Counter[str],
    coverage_counts: collections.Counter[str],
    split_groups: list[str],
    repo_root: Path,
    files: dict[str, bytes],
    receipt_schema: str,
    allocation_path: Path | None = None,
    allocation_sha256: str | None = None,
) -> dict[str, Any]:
    input_value = changeset["input"]
    counts = manifest.get("counts", {})
    source_snapshot = {
        "changeset_path": changeset_path.resolve().relative_to(repo_root.resolve()).as_posix(),
        "changeset_sha256": changeset_sha,
        "manifest_path": manifest_path.resolve().relative_to(repo_root.resolve()).as_posix(),
        "manifest_sha256": manifest_sha,
        "corpus_commit": input_value.get("corpus_commit"),
        "evidence_commit": input_value.get("evidence_commit"),
        "evidence_records_sha256": evidence_sha,
        "time_boundary_utc": input_value.get("time_boundary_utc"),
    }
    if allocation_path is not None:
        source_snapshot["allocation_path"] = (
            allocation_path.resolve().relative_to(repo_root.resolve()).as_posix()
        )
        source_snapshot["allocation_sha256"] = allocation_sha256
    for field in (
        "prompt_path",
        "prompt_sha256",
        "materializer_path",
        "materializer_sha256",
        "output_contract_sha256",
    ):
        if field in input_value:
            source_snapshot[field] = input_value[field]
    receipt = {
        "schema": receipt_schema,
        "status": "materialized-candidate",
        "batch_id": changeset.get("batch_id"),
        "previous_batch_id": changeset.get("previous_batch_id"),
        "source_snapshot": source_snapshot,
        "tree_digest": {
            "algorithm": TREE_ALGORITHM,
            "before": {
                "wiki_root": changeset["prior_checkpoint"]["wiki_root"],
                "sha256": before_sha,
                "entries": before_entries,
            },
            "after": {
                "wiki_root": changeset["prior_checkpoint"]["wiki_root"],
                "sha256": after_sha,
                "entries": after_entries,
            },
        },
        "active_page_set": {
            "count": len(after_entries),
            "paths": [f"current/wiki/{entry['path']}" for entry in after_entries],
            "materialized_operations": materialized,
            "unchanged_prior_pages": [
                f"current/wiki/{entry['path']}"
                for entry in before_entries
                if entry["path"]
                not in {
                    Path(item["page_path"]).relative_to("current/wiki").as_posix()
                    for item in materialized
                }
            ],
        },
        "operations": {
            operation: operation_counts[operation]
            for operation in sorted(ALLOWED_OPERATIONS)
        },
        "split_groups": split_groups,
        "coverage": {
            "total": len(manifest_ids),
            "used": coverage_counts["used"],
            "reject": coverage_counts["reject"],
            "skipped": coverage_counts["skipped"],
            "record_ids_in_manifest_order": manifest_ids,
        },
        "source_addresses": [
            {
                "record_id": record_id,
                "address": evidence[record_id]["source_address"],
                "source_path": evidence[record_id]["source_path"],
                "source_line": evidence[record_id]["source_line"],
            }
            for record_id in manifest_ids
        ],
        "execution": {
            "semantic_model": changeset.get("model"),
            "semantic_thinking": changeset.get("thinking"),
            "materializer": "deterministic-python",
            "subagents": False,
            "worktree": False,
            "git_commit": False,
            "git_push": False,
        },
        "diagnostics": {
            "evaluation": "diagnostic-only; no size target or semantic gate evaluated",
            "source_quotes": {
                "chars": counts.get("source_quote_chars"),
                "utf8_bytes": counts.get("source_quote_utf8_bytes"),
            },
            "current_wiki": {
                "chars": sum(len(raw.decode("utf-8")) for raw in files.values()),
                "utf8_bytes": sum(len(raw) for raw in files.values()),
            },
        },
        "gaps": changeset.get("gaps", []),
        "evidence_metadata": changeset.get("evidence_metadata"),
        "content_exclusions": {"hidden_reasoning": True, "full_quotes": True},
    }
    return receipt


def _write_staged_tree(root: Path, files: dict[str, bytes]) -> None:
    for relative, raw in sorted(files.items()):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def _commit_materialization(
    wiki_root: Path,
    receipt_path: Path,
    files: dict[str, bytes],
    receipt_raw: bytes,
    expected_after_sha: str,
) -> None:
    if receipt_path.exists() or receipt_path.is_symlink():
        raise MaterializationError(f"receipt target already exists: {receipt_path}")
    if not receipt_path.parent.is_dir() or receipt_path.parent.is_symlink():
        raise MaterializationError(f"receipt parent is not a regular directory: {receipt_path.parent}")
    stage = Path(
        tempfile.mkdtemp(prefix=f".{wiki_root.name}.stage-", dir=wiki_root.parent)
    )
    backup = wiki_root.parent / f".{wiki_root.name}.backup-{uuid.uuid4().hex}"
    receipt_temp = receipt_path.parent / f".{receipt_path.name}.tmp-{uuid.uuid4().hex}"
    old_moved = False
    new_moved = False
    receipt_moved = False
    try:
        _write_staged_tree(stage, files)
        staged_sha, _ = tree_digest(stage)
        if staged_sha != expected_after_sha:
            raise MaterializationError("staged tree digest mismatch")
        receipt_temp.write_bytes(receipt_raw)
        os.replace(wiki_root, backup)
        old_moved = True
        os.replace(stage, wiki_root)
        new_moved = True
        os.replace(receipt_temp, receipt_path)
        receipt_moved = True
        final_sha, _ = tree_digest(wiki_root)
        if final_sha != expected_after_sha:
            raise MaterializationError("materialized tree digest mismatch")
        shutil.rmtree(backup)
        old_moved = False
    except Exception:
        if receipt_moved and receipt_path.exists():
            receipt_path.unlink()
        elif receipt_temp.exists():
            receipt_temp.unlink()
        if new_moved and wiki_root.exists():
            shutil.rmtree(wiki_root)
        if old_moved and backup.exists():
            os.replace(backup, wiki_root)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
        if receipt_temp.exists():
            receipt_temp.unlink()
        if backup.exists() and not old_moved:
            shutil.rmtree(backup)


def materialize(
    *,
    repo_root: Path,
    changeset_path: Path,
    manifest_path: Path,
    evidence_records_path: Path,
    wiki_root: Path,
    receipt_path: Path,
    accepted_changeset_sha256: str,
    allocation_path: Path | None = None,
    accepted_allocation_sha256: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Validate and optionally materialize one accepted chronological changeset."""

    repo_root = Path(os.path.abspath(repo_root))
    if not repo_root.is_dir() or repo_root.is_symlink():
        raise MaterializationError(f"repository root is not a regular directory: {repo_root}")
    for path, label in (
        (changeset_path, "changeset path"),
        (manifest_path, "manifest path"),
        (evidence_records_path, "evidence path"),
        (wiki_root, "Wiki root"),
        (receipt_path, "receipt path"),
    ):
        _inside(repo_root, path, label)
        _assert_existing_components_not_symlinks(repo_root, path, label)
    if allocation_path is not None:
        _inside(repo_root, allocation_path, "allocation path")
        _assert_existing_components_not_symlinks(
            repo_root, allocation_path, "allocation path"
        )

    changeset, changeset_raw = _read_json(changeset_path, "changeset")
    accepted_sha = _require_sha(
        accepted_changeset_sha256, "accepted changeset SHA"
    )
    actual_changeset_sha = sha256_bytes(changeset_raw)
    if actual_changeset_sha != accepted_sha:
        raise MaterializationError("accepted changeset SHA mismatch")
    changeset_schema = changeset.get("schema")
    if changeset_schema == CHANGESET_SCHEMA_V3:
        if changeset.get("batch_id") != "batch-003":
            raise MaterializationError("v3 changeset is supported only for batch-003")
        if allocation_path is not None or accepted_allocation_sha256 is not None:
            raise MaterializationError("v3 changeset cannot use allocation inputs")
        receipt_schema = RECEIPT_SCHEMA_V3
    elif changeset_schema == CHANGESET_SCHEMA_V4:
        if allocation_path is None:
            raise MaterializationError("v4 changeset requires allocation_path")
        if accepted_allocation_sha256 is None:
            raise MaterializationError(
                "v4 changeset requires accepted_allocation_sha256"
            )
        receipt_schema = RECEIPT_SCHEMA_V4
    elif changeset_schema == CHANGESET_SCHEMA_V5:
        if allocation_path is not None or accepted_allocation_sha256 is not None:
            raise MaterializationError("v5 changeset cannot use allocation inputs")
        receipt_schema = RECEIPT_SCHEMA_V5
    else:
        raise MaterializationError("changeset schema mismatch")
    status = changeset.get("status")
    if changeset.get("phase") != "semantic-draft" or status not in {
        "candidate",
        "accepted",
    }:
        raise MaterializationError("changeset is not a semantic draft candidate")
    if not dry_run and status != "accepted":
        raise MaterializationError(
            "candidate changeset cannot be materialized before acceptance"
        )
    allowed = changeset.get("allowed_operations")
    if not isinstance(allowed, list) or set(allowed) != ALLOWED_OPERATIONS:
        raise MaterializationError("changeset allowed_operations mismatch")

    manifest, manifest_raw = _read_json(manifest_path, "batch manifest")
    evidence, evidence_raw = _read_records(evidence_records_path)
    _validate_input_binding(
        repo_root,
        changeset,
        manifest_path,
        manifest_raw,
        evidence_records_path,
        evidence_raw,
    )
    manifest_ids = _manifest_record_ids(manifest)
    if manifest.get("batch_id") != changeset.get("batch_id"):
        raise MaterializationError("manifest and changeset batch_id mismatch")
    input_value = changeset["input"]
    for field in ("corpus_commit", "evidence_commit", "time_boundary_utc"):
        if input_value.get(field) != manifest.get(field):
            raise MaterializationError(f"manifest and changeset {field} mismatch")

    expected_wiki_root = _inside(
        repo_root,
        repo_root / str(changeset.get("prior_checkpoint", {}).get("wiki_root", "")),
        "prior Wiki root",
    )
    if wiki_root.resolve() != expected_wiki_root:
        raise MaterializationError("Wiki root does not match prior checkpoint")
    before_files = _wiki_files(wiki_root)
    prior_cited_ids = _prior_cited_record_ids(
        repo_root, wiki_root, before_files, evidence
    )
    before_sha, before_entries = _tree_from_files(before_files)
    expected_before = _require_sha(
        changeset.get("prior_checkpoint", {}).get("wiki_tree_sha256_target"),
        "prior tree SHA",
    )
    if before_sha != expected_before:
        raise MaterializationError("prior Wiki tree SHA mismatch")

    source_targets: dict[str, str] | None = None
    if changeset_schema == CHANGESET_SCHEMA_V5:
        source_targets = _validate_v5_bindings(
            repo_root=repo_root,
            changeset=changeset,
            changeset_path=changeset_path,
            manifest=manifest,
            manifest_path=manifest_path,
            manifest_raw=manifest_raw,
            before_sha=before_sha,
        )
        _validate_v5_evidence_metadata(changeset, evidence)

    allocation_page_map: dict[str, dict[str, Any]] | None = None
    allocation_record_map: dict[str, dict[str, Any]] | None = None
    actual_allocation_sha: str | None = None
    if changeset_schema == CHANGESET_SCHEMA_V4:
        if allocation_path is None or accepted_allocation_sha256 is None:  # pragma: no cover
            raise MaterializationError("v4 allocation inputs are missing")
        allocation, allocation_raw = _read_json(allocation_path, "allocation")
        actual_allocation_sha = sha256_bytes(allocation_raw)
        allocation_page_map, allocation_record_map = _validate_allocation_binding(
            repo_root=repo_root,
            changeset=changeset,
            allocation=allocation,
            allocation_path=allocation_path,
            allocation_raw=allocation_raw,
            accepted_allocation_sha256=accepted_allocation_sha256,
            manifest_path=manifest_path,
            manifest_raw=manifest_raw,
            evidence_raw=evidence_raw,
            manifest_ids=manifest_ids,
            evidence=evidence,
            prior_wiki_tree_sha256=before_sha,
        )

    operations = changeset.get("operations")
    if not isinstance(operations, list) or not operations:
        raise MaterializationError("changeset operations must be a non-empty list")
    split_groups = _validate_split_groups(operations)
    after_files, materialized, operation_counts = _apply_operations(
        before_files,
        operations,
        evidence,
        strict_v5=changeset_schema == CHANGESET_SCHEMA_V5,
    )
    coverage, coverage_counts = _validate_coverage(
        changeset, manifest_ids, evidence, operations, prior_cited_ids
    )
    if allocation_page_map is not None and allocation_record_map is not None:
        _validate_allocation_against_changeset(
            page_map=allocation_page_map,
            record_map=allocation_record_map,
            operations=operations,
            coverage=coverage,
            before=before_files,
            evidence=evidence,
        )
    _validate_links_and_content(
        repo_root,
        wiki_root,
        after_files,
        evidence,
        operations,
        source_targets=source_targets,
    )
    after_sha, after_entries = _tree_from_files(after_files)

    receipt = _build_receipt(
        changeset=changeset,
        changeset_path=changeset_path,
        changeset_sha=actual_changeset_sha,
        manifest=manifest,
        manifest_path=manifest_path,
        manifest_sha=sha256_bytes(manifest_raw),
        evidence_sha=sha256_bytes(evidence_raw),
        evidence=evidence,
        manifest_ids=manifest_ids,
        before_sha=before_sha,
        before_entries=before_entries,
        after_sha=after_sha,
        after_entries=after_entries,
        materialized=materialized,
        operation_counts=operation_counts,
        coverage_counts=coverage_counts,
        split_groups=split_groups,
        repo_root=repo_root,
        files=after_files,
        receipt_schema=receipt_schema,
        allocation_path=allocation_path,
        allocation_sha256=actual_allocation_sha,
    )
    receipt_raw = json_bytes(receipt)
    if not dry_run:
        _commit_materialization(
            wiki_root, receipt_path, after_files, receipt_raw, after_sha
        )
    return receipt


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministically materialize one accepted chronological Wiki changeset."
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--changeset", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence-records", type=Path, required=True)
    parser.add_argument("--wiki-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--accepted-changeset-sha256", required=True)
    parser.add_argument("--allocation", type=Path)
    parser.add_argument("--accepted-allocation-sha256")
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        receipt = materialize(
            repo_root=args.repo_root,
            changeset_path=args.changeset,
            manifest_path=args.manifest,
            evidence_records_path=args.evidence_records,
            wiki_root=args.wiki_root,
            receipt_path=args.receipt,
            accepted_changeset_sha256=args.accepted_changeset_sha256,
            allocation_path=args.allocation,
            accepted_allocation_sha256=args.accepted_allocation_sha256,
            dry_run=args.check_only,
        )
    except MaterializationError as exc:
        print(f"materialize_chronological_changeset: {exc}", file=os.sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check-only" if args.check_only else "materialized",
                "batch_id": receipt["batch_id"],
                "after_tree_sha256": receipt["tree_digest"]["after"]["sha256"],
                "active_page_count": receipt["active_page_set"]["count"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
