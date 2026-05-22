# CLI Conventions

Task-001 decisions for the `md` CLI surface.

## Subcommands

Decision: MCP `md_read_related` maps to CLI `md read-related`; no `md_`
prefix in CLI.

Rationale: matches existing `md_navigator.py` kebab-case commands and keeps
agent prompts readable.

Example: `md section-blast-radius PATH CORPUS --query "owner rule" --json`.

Edge case: `md_ping` becomes `md ping`, not bare `md`.

## JSON Output

Decision: every agent-facing invocation supports `--json` and receives the
preserved `_envelope` shape.

Rationale: skills need stable machine output; human output is only for local
debugging.

Example: `md search knowledge "skill contract" --limit 3 --json`.

Edge case: `md tools --json` also goes through the runner; the handler returns
`ToolResult`, not raw JSON.

## Booleans

Decision: presence flags such as `--compact`; negation only when a default true
needs override.

Rationale: avoids `"true"` / `"false"` string ambiguity.

Example: `md orient knowledge --compact --json`.

Edge case: mutating/cost-bearing gates use explicit mode flags (`--dry-run`,
`--confirm`) because they represent separate safety states, not cosmetic
booleans. `--confirm` must be paired with `--transaction-id` for gated tools;
the only safe next-step before that token exists is a dry-run.

## Arrays

Decision: repeated flags for path filters; comma-separated values only for short
enum lists.

Rationale: paths may contain commas; enum lists are agent-readable as CSV.

Examples:

- `md search knowledge "routing" --path-include _ops --path-include knowledge --json`
- `md query-by-type _ops --types decision,open-question --json`

Edge case: when a schema accepts arbitrary strings, prefer repeated flags over
CSV.

## Nested Objects

Decision: flatten stable two-level filters; use JSON string flags only for
dynamic structures.

Rationale: stable filters should be discoverable in `--help`; dynamic payloads
should not create a custom mini-language.

Example: `md query-by-type _ops --types decision --filter-depth 2 --json` if
the filter shape remains stable.

Edge case: `md extract --map-data` keeps a JSON value because `map_data` is a
real nested object produced by `md toc` / `md ls`.

## Paths

Decision: keep existing positional style where the current Python CLI already
uses it; otherwise use named `--path` / `--corpus`.

Rationale: preserves muscle memory for common commands while avoiding ambiguous
multi-path tools.

Examples:

- `md status knowledge --json`
- `md preflight README.md --scan . --json`
- `md read-related --paths README.md --scan . --json`

Edge case: tools with multiple target files use repeated `--paths`, not many
positionals.

## Optional Values

Decision: omit absent optional values; never pass empty string or `null`.

Rationale: keeps argparse namespace and catalog schema aligned with MCP
optional fields.

Example: use `md edit-context README.md --mode preview --json`, not
`--query ""`.

Edge case: an explicit empty query is a usage error for
`md section-blast-radius`, because semantic search needs a real query.

## Spike Coverage

Task-002 verified these edge cases with `argparse`, Typer and catalog-driven
argparse:

- `md section-blast-radius`
- `md query-by-type`
- `md edit-context`
