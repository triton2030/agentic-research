"""Compose Graphiti and preserve fact-to-quote provenance at its public boundary."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.edges import EntityEdge
from graphiti_core.nodes import EpisodeType, EpisodicNode
from redislite.async_falkordb_client import AsyncFalkorDB

from graphiti_codex.codex_llm import CodexLLMClient
from graphiti_codex.local_clients import LocalFastEmbedder, PassThroughCrossEncoder
from graphiti_codex.quotes import SourceQuote

GROUP_ID = "owner-quotes"
EXTRACTION_INSTRUCTIONS = (
    "This episode is one verbatim statement by the owner. Extract only claims explicitly present "
    "in that statement. Do not infer approval, permanence, or scope beyond its wording. "
    "Keep temporal language and corrections visible."
)


@asynccontextmanager
async def open_graph(database: Path) -> AsyncIterator[Graphiti]:
    database.parent.mkdir(parents=True, exist_ok=True)
    embedded = AsyncFalkorDB(dbfilename=str(database))
    driver = FalkorDriver(falkor_db=embedded, database=GROUP_ID)
    graphiti = Graphiti(
        graph_driver=driver,
        llm_client=CodexLLMClient(),
        embedder=LocalFastEmbedder(),
        cross_encoder=PassThroughCrossEncoder(),
        store_raw_episode_content=True,
        max_coroutines=1,
    )
    try:
        # FalkorDriver schedules this task in its constructor. Awaiting that
        # exact task avoids a duplicate index build racing with shutdown.
        if driver._init_task is not None:  # noqa: SLF001 - upstream lifecycle contract
            await driver._init_task  # noqa: SLF001
        yield graphiti
    finally:
        # falkordblite 0.10 marks its sync owner as async-managed, so the public
        # async close disconnects the client but leaves the embedded server and
        # its socket registry alive. Finish that sync-owned lifecycle only after
        # Graphiti has released the async connection.
        await graphiti.close()
        sync_owner = embedded.connection._sync_client  # noqa: SLF001 - upstream lifecycle gap
        sync_owner._async_managed = False  # noqa: SLF001
        await asyncio.to_thread(sync_owner._cleanup)  # noqa: SLF001
        sync_owner._async_managed = True  # noqa: SLF001


async def ingest_quotes(graphiti: Graphiti, quotes: list[SourceQuote]) -> dict[str, Any]:
    added: list[dict[str, Any]] = []
    skipped: list[str] = []
    existing = {
        episode.name: episode
        for episode in await EpisodicNode.get_by_group_ids(graphiti.driver, [GROUP_ID])
    }
    for quote in quotes:
        prior = existing.get(quote.name)
        if prior is not None:
            if prior.content != quote.text or prior.source_description != quote.address:
                raise RuntimeError(f"episode identity collision for {quote.address}")
            skipped.append(quote.address)
            continue

        result = await graphiti.add_episode(
            name=quote.name,
            episode_body=quote.text,
            source_description=quote.address,
            reference_time=quote.timestamp,
            source=EpisodeType.text,
            group_id=GROUP_ID,
            custom_extraction_instructions=EXTRACTION_INSTRUCTIONS,
            saga=f"quote-session:{quote.session}",
        )
        if result.episode.content != quote.text:
            raise RuntimeError(f"Graphiti did not preserve episode {quote.address}")
        existing[result.episode.name] = result.episode
        added.append(
            {
                "episode_uuid": result.episode.uuid,
                "source": result.episode.source_description,
                "derived_facts": len(result.edges),
            }
        )
    return {"added": added, "skipped_existing": skipped}


async def _sources_for_edge(graphiti: Graphiti, edge: EntityEdge) -> list[dict[str, Any]]:
    if not edge.episodes:
        raise RuntimeError(f"derived fact {edge.uuid} has no source episodes")
    episodes = await EpisodicNode.get_by_uuids(graphiti.driver, edge.episodes)
    by_uuid = {episode.uuid: episode for episode in episodes}
    missing = [episode_uuid for episode_uuid in edge.episodes if episode_uuid not in by_uuid]
    if missing:
        raise RuntimeError(f"derived fact {edge.uuid} has missing episodes: {missing}")
    return [
        {
            "episode_uuid": episode_uuid,
            "source": by_uuid[episode_uuid].source_description,
            "quote": by_uuid[episode_uuid].content,
            "reference_time": by_uuid[episode_uuid].valid_at.isoformat(),
        }
        for episode_uuid in edge.episodes
    ]


async def query_facts(graphiti: Graphiti, query: str, *, limit: int = 10) -> dict[str, Any]:
    edges = await graphiti.search(query, group_ids=[GROUP_ID], num_results=limit)
    facts = []
    for edge in edges:
        facts.append(
            {
                "kind": "derived_fact",
                "fact": edge.fact,
                "valid_at": edge.valid_at.isoformat() if edge.valid_at else None,
                "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None,
                "sources": await _sources_for_edge(graphiti, edge),
            }
        )
    return {"query": query, "facts": facts}
