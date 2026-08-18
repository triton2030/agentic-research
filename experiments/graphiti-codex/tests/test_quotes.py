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


def test_single_holder_interpolates_date_only_records_in_source_order(tmp_path: Path) -> None:
    holder = tmp_path / "2026-08-18-000000-claude-session.md"
    holder.write_text(
        "\n".join(
            [
                '* 2026-08-18 — "первая" — type: идея | topic: продукт-и-ценность',
                '* 2026-08-18 — "вторая" — type: идея | topic: продукт-и-ценность',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    quotes = read_quotes(holder, root=tmp_path)

    assert [quote.text for quote in quotes] == ["первая", "вторая"]
    assert all(quote.timestamp_precision == "interpolated" for quote in quotes)
    assert quotes[0].timestamp.isoformat() == "2026-08-18T08:00:00+05:00"
    assert quotes[1].timestamp.isoformat() == "2026-08-18T16:00:00+05:00"


def test_reader_interpolates_between_neighboring_session_files(tmp_path: Path) -> None:
    previous = tmp_path / "2026-08-09-220000-codex-previous.md"
    previous.write_text("# no quotes\n", encoding="utf-8")
    legacy = tmp_path / "2026-08-10-000000-claude-legacy.md"
    legacy.write_text(
        "\n".join(
            [
                '* 2026-08-10 — "первая" — type: идея | topic: агенты-и-ии',
                '* 2026-08-10 — "вторая" — type: идея | topic: агенты-и-ии',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    following = tmp_path / "2026-08-10-140000-codex-following.md"
    following.write_text("# no quotes\n", encoding="utf-8")

    quotes, diagnostics = load_quotes(
        [following, legacy, previous], root=tmp_path, strict=False
    )

    assert diagnostics == []
    assert [quote.text for quote in quotes] == ["первая", "вторая"]
    assert [quote.timestamp.isoformat() for quote in quotes] == [
        "2026-08-10T04:40:00+05:00",
        "2026-08-10T09:20:00+05:00",
    ]


def test_reader_still_rejects_timed_record_without_timezone(tmp_path: Path) -> None:
    holder = tmp_path / "holder.md"
    holder.write_text(
        '* 2026-08-10T07:00:00 — "нет timezone" — type: идея\n', encoding="utf-8"
    )

    quotes, diagnostics = load_quotes([holder], root=tmp_path, strict=False)

    assert quotes == []
    assert [item.address for item in diagnostics] == ["holder.md:1"]
    assert "must include timezone" in diagnostics[0].reason


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
