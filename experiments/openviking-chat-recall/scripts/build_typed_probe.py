#!/usr/bin/env python3
"""Build and validate the deterministic typed-evidence input for wave 3."""

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
    """Raised when frozen evidence or deterministic output is invalid."""


RECORD_RE = re.compile(
    r'^\* (?P<timestamp>\S+) — "(?P<quote>.*)" — (?P<meta>.*)$'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repository containing the frozen git objects.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "openviking-chat-recall/typed-gold.v1":
        raise ProbeError("unsupported typed gold manifest schema")
    clusters = value.get("clusters")
    if not isinstance(clusters, list) or len(clusters) != 2:
        raise ProbeError("typed gold manifest must contain exactly two clusters")
    return value


def git_blob(repo_root: Path, provenance_ref: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", provenance_ref],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if completed.returncode:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ProbeError(f"cannot resolve frozen source {provenance_ref}: {detail}")
    return completed.stdout


def parse_source_line(line: str) -> dict[str, str | None]:
    match = RECORD_RE.match(line)
    if not match:
        raise ProbeError(f"source line is not a chat-recall record: {line!r}")
    metadata: dict[str, str | None] = {"kind": None, "type": None, "topic": None}
    for field in match.group("meta").split(" | "):
        key, separator, value = field.partition(": ")
        if separator and key in metadata:
            metadata[key] = value
    if metadata["type"] is None or metadata["topic"] is None:
        raise ProbeError(f"record metadata is incomplete: {line!r}")
    return {
        "timestamp": match.group("timestamp"),
        "quote": match.group("quote"),
        **metadata,
    }


def validate_cluster(cluster: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    source = cluster["source"]
    expected_sha = source["sha256"]
    blob = git_blob(repo_root, source["provenance_ref"])
    actual_sha = hashlib.sha256(blob).hexdigest()
    if actual_sha != expected_sha:
        raise ProbeError(
            f"{cluster['id']}: frozen SHA mismatch: expected {expected_sha}, got {actual_sha}"
        )

    lines = blob.decode("utf-8").splitlines()
    records = cluster["records"]
    if not records:
        raise ProbeError(f"{cluster['id']}: no records in manifest")
    line_numbers = [record["line"] for record in records]
    if line_numbers != sorted(line_numbers) or len(set(line_numbers)) != len(line_numbers):
        raise ProbeError(f"{cluster['id']}: record lines must be unique and ordered")

    validated: list[dict[str, Any]] = []
    for record in records:
        line_number = record["line"]
        if not isinstance(line_number, int) or line_number < 1 or line_number > len(lines):
            raise ProbeError(f"{cluster['id']}: invalid source line {line_number}")
        source_record = parse_source_line(lines[line_number - 1])
        expected_record_id = f"{Path(source['path']).name}:{line_number}"
        if record["record_id"] != expected_record_id:
            raise ProbeError(f"{cluster['id']}: record id does not match source address")
        for field in ("timestamp", "quote", "kind", "type", "topic"):
            if source_record[field] != record[field]:
                raise ProbeError(
                    f"{cluster['id']}:{line_number}: {field} differs from frozen source"
                )
        datetime.fromisoformat(record["timestamp"])
        validated.append(record)

    expected = cluster["expected"]
    timestamps = [datetime.fromisoformat(record["timestamp"]) for record in validated]
    first = min(timestamps).isoformat()
    latest = max(timestamps).isoformat()
    if expected["record_count"] != len(validated):
        raise ProbeError(f"{cluster['id']}: exact count does not match records")
    if expected["first"] != first or expected["latest"] != latest:
        raise ProbeError(
            f"{cluster['id']}: expected chronology {expected['first']}..{expected['latest']}, "
            f"computed {first}..{latest}"
        )
    return {
        "cluster": cluster,
        "source_sha256": actual_sha,
        "records": validated,
        "first": first,
        "latest": latest,
    }


def quote_block(quote: str) -> str:
    return "> " + quote.replace("\n", "\n> ")


def render_cluster(result: dict[str, Any]) -> str:
    cluster = result["cluster"]
    source = cluster["source"]
    expected = cluster["expected"]
    lines = [
        f"# Typed evidence — {cluster['title']}",
        "",
        "This is a deterministic typed-evidence input. Exact count, first/latest and source provenance are gold facts; the LLM must not recalculate or replace them.",
        "",
        f"Probe claim: {cluster['probe_claim']}",
        "",
        "## Deterministic facts",
        "",
        f"- Exact source records: `{expected['record_count']}`",
        f"- First recorded occurrence: `{expected['first']}`",
        f"- Latest recorded occurrence: `{expected['latest']}`",
        f"- Source path: `{source['path']}`",
        f"- Frozen provenance ref: `{source['provenance_ref']}`",
        f"- Frozen source SHA-256: `{result['source_sha256']}`",
        "",
        "## Gold assertions",
        "",
    ]
    for assertion in cluster["gold_assertions"]:
        lines.extend(
            [
                f"### {assertion['id']}",
                "",
                assertion["statement"],
                "",
                "Provenance records: "
                + ", ".join(f"`{record_id}`" for record_id in assertion["record_ids"]),
                "",
            ]
        )
    lines.extend(["## Exact owner records", ""])
    for record in result["records"]:
        lines.extend(
            [
                f"### {record['record_id']}",
                "",
                f"- Timestamp: `{record['timestamp']}`",
                f"- Kind: `{record['kind'] or 'not recorded'}`",
                f"- Type: `{record['type']}`",
                f"- Topic: `{record['topic']}`",
                f"- Source line: `{record['line']}`",
                "- Exact owner quote:",
                quote_block(record["quote"]),
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_index(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Typed evidence probe input",
        "",
        "This directory is the deterministic input arm for the OpenViking LLM Wiki Compile route.",
        "The two cluster pages contain frozen Git provenance, exact owner records and gold assertions.",
        "Unsupported claims must remain unsupported; this input does not authorize inference beyond its records.",
        "",
        "## Clusters",
        "",
    ]
    for result in results:
        cluster = result["cluster"]
        slug = cluster["id"]
        lines.extend(
            [
                f"- [{cluster['title']}]({slug}.md): `{cluster['expected']['record_count']}` records, "
                f"`{cluster['expected']['first']}` to `{cluster['expected']['latest']}`.",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The deterministic builder owns exact count, first/latest, membership and provenance. The official Skill/IA/Compile route owns the derived Wiki representation. A Wiki page is not accepted here as semantic proof; a separate blind reader must audit it.",
            "",
        ]
    )
    return "\n".join(lines)


def build(manifest_path: Path, output_dir: Path, repo_root: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    results = [validate_cluster(cluster, repo_root) for cluster in manifest["clusters"]]
    output_dir.mkdir(parents=True, exist_ok=True)
    for result in results:
        cluster = result["cluster"]
        (output_dir / f"{cluster['id']}.md").write_text(
            render_cluster(result), encoding="utf-8"
        )
    (output_dir / "index.md").write_text(render_index(results), encoding="utf-8")
    return {
        "schema": "openviking-chat-recall/typed-build-receipt.v1",
        "manifest": str(manifest_path),
        "provenance_commit": manifest["frozen_provenance_commit"],
        "clusters": [
            {
                "id": result["cluster"]["id"],
                "record_count": len(result["records"]),
                "first": result["first"],
                "latest": result["latest"],
                "source_sha256": result["source_sha256"],
            }
            for result in results
        ],
        "output_dir": str(output_dir),
    }


def main() -> None:
    args = parse_args()
    receipt = build(args.manifest, args.output_dir, args.repo_root.resolve())
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
