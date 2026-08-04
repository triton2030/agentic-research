#!/usr/bin/env python3
"""Render and verify simple shared or runtime-owned skill projections."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SHARED_ROOT = Path(__file__).resolve().parent
SKILLS_ROOT = SHARED_ROOT.parent
RUNTIMES = ("codex", "claude")


def files_under(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(root.rglob("*"))
        if path.is_file() or path.is_symlink()
    }


def source_manifest(skill: str, runtime: str) -> tuple[str, dict[str, Path]]:
    shared_owner = SHARED_ROOT / skill
    portable = shared_owner / "portable"
    if portable.is_dir():
        manifest = files_under(portable)
        platform = files_under(shared_owner / "platforms" / runtime)
        overlap = sorted(set(manifest) & set(platform))
        if overlap:
            joined = ", ".join(overlap)
            raise ValueError(f"{skill}/{runtime}: platform files shadow portable files: {joined}")
        manifest.update(platform)
        return "shared", manifest

    runtime_owner = SKILLS_ROOT / runtime / skill
    manifest = files_under(runtime_owner)
    if not manifest:
        raise ValueError(f"{skill}/{runtime}: no shared or runtime owner")
    return "runtime", manifest


def tracked_target(skill: str, runtime: str) -> Path:
    return SKILLS_ROOT / runtime / skill


def installed_target(skill: str, runtime: str) -> Path:
    override = os.environ.get(f"SKILL_SYNC_{runtime.upper()}_ROOT")
    if override:
        return Path(override).expanduser().resolve() / skill
    runtime_root = ".codex" if runtime == "codex" else ".claude"
    return Path.home() / runtime_root / "skills" / skill


def unexpected_files(target: Path, manifest: dict[str, Path]) -> list[str]:
    return sorted(set(files_under(target)) - set(manifest))


def write_projection(target: Path, manifest: dict[str, Path], label: str) -> None:
    unexpected = unexpected_files(target, manifest)
    if unexpected:
        joined = ", ".join(unexpected)
        raise ValueError(f"{label}: refusing to delete unexpected files: {joined}")
    for relative, source in manifest.items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def check_projection(
    target: Path,
    manifest: dict[str, Path],
    label: str,
) -> list[str]:
    errors: list[str] = []
    for relative, source in manifest.items():
        destination = target / relative
        if not destination.is_file():
            errors.append(f"{label}: missing {relative}")
        elif source.read_bytes() != destination.read_bytes():
            errors.append(f"{label}: drifted {relative}")
    for relative in unexpected_files(target, manifest):
        errors.append(f"{label}: unexpected {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skills", nargs="+", help="skill package names")
    parser.add_argument("--write", action="store_true", help="render tracked shared projections")
    parser.add_argument(
        "--install",
        action="store_true",
        help="also render installed projections; requires --write",
    )
    parser.add_argument("--check", action="store_true", help="verify tracked and installed projections")
    args = parser.parse_args()

    if args.install and not args.write:
        parser.error("--install requires --write")
    if not args.write and not args.check:
        parser.error("choose --write or --check")

    packages: list[tuple[str, str, str, dict[str, Path]]] = []
    try:
        for skill in args.skills:
            for runtime in RUNTIMES:
                owner_kind, manifest = source_manifest(skill, runtime)
                packages.append((skill, runtime, owner_kind, manifest))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    try:
        if args.write:
            for skill, runtime, owner_kind, manifest in packages:
                if owner_kind == "shared":
                    target = tracked_target(skill, runtime)
                    write_projection(target, manifest, f"tracked {runtime}/{skill}")
                    print(f"wrote tracked {runtime}/{skill}")
                if args.install:
                    target = installed_target(skill, runtime)
                    write_projection(target, manifest, f"installed {runtime}/{skill}")
                    print(f"wrote installed {runtime}/{skill}")
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    if args.check or args.write:
        errors: list[str] = []
        for skill, runtime, owner_kind, manifest in packages:
            if owner_kind == "shared":
                errors.extend(
                    check_projection(
                        tracked_target(skill, runtime),
                        manifest,
                        f"tracked {runtime}/{skill}",
                    )
                )
            errors.extend(
                check_projection(
                    installed_target(skill, runtime),
                    manifest,
                    f"installed {runtime}/{skill}",
                )
            )
        if errors:
            print(*errors, sep="\n", file=sys.stderr)
            return 1
        print("all requested tracked and installed projections match their owners")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
