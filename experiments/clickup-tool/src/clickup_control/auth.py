from __future__ import annotations

import os
import re
import stat
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

TOKEN_PATTERN = re.compile(r"\bpk_[A-Za-z0-9_-]+\b")
KEYCHAIN_SERVICE = "agentic-research.clickup-control"
KEYCHAIN_ACCOUNT = "triton"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TOKEN_FILE = PROJECT_ROOT / "api_key.md"


class TokenNotFoundError(RuntimeError):
    """Raised when no supported credential source contains a token."""


@dataclass(frozen=True)
class ResolvedToken:
    value: str = field(repr=False)
    source: str


def parse_token(text: str) -> str:
    match = TOKEN_PATTERN.search(text)
    if not match:
        raise TokenNotFoundError("No ClickUp personal token beginning with pk_ was found")
    return match.group(0)


def token_file_mode(path: Path = DEFAULT_TOKEN_FILE) -> str | None:
    if not path.exists():
        return None
    return stat.filemode(path.stat().st_mode)


def _require_private_file(path: Path) -> None:
    permissions = stat.S_IMODE(path.stat().st_mode)
    if permissions & 0o077:
        raise PermissionError(
            f"Refusing to read {path}: expected private mode 0600, got {permissions:04o}"
        )


def _read_keychain() -> str | None:
    try:
        completed = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                KEYCHAIN_ACCOUNT,
                "-w",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    value = completed.stdout.strip()
    return parse_token(value) if value else None


def resolve_token(
    environ: Mapping[str, str] | None = None,
    token_file: Path = DEFAULT_TOKEN_FILE,
) -> ResolvedToken:
    environment = os.environ if environ is None else environ
    env_value = environment.get("CLICKUP_API_TOKEN", "").strip()
    if env_value:
        return ResolvedToken(parse_token(env_value), "environment")

    keychain_value = _read_keychain()
    if keychain_value:
        return ResolvedToken(keychain_value, "keychain")

    if token_file.exists():
        _require_private_file(token_file)
        return ResolvedToken(parse_token(token_file.read_text(encoding="utf-8")), str(token_file))

    raise TokenNotFoundError(
        "Set CLICKUP_API_TOKEN, add the token to macOS Keychain, or create ignored api_key.md"
    )
