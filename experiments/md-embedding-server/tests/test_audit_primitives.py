"""Unit tests for `audit.py` primitives — pure functions on dict / numpy
synthetic data. No HTTP, no embedding API, no DB. These are the seams
that the audit command orchestrates; testing them in isolation makes
the audit smoke test much easier to debug when something regresses."""

from __future__ import annotations

import sqlite3

import pytest

from navigator.audit import (
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    _normalize_heading,
    classify_pairs_by_template,
    compute_health,
    detect_intra_file_drift,
    severity_counts,
    severity_for_classified_pair,
    severity_for_discovery_gap,
    severity_for_intra_file_drift,
    severity_for_smeared_concept,
)


# --- heading normalisation -----------------------------------------------


def test_normalize_heading_strips_and_lowers():
    assert _normalize_heading("  ## Опоры  ") == "## опоры"
    assert _normalize_heading("Heading\twith\ttabs") == "heading with tabs"
    assert _normalize_heading("ALL CAPS") == "all caps"


def test_normalize_heading_collapses_whitespace():
    assert _normalize_heading("foo   bar    baz") == "foo bar baz"


def test_normalize_heading_handles_empty_and_none_safe():
    assert _normalize_heading("") == ""
    assert _normalize_heading(None) == ""  # type: ignore[arg-type]


# --- classify_pairs_by_template ------------------------------------------


def _file_entry(rel_path: str, heading_texts: list[str]) -> dict:
    return {
        "relative_path": rel_path,
        "headings": [{"id": f"x.{i}", "text": t} for i, t in enumerate(heading_texts)],
    }


def _pair(rel_a: str, rel_b: str, similarity: float) -> dict:
    return {
        "similarity": similarity,
        "a": {"relative_path": rel_a, "section_id": f"{rel_a}.1"},
        "b": {"relative_path": rel_b, "section_id": f"{rel_b}.1"},
    }


def test_classify_template_effect_high_jaccard_low_body():
    # Same headings, different body content.
    map_data = {
        "files": [
            _file_entry("a.md", ["Опоры", "Проверено", "Где использовать"]),
            _file_entry("b.md", ["Опоры", "Проверено", "Где использовать"]),
        ]
    }
    out = classify_pairs_by_template([_pair("a.md", "b.md", 0.75)], map_data)
    assert len(out) == 1
    assert out[0]["classification"] == "TEMPLATE_EFFECT"
    assert out[0]["heading_jaccard"] == pytest.approx(1.0)


def test_classify_semantic_smear_low_jaccard_high_body():
    # Different headings, same content topic.
    map_data = {
        "files": [
            _file_entry("a.md", ["Intro"]),
            _file_entry("b.md", ["Conclusion"]),
        ]
    }
    out = classify_pairs_by_template([_pair("a.md", "b.md", 0.90)], map_data)
    assert out[0]["classification"] == "SEMANTIC_SMEAR"


def test_classify_full_duplicate_both_high():
    map_data = {
        "files": [
            _file_entry("a.md", ["Intro", "Body", "Conclusion"]),
            _file_entry("b.md", ["Intro", "Body", "Conclusion"]),
        ]
    }
    out = classify_pairs_by_template([_pair("a.md", "b.md", 0.95)], map_data)
    assert out[0]["classification"] == "FULL_DUPLICATE"


def test_classify_unclassified_when_both_low():
    map_data = {
        "files": [
            _file_entry("a.md", ["Intro"]),
            _file_entry("b.md", ["Conclusion"]),
        ]
    }
    out = classify_pairs_by_template([_pair("a.md", "b.md", 0.70)], map_data)
    assert out[0]["classification"] == "UNCLASSIFIED"


