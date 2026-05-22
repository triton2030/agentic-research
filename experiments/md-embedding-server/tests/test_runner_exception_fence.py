"""Exception fence on the handler boundary.

`md_cli.handlers._generic._call` now catches unhandled `Exception` and wraps
it in an `internal_error` envelope (exit code 3), so unexpected runtime
failures (URLError, NetworkXError, etc.) reach the agent caller as JSON
instead of a raw traceback. `BaseException` subclasses (KeyboardInterrupt,
SystemExit) still propagate.

Note: ``runner.run_tool(tool_name, handler_run, args)`` returns ``int`` and
prints JSON to stdout, so these tests capture stdout via ``capsys`` and read
the exit code from the return value.
"""
from __future__ import annotations

import json
import urllib.error
from argparse import Namespace
from typing import Any

import pytest

from md_cli.handlers._generic import _call
from md_cli.result import ToolResult
from md_cli.runner import run_tool


def _payload(result: ToolResult) -> dict[str, Any]:
    assert isinstance(result.payload, dict), f"payload must be dict, got {result.payload!r}"
    return result.payload


def test_unhandled_runtime_error_becomes_envelope_error() -> None:
    def boom(**kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("boom")

    result = _call(boom, {})
    assert isinstance(result, ToolResult)
    assert result.exit_code == 3
    payload = _payload(result)
    assert payload["error"] == "internal_error"
    assert payload["exception"] == "RuntimeError"
    assert payload["detail"] == "boom"


def test_urlerror_becomes_envelope_error() -> None:
    def boom(**kwargs: Any) -> dict[str, Any]:
        raise urllib.error.URLError("net is down")

    result = _call(boom, {})
    assert result.exit_code == 3
    payload = _payload(result)
    assert payload["error"] == "internal_error"
    assert payload["exception"] == "URLError"
    assert "net is down" in payload["detail"]


def test_keyboard_interrupt_propagates() -> None:
    """BaseException subclasses must NOT be caught by the fence."""

    def boom(**kwargs: Any) -> dict[str, Any]:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        _call(boom, {})


def test_runner_emits_envelope_for_internal_error(capsys) -> None:
    """End-to-end: runner.run_tool prints a JSON envelope and returns exit_code 3
    when the handler returns an internal_error ToolResult."""

    def handler(args: Any) -> ToolResult:
        return ToolResult(
            {"error": "internal_error", "exception": "RuntimeError", "detail": "boom"},
            3,
        )

    args = Namespace(json=True, subcommand="md_ping")
    code = run_tool("md_ping", handler, args)
    assert code == 3
    captured = capsys.readouterr().out.strip()
    assert captured, "runner must print JSON envelope to stdout"
    parsed = json.loads(captured)
    assert parsed["error"] == "internal_error"
    assert parsed["exception"] == "RuntimeError"
    assert "_envelope" in parsed
