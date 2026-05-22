"""Shared argparse helpers reused across every embedding-aware command.

Before this layer, `--embed-model`, `--embedding-api-url`,
`--embedding-timeout`, `--cache-dir`, `--max-auto-embed`, `--no-cache`,
and `--json` were duplicated in 5+ subparser blocks (≈ 200 lines of
repeated argparse boilerplate). The helpers keep cli.py and the
per-command register_X functions short and consistent."""

from __future__ import annotations

import argparse

from .embeddings import (
    SEARCH_DEFAULT_EMBED_MODEL,
    SEARCH_DEFAULT_EMBEDDING_API_URL,
    SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
)


def add_embedding_args(parser: argparse.ArgumentParser) -> None:
    """Add the three flags every embedding-touching command shares."""
    parser.add_argument(
        "--embed-model",
        default=None,
        help=(
            f"Embedding model id. Default: sticky from existing index meta; "
            f"`{SEARCH_DEFAULT_EMBED_MODEL}` for a new corpus. Explicit flag "
            f"always wins and triggers reindex on mismatch."
        ),
    )
    parser.add_argument(
        "--embedding-api-url",
        default=SEARCH_DEFAULT_EMBEDDING_API_URL,
        help=(
            "OpenAI-compatible API base URL for embeddings "
            f"(default: {SEARCH_DEFAULT_EMBEDDING_API_URL})."
        ),
    )
    parser.add_argument(
        "--embedding-timeout",
        type=float,
        default=SEARCH_DEFAULT_EMBEDDING_TIMEOUT,
        help=f"Embedding API request timeout in seconds (default: {SEARCH_DEFAULT_EMBEDDING_TIMEOUT}).",
    )


def add_cache_arg(parser: argparse.ArgumentParser) -> None:
    """Index location override — used by every command that opens the
    on-disk index."""
    parser.add_argument(
        "--cache-dir",
        default=None,
        help=(
            "Override the index location. Default: `<corpus>/.md-navigator/` "
            "inside the corpus itself."
        ),
    )


def add_max_heading_level_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--max-heading-level",
        type=int,
        default=6,
        choices=range(1, 7),
        metavar="1-6",
        help="Deepest heading level to index as separate section.",
    )


def add_auto_embed_args(parser: argparse.ArgumentParser, default_cap: int) -> None:
    """Add --max-auto-embed and --no-cache for read-path commands that
    can do small inline embedding work on warm-start. `default_cap`
    differs slightly by command — pass the right value."""
    parser.add_argument(
        "--max-auto-embed",
        type=int,
        default=default_cap,
        help=(
            f"If the new-section delta needs more than this many chunks to "
            f"embed, the command refuses and asks you to run `index` first "
            f"(default: {default_cap}). Pass 0 to allow any size."
        ),
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Wipe the on-disk index for this corpus and rebuild from scratch.",
    )


def add_json_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of the human Markdown view.",
    )
