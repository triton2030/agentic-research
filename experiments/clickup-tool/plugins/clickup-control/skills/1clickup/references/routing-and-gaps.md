# Routing And Live Gaps

Snapshot: 2026-07-12. Re-check official docs and live tool discovery when the
request depends on current coverage.

## Choose The Surface

| Need | Default surface | Why |
|---|---|---|
| Search across tasks, Docs, attachments, Chat, dashboards, or whiteboards | Official ClickUp MCP `clickup_search` | Broad semantic workspace search |
| Resolve people, inspect common task/Doc/Chat data, attach a file, or combine supported actions | Official ClickUp MCP | Typed convenience tools and OAuth context |
| Exact hierarchy, deterministic reporting, or a missing/broken official MCP operation | `clickup-control` MCP/CLI | Stable IDs and direct Public API responses |
| Goals/KRs, checklists, Views, templates, webhook registrations, or uncommon JSON endpoints | `clickup-control` generic API | Public API is broader than the installed MCP snapshot |
| Automations, Dashboards, Whiteboards, settings, or an API-absent feature | ClickUp desktop/browser | UI owns these flows |

Prefer one owner for the main action. Use a second read surface only when it
materially cross-checks hierarchy, permissions, or a high-cost decision.

## Observed Live Gaps

- The official hierarchy tool advertises numeric `max_depth`, while its runtime
  currently expects string values. Omit the argument or use
  `clickup_control_hierarchy` / `bin/clickup tree`.
- Official MCP documentation and live tool exposure can drift. Live discovery
  is stronger evidence than the marketing/tool table.
- Official MCP is OAuth-only. The private API runtime uses the personal token.
- The private generic client is JSON-only. Route multipart task attachments to
  the official MCP attachment tool.
- The private runtime manages webhook registrations/status. It does not receive
  webhook deliveries or verify their signatures.
- ClickUp Chat v3 is experimental; verify its current contract before use.

## Current Sources

- https://developer.clickup.com/docs/mcp-tools
- https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server
- https://developer.clickup.com/llms.txt
- https://developer.clickup.com/docs/apis-available-by-plan
- https://developer.clickup.com/docs/chat