def test_classify_missing_file_in_map_falls_back_to_empty_set():
    # Pair references a file the map doesn't know — should not crash;
    # heading sets become empty, jaccard 0.
    map_data = {"files": [_file_entry("a.md", ["A"])]}
    out = classify_pairs_by_template([_pair("a.md", "ghost.md", 0.95)], map_data)
    assert out[0]["heading_jaccard"] == 0.0
    assert out[0]["classification"] == "SEMANTIC_SMEAR"  # body high, jaccard 0


# --- detect_intra_file_drift ---------------------------------------------


def _make_drift_index(tmp_path, files_to_vectors):
    """Build a minimal in-memory SQLite with the schema audit.detect_intra_file_drift
    expects: sections + chunks + sections_vec. files_to_vectors maps
    relative_path → list of (heading_chain, np.array) — one entry per section."""
    import numpy as np  # type: ignore

    db = tmp_path / "stub.sqlite"
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE sections (rowid INTEGER PRIMARY KEY, section_id TEXT, "
        "scope TEXT, file_id INTEGER, relative_path TEXT, start_line INTEGER, "
        "level INTEGER, heading_text TEXT, heading_chain TEXT, body TEXT, "
        "file_description TEXT, file_title TEXT, content_hash TEXT, "
        "token_count INTEGER)"
    )
    conn.execute(
        "CREATE TABLE chunks (chunk_id INTEGER PRIMARY KEY, section_rowid INTEGER, "
        "chunk_idx INTEGER, chunk_hash TEXT, chunk_body TEXT)"
    )
    conn.execute(
        "CREATE TABLE sections_vec (rowid INTEGER PRIMARY KEY, embedding BLOB)"
    )

    next_rowid = 1
    next_chunk = 1
    fid = 1
    for rel_path, sections in files_to_vectors.items():
        for i, (heading_chain, vec) in enumerate(sections):
            vec = np.asarray(vec, dtype="float32")
            norm = float(np.linalg.norm(vec))
            if norm > 1e-12:
                vec = vec / norm
            conn.execute(
                "INSERT INTO sections VALUES (?, ?, 'sections', ?, ?, ?, 2, ?, ?, '', '', '', ?, 100)",
                (next_rowid, f"{fid}.{i}", fid, rel_path, i + 1, heading_chain, heading_chain, f"hash{next_rowid}"),
            )
            conn.execute(
                "INSERT INTO chunks VALUES (?, ?, 0, ?, '')",
                (next_chunk, next_rowid, f"ch{next_chunk}"),
            )
            conn.execute(
                "INSERT INTO sections_vec VALUES (?, ?)",
                (next_chunk, vec.tobytes()),
            )
            next_rowid += 1
            next_chunk += 1
        fid += 1
    conn.commit()
    return conn


def test_detect_intra_file_drift_flags_split_file(tmp_path):
    """A single file with two disjoint topic clusters (orthogonal vectors)
    must be flagged."""
    import numpy as np  # type: ignore

    # 6 sections: 3 around topic A (axis 0), 3 around topic B (axis 5).
    sections = []
    for i in range(3):
        v = np.zeros(8)
        v[0] = 1.0
        v[1] = 0.1 * i  # small variation
        sections.append((f"A.{i}", v))
    for i in range(3):
        v = np.zeros(8)
        v[5] = 1.0
        v[6] = 0.1 * i
        sections.append((f"B.{i}", v))

    conn = _make_drift_index(tmp_path, {"drift.md": sections})
    drift = detect_intra_file_drift(conn)
    assert len(drift) == 1
    assert drift[0]["relative_path"] == "drift.md"
    assert drift[0]["section_count"] == 6
    # Two well-separated topics: inter_cluster_sim should be near 0.
    assert drift[0]["inter_cluster_sim"] < 0.4
    assert len(drift[0]["topic_groups"]) >= 2


def test_detect_intra_file_drift_skips_cohesive_file(tmp_path):
    """All sections clustered around one topic → not flagged."""
    import numpy as np  # type: ignore

    sections = []
    for i in range(6):
        v = np.zeros(8)
        v[0] = 1.0
        v[1] = 0.02 * i  # tiny variation in same dimension
        sections.append((f"A.{i}", v))

    conn = _make_drift_index(tmp_path, {"cohesive.md": sections})
    drift = detect_intra_file_drift(conn)
    assert drift == []


