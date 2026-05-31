from __future__ import annotations

from typing import Any


SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

SEVERITY_BADGE = {
    SEVERITY_CRITICAL: "🔴",
    SEVERITY_WARNING: "🟡",
    SEVERITY_INFO: "ℹ️",
}

# Health gauge: deduct per finding by severity. Floor at 0.
SEVERITY_WEIGHTS = {
    SEVERITY_CRITICAL: 15,
    SEVERITY_WARNING: 5,
    SEVERITY_INFO: 0,
}


def compute_health(findings: list[dict[str, Any]]) -> int:
    """0-100 score: start at 100, subtract per finding by severity, floor at 0."""
    health = 100
    for f in findings:
        health -= SEVERITY_WEIGHTS.get(f.get("severity", SEVERITY_INFO), 0)
    return max(0, health)


def severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 0, SEVERITY_INFO: 0}
    for f in findings:
        sev = f.get("severity", SEVERITY_INFO)
        if sev in counts:
            counts[sev] += 1
    return counts


# --- Per-class severity logic --------------------------------------------
#
# One pure function per finding class: maps the class-specific evidence
# (counts, ratios, cohesion, classification label) to a severity badge or
# None ("drop — not surfaced"). Kept here next to the severity constants and
# the health gauge so the whole severity contract lives in one file; the
# detection engine in `audit.py` imports these by name.


def severity_for_smeared_concept(unique_files: int, cohesion: float) -> str | None:
    """Repeated-concepts entry → severity. None = drop (not surfaced)."""
    if unique_files >= 4 and cohesion >= 0.7:
        return SEVERITY_CRITICAL
    if unique_files in (2, 3) and cohesion >= 0.55:
        return SEVERITY_WARNING
    return None


def severity_for_classified_pair(classification: str) -> str | None:
    if classification == "FULL_DUPLICATE":
        return SEVERITY_CRITICAL
    if classification == "SEMANTIC_SMEAR":
        return SEVERITY_WARNING
    if classification == "TEMPLATE_EFFECT":
        return SEVERITY_INFO
    return None


def severity_for_discovery_gap(ratio: float) -> str | None:
    if ratio > 0.50:
        return SEVERITY_CRITICAL
    if ratio >= 0.25:
        return SEVERITY_WARNING
    if ratio >= 0.10:
        return SEVERITY_INFO
    return None


def severity_for_intra_file_drift(drift_count: int) -> str | None:
    if drift_count >= 2:
        return SEVERITY_CRITICAL
    if drift_count == 1:
        return SEVERITY_WARNING
    return None


def severity_for_cluster_mismatch(common_parent: str, size: int) -> str | None:
    if not common_parent and size >= 5:
        return SEVERITY_WARNING
    return SEVERITY_INFO


def severity_for_heading_family(file_count: int) -> str | None:
    """Heading appearing in many files is a template-family signal.
    INFO by default — templates can be by design (parallel-structure
    `_research/{category}/inventory.md`). WARNING when family is broad
    enough that splitting / consolidating warrants attention."""
    if file_count >= 5:
        return SEVERITY_WARNING
    if file_count >= 3:
        return SEVERITY_INFO
    return None


def severity_for_heading_lex_drift(diversity: float) -> str | None:
    """Mean (1 − Jaccard) between H2+ headings inside one file.
    0.85+ = headings share almost no tokens — strong drift signal even
    when section bodies are embed-tight under the file's H1 title."""
    if diversity >= 0.92:
        return SEVERITY_WARNING
    if diversity >= 0.85:
        return SEVERITY_INFO
    return None


