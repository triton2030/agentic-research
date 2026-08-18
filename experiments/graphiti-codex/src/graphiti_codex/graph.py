"""Thin Graphiti 0.29.3 adapter for local storage and provider clients."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.edges import EntityEdge
from graphiti_core.nodes import EpisodeType, EpisodicNode
from graphiti_core.search.search_filters import ComparisonOperator, DateFilter, SearchFilters
from redislite.async_falkordb_client import AsyncFalkorDB

from graphiti_codex.codex_llm import CODEX_MAX_PARALLEL_TURNS, CodexLLMClient
from graphiti_codex.local_clients import FailClosedCrossEncoder, LocalFastEmbedder
from graphiti_codex.quotes import SourceQuote

GROUP_ID = "owner-quotes"
OWNER_SPEAKER = "Owner"


def episode_body(quote: SourceQuote) -> str:
    """Format one owner utterance as Graphiti's documented message episode."""

    return f"{OWNER_SPEAKER}: {quote.text}"


@asynccontextmanager
async def open_graph(database: Path) -> AsyncIterator[Graphiti]:
    """Open one embedded FalkorDBLite graph and close its full lifecycle."""

    database.parent.mkdir(parents=True, exist_ok=True)
    embedded = AsyncFalkorDB(dbfilename=str(database))
    driver = FalkorDriver(falkor_db=embedded, database=GROUP_ID)
    graphiti = Graphiti(
        graph_driver=driver,
        llm_client=CodexLLMClient(),
        embedder=LocalFastEmbedder(),
        # Graphiti.search() uses the stock RRF recipe. If another caller picks
        # a cross-encoder recipe, fail explicitly instead of using OpenAI or a
        # silent pass-through ranker.
        cross_encoder=FailClosedCrossEncoder(),
        store_raw_episode_content=True,
        # Episodes remain sequential in ingest_quotes(). Graphiti may run
        # independent extraction/resolution work inside one episode in parallel.
        max_coroutines=CODEX_MAX_PARALLEL_TURNS,
    )
    try:
        if driver._init_task is not None:  # noqa: SLF001 - upstream lifecycle contract
            await driver._init_task  # noqa: SLF001
        yield graphiti
    finally:
        # falkordblite owns a sync server behind its async client. Graphiti's
        # public close releases the async connection; the sync owner then
        # needs its upstream cleanup hook to stop the embedded process.
        await graphiti.close()
        sync_owner = embedded.connection._sync_client  # noqa: SLF001 - upstream lifecycle gap
        sync_owner._async_managed = False  # noqa: SLF001
        await asyncio.to_thread(sync_owner._cleanup)  # noqa: SLF001
        sync_owner._async_managed = True  # noqa: SLF001


async def existing_episodes(graphiti: Graphiti) -> dict[str, EpisodicNode]:
    """Read stable adapter identities without replacing Graphiti UUIDs."""

    return {
        episode.name: episode
        for episode in await EpisodicNode.get_by_group_ids(graphiti.driver, [GROUP_ID])
    }


async def ingest_quote(
    graphiti: Graphiti,
    quote: SourceQuote,
    existing: dict[str, EpisodicNode],
) -> dict[str, Any]:
    """Add one source record through stock ``Graphiti.add_episode``."""

    body = episode_body(quote)
    prior = existing.get(quote.name)
    if prior is not None:
        if prior.content != body or prior.source_description != quote.address:
            raise RuntimeError(f"episode identity collision for {quote.address}")
        return {"status": "skipped_existing"}

    result = await graphiti.add_episode(
        name=quote.name,
        episode_body=body,
        source_description=quote.address,
        reference_time=quote.timestamp,
        source=EpisodeType.message,
        group_id=GROUP_ID,
    )
    if result.episode.content != body:
        raise RuntimeError(f"Graphiti did not preserve episode {quote.address}")
    existing[result.episode.name] = result.episode
    return {
        "status": "added",
        "derived_facts": len(result.edges),
    }


