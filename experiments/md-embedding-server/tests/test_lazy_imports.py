from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEAVY = ("networkx", "numpy", "scipy", "pymorphy3", "requests")


def _probe(argv: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    code = f"""
import sys
from md_cli.main import main
sys.argv = {argv!r}
try:
    rc = main()
except SystemExit as exc:
    rc = exc.code
print({HEAVY!r}, [name for name in {HEAVY!r} if name in sys.modules])
raise SystemExit(rc)
"""
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_help_paths_do_not_load_heavy_deps() -> None:
    for argv in [
        ["md", "--help"],
        ["md", "tools", "--help"],
        ["md", "ping", "--help"],
        ["md", "status", "--help"],
    ]:
        result = _probe(argv)
        assert result.returncode == 0
        assert "[]" in result.stdout


def test_tools_list_does_not_load_heavy_deps() -> None:
    result = _probe(["md", "tools"])
    assert result.returncode == 0
    assert "[]" in result.stdout

