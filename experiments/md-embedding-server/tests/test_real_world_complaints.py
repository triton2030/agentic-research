"""Characterization tests for real-world agent complaints.

An external agent surfaced 7 complaints after a Markdown navigation
session. These tests document current behavior on a tiny in-process
corpus. Failures here are evidence about which complaints are real CLI
bugs vs which are harness artifacts or schema misunderstandings — they
should NOT be silenced with xfail; either they pass (proving the
complaint was not a CLI bug) or they fail and direct the next fix.

Complaint index:
  1. stderr leak в stdout (`using OpenRouter key from ...`)
  2. Mixed types in `md health --json` (broken_graph_links int, cycles list)
  3. `md changed --base HEAD` returned 4 files instead of 11
  4. `md repeated-concepts` без `--path-include` = 270KB
  5. `md index --confirm` workflow требует 3 запусков
  6. `md status --json` всегда 3KB
  7. `md search-read` забивает контекст полным телом по умолчанию

Covered here: 1, 2, 6, 7. Complaints 3, 4, 5 need git fixtures / large
corpora / transaction probes and are scheduled for follow-up.
"""

from __future__ import annotations

import json
from argparse import Namespace

import pytest

from navigator.graph import cmd_health
from navigator.index_build import cmd_index
from navigator.index_status import cmd_status
from navigator.api import DEFAULT_SEARCH_READ_TOKEN_BUDGET, search_read


def test_complaint_1_health_json_keeps_stdout_pure(tiny_corpus, monkeypatch, capsys):
    """Probe для жалобы #1.

    `embeddings.py:105` уже использует `file=sys.stderr` для key-path
    diagnostic. Если этот тест проходит — диагностика в stderr,
    жалоба = harness artifact (caller-агент мерджит stdout+stderr,
    например `subprocess.run(..., stderr=STDOUT)` или Codex tool
    merge). Если падает — есть реальный leak на этом пути, и contract
    `stream: stdout = data only` должен попасть в cli-conventions.md.
    """
    monkeypatch.chdir(tiny_corpus)
    args = Namespace(
        paths=[str(tiny_corpus)],
        json=True,
        path_include=[],
        path_exclude=[],
        no_default_excludes=False,
    )
    rc = cmd_health(args)
    captured = capsys.readouterr()
    assert rc == 0

    try:
        json.loads(captured.out)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"stdout не valid JSON: {exc}\n"
            f"---stdout (first 800 bytes)---\n{captured.out[:800]}"
        )

    forbidden = [
        "using OpenRouter",
        "using MD_EMBEDDING",
        "INFO ",
        "WARN ",
        "DEBUG ",
    ]
    for marker in forbidden:
        assert marker not in captured.out, (
            f"diagnostic {marker!r} leaked to stdout — JSON-parsing agents "
            f"will break without `2>/dev/null`"
        )


def test_complaint_2_md_health_schema_field_types_are_stable(
    tiny_corpus, monkeypatch, capsys
):
    """Probe для жалобы #2.

    Agent применил `len()` к health JSON и упал TypeError —
    broken_graph_links это int, cycles это list объектов. Probe
    доказывает: schema consistent, эти поля семантически разные
    (счётчик vs список), оба правильные. Жалоба = schema
    misunderstanding, не bug. UX improvement (шаг 3): additive
    cycles_count: int — non-breaking, agent сможет применять len()
    единообразно к count-fields.
    """
    monkeypatch.chdir(tiny_corpus)
    args = Namespace(
        paths=[str(tiny_corpus)],
        json=True,
        path_include=[],
        path_exclude=[],
        no_default_excludes=False,
    )
    cmd_health(args)
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert "broken_graph_links" in payload, "broken_graph_links отсутствует"
    assert isinstance(payload["broken_graph_links"], int), (
        f"broken_graph_links должен быть int (count), "
        f"got {type(payload['broken_graph_links']).__name__}"
    )

    assert "cycles" in payload, "cycles отсутствует"
    assert isinstance(payload["cycles"], list), (
        f"cycles должен быть list (may be empty), "
        f"got {type(payload['cycles']).__name__}"
    )

    assert "cycles_count" in payload, (
        "cycles_count отсутствует — additive count-поле для UX "
        "однородности с broken_graph_links (шаг 3b Варианта D)"
    )
    assert isinstance(payload["cycles_count"], int), (
        f"cycles_count должен быть int (count), "
        f"got {type(payload['cycles_count']).__name__}"
    )
    assert payload["cycles_count"] == len(payload["cycles"]), (
        "cycles_count должен соответствовать len(cycles)"
    )


