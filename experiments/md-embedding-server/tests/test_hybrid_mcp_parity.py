from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests" / "fixtures" / "sample-corpus"
README = CORPUS / "README.md"


def test_section_blast_radius_cli_preserves_mcp_envelope() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "md_cli",
            "section-blast-radius",
            str(README),
            str(CORPUS),
            "--query",
            "sample frontmatter contract",
            "--scan",
            str(CORPUS),
            "--json",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["_envelope"]["tool"] == "md_section_blast_radius"
    assert payload["graph"]["command"] == "preflight"
    assert payload["semantic"]["error"] == "index_warmup_required"
