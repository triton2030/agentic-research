from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_filters import ComparisonOperator

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
    def __init__(self) -> None:
        self.search_filter: object | None = None

    async def search(
        self,
        query: str,
        *,
        group_ids: list[str],
        num_results: int,
        search_filter: object,
    ) -> list[object]:
        assert query == "owner preference"
        assert group_ids == ["owner-quotes"]
        assert num_results == 3
        self.search_filter = search_filter
        return [
            SimpleNamespace(
                name="HAS_PREFERENCE_ABOUT",
                fact=(
                    "The owner prefers source-bound retrieval to return a holder "
                    "for full reading."
                ),
                valid_at=datetime.fromisoformat("2026-08-18T15:00:00+05:00"),
                invalid_at=None,
            )
        ]


def test_public_query_returns_derived_layer_without_episode_trace() -> None:
    graph = FakeGraph()
    as_of = datetime.fromisoformat("2026-08-18T16:00:00+05:00")
    result = asyncio.run(query_facts(graph, "owner preference", limit=3, as_of=as_of))

    assert result["as_of"] == "2026-08-18T11:00:00+00:00"
    assert result["facts"] == [
        {
            "kind": "derived_fact",
            "fact": "The owner prefers source-bound retrieval to return a holder for full reading.",
            "valid_at": "2026-08-18T15:00:00+05:00",
            "invalid_at": None,
        }
    ]
    assert "sources" not in result["facts"][0]
    assert graph.search_filter.valid_at[0][0].comparison_operator is (
        ComparisonOperator.less_than_equal
    )
    assert graph.search_filter.valid_at[1][0].comparison_operator is ComparisonOperator.is_null
    assert graph.search_filter.invalid_at[0][0].comparison_operator is (
        ComparisonOperator.greater_than
    )
    assert graph.search_filter.invalid_at[1][0].comparison_operator is ComparisonOperator.is_null


def test_current_query_fails_closed_if_search_returns_an_invalidated_fact() -> None:
    class LeakyGraph:
        async def search(self, *_args: object, **_kwargs: object) -> list[object]:
            return [
                SimpleNamespace(
                    name="HAS_POSITION_ABOUT",
                    fact="old idea",
                    valid_at=datetime(2026, 8, 1, tzinfo=UTC),
                    invalid_at=datetime(2026, 8, 10, tzinfo=UTC),
                ),
                SimpleNamespace(
                    name="HAS_POSITION_ABOUT",
                    fact="current idea",
                    valid_at=datetime(2026, 8, 10, tzinfo=UTC),
                    invalid_at=None,
                ),
            ]

    result = asyncio.run(
        query_facts(
            LeakyGraph(),
            "idea",
            as_of=datetime(2026, 8, 18, tzinfo=UTC),
        )
    )

    assert [fact["fact"] for fact in result["facts"]] == ["current idea"]


def test_historical_query_returns_only_facts_valid_at_that_time() -> None:
    class HistoricalGraph:
        async def search(self, *_args: object, **_kwargs: object) -> list[object]:
            return [
                SimpleNamespace(
                    name="HAS_POSITION_ABOUT",
                    fact="old idea",
                    valid_at=datetime(2026, 8, 1, tzinfo=UTC),
                    invalid_at=datetime(2026, 8, 10, tzinfo=UTC),
                ),
                SimpleNamespace(
                    name="HAS_POSITION_ABOUT",
                    fact="later idea",
                    valid_at=datetime(2026, 8, 10, tzinfo=UTC),
                    invalid_at=None,
                ),
            ]

    result = asyncio.run(
        query_facts(
            HistoricalGraph(),
            "idea",
            as_of=datetime(2026, 8, 5, tzinfo=UTC),
        )
    )

    assert [fact["fact"] for fact in result["facts"]] == ["old idea"]


def test_query_rejects_a_time_without_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        asyncio.run(
            query_facts(
                FakeGraph(),
                "owner preference",
                as_of=datetime(2026, 8, 18),
            )
        )


def test_ingest_uses_stock_message_episode() -> None:
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
    assert "entity_types" not in graph.kwargs
    assert "edge_types" not in graph.kwargs
    assert "edge_type_map" not in graph.kwargs
    assert "custom_extraction_instructions" not in graph.kwargs


def test_episode_body_keeps_optional_agent_context_as_second_message() -> None:
    quote = SourceQuote(
        text="давай поставим красный цвет",
        timestamp=datetime.fromisoformat("2026-08-18T15:00:00+05:00"),
        address="holder.md:1",
        session="session-1",
        uuid="scoped-record",
        context_note="Правка черновика: только эта задача",
    )

    assert episode_body(quote) == (
        "Owner: давай поставим красный цвет\n"
        "Agent: Правка черновика: только эта задача"
    )


def test_cross_encoder_seam_fails_closed_instead_of_faking_rank() -> None:
    with pytest.raises(RuntimeError, match="stock RRF"):
        asyncio.run(FailClosedCrossEncoder().rank("query", ["passage"]))


def test_successful_ingest_summary_reports_completion(monkeypatch: pytest.MonkeyPatch) -> None:
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
        "remaining_count": 0,
        "complete": True,
    }
    assert "source" not in result
    assert "episode_uuid" not in result


def test_ingest_batch_skips_existing_and_limits_only_new_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timestamp = datetime.fromisoformat("2026-08-18T15:00:00+05:00")
    quotes = [
        SourceQuote(
            text=f"quote {position}",
            timestamp=timestamp,
            address=f"holder.md:{position}",
            session="session-1",
            uuid=f"record-{position}",
        )
        for position in range(1, 6)
    ]
    prior = {
        quote.name: SimpleNamespace(
            name=quote.name,
            content=episode_body(quote),
            source_description=quote.address,
        )
        for quote in quotes[:2]
    }

    async def two_existing(_graph: object) -> dict[str, object]:
        return prior

    class BatchGraph:
        def __init__(self) -> None:
            self.added: list[str] = []

        async def add_episode(self, **kwargs: object) -> object:
            self.added.append(str(kwargs["name"]))
            return SimpleNamespace(
                episode=SimpleNamespace(
                    name=kwargs["name"],
                    content=kwargs["episode_body"],
                    source_description=kwargs["source_description"],
                ),
                edges=[object()],
            )

    monkeypatch.setattr(graph_module, "existing_episodes", two_existing)
    graph = BatchGraph()

    result = asyncio.run(ingest_quotes(graph, quotes, batch_size=2))

    assert graph.added == [quotes[2].name, quotes[3].name]
    assert result == {
        "added_count": 2,
        "skipped_existing_count": 2,
        "derived_facts_count": 2,
        "remaining_count": 1,
        "complete": False,
    }


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


def test_existing_episodes_fails_closed_on_duplicate_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def duplicate_episodes(_driver: object, _group_ids: list[str]) -> list[object]:
        return [
            SimpleNamespace(name="quote:duplicate"),
            SimpleNamespace(name="quote:duplicate"),
        ]

    monkeypatch.setattr(
        graph_module.EpisodicNode,
        "get_by_group_ids",
        staticmethod(duplicate_episodes),
    )

    with pytest.raises(RuntimeError, match="duplicate episode identity"):
        asyncio.run(graph_module.existing_episodes(SimpleNamespace(driver=object())))


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
