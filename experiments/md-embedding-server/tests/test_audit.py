"""Integration smoke for the `audit` command — uses `tiny_corpus` + `mock_embed`
fixtures so no network or real API key. Verifies, against the canonical
importable surface `navigator.api`:
  * api.audit succeeds (no error _exit_code)
  * payload matches AUDIT_SCHEMA required fields
  * Findings (expanded mode) carry severity / class / evidence / next_step
  * Health gauge / severity_counts shape
  * render_audit turns the payload into the doctor's-report Markdown
"""

from __future__ import annotations

from pathlib import Path

from navigator.api import audit as api_audit
from navigator.api import index as api_index
from navigator.audit_render import render_audit
from navigator.schemas import ALL_SCHEMAS


_AUDIT_KWARGS = dict(
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
)


def _audit(corpus: Path, **overrides) -> dict:
    kwargs = dict(_AUDIT_KWARGS)
    kwargs.update(overrides)
    return api_audit(str(corpus), **kwargs)


def _index(corpus: Path) -> None:
    payload = api_index(
        str(corpus),
        confirm=True,
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )
    assert payload.get("_exit_code", 0) == 0


def test_audit_smoke_runs_on_tiny_corpus(tiny_corpus: Path, mock_embed):
    _index(tiny_corpus)

    payload = _audit(tiny_corpus)
    assert payload.get("_exit_code", 0) == 0

    required = {"root", "health", "severity_counts", "findings", "stats", "engine"}
    assert required <= set(payload.keys()), f"Missing keys: {required - set(payload.keys())}"
    assert isinstance(payload["health"], int)
    assert 0 <= payload["health"] <= 100


def test_audit_json_matches_schema_top_level(tiny_corpus: Path, mock_embed):
    _index(tiny_corpus)

    payload = _audit(tiny_corpus)
    assert payload.get("_exit_code", 0) == 0

    schema = ALL_SCHEMAS["audit"]
    required_top = set(schema["required"])
    assert required_top <= set(payload.keys())

    sc = payload["severity_counts"]
    assert set(sc.keys()) == {"critical", "warning", "info"}
    assert all(isinstance(v, int) for v in sc.values())


def test_audit_findings_have_required_fields(tiny_corpus: Path, mock_embed):
    _index(tiny_corpus)

    # `expanded=True` returns the full audit_payload findings (with `evidence`
    # and every detection class), which is what the legacy `--json` output
    # carried. The default map mode summarises evidence and drops the key.
    payload = _audit(tiny_corpus, expanded=True)
    assert payload.get("_exit_code", 0) == 0
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


def test_audit_render_produces_markdown(tiny_corpus: Path, mock_embed):
    _index(tiny_corpus)

    payload = _audit(tiny_corpus, expanded=True)
    assert payload.get("_exit_code", 0) == 0
    rendered = render_audit(payload)
    assert "# Markdown audit:" in rendered
    assert "**Health:" in rendered
