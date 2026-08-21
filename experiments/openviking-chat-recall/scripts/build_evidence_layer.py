#!/usr/bin/env python3
"""Build the deterministic private evidence layer from an explicit Git snapshot.

The source parser is the installed ``1chat-recall`` parser.  It receives only
bytes read with ``git cat-file blob``; the live holder directory is never a
source of records.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


class EvidenceError(ValueError):
    """Raised when an input or generated surface cannot be trusted."""


SOURCE_ROOT = "_ops/chat-recall"
CORPUS_COMMIT = "6f98fcccdbf4b4de45ef787239ad101f70d106e2"
F1_COMMITS = (
    "acb3deff4bbbfa502e7e990d5c6d36fbb5772660",
    "31c8a4f590ce91e37dd8a09cfaaef94594932b87",
)
EXPECTED_HOLDER_COUNT = 184
EXPECTED_RECORD_COUNT = 1101
EXPECTED_DIAGNOSTIC_RECORD_COUNT = 34
EXPECTED_DIAGNOSTIC_COUNTS = {
    "duplicate-session-holder": 29,
    "unmarked-approximate": 4,
    "invalid-type": 1,
}

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FROZEN_DIR = EXPERIMENT_ROOT / "artifacts/full-build/frozen"
DEFAULT_OUTPUT_DIR = EXPERIMENT_ROOT / "artifacts/full-build/evidence"
FROZEN_MANIFEST_NAME = "source-manifest.json"
FROZEN_LOCK_NAME = "source-lock.json"
RECORDS_NAME = "records.jsonl"
COVERAGE_NAME = "coverage-input.json"

MANIFEST_SCHEMA = "openviking-chat-recall/source-manifest.v1"
LOCK_SCHEMA = "openviking-chat-recall/source-lock.v1"
EVIDENCE_RECORD_SCHEMA = "openviking-chat-recall/evidence-record.v1"
COVERAGE_SCHEMA = "openviking-chat-recall/coverage-input.v1"

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
OID_RE = re.compile(r"^[0-9a-f]{40,64}$")
RECORD_ID_RE = re.compile(r"^cr-[0-9a-f]{16}$")
SYSTEM_PATH_ALIASES = (Path("/tmp"), Path("/var"))

# These are the accepted F1 artifacts from acb3def + 31c8a4f.  Keeping the
# values here makes a dirty or substituted F1 artifact fail closed before any
# source blob is parsed.
EXPECTED_F1 = {
    "manifest_sha256": "9cf1f74a0ee48347a9f2db4bf01eeb795577913fd9d04c235540564e9c753450",
    "parser_sha256": "cd2f558947255f8648a08a0c86989a2c8af60e2439be617b5e2a02db94cc1d23",
    "config_sha256": "d8122ad1c5b4bb889459f3959bb3a5e5fcd406431904109a1d3dbcc79b86e153",
    "code_sha256": "b580f5d79601dcb4bb15cbbed4e06bdd3ec561cfb94809e5700bb0636974de85",
    "source_lock_sha256": "8d370407047e7d600e5656e153842120fc6bd7fdca1ee0b4d5ad957a261e52fc",
}

# The parser/config are global runtime owners, not a second local parser.  A
# changed installation is rejected rather than silently changing the frozen
# evidence layer.
EXPECTED_PARSER_SHA256 = "da916bed0cae02dd784e29ae2187884897346426126047357cc7143a293cd456"
EXPECTED_CONFIG_SHA256 = "e75c288f3fa23aef3ce78558e95d40266618dc3a9682213526931b796c87f3c2"
PARSER_RELATIVE_PATH = "skills/1chat-recall/scripts/chat_digest.py"
CONFIG_RELATIVE_PATH = "skills/1chat-recall/scripts/recall_metadata.py"
PARSER_FUNCTIONS = ("_frontmatter", "_star_blocks", "_parse_block")


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
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )


def _git_error(result: subprocess.CompletedProcess[bytes]) -> str:
    return result.stderr.decode("utf-8", errors="replace").strip()


def _git_text(repo_root: Path, *args: str) -> str:
    result = _run_git(repo_root, *args)
    if result.returncode:
        raise EvidenceError(f"git {' '.join(args)} failed: {_git_error(result)}")
    return result.stdout.decode("utf-8")


def validate_commit(repo_root: Path, commit: str) -> str:
    if not FULL_SHA_RE.fullmatch(commit):
        raise EvidenceError(
            "commit must be the explicit lowercase 40-character corpus SHA"
        )
    result = _run_git(repo_root, "cat-file", "-t", commit)
    if result.returncode:
        raise EvidenceError(f"cannot resolve explicit corpus commit: {_git_error(result)}")
    if result.stdout.decode("ascii", errors="replace").strip() != "commit":
        raise EvidenceError("explicit corpus object is not a commit")
    if commit != CORPUS_COMMIT:
        raise EvidenceError("corpus commit is not the accepted Wave 6 snapshot")
    return commit


def _decode_path(value: bytes) -> str:
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError("Git source path is not valid UTF-8") from exc


def _git_tree_entries(repo_root: Path, commit: str) -> list[dict[str, str]]:
    raw = _run_git(
        repo_root,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        commit,
        "--",
        SOURCE_ROOT,
    )
    if raw.returncode:
        raise EvidenceError(f"cannot inspect exact source tree: {_git_error(raw)}")

    entries: list[dict[str, str]] = []
    prefix = SOURCE_ROOT + "/"
    for item in raw.stdout.split(b"\0"):
        if not item:
            continue
        try:
            header, path_bytes = item.split(b"\t", 1)
            mode, object_type, oid = header.decode("ascii").split(" ")
        except (ValueError, UnicodeDecodeError) as exc:
            raise EvidenceError("malformed Git source tree entry") from exc
        path = _decode_path(path_bytes)
        if not path.startswith(prefix):
            raise EvidenceError(f"source tree escaped the required root: {path}")
        relative = path.removeprefix(prefix)
        if not relative or "/" in relative:
            raise EvidenceError(f"source path is not a top-level holder: {path}")
        if object_type != "blob" or mode != "100644":
            raise EvidenceError(f"unsupported source tree entry: {path}")
        if not OID_RE.fullmatch(oid):
            raise EvidenceError(f"invalid Git blob OID for {path}")
        entries.append({"path": relative, "blob_oid": oid})
    return sorted(entries, key=lambda entry: entry["path"])


def read_blob(repo_root: Path, blob_oid: str) -> bytes:
    if not OID_RE.fullmatch(blob_oid):
        raise EvidenceError(f"invalid source blob OID: {blob_oid!r}")
    object_type = _run_git(repo_root, "cat-file", "-t", blob_oid)
    if object_type.returncode:
        raise EvidenceError(f"cannot resolve source blob {blob_oid}: {_git_error(object_type)}")
    if object_type.stdout.decode("ascii", errors="replace").strip() != "blob":
        raise EvidenceError(f"source object {blob_oid} is not a blob")
    result = _run_git(repo_root, "cat-file", "blob", blob_oid)
    if result.returncode:
        raise EvidenceError(f"cannot read source blob {blob_oid}: {_git_error(result)}")
    return result.stdout


def _read_regular_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise EvidenceError(f"{label} is not a regular file")
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} must contain a JSON object")
    return value, raw


def _validate_frozen_inputs(
    repo_root: Path, frozen_dir: Path, commit: str
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes, list[dict[str, str]]]:
    manifest_path = frozen_dir / FROZEN_MANIFEST_NAME
    lock_path = frozen_dir / FROZEN_LOCK_NAME
    manifest, manifest_raw = _read_regular_json(manifest_path, "F1 source manifest")
    lock, lock_raw = _read_regular_json(lock_path, "F1 source lock")

    if sha256_bytes(manifest_raw) != EXPECTED_F1["manifest_sha256"]:
        raise EvidenceError("F1 source manifest digest drift")
    if sha256_bytes(lock_raw) != EXPECTED_F1["source_lock_sha256"]:
        raise EvidenceError("F1 source lock digest drift")

    if set(manifest) != {"schema", "source_root", "source_rule", "count", "files"}:
        raise EvidenceError("F1 source manifest schema drift")
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise EvidenceError("F1 source manifest schema mismatch")
    if manifest.get("source_root") != SOURCE_ROOT:
        raise EvidenceError("F1 source manifest source-root drift")
    if manifest.get("source_rule") != "top-level *.md excluding README.md; sorted by relative POSIX path":
        raise EvidenceError("F1 source manifest source-rule drift")
    if manifest.get("count") != EXPECTED_HOLDER_COUNT:
        raise EvidenceError("F1 holder count drift")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != EXPECTED_HOLDER_COUNT:
        raise EvidenceError("F1 source manifest file count drift")
    paths: list[str] = []
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "blob_oid", "sha256", "bytes"}:
            raise EvidenceError("F1 source manifest file entry drift")
        path = entry.get("path")
        if (
            not isinstance(path, str)
            or not path.endswith(".md")
            or path == "README.md"
            or "/" in path
            or path.startswith("/")
            or ".." in Path(path).parts
        ):
            raise EvidenceError("F1 source manifest path drift")
        if not isinstance(entry.get("blob_oid"), str) or not OID_RE.fullmatch(entry["blob_oid"]):
            raise EvidenceError(f"F1 source manifest blob OID drift for {path}")
        if not isinstance(entry.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise EvidenceError(f"F1 source manifest SHA-256 drift for {path}")
        if not isinstance(entry.get("bytes"), int) or entry["bytes"] < 0:
            raise EvidenceError(f"F1 source manifest byte count drift for {path}")
        paths.append(path)
    if paths != sorted(paths) or len(set(paths)) != len(paths):
        raise EvidenceError("F1 source manifest path order or uniqueness drift")

    expected_lock_keys = {
        "schema",
        "corpus_commit",
        "source_root",
        "holder_count",
        "manifest_sha256",
        "parser_sha256",
        "config_sha256",
        "code_sha256",
        "owned_files",
    }
    if set(lock) != expected_lock_keys or lock.get("schema") != LOCK_SCHEMA:
        raise EvidenceError("F1 source lock schema drift")
    expected_lock_values = {
        "corpus_commit": CORPUS_COMMIT,
        "source_root": SOURCE_ROOT,
        "holder_count": EXPECTED_HOLDER_COUNT,
        "manifest_sha256": EXPECTED_F1["manifest_sha256"],
        "parser_sha256": EXPECTED_F1["parser_sha256"],
        "config_sha256": EXPECTED_F1["config_sha256"],
        "code_sha256": EXPECTED_F1["code_sha256"],
        "owned_files": [FROZEN_MANIFEST_NAME, FROZEN_LOCK_NAME],
    }
    for key, expected in expected_lock_values.items():
        if lock.get(key) != expected:
            raise EvidenceError(f"F1 source lock {key} drift")
    if commit != CORPUS_COMMIT:
        raise EvidenceError("F2 commit does not match F1 source lock")
    if lock["manifest_sha256"] != sha256_bytes(manifest_raw):
        raise EvidenceError("F1 source lock does not cover current manifest bytes")

    tree_entries = _git_tree_entries(repo_root, commit)
    tree_holders = [entry for entry in tree_entries if entry["path"] != "README.md"]
    tree_nonholders = [entry for entry in tree_entries if entry["path"] == "README.md"]
    if any(not entry["path"].endswith(".md") for entry in tree_holders):
        raise EvidenceError("exact Git source tree contains an unexpected non-Markdown path")
    if len(tree_holders) != EXPECTED_HOLDER_COUNT or len(tree_nonholders) > 1:
        raise EvidenceError("exact Git source holder count or README path drift")
    if [entry["path"] for entry in tree_holders] != paths:
        raise EvidenceError("F1 manifest path set differs from exact Git tree")
    manifest_by_path = {entry["path"]: entry for entry in files}
    for tree_entry in tree_holders:
        if manifest_by_path[tree_entry["path"]]["blob_oid"] != tree_entry["blob_oid"]:
            raise EvidenceError(f"F1 manifest blob OID differs for {tree_entry['path']}")
    return manifest, lock, manifest_raw, lock_raw, tree_holders


def _codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def _load_parser() -> tuple[ModuleType, dict[str, str]]:
    parser_dir = _codex_home() / "skills/1chat-recall/scripts"
    parser_path = parser_dir / "chat_digest.py"
    config_path = parser_dir / "recall_metadata.py"
    try:
        parser_raw = parser_path.read_bytes()
        config_raw = config_path.read_bytes()
    except OSError as exc:
        raise EvidenceError("installed 1chat-recall parser/config is unavailable") from exc
    parser_sha256 = sha256_bytes(parser_raw)
    config_sha256 = sha256_bytes(config_raw)
    if parser_sha256 != EXPECTED_PARSER_SHA256:
        raise EvidenceError("1chat-recall parser digest drift")
    if config_sha256 != EXPECTED_CONFIG_SHA256:
        raise EvidenceError("1chat-recall metadata config digest drift")

    module_name = "_openviking_chat_digest_for_evidence"
    spec = importlib.util.spec_from_file_location(module_name, parser_path)
    if spec is None or spec.loader is None:
        raise EvidenceError("cannot load the pinned 1chat-recall parser")
    module = importlib.util.module_from_spec(spec)
    old_recall_metadata = sys.modules.pop("recall_metadata", None)
    sys.path.insert(0, str(parser_dir))
    try:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - reports an environment failure
        raise EvidenceError("pinned 1chat-recall parser failed to load") from exc
    finally:
        sys.path.remove(str(parser_dir))
        if old_recall_metadata is not None:
            sys.modules["recall_metadata"] = old_recall_metadata
        else:
            sys.modules.pop("recall_metadata", None)
    if any(not callable(getattr(module, name, None)) for name in PARSER_FUNCTIONS):
        raise EvidenceError("pinned 1chat-recall parser seam drift")
    return module, {
        "sha256": parser_sha256,
        "config_sha256": config_sha256,
        "parser_path": PARSER_RELATIVE_PATH,
        "config_path": CONFIG_RELATIVE_PATH,
    }


def _apply_parser_diagnostics(records: list[dict[str, Any]]) -> None:
    session_holders: dict[str, set[str]] = collections.defaultdict(set)
    id_counts: collections.Counter[str] = collections.Counter()
    for record in records:
        if record.get("session") != "unknown":
            session_holders[str(record["session"])].add(str(record["file"]))
        id_counts[str(record["record_id"])] += 1
    for record in records:
        diagnostics = set(record.get("diagnostics") or [])
        session = str(record.get("session"))
        record_id = str(record.get("record_id"))
        if len(session_holders[session]) > 1:
            diagnostics.add("duplicate-session-holder")
        if id_counts[record_id] > 1:
            diagnostics.add("duplicate-record-id")
        record["diagnostics"] = sorted(diagnostics)


def _parse_snapshot(
    repo_root: Path,
    manifest: dict[str, Any],
    tree_holders: list[dict[str, str]],
    parser: ModuleType,
) -> list[dict[str, Any]]:
    manifest_by_path = {entry["path"]: entry for entry in manifest["files"]}
    records: list[dict[str, Any]] = []
    for tree_entry in tree_holders:
        path = tree_entry["path"]
        manifest_entry = manifest_by_path[path]
        blob = read_blob(repo_root, tree_entry["blob_oid"])
        if sha256_bytes(blob) != manifest_entry["sha256"]:
            raise EvidenceError(f"source blob digest drift for {path}")
        if len(blob) != manifest_entry["bytes"]:
            raise EvidenceError(f"source blob byte count drift for {path}")
        try:
            lines = blob.decode("utf-8-sig").splitlines()
        except UnicodeDecodeError as exc:
            raise EvidenceError(f"source blob is not UTF-8: {path}") from exc
        header = parser._frontmatter(lines)
        for line, block in parser._star_blocks(lines):
            record = parser._parse_block(Path(path), line, block, header)
            if record.get("file") != Path(path).name or record.get("line") != line:
                raise EvidenceError(f"parser address drift for {path}:{line}")
            record["_source_path"] = path
            record["_source_blob_oid"] = tree_entry["blob_oid"]
            record["_source_blob_sha256"] = manifest_entry["sha256"]
            records.append(record)
    _apply_parser_diagnostics(records)
    if len(records) != EXPECTED_RECORD_COUNT:
        raise EvidenceError(f"parsed record count drift: expected {EXPECTED_RECORD_COUNT}, got {len(records)}")
    record_ids = [str(record.get("record_id")) for record in records]
    if any(not RECORD_ID_RE.fullmatch(record_id) for record_id in record_ids):
        raise EvidenceError("parser produced an invalid stable record ID")
    if len(set(record_ids)) != len(record_ids):
        raise EvidenceError("duplicate stable record ID in exact snapshot")
    diagnostic_counts = collections.Counter(
        diagnostic
        for record in records
        for diagnostic in record.get("diagnostics", [])
    )
    if dict(sorted(diagnostic_counts.items())) != EXPECTED_DIAGNOSTIC_COUNTS:
        raise EvidenceError("source diagnostic count drift")
    if sum(bool(record.get("diagnostics")) for record in records) != EXPECTED_DIAGNOSTIC_RECORD_COUNT:
        raise EvidenceError("source diagnostic record count drift")
    return records


def _disposition(record: dict[str, Any]) -> tuple[str, str]:
    diagnostics = sorted(str(value) for value in record.get("diagnostics", []))
    if diagnostics:
        return (
            "rejected",
            "source diagnostics preserved; not admitted as accepted knowledge: "
            + ", ".join(diagnostics),
        )
    return "used", "parsed from exact Git blob with no source diagnostics"


def _metadata(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "kind",
        "timestamp",
        "sort_timestamp",
        "date",
        "source",
        "precision",
        "source_ref",
        "type",
        "type_raw",
        "topic",
        "topic_raw",
        "session",
        "agent",
        "model",
        "project",
        "context_note",
        "session_context",
    )
    return {key: record.get(key) for key in keys}


def _evidence_record(record: dict[str, Any]) -> dict[str, Any]:
    disposition, reason = _disposition(record)
    source_path = f"{SOURCE_ROOT}/{record['_source_path']}"
    source_address = f"{source_path}:{record['line']}"
    quote = str(record["quote"])
    return {
        "schema": EVIDENCE_RECORD_SCHEMA,
        "record_id": record["record_id"],
        "source_commit": CORPUS_COMMIT,
        "source_path": source_path,
        "source_line": record["line"],
        "source_address": source_address,
        "address": source_address,
        "source_blob_oid": record["_source_blob_oid"],
        "source_blob_sha256": record["_source_blob_sha256"],
        "content_sha256": sha256_bytes(quote.encode("utf-8")),
        "text": quote,
        "quote": quote,
        "metadata": _metadata(record),
        "diagnostics": sorted(record.get("diagnostics", [])),
        "disposition": disposition,
        "disposition_reason": reason,
    }


def _records_bytes(records: list[dict[str, Any]]) -> bytes:
    return b"".join(
        (
            json.dumps(
                _evidence_record(record),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        for record in records
    )


def _coverage_item(record: dict[str, Any]) -> dict[str, Any]:
    disposition, reason = _disposition(record)
    source_path = f"{SOURCE_ROOT}/{record['_source_path']}"
    return {
        "record_id": record["record_id"],
        "source_address": f"{source_path}:{record['line']}",
        "source_path": source_path,
        "source_line": record["line"],
        "diagnostics": sorted(record.get("diagnostics", [])),
        "disposition": disposition,
        "reason": reason,
    }


def _coverage_bytes(
    records: list[dict[str, Any]],
    records_raw: bytes,
    lock: dict[str, Any],
    manifest_raw: bytes,
    lock_raw: bytes,
    parser_digests: dict[str, str],
) -> bytes:
    items = [_coverage_item(record) for record in records]
    diagnostic_items = [item for item in items if item["diagnostics"]]
    diagnostic_counts = collections.Counter(
        diagnostic
        for item in diagnostic_items
        for diagnostic in item["diagnostics"]
    )
    payload = {
        "schema": COVERAGE_SCHEMA,
        "owned_files": [RECORDS_NAME, COVERAGE_NAME],
        "f1_commits": list(F1_COMMITS),
        "source": {
            "commit": CORPUS_COMMIT,
            "source_root": SOURCE_ROOT,
            "holder_count": EXPECTED_HOLDER_COUNT,
            "record_count": len(records),
            "diagnostic_record_count": len(diagnostic_items),
            "diagnostic_counts": dict(sorted(diagnostic_counts.items())),
        },
        "digests": {
            "f1_manifest_sha256": sha256_bytes(manifest_raw),
            "f1_source_lock_sha256": sha256_bytes(lock_raw),
            "f1_parser_sha256": lock["parser_sha256"],
            "f1_config_sha256": lock["config_sha256"],
            "f1_code_sha256": lock["code_sha256"],
            "parser_sha256": parser_digests["sha256"],
            "config_sha256": parser_digests["config_sha256"],
            "code_sha256": sha256_bytes(Path(__file__).read_bytes()),
            "records_sha256": sha256_bytes(records_raw),
        },
        "records": items,
    }
    return json_bytes(payload)


def _reject_symlink_components(path: Path, label: str) -> None:
    absolute = path.absolute()
    for component in (absolute, *absolute.parents):
        try:
            is_symlink = component.is_symlink()
        except OSError as exc:
            raise EvidenceError(f"cannot inspect {label} path") from exc
        if not is_symlink:
            continue
        if component in SYSTEM_PATH_ALIASES:
            continue
        raise EvidenceError(f"{label} path contains a symlink: {component.name}")


def _output_paths(repo_root: Path, output_dir: Path) -> tuple[Path, Path, Path]:
    output_root = output_dir.absolute()
    _reject_symlink_components(output_root, "evidence output")
    output_root = output_root.resolve(strict=False)
    source_root = (repo_root / SOURCE_ROOT).resolve(strict=False)
    if output_root == source_root or output_root.is_relative_to(source_root):
        raise EvidenceError("evidence output overlaps the live source root")
    if source_root.is_relative_to(output_root):
        raise EvidenceError("evidence output contains the live source root")
    return output_root, output_root / RECORDS_NAME, output_root / COVERAGE_NAME


def _validate_existing_owned_root(output_root: Path) -> bool:
    records_path = output_root / RECORDS_NAME
    coverage_path = output_root / COVERAGE_NAME
    for path in (records_path, coverage_path):
        if path.is_symlink():
            raise EvidenceError(f"owned evidence output is a symlink: {path.name}")
    records_exists = records_path.exists()
    coverage_exists = coverage_path.exists()
    if not records_exists and not coverage_exists:
        return False
    if records_exists != coverage_exists:
        raise EvidenceError("evidence output ownership is unproven: partial pair")
    if not records_path.is_file() or not coverage_path.is_file():
        raise EvidenceError("evidence output ownership is unproven: non-file artifact")
    coverage, coverage_raw = _read_regular_json(coverage_path, "existing coverage input")
    if coverage.get("schema") != COVERAGE_SCHEMA:
        raise EvidenceError("evidence output ownership is unproven: schema mismatch")
    if coverage.get("owned_files") != [RECORDS_NAME, COVERAGE_NAME]:
        raise EvidenceError("evidence output ownership is unproven: owned-file mismatch")
    digests = coverage.get("digests")
    if not isinstance(digests, dict) or digests.get("records_sha256") != sha256_bytes(records_path.read_bytes()):
        raise EvidenceError("evidence output ownership is unproven: records digest mismatch")
    if not coverage_raw:
        raise EvidenceError("evidence output ownership is unproven: empty coverage artifact")
    return True


def _prepare_output_root(repo_root: Path, output_dir: Path) -> tuple[Path, Path, Path]:
    output_root, records_path, coverage_path = _output_paths(repo_root, output_dir)
    try:
        output_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise EvidenceError("cannot create evidence output root") from exc
    if output_root.is_symlink() or not output_root.is_dir():
        raise EvidenceError("evidence output root is not a real directory")
    if _validate_existing_owned_root(output_root):
        records_path.unlink()
        coverage_path.unlink()
    return output_root, records_path, coverage_path


def _build_bytes(
    repo_root: Path,
    commit: str,
    frozen_dir: Path,
) -> tuple[bytes, bytes, dict[str, Any]]:
    repo_root = repo_root.resolve()
    commit = validate_commit(repo_root, commit)
    manifest, lock, manifest_raw, lock_raw, tree_holders = _validate_frozen_inputs(
        repo_root, frozen_dir, commit
    )
    parser, parser_digests = _load_parser()
    records = _parse_snapshot(repo_root, manifest, tree_holders, parser)
    records_raw = _records_bytes(records)
    coverage_raw = _coverage_bytes(
        records,
        records_raw,
        lock,
        manifest_raw,
        lock_raw,
        parser_digests,
    )
    diagnostic_counts = collections.Counter(
        diagnostic
        for record in records
        for diagnostic in record.get("diagnostics", [])
    )
    summary = {
        "commit": commit,
        "source_root": SOURCE_ROOT,
        "holder_count": EXPECTED_HOLDER_COUNT,
        "record_count": len(records),
        "diagnostic_record_count": sum(bool(record.get("diagnostics")) for record in records),
        "diagnostic_counts": dict(sorted(diagnostic_counts.items())),
        "records_sha256": sha256_bytes(records_raw),
        "coverage_sha256": sha256_bytes(coverage_raw),
        "parser_sha256": parser_digests["sha256"],
        "config_sha256": parser_digests["config_sha256"],
        "code_sha256": sha256_bytes(Path(__file__).read_bytes()),
    }
    return records_raw, coverage_raw, summary


def build(
    repo_root: Path,
    commit: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    frozen_dir: Path = DEFAULT_FROZEN_DIR,
) -> dict[str, Any]:
    """Build the owned F2 pair from one exact commit and return its summary."""
    records_raw, coverage_raw, summary = _build_bytes(
        repo_root, commit, frozen_dir if frozen_dir.is_absolute() else repo_root / frozen_dir
    )
    _, records_path, coverage_path = _prepare_output_root(
        repo_root,
        output_dir if output_dir.is_absolute() else repo_root / output_dir
    )
    try:
        records_path.write_bytes(records_raw)
        coverage_path.write_bytes(coverage_raw)
    except OSError as exc:
        raise EvidenceError("cannot write owned evidence outputs") from exc
    return {**summary, "output_dir": str(records_path.parent)}


def check(
    repo_root: Path,
    commit: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    frozen_dir: Path = DEFAULT_FROZEN_DIR,
) -> dict[str, Any]:
    """Verify committed/current outputs without writing or deleting anything."""
    records_raw, coverage_raw, summary = _build_bytes(
        repo_root, commit, frozen_dir if frozen_dir.is_absolute() else repo_root / frozen_dir
    )
    output_root, records_path, coverage_path = _output_paths(
        repo_root,
        output_dir if output_dir.is_absolute() else repo_root / output_dir
    )
    if not output_root.is_dir() or output_root.is_symlink():
        raise EvidenceError("evidence output root is missing or not a real directory")
    for path in (records_path, coverage_path):
        if path.is_symlink() or not path.is_file():
            raise EvidenceError(f"committed evidence output is missing or symlinked: {path.name}")
    if records_path.read_bytes() != records_raw:
        raise EvidenceError("records.jsonl differs from current writer")
    if coverage_path.read_bytes() != coverage_raw:
        raise EvidenceError("coverage-input.json differs from current writer")
    return {**summary, "output_dir": str(output_root), "status": "pass"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True, help="full accepted corpus commit SHA")
    parser.add_argument("--repo-root", type=Path, default=EXPERIMENT_ROOT.parents[1])
    parser.add_argument("--frozen-dir", type=Path, default=DEFAULT_FROZEN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true", help="verify outputs without writing")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    operation = check if args.check else build
    result = operation(args.repo_root, args.commit, args.output_dir, args.frozen_dir)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except EvidenceError as exc:
        raise SystemExit(f"build_evidence_layer: {exc}") from exc
