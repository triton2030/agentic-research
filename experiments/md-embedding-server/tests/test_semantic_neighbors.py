from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from navigator.api import corpus_scan, index, read_related, semantic_neighbors
from navigator.workflows import edit_context


ROOT = Path(__file__).resolve().parents[1]
EMBED_KWARGS = {
    "embed_model": "test/root",
    "embedding_api_url": "http://test.local/v1",
    "embedding_timeout": 5,
    "cache_dir": None,
    "max_heading_level": 6,
}


def _build_index(corpus: Path, *, embed_model: str = "test/root", allow_nested: bool = False) -> dict:
    return index(
        str(corpus),
        confirm=True,
        batch_size=32,
        batch_pause_ms=0,
        allow_nested_corpus=allow_nested,
        **{**EMBED_KWARGS, "embed_model": embed_model},
    )


def _corpus_with_folder(tmp_path: Path) -> tuple[Path, Path, Path]:
    root = tmp_path / "corpus"
    target_folder = root / "agents"
    target_folder.mkdir(parents=True)
    target_file = target_folder / "memory.md"
    target_file.write_text(
        "# Agent Memory\n\n## Recall\n\nAgents retrieve relevant knowledge before acting.\n",
        encoding="utf-8",
    )
    (root / "evaluation.md").write_text(
        "# Evaluation\n\n## Evidence\n\nEvaluation checks whether retrieved knowledge changed the action.\n",
        encoding="utf-8",
    )
    (root / "runtime.md").write_text(
        "# Runtime\n\n## Locks\n\nRuntime guardrails keep generated state explicit and reversible.\n",
        encoding="utf-8",
    )
    return root, target_folder, target_file


def test_semantic_neighbors_file_target_returns_agent_block_contract(tmp_path: Path, mock_embed, monkeypatch) -> None:
    corpus, _folder, target_file = _corpus_with_folder(tmp_path)
    assert _build_index(corpus).get("_exit_code", 0) == 0
    mtime_before = (corpus / ".md-navigator" / "index.sqlite").stat().st_mtime_ns
    from navigator import embeddings, index_build, index_meta, search as search_mod

    def fail_embed(*_args, **_kwargs):
        raise AssertionError("semantic-neighbors must not call the embedding backend")

    monkeypatch.setattr(embeddings, "_embed_texts_http", fail_embed)
    monkeypatch.setattr(index_meta, "_embed_texts_http", fail_embed)
    monkeypatch.setattr(index_build, "_embed_texts_http", fail_embed)
    monkeypatch.setattr(search_mod, "_embed_texts_http", fail_embed)

    payload = semantic_neighbors(str(target_file), str(corpus), limit=2)

    assert payload.get("_exit_code", 0) == 0, payload
    assert payload["target"]["kind"] == "file"
    assert payload["usage_note"] == "candidate only, not graph obligation"
    assert payload["read_next"][0]["tool"] == "md_semantic_neighbors"
    assert payload["candidates"], payload
    first = payload["candidates"][0]
    assert {
        "relative_path",
        "heading_chain",
        "start_line",
        "snippet",
        "matched_target",
        "mdref",
    } <= set(first)
    assert first["candidate_class"] == "semantic_neighbor"
    assert first["obligation"] is False
    assert first["graph_edge"] is False
    assert first["relative_path"] != "agents/memory.md"
    assert (corpus / ".md-navigator" / "index.sqlite").stat().st_mtime_ns == mtime_before


def test_semantic_neighbors_folder_target_excludes_target_folder(tmp_path: Path, mock_embed) -> None:
    corpus, target_folder, _target_file = _corpus_with_folder(tmp_path)
    assert _build_index(corpus).get("_exit_code", 0) == 0

    payload = semantic_neighbors(str(target_folder), str(corpus), limit=5)

    assert payload.get("_exit_code", 0) == 0, payload
    assert payload["target"]["kind"] == "folder"
    assert payload["candidates"]
    assert all(not row["relative_path"].startswith("agents/") for row in payload["candidates"])


