"""Shared terminal guidance for agent-facing index warmup hints."""

from __future__ import annotations

import shlex
from collections.abc import Iterable
from pathlib import Path


INDEX_DRY_RUN_PLACEHOLDER = "md index CORPUS --dry-run --json"


def quote_arg(value: str | Path) -> str:
    return shlex.quote(str(value))


def path_filter_args(
    *,
    path_include: Iterable[str] | None = None,
    path_exclude: Iterable[str] | None = None,
) -> list[str]:
    args: list[str] = []
    for pattern in path_include or []:
        args.extend(["--path-include", quote_arg(pattern)])
    for pattern in path_exclude or []:
        args.extend(["--path-exclude", quote_arg(pattern)])
    return args


def index_dry_run_command(
    corpus: str | Path,
    *,
    path_include: Iterable[str] | None = None,
    path_exclude: Iterable[str] | None = None,
) -> str:
    parts = [
        "md",
        "index",
        quote_arg(corpus),
        *path_filter_args(path_include=path_include, path_exclude=path_exclude),
        "--dry-run",
        "--json",
    ]
    return " ".join(parts)


def index_confirm_command(
    corpus: str | Path,
    *,
    path_include: Iterable[str] | None = None,
    path_exclude: Iterable[str] | None = None,
    transaction_id: str = "<id>",
) -> str:
    parts = [
        "md",
        "index",
        quote_arg(corpus),
        *path_filter_args(path_include=path_include, path_exclude=path_exclude),
        "--confirm",
        "--transaction-id",
        transaction_id,
        "--json",
    ]
    return " ".join(parts)


def scoped_rerun_command(
    subcommand: str,
    corpus: str | Path,
    *,
    path_include: Iterable[str] | None = None,
    path_exclude: Iterable[str] | None = None,
) -> str:
    parts = [
        "md",
        subcommand,
        quote_arg(corpus),
        *path_filter_args(path_include=path_include, path_exclude=path_exclude),
        "--json",
    ]
    return " ".join(parts)
