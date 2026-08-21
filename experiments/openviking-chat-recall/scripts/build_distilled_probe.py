#!/usr/bin/env python3
"""Build the small, source-bound distilled-knowledge probe for wave 5.

The manifest is the only semantic input.  This script validates deterministic
evidence and projects only explicitly accepted claim statuses into the default
Wiki surface; it never infers currentness from timestamps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class ProbeError(ValueError):
    """Raised when frozen evidence or the distilled contract is invalid."""


SCHEMA = "openviking-chat-recall/distilled-gold.v1"
RECEIPT_SCHEMA = "openviking-chat-recall/distilled-probe-receipt.v1"
FROZEN_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RECORD_PREFIX = "* "
LIFECYCLE_STATUSES = frozenset({"current", "contested", "non-current", "uncertain"})
DEFAULT_WIKI_STATUSES = frozenset({"current", "contested"})
FORBIDDEN_DEFAULT_MARKERS = (
    "Exact count:",
    "First recorded occurrence:",
    "Latest recorded occurrence:",
    "## Evolution",
    "Evolution:",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--wiki-dir", type=Path, required=True)
    parser.add_argument("--receipt-json", type=Path)
    parser.add_argument("--receipt-md", type=Path)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository containing the frozen Git objects.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProbeError(f"cannot load manifest {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ProbeError(f"unsupported distilled manifest schema in {path}")
    return value


def git_blob(repo_root: Path, provenance_commit: str, source_path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{provenance_commit}:{source_path}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProbeError(
            f"cannot resolve frozen source {provenance_commit}:{source_path}: {detail}"
        )
    return completed.stdout


def parse_source_line(line: str) -> dict[str, str | None]:
    if not line.startswith(RECORD_PREFIX) or " — \"" not in line:
        raise ProbeError(f"source line is not a chat-recall record: {line!r}")
    prefix, rest = line.split(" — \"", 1)
    try:
        quote, metadata_text = rest.rsplit("\" — ", 1)
    except ValueError as exc:
        raise ProbeError(f"source line has no closed quote: {line!r}") from exc
    timestamp = prefix.removeprefix(RECORD_PREFIX)
    metadata: dict[str, str | None] = {
        "kind": None,
        "type": None,
        "topic": None,
    }
    for field in metadata_text.split(" | "):
        key, separator, value = field.partition(": ")
        if separator and key in metadata:
            metadata[key] = value
    if metadata["type"] is None or metadata["topic"] is None:
        raise ProbeError(f"record metadata is incomplete: {line!r}")
    return {
        "timestamp": timestamp,
        "quote": quote,
        **metadata,
    }


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProbeError(f"{label} must be a non-empty string")
    return value


def validate_manifest(manifest: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    frozen_commit = _require_string(
        manifest.get("frozen_provenance_commit"), "frozen_provenance_commit"
    )
    if not FROZEN_COMMIT_RE.fullmatch(frozen_commit):
        raise ProbeError("frozen_provenance_commit must be a full 40-character SHA")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ProbeError("manifest must contain at least one source")

    source_results: list[dict[str, Any]] = []
    record_map: dict[str, dict[str, Any]] = {}
    source_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ProbeError("each source must be an object")
        source_id = _require_string(source.get("id"), "source.id")
        source_path = _require_string(source.get("path"), f"{source_id}.path")
        source_commit = _require_string(
            source.get("provenance_commit"), f"{source_id}.provenance_commit"
        )
        if source_id in source_ids:
            raise ProbeError(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        if source_commit != frozen_commit:
            raise ProbeError(f"{source_id}: source commit differs from frozen commit")
        if Path(source_path).is_absolute() or ".." in Path(source_path).parts:
            raise ProbeError(f"{source_id}: source path escapes repository")

        blob = git_blob(repo_root, frozen_commit, source_path)
        actual_blob_sha = sha256_bytes(blob)
        expected_blob_sha = _require_string(
            source.get("blob_sha256"), f"{source_id}.blob_sha256"
        )
        if actual_blob_sha != expected_blob_sha:
            raise ProbeError(
                f"{source_id}: frozen blob mismatch: expected {expected_blob_sha}, "
                f"got {actual_blob_sha}"
            )

        records = source.get("records")
        if not isinstance(records, list) or not records:
            raise ProbeError(f"{source_id}: records must be a non-empty list")
        lines = blob.decode("utf-8").splitlines()
        source_record_results: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, dict):
                raise ProbeError(f"{source_id}: each record must be an object")
            record_id = _require_string(record.get("record_id"), "record.record_id")
            line_number = record.get("line")
            if not isinstance(line_number, int) or line_number < 1 or line_number > len(lines):
                raise ProbeError(f"{source_id}: invalid source line {line_number}")
            expected_record_id = f"{source_path}:{line_number}"
            if record_id != expected_record_id:
                raise ProbeError(
                    f"{source_id}:{line_number}: record id does not match source address"
                )
            if record_id in record_map:
                raise ProbeError(f"duplicate record id: {record_id}")
            source_record = parse_source_line(lines[line_number - 1])
            for field in ("timestamp", "kind", "type", "topic"):
                if source_record[field] != record.get(field):
                    raise ProbeError(f"{record_id}: {field} differs from frozen source")
            timestamp = _require_string(record.get("timestamp"), f"{record_id}.timestamp")
            if timestamp != source_record["timestamp"]:
                raise ProbeError(f"{record_id}: timestamp differs from frozen source")
            try:
                datetime.fromisoformat(timestamp)
            except ValueError as exc:
                raise ProbeError(f"{record_id}: invalid timestamp {timestamp!r}") from exc
            expected_quote_sha = _require_string(
                record.get("quote_sha256"), f"{record_id}.quote_sha256"
            )
            actual_quote_sha = sha256_bytes((source_record["quote"] or "").encode("utf-8"))
            if actual_quote_sha != expected_quote_sha:
                raise ProbeError(
                    f"{record_id}: quote digest differs: expected {expected_quote_sha}, "
                    f"got {actual_quote_sha}"
                )
            validated_record = {
                "record_id": record_id,
                "line": line_number,
                "timestamp": timestamp,
                "kind": source_record["kind"],
                "type": source_record["type"],
                "topic": source_record["topic"],
                "quote": source_record["quote"],
                "source_id": source_id,
                "source_path": source_path,
                "blob_sha256": actual_blob_sha,
            }
            source_record_results.append(validated_record)
            record_map[record_id] = validated_record
        source_results.append(
            {
                "id": source_id,
                "path": source_path,
                "provenance_commit": frozen_commit,
                "blob_sha256": actual_blob_sha,
                "records": source_record_results,
            }
        )

    claims = manifest.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ProbeError("manifest must contain at least one claim")
    claim_map: dict[str, dict[str, Any]] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            raise ProbeError("each claim must be an object")
        claim_id = _require_string(claim.get("id"), "claim.id")
        if claim_id in claim_map:
            raise ProbeError(f"duplicate claim id: {claim_id}")
        status = _require_string(claim.get("lifecycle_status"), f"{claim_id}.lifecycle_status")
        if status not in LIFECYCLE_STATUSES:
            raise ProbeError(f"{claim_id}: unknown lifecycle status {status!r}")
        slug = _require_string(claim.get("slug"), f"{claim_id}.slug")
        if not SLUG_RE.fullmatch(slug):
            raise ProbeError(f"{claim_id}: invalid wiki slug {slug!r}")
        source_record_ids = claim.get("source_record_ids")
        if not isinstance(source_record_ids, list) or not source_record_ids:
            raise ProbeError(f"{claim_id}: source_record_ids must be non-empty")
        if len(set(source_record_ids)) != len(source_record_ids):
            raise ProbeError(f"{claim_id}: duplicate source record id")
        for record_id in source_record_ids:
            if record_id not in record_map:
                raise ProbeError(f"{claim_id}: unknown source record id {record_id}")
        claim_map[claim_id] = {
            "id": claim_id,
            "slug": slug,
            "title": _require_string(claim.get("title"), f"{claim_id}.title"),
            "statement": _require_string(claim.get("statement"), f"{claim_id}.statement"),
            "applicability": _require_string(
                claim.get("applicability"), f"{claim_id}.applicability"
            ),
            "lifecycle_status": status,
            "source_record_ids": source_record_ids,
            "superseded_by": claim.get("superseded_by"),
        }
    for claim in claim_map.values():
        superseded_by = claim["superseded_by"]
        if superseded_by is None:
            continue
        if not isinstance(superseded_by, str) or superseded_by not in claim_map:
            raise ProbeError(f"{claim['id']}: dangling superseded_by {superseded_by!r}")
        if superseded_by == claim["id"]:
            raise ProbeError(f"{claim['id']}: claim cannot supersede itself")
        if claim_map[superseded_by]["lifecycle_status"] not in DEFAULT_WIKI_STATUSES:
            raise ProbeError(
                f"{claim['id']}: superseded_by must point to current or contested claim"
            )

    no_gold_controls = manifest.get("no_gold_controls", [])
    if not isinstance(no_gold_controls, list):
        raise ProbeError("no_gold_controls must be a list")
    validated_controls: list[dict[str, str]] = []
    control_ids: set[str] = set()
    for control in no_gold_controls:
        if not isinstance(control, dict):
            raise ProbeError("each no-gold control must be an object")
        control_id = _require_string(control.get("id"), "no_gold_control.id")
        if control_id in control_ids:
            raise ProbeError(f"duplicate no-gold control id: {control_id}")
        control_ids.add(control_id)
        validated_controls.append(
            {
                "id": control_id,
                "statement": _require_string(
                    control.get("statement"), f"{control_id}.statement"
                ),
            }
        )

    return {
        "frozen_provenance_commit": frozen_commit,
        "sources": source_results,
        "records": record_map,
        "claims": list(claim_map.values()),
        "claim_map": claim_map,
        "no_gold_controls": validated_controls,
    }


def quote_block(quote: str) -> str:
    return "> " + quote.replace("\n", "\n> ")


def render_input(bundle: dict[str, Any]) -> dict[str, str]:
    files: dict[str, str] = {}
    index_lines = [
        "# Distilled probe frozen input",
        "",
        "This directory is generated from the exact frozen Git snapshot. Exact owner quotes live here for validation; they are not copied into the default Wiki.",
        "",
        f"Frozen provenance commit: `{bundle['frozen_provenance_commit']}`",
        "",
        "## Sources",
        "",
    ]
    for number, source in enumerate(bundle["sources"], start=1):
        filename = f"source-{number:02d}.md"
        index_lines.append(
            f"- [{source['id']}]({filename}): `{source['path']}`; "
            f"`{len(source['records'])}` frozen records; blob `{source['blob_sha256']}`."
        )
        source_lines = [
            f"# Frozen source — {source['id']}",
            "",
            f"- Source path: `{source['path']}`",
            f"- Provenance commit: `{source['provenance_commit']}`",
            f"- Source blob SHA-256: `{source['blob_sha256']}`",
            "",
            "## Exact owner records",
            "",
        ]
        for record in source["records"]:
            source_lines.extend(
                [
                    f"### {record['record_id']}",
                    "",
                    f"- Timestamp: `{record['timestamp']}`",
                    f"- Kind: `{record['kind'] or 'not recorded'}`",
                    f"- Type: `{record['type']}`",
                    f"- Topic: `{record['topic']}`",
                    f"- Source line: `{record['line']}`",
                    f"- Quote SHA-256: `{sha256_bytes((record['quote'] or '').encode('utf-8'))}`",
                    "- Exact owner quote:",
                    quote_block(record["quote"] or ""),
                    "",
                ]
            )
        files[filename] = "\n".join(source_lines).rstrip() + "\n"
    index_lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This input does not authorize unsupported claims. Claim status is supplied by the manifest and is not derived from `latest`.",
            "",
        ]
    )
    files["index.md"] = "\n".join(index_lines)
    return files


def render_claim(claim: dict[str, Any]) -> str:
    source_lines = "\n".join(f"- `{record_id}`" for record_id in claim["source_record_ids"])
    return "\n".join(
        [
            "---",
            "type: concept",
            f"title: {claim['title']}",
            f"lifecycle_status: {claim['lifecycle_status']}",
            "---",
            "",
            f"# {claim['title']}",
            "",
            "## Distilled knowledge",
            "",
            claim["statement"],
            "",
            "## Applicability",
            "",
            claim["applicability"],
            "",
            "## Evidence addresses",
            "",
            source_lines,
            "",
        ]
    )


def render_wiki(bundle: dict[str, Any]) -> dict[str, str]:
    eligible = [
        claim
        for claim in sorted(bundle["claims"], key=lambda item: item["id"])
        if claim["lifecycle_status"] in DEFAULT_WIKI_STATUSES
    ]
    files: dict[str, str] = {}
    index_lines = [
        "---",
        "type: index",
        "title: Distilled knowledge probe",
        "description: Current and contested distilled knowledge from frozen owner records.",
        "---",
        "",
        "# Distilled knowledge probe",
        "",
        "This default surface contains only claims explicitly marked `current` or `contested` in the evidence manifest. Exact wording, chronology and unresolved claims stay outside this surface.",
        "",
        "## Knowledge",
        "",
    ]
    for claim in eligible:
        path = f"concept/{claim['slug']}.md"
        index_lines.append(
            f"- [{claim['title']}]({path}) — {claim['statement']} ({claim['lifecycle_status']})"
        )
        files[path] = render_claim(claim)
    files["index.md"] = "\n".join(index_lines).rstrip() + "\n"
    return files


def validate_default_wiki(
    wiki_files: dict[str, str], bundle: dict[str, Any]
) -> list[dict[str, str]]:
    body = "\n".join(wiki_files.values())
    checks: list[dict[str, str]] = []
    for record in bundle["records"].values():
        quote = record["quote"] or ""
        if quote and quote in body:
            raise ProbeError(f"default Wiki contains exact source quote {record['record_id']}")
    checks.append({"id": "exact-source-quotes-absent", "status": "pass"})
    for marker in FORBIDDEN_DEFAULT_MARKERS:
        if marker in body:
            raise ProbeError(f"default Wiki contains forbidden history marker {marker!r}")
    checks.append({"id": "history-fields-absent", "status": "pass"})
    for claim in bundle["claims"]:
        present = claim["statement"] in body
        expected = claim["lifecycle_status"] in DEFAULT_WIKI_STATUSES
        if present != expected:
            raise ProbeError(
                f"claim {claim['id']}: Wiki presence {present} does not match status "
                f"{claim['lifecycle_status']}"
            )
    checks.append({"id": "lifecycle-filter-is-explicit", "status": "pass"})
    for control in bundle["no_gold_controls"]:
        if control["statement"] in body:
            raise ProbeError(f"no-gold control leaked into Wiki: {control['id']}")
    checks.append({"id": "no-gold-boundary", "status": "pass"})
    return checks


def write_files(root: Path, files: dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for relative_path, content in files.items():
        destination = root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def receipt_payload(
    manifest_path: Path,
    bundle: dict[str, Any],
    input_files: dict[str, str],
    wiki_files: dict[str, str],
    deterministic_checks: list[dict[str, str]],
) -> dict[str, Any]:
    rendered = [
        claim["id"]
        for claim in bundle["claims"]
        if claim["lifecycle_status"] in DEFAULT_WIKI_STATUSES
    ]
    suppressed = [
        claim["id"]
        for claim in bundle["claims"]
        if claim["lifecycle_status"] not in DEFAULT_WIKI_STATUSES
    ]
    return {
        "schema": RECEIPT_SCHEMA,
        "status": "candidate",
        "manifest": str(manifest_path),
        "provenance_commit": bundle["frozen_provenance_commit"],
        "generated": {
            "input_files": sorted(input_files),
            "wiki_files": sorted(wiki_files),
        },
        "evidence": {
            "source_count": len(bundle["sources"]),
            "record_count": len(bundle["records"]),
            "claim_count": len(bundle["claims"]),
            "rendered_claim_ids": rendered,
            "suppressed_claim_ids": suppressed,
        },
        "deterministic_validation": {
            "status": "pass",
            "checks": deterministic_checks,
        },
        "semantic_boundary": {
            "status": "candidate",
            "claim_statuses_are_manifest_input": True,
            "not_proven": [
                "semantic grouping quality",
                "currentness beyond the explicit manifest status",
                "blind retrieval usefulness",
            ],
        },
        "test_command": "python3 -m unittest discover -s tests -p 'test_*.py' -v",
    }


def render_receipt_markdown(payload: dict[str, Any]) -> str:
    evidence = payload["evidence"]
    checks = payload["deterministic_validation"]["checks"]
    semantic = payload["semantic_boundary"]
    lines = [
        "# Distilled probe receipt",
        "",
        "Status: `candidate` — deterministic evidence passed; semantic acceptance is external.",
        "",
        "## Frozen provenance",
        "",
        f"- Commit: `{payload['provenance_commit']}`",
        f"- Manifest: `{payload['manifest']}`",
        f"- Sources: `{evidence['source_count']}`; records: `{evidence['record_count']}`; claims: `{evidence['claim_count']}`.",
        "",
        "## Design trace",
        "",
        "- Owner: `scripts/build_distilled_probe.py`; manifest owns frozen membership and explicit claim status; tests own the boundary proof.",
        "- Chosen seam: one stdlib compiler with `manifest → evidence validation → input/Wiki projection`; a multi-module package was rejected because the probe has one writer and no evidenced independent runtime seam.",
        "- Applied project principles: Product Frame P-001/P-003/P-004/P-005/P-008; this keeps the derived experiment separate from immutable holders, makes the evidence chain visible, and leaves semantic self-report unaccepted.",
        "",
        "## Deterministic validation",
        "",
    ]
    lines.extend(f"- `{check['id']}`: `{check['status']}`" for check in checks)
    lines.extend(
        [
            "- Rebuild check: the test suite compares every generated input/Wiki file byte-for-byte across two temporary output roots.",
            "",
            "## Semantic boundary",
            "",
            f"- Status: `{semantic['status']}`.",
            "- The builder accepts `current`/`contested` as explicit candidate input and suppresses `non-current`/`uncertain`; it never derives currentness from `latest`.",
            "- Not proven here: semantic grouping quality, currentness beyond the manifest status, and blind retrieval usefulness.",
            "",
            "## Falsifying checks",
            "",
            "- frozen blob, line, record ID, timestamp or quote-digest drift fails closed;\n"
            "- unknown record ID or lifecycle status fails closed;\n"
            "- dangling `superseded_by` fails closed;\n"
            "- exact source quotes and count/first/latest/evolution markers cannot enter default Wiki;\n"
            "- non-current/uncertain claims and no-gold controls cannot enter default Wiki;\n"
            "- deterministic rebuild must be byte-identical.",
            "",
            "## Test command",
            "",
            f"`{payload['test_command']}` (run from a clean checkout of the writer commit).",
            "",
            "## Nested-agent receipts",
            "",
            "The three requested internal read-only scout packets are explicit UNKNOWN after bounded runtime recovery; their handles and shutdown state are recorded in the terminal return, not promoted to evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def build(
    manifest_path: Path,
    input_dir: Path,
    wiki_dir: Path,
    repo_root: Path,
    receipt_json: Path | None = None,
    receipt_md: Path | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    bundle = validate_manifest(manifest, repo_root.resolve())
    input_files = render_input(bundle)
    wiki_files = render_wiki(bundle)
    deterministic_checks = validate_default_wiki(wiki_files, bundle)
    write_files(input_dir, input_files)
    write_files(wiki_dir, wiki_files)
    payload = receipt_payload(
        manifest_path,
        bundle,
        input_files,
        wiki_files,
        deterministic_checks,
    )
    if receipt_json is not None:
        receipt_json.parent.mkdir(parents=True, exist_ok=True)
        receipt_json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if receipt_md is not None:
        receipt_md.parent.mkdir(parents=True, exist_ok=True)
        receipt_md.write_text(render_receipt_markdown(payload), encoding="utf-8")
    return payload


def main() -> None:
    args = parse_args()
    payload = build(
        args.manifest,
        args.input_dir,
        args.wiki_dir,
        args.repo_root,
        args.receipt_json,
        args.receipt_md,
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
