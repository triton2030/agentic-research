from pathlib import Path

import pytest

from clickup_control.auth import TokenNotFoundError, parse_token, resolve_token


def test_parse_token_extracts_personal_token() -> None:
    assert parse_token("token: pk_example_123") == "pk_example_123"


def test_parse_token_rejects_missing_token() -> None:
    with pytest.raises(TokenNotFoundError):
        parse_token("not a token")


def test_environment_wins_over_file(tmp_path: Path) -> None:
    token_file = tmp_path / "api_key.md"
    token_file.write_text("pk_file_token", encoding="utf-8")
    resolved = resolve_token({"CLICKUP_API_TOKEN": "pk_env_token"}, token_file)
    assert resolved.source == "environment"
    assert resolved.value == "pk_env_token"


def test_insecure_token_file_is_rejected(tmp_path: Path) -> None:
    token_file = tmp_path / "api_key.md"
    token_file.write_text("pk_file_token", encoding="utf-8")
    token_file.chmod(0o644)

    with pytest.raises(PermissionError, match="expected private mode 0600"):
        resolve_token({}, token_file)