def test_detect_intra_file_drift_skips_short_file(tmp_path):
    """Files with < min_sections sections are not evaluated."""
    import numpy as np  # type: ignore

    sections = [
        ("A.0", np.array([1.0, 0, 0, 0, 0, 0, 0, 0])),
        ("A.1", np.array([0, 0, 0, 0, 0, 1.0, 0, 0])),
        ("A.2", np.array([1.0, 0, 0, 0, 0, 0, 0, 0])),
    ]
    conn = _make_drift_index(tmp_path, {"short.md": sections})
    drift = detect_intra_file_drift(conn, min_sections=5)
    assert drift == []


# --- severity classifiers ------------------------------------------------


def test_severity_for_smeared_concept_critical_when_many_files():
    assert severity_for_smeared_concept(unique_files=4, cohesion=0.85) == SEVERITY_CRITICAL


def test_severity_for_smeared_concept_warning_for_2_3_files():
    assert severity_for_smeared_concept(unique_files=2, cohesion=0.6) == SEVERITY_WARNING
    assert severity_for_smeared_concept(unique_files=3, cohesion=0.6) == SEVERITY_WARNING


def test_severity_for_smeared_concept_drop_low_cohesion():
    assert severity_for_smeared_concept(unique_files=2, cohesion=0.3) is None


def test_severity_for_classified_pair():
    assert severity_for_classified_pair("FULL_DUPLICATE") == SEVERITY_CRITICAL
    assert severity_for_classified_pair("SEMANTIC_SMEAR") == SEVERITY_WARNING
    assert severity_for_classified_pair("TEMPLATE_EFFECT") == SEVERITY_INFO
    assert severity_for_classified_pair("UNCLASSIFIED") is None


def test_severity_for_discovery_gap_thresholds():
    assert severity_for_discovery_gap(0.60) == SEVERITY_CRITICAL
    assert severity_for_discovery_gap(0.30) == SEVERITY_WARNING
    assert severity_for_discovery_gap(0.15) == SEVERITY_INFO
    assert severity_for_discovery_gap(0.05) is None


def test_severity_for_intra_file_drift_thresholds():
    assert severity_for_intra_file_drift(3) == SEVERITY_CRITICAL
    assert severity_for_intra_file_drift(2) == SEVERITY_CRITICAL
    assert severity_for_intra_file_drift(1) == SEVERITY_WARNING
    assert severity_for_intra_file_drift(0) is None


# --- health gauge --------------------------------------------------------


def test_health_starts_at_100_clean():
    assert compute_health([]) == 100


def test_health_drops_15_per_critical():
    findings = [{"severity": SEVERITY_CRITICAL} for _ in range(2)]
    assert compute_health(findings) == 100 - 2 * 15


def test_health_drops_5_per_warning():
    findings = [{"severity": SEVERITY_WARNING} for _ in range(4)]
    assert compute_health(findings) == 100 - 4 * 5


def test_health_info_doesnt_deduct():
    findings = [{"severity": SEVERITY_INFO} for _ in range(5)]
    assert compute_health(findings) == 100


def test_health_floors_at_zero():
    findings = [{"severity": SEVERITY_CRITICAL} for _ in range(20)]
    assert compute_health(findings) == 0


def test_severity_counts_match_findings():
    findings = [
        {"severity": SEVERITY_CRITICAL},
        {"severity": SEVERITY_CRITICAL},
        {"severity": SEVERITY_WARNING},
        {"severity": SEVERITY_INFO},
        {"severity": SEVERITY_INFO},
        {"severity": SEVERITY_INFO},
    ]
    counts = severity_counts(findings)
    assert counts == {"critical": 2, "warning": 1, "info": 3}
