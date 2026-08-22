---
description: "Target classification and complete-enough retrieval across databases, data sources, views, and search."
---

# Databases, Search, And Views

## Classify The URL

A Notion database is a container, a data source owns rows and properties, and a
view owns a saved presentation with filters and sorts. A copied database URL can
contain `?v=VIEW_ID`; preserve that ID when the request concerns the visible
view rather than all rows.

For a single-source database or URL:

```bash
ntn datasources query 'NOTION_URL' --json
```

For a database with multiple data sources:

```bash
ntn datasources resolve DATABASE_ID --json
ntn datasources query DATA_SOURCE_ID --json
```

Resolve the schema before constructing property filters. Prefer property IDs in
durable code when names can be renamed. Use `--limit`, inspect the returned
cursor, and continue with `--start-cursor`; report any unvisited remainder.

## Respect A Saved View

`ntn datasources query` queries the data source. It does not prove that the
result matches a saved view's filters or order. When the user refers to the
specific view from `v=VIEW_ID`, use the Views API:

```bash
ntn api /v1/views/VIEW_ID -X GET --docs
ntn api /v1/views/VIEW_ID
ntn api /v1/views/VIEW_ID/queries --docs
ntn api /v1/views/VIEW_ID/queries --data '{"page_size":100}'
```

A view query returns a `query_id` and cached results. Paginate through that
query, then delete it when finished. The cache expires after roughly 15 minutes.
Current documentation caps a view query cache at 10,000 matches and marks a
truncated query as `request_status.type = incomplete`; never report that result
as complete coverage.

## Search Strategy

The public `/v1/search` endpoint searches page and data-source titles, not full
page bodies. It is best for locating candidate objects:

```bash
ntn api /v1/search --docs
ntn api /v1/search --data @search.json
```

For a question like “where did I mention crypto?” use a bounded two-stage
search:

1. Identify the intended database, view, or page cohort.
2. Enumerate all candidate page IDs with pagination.
3. Fetch each page's Markdown and JSON status.
4. Search locally across bodies and relevant properties.
5. Return matching page titles/URLs and quoted context, plus the denominator,
   unread pages, truncation, unknown blocks, and pagination remainder.

An empty title search is not evidence that body text is absent. An empty body
scan means only “no match in the reported cohort and readable content.”

## Privacy And Scale

Do exact local search before embeddings. Do not send private Notion content to
an external embedding, search, or model service unless the user explicitly
authorizes that data transfer. For large recurring scans, use bounded
concurrency, respect `429 Retry-After`, and consider webhooks instead of polling.

## Official Sources

- [Working with databases](https://developers.notion.com/guides/data-apis/working-with-databases)
- [Search by title](https://developers.notion.com/reference/post-search)
- [Search limitations](https://developers.notion.com/reference/search-optimizations-and-limitations)
- [Working with views](https://developers.notion.com/guides/data-apis/working-with-views)
- [Create a view query](https://developers.notion.com/reference/create-view-query)
