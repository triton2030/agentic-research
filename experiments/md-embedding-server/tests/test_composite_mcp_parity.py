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
        [sys.executable, "-m", "md_cli", *args, "--json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_composite_cli_tools_keep_mcp_envelope_names() -> None:
    commands = {
        "md_orient": ["orient", str(CORPUS), "--compact"],
        "md_edit_context": ["edit-context", str(README), "--scan", str(CORPUS), "--mode", "strict"],
        "md_query_by_type": ["query-by-type", str(CORPUS), "--types", "rule"],
        "md_refactor_candidates": ["refactor-candidates", str(CORPUS), "--compact"],
    }

    for tool_id, argv in commands.items():
        result = _run_md(*argv)
        assert result.returncode in {0, 1, 4}, (tool_id, result.stderr)
        payload = json.loads(result.stdout)
        assert payload["_envelope"]["tool"] == tool_id
        assert payload["_envelope"]["size_estimate"]["bytes"] is not None
