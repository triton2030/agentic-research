# CLI Framework Decision

Verdict: `argparse` with catalog-driven parser construction.

## Evidence

Three spike files exist in `spike/`:

- `argparse_version.py`
- `typer_version.py`
- `catalog_driven.py`

The spike covered the three hardest signatures:

- `section-blast-radius`: required query, optional heading id, repeated path filters.
- `query-by-type`: enum-like list input through `--types`.
- `edit-context`: mode enum and optional branching arguments.

## Benchmark

Measured on 2026-05-22 with command help output redirected to `/tmp`.

| Implementation | Command | real |
|---|---|---:|
| argparse | `python3 spike/argparse_version.py section-blast-radius --help` | 0.08s |
| catalog-driven argparse | `python3 spike/catalog_driven.py section-blast-radius --help` | 0.08s |
| Typer | `uv run --with typer python spike/typer_version.py section-blast-radius --help` | 0.34s |

## Rationale

`argparse` wins Phase A because it is stdlib, fastest, enough for all three
edge-case signatures, and preserves lazy startup. Typer has nicer help output,
but adds a runtime dependency and higher cold-start cost for a tool whose common
path is agent invocation with `--json`.

Catalog-driven registration wins Phase B because `catalog.py` must already be
the single source of truth for tool names, schemas, handler modules and docs.
Hand-written parser registration would recreate drift between catalog,
subcommand help and skills.

## Accepted Trade-offs

- Help output is plainer than Typer, but stable and dependency-free.
- Catalog-to-argparse conversion needs a small local builder, but the builder
is cheaper than 29 hand-maintained parsers.
- Complex dynamic objects may still use JSON string flags, but the current
three hardest signatures work with flattened/repeated flags.

## Production Direction

Task-101 should create `md_cli/catalog.py` and `md_cli/argparse_builder.py`.
Handlers should receive an already parsed namespace and return `ToolResult`;
they should not own parser drift, JSON serialization or envelope wrapping.
