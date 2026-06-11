from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from navigator.canon import retrieval


def test_fused_search_merges_different_query_results(monkeypatch) -> None:
    calls: list[str] = []

    def fake_search_one(_ctx, query: str, *, limit: int, candidates: int):
        calls.append(query)
        if query == "alpha":
            return [{"rowid": 1, "relative_path": "a.md", "rrf_score": 0.1, "fields_hit": ["body"]}]
        return [{"rowid": 2, "relative_path": "b.md", "rrf_score": 0.1, "fields_hit": ["heading"]}]

    monkeypatch.setattr(retrieval, "search_one", fake_search_one)

    rows = retrieval.fused_search(SimpleNamespace(), ["alpha", "beta"], limit=10)

    assert calls == ["alpha", "beta"]
    assert {row["relative_path"] for row in rows} == {"a.md", "b.md"}
    assert all("query_ranks" in row for row in rows)


def test_graph_bonus_lifts_link_neighbor(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    source = corpus / "source.md"
    source.write_text("# Source\n\nSee [[neighbor]].\n", encoding="utf-8")
    (corpus / "neighbor.md").write_text("# Neighbor\n\nCanon owner.\n", encoding="utf-8")
    (corpus / "other.md").write_text("# Other\n\nNoise.\n", encoding="utf-8")

    rows = [
        {"rowid": 1, "relative_path": "other.md", "rrf_score": 0.02},
        {"rowid": 2, "relative_path": "neighbor.md", "rrf_score": 0.01},
    ]

    boosted = retrieval.apply_graph_bonus(corpus, source, rows)

    assert boosted[0]["relative_path"] == "neighbor.md"
    assert boosted[0]["graph_bonus"] > 0


def test_rerank_fallback_and_success(monkeypatch) -> None:
    rows = [
        {"relative_path": "a.md", "heading_chain": "A", "body": "aaa"},
        {"relative_path": "b.md", "heading_chain": "B", "body": "bbb"},
    ]

    def fake_rerank(_query, _docs, **_kwargs):
        return [(1, 0.9), (0, 0.1)]

    import navigator.rerank as rerank_mod

    monkeypatch.setattr(rerank_mod, "rerank_documents", fake_rerank)
    reranked, applied = retrieval.apply_rerank("claim", rows)
    assert applied is True
    assert reranked[0]["relative_path"] == "b.md"
    assert reranked[0]["rerank_score"] == 0.9

    def failing_rerank(_query, _docs, **_kwargs):
        raise RuntimeError("no key")

    monkeypatch.setattr(rerank_mod, "rerank_documents", failing_rerank)
    fallback, applied = retrieval.apply_rerank("claim", rows)
    assert applied is False
    assert fallback == rows