def test_semantic_neighbors_expanded_omits_rows_without_body_content(tmp_path: Path, mock_embed) -> None:
    corpus, _target_folder, target_file = _corpus_with_folder(tmp_path)
    assert _build_index(corpus).get("_exit_code", 0) == 0

    payload = semantic_neighbors(str(target_file), str(corpus), limit=2, expanded=True, token_budget=1)

    assert payload.get("_exit_code", 0) == 0, payload
    assert payload["expanded"] is True
    assert payload["candidates"], payload
    assert all(row.get("content") for row in payload["candidates"])
    assert all("content_omitted_reason" not in row for row in payload["candidates"])
    assert any(row["reason"] == "over_budget" for row in payload["dropped_by_budget"])


def test_semantic_neighbors_refuses_conflicting_nested_index(tmp_path: Path, mock_embed) -> None:
    corpus, target_folder, _target_file = _corpus_with_folder(tmp_path)
    assert _build_index(corpus, embed_model="test/root").get("_exit_code", 0) == 0
    assert _build_index(target_folder, embed_model="test/nested", allow_nested=True).get("_exit_code", 0) == 0

    payload = semantic_neighbors(str(target_folder), str(corpus))

    assert payload["_exit_code"] == 2
    assert payload["error"] == "INDEX_CONFLICT"
    assert payload["conflicts"]
    assert "embed_model_mismatch" in payload["conflicts"][0]["conflict_reasons"]
    assert payload["read_next"][1]["tool"] == "md_index"
    assert payload["read_next"][1]["args"]["cleanup_shadowed"] is True


def test_corpus_scan_routes_configured_index_root_before_parent_cleanup(tmp_path: Path, mock_embed) -> None:
    repo = tmp_path / "repo"
    knowledge = repo / "knowledge"
    agents = knowledge / "agents"
    agents.mkdir(parents=True)
    (repo / ".md-tools.toml").write_text('[index]\ninclude = ["knowledge/**"]\n', encoding="utf-8")
    (agents / "memory.md").write_text("# Memory\n\nAgent memory belongs in knowledge.\n", encoding="utf-8")
    (knowledge / "evaluation.md").write_text("# Evaluation\n\nKnowledge evaluation lives here.\n", encoding="utf-8")

    assert _build_index(repo, embed_model="test/root").get("_exit_code", 0) == 0
    assert _build_index(knowledge, embed_model="test/knowledge", allow_nested=True).get("_exit_code", 0) == 0

    payload = corpus_scan(str(repo))

    assert payload["configured_index_roots"] == [
        {"root": str(knowledge.resolve()), "pattern": "knowledge/**"}
    ]
    assert payload["conflicts"]
    assert payload["read_next"][0]["args"]["root"] == str(knowledge.resolve())
    assert payload["read_next"][1]["args"]["corpus"] == str(knowledge.resolve())
    assert payload["read_next"][1]["args"]["cleanup_shadowed"] is True


def test_semantic_neighbors_missing_index_returns_warmup_route(tmp_path: Path) -> None:
    corpus, _folder, target_file = _corpus_with_folder(tmp_path)

    payload = semantic_neighbors(str(target_file), str(corpus))

    assert payload["_exit_code"] == 4
    assert payload["error"] == "index_warmup_required"
    assert payload["read_next"][0]["tool"] == "md_index"


def test_cleanup_shadowed_dry_run_and_confirm_preserve_reports(tmp_path: Path, mock_embed) -> None:
    corpus, target_folder, _target_file = _corpus_with_folder(tmp_path)
    assert _build_index(corpus, embed_model="test/root").get("_exit_code", 0) == 0
    assert _build_index(target_folder, embed_model="test/nested", allow_nested=True).get("_exit_code", 0) == 0
    report = target_folder / ".md-navigator" / "repeated-concepts.md"
    report.write_text("# Report\n", encoding="utf-8")

    preview = index(str(corpus), cleanup_shadowed=True, dry_run=True)

    assert preview["operation"] == "cleanup-shadowed"
    assert str(report.resolve()) not in preview["affected_files"]
    assert any(path.endswith("index.sqlite") for path in preview["affected_files"])

    applied = index(str(corpus), cleanup_shadowed=True, confirm=True)

    assert applied["deleted"]
    assert not (target_folder / ".md-navigator" / "index.sqlite").exists()
    assert report.exists()


