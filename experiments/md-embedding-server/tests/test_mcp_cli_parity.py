from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"

ATOMIC_COMMANDS = {
    "md_ping": ["ping"],
    "md_status": ["status", str(CORPUS)],
    "md_ls": ["ls", str(CORPUS)],
    "md_toc": ["toc", str(CORPUS)],
    "md_read_related": ["read-related", "--paths", str(README), "--scan", str(CORPUS)],
    "md_importance": ["importance", str(CORPUS)],
    "md_extract": ["extract", "--map-data", json.dumps({"root": str(CORPUS), "files": []})],
    "md_search": ["search", str(CORPUS), "--query", "sample"],
    "md_overlaps": ["overlaps", str(CORPUS)],
    "md_repeated_concepts": ["repeated-concepts", str(CORPUS)],
    "md_audit": ["audit", str(CORPUS)],
    "md_corpus_scan": ["corpus-scan", str(CORPUS)],
    "md_index": ["index", str(CORPUS), "--dry-run"],
    "md_init": ["init", "--paths", str(CORPUS), "--dry-run"],
    "md_strip": ["strip", "--paths", str(CORPUS), "--dry-run"],
    "md_profile_sections": ["profile-sections", str(CORPUS), "--dry-run", "--mode", "llm"],
    "md_scan": ["scan", "--paths", str(CORPUS)],
    "md_check": ["check", "--paths", str(CORPUS)],
    "md_health": ["health", "--paths", str(CORPUS)],
    "md_cycles": ["cycles", "--paths", str(CORPUS)],
    "md_deps": ["deps", str(README), "--scan", str(CORPUS)],
    "md_impact": ["impact", str(README), "--scan", str(CORPUS)],
    "md_preflight": ["preflight", str(README), "--scan", str(CORPUS)],
    "md_changed": ["changed", "--scan", str(CORPUS), "--staged"],
}


def _run_md(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args, "--json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_atomic_cli_surface_matches_frozen_mcp_tool_names() -> None:
    snapshot = json.loads((ROOT / "tests" / "golden" / "mcp-tool-snapshot.json").read_text())
    snapshot_names = {tool["name"] for tool in snapshot["tools"]}

    assert set(ATOMIC_COMMANDS) <= snapshot_names
    assert len(ATOMIC_COMMANDS) == 24
    for tool_id, argv in ATOMIC_COMMANDS.items():
        result = _run_md(*argv)
        assert result.returncode in {0, 1, 4}, (tool_id, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["_envelope"]["tool"] == tool_id
        assert payload["_envelope"]["next_step"] is not None


def test_mutating_cli_contract_exposes_transaction_and_fingerprint() -> None:
    result = _run_md("index", str(CORPUS), "--dry-run")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["transaction_id"].startswith("txn_")
    assert len(payload["fingerprint"]) == 32
