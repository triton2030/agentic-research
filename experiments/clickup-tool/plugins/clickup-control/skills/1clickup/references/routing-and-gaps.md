# Routing And Live Gaps

Snapshot: 2026-07-12. Re-check official docs and live tool discovery when the
request depends on current coverage.

## Choose The Surface

| Need | Default surface | Why |
|---|---|---|
| Search across tasks, Docs, attachments, Chat, dashboards, or whiteboards | Official ClickUp MCP `clickup_search` | Broad semantic workspace search |
| Resolve people, inspect common task/Doc/Chat data, attach a file, or combine supported actions | Official ClickUp MCP | Typed convenience tools and OAuth context |
| Exact hierarchy, deterministic reporting, or a missing/broken official MCP operation | `clickup-control` MCP/CLI | Stable IDs and direct Public API responses |
| Task Views: List, Board/Kanban, Table, sorting, filters, columns, or visible tasks | `clickup-control` named View commands | Public API supports deterministic View configuration |
| Privacy/access for a supported object with known IDs | Documented v3 ACL through generic API | API supports ACL writes, but sharing can incur charges and lacks a matching public read contract |
| Goals/KRs, checklists, templates, webhook registrations, or uncommon JSON endpoints | `clickup-control` generic API | Public API is broader than the installed MCP snapshot |
| View pin/protect/default/tab order, Automations, Dashboard/Whiteboard content, or an API-absent feature | ClickUp desktop/browser | UI owns these flows |

Prefer one owner for the main action. Use a second read surface only when it
materially cross-checks hierarchy, permissions, or a high-cost decision.

## Observed Live Gaps

- The official hierarchy tool advertises numeric `max_depth`, while its runtime
  currently expects string values. Omit the argument or use
  `clickup_control_hierarchy` / `bin/clickup tree`.
- Official MCP documentation and live tool exposure can drift. Live discovery
  is stronger evidence than the marketing/tool table.
- Current official docs describe 48 capability rows while the connected Codex
  catalog exposes 32 tools. Treat a documented-but-missing tool as unavailable
  and route to the public API or UI.
- Official ClickUp MCP does not currently expose task View management. Its Chat
  channel "views" are not List/Board/Table task Views.
- View updates use a complete PUT body. Preserve unknown nested settings during
  read-modify-write; the OpenAPI schema disagrees with its own object examples.
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
