from __future__ import annotations

import sqlite3

from navigator import query_vectors


def test_query_vectors_batch_and_cache(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_embed(_model, texts, _api_url, _timeout, batch_size=32, corpus_root=None):
        calls.append(list(texts))
        return [[float(idx), 1.0] for idx, _text in enumerate(texts, start=1)]

    monkeypatch.setattr(query_vectors.embeddings, "_embed_texts_http", fake_embed)
    conn = sqlite3.connect(":memory:")

    first = query_vectors.get_query_vectors(
        conn,
        "test/model",
        ["alpha", "beta", "alpha"],
        "http://test.local/v1",
        5,
    )

    assert calls == [["alpha", "beta"]]
    assert first.cached == 0
    assert first.computed == 2
    assert set(first.vectors) == {"alpha", "beta"}

    second = query_vectors.get_query_vectors(
        conn,
        "test/model",
        ["beta", "alpha"],
        "http://test.local/v1",
        5,
    )

    assert calls == [["alpha", "beta"]]
    assert second.cached == 2
    assert second.computed == 0
    assert set(second.vectors) == {"alpha", "beta"}
