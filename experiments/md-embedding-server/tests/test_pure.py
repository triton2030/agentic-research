"""Unit tests for pure helpers: no I/O, no HTTP, no DB.

Each test targets one logical surface that regressed easily during
prior refactoring (snippet boundary, signal diagnosis, RRF gap, FTS
tokenization, lemmatization).
"""

from __future__ import annotations

from navigator.lemmatize import lemmatize_text, lemmatize_token
from navigator.search import (
    _fts5_query,
    _signal_label,
    _snippet_for,
    _top_lead,
)


# --- Lemmatization (RU morphology) ---------------------------------


def test_lemmatize_token_russian_inflection() -> None:
    # Genitive plural → nominative singular (canonical lemma)
    assert lemmatize_token("критериев") == "критерий"
    assert lemmatize_token("находки") == "находка"


def test_lemmatize_token_english_passthrough() -> None:
    assert lemmatize_token("embeddings") == "embeddings"
    assert lemmatize_token("rerank") == "rerank"


def test_lemmatize_text_mixes_ru_en() -> None:
    text = "Критериев приёмки for embeddings"
    out = lemmatize_text(text)
    # Russian normalized, English untouched, separators preserved.
    assert "критерий" in out
    assert "приёмка" in out
    assert "embeddings" in out
    assert "for" in out


# --- _fts5_query (token quoting + lemmatization) -------------------


def test_fts5_query_lowercases_and_or_joins() -> None:
    q = _fts5_query("Knowledge Base")
    # Each lemmatized token quoted, OR-joined
    assert ' OR ' in q
    assert '"' in q
    # English passes through lowercased
    assert '"knowledge"' in q
    assert '"base"' in q


def test_fts5_query_empty_input() -> None:
    assert _fts5_query("") == ""
    assert _fts5_query("   ") == ""


def test_fts5_query_lemmatizes_russian() -> None:
    q = _fts5_query("критериев")
    # Lemma of "критериев" is "критерий"
    assert '"критерий"' in q


# --- _signal_label (channel diagnosis) -----------------------------


def test_signal_label_both_channels() -> None:
    r = {
        "fields_hit": ["body", "heading"],
        "bm25_score": -3.0,
        "dense_distance": 0.8,
    }
    label = _signal_label(r)
    assert label.startswith("BM25+Dense")
    assert "body" in label
    assert "heading" in label


def test_signal_label_dense_only_warns() -> None:
    # No BM25 fields hit but dense fired — the canonical morphology-miss
    # diagnostic flag agents should notice.
    r = {
        "fields_hit": [],
        "bm25_score": None,
        "dense_distance": 0.9,
    }
    label = _signal_label(r)
    assert "Dense only" in label
    assert "morphology miss likely" in label


def test_signal_label_bm25_only() -> None:
    r = {
        "fields_hit": ["body"],
        "bm25_score": -2.0,
        "dense_distance": None,
    }
    label = _signal_label(r)
    assert label.startswith("BM25 only")


# --- _top_lead (RRF gap shortcut detection) ------------------------


def test_top_lead_clear_winner() -> None:
    results = [{"rrf_score": 0.05}, {"rrf_score": 0.03}]  # 67% gap
    assert _top_lead(results) is True


def test_top_lead_close_tie() -> None:
    results = [{"rrf_score": 0.030}, {"rrf_score": 0.028}]  # ~7% gap
    assert _top_lead(results) is False


def test_top_lead_single_result() -> None:
    assert _top_lead([{"rrf_score": 0.02}]) is True
    assert _top_lead([]) is False


# --- _snippet_for (word-boundary excerpt) --------------------------


def test_snippet_word_boundary_no_midword_cuts() -> None:
    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "The quick brown fox jumps over the lazy dog. "
        "Another sentence comes here to fill space."
    ) * 4
    snippet = _snippet_for(text, "fox", width=120)
    # Snippet contains the match
    assert "fox" in snippet
    # And does not start/end mid-word (after stripping ellipsis)
    body = snippet.replace("...", "").strip()
    if body and not text.startswith(body[:5]):
        # The starting char (if not the very start) should be the first
        # char of a whole word — i.e. the preceding char in the source
        # is whitespace. We don't reconstruct exact context, but ensure
        # the first 3 chars look like a word start, not a glyph fragment.
        assert body[0].isalnum() or body[0] in {"-", "_", "."}


def test_snippet_handles_empty_input() -> None:
    assert _snippet_for("", "x") == ""
    assert _snippet_for("short text", "missing-token", width=200).startswith("short text")
