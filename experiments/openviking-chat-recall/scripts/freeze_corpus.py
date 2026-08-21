#!/usr/bin/env python3
"""Freeze the chat-recall holder corpus from one explicit Git commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


class FreezeError(ValueError):
    """Raised when the frozen source or generated root is not trustworthy."""


MANIFEST_SCHEMA = "openviking-chat-recall/source-manifest.v1"
LOCK_SCHEMA = "openviking-chat-recall/source-lock.v1"
DEFAULT_SOURCE_ROOT = "_ops/chat-recall"
DEFAULT_OUTPUT_DIR = Path(
    "experiments/openviking-chat-recall/artifacts/full-build/frozen"
)
MANIFEST_NAME = "source-manifest.json"
LOCK_NAME = "source-lock.json"
EXPECTED_HOLDER_COUNT = 184
FULL_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
OID_RE = re.compile(r"^[0-9a-f]{40,64}$")
SOURCE_RULE = "top-level *.md excluding README.md; sorted by relative POSIX path"
SYSTEM_PATH_ALIASES = (Path("/tmp"), Path("/var"))

PARSER_SPEC: dict[str, object] = {
    "blob_read": "git cat-file blob <oid>",
    "holder_rule": SOURCE_RULE,
    "input_mode": "raw Git blob bytes; no semantic record parsing",
    "path_encoding": "UTF-8",
}
CONFIG_SPEC: dict[str, object] = {
    "expected_holder_count": EXPECTED_HOLDER_COUNT,
    "lock_schema": LOCK_SCHEMA,
    "manifest_schema": MANIFEST_SCHEMA,
    "owned_files": [MANIFEST_NAME, LOCK_NAME],
    "source_root": DEFAULT_SOURCE_ROOT,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic source manifest from an explicit Git commit."
    )
    parser.add_argument(
        "--commit",
        required=True,
        help="full 40-character commit SHA; refs, HEAD and abbreviated SHAs are rejected",
    )
    parser.add_argument(
        "--source-root",
        default=DEFAULT_SOURCE_ROOT,
        help=f"repository-relative holder root (must be {DEFAULT_SOURCE_ROOT})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="generated frozen-root directory",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="repository containing the explicit commit",
    )
    return parser.parse_args()


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )


def _git_error(completed: subprocess.CompletedProcess[bytes]) -> str:
    return completed.stderr.decode("utf-8", errors="replace").strip()


def _git_text(repo_root: Path, *args: str) -> str:
    completed = _run_git(repo_root, *args)
    if completed.returncode:
        detail = _git_error(completed)
        raise FreezeError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.decode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_digest(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(payload)


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def normalize_source_root(source_root: str) -> str:
    candidate = Path(source_root)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise FreezeError(f"source root must be repository-relative: {source_root!r}")
    normalized = candidate.as_posix()
    if normalized != DEFAULT_SOURCE_ROOT:
        raise FreezeError(
            f"source root drift: expected {DEFAULT_SOURCE_ROOT!r}, got {normalized!r}"
        )
    return normalized


def validate_commit(repo_root: Path, commit: str) -> str:
    if not FULL_COMMIT_RE.fullmatch(commit):
        raise FreezeError(
            "commit must be an explicit lowercase 40-character commit SHA; "
            "refs, HEAD and abbreviated SHAs are rejected"
        )
    completed = _run_git(repo_root, "cat-file", "-t", commit)
    if completed.returncode:
        detail = _git_error(completed)
        raise FreezeError(f"cannot resolve commit {commit}: {detail}")
    object_type = completed.stdout.decode("ascii", errors="replace").strip()
    if object_type != "commit":
        raise FreezeError(f"object {commit} is {object_type or 'missing'}, not a commit")
    return commit


def _decode_path(value: bytes) -> str:
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FreezeError("source path is not valid UTF-8") from exc


def _snapshot_entries(
    repo_root: Path, commit: str, source_root: str
) -> tuple[list[dict[str, str]], set[str]]:
    raw = _run_git(
        repo_root,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        commit,
        "--",
        source_root,
    )
    if raw.returncode:
        raise FreezeError(f"cannot inspect source tree: {_git_error(raw)}")

    expected_prefix = source_root + "/"
    entries: list[dict[str, str]] = []
    snapshot_paths: set[str] = set()
    for item in raw.stdout.split(b"\0"):
        if not item:
            continue
        try:
            header, path_bytes = item.split(b"\t", 1)
            mode, object_type, oid = header.decode("ascii").split(" ")
        except (ValueError, UnicodeDecodeError) as exc:
            raise FreezeError("malformed Git tree entry in source root") from exc
        path = _decode_path(path_bytes)
        snapshot_paths.add(path)
        if object_type != "blob" or mode != "100644":
            raise FreezeError(f"unsupported source tree entry: {path}")
        if not path.startswith(expected_prefix):
            raise FreezeError(f"source tree path escaped source root: {path}")
        relative = path.removeprefix(expected_prefix)
        if "/" in relative or not relative:
            raise FreezeError(f"source path drift: expected top-level holder, got {path}")
        if relative == "README.md":
            continue
        if not relative.endswith(".md"):
            raise FreezeError(f"unexpected path under source root: {path}")
        if not OID_RE.fullmatch(oid):
            raise FreezeError(f"invalid Git blob OID for {path}: {oid!r}")
        entries.append({"path": relative, "blob_oid": oid})

    entries.sort(key=lambda entry: entry["path"])
    return entries, snapshot_paths


def _worktree_paths(repo_root: Path, source_root: str) -> set[str]:
    raw = _git_text(repo_root, "ls-files", "-z", "--", source_root).encode("utf-8")
    return {
        _decode_path(path)
        for path in raw.split(b"\0")
        if path
    }


def _assert_source_worktree_matches(
    repo_root: Path, source_root: str, snapshot_paths: set[str]
) -> None:
    source_path = repo_root / source_root
    if source_path.is_symlink():
        raise FreezeError(f"source root is a symlink: {source_root}")
    status = _git_text(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignored=matching",
        "--",
        source_root,
    )
    if status:
        raise FreezeError(
            "live source tree is dirty; freeze only from a clean exact source path"
        )
    current_paths = _worktree_paths(repo_root, source_root)
    if current_paths != snapshot_paths:
        missing = sorted(snapshot_paths - current_paths)
        extra = sorted(current_paths - snapshot_paths)
        raise FreezeError(
            "source path drift between worktree and explicit commit: "
            f"missing={missing[:3]!r}, extra={extra[:3]!r}"
        )


def read_blob(repo_root: Path, blob_oid: str) -> bytes:
    if not OID_RE.fullmatch(blob_oid):
        raise FreezeError(f"invalid Git blob OID: {blob_oid!r}")
    completed = _run_git(repo_root, "cat-file", "blob", blob_oid)
    if completed.returncode:
        raise FreezeError(f"cannot read Git blob {blob_oid}: {_git_error(completed)}")
    return completed.stdout


def build_manifest(
    repo_root: Path,
    commit: str,
    source_root: str = DEFAULT_SOURCE_ROOT,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    source_root = normalize_source_root(source_root)
    commit = validate_commit(repo_root, commit)
    entries, snapshot_paths = _snapshot_entries(repo_root, commit, source_root)
    _assert_source_worktree_matches(repo_root, source_root, snapshot_paths)
    if len(entries) != EXPECTED_HOLDER_COUNT:
        raise FreezeError(
            f"holder count drift: expected {EXPECTED_HOLDER_COUNT}, got {len(entries)}"
        )

    files: list[dict[str, object]] = []
    for entry in entries:
        content = read_blob(repo_root, entry["blob_oid"])
        files.append(
            {
                "path": entry["path"],
                "blob_oid": entry["blob_oid"],
                "sha256": sha256_bytes(content),
                "bytes": len(content),
            }
        )
    return {
        "schema": MANIFEST_SCHEMA,
        "source_root": source_root,
        "source_rule": SOURCE_RULE,
        "count": len(files),
        "files": files,
    }


def _code_digest() -> str:
    try:
        return sha256_bytes(Path(__file__).read_bytes())
    except OSError as exc:
        raise FreezeError(f"cannot hash writer code: {exc}") from exc


def build_lock(
    commit: str,
    source_root: str,
    holder_count: int,
    manifest_bytes: bytes,
) -> dict[str, object]:
    return {
        "schema": LOCK_SCHEMA,
        "corpus_commit": commit,
        "source_root": source_root,
        "holder_count": holder_count,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "parser_sha256": stable_digest(PARSER_SPEC),
        "config_sha256": stable_digest(CONFIG_SPEC),
        "code_sha256": _code_digest(),
        "owned_files": [MANIFEST_NAME, LOCK_NAME],
    }


def _reject_symlink_components(path: Path, label: str, repo_root: Path) -> None:
    resolved_repo_root = repo_root.resolve()
    for component in (path, *path.parents):
        try:
            is_symlink = component.is_symlink()
        except OSError as exc:
            raise FreezeError(f"cannot inspect {label} path: {path}") from exc
        if not is_symlink:
            continue
        try:
            resolved_component = component.resolve()
        except (OSError, RuntimeError) as exc:
            raise FreezeError(f"cannot resolve symlink in {label} path: {component}") from exc
        if component in SYSTEM_PATH_ALIASES:
            continue
        if not resolved_repo_root.is_relative_to(resolved_component):
            raise FreezeError(f"{label} path contains an escaping symlink: {component}")


def _contained_destination(root: Path, name: str) -> Path:
    destination = root / name
    try:
        resolved_root = root.resolve()
        resolved_destination = destination.resolve(strict=False)
        resolved_destination.relative_to(resolved_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise FreezeError(f"owned destination escapes generated root: {name!r}") from exc
    if destination.is_symlink():
        raise FreezeError(f"owned destination is a symlink: {name!r}")
    return destination


def _validate_existing_owned_root(root: Path, source_root: str) -> bool:
    manifest_path = _contained_destination(root, MANIFEST_NAME)
    lock_path = _contained_destination(root, LOCK_NAME)
    manifest_exists = manifest_path.exists()
    lock_exists = lock_path.exists()
    if not manifest_exists and not lock_exists:
        return False
    if manifest_path.is_symlink() or lock_path.is_symlink():
        raise FreezeError("generated root contains a symlink in the owned artifact pair")
    if not manifest_exists or not lock_exists:
        raise FreezeError("generated root ownership is unproven: artifact pair is partial")
    if not manifest_path.is_file() or not lock_path.is_file():
        raise FreezeError("generated root ownership is unproven: artifact is not a file")
    try:
        manifest_value = json.loads(manifest_path.read_text(encoding="utf-8"))
        lock_value = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FreezeError("generated root ownership is unproven: invalid artifact JSON") from exc
    if not isinstance(manifest_value, dict) or manifest_value.get("schema") != MANIFEST_SCHEMA:
        raise FreezeError("generated root ownership is unproven: manifest schema mismatch")
    if not isinstance(lock_value, dict) or lock_value.get("schema") != LOCK_SCHEMA:
        raise FreezeError("generated root ownership is unproven: lock schema mismatch")
    if lock_value.get("source_root") != source_root:
        raise FreezeError("generated root ownership is unproven: source root mismatch")
    if lock_value.get("owned_files") != [MANIFEST_NAME, LOCK_NAME]:
        raise FreezeError("generated root ownership is unproven: owned file list mismatch")
    if lock_value.get("manifest_sha256") != sha256_bytes(manifest_path.read_bytes()):
        raise FreezeError("generated root ownership is unproven: manifest digest mismatch")
    return True


def _prepare_output_root(
    output_root: Path,
    repo_root: Path,
    source_root: str,
) -> tuple[Path, Path]:
    output_root = output_root.absolute()
    _reject_symlink_components(output_root, "generated root", repo_root)
    output_root = output_root.resolve(strict=False)
    source_path = (repo_root / source_root).resolve()
    if output_root == source_path or output_root.is_relative_to(source_path):
        raise FreezeError("generated root overlaps the live source root")
    if source_path.is_relative_to(output_root):
        raise FreezeError("generated root contains the live source root")
    try:
        output_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise FreezeError(f"cannot create generated root {output_root}") from exc
    if output_root.is_symlink() or not output_root.is_dir():
        raise FreezeError("generated root is not a real directory")
    owned = _validate_existing_owned_root(output_root, source_root)
    manifest_path = _contained_destination(output_root, MANIFEST_NAME)
    lock_path = _contained_destination(output_root, LOCK_NAME)
    if owned:
        manifest_path.unlink()
        lock_path.unlink()
    return manifest_path, lock_path


def build(
    repo_root: Path,
    commit: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    source_root: str = DEFAULT_SOURCE_ROOT,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    source_root = normalize_source_root(source_root)
    output_root = output_dir if output_dir.is_absolute() else repo_root / output_dir
    manifest = build_manifest(repo_root, commit, source_root)
    manifest_bytes = json_bytes(manifest)
    lock = build_lock(commit, source_root, manifest["count"], manifest_bytes)
    lock_bytes = json_bytes(lock)
    manifest_path, lock_path = _prepare_output_root(output_root, repo_root, source_root)
    manifest_path.write_bytes(manifest_bytes)
    lock_path.write_bytes(lock_bytes)
    return {
        "commit": commit,
        "source_root": source_root,
        "holder_count": manifest["count"],
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "parser_sha256": lock["parser_sha256"],
        "config_sha256": lock["config_sha256"],
        "code_sha256": lock["code_sha256"],
        "output_dir": output_root,
    }


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    source_root = normalize_source_root(args.source_root)
    result = build(repo_root, args.commit, args.output_dir, source_root)
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "output_dir"},
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except FreezeError as exc:
        raise SystemExit(f"freeze_corpus: {exc}") from exc
