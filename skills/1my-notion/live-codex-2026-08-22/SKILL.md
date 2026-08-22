---
name: 1my-notion
description: >
  Use when the user gives a Notion page, database, data-source, or view URL, or
  asks to inspect, search, create, edit, or automate their personal Notion
  through the local `ntn` CLI. Resolve the live surface before calls, preserve
  remote content, and distinguish explicit pull/push from automatic sync.
---

# 1 My Notion

## Outcome

Do the smallest reliable Notion operation through the installed `ntn` CLI and
return the affected Notion address, coverage, and verification evidence.

## Contract

1. Start from the live runtime: run `ntn --version`, then the narrow command's
   `--help`. For raw API work, inspect `ntn api ls` and the endpoint with
   `--docs` or `--spec`; copied command names are not a contract.
2. Check access with `ntn whoami` or `ntn doctor`. Never print, log, or paste
   `ntn auth token` or `NOTION_API_TOKEN`.
3. Classify the target before acting: page, database, data source, or view.
   Preserve a URL's `v=` view ID when the user's intent is “what this view
   shows.”
4. Default to read-only discovery. Before editing an existing page, fetch its
   current Markdown and machine-readable status in the same turn.
5. Treat local Markdown as an explicit snapshot, not a live mirror. Do not
   claim background synchronization unless a real Worker or another active
   sync owner proves it.
6. Use convenience commands for ordinary page Markdown and data-source queries;
   use `ntn api` for properties, templates, views, targeted Markdown updates,
   and endpoints missing from the convenience surface.
7. After a write, retrieve the changed object again. Report truncation,
   unsupported blocks, pagination remainder, skipped properties, and any
   semantic normalization instead of calling the result exact.

## Conditional References

Open only the reference that owns the current decision:

- CLI discovery, authentication, API invocation, and rate limits:
  [`cli-and-auth.md`](references/cli-and-auth.md).
- Page Markdown, local snapshots, safe create/edit, and round-trip checks:
  [`pages-and-roundtrip.md`](references/pages-and-roundtrip.md).
- Database URLs, data sources, views, title search, body search, and coverage:
  [`databases-search-and-views.md`](references/databases-search-and-views.md).
- Creative page layouts, formulas, charts, dashboards, and extension surfaces:
  [`creative-surfaces.md`](references/creative-surfaces.md).
- Persistent schedules, webhooks, tools, syncs, deployment, and secrets:
  [`workers.md`](references/workers.md).

## Stop

Stop before a write when the target identity is ambiguous, current content was
not retrieved, the response is truncated or contains unknown blocks that may be
overwritten, required permissions are absent, or the requested automation would
introduce an unapproved persistent Worker, secret, external data transfer, or
recurring cost.

Finish with: operation and target; read/write scope; live command or endpoint;
verification; coverage or remainder; whether any persistent automation now
exists.