async def ingest_quotes(graphiti: Graphiti, quotes: list[SourceQuote]) -> dict[str, Any]:
    """Ingest records in source order, one awaited episode at a time."""

    added_count = 0
    skipped_existing_count = 0
    derived_facts_count = 0
    existing = await existing_episodes(graphiti)
    for quote in quotes:
        outcome = await ingest_quote(graphiti, quote, existing)
        if outcome["status"] == "skipped_existing":
            skipped_existing_count += 1
        else:
            added_count += 1
            derived_facts_count += int(outcome["derived_facts"])
    return {
        "added_count": added_count,
        "skipped_existing_count": skipped_existing_count,
        "derived_facts_count": derived_facts_count,
    }


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("fact validity time must include a timezone")
    return value.astimezone(UTC)


def _facts_valid_at(as_of: datetime) -> SearchFilters:
    """Build Graphiti's documented temporal filter for one point in time."""

    point = _as_utc(as_of)
    return SearchFilters(
        valid_at=[
            [
                DateFilter(
                    date=point,
                    comparison_operator=ComparisonOperator.less_than_equal,
                )
            ],
            [DateFilter(comparison_operator=ComparisonOperator.is_null)],
        ],
        invalid_at=[
            [
                DateFilter(
                    date=point,
                    comparison_operator=ComparisonOperator.greater_than,
                )
            ],
            [DateFilter(comparison_operator=ComparisonOperator.is_null)],
        ],
    )


def _edge_is_valid_at(edge: EntityEdge, as_of: datetime) -> bool:
    point = _as_utc(as_of)
    starts_before_point = edge.valid_at is None or _as_utc(edge.valid_at) <= point
    ends_after_point = edge.invalid_at is None or _as_utc(edge.invalid_at) > point
    return starts_before_point and ends_after_point


async def _search_fact_edges(
    graphiti: Graphiti,
    query: str,
    *,
    limit: int,
    as_of: datetime,
) -> list[EntityEdge]:
    """Run stock hybrid search, restricted to facts valid at ``as_of``."""

    edges = await graphiti.search(
        query,
        group_ids=[GROUP_ID],
        num_results=limit,
        search_filter=_facts_valid_at(as_of),
    )
    # The explicit Graphiti filter is authoritative. This local check makes the
    # public boundary fail closed if a backend ever returns an out-of-range edge.
    return [edge for edge in edges if _edge_is_valid_at(edge, as_of)]


def _derived_fact(edge: EntityEdge) -> dict[str, Any]:
    """Serialize a Graphiti edge without exposing episode provenance."""

    return {
        "kind": "derived_fact",
        "fact": edge.fact,
        "valid_at": edge.valid_at.isoformat() if edge.valid_at else None,
        "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None,
    }


def _facts_from_edges(edges: list[EntityEdge]) -> list[dict[str, Any]]:
    return [_derived_fact(edge) for edge in edges]


async def query_facts(
    graphiti: Graphiti,
    query: str,
    *,
    limit: int = 10,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Return derived facts that were valid at one explicit point in time."""

    point = _as_utc(as_of or datetime.now(UTC))
    edges = await _search_fact_edges(graphiti, query, limit=limit, as_of=point)
    return {"query": query, "as_of": point.isoformat(), "facts": _facts_from_edges(edges)}


async def validate_edge_provenance_once(
    graphiti: Graphiti,
    edges: list[EntityEdge],
    quotes: list[SourceQuote],
) -> int:
    """Private one-shot demo/test validator; it returns no trace payload."""

    expected = {quote.address: quote for quote in quotes}
    checked = 0
    for edge in edges:
        if not edge.episodes:
            raise RuntimeError(f"derived fact {edge.uuid} has no source episodes")
        episodes = await EpisodicNode.get_by_uuids(graphiti.driver, edge.episodes)
        by_uuid = {episode.uuid: episode for episode in episodes}
        for episode_uuid in edge.episodes:
            episode = by_uuid.get(episode_uuid)
            if episode is None:
                raise RuntimeError(f"derived fact {edge.uuid} has missing episode {episode_uuid}")
            quote = expected.get(episode.source_description)
            if quote is None:
                raise RuntimeError(
                    f"derived fact {edge.uuid} points outside supplied holders: "
                    f"{episode.source_description}"
                )
            if episode.content != episode_body(quote):
                raise RuntimeError(f"episode content mismatch: {quote.address}")
            if (
                episode.valid_at is None
                or episode.valid_at.astimezone(UTC) != quote.timestamp.astimezone(UTC)
            ):
                raise RuntimeError(f"episode reference time mismatch: {quote.address}")
            checked += 1
    return checked
