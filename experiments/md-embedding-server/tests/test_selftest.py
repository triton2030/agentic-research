from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def test_selftest_fixture_corpus_passes() -> None:
    result = _run_md("selftest", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["summary"] == {"pass": 28, "fail": 0, "skip": 1, "total": 29}
    assert payload["_envelope"]["tool"] == "md_selftest"


def test_selftest_single_tool() -> None:
    result = _run_md("selftest", "--tool", "md_orient", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["summary"] == {"pass": 1, "fail": 0, "skip": 0, "total": 1}


def test_selftest_human_summary() -> None:
    result = _run_md("selftest")
    assert result.returncode == 0
    assert "Pass: 28/29" in result.stdout

