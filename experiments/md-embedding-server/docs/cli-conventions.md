---
description: CLI conventions for md agent-facing subcommands, JSON output, flags,
  paths, and schema vocabulary.
depends-on: []
---
# CLI Conventions

Task-001 decisions for the `md` CLI surface.

## Subcommands

Decision: MCP `md_read_related` maps to CLI `md read-related`; no `md_`
prefix in CLI.

Rationale: kebab-case keeps agent prompts readable and matched the original
`md_navigator.py` command naming.

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

## Help Text

Decision: `src/md_cli/catalog.py` is the only source for agent-facing argument
help. Each public `input_schema.properties.*` entry carries a non-empty
`description`; `md_cli.main` reads that schema description directly.

Rationale: the CLI parser, MCP/catalog snapshot and installed skill catalogs
must not drift through a second hand-maintained fallback dictionary.

Example: `md search-read --help` explains `--query`, `--limit`,
`--path-include`, `--token-budget` and `--expanded` from the same schema that
`md tools md_search_read --json` exposes.

Edge case: when adding a new optional flag, update the catalog property
description in the same change as the signature. The contract test rejects
blank descriptions.

## Booleans

Decision: presence flags such as `--expanded`; negation only when a default true
needs override.

Rationale: avoids `"true"` / `"false"` string ambiguity.

Example: `md search-read knowledge --query "skill contract" --expanded --json`.

Context ladder rule: normal output is already the bounded map for
agent-facing reading commands. Do not call it compact in new docs. Legacy
`--compact` is accepted only as a compatibility alias where it already
existed (`orient`, `query-by-type`, `refactor-candidates`).

Edge case: mutating/cost-bearing gates use explicit mode flags (`--dry-run`,
`--confirm`) because they represent separate safety states, not cosmetic
booleans. `--confirm` must be paired with `--transaction-id` for gated tools;
the only safe next-step before that token exists is a dry-run.

## Index Guidance

Decision: any human-facing warmup hint that prints `md index ...` must use
the shared index-guidance helper.

Rationale: nested corpora are refused by default; the correct repair is often
the indexed parent corpus plus translated `--path-include` / `--path-exclude`.
Hand-built strings are likely to lose that scope and point the agent at the
wrong corpus.

Example:

```bash
md index PARENT --path-include child/** --dry-run --json
md index PARENT --path-include child/** --confirm --transaction-id <id> --json
md overlaps PARENT --path-include child/** --json
```

Edge case: `_envelope.corpus_state.recommended_action.args` and
`_envelope.next_step[].args` are the structured source for agent action. Human
text can mirror it, but must not widen scope or suggest bare `--confirm`.

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

## Schema Vocabulary

Several `--json` outputs use a shared "reverse-relationship" vocabulary that
trips up first-time agent readers. Settle the
meaning once, here, so handlers and `--help` text can stay short.

Decision: `md impact` and any future reverse-scan output use these keys with
fixed semantics.

| Key | What it captures | Caused by which edit |
|---|---|---|
| `dependent_breaks` | Files holding `depends-on: [this]` in frontmatter. They consume this file as a source; editing/deleting this file creates a propagation worklist. | reverse depends-on graph |
| `body_wikilink_refs` | Files whose **body text** contains an Obsidian-style wikilink to this file, with or without anchor. No graph contract attached. | hand-written body links |
| `body_markdown_refs` | Files whose **body text** contains a CommonMark link to this file. No graph contract attached. | hand-written body links |

Rule of thumb: `*_breaks` are **contract** breaks (frontmatter promises
broken). `*_refs` are **content** breaks (prose references that will produce
broken links but no obligation cascade). An agent deciding "safe to delete?"
must look at both classes — contract breaks block the move, content breaks
just need search-and-replace.

Rationale: shared vocabulary lets `md impact`, `md preflight`, future
`md unused` and any reverse-scan tool reuse identical keys; agent prompts
that mention one transfer to all.

Example caller: «if `dependent_breaks` is non-empty, run `md preflight` on each
listed holder before deleting».

Edge case: a single file can appear in both `dependent_breaks` AND
`body_wikilink_refs` if it both holds reverse `depends-on` and links in body
prose. Both lists report it independently — dedup is the caller's job.

Companion field for counts: where a list field exists for human inspection
(e.g. `cycles` in `md health`), the corresponding count field (`cycles_count`)
exists in the same payload so agents can apply `len()` uniformly across
count-fields without polymorphic type-checks. Add the `_count` companion when
introducing a new agent-facing list whose typical caller wants both.
