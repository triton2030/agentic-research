"""CLI for the thin Graphiti adapter."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from graphiti_codex.codex_llm import CODEX_EFFORT, CODEX_MODEL, resolve_codex_binary
from graphiti_codex.graph import (
    _facts_from_edges,
    _search_fact_edges,
    ingest_quotes,
    open_graph,
    query_facts,
    validate_edge_provenance_once,
)
from graphiti_codex.local_clients import (
    EMBEDDING_DIMENSION,
    FailClosedCrossEncoder,
    LocalFastEmbedder,
)
from graphiti_codex.quotes import load_quotes

EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = EXPERIMENT_ROOT / ".data"
DEFAULT_DATABASE = DATA_ROOT / "graphiti.db"


def project_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "_ops" / "chat-recall").is_dir():
            return candidate
    raise RuntimeError("Run inside agentic-research or pass holder paths from that repository")


def _run_receipt(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return (result.stdout or result.stderr).strip()


def _data_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(DATA_ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"runtime database must stay under {DATA_ROOT}") from error
    return resolved


def _emit(event: str, **payload: Any) -> None:
    print(json.dumps({"event": event, **payload}, ensure_ascii=False), flush=True)


def _read_inputs(args: argparse.Namespace) -> tuple[list[Any], list[dict[str, str]]]:
    root = project_root(Path.cwd())
    holders = [Path(holder).resolve() for holder in args.holders]
    record_ids = set(args.record_id or [])
    quotes, diagnostics = load_quotes(
        holders,
        root=root,
        limit=args.limit,
        record_ids=record_ids or None,
        strict=False,
    )
    skipped = [{"address": item.address, "reason": item.reason} for item in diagnostics]
    for item in skipped:
        _emit("record.skipped", **item)
    if not quotes:
        raise RuntimeError("No exact source-bound quote records found")
    return quotes, skipped


async def doctor() -> dict[str, Any]:
    binary = resolve_codex_binary()
    version = _run_receipt([binary, "--version"])
    login = _run_receipt([binary, "login", "status"])
    if "ChatGPT" not in login:
        raise RuntimeError(f"Codex is not using ChatGPT login: {login}")
    catalog = json.loads(_run_receipt([binary, "debug", "models"]))
    model = next((item for item in catalog["models"] if item["slug"] == CODEX_MODEL), None)
    if model is None:
        raise RuntimeError(f"{CODEX_MODEL} is absent from the Codex model catalog")
    efforts = {item["effort"] for item in model["supported_reasoning_levels"]}
    if CODEX_EFFORT not in efforts:
        raise RuntimeError(f"{CODEX_MODEL} does not support effort {CODEX_EFFORT}")

    embedder = LocalFastEmbedder()
    vector = await embedder.create("Graphiti local readiness")
    if len(vector) != EMBEDDING_DIMENSION:
        raise RuntimeError("local embedding dimension mismatch")
    try:
        await FailClosedCrossEncoder().rank("query", ["passage"])
    except RuntimeError:
        reranker_status = "fail_closed"
    else:  # pragma: no cover - defensive: the implementation must never rank
        raise RuntimeError("cross-encoder seam did not fail closed")

    with tempfile.TemporaryDirectory(prefix="graphiti-codex-doctor-") as workdir:
        async with open_graph(Path(workdir) / "doctor.db"):
            pass
    return {
        "status": "ready",
        "codex": {"version": version, "login": login, "model": CODEX_MODEL, "effort": CODEX_EFFORT},
        "embedding": {"dimension": len(vector), "local": True},
        "reranker": {
            "implementation": "CrossEncoderClient fail-closed seam",
            "status": reranker_status,
        },
        "graph": {"backend": "FalkorDBLite", "embedded": True},
    }


async def run_ingest(args: argparse.Namespace) -> dict[str, Any]:
    quotes, skipped_records = _read_inputs(args)
    database = _data_path(args.database)
    async with open_graph(database) as graphiti:
        result = await ingest_quotes(graphiti, quotes)
    return {
        "quotes_read": len(quotes),
        "skipped_records": skipped_records,
        "ingestion": result,
    }


async def run_query(args: argparse.Namespace) -> dict[str, Any]:
    database = _data_path(args.database)
    async with open_graph(database) as graphiti:
        return await query_facts(graphiti, args.query, limit=args.results)


async def run_demo(args: argparse.Namespace) -> dict[str, Any]:
    quotes, skipped_records = _read_inputs(args)
    database = _data_path(args.database)
    async with open_graph(database) as graphiti:
        ingestion = await ingest_quotes(graphiti, quotes)
        edges = await _search_fact_edges(graphiti, args.query, limit=args.results)
        if not edges:
            raise RuntimeError("live vertical returned no derived facts")
        await validate_edge_provenance_once(graphiti, edges, quotes)
    return {
        "quotes_read": len(quotes),
        "skipped_records": skipped_records,
        "ingestion": ingestion,
        "query": args.query,
        "facts": _facts_from_edges(edges),
    }


def _add_source_arguments(command: argparse.ArgumentParser, *, limit_default: int | None) -> None:
    command.add_argument("holders", nargs="+")
    command.add_argument("--record-id", action="append", help="stable quote UUID or episode.name")
    command.add_argument("--limit", type=int, default=limit_default)
    command.add_argument("--database", type=Path, default=DEFAULT_DATABASE)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subcommands = result.add_subparsers(dest="command", required=True)

    subcommands.add_parser("doctor", help="check Codex, embeddings, reranker and embedded graph")

    ingest = subcommands.add_parser("ingest", help="turn explicit holder records into episodes")
    _add_source_arguments(ingest, limit_default=None)

    query = subcommands.add_parser("query", help="search Graphiti's derived facts")
    query.add_argument("query")
    query.add_argument("--results", type=int, default=10)
    query.add_argument("--database", type=Path, default=DEFAULT_DATABASE)

    demo = subcommands.add_parser("demo", help="ingest explicit records and query derived facts")
    _add_source_arguments(demo, limit_default=3)
    demo.add_argument("--query", required=True)
    demo.add_argument("--results", type=int, default=10)
    return result


def main() -> None:
    args = parser().parse_args()
    actions = {
        "doctor": lambda: doctor(),
        "ingest": lambda: run_ingest(args),
        "query": lambda: run_query(args),
        "demo": lambda: run_demo(args),
    }
    try:
        result = asyncio.run(actions[args.command]())
    except Exception as error:  # noqa: BLE001 - CLI owns one compact failure boundary
        print(f"graphiti-codex: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
