---
name: 1clickup
description: >
  Use when the user asks to read or change ClickUp. Choose official MCP,
  clickup-control API, or UI fallback; preserve hierarchy and preview writes.
  Skip non-ClickUp planning.
---

# ClickUp Control

## Outcome

Complete the requested ClickUp result through the strongest live surface while
preserving hierarchy, permissions, and user intent. Use the official OAuth MCP
for semantic search and common composites; use `clickup-control` for broader or
deterministic Public API work; use desktop/browser control only for UI-only
features.

Runtime owner:
`/Users/triton/Documents/GitHub/agentic-research/experiments/clickup-tool`.
Never read or print its token file. Invoke the stable launcher or namespaced MCP
tools; credential resolution belongs to the runtime.

## Default Path

1. Establish the target Workspace and requested outcome. For hierarchy-sensitive
   work, rebuild parent/child truth from IDs instead of trusting visual nesting
   or aggregate `subtasks_count` alone.
2. Choose the surface:
   - official `clickup_*` MCP tools for semantic search, Docs/Chat, assignee
     resolution, and supported composites;
   - `clickup_control_*` tools or `bin/clickup` for Goals/KRs, checklists, Views,
     templates, webhooks, deterministic reporting, missing MCP operations, or a
     newly documented v2/v3 endpoint;
   - ClickUp desktop/browser only for Automations, Dashboards, Whiteboards,
     settings, and other API-absent UI flows.
   The official hierarchy tool currently has a `max_depth` schema mismatch;
   omit that argument or use `clickup_control_hierarchy` / `bin/clickup tree`.
3. Read before write. Resolve exact IDs, valid statuses, field schemas, current
   values, and plan/permission limits before constructing a mutation.
4. For writes, call once without a token and show the returned preview. It is
   bound to method, path, query, and body. Use its one-use token only after the
   user confirms that exact delta. Bulk, merge, and delete require explicit
   review; named create/delete previews include the target/current object. For
   generic writes, pre-read the target explicitly before creating a preview.
5. Verify by re-reading the changed object or recomputing the report. Distinguish
   API proof, inference, and any UI-only residual risk.

## Runtime Commands

```bash
CLICKUP_TOOL_HOME="${CLICKUP_TOOL_HOME:-/Users/triton/Documents/GitHub/agentic-research/experiments/clickup-tool}"
"$CLICKUP_TOOL_HOME/bin/clickup" doctor --live
"$CLICKUP_TOOL_HOME/bin/clickup" workspaces
"$CLICKUP_TOOL_HOME/bin/clickup" tree WORKSPACE_ID
"$CLICKUP_TOOL_HOME/bin/clickup" task get TASK_ID
"$CLICKUP_TOOL_HOME/bin/clickup" api GET /v2/ENDPOINT
```

Use generic `api` only after checking the current official ClickUp JSON endpoint
contract. It exists to prevent the skill from becoming a stale copy of the API
catalog, not to guess undocumented paths.

## Stop

- Stop before any external mutation not requested by the user.
- Stop when IDs, permissions, valid values, or target Workspace remain
  ambiguous after safe reads.
- Never bypass the runtime preview gate or send credentials through chat,
  command arguments, logs, plugin metadata, or task content.
