#!/usr/bin/env python3
"""Deterministic checks for a prose-audit run folder."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import sys


REQUIRED_RUN_FILES = ("run.md", "evidence-ledger.tsv", "role-manifest.tsv", "report.md")
REQUIRED_LEDGER_COLUMNS = (
    "claim_id",
    "question_id",
    "artifact_ref",
    "modality",
    "locator_type",
    "locator",
    "capture_ref",
    "source_strength",
    "source_role",
    "text_excerpt",
    "notes",
)
REQUIRED_MANIFEST_COLUMNS = (
    "role_id",
    "raw_file",
    "status",
    "independence_label",
    "notes",
)
VALID_MODALITIES = {
    "markdown",
    "plain_text",
    "url",
    "screenshot",
    "deck",
    "video",
    "audio",
    "figma",
    "dataset",
    "interview",
    "measurement",
}
VALID_LOCATOR_TYPES_BY_MODALITY = {
    "markdown": {"line_range", "heading", "block_id"},
    "plain_text": {"line_range", "paragraph", "char_range"},
    "url": {"url", "dom_selector", "viewport_state"},
    "screenshot": {"region", "ocr_text", "visual_element"},
    "deck": {"slide", "slide_region", "speaker_note"},
    "video": {"timecode", "shot", "transcript_range"},
    "audio": {"timecode", "transcript_range"},
    "figma": {"node_id", "frame", "component"},
    "dataset": {"row_id", "column", "query"},
    "interview": {"participant_id", "quote_id", "timecode"},
    "measurement": {"metric", "event", "query"},
}
SOURCE_STRENGTHS = {
    "self_canon",
    "derived_research",
    "external_secondary",
    "external_primary",
    "observed_reality",
}
WEAK_DECISION_STRENGTHS = {"self_canon", "derived_research"}
TEXT_RESOLVABLE_MODALITIES = {"markdown", "plain_text"}
LINE_RANGE_LOCATOR_TYPES = {"line_range"}
ROLE_ALIASES = {
    "trace-auditor": {"trace-auditor", "md-scout"},
    "challenger": {"challenger", "business-critic"},
    "buyer-skeptic": {"buyer-skeptic", "business-critic"},
    "studio-skeptic": {"studio-skeptic", "business-critic"},
    "defender": {"defender", "local-defender"},
    "judge": {"judge"},
    "auditor": {"auditor"},
}


@dataclass(frozen=True)
class CheckResult:
    level: str
    message: str


def read_ledger(path: Path) -> tuple[list[dict[str, str]], list[CheckResult]]:
    results: list[CheckResult] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = tuple(reader.fieldnames or ())
        missing = [name for name in REQUIRED_LEDGER_COLUMNS if name not in fieldnames]
        if missing:
            results.append(CheckResult("error", f"ledger missing columns: {', '.join(missing)}"))
            return [], results
        rows = list(reader)
    if not rows:
        results.append(CheckResult("error", "evidence-ledger.tsv has no rows"))
    return rows, results


def read_tsv(path: Path, required_columns: tuple[str, ...], label: str) -> tuple[list[dict[str, str]], list[CheckResult]]:
    results: list[CheckResult] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = tuple(reader.fieldnames or ())
        missing = [name for name in required_columns if name not in fieldnames]
        if missing:
            results.append(CheckResult("error", f"{label} missing columns: {', '.join(missing)}"))
            return [], results
        rows = list(reader)
    if not rows:
        results.append(CheckResult("error", f"{label} has no rows"))
    return rows, results


def extract_required_roles(suite_dir: Path) -> set[str]:
    roles: set[str] = set()
    for test_card in suite_dir.glob("*.md"):
        for line in test_card.read_text(encoding="utf-8").splitlines():
            normalized = line.strip().removeprefix("-").strip()
            if normalized.startswith("required_roles:"):
                value = normalized.split(":", 1)[1]
                roles.update(part.strip() for part in value.split(",") if part.strip())
    return roles


def role_is_satisfied(required_role: str, completed_roles: set[str]) -> bool:
    allowed_roles = ROLE_ALIASES.get(required_role, {required_role})
    return bool(allowed_roles & completed_roles)


def parse_line_ranges(locator: str) -> tuple[list[tuple[int, int]], str | None]:
    """Parse '31-37', '8', or '31-37,94-103' into line ranges. Returns (ranges, error)."""
    ranges: list[tuple[int, int]] = []
    for part in locator.split(","):
        part = part.strip()
        if not part:
            continue
        low, separator, high = part.partition("-")
        if not separator:
            high = low
        try:
            start, end = int(low), int(high)
        except ValueError:
            return [], f"unparseable line locator {part!r}"
        if start < 1 or end < start:
            return [], f"invalid line range {part!r}"
        ranges.append((start, end))
    if not ranges:
        return [], "empty line locator"
    return ranges, None


def _normalize(text: str) -> str:
    """Collapse whitespace so a translated/re-wrapped quote still matches."""
    return " ".join(text.split())


def check_anchor_resolution(
    claim_id: str,
    artifact_path: Path,
    modality: str,
    locator_type: str,
    locator: str,
    anchor_quote: str,
) -> list[CheckResult]:
    """Deterministically resolve a line anchor: in-range, non-blank, and (if given) quote present.

    Semantic match of text_excerpt is out of scope here — excerpts are auditor
    interpretations, often in another language than the source. This layer only
    proves the anchor still points at real, non-empty text at the cited lines.
    """
    if modality not in TEXT_RESOLVABLE_MODALITIES or locator_type not in LINE_RANGE_LOCATOR_TYPES:
        return []
    try:
        file_lines = artifact_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return [CheckResult("error", f"{claim_id}: cannot read artifact to resolve anchor: {exc}")]
    ranges, error = parse_line_ranges(locator)
    if error:
        return [CheckResult("error", f"{claim_id}: {error}")]

    results: list[CheckResult] = []
    total_lines = len(file_lines)
    normalized_quote = _normalize(anchor_quote)
    for start, end in ranges:
        if end > total_lines:
            results.append(
                CheckResult("error", f"{claim_id}: anchor {start}-{end} out of range (file has {total_lines} lines)")
            )
            continue
        span = file_lines[start - 1 : end]
        if not any(line.strip() for line in span):
            results.append(CheckResult("error", f"{claim_id}: anchor {start}-{end} resolves to blank lines"))
        elif normalized_quote and normalized_quote not in _normalize("\n".join(span)):
            results.append(
                CheckResult("error", f"{claim_id}: anchor_quote not found at {start}-{end} (anchor drifted?)")
            )
    return results


def check_run(run_dir: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    if not run_dir.exists():
        return [CheckResult("error", f"run directory does not exist: {run_dir}")]

    for name in REQUIRED_RUN_FILES:
        if not (run_dir / name).is_file():
            results.append(CheckResult("error", f"missing required file: {name}"))

    raw_dir = run_dir / "raw"
    if not raw_dir.is_dir() or not any(raw_dir.iterdir()):
        results.append(CheckResult("warning", "raw/ is missing or empty"))

    suite_dir = run_dir / "suite"
    if not suite_dir.is_dir() or not any(suite_dir.glob("*.md")):
        results.append(CheckResult("warning", "suite/ is missing or has no test cards"))

    manifest_path = run_dir / "role-manifest.tsv"
    if manifest_path.is_file():
        rows, manifest_results = read_tsv(manifest_path, REQUIRED_MANIFEST_COLUMNS, "role-manifest.tsv")
        results.extend(manifest_results)
        completed_roles: set[str] = set()
        for row in rows:
            role_id = row["role_id"].strip()
            status = row["status"].strip()
            raw_file = row["raw_file"].strip()
            if status == "completed":
                completed_roles.add(role_id)
            elif status == "pending":
                results.append(CheckResult("warning", f"{role_id}: role status is pending"))
            elif status not in {"skipped", "not_applicable", "failed"}:
                results.append(CheckResult("error", f"{role_id}: invalid role status {status!r}"))
            if raw_file and raw_file != "report.md":
                candidate = run_dir / raw_file
                if status == "completed" and not candidate.is_file():
                    results.append(CheckResult("error", f"{role_id}: completed role raw_file not found: {raw_file}"))

        if suite_dir.is_dir():
            for role in sorted(extract_required_roles(suite_dir)):
                if not role_is_satisfied(role, completed_roles):
                    results.append(CheckResult("error", f"required role not completed: {role}"))

    ledger_path = run_dir / "evidence-ledger.tsv"
    if not ledger_path.is_file():
        return results

    rows, ledger_results = read_ledger(ledger_path)
    results.extend(ledger_results)
    for index, row in enumerate(rows, start=2):
        strength = row["source_strength"].strip()
        role = row["source_role"].strip()
        modality = row["modality"].strip()
        locator_type = row["locator_type"].strip()
        locator = row["locator"].strip()
        claim_id = row["claim_id"].strip() or f"row {index}"
        artifact_ref = row["artifact_ref"].strip()
        if strength not in SOURCE_STRENGTHS:
            results.append(CheckResult("error", f"{claim_id}: invalid source_strength {strength!r}"))
        if modality not in VALID_MODALITIES:
            results.append(CheckResult("error", f"{claim_id}: invalid modality {modality!r}"))
        elif locator_type not in VALID_LOCATOR_TYPES_BY_MODALITY[modality]:
            results.append(
                CheckResult(
                    "error",
                    f"{claim_id}: invalid locator_type {locator_type!r} for modality {modality!r}",
                )
            )
        if not artifact_ref:
            results.append(CheckResult("error", f"{claim_id}: artifact_ref is empty"))
        if not locator:
            results.append(CheckResult("error", f"{claim_id}: locator is empty"))
        if role == "decision_ground" and strength in WEAK_DECISION_STRENGTHS:
            results.append(
                CheckResult(
                    "warning",
                    f"{claim_id}: decision_ground uses weak source_strength {strength!r}",
                )
            )
        if modality in {"markdown", "plain_text", "screenshot", "deck", "video", "audio", "dataset"}:
            candidate = Path(artifact_ref)
            if not candidate.is_absolute():
                candidate = run_dir / candidate
            if not candidate.exists():
                results.append(CheckResult("error", f"{claim_id}: artifact_ref not found: {artifact_ref}"))
            else:
                anchor_quote = (row.get("anchor_quote") or "").strip()
                results.extend(
                    check_anchor_resolution(
                        claim_id, candidate, modality, locator_type, locator, anchor_quote
                    )
                )
    return results


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args(argv)

    results = check_run(args.run_dir)
    for result in results:
        print(f"{result.level.upper()}: {result.message}")

    has_errors = any(result.level == "error" for result in results)
    has_warnings = any(result.level == "warning" for result in results)
    if has_errors or (args.strict and has_warnings):
        return 1
    print("OK: deterministic run checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
