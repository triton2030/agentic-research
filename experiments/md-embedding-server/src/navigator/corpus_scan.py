from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .api_utils import _read_next
from .config import load_corpus_config
from .index_resolution import iter_index_roots, read_index_metadata, shadowed_indexes
from .markdown_io import DEFAULT_EXCLUDED_PARTS


def corpus_scan(root: str | Path = ".") -> dict[str, object]:
    repo_root = Path(root).expanduser().resolve()
    corpora = _corpora(repo_root)
    configured_roots = _configured_index_roots(repo_root)
    unindexed = _unindexed_markdown_folders(repo_root, corpora)
    conflicts = [
        entry
        for corpus in corpora
        for entry in corpus.get("shadowed_indexes", [])
        if isinstance(entry, dict) and entry.get("conflicting")
    ]
    payload: dict[str, Any] = {
        "repo_root": str(repo_root),
        "corpora": corpora,
        "configured_index_roots": configured_roots,
        "unindexed_with_md": unindexed,
        "excluded_dirs_skipped": sorted(DEFAULT_EXCLUDED_PARTS),
        "conflicts": conflicts,
    }
    if conflicts:
        first = conflicts[0]
        cleanup_root = _cleanup_owner_for_conflict(first, configured_roots) or first["shadowed_by"]
        payload["read_next"] = [
            _read_next(
                "md_corpus_scan",
                {"root": cleanup_root},
                "Narrow to the intended corpus before choosing which shadowed indexes to clean.",
            ),
            _read_next(
                "md_index",
                {"corpus": cleanup_root, "cleanup_shadowed": True, "dry_run": True},
                "Preview cleanup only after confirming this is the intended corpus owner.",
            ),
        ]
    return payload


def ping() -> dict[str, object]:
    return {"name": "md-tools", "version": "0.7.0"}


def _corpora(repo_root: Path) -> list[dict[str, Any]]:
    roots = iter_index_roots(repo_root)
    entries: list[dict[str, Any]] = []
    for index_root in roots:
        index_path = index_root / ".md-navigator" / "index.sqlite"
        stat = index_path.stat()
        ancestor = _nearest_indexed_ancestor(index_root, roots)
        meta = read_index_metadata(index_root)
        entry: dict[str, Any] = {
            "root": str(index_root),
            "index_path": str(index_path),
            "last_touched": stat.st_mtime,
            "index_size_bytes": stat.st_size,
            "shadowed_by": str(ancestor) if ancestor else None,
            "shadowed": ancestor is not None,
            "metadata": {
                key: meta.get(key)
                for key in ("schema_version", "embed_model", "embedding_api_url", "vec_dim")
                if meta.get(key) is not None
            },
        }
        if meta.get("metadata_error"):
            entry["metadata_error"] = meta.get("metadata_error")
            entry["detail"] = meta.get("detail")
        if ancestor is None:
            entry["shadowed_indexes"] = shadowed_indexes(index_root)
        entries.append(entry)
    return entries


def _nearest_indexed_ancestor(path: Path, indexed_roots: list[Path]) -> Path | None:
    ancestors = set(path.parents)
    candidates = [root for root in indexed_roots if root in ancestors]
    if not candidates:
        return None
    return max(candidates, key=lambda item: len(item.parts))


def _configured_index_roots(repo_root: Path) -> list[dict[str, str]]:
    cfg = load_corpus_config(repo_root)
    out: list[dict[str, str]] = []
    for pattern in cfg.index.include:
        prefix = _static_prefix(pattern)
        if not prefix:
            continue
        root = prefix if prefix.is_absolute() else repo_root / prefix
        out.append({"root": str(root.resolve()), "pattern": pattern})
    return out


def _static_prefix(pattern: str) -> Path | None:
    parts: list[str] = []
    for part in pattern.replace("\\", "/").split("/"):
        if not part or any(char in part for char in "*?["):
            break
        parts.append(part)
    if not parts:
        return None
    return Path(*parts)


def _cleanup_owner_for_conflict(
    conflict: dict[str, Any],
    configured_roots: list[dict[str, str]],
) -> str | None:
    conflict_root = Path(str(conflict["root"]))
    matches: list[Path] = []
    for entry in configured_roots:
        configured_root = Path(entry["root"])
        if conflict_root == configured_root:
            matches.append(configured_root)
        elif conflict_root.is_relative_to(configured_root):
            matches.append(configured_root)
        elif configured_root.is_relative_to(conflict_root):
            matches.append(configured_root)
    if not matches:
        return None
    return str(max(matches, key=lambda path: len(path.parts)))


def _unindexed_markdown_folders(repo_root: Path, corpora: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed_roots = [Path(str(item["root"])) for item in corpora]
    unindexed: list[dict[str, Any]] = []
    for current, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in DEFAULT_EXCLUDED_PARTS
            and name != ".md-navigator"
            and not (name.startswith(".") and name not in {".", ".."})
        ]
        current_path = Path(current).resolve()
        if any(current_path.is_relative_to(index_root) for index_root in indexed_roots):
            continue
        md_count = sum(1 for name in filenames if name.endswith((".md", ".mdx")))
        if md_count:
            unindexed.append({"folder": str(current_path), "md_files": md_count})
    return unindexed
