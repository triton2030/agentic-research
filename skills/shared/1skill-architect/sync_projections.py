#!/usr/bin/env python3
"""Render and verify tracked and installed 1skill-architect projections."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


OWNER_ROOT = Path(__file__).resolve().parent
SKILLS_ROOT = OWNER_ROOT.parents[1]
PORTABLE_ROOT = OWNER_ROOT / "portable"

PORTABLE_FILES = (
    "SKILL.md",
    "references/design.md",
    "references/evidence.md",
    "references/failures.md",
)

PLATFORM_FILES = {
    "codex": ("agents/openai.yaml",),
    "claude": (),
}

OBSOLETE_FILES = {
    "codex": (
        "GLOSSARY.md",
        "references/anti-patterns.md",
        "references/check.md",
        "references/codex-skill-authoring.md",
        "references/deep-audit.md",
        "references/description.md",
        "references/local-skill-contract.md",
        "references/platform-skill-authoring.md",
        "references/protocol.md",
    ),
    "claude": (
        "GLOSSARY.md",
        "references/anti-patterns.md",
        "references/check.md",
        "references/claude-skill-authoring.md",
        "references/deep-audit.md",
        "references/description.md",
        "references/local-skill-contract.md",
        "references/platform-skill-authoring.md",
        "references/protocol.md",
    ),
}


def source_manifest(runtime: str) -> dict[str, Path]:
    manifest = {name: PORTABLE_ROOT / name for name in PORTABLE_FILES}
    platform_root = OWNER_ROOT / "platforms" / runtime
    manifest.update({name: platform_root / name for name in PLATFORM_FILES[runtime]})
    return manifest


def tracked_target(runtime: str) -> Path:
    return SKILLS_ROOT / runtime / "1skill-architect"


def installed_target(runtime: str) -> Path:
    override = os.environ.get(f"SKILL_ARCHITECT_{runtime.upper()}_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    runtime_root = ".codex" if runtime == "codex" else ".claude"
    return Path.home() / runtime_root / "skills" / "1skill-architect"


def write_projection(runtime: str, target: Path) -> None:
    for relative, source in source_manifest(runtime).items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    for relative in OBSOLETE_FILES[runtime]:
        obsolete = target / relative
        if obsolete.is_file() or obsolete.is_symlink():
            obsolete.unlink()


def check_projection(runtime: str, label: str, target: Path) -> list[str]:
    manifest = source_manifest(runtime)
    errors: list[str] = []

    for relative, source in manifest.items():
        destination = target / relative
        if not destination.is_file():
            errors.append(f"{label}: missing {relative}")
        elif source.read_bytes() != destination.read_bytes():
            errors.append(f"{label}: drifted {relative}")

    expected = set(manifest)
    actual = {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_file() or path.is_symlink()
    } if target.is_dir() else set()
    for relative in sorted(actual - expected):
        errors.append(f"{label}: unexpected {relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="render tracked projections")
    parser.add_argument(
        "--install",
        action="store_true",
        help="also render installed projections; requires --write",
    )
    parser.add_argument("--check", action="store_true", help="verify all projections")
    args = parser.parse_args()

    if args.install and not args.write:
        parser.error("--install requires --write")
    if not args.write and not args.check:
        parser.error("choose --write or --check")

    for runtime in PLATFORM_FILES:
        missing_sources = [
            str(path) for path in source_manifest(runtime).values() if not path.is_file()
        ]
        if missing_sources:
            print("missing owner sources:", *missing_sources, sep="\n  ", file=sys.stderr)
            return 2

    if args.write:
        for runtime in PLATFORM_FILES:
            write_projection(runtime, tracked_target(runtime))
            print(f"wrote tracked {runtime}")
            if args.install:
                write_projection(runtime, installed_target(runtime))
                print(f"wrote installed {runtime}")

    if args.check or args.write:
        errors: list[str] = []
        for runtime in PLATFORM_FILES:
            errors.extend(check_projection(runtime, f"tracked {runtime}", tracked_target(runtime)))
            errors.extend(
                check_projection(runtime, f"installed {runtime}", installed_target(runtime))
            )
        if errors:
            print(*errors, sep="\n", file=sys.stderr)
            return 1
        print("all tracked and installed projections match the shared owner")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
