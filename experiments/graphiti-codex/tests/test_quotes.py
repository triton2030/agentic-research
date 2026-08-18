from __future__ import annotations

from pathlib import Path

from graphiti_codex.quotes import read_quotes


def test_quote_keeps_exact_text_time_and_address_and_skips_selection(tmp_path: Path) -> None:
    holder = tmp_path / "holder.md"
    holder.write_text(
        (
            """---
project: agentic-research
session: 12345678-abcd
---

# Chat recall

* 2026-08-18T15:00:00+05:00 — "дословная цитата" — type: решение | topic: продукт-и-ценность
"""
            '* 2026-08-18T15:01:00+05:00 — "выбранный пересказ" — '
            "kind: selection | type: решение | topic: продукт-и-ценность\n"
        ),
        encoding="utf-8",
    )

    quotes = read_quotes(holder, root=tmp_path)

    assert len(quotes) == 1
    assert quotes[0].text == "дословная цитата"
    assert quotes[0].timestamp.isoformat() == "2026-08-18T15:00:00+05:00"
    assert quotes[0].address == "holder.md:8"
    assert quotes[0].session == "12345678-abcd"


def test_quote_rejects_approximate_timestamp(tmp_path: Path) -> None:
    holder = tmp_path / "holder.md"
    holder.write_text(
        '* 2026-08-18 — "нет точного времени" — type: идея | topic: продукт-и-ценность\n',
        encoding="utf-8",
    )

    try:
        read_quotes(holder, root=tmp_path)
    except ValueError as error:
        assert "time and timezone" in str(error)
    else:
        raise AssertionError("approximate timestamp was accepted")
