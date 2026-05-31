"""Characterization tests for real-world agent complaints.

An external agent surfaced 7 complaints after a Markdown navigation
session. These tests document current behavior on a tiny in-process
corpus. Failures here are evidence about which complaints are real CLI
bugs vs which are harness artifacts or schema misunderstandings — they
should NOT be silenced with xfail; either they pass (proving the
complaint was not a CLI bug) or they fail and direct the next fix.

These probes now exercise the canonical `navigator.api` boundary
directly (the library surface CLI handlers call), not the legacy
argparse `cmd_*` shims. Functions return payload dictionaries; the data
the agent ultimately consumes is the dict, so assertions work against the
payload instead of parsed stdout.

Complaint index:
  1. stderr leak в stdout (`using OpenRouter key from ...`)
  2. Mixed types in `md health --json` (broken_graph_links int, cycles list)
  3. Removed changed-file helper returned 4 files instead of 11
  4. `md repeated-concepts` без `--path-include` = 270KB
  5. `md index --confirm` workflow требует 3 запусков
  6. `md status --json` всегда 3KB
  7. `md search-read` забивает контекст полным телом по умолчанию

Covered here: 1, 2, 6, 7. Follow-up coverage lives in:
  * #3: retired with the changed-file helper; git-diff file selection is outside the md CLI
  * #4: test_envelope_truncation_hint.py
  * #5: test_mcp_cli_parity.py + mutating transaction tests
"""

from __future__ import annotations

import json

import pytest

from navigator.api import (
    DEFAULT_SEARCH_READ_TOKEN_BUDGET,
    health,
    index,
    search_read,
    status,
)


def test_complaint_1_health_payload_carries_no_diagnostic_leak(tiny_corpus, monkeypatch):
    """Probe для жалобы #1.

    На уровне CLI жалоба была про diagnostic, утёкший в stdout
    (`embeddings.py:105` пишет key-path в `sys.stderr`). На каноническом
    `navigator.api` боундари stdout/stderr вообще нет — handler получает
    payload-словарь. Эквивалентный контракт: данные, которые агент
    потребляет (payload), должны быть чистым JSON-сериализуемым объектом
    без вкраплённых diagnostic-строк. Если этот тест проходит — payload
    чистый, а исходная жалоба = harness artifact на уровне процесса
    (caller-агент мерджит stdout+stderr). Если падает — diagnostic
    просочился в сами данные, и это реальный contract-баг.
    """
    monkeypatch.chdir(tiny_corpus)
    payload = health(paths=[str(tiny_corpus)])
    assert payload.get("_exit_code", 0) == 0

    try:
        serialized = json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        pytest.fail(f"health payload не JSON-сериализуем: {exc}\npayload={payload!r}")
    # Round-trip обратно — данные должны выживать сериализацию без потерь.
    json.loads(serialized)

    forbidden = [
        "using OpenRouter",
        "using MD_EMBEDDING",
        "INFO ",
        "WARN ",
        "DEBUG ",
    ]
    for marker in forbidden:
        assert marker not in serialized, (
            f"diagnostic {marker!r} просочился в health payload — "
            f"JSON-parsing агенты сломаются на грязных данных"
        )


def test_complaint_2_md_health_schema_field_types_are_stable(tiny_corpus, monkeypatch):
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
    payload = health(paths=[str(tiny_corpus)])

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


def test_complaint_6_md_status_default_size_baseline(tiny_corpus, mock_embed):
    """Probe для жалобы #6.

    `md status --json` жалуется на 3KB output на каждом запросе.
    Probe устанавливает baseline для 4-файлового corpus. Если на tiny
    corpus уже выходит ≥2KB — shape избыточен в principle и жалоба
    подтверждается. Если меньше — баг scale-dependent (зависит от
    числа секций), нужен отдельный probe на большом corpus.

    Размер меряем как сериализованный JSON payload — это байты, которые
    CLI печатает в stdout (`json.dumps(..., ensure_ascii=False,
    indent=2)`), без служебного `_exit_code`.
    """
    assert index(str(tiny_corpus), confirm=True).get("_exit_code", 0) == 0

    payload = status(str(tiny_corpus))
    payload.pop("_exit_code", None)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)

    size = len(serialized)
    keys = list(payload.keys())

    assert size < 2000, (
        f"md status --json для 4-файлового corpus = {size} bytes "
        f"({len(keys)} top-level keys: {keys}). Жалоба #6 (3KB на каждом "
        f"запросе) подтверждается на baseline; --brief / --fields в шаге 5 "
        f"обоснован."
    )


def test_complaint_7_search_read_default_is_bounded_but_not_empty(tmp_path, mock_embed):
    """Probe для жалобы #7.

    `md search-read` — default agent path для "find + choose", поэтому default
    не должен возвращать body dump. Но агенту всё ещё нужен читаемый map item:
    snippet + read_next, а bounded body path остаётся за явным expanded.
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

    assert index(str(corpus), confirm=True).get("_exit_code", 0) == 0

    payload = search_read(str(corpus), "needle", limit=1)

    assert payload["expanded"] is False
    assert payload["view"] == "map"
    assert payload["token_budget"] == 0
    assert payload["token_budget_defaulted"] is False
    assert payload["sections"], payload
    top = payload["sections"][0]
    assert "content" not in top
    assert "needle" in top["snippet"]
    assert payload["read_next"][0]["args"]["expanded"] is True

    expanded = search_read(str(corpus), "needle", limit=1, expanded=True)
    assert expanded["token_budget"] == DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert expanded["token_budget_defaulted"] is True
    assert expanded["expanded"] is True
    assert expanded["view"] == "expanded"
    assert expanded["token_total"] <= DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert expanded["sections"], expanded
    top = expanded["sections"][0]
    assert top["truncated_by_budget"] is True
    assert top["included_token_count"] <= DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert "needle" in top["content"]
    assert len(top["content"]) < len(large_body)
    assert expanded["dropped_by_budget"][0]["reason"] == "truncated"

    unbounded = search_read(str(corpus), "needle", limit=1, token_budget=0, expanded=True)
    assert unbounded["token_budget"] == 0
    assert unbounded["token_budget_defaulted"] is False
    assert payload["token_total"] <= DEFAULT_SEARCH_READ_TOKEN_BUDGET
    assert unbounded["sections"][0].get("truncated_by_budget") is not True
    assert len(unbounded["sections"][0]["content"]) >= len(large_body)
