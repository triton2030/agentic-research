"""Small CLI for the one accepted Graphiti/Codex vertical."""

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
from graphiti_codex.graph import ingest_quotes, open_graph, query_facts
from graphiti_codex.local_clients import EMBEDDING_DIMENSION, LocalFastEmbedder
from graphiti_codex.quotes import load_quotes

EXPERIMENT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = EXPERIMENT_ROOT / ".data" / "graphiti.db"


def project_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "_ops" / "chat-recall").is_dir():
            return candidate
    raise RuntimeError("Run inside agentic-research or pass holder paths from that repository")


def _run_receipt(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return (result.stdout or result.stderr).strip()


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

    with tempfile.TemporaryDirectory(prefix="graphiti-codex-doctor-") as workdir:
        async with open_graph(Path(workdir) / "doctor.db"):
            pass
    return {
        "status": "ready",
        "codex": {"version": version, "login": login, "model": CODEX_MODEL, "effort": CODEX_EFFORT},
        "embedding": {"dimension": len(vector), "local": True},
        "graph": {"backend": "FalkorDBLite", "embedded": True},
    }


async def run_ingest(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(Path.cwd())
    holders = [Path(holder).resolve() for holder in args.holders]
    quotes = load_quotes(holders, root=root, limit=args.limit)
    if not quotes:
        raise RuntimeError("No exact source-bound quote records found")
    async with open_graph(args.database) as graphiti:
        result = await ingest_quotes(graphiti, quotes)
    return {"quotes_read": len(quotes), **result}


async def run_query(args: argparse.Namespace) -> dict[str, Any]:
    async with open_graph(args.database) as graphiti:
        return await query_facts(graphiti, args.query, limit=args.results)


async def run_demo(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(Path.cwd())
    holders = [Path(holder).resolve() for holder in args.holders]
    quotes = load_quotes(holders, root=root, limit=args.limit)
    if not quotes:
        raise RuntimeError("No exact source-bound quote records found")
    async with open_graph(args.database) as graphiti:
        ingestion = await ingest_quotes(graphiti, quotes)
        answer = await query_facts(graphiti, args.query, limit=args.results)
    return {"quotes_read": len(quotes), "ingestion": ingestion, **answer}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subcommands = result.add_subparsers(dest="command", required=True)

    subcommands.add_parser("doctor", help="check Codex, embeddings and embedded graph")

    ingest = subcommands.add_parser(
        "ingest", help="turn exact quote records into Graphiti episodes"
    )
    ingest.add_argument("holders", nargs="+")
    ingest.add_argument("--limit", type=int)
    ingest.add_argument("--database", type=Path, default=DEFAULT_DATABASE)

    query = subcommands.add_parser("query", help="search derived facts with source episodes")
    query.add_argument("query")
    query.add_argument("--results", type=int, default=10)
    query.add_argument("--database", type=Path, default=DEFAULT_DATABASE)

    demo = subcommands.add_parser("demo", help="ingest quotes and query them in one run")
    demo.add_argument("holders", nargs="+")
    demo.add_argument("--limit", type=int, default=3)
    demo.add_argument("--query", required=True)
    demo.add_argument("--results", type=int, default=10)
    demo.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
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
        receipt = asyncio.run(actions[args.command]())
    except Exception as error:  # noqa: BLE001 - CLI owns one compact failure boundary
        print(f"graphiti-codex: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