def test_cleanup_shadowed_cli_confirm_refuses_drift(tmp_path: Path, mock_embed) -> None:
    corpus, target_folder, _target_file = _corpus_with_folder(tmp_path)
    assert _build_index(corpus, embed_model="test/root").get("_exit_code", 0) == 0
    assert _build_index(target_folder, embed_model="test/nested", allow_nested=True).get("_exit_code", 0) == 0

    dry = _run_md("index", str(corpus), "--cleanup-shadowed", "--dry-run", "--json")
    assert dry.returncode == 0, dry.stderr
    dry_payload = json.loads(dry.stdout)
    txn = dry_payload["_envelope"]["lock"]["transaction_id"]
    nested_db = target_folder / ".md-navigator" / "index.sqlite"
    nested_db.write_bytes(nested_db.read_bytes() + b"drift")

    confirmed = _run_md(
        "index",
        str(corpus),
        "--cleanup-shadowed",
        "--confirm",
        "--transaction-id",
        txn,
        "--json",
    )

    assert confirmed.returncode == 1
    assert json.loads(confirmed.stdout)["error"] == "drift_detected"


def test_read_related_semantic_radius_is_retired_route(tmp_path: Path) -> None:
    corpus, _folder, target_file = _corpus_with_folder(tmp_path)

    payload = read_related(paths=[str(target_file)], scan=str(corpus), semantic_radius=3)

    assert payload["_exit_code"] == 2
    assert payload["error"] == "semantic_radius_retired"
    assert payload["read_next"][0]["tool"] == "md_semantic_neighbors"


def test_read_related_check_links_uses_existing_index_without_embedding_calls(
    tmp_path: Path,
    mock_embed,
    monkeypatch,
) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    source = corpus / "source.md"
    target = corpus / "target.md"
    source.write_text(
        "# Source\n\n## Alpha\n\nExplicit link to [[target]].\n",
        encoding="utf-8",
    )
    target.write_text(
        "# Target\n\n## Beta\n\nDifferent linked topic.\n",
        encoding="utf-8",
    )
    assert _build_index(corpus).get("_exit_code", 0) == 0

    from navigator import embeddings, index_build, index_meta, search as search_mod

    def fail_embed(*_args, **_kwargs):
        raise AssertionError("read-related --check-links must not call embeddings")

    monkeypatch.setattr(embeddings, "_embed_texts_http", fail_embed)
    monkeypatch.setattr(index_meta, "_embed_texts_http", fail_embed)
    monkeypatch.setattr(index_build, "_embed_texts_http", fail_embed)
    monkeypatch.setattr(search_mod, "_embed_texts_http", fail_embed)

    payload = read_related(
        paths=[str(source)],
        scan=str(corpus),
        check_links=True,
        link_distance_threshold=-1.0,
    )

    assert payload.get("_exit_code", 0) == 0, payload
    assert payload["semantic_status"] == "ok"
    assert payload["semantic_neighbors"] == []
    assert payload["suspicious_links"]
    assert payload["suspicious_links"][0]["target_relative_path"] == "target.md"


def test_read_related_and_edit_context_return_structured_target_errors(tmp_path: Path) -> None:
    corpus, target_folder, _target_file = _corpus_with_folder(tmp_path)

    related = read_related(paths=[str(target_folder)], scan=str(corpus))
    edit = edit_context(str(target_folder), scan=str(corpus), mode="strict")

    assert related["_exit_code"] == 2
    assert related["error"] == "path_not_found"
    assert edit["_exit_code"] == 2
    assert edit["error"] == "preflight_failed"
    assert edit["preflight"]["error"] == "path_not_found"


def _run_md(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "md_cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
