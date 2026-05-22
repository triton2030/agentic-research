#!/usr/bin/env python3
import json
from typing import Optional

import typer


app = typer.Typer(add_completion=False)


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def emit(command: str, **kwargs) -> None:
    typer.echo(json.dumps({"framework": "typer", "command": command, "args": kwargs}, ensure_ascii=False, indent=2))


@app.command("section-blast-radius")
def section_blast_radius(
    path: str,
    corpus: str,
    query: str = typer.Option(...),
    heading_id: Optional[str] = None,
    scan: Optional[str] = None,
    depth: int = 2,
    limit: int = 5,
    path_include: list[str] = typer.Option([], "--path-include"),
    path_exclude: list[str] = typer.Option([], "--path-exclude"),
) -> None:
    emit("section-blast-radius", path=path, corpus=corpus, query=query, heading_id=heading_id, scan=scan, depth=depth, limit=limit, path_include=path_include, path_exclude=path_exclude)


@app.command("query-by-type")
def query_by_type(
    corpus: str,
    types: str = typer.Option(...),
    filter: Optional[str] = None,
    limit: int = 10,
    path_include: list[str] = typer.Option([], "--path-include"),
    path_exclude: list[str] = typer.Option([], "--path-exclude"),
    compact: bool = False,
) -> None:
    emit("query-by-type", corpus=corpus, types=_csv(types), filter=filter, limit=limit, path_include=path_include, path_exclude=path_exclude, compact=compact)


@app.command("edit-context")
def edit_context(
    path: str,
    mode: str = typer.Option("preview"),
    scan: Optional[str] = None,
    depth: int = 2,
    query: Optional[str] = None,
    corpus: Optional[str] = None,
) -> None:
    if mode not in {"preview", "full", "strict"}:
        raise typer.BadParameter("mode must be preview, full, or strict")
    emit("edit-context", path=path, mode=mode, scan=scan, depth=depth, query=query, corpus=corpus)


if __name__ == "__main__":
    app()
