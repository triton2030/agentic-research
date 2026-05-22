from __future__ import annotations

import json
from pathlib import Path

from md_cli.envelope import wrap


ROOT = Path(__file__).resolve().parents[1]


def test_cli_envelope_shape_matches_mcp_ping_snapshot() -> None:
    mcp_snapshot = json.loads(
        (ROOT / "tests/golden/mcp-responses/md_ping.json").read_text(encoding="utf-8")
    )["payload"]["_envelope"]
    cli_envelope = wrap({}, tool_name="md_ping", args={})["_envelope"]
    assert cli_envelope.keys() == mcp_snapshot.keys()
    for key, expected in mcp_snapshot.items():
        actual = cli_envelope[key]
        if key == "cost":
            assert actual.keys() == expected.keys()
            continue
        if isinstance(expected, dict):
            assert isinstance(actual, dict)
            assert actual.keys() == expected.keys()
        elif isinstance(expected, list):
            assert isinstance(actual, list)
        elif expected is None:
            assert actual is None
        else:
            assert isinstance(actual, type(expected))

