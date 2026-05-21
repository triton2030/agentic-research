"""Shared test fixtures.

Adds the navigator package to sys.path so tests can import without an
installed package. The script is run via `uv run --script` in normal
use; tests run via `pytest` in the same uv environment.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))


@pytest.fixture
def tiny_corpus(tmp_path: Path) -> Path:
    """A 4-file Markdown corpus used by integration tests.

    Keep it small enough that retrieval is unambiguous: each query
    should have one obvious best section."""
    root = tmp_path / "corpus"
    root.mkdir()

    (root / "agents.md").write_text(
        "# Agents\n\n"
        "## Что делает агент\n\n"
        "Агент читает источники истины перед действием.\n\n"
        "## Frame capture\n\n"
        "Защита от sycophancy и frame capture важна.\n",
        encoding="utf-8",
    )
    (root / "criteria.md").write_text(
        "---\ndescription: Критерии приёмки задач\n---\n\n"
        "# Критерии\n\n"
        "## Definition of done\n\n"
        "Критерий приёмки требует evidence и проверки.\n",
        encoding="utf-8",
    )
    (root / "knowledge.md").write_text(
        "# Knowledge\n\n"
        "## Embeddings\n\n"
        "Vector embeddings encode semantic meaning for retrieval.\n\n"
        "## Reranking\n\n"
        "Cross-encoder reranking boosts top-k precision after RRF.\n",
        encoding="utf-8",
    )
    (root / "noise.md").write_text(
        "# Noise file\n\n"
        "## Random\n\n"
        "Lorem ipsum dolor sit amet.\n",
        encoding="utf-8",
    )
    return root


def _deterministic_embedding(text: str, dim: int = 16) -> list[float]:
    """Hash-derived embedding for tests. Same text → same vector.

    Not semantically meaningful, but enough for round-trip and
    field-hit / fusion-logic verification."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # Spread 32 bytes across `dim` floats in [-1, 1].
    vec: list[float] = []
    for i in range(dim):
        b = digest[i % len(digest)]
        vec.append((b / 127.5) - 1.0)
    return vec


@pytest.fixture
def mock_embed(monkeypatch):
    """Replace the HTTP embedding call with a deterministic hash-based
    stub. Tests using this fixture do not require a network or API key.

    Yields the mock so a test can override the embedding for specific
    texts to engineer retrieval scenarios."""
    from navigator import embeddings

    overrides: dict[str, list[float]] = {}

    def _stub(model_name, texts, api_url, timeout, batch_size=32, corpus_root=None):
        return [
            overrides.get(t, _deterministic_embedding(t)) for t in texts
        ]

    monkeypatch.setattr(embeddings, "_embed_texts_http", _stub)
    # Each consumer module imports the symbol directly via `from .embeddings
    # import _embed_texts_http`, so each gets its own bound reference and
    # we must patch the symbol in every module's namespace.
    from navigator import index_meta, index_build, search as search_mod

    monkeypatch.setattr(index_meta, "_embed_texts_http", _stub)
    monkeypatch.setattr(index_build, "_embed_texts_http", _stub)
    monkeypatch.setattr(search_mod, "_embed_texts_http", _stub)
    yield overrides
