"""Шаг 4 Варианта D: envelope.derive_next_step добавляет narrowing
suggestion когда size_estimate.large_reply == True.

Лечит жалобы #4 (md repeated-concepts 270KB), #6 (md status verbose),
#7 (md search-read 14KB) одной точкой — каждая large reply теперь
несёт executable `next_step` с уменьшающими параметрами, который агент
может скопировать verbatim.

Hint срабатывает только когда:
- tool_name указан
- size_estimate.large_reply == True (> LARGE_REPLY_BYTES, 10KB)
- result.error отсутствует (errors имеют свои own next_step)
"""

from __future__ import annotations

from md_cli.envelope import LARGE_REPLY_BYTES, wrap


def _padding(target_bytes: int) -> str:
    """Build a string long enough to push JSON over LARGE_REPLY_BYTES."""
    return "x" * (target_bytes + 200)


def _assert_shell_filter_guard(reason: str) -> None:
    assert "compact UTF-8 JSON" in reason
    assert "python3 -m json.tool" in reason
    assert "head -N" in reason
    assert "next_step.args" in reason


def test_large_search_reply_adds_limit_narrowing_hint() -> None:
    big_results = [{"snippet": _padding(LARGE_REPLY_BYTES // 5)} for _ in range(5)]
    envelope = wrap(
        {"results": big_results},
        tool_name="md_search",
        args={"corpus": "knowledge", "query": "x", "limit": 10, "scope": "sections"},
    )["_envelope"]

    assert envelope["size_estimate"]["large_reply"] is True
    steps = envelope["next_step"]
    assert len(steps) == 1
    step = steps[0]
    assert step["tool"] == "md_search"
    assert step["args"]["limit"] == 5
    assert "top" not in step["args"]
    assert "Try --limit 5" in step["reason"]
    assert "descriptions" in step["reason"]
    _assert_shell_filter_guard(step["reason"])


def test_large_search_read_reply_recommends_existing_narrowing_args() -> None:
    big_sections = [{"body": _padding(LARGE_REPLY_BYTES // 4)} for _ in range(4)]
    envelope = wrap(
        {"sections": big_sections},
        tool_name="md_search_read",
        args={"corpus": "knowledge", "query": "x", "limit": 3},
    )["_envelope"]

    assert envelope["size_estimate"]["large_reply"] is True
    step = envelope["next_step"][0]
    assert step["tool"] == "md_search_read"
    assert step["args"]["limit"] == 1
    assert "token_budget" not in step["args"]
    assert "top" not in step["args"]
    assert "read_next" in step["reason"]
    assert "--no-body" not in step["reason"]
    _assert_shell_filter_guard(step["reason"])


def test_large_repeated_concepts_reply_recommends_path_include() -> None:
    big_concepts = [{"members": _padding(LARGE_REPLY_BYTES // 3)} for _ in range(3)]
    envelope = wrap(
        {"concepts": big_concepts},
        tool_name="md_repeated_concepts",
        args={"corpus": "knowledge", "top": 50},
    )["_envelope"]

    step = envelope["next_step"][0]
    assert step["tool"] == "md_repeated_concepts"
    assert step["args"]["top"] == 10
    assert "--path-include" in step["reason"]
    _assert_shell_filter_guard(step["reason"])


def test_large_overlaps_reply_does_not_widen_top() -> None:
    big_pairs = [
        {"a": {}, "b": {}, "similarity": 0.9, "content": _padding(LARGE_REPLY_BYTES // 3)}
        for _ in range(3)
    ]
    envelope = wrap(
        {"pairs": big_pairs},
        tool_name="md_overlaps",
        args={"corpus": "knowledge", "top": 5},
    )["_envelope"]

    step = envelope["next_step"][0]
    assert step["tool"] == "md_overlaps"
    assert step["args"]["top"] == 5
    assert "raise --threshold" in step["reason"]
    _assert_shell_filter_guard(step["reason"])


def test_small_reply_keeps_next_step_empty() -> None:
    envelope = wrap(
        {"results": [{"snippet": "tiny"}]},
        tool_name="md_search",
        args={"query": "x"},
    )["_envelope"]

    assert envelope["size_estimate"].get("large_reply") is not True
    assert envelope["next_step"] == []


def test_error_reply_does_not_overwrite_existing_next_step() -> None:
    """Large reply hint must NOT supplant error-driven next_step (e.g.
    index_warmup_required already has its own steps)."""
    envelope = wrap(
        {"error": "index_warmup_required", "padding": _padding(LARGE_REPLY_BYTES)},
        tool_name="md_search",
        args={"corpus": "knowledge", "query": "x"},
    )["_envelope"]

    steps = envelope["next_step"]
    assert len(steps) >= 1
    assert steps[0]["tool"] == "md_index"


def test_unsupported_tool_with_large_reply_yields_empty_next_step() -> None:
    """Tools without natural narrowing axis (e.g. md_ping) get no hint
    even when reply is large — they fall through to empty next_step."""
    envelope = wrap(
        {"value": _padding(LARGE_REPLY_BYTES)},
        tool_name="md_ping",
        args={},
    )["_envelope"]

    assert envelope["size_estimate"]["large_reply"] is True
    assert envelope["next_step"] == []
