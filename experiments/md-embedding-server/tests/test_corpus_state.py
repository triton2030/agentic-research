from __future__ import annotations

import json
from pathlib import Path

from md_cli import corpus_state


def test_corpus_state_disk_cache(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    root = str((tmp_path / "corpus").resolve())
    (tmp_path / "corpus").mkdir()
    cache_file = tmp_path / "cache" / "corpus-state-cache.json"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text(
        json.dumps(
            {
                root: {
                    "version": corpus_state.CACHE_SCHEMA_VERSION,
                    "fetched_at": 9_999_999_999,
                    "state": {"state": "FRESH", "index_exists": True},
                }
            }
        ),
        encoding="utf-8",
    )
    corpus_state._CACHE.clear()
    assert corpus_state.quick_corpus_state(root) == {"state": "FRESH", "index_exists": True}


def test_corpus_state_ignores_stale_cache_schema(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    root = str((tmp_path / "corpus").resolve())
    (tmp_path / "corpus").mkdir()
    cache_file = tmp_path / "cache" / "corpus-state-cache.json"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text(
        json.dumps(
            {
                root: {
                    "fetched_at": 9_999_999_999,
                    "state": {
                        "state": "HEALTHY",
                        "recommended_action": {
                            "tool": "md_index",
                            "args": {"corpus": root, "confirm": True},
                        },
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    corpus_state._CACHE.clear()
    assert corpus_state.quick_corpus_state(root)["recommended_action"] is None


def test_corpus_state_uses_public_api(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    root = str((tmp_path / "corpus").resolve())
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "doc.md").write_text("# Doc\n", encoding="utf-8")
    corpus_state._CACHE.clear()

    from navigator import api

    def fake_status(corpus: str, **kwargs):
        assert corpus == root
        assert kwargs == {"path_include": None, "path_exclude": None}
        return {"state": "NO_INDEX", "index_exists": False, "pending_chunks": 1}

    monkeypatch.setattr(api, "status", fake_status)
    assert corpus_state.quick_corpus_state(root) == {
        "state": "NO_INDEX",
        "model": None,
        "index_exists": False,
        "last_touched": None,
        "added_sections": 0,
        "removed_sections": 0,
        "pending_chunks": 1,
        "drift_count": 0,
        "metadata_mismatch": False,
        "delta_too_large": False,
        "recommended_action": None,
    }


def test_corpus_state_passes_scope_to_public_api(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    root = str((tmp_path / "corpus").resolve())
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "doc.md").write_text("# Doc\n", encoding="utf-8")
    corpus_state._CACHE.clear()

    from navigator import api

    def fake_status(corpus: str, **kwargs):
        assert corpus == root
        assert kwargs == {"path_include": ["keep/*"], "path_exclude": ["skip/*"]}
        return {
            "state": "NO_INDEX",
            "index_exists": False,
            "pending_chunks": 1,
            "recommended_action": {
                "tool": "md_index",
                "args": {
                    "corpus": root,
                    "dry_run": True,
                    "path_include": ["keep/*"],
                    "path_exclude": ["skip/*"],
                },
            },
        }

    monkeypatch.setattr(api, "status", fake_status)
    state = corpus_state.quick_corpus_state(
        root,
        path_include=["keep/*"],
        path_exclude=["skip/*"],
    )
    assert state["recommended_action"]["args"]["path_include"] == ["keep/*"]
    assert state["recommended_action"]["args"]["path_exclude"] == ["skip/*"]
