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


def test_doctor_json_shape() -> None:
    result = _run_md("doctor", "--json")
    payload = json.loads(result.stdout)
    assert "checks" in payload
    assert payload["_envelope"]["tool"] == "md_doctor"
    ok_or_warn = [check for check in payload["checks"] if check["status"] in {"OK", "WARN"}]
    assert len(ok_or_warn) / len(payload["checks"]) >= 0.8


def test_doctor_human_report() -> None:
    result = _run_md("doctor")
    assert "Check" in result.stdout
    assert "python >=3.11" in result.stdout

