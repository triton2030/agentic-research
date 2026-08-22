#!/usr/bin/env python3
"""Inspect a repository's Mantine integration without changing it."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".next",
    ".turbo",
    ".cache",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
}
SOURCE_SUFFIXES = {".css", ".cjs", ".js", ".jsx", ".mjs", ".scss", ".ts", ".tsx"}
DEPENDENCY_FIELDS = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
FRAMEWORK_PACKAGES = {
    "@remix-run/react",
    "astro",
    "gatsby",
    "next",
    "react",
    "react-dom",
    "react-router",
    "react-router-dom",
    "vite",
}
MANTINE_REF_RE = re.compile(r"['\"](@mantine/[a-z0-9-]+(?:/[^'\"]*)?)['\"]", re.I)
STYLE_IMPORT_RE = re.compile(
    r"@mantine/(?P<package>[a-z0-9-]+)/styles(?P<layer>\.layer)?(?:/[A-Za-z0-9_.-]+)?\.css",
    re.I,
)


def walk_files(root: Path, *, names: set[str] | None = None, suffixes: set[str] | None = None):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith(".venv"))
        for filename in sorted(files):
            if names is not None and filename not in names:
                continue
            path = Path(current) / filename
            if suffixes is not None and path.suffix.lower() not in suffixes:
                continue
            yield path


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, str(error)
    if not isinstance(value, dict):
        return None, "top-level JSON value is not an object"
    return value, None


def inspect_manifests(root: Path):
    declarations: list[dict[str, str]] = []
    frameworks: list[dict[str, str]] = []
    manifests: list[str] = []
    errors: list[dict[str, str]] = []

    for path in walk_files(root, names={"package.json"}):
        manifest, error = load_json(path)
        rel = relative(path, root)
        manifests.append(rel)
        if error:
            errors.append({"path": rel, "error": error})
            continue

        assert manifest is not None
        for field in DEPENDENCY_FIELDS:
            values = manifest.get(field, {})
            if not isinstance(values, dict):
                continue
            for package, spec in sorted(values.items()):
                if not isinstance(spec, str):
                    continue
                row = {"manifest": rel, "field": field, "package": package, "spec": spec}
                if package.startswith("@mantine/"):
                    declarations.append(row)
                if package in FRAMEWORK_PACKAGES:
                    frameworks.append(row)

    return manifests, declarations, frameworks, errors


OTHER_LOCKFILES = ("pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb")


def inspect_package_lock(root: Path):
    path = root / "package-lock.json"
    if not path.exists():
        unread = [name for name in OTHER_LOCKFILES if (root / name).exists()]
        return {"path": None, "resolved": [], "error": None, "unread_lockfiles": unread}
    data, error = load_json(path)
    if error:
        return {"path": "package-lock.json", "resolved": [], "error": error}

    resolved: list[dict[str, str]] = []
    packages = data.get("packages", {}) if data else {}
    if isinstance(packages, dict):
        for key, value in sorted(packages.items()):
            marker = "node_modules/@mantine/"
            if marker not in key or not isinstance(value, dict):
                continue
            package = "@mantine/" + key.split(marker, 1)[1].split("/node_modules/", 1)[0]
            version = value.get("version")
            if isinstance(version, str):
                resolved.append({"package": package, "version": version, "lock_key": key})
    return {"path": "package-lock.json", "resolved": resolved, "error": None}


def inspect_sources(root: Path):
    import_files: dict[str, set[str]] = defaultdict(set)
    style_imports: list[dict[str, Any]] = []
    signals: dict[str, list[str]] = defaultdict(list)
    unreadable: list[dict[str, str]] = []

    symbol_patterns = {
        "mantine_provider": re.compile(r"\bMantineProvider\b"),
        "color_scheme_script": re.compile(r"\bColorSchemeScript\b"),
        "mantine_html_props": re.compile(r"\bmantineHtmlProps\b"),
        "create_theme": re.compile(r"\bcreateTheme\s*\("),
        "component_extend": re.compile(r"\.extend\s*\("),
        "styles_prop": re.compile(r"\bstyles\s*="),
        "class_names_prop": re.compile(r"\bclassNames\s*="),
        "private_css_variable": re.compile(r"--_[A-Za-z0-9_-]+"),
        "use_media_query": re.compile(r"\buseMediaQuery\s*\("),
    }

    for path in walk_files(root, suffixes=SOURCE_SUFFIXES):
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            unreadable.append({"path": relative(path, root), "error": str(error)})
            continue

        rel = relative(path, root)
        for package_ref in MANTINE_REF_RE.findall(text):
            package = "/".join(package_ref.split("/")[:2])
            import_files[package].add(rel)

        for match in STYLE_IMPORT_RE.finditer(text):
            style_imports.append(
                {
                    "file": rel,
                    "line": text.count("\n", 0, match.start()) + 1,
                    "package": f"@mantine/{match.group('package')}",
                    "layered": bool(match.group("layer")),
                    "import": match.group(0),
                }
            )

        for name, pattern in symbol_patterns.items():
            if pattern.search(text):
                signals[name].append(rel)

    return {
        "imports": [
            {"package": package, "files": sorted(files)}
            for package, files in sorted(import_files.items())
        ],
        "style_imports": sorted(style_imports, key=lambda row: (row["file"], row["line"])),
        "signals": {name: sorted(files) for name, files in sorted(signals.items())},
        "unreadable": unreadable,
    }


def exact_version(spec: str) -> str | None:
    match = re.fullmatch(r"(?:workspace:)?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)", spec.strip())
    return match.group(1) if match else None


def version_hint(spec: str) -> str | None:
    match = re.search(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", spec)
    return match.group(0) if match else None


def derive_findings(declarations, lock, sources):
    findings: list[dict[str, Any]] = []
    specs_by_package: dict[str, set[str]] = defaultdict(set)
    exact_versions: set[str] = set()
    declared_version_hints: set[str] = set()
    for row in declarations:
        specs_by_package[row["package"]].add(row["spec"])
        version = exact_version(row["spec"])
        if version:
            exact_versions.add(version)
        hint = version_hint(row["spec"])
        if hint:
            declared_version_hints.add(hint)

    mixed_specs = {package: sorted(specs) for package, specs in specs_by_package.items() if len(specs) > 1}
    if mixed_specs:
        findings.append(
            {
                "code": "mixed-declared-specs",
                "level": "inspect",
                "detail": mixed_specs,
                "meaning": "The same Mantine package is declared with multiple version specs.",
            }
        )
    if len(exact_versions) > 1:
        findings.append(
            {
                "code": "mixed-exact-versions",
                "level": "inspect",
                "detail": sorted(exact_versions),
                "meaning": "Official guidance requires all @mantine/* packages to use one version.",
            }
        )
    elif len(declared_version_hints) > 1:
        findings.append(
            {
                "code": "mixed-declared-cohort",
                "level": "inspect",
                "detail": sorted(declared_version_hints),
                "meaning": "Mantine dependency specs point at more than one version cohort.",
            }
        )

    if declarations and not lock.get("path"):
        findings.append(
            {
                "code": "unresolved-cohort",
                "level": "inspect",
                "detail": lock.get("unread_lockfiles") or [],
                "meaning": (
                    "This script reads only package-lock.json. The resolved cohort is unverified; "
                    "read the project's own lockfile instead of inferring it from declared ranges."
                ),
            }
        )

    locked_versions = {row["version"] for row in lock.get("resolved", [])}
    if len(locked_versions) > 1:
        findings.append(
            {
                "code": "mixed-locked-versions",
                "level": "inspect",
                "detail": sorted(locked_versions),
                "meaning": "The package lock resolves more than one Mantine version.",
            }
        )

    if sources["signals"].get("private_css_variable"):
        findings.append(
            {
                "code": "private-css-variable",
                "level": "warning",
                "detail": sources["signals"]["private_css_variable"],
                "meaning": "Mantine --_* variables are private and may change in patch releases.",
            }
        )

    style_modes: dict[str, set[bool]] = defaultdict(set)
    for row in sources["style_imports"]:
        style_modes[row["package"]].add(row["layered"])
    mixed_style_modes = sorted(package for package, modes in style_modes.items() if len(modes) > 1)
    if mixed_style_modes:
        findings.append(
            {
                "code": "mixed-style-files",
                "level": "warning",
                "detail": mixed_style_modes,
                "meaning": "Do not import both styles.css and styles.layer.css for one Mantine package.",
            }
        )

    style_rows_by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sources["style_imports"]:
        style_rows_by_file[row["file"]].append(row)
    order_issues: list[dict[str, Any]] = []
    for file, rows in sorted(style_rows_by_file.items()):
        core_lines = [row["line"] for row in rows if row["package"] == "@mantine/core"]
        extension_lines = [row["line"] for row in rows if row["package"] != "@mantine/core"]
        if core_lines and extension_lines and min(core_lines) > min(extension_lines):
            order_issues.append({"file": file, "core_line": min(core_lines), "first_extension_line": min(extension_lines)})
    if order_issues:
        findings.append(
            {
                "code": "core-styles-not-first",
                "level": "warning",
                "detail": order_issues,
                "meaning": "Mantine core styles must be imported before extension package styles.",
            }
        )

    if not declarations and not sources["imports"]:
        findings.append(
            {
                "code": "mantine-not-found",
                "level": "info",
                "detail": [],
                "meaning": "No Mantine dependency declaration or source import was found.",
            }
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON (the default; kept for explicit workflows)")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}, ensure_ascii=False), file=sys.stderr)
        return 2

    manifests, declarations, frameworks, manifest_errors = inspect_manifests(root)
    lock = inspect_package_lock(root)
    sources = inspect_sources(root)
    result = {
        "schema_version": 1,
        "root": str(root),
        "manifests": manifests,
        "mantine_declarations": declarations,
        "framework_declarations": frameworks,
        "package_lock": lock,
        "source": sources,
        "findings": derive_findings(declarations, lock, sources),
        "errors": manifest_errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
