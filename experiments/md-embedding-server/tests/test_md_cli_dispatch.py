from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from md_cli.catalog import TOOLS


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


def test_version() -> None:
    result = _run_md("--version")
    assert result.returncode == 0
    assert "md-tools 0.7.0" in result.stdout


def test_help_mentions_all_subcommands() -> None:
    result = _run_md("--help")
    assert result.returncode == 0
    for tool in TOOLS:
        assert tool.subcommand in result.stdout


def test_nonexistent_subcommand_exits_2() -> None:
    result = _run_md("nonexistent_tool")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_help_is_lazy() -> None:
    code = """
import sys
from md_cli.main import main

sys.argv = ["md", "--help"]
try:
    rc = main()
except SystemExit as exc:
    rc = exc.code
print("networkx in modules:", "networkx" in sys.modules)
raise SystemExit(rc)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "networkx in modules: False" in result.stdout
