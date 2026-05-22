from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


def _run_md(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_all_30_cli_subcommands_emit_json_envelope() -> None:
    map_json = json.dumps(_run_json("ls", str(CORPUS)) | {"_envelope": None})
    commands = [
        ("ping",),
        ("status", str(CORPUS)),
        ("ls", str(CORPUS)),
        ("toc", str(CORPUS)),
        ("read-related", "--paths", str(README), "--scan", str(CORPUS), "--mode", "preview"),
        ("importance", str(CORPUS)),
        ("extract", "--map-data", map_json, "--files", "1"),
        ("search", str(CORPUS), "--query", "sample"),
        ("search-read", str(CORPUS), "--query", "sample"),
        ("overlaps", str(CORPUS)),
        ("repeated-concepts", str(CORPUS)),
        ("audit", str(CORPUS)),
        ("corpus-scan", str(CORPUS)),
        ("preflight", str(README), "--scan", str(CORPUS)),
        ("impact", str(README), "--scan", str(CORPUS)),
        ("deps", str(README), "--scan", str(CORPUS)),
        ("check", "--paths", str(CORPUS)),
        ("scan", "--paths", str(CORPUS)),
        ("health", "--paths", str(CORPUS)),
        ("cycles", "--paths", str(CORPUS)),
        ("changed", "--scan", str(CORPUS), "--staged"),
        ("init", "--paths", str(CORPUS), "--dry-run"),
        ("strip", "--paths", str(CORPUS), "--dry-run"),
        ("index", str(CORPUS), "--dry-run"),
        ("profile-sections", str(CORPUS), "--dry-run", "--mode", "llm"),
        ("orient", str(CORPUS), "--compact"),
        ("edit-context", str(README), "--scan", str(CORPUS), "--mode", "strict"),
        ("refactor-candidates", str(CORPUS), "--compact"),
        ("query-by-type", str(CORPUS), "--types", "rule"),
        ("section-blast-radius", str(README), str(CORPUS), "--query", "sample", "--scan", str(CORPUS)),
    ]
    assert len(commands) == 30
    for command in commands:
        result = _run_md(*command, "--json")
        assert result.returncode in {0, 1, 4}, (command, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["_envelope"]["tool"].startswith("md_")


def _run_json(*args: str) -> dict[str, object]:
    result = _run_md(*args, "--json")
    assert result.returncode == 0
    return json.loads(result.stdout)
