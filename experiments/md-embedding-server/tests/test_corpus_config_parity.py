"""Parity tests: `.md-tools.toml` applies identically through CLI and MCP.

Critic finding (2026-05-23 review): without an explicit test, config-merge
on the CLI side could diverge from the MCP side. Both paths terminate at
`navigator.api.*`, so the merge happens there; this test pins the contract.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from navigator.api import status

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILENAME = ".md-tools.toml"


def _make_corpus_with_config(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    (corpus / "keep").mkdir(parents=True)
    (corpus / "drafts").mkdir(parents=True)
    (corpus / "keep" / "a.md").write_text("# Keep A\n\nContent.\n", encoding="utf-8")
    (corpus / "drafts" / "b.md").write_text("# Drop B\n\nDraft.\n", encoding="utf-8")
    (corpus / CONFIG_FILENAME).write_text(
        "[index]\n"
        'exclude = ["drafts/*"]\n'
        "\n"
        "[graph]\n"
        'exclude = ["drafts/*"]\n',
        encoding="utf-8",
    )
    return corpus


def test_mcp_status_applies_config_exclude(tmp_path: Path) -> None:
    """Calling navigator.api.status directly (MCP path) must surface the
    config exclude in the returned payload's path_scope."""
    corpus = _make_corpus_with_config(tmp_path)
    payload = status(str(corpus))
    excluded = payload.get("excluded", {})
    by_path_exclude = excluded.get("by_path_exclude") or []
    assert "drafts/*" in by_path_exclude


def test_mcp_status_cli_args_append_onto_config(tmp_path: Path) -> None:
    """CLI/MCP-passed path_exclude must APPEND onto the config baseline,
    not replace it (user decision 2026-05-23)."""
    corpus = _make_corpus_with_config(tmp_path)
    payload = status(str(corpus), path_exclude=["experiments/*"])
    excluded = payload.get("excluded", {})
    by_path_exclude = excluded.get("by_path_exclude") or []
    assert "drafts/*" in by_path_exclude, "config baseline lost"
    assert "experiments/*" in by_path_exclude, "CLI append missing"


def test_cli_subprocess_status_applies_config_exclude(tmp_path: Path) -> None:
    """Run `md status` as a subprocess (full CLI dispatch). Same config
    must produce the same path_scope as the MCP-style call above."""
    corpus = _make_corpus_with_config(tmp_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "md_cli", "status", str(corpus), "--json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode in {0, 1, 4}, result.stderr
    payload = json.loads(result.stdout)
    excluded = payload.get("excluded", {})
    by_path_exclude = excluded.get("by_path_exclude") or []
    assert "drafts/*" in by_path_exclude


def test_no_config_returns_empty_filters(tmp_path: Path) -> None:
    """Corpus without .md-tools.toml gets no config-injected filters."""
    corpus = tmp_path / "empty"
    (corpus / "a").mkdir(parents=True)
    (corpus / "a" / "x.md").write_text("# X\n\nbody.\n", encoding="utf-8")
    payload = status(str(corpus))
    excluded = payload.get("excluded", {})
    assert (excluded.get("by_path_exclude") or []) == []
    assert (excluded.get("by_path_include") or []) == []


def test_broken_toml_is_user_facing_error(tmp_path: Path) -> None:
    """Broken .md-tools.toml must raise SystemExit (not silently disable
    filters), so the user sees the problem immediately."""
    corpus = tmp_path / "broken-cfg"
    corpus.mkdir()
    (corpus / "a.md").write_text("# A\n\nx.\n", encoding="utf-8")
    (corpus / CONFIG_FILENAME).write_text("[index\nbroken", encoding="utf-8")
    import pytest

    with pytest.raises(SystemExit) as exc:
        status(str(corpus))
    assert CONFIG_FILENAME in str(exc.value)
