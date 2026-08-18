from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest
from graphiti_core.nodes import EpisodeType

import graphiti_codex.graph as graph_module
from graphiti_codex.graph import (
    episode_body,
    ingest_quote,
    ingest_quotes,
    query_facts,
    validate_edge_provenance_once,
)
from graphiti_codex.local_clients import FailClosedCrossEncoder
from graphiti_codex.quotes import SourceQuote


class FakeGraph:
    async def search(self, query: str, *, group_ids: list[str], num_results: int) -> list[object]:
        assert query == "owner preference"
        assert group_ids == ["owner-quotes"]
        assert num_results == 3
        return [
            SimpleNamespace(
                fact=(
                    "The owner prefers source-bound retrieval to return a holder "
                    "for full reading."
                ),
                valid_at=datetime.fromisoformat("2026-08-18T15:00:00+05:00"),
                invalid_at=None,
            )
        ]


def test_public_query_returns_derived_layer_without_episode_trace() -> None:
    result = asyncio.run(query_facts(FakeGraph(), "owner preference", limit=3))

    assert result["facts"] == [
        {
            "kind": "derived_fact",
            "fact": "The owner prefers source-bound retrieval to return a holder for full reading.",
            "valid_at": "2026-08-18T15:00:00+05:00",
            "invalid_at": None,
        }
    ]
    assert "sources" not in result["facts"][0]


def test_ingest_uses_stock_episode_arguments_without_custom_extraction() -> None:
    timestamp = datetime.fromisoformat("2026-08-18T15:00:00+05:00")
    quote = SourceQuote(
        text="владелец хочет derived knowledge",
        timestamp=timestamp,
        address="_ops/chat-recall/example.md:8",
        session="session-1",
        uuid="record-1",
    )

    class FakeGraph:
        def __init__(self) -> None:
            self.kwargs: dict[str, object] = {}

        async def add_episode(self, **kwargs: object) -> object:
            self.kwargs = kwargs
            return SimpleNamespace(
                episode=SimpleNamespace(
                    name=kwargs["name"],
                    uuid="graphiti-uuid",
                    content=kwargs["episode_body"],
                    source_description=kwargs["source_description"],
                ),
                edges=[],
            )

    graph = FakeGraph()
    result = asyncio.run(ingest_quote(graph, quote, {}))

    assert result["status"] == "added"
    assert graph.kwargs["source"] is EpisodeType.message
    assert graph.kwargs["group_id"] == "owner-quotes"
    assert graph.kwargs["name"] == quote.name
    assert graph.kwargs["episode_body"] == "Owner: владелец хочет derived knowledge"
    assert "custom_extraction_instructions" not in graph.kwargs
    assert "entity_types" not in graph.kwargs
    assert "edge_types" not in graph.kwargs


def test_cross_encoder_seam_fails_closed_instead_of_faking_rank() -> None:
    with pytest.raises(RuntimeError, match="stock RRF"):
        asyncio.run(FailClosedCrossEncoder().rank("query", ["passage"]))


def test_successful_ingest_summary_has_counts_only(monkeypatch: pytest.MonkeyPatch) -> None:
    timestamp = datetime.fromisoformat("2026-08-18T15:00:00+05:00")
    quote = SourceQuote(
        text="derived knowledge",
        timestamp=timestamp,
        address="holder.md:1",
        session="session-1",
        uuid="record-1",
    )

    class FakeGraph:
        async def add_episode(self, **kwargs: object) -> object:
            return SimpleNamespace(
                episode=SimpleNamespace(
                    name=kwargs["name"],
                    uuid="internal-uuid",
                    content=kwargs["episode_body"],
                    source_description=kwargs["source_description"],
                ),
                edges=[object(), object()],
            )

    async def no_existing(_graph: object) -> dict[str, object]:
        return {}

    monkeypatch.setattr(graph_module, "existing_episodes", no_existing)
    result = asyncio.run(ingest_quotes(FakeGraph(), [quote]))

    assert result == {
        "added_count": 1,
        "skipped_existing_count": 0,
        "derived_facts_count": 2,
    }
    assert "source" not in result
    assert "episode_uuid" not in result


def test_stable_episode_name_turns_source_change_into_collision() -> None:
    timestamp = datetime.fromisoformat("2026-08-18T15:00:00+05:00")
    quote = SourceQuote(
        text="new content",
        timestamp=timestamp,
        address="holder.md:1",
        session="session-1",
        uuid="stable-record",
    )
    prior = SimpleNamespace(content="old content", source_description=quote.address)

    with pytest.raises(RuntimeError, match="identity collision"):
        asyncio.run(ingest_quote(object(), quote, {quote.name: prior}))


def test_private_validator_checks_provenance_not_fact_wording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timestamp = datetime.fromisoformat("2026-08-18T15:00:00+05:00")
    quote = SourceQuote(
        text="the exact episode wording",
        timestamp=timestamp,
        address="holder.md:1",
        session="session-1",
        uuid="record-1",
    )
    edge = SimpleNamespace(uuid="edge-1", fact=quote.text, episodes=["episode-1"])
    episode = SimpleNamespace(
        uuid="episode-1",
        content=episode_body(quote),
        source_description=quote.address,
        valid_at=timestamp,
    )

    async def get_episodes(_driver: object, _uuids: list[str]) -> list[object]:
        return [episode]

    monkeypatch.setattr(
        graph_module.EpisodicNode,
        "get_by_uuids",
        staticmethod(get_episodes),
    )
    checked = asyncio.run(
        validate_edge_provenance_once(SimpleNamespace(driver=object()), [edge], [quote])
    )

    assert checked == 1
