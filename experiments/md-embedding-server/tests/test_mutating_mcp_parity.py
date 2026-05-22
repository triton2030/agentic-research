from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run_md(cwd: Path, *args: str) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "md_cli", *args, "--json"],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (args, result.stderr, result.stdout)
    return json.loads(result.stdout)


def test_mutating_dry_runs_share_guard_shape(tmp_path: Path) -> None:
    (tmp_path / "plain.md").write_text("# Plain\n", encoding="utf-8")
    (tmp_path / "legacy.md").write_text(
        "---\ndescription: Legacy\nread-before-edit: []\nedit-after-edit: []\nowner: old\n---\n\n# Legacy\n",
        encoding="utf-8",
    )

    commands = {
        "md_init": ["init", "--paths", "plain.md", "--dry-run"],
        "md_strip": ["strip", "--paths", "legacy.md", "--dry-run"],
        "md_index": ["index", str(tmp_path), "--dry-run"],
        "md_profile_sections": ["profile-sections", str(tmp_path), "--dry-run", "--mode", "llm"],
    }

    for tool_id, argv in commands.items():
        payload = _run_md(tmp_path, *argv)
        assert payload["_envelope"]["tool"] == tool_id
        assert payload["dry_run"] is True
        assert payload["transaction_id"].startswith("txn_")
        assert len(payload["fingerprint"]) == 32
        assert isinstance(payload["files"], list)
