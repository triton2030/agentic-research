from __future__ import annotations

from navigator.canon import query_pack
from navigator.canon.query_pack import build_query_pack


def test_query_pack_has_deterministic_projections() -> None:
    queries = build_query_pack("Студия должна нажать `Принять` только после проверки.", "Критерии > Правило")

    assert queries[0] == "Студия должна нажать `Принять` только после проверки."
    assert any("принять" in item.lower() or "нажать" in item.lower() for item in queries)
    assert any("Принять" in item for item in queries)
    assert any(item.startswith("правило:") for item in queries)
    assert len(queries) == len(set(q.lower() for q in queries))


def test_query_pack_drops_empty_and_dedups() -> None:
    queries = build_query_pack("и или но", "")

    assert queries == ["и или но"]


def test_query_pack_degrades_without_morphology(monkeypatch) -> None:
    monkeypatch.setattr(query_pack, "_morph_parse", lambda _token: None)

    queries = build_query_pack("Студии должны проверять заявки", "")

    assert queries[0] == "Студии должны проверять заявки"
    assert any("заявки" in item for item in queries)
