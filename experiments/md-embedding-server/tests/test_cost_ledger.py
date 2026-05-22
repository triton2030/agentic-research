from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from md_cli.cost_ledger import get_cost_snapshot, record_cost


ROOT = Path(__file__).resolve().parents[1]


def test_cost_ledger_records_and_aggregates(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path))
    monkeypatch.setenv("MD_CLI_SESSION_ID", "unit")
    record_cost(0.123456)
    assert get_cost_snapshot() == {"turn_usd": 0.1235, "session_usd": 0.1235}


def test_cost_ledger_concurrent_appends(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["MD_TOOLS_CACHE_DIR"] = str(tmp_path)
    env["MD_CLI_SESSION_ID"] = "concurrent"
    env["PYTHONPATH"] = str(ROOT / "src")
    code = "from md_cli.cost_ledger import record_cost; record_cost(0.1)"
    procs = [
        subprocess.Popen([sys.executable, "-c", code], cwd=ROOT, env=env)
        for _ in range(4)
    ]
    for proc in procs:
        assert proc.wait(timeout=10) == 0
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json; from md_cli.cost_ledger import get_cost_snapshot; print(json.dumps(get_cost_snapshot()))",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout) == {"turn_usd": 0.4, "session_usd": 0.4}

