from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .api_utils import _exit, _read_next
from .index_meta import INDEX_DIRNAME, _index_dir_for_corpus, _meta_get, _open_index_metadata_readonly
from .markdown_io import DEFAULT_EXCLUDED_PARTS


GENERATED_INDEX_FILES = ("index.sqlite", "index.sqlite-wal", "index.sqlite-shm", "index.lock")
META_KEYS = ("schema_version", "embed_model", "embedding_api_url", "vec_dim")


def index_db_path(corpus_root: Path, *, cache_root: Path | None = None) -> Path:
    return _index_dir_for_corpus(corpus_root, cache_root=cache_root, create=False) / "index.sqlite"


def index_exists(corpus_root: Path, *, cache_root: Path | None = None) -> bool:
    return index_db_path(corpus_root, cache_root=cache_root).exists()


def read_index_metadata(corpus_root: Path, *, cache_root: Path | None = None) -> dict[str, Any]:
    db_path = index_db_path(corpus_root, cache_root=cache_root)
    if not db_path.exists():
        return {"exists": False, "index_path": str(db_path)}
    try:
        conn = _open_index_metadata_readonly(corpus_root, cache_root=cache_root)
        try:
            meta = {key: _meta_get(conn, key) for key in META_KEYS}
        finally:
            conn.close()
    except Exception as exc:
        return {
            "exists": True,
            "index_path": str(db_path),
            "metadata_error": type(exc).__name__,
            "detail": str(exc),
        }
    return {
        "exists": True,
        "index_path": str(db_path),
        **meta,
    }


def iter_index_roots(root: Path) -> list[Path]:
    found: list[Path] = []
    for current, dirnames, _filenames in os.walk(root):
        current_path = Path(current)
        if (current_path / INDEX_DIRNAME / "index.sqlite").exists():
            found.append(current_path.resolve())
        dirnames[:] = [
            name
            for name in dirnames
            if name not in DEFAULT_EXCLUDED_PARTS
            and name != INDEX_DIRNAME
            and not (name.startswith(".") and name not in {".", ".."})
        ]
    found.sort(key=lambda path: path.as_posix())
    return found


def shadowed_indexes(corpus_root: Path, *, cache_root: Path | None = None) -> list[dict[str, Any]]:
    if cache_root is not None:
        return []
    root = corpus_root.resolve()
    root_meta = read_index_metadata(root, cache_root=cache_root)
    entries: list[dict[str, Any]] = []
    for index_root in iter_index_roots(root):
        if index_root == root:
            continue
        meta = read_index_metadata(index_root)
        reasons = _conflict_reasons(root_meta, meta)
        entry = {
            "root": str(index_root),
            "relative_root": index_root.relative_to(root).as_posix(),
            "index_path": meta.get("index_path") or str(index_root / INDEX_DIRNAME / "index.sqlite"),
            "shadowed_by": str(root),
            "conflicting": bool(reasons),
            "conflict_reasons": reasons,
            "metadata": {key: meta.get(key) for key in META_KEYS if key in meta},
            "generated_files": _generated_files_for(index_root),
        }
        if meta.get("metadata_error"):
            entry["metadata_error"] = meta.get("metadata_error")
            entry["detail"] = meta.get("detail")
        entries.append(entry)
    return entries


def index_conflict_payload(corpus_root: Path, *, cache_root: Path | None = None) -> dict[str, Any] | None:
    conflicts = [entry for entry in shadowed_indexes(corpus_root, cache_root=cache_root) if entry["conflicting"]]
    if not conflicts:
        return None
    return _exit(
        {
            "error": "INDEX_CONFLICT",
            "corpus": str(corpus_root),
            "message": "Nested md-navigator indexes conflict with the explicit corpus index; semantic reads refuse to choose silently.",
            "conflicts": conflicts,
            "read_next": [
                _read_next(
                    "md_corpus_scan",
                    {"root": str(corpus_root)},
                    "Inspect indexed corpora and shadowed nested indexes.",
                ),
                _read_next(
                    "md_index",
                    {"corpus": str(corpus_root), "cleanup_shadowed": True, "dry_run": True},
                    "Preview cleanup of shadowed generated index files before retrying semantic reads.",
                ),
            ],
        },
        2,
    )


def cleanup_shadowed_indexes(
    corpus_root: Path,
    *,
    dry_run: bool,
    confirm: bool,
    cache_root: Path | None = None,
) -> dict[str, Any]:
    if cache_root is not None:
        return _exit(
            {
                "command": "index",
                "operation": "cleanup-shadowed",
                "error": "unsupported_cache_root",
                "reason": "Shadowed cleanup only applies to in-corpus .md-navigator folders.",
            },
            2,
        )
    if not corpus_root.exists():
        return _exit({"command": "index", "operation": "cleanup-shadowed", "error": "path_not_found", "corpus": str(corpus_root)}, 2)

    shadows = shadowed_indexes(corpus_root)
    busy = [entry for entry in shadows if _index_lock_busy(Path(str(entry["root"])))]
    if busy:
        return _exit(
            {
                "command": "index",
                "operation": "cleanup-shadowed",
                "error": "index_locked",
                "locked_indexes": busy,
                "reason": "A shadowed index appears to be locked by another writer; retry after it finishes.",
            },
            1,
        )

    affected = sorted(
        {
            path
            for entry in shadows
            for path in entry["generated_files"]
        }
    )
    payload: dict[str, Any] = {
        "command": "index",
        "operation": "cleanup-shadowed",
        "dry_run": bool(dry_run),
        "corpus": str(corpus_root),
        "shadowed_indexes": shadows,
        "shadowed_count": len(shadows),
        "affected_files": affected,
        "usage_note": "Deletes only generated nested index files; Markdown reports and source files are not touched.",
    }
    if dry_run or not confirm:
        return payload

    deleted: list[str] = []
    missing: list[str] = []
    for raw in affected:
        path = Path(raw)
        try:
            path.unlink()
        except FileNotFoundError:
            missing.append(str(path))
        else:
            deleted.append(str(path))
    payload["dry_run"] = False
    payload["deleted"] = deleted
    payload["missing"] = missing
    return payload


def _conflict_reasons(root_meta: dict[str, Any], nested_meta: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not root_meta.get("exists"):
        reasons.append("root_index_missing")
    if root_meta.get("metadata_error"):
        reasons.append("root_index_metadata_unreadable")
    if nested_meta.get("metadata_error"):
        reasons.append("nested_index_metadata_unreadable")
    for key in META_KEYS:
        root_value = root_meta.get(key)
        nested_value = nested_meta.get(key)
        if root_value is not None and nested_value is not None and root_value != nested_value:
            reasons.append(f"{key}_mismatch")
    return reasons


def _generated_files_for(index_root: Path) -> list[str]:
    index_dir = index_root / INDEX_DIRNAME
    return [
        str((index_dir / filename).resolve())
        for filename in GENERATED_INDEX_FILES
        if (index_dir / filename).exists()
    ]


def _index_lock_busy(index_root: Path) -> bool:
    lock_path = index_root / INDEX_DIRNAME / "index.lock"
    if not lock_path.exists():
        return False
    try:
        import fcntl

        with lock_path.open("r", encoding="utf-8") as handle:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return True
            finally:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
    except OSError:
        return True
    return False
