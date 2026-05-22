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
                    "fetched_at": 9_999_999_999,
                    "state": {"state": "FRESH", "index_exists": True},
                }
            }
        ),
        encoding="utf-8",
    )
    corpus_state._CACHE.clear()
    assert corpus_state.quick_corpus_state(root) == {"state": "FRESH", "index_exists": True}


def test_corpus_state_uses_public_api(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MD_TOOLS_CACHE_DIR", str(tmp_path / "cache"))
    root = str((tmp_path / "corpus").resolve())
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "doc.md").write_text("# Doc\n", encoding="utf-8")
    corpus_state._CACHE.clear()

    from navigator import api

    def fake_status(corpus: str):
        assert corpus == root
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
