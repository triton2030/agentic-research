#!/usr/bin/env python3
"""Build one prompt-bound owner-attributed Wiki batch and its preflight receipt."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import build_chronological_batch as chronological
import materialize_chronological_changeset as materializer


class OwnerWikiBatchError(ValueError):
    """Raised when a clean-chain batch cannot be frozen exactly."""


MANIFEST_SCHEMA = "openviking-chat-recall/chronological-batch-input.v4"
CHANGESET_SCHEMA = "openviking-chat-recall/chronological-wiki-changeset.v5"
RECEIPT_SCHEMA = "openviking-chat-recall/chronological-wiki-receipt.v5"
PREFLIGHT_SCHEMA = "openviking-chat-recall/wiki-writer-preflight.v1"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _read_regular(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise OwnerWikiBatchError(f"{label} is not a regular file: {path}")
    return path.read_bytes()


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = _read_regular(path, label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OwnerWikiBatchError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise OwnerWikiBatchError(f"{label} must contain a JSON object")
    return value, raw


def _relative(repo_root: Path, path: Path, label: str) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise OwnerWikiBatchError(f"{label} escaped repository root: {path}") from exc


def _verify_commit_file(
    repo_root: Path, commit: str, path: Path, expected: bytes, label: str
) -> None:
    if not FULL_SHA_RE.fullmatch(commit):
        raise OwnerWikiBatchError(f"{label} commit must be a full SHA")
    relative = _relative(repo_root, path, label)
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{commit}:{relative}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise OwnerWikiBatchError(f"commit cannot prove {label}") from exc
    if result.stdout != expected:
        raise OwnerWikiBatchError(f"commit has different {label} bytes")


def output_contract() -> dict[str, Any]:
    """Return the complete mechanical envelope the semantic writer must emit."""

    return {
        "top_level_required": [
            "schema",
            "phase",
            "status",
            "batch_id",
            "previous_batch_id",
            "model",
            "thinking",
            "input",
            "prior_checkpoint",
            "allowed_operations",
            "frozen_record_ids_in_manifest_order",
            "operations",
            "coverage",
            "evidence_metadata",
            "gaps",
        ],
        "fixed_values": {
            "schema": CHANGESET_SCHEMA,
            "phase": "semantic-draft",
            "status": "candidate",
            "model": "gpt-5.6-luna",
            "thinking": "max",
            "allowed_operations": [
                "create",
                "update",
                "supersede",
                "no-change",
                "reject",
            ],
        },
        "input_echoes": [
            "manifest_path",
            "manifest_sha256",
            "evidence_records_path",
            "evidence_records_sha256",
            "corpus_commit",
            "evidence_commit",
            "time_boundary_utc",
            "prompt_path",
            "prompt_sha256",
            "materializer_path",
            "materializer_sha256",
            "output_contract_sha256",
        ],
        "operation": {
            "common": ["operation", "record_ids"],
            "create_update": [
                "page_path",
                "page_type",
                "prior_sha256",
                "proposed_content",
                "proposed_sha256",
                "material_claims",
                "prior_page_review",
            ],
            "no_change": [
                "page_path",
                "page_type",
                "prior_sha256",
                "material_claims",
                "prior_page_review",
            ],
            "supersede": [
                "page_path",
                "page_type",
                "prior_sha256",
                "material_claims",
                "prior_page_review",
            ],
            "reject": ["operation", "record_ids"],
            "split_encoding": (
                "exactly one update|supersede and one or more create operations "
                "share one non-empty split_group_id"
            ),
        },
        "material_claim": [
            "claim_id",
            "statement",
            "epistemic_kind",
            "supporting_record_ids",
            "page_fit.page_question",
            "page_fit.answering_record_ids",
            "page_fit.reason",
        ],
        "coverage": {
            "order": "exact frozen_record_ids_in_manifest_order",
            "fields": ["record_id", "disposition", "reason"],
            "dispositions": ["used", "reject", "skipped"],
            "used_adds": ["page_path"],
        },
        "evidence_metadata": {
            "required": ["repetition_groups", "unresolved_conflicts"],
            "repetition_group": [
                "group_id",
                "statement",
                "record_ids",
                "occurrence_count",
                "first_record_id",
                "latest_record_id",
            ],
            "unresolved_conflict": ["statement", "record_ids"],
        },
        "index": {
            "page_path": "current/wiki/index.md",
            "page_type": "index",
            "record_ids": [],
            "material_claims": [],
        },
        "source_links": "copy record_bindings[].source_link_target exactly",
        "candidate_only": True,
    }


def _source_link_target(
    repo_root: Path, wiki_root: Path, source_path: str, source_line: int
) -> str:
    page_parent = wiki_root / "entity"
    target = os.path.relpath(repo_root / source_path, start=page_parent).replace(
        os.sep, "/"
    )
    if any(character.isspace() for character in target):
        raise OwnerWikiBatchError(f"source link contains whitespace: {source_path}")
    return f"{target}#L{source_line}"


def _write_output(path: Path, raw: bytes, *, check: bool) -> None:
    if check:
        if path.is_symlink() or not path.is_file() or path.read_bytes() != raw:
            raise OwnerWikiBatchError(f"output is missing or stale: {path}")
        return
    if path.exists() or path.is_symlink():
        raise OwnerWikiBatchError(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def build_batch(
    *,
    repo_root: Path,
    batch_number: int,
    frozen_manifest_path: Path,
    evidence_records_path: Path,
    evidence_commit: str,
    prompt_path: Path,
    materializer_path: Path,
    wiki_root: Path,
    manifest_path: Path,
    changeset_path: Path,
    preflight_path: Path,
    previous_manifest_path: Path | None = None,
    previous_receipt_path: Path | None = None,
    accepted_prior_commit: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if batch_number < 1:
        raise OwnerWikiBatchError("batch number must be positive")
    if not FULL_SHA_RE.fullmatch(evidence_commit):
        raise OwnerWikiBatchError("evidence commit must be a full SHA")
    if wiki_root.is_symlink() or not wiki_root.is_dir():
        raise OwnerWikiBatchError("Wiki root must be an existing regular directory")

    ordered, no_record_paths, metadata = chronological.load_ordered_inventory(
        frozen_manifest_path, evidence_records_path
    )
    start = (batch_number - 1) * chronological.BATCH_SIZE
    selected = ordered[start : start + chronological.BATCH_SIZE]
    if not selected:
        raise OwnerWikiBatchError("no record-bearing holders remain for this batch")
    batch_id = f"batch-{batch_number:03d}"
    previous_batch_id = f"batch-{batch_number - 1:03d}" if batch_number > 1 else None

    prior_sha, prior_entries = materializer.tree_digest(wiki_root)
    source_snapshot: dict[str, Any] = {
        "frozen_manifest_path": _relative(
            repo_root, frozen_manifest_path, "frozen manifest"
        ),
        "frozen_manifest_sha256": metadata["frozen_manifest_sha256"],
        "evidence_records_path": _relative(
            repo_root, evidence_records_path, "evidence records"
        ),
        "evidence_records_sha256": metadata["evidence_records_sha256"],
    }
    if batch_number == 1:
        if previous_manifest_path or previous_receipt_path or accepted_prior_commit:
            raise OwnerWikiBatchError("batch-001 cannot have a previous checkpoint")
        if prior_entries:
            raise OwnerWikiBatchError("batch-001 clean Wiki root must be empty")
    else:
        if not previous_manifest_path or not previous_receipt_path or not accepted_prior_commit:
            raise OwnerWikiBatchError("later batches require the accepted previous checkpoint")
        previous_manifest, previous_manifest_raw = _read_json(
            previous_manifest_path, "previous manifest"
        )
        previous_receipt, previous_receipt_raw = _read_json(
            previous_receipt_path, "previous receipt"
        )
        if (
            previous_manifest.get("schema") != MANIFEST_SCHEMA
            or previous_manifest.get("batch_id") != previous_batch_id
            or previous_receipt.get("schema") != RECEIPT_SCHEMA
            or previous_receipt.get("batch_id") != previous_batch_id
        ):
            raise OwnerWikiBatchError("previous checkpoint schema or batch mismatch")
        previous_after = previous_receipt.get("tree_digest", {}).get("after", {})
        if previous_after.get("sha256") != prior_sha:
            raise OwnerWikiBatchError("current Wiki differs from previous receipt")
        _verify_commit_file(
            repo_root,
            accepted_prior_commit,
            previous_manifest_path,
            previous_manifest_raw,
            "previous manifest",
        )
        _verify_commit_file(
            repo_root,
            accepted_prior_commit,
            previous_receipt_path,
            previous_receipt_raw,
            "previous receipt",
        )
        source_snapshot.update(
            {
                "previous_manifest_path": _relative(
                    repo_root, previous_manifest_path, "previous manifest"
                ),
                "previous_manifest_sha256": chronological.sha256_bytes(
                    previous_manifest_raw
                ),
                "previous_receipt_path": _relative(
                    repo_root, previous_receipt_path, "previous receipt"
                ),
                "previous_receipt_sha256": chronological.sha256_bytes(
                    previous_receipt_raw
                ),
            }
        )

    prompt_raw = _read_regular(prompt_path, "writer prompt")
    materializer_raw = _read_regular(materializer_path, "materializer")
    contract = output_contract()
    contract_sha = chronological.sha256_bytes(chronological.json_bytes(contract))
    batch_counts = chronological._counts(selected)
    cumulative = chronological._counts(ordered[: start + len(selected)])
    counts = dict(batch_counts)
    counts.update({f"cumulative_{key}": value for key, value in cumulative.items()})
    processed = ordered[: start + len(selected)]

    record_bindings: list[dict[str, Any]] = []
    for holder in selected:
        for record in holder["_records"]:
            record_bindings.append(
                {
                    "record_id": record["record_id"],
                    "source_address": record["source_address"],
                    "source_path": record["source_path"],
                    "source_line": record["source_line"],
                    "source_link_target": _source_link_target(
                        repo_root,
                        wiki_root,
                        record["source_path"],
                        record["source_line"],
                    ),
                    "sort_timestamp": record["metadata"].get("sort_timestamp"),
                }
            )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "batch_id": batch_id,
        "previous_batch_id": previous_batch_id,
        "corpus_commit": metadata["corpus_commit"],
        "evidence_commit": evidence_commit,
        "evidence_records_sha256": metadata["evidence_records_sha256"],
        "source_snapshot": source_snapshot,
        "prior_checkpoint": {
            "wiki_root": _relative(repo_root, wiki_root, "Wiki root"),
            "wiki_tree_sha256_target": prior_sha,
            "accepted_prior_commit": accepted_prior_commit,
        },
        "prompt": {
            "path": _relative(repo_root, prompt_path, "writer prompt"),
            "sha256": chronological.sha256_bytes(prompt_raw),
        },
        "materializer": {
            "path": _relative(repo_root, materializer_path, "materializer"),
            "sha256": chronological.sha256_bytes(materializer_raw),
        },
        "output": {
            "changeset_path": _relative(repo_root, changeset_path, "changeset"),
            "changeset_schema": CHANGESET_SCHEMA,
            "output_contract": contract,
            "output_contract_sha256": contract_sha,
        },
        "preflight_receipt_path": _relative(
            repo_root, preflight_path, "preflight receipt"
        ),
        "ordering": {
            "holder_key": "maximum normalized record timestamp",
            "record_key": "source_line then record_id",
            "naive_timestamp_timezone": "Asia/Almaty",
            "normalized_timezone": "UTC",
            "tie_break": "source_path",
            "holder_split": False,
            "batch_size": chronological.BATCH_SIZE,
        },
        "counts": counts,
        "run_state": {
            "frozen_holder_count": metadata["frozen_holder_count"],
            "record_bearing_holder_count": metadata[
                "record_bearing_holder_count"
            ],
            "no_record_holder_count": len(no_record_paths),
            "no_record_holders": no_record_paths,
            "processed_record_bearing_holder_count": len(processed),
            "remaining_record_bearing_holder_count": len(ordered) - len(processed),
            "processed_holder_paths": [item["source_path"] for item in processed],
            "terminal_coverage_equation": (
                f"{metadata['record_bearing_holder_count']} record-bearing + "
                f"{len(no_record_paths)} no-record = "
                f"{metadata['frozen_holder_count']} frozen"
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
            "third_person_owner_attribution": True,
            "paraphrase_and_synthesis_allowed": True,
            "material_claims_require_source_record_ids": True,
            "page_fit_required_per_material_claim": True,
            "project_corpus_enrichment": False,
            "full_quote_copy": False,
            "current_only_projection": True,
            "exact_repetition_metadata": True,
        },
        "time_boundary_utc": selected[-1]["max_timestamp_utc"],
        "holders": [chronological._public_holder(holder) for holder in selected],
        "record_bindings": record_bindings,
    }
    manifest_raw = chronological.json_bytes(manifest)
    preflight = {
        "schema": PREFLIGHT_SCHEMA,
        "status": "pass",
        "batch_id": batch_id,
        "manifest_path": _relative(repo_root, manifest_path, "manifest"),
        "manifest_sha256": chronological.sha256_bytes(manifest_raw),
        "prompt_sha256": manifest["prompt"]["sha256"],
        "materializer_sha256": manifest["materializer"]["sha256"],
        "prior_wiki_tree_sha256": prior_sha,
    }
    return manifest, preflight


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--batch-number", type=int, required=True)
    parser.add_argument("--frozen-manifest", type=Path, required=True)
    parser.add_argument("--evidence-records", type=Path, required=True)
    parser.add_argument("--evidence-commit", required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--materializer", type=Path, required=True)
    parser.add_argument("--wiki-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--changeset", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--previous-manifest", type=Path)
    parser.add_argument("--previous-receipt", type=Path)
    parser.add_argument("--accepted-prior-commit")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest, preflight = build_batch(
            repo_root=args.repo_root,
            batch_number=args.batch_number,
            frozen_manifest_path=args.frozen_manifest,
            evidence_records_path=args.evidence_records,
            evidence_commit=args.evidence_commit,
            prompt_path=args.prompt,
            materializer_path=args.materializer,
            wiki_root=args.wiki_root,
            manifest_path=args.manifest,
            changeset_path=args.changeset,
            preflight_path=args.preflight,
            previous_manifest_path=args.previous_manifest,
            previous_receipt_path=args.previous_receipt,
            accepted_prior_commit=args.accepted_prior_commit,
        )
        _write_output(
            args.manifest, chronological.json_bytes(manifest), check=args.check
        )
        _write_output(
            args.preflight, chronological.json_bytes(preflight), check=args.check
        )
    except (
        OwnerWikiBatchError,
        chronological.BatchBuildError,
        materializer.MaterializationError,
    ) as exc:
        print(f"build_owner_wiki_batch: {exc}", file=os.sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "check" if args.check else "write",
                "batch_id": manifest["batch_id"],
                "manifest_sha256": chronological.sha256_bytes(
                    chronological.json_bytes(manifest)
                ),
                "prompt_sha256": manifest["prompt"]["sha256"],
                "holder_count": manifest["counts"]["holder_count"],
                "record_count": manifest["counts"]["record_count"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
