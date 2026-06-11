from __future__ import annotations

from pathlib import Path

from md_cli.envelope import wrap


def test_owner_blind_search_suggests_canon_scope(tmp_path: Path) -> None:
    (tmp_path / ".md-tools.toml").write_text('[canon]\nroot = ["01_*"]\n', encoding="utf-8")

    payload = wrap(
        {"results": [{"path": "x.md"}]},
        tool_name="md_search",
        args={"corpus": str(tmp_path), "query": "правило"},
    )

    steps = payload["_envelope"]["next_step"]
    assert steps[0]["tool"] == "md_search"
    assert steps[0]["args"]["path_include"] == ["01_*"]


def test_owner_blind_search_respects_existing_scope(tmp_path: Path) -> None:
    (tmp_path / ".md-tools.toml").write_text('[canon]\nroot = ["01_*"]\n', encoding="utf-8")

    payload = wrap(
        {"results": [{"path": "x.md"}]},
        tool_name="md_search",
        args={"corpus": str(tmp_path), "query": "правило", "path_include": ["02_*"]},
    )

    assert payload["_envelope"]["next_step"] == []


def test_empty_search_handler_takes_precedence(tmp_path: Path) -> None:
    (tmp_path / ".md-tools.toml").write_text('[canon]\nroot = ["01_*"]\n', encoding="utf-8")

    payload = wrap(
        {"empty": True},
        tool_name="md_search",
        args={"corpus": str(tmp_path), "query": "missing"},
    )

    assert payload["_envelope"]["next_step"][0]["args"]["scope"] == "descriptions"


def test_profiles_silent_zero_guidance() -> None:
    payload = wrap(
        {"sections": []},
        tool_name="md_query_by_type",
        args={"corpus": "knowledge", "types": ["rule"]},
    )

    steps = payload["_envelope"]["next_step"]
    assert steps[0]["tool"] == "md_profile_sections"
    assert steps[0]["args"]["dry_run"] is True


def test_canon_check_read_next_is_forwarded() -> None:
    payload = wrap(
        {"read_next": [{"tool": "md_search_read", "args": {"corpus": "c", "query": "q"}, "reason": "read"}]},
        tool_name="md_canon_check",
        args={"file": "a.md", "corpus": "c"},
    )

    assert payload["_envelope"]["next_step"][0]["tool"] == "md_search_read"
