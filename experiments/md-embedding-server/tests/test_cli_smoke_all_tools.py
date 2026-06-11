from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


def _run_md(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _smoke_commands(corpus: str, readme: str, map_json: str) -> list[tuple[str, ...]]:
    return [
        ("ping",),
        ("status", corpus),
        ("ls", corpus),
        ("toc", corpus),
        ("read-related", "--paths", readme, "--scan", corpus, "--mode", "preview"),
        ("coherence-audit", readme, "--scan", corpus, "--depth", "1"),
        ("walk", readme, "--anchor", "Rule", "--scan", corpus, "--depth", "1"),
        ("importance", corpus),
        ("extract", "--map-data", map_json, "--files", "1"),
        ("search", corpus, "--query", "sample"),
        ("search-read", corpus, "--query", "sample"),
        ("semantic-neighbors", readme, corpus),
        ("overlaps", corpus),
        ("repeated-concepts", corpus),
        ("audit", corpus),
        ("corpus-scan", corpus),
        ("canon-check", readme, corpus),
        ("preflight", readme, "--scan", corpus),
        ("impact", readme, "--scan", corpus),
        ("deps", readme, "--scan", corpus),
        ("check", "--paths", corpus),
        ("scan", "--paths", corpus),
        ("health", "--paths", corpus),
        ("cycles", "--paths", corpus),
        ("cluster", corpus),
        ("init", "--paths", corpus, "--dry-run"),
        ("strip", "--paths", corpus, "--dry-run"),
        ("index", corpus, "--dry-run"),
        ("profile-sections", corpus, "--dry-run", "--mode", "llm"),
        ("orient", corpus, "--compact"),
        ("edit-context", readme, "--scan", corpus, "--mode", "strict"),
        ("refactor-candidates", corpus, "--compact"),
        ("query-by-type", corpus, "--types", "rule"),
        ("section-blast-radius", readme, corpus, "--query", "sample", "--scan", corpus),
    ]


def test_all_cli_subcommands_emit_json_envelope() -> None:
    map_json = json.dumps(_run_json("ls", str(CORPUS)) | {"_envelope": None})
    commands = _smoke_commands(str(CORPUS), str(README), map_json)
    assert len(commands) >= 33
    for command in commands:
        result = _run_md(*command, "--json")
        assert result.returncode in {0, 1, 4}, (command, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["_envelope"]["tool"].startswith("md_")


def test_all_cli_subcommands_emit_json_from_nested_cwd_with_relative_paths() -> None:
    nested_cwd = ROOT / "src"
    corpus = "../tests/fixtures/sample-corpus"
    readme = "../tests/fixtures/sample-corpus/README.md"
    map_json = json.dumps(
        _run_json("ls", corpus, cwd=nested_cwd) | {"_envelope": None}
    )
    commands = _smoke_commands(corpus, readme, map_json)
    assert len(commands) >= 33
    for command in commands:
        result = _run_md(*command, "--json", cwd=nested_cwd)
        assert result.returncode in {0, 1, 4}, (command, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["_envelope"]["tool"].startswith("md_")


def _run_json(*args: str, cwd: Path = ROOT) -> dict[str, object]:
    result = _run_md(*args, "--json", cwd=cwd)
    assert result.returncode == 0
    return json.loads(result.stdout)
