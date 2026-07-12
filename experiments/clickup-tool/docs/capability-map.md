# Capability Map

Snapshot: 2026-07-12. Verify current official docs before depending on a new
endpoint.

| Surface | Best use | Material limits |
|---|---|---|
| Official ClickUp MCP | Semantic search, assignee resolution, common task/Doc/Chat composites | OAuth-only; live tools can lag docs |
| ClickUp Public API | Deterministic CRUD, Goals/KRs, checklists, Views, templates, webhooks, time data | Personal token inherits the user's permissions; plan/rate limits apply |
| ClickUp desktop/browser | Automations, Dashboards, Whiteboards, settings, UI-only work | UI automation is slower and more brittle |

## Public API Families

- identity, Workspaces, roles and plan information;
- Spaces, Folders, Lists, Views, templates and shared hierarchy;
- tasks, custom task types/fields, tags, checklists, links and dependencies;
- comments and threaded replies; use official MCP for multipart task uploads;
- Goals and Key Results;
- timers, time entries, time-in-status and reporting;
- Docs and experimental Chat v3;
- webhook registration and health/status; inbound delivery/signature
  verification remains outside this runtime;
- Enterprise-only user/guest administration and audit logs.

Generic CLI/MCP API operations intentionally cover JSON endpoints. Requested
mutations execute directly, including semantically read-like POSTs.

## Sources

- https://developer.clickup.com/llms.txt
- https://developer.clickup.com/docs/authentication
- https://developer.clickup.com/docs/rate-limits
- https://developer.clickup.com/docs/apis-available-by-plan
- https://developer.clickup.com/docs/mcp-tools
- https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server
- https://developer.clickup.com/docs/chat