def test_complaint_6_md_status_default_size_baseline(
    tiny_corpus, mock_embed, capsys
):
    """Probe для жалобы #6.

    `md status --json` жалуется на 3KB output на каждом запросе.
    Probe устанавливает baseline для 4-файлового corpus. Если на tiny
    corpus уже выходит ≥2KB — shape избыточен в principle и жалоба
    подтверждается. Если меньше — баг scale-dependent (зависит от
    числа секций), нужен отдельный probe на большом corpus.
    """
    idx_args = Namespace(
        path=str(tiny_corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )
    assert cmd_index(idx_args) == 0
    capsys.readouterr()

    status_args = Namespace(
        path=str(tiny_corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        json=True,
        path_include=[],
        path_exclude=[],
    )
    cmd_status(status_args)
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    size = len(captured.out)
    keys = list(payload.keys())

    assert size < 2000, (
        f"md status --json для 4-файлового corpus = {size} bytes "
        f"({len(keys)} top-level keys: {keys}). Жалоба #6 (3KB на каждом "
        f"запросе) подтверждается на baseline; --brief / --fields в шаге 5 "
        f"обоснован."
    )


def test_complaint_7_search_read_default_is_bounded_but_not_empty(
    tmp_path, mock_embed, capsys
):
    """Probe для жалобы #7.

    `md search-read` — default agent path для "find + read", поэтому отсутствие
    `--token-budget` не должно означать unbounded body dump. Но агенту всё ещё
    нужен читаемый фрагмент: oversize top section should be truncated, not
    dropped into an empty result.
    """
    corpus = tmp_path / "big-corpus"
    corpus.mkdir()
    large_body = "needle " + ("long context sentence. " * 6000)
    (corpus / "large.md").write_text(
        "# Large\n\n## Relevant\n\n" + large_body + "\n",
        encoding="utf-8",
    )
    (corpus / "small.md").write_text(
        "# Small\n\n## Other\n\nShort unrelated body.\n",
        encoding="utf-8",
    )

    assert cmd_index(_index_args(corpus)) == 0
    capsys.readouterr()

    payload = search_read(str(corpus), "needle", limit=1)

    assert payload["token_budget"] == DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert payload["token_budget_defaulted"] is True
    assert payload["token_total"] <= DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert payload["sections"], payload
    top = payload["sections"][0]
    assert top["truncated_by_budget"] is True
    assert top["included_token_count"] <= DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert "needle" in top["content"]
    assert len(top["content"]) < len(large_body)
    assert payload["dropped_by_budget"][0]["reason"] == "truncated"

    unbounded = search_read(str(corpus), "needle", limit=1, token_budget=0)
    assert unbounded["token_budget"] == 0
    assert unbounded["token_budget_defaulted"] is False
    assert unbounded["sections"][0].get("truncated_by_budget") is not True
    assert len(unbounded["sections"][0]["content"]) >= len(large_body)


def _index_args(corpus):
    return Namespace(
        path=str(corpus),
        max_heading_level=6,
        embed_model="test/stub-1",
        embedding_api_url="http://test.local/v1",
        embedding_timeout=5,
        cache_dir=None,
        max_auto_embed=10000,
        batch_size=32,
        batch_pause_ms=0,
    )
