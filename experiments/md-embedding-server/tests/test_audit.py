"""Integration smoke for `audit` command — uses `tiny_corpus` + `mock_embed`
fixtures so no network or real API key. Verifies:
  * cmd_audit returns 0
  * JSON output matches AUDIT_SCHEMA required fields
  * Findings have severity / class / evidence / next_step
  * Health gauge / severity_counts shape
"""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from navigator.audit import cmd_audit
from navigator.index import cmd_index
from navigator.schemas import ALL_SCHEMAS


def _audit_args(corpus: Path, **overrides) -> Namespace:
    base = dict(
        path=str(corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        no_cache=False,
        path_include=[],
        path_exclude=[],
        threshold_smear=0.85,
        threshold_drift=0.65,
        threshold_inter=0.40,
        threshold_template=0.70,
        min_sections_per_file=5,
        max_concepts=10,
        cluster_k=4,
        discovery_gap_warn=0.25,
        discovery_gap_crit=0.50,
        output=None,
        stdout=False,
        json=True,  # default to JSON in tests so we can parse
    )
    base.update(overrides)
    return Namespace(**base)


def _index(corpus: Path) -> None:
    args = Namespace(
        path=str(corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )
    assert cmd_index(args) == 0


def test_audit_smoke_runs_on_tiny_corpus(tiny_corpus: Path, mock_embed, capsys):
    _index(tiny_corpus)
    capsys.readouterr()

    rc = cmd_audit(_audit_args(tiny_corpus))
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)

    required = {"root", "health", "severity_counts", "findings", "stats", "engine"}
    assert required <= set(payload.keys()), f"Missing keys: {required - set(payload.keys())}"
    assert isinstance(payload["health"], int)
    assert 0 <= payload["health"] <= 100


def test_audit_json_matches_schema_top_level(tiny_corpus: Path, mock_embed, capsys):
    _index(tiny_corpus)
    capsys.readouterr()

    assert cmd_audit(_audit_args(tiny_corpus)) == 0
    payload = json.loads(capsys.readouterr().out)

    schema = ALL_SCHEMAS["audit"]
    required_top = set(schema["required"])
    assert required_top <= set(payload.keys())

    sc = payload["severity_counts"]
    assert set(sc.keys()) == {"critical", "warning", "info"}
    assert all(isinstance(v, int) for v in sc.values())


def test_audit_findings_have_required_fields(tiny_corpus: Path, mock_embed, capsys):
    _index(tiny_corpus)
    capsys.readouterr()

    assert cmd_audit(_audit_args(tiny_corpus)) == 0
    payload = json.loads(capsys.readouterr().out)
    for f in payload["findings"]:
        assert {"class", "severity", "label", "evidence", "next_step"} <= set(f.keys())
        assert f["severity"] in {"critical", "warning", "info"}
        assert f["class"] in {
            "smeared_owner_truth",
            "tight_duplicates",
            "intra_file_drift",
            "discovery_gaps",
            "cluster_folder_mismatch",
        }


def test_audit_stdout_mode_prints_markdown(tiny_corpus: Path, mock_embed, capsys):
    _index(tiny_corpus)
    capsys.readouterr()

    args = _audit_args(tiny_corpus, json=False, stdout=True)
    assert cmd_audit(args) == 0
    out = capsys.readouterr().out
    assert "# Markdown audit:" in out
    assert "**Health:" in out


def test_audit_default_writes_file_and_prints_summary(
    tiny_corpus: Path, mock_embed, capsys
):
    _index(tiny_corpus)
    capsys.readouterr()

    args = _audit_args(tiny_corpus, json=False, stdout=False)
    assert cmd_audit(args) == 0
    out = capsys.readouterr().out
    assert "Audit →" in out
    audit_md = tiny_corpus / ".md-navigator" / "audit.md"
    assert audit_md.exists()
    assert "# Markdown audit:" in audit_md.read_text(encoding="utf-8")
