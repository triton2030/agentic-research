# Capability Map

Snapshot: 2026-07-12. Verify current official docs before depending on a new
endpoint.

| Surface | Best use | Material limits |
|---|---|---|
| Official ClickUp MCP | Semantic search, assignee resolution, common task/Doc/Chat composites | OAuth-only; live tools can lag docs |
| ClickUp Public API | Deterministic CRUD, Goals/KRs, checklists, named Views, templates, webhooks, time data, adaptive JSON endpoints | Personal token inherits the user's permissions; plan/rate limits apply |
| ClickUp desktop/browser | Automations, Dashboards, Whiteboards, settings, UI-only work | UI automation is slower and more brittle |

## Public API Families

- identity, Workspaces, roles and plan information;
- Spaces, Folders, Lists, Views, templates and shared hierarchy;
- tasks, custom task types/fields, tags, checklists, links and dependencies;
- comments and threaded replies; use official MCP for multipart task uploads;
- Goals and Key Results;
- timers, time entries, time-in-status and reporting;
- Docs and experimental Chat v3;
- v3 task moves, per-user estimates, and object privacy/access through generic
  JSON routes after checking current schemas;
- webhook registration and health/status; inbound delivery/signature
  verification remains outside this runtime;
- Enterprise-only user/guest administration and audit logs.

Named View commands cover the full task-View lifecycle and preserve unknown
nested settings through verified read-modify-write. Generic CLI/MCP operations
accept any JSON body for current documented endpoints. Multipart and UI-only
operations keep their dedicated routes. The current v3 attachment schema does
not expose a usable binary field, so File Custom Field upload remains a known
gap rather than an inferred implementation.

Named exhaustive task reads stop on an explicit last page, an empty page, or a
repeated page and deduplicate task IDs. The read-only portfolio audit combines
that pagination with saved View configuration, visible task sets, checklist
state, Goals, templates, Docs, statuses, fields, and task types. Optional
expected manifests make acceptance explicit without hard-coding one workspace
model into the runtime.

## Sources

- https://developer.clickup.com/llms.txt
- https://developer.clickup.com/docs/authentication
- https://developer.clickup.com/docs/rate-limits
- https://developer.clickup.com/docs/apis-available-by-plan
- https://developer.clickup.com/docs/mcp-tools
- https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server
- https://developer.clickup.com/docs/chat
