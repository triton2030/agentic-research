---
description: "Native Notion layouts, typed data systems, programmable views, and extension-surface boundaries."
---

# Creative Surfaces

Contents: Page Layout · Typed Data Systems · Views And Visualizations ·
Extensions, Not Generic Plugins · Official Sources.

## Page Layout

Enhanced Markdown maps to native Notion blocks. It supports colored headings
and text, callouts, toggles, toggle headings, columns, tables, equations,
Mermaid, media, page/database references, table of contents, synced blocks,
mentions, custom emoji, and citations. Use tabs for child indentation.

```markdown
<callout icon="🧪" color="purple_bg">
	**Native block**, not HTML pasted into a text paragraph.
</callout>

<columns>
	<column>
		Left side
	</column>
	<column>
		<details color="blue_bg">
		<summary>Toggle</summary>
			Nested content
		</details>
	</column>
</columns>
```

Prefer a targeted Markdown `update_content` operation for an existing page.
Retrieve before and after the write; normalization of indentation or block
syntax is expected, but `truncated` and `unknown_block_ids` must remain visible.

## Typed Data Systems

A database is the container, a data source owns the schema and rows, and each
row is a page. Creating a database through the current API provisions an initial
data source and default table view. Data-source properties include title,
rich-text, number, select/status, multi-select, date, checkbox, people, files,
place, relations, rollups, formulas, buttons, and unique IDs.

Formula definitions are schema, not row values:

```json
{
  "Leverage": {
    "formula": {
      "expression": "prop(\"Impact\") - prop(\"Effort\")"
    }
  }
}
```

After schema creation, retrieve the data source and use returned property IDs
for durable view configuration. Formula reads can require access to every
related page and data source they traverse.

## Views And Visualizations

The current Views API supports `table`, `board`, `list`, `calendar`, `timeline`,
`gallery`, `form`, `chart`, `map`, and `dashboard`. Each view can own filters,
sorts, quick filters, property visibility, and type-specific presentation.

- A Gantt-like plan is a `timeline` with start and optional end date property
  IDs; dependency arrows require a relation configured through `arrows_by`.
- Native chart types are `column`, `bar`, `line`, `donut`, and `number`.
  Waterfall is not a native chart type in the observed schema. Do not rename a
  column or cumulative line chart “waterfall” without explaining the emulation.
- A dashboard is a grid of widget views. Create the dashboard first, then add
  table, board, timeline, or chart views using its `view_id` and a placement.
- Retrieve every created view and verify resolved property IDs, configuration,
  filters, sorts, and `dashboard_view_id` where applicable.

Always inspect `ntn api /v1/views -X POST --spec` before authoring a view; this
surface evolves faster than ordinary page blocks.

## Extensions, Not Generic Plugins

Notion does not expose one generic “plugin” model. Choose the actual surface:

- **Connection** — private or OAuth integration using the public API; a public
  connection can optionally be reviewed and listed on Marketplace.
- **Link Preview connection** — authenticated unfurling for links from a domain
  you own; it requires OAuth, special access, and platform/security review.
- **Notion MCP** — hosted agent-facing access for external AI clients.
- **Worker** — hosted TypeScript for syncs, webhooks, and tools callable by
  Notion Custom Agents.
- **MCP connection in a Custom Agent** — lets an in-Notion agent call an
  external system; plan and permission availability must be checked live.

Use page/database APIs for native Notion content. Add an extension only when the
outcome requires external data, custom code, authenticated unfurling, or an
agent tool that Notion and its MCP do not already provide.

## Official Sources

- [Enhanced Markdown](https://developers.notion.com/guides/data-apis/enhanced-markdown)
- [Data-source properties](https://developers.notion.com/reference/property-object)
- [Working with views](https://developers.notion.com/guides/data-apis/working-with-views)
- [Connections overview](https://developers.notion.com/guides/get-started/overview)
- [Notion MCP](https://developers.notion.com/guides/mcp/overview)
- [Workers overview](https://developers.notion.com/workers/get-started/overview)
- [Link Preview connections](https://developers.notion.com/guides/link-previews/introduction)
