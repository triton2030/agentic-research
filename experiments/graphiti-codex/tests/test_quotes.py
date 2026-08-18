from __future__ import annotations

from pathlib import Path

from graphiti_codex.quotes import load_quotes, read_quotes


def test_quote_keeps_exact_text_time_and_address_and_skips_selection(tmp_path: Path) -> None:
    holder = tmp_path / "holder.md"
    holder.write_text(
        (
            "---\n"
            "project: agentic-research\n"
            "session: 12345678-abcd\n"
            "---\n\n"
            "# Chat recall\n\n"
            '* 2026-08-18T15:00:00+05:00 — "дословная цитата" — '
            "type: решение | topic: продукт-и-ценность | "
            "context-note: Правка черновика: красный цвет только здесь\n"
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
    assert quotes[0].context_note == "Правка черновика: красный цвет только здесь"


def test_strict_reader_rejects_approximate_timestamp(tmp_path: Path) -> None:
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


def test_explicit_reader_skips_legacy_record_and_keeps_diagnostic(tmp_path: Path) -> None:
    legacy = tmp_path / "legacy.md"
    legacy.write_text(
        '* 2026-08-10 — "старый неточный record" — type: идея | topic: агенты-и-ии\n',
        encoding="utf-8",
    )
    target = tmp_path / "target.md"
    target.write_text(
        '* 2026-08-10T07:00:00+00:00 — "точная цитата" — type: решение | topic: агенты-и-ии\n',
        encoding="utf-8",
    )

    quotes, diagnostics = load_quotes([legacy, target], root=tmp_path, strict=False)

    assert [quote.text for quote in quotes] == ["точная цитата"]
    assert [item.address for item in diagnostics] == ["legacy.md:1"]
    assert "time and timezone" in diagnostics[0].reason


def test_reader_accepts_explicit_stable_record_id(tmp_path: Path) -> None:
    holder = tmp_path / "holder.md"
    holder.write_text(
        "\n".join(
            [
                '* 2026-08-18T15:00:00+05:00 — "первая" — type: решение',
                '* 2026-08-18T15:01:00+05:00 — "вторая" — type: решение',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    all_quotes = read_quotes(holder, root=tmp_path)

    quotes, diagnostics = load_quotes(
        [holder], root=tmp_path, record_ids={all_quotes[1].uuid}, strict=False
    )

    assert diagnostics == []
    assert [quote.text for quote in quotes] == ["вторая"]
