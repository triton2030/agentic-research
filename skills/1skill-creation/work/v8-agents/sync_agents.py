#!/usr/bin/env python3
"""Render, install, and verify the official 1skill-creation agents."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "sources"
PROJECTION_ROOT = ROOT / "projections"
ROLE_NAMES = (
    "skill-creation-instruction-auditor",
    "skill-creation-trajectory-reviewer",
)


@dataclass(frozen=True)
class Role:
    name: str
    description: str
    instructions: str


def parse_source(path: Path) -> Role:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError(f"{path}: expected a YAML-style metadata header")

    header_text, instructions = text[4:].split("\n---\n", 1)
    if instructions.startswith("\n"):
        instructions = instructions[1:]
    header: dict[str, str] = {}
    for line in header_text.splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key or not value.strip():
            raise ValueError(f"{path}: invalid metadata line: {line!r}")
        header[key] = value.strip()

    if set(header) != {"name", "description"}:
        raise ValueError(f"{path}: metadata must contain only name and description")
    if header["name"] != path.stem:
        raise ValueError(f"{path}: filename and agent name differ")
    if not instructions.startswith("# ") or not instructions.endswith("\n"):
        raise ValueError(f"{path}: instructions must be complete Markdown ending in a newline")
    if '"""' in instructions:
        raise ValueError(f"{path}: instructions cannot contain a TOML triple quote")

    return Role(header["name"], header["description"], instructions)


def render_claude(role: Role) -> str:
    description = "\n".join(
        f"  {line}" for line in textwrap.wrap(role.description, width=76)
    )
    return (
        "---\n"
        f"name: {role.name}\n"
        "description: >\n"
        f"{description}\n"
        "tools: Read, Grep, Glob\n"
        "---\n\n"
        f"{role.instructions}"
    )


def render_codex(role: Role) -> str:
    name = json.dumps(role.name, ensure_ascii=False)
    description = json.dumps(role.description, ensure_ascii=False)
    return (
        f"name = {name}\n"
        f"description = {description}\n"
        'model_reasoning_effort = "high"\n'
        'sandbox_mode = "read-only"\n\n'
        'developer_instructions = """\n'
        f"{role.instructions}"
        '"""\n'
    )


def expected_projections() -> dict[Path, str]:
    roles = [parse_source(SOURCE_ROOT / f"{name}.md") for name in ROLE_NAMES]
    expected: dict[Path, str] = {}
    for role in roles:
        expected[PROJECTION_ROOT / "claude" / f"{role.name}.md"] = render_claude(role)
        expected[PROJECTION_ROOT / "codex" / f"{role.name}.toml"] = render_codex(role)
    return expected


def unexpected_projection_files(expected: dict[Path, str]) -> list[Path]:
    if not PROJECTION_ROOT.is_dir():
        return []
    actual = {path for path in PROJECTION_ROOT.rglob("*") if path.is_file()}
    return sorted(actual - set(expected))


def write_projections(expected: dict[Path, str]) -> None:
    unexpected = unexpected_projection_files(expected)
    if unexpected:
        paths = ", ".join(str(path.relative_to(ROOT)) for path in unexpected)
        raise ValueError(f"refusing to delete unexpected projection files: {paths}")
    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def installed_root(runtime: str) -> Path:
    override = os.environ.get(f"SKILL_CREATION_{runtime.upper()}_AGENT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    runtime_home = ".codex" if runtime == "codex" else ".claude"
    return Path.home() / runtime_home / "agents"


def install_projections(expected: dict[Path, str]) -> None:
    for source in expected:
        runtime = source.parent.name
        destination = installed_root(runtime) / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def check_projection_files(expected: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, content in expected.items():
        if not path.is_file():
            errors.append(f"missing projection: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"stale projection: {path.relative_to(ROOT)}")
    for path in unexpected_projection_files(expected):
        errors.append(f"unexpected projection: {path.relative_to(ROOT)}")
    return errors


def check_installed_files(expected: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for source, content in expected.items():
        runtime = source.parent.name
        installed = installed_root(runtime) / source.name
        if not installed.is_file():
            errors.append(f"missing installed {runtime} agent: {installed}")
        elif installed.read_text(encoding="utf-8") != content:
            errors.append(f"drifted installed {runtime} agent: {installed}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="render tracked projections")
    parser.add_argument(
        "--install",
        action="store_true",
        help="install rendered projections; requires --write",
    )
    parser.add_argument("--check", action="store_true", help="verify tracked projections")
    parser.add_argument(
        "--check-installed",
        action="store_true",
        help="verify the two files in each official global agent directory",
    )
    args = parser.parse_args()

    if args.install and not args.write:
        parser.error("--install requires --write")
    if not any((args.write, args.install, args.check, args.check_installed)):
        parser.error("choose --write, --install, --check, or --check-installed")

    try:
        expected = expected_projections()
        if args.write:
            write_projections(expected)
            print("rendered Claude Markdown and Codex TOML projections")
        if args.install:
            install_projections(expected)
            print("installed both named agents for Claude and Codex")

        errors: list[str] = []
        if args.check or args.write:
            errors.extend(check_projection_files(expected))
        if args.check_installed or args.install:
            errors.extend(check_installed_files(expected))
        if errors:
            print(*errors, sep="\n", file=sys.stderr)
            return 1
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2

    print("all requested agent projections match their semantic sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
