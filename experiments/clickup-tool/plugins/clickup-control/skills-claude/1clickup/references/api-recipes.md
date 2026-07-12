# API Recipes

Use only after `1clickup` selects the private API route. Replace placeholders
with IDs resolved through safe reads.

## Launcher

```bash
CLICKUP_TOOL_HOME="${CLICKUP_TOOL_HOME:-/Users/triton/Documents/GitHub/agentic-research/experiments/clickup-tool}"
CU="$CLICKUP_TOOL_HOME/bin/clickup"
```

## Health And Discovery

```bash
"$CU" doctor --live
"$CU" workspaces
"$CU" tree WORKSPACE_ID
"$CU" task search WORKSPACE_ID --include-closed
"$CU" task search WORKSPACE_ID --include-closed --all
"$CU" task get TASK_ID
```

`doctor` returns redacted health only. Use `workspaces` or a targeted endpoint
when actual IDs/names are required.

## Generic JSON Reads

```bash
"$CU" api GET /v2/team/WORKSPACE_ID/goal
"$CU" api GET /v2/team/WORKSPACE_ID/webhook
"$CU" api GET /v2/task/TASK_ID/time_in_status
```

Confirm each path against current official docs. Some endpoint families use the
legacy API term `team` for Workspace.

For Views, use [views.md](views.md) and named View commands. Do not hand-build a
partial generic PUT.

## Task Views

```bash
"$CU" view list list LIST_ID
"$CU" view get VIEW_ID
"$CU" view create list LIST_ID --name "Delivery" --type board \
  --config '{"sorting":{"fields":[{"field":"priority","dir":1}]}}'
"$CU" view configure VIEW_ID \
  --patch '{"settings":{"show_images":false}}'
"$CU" view tasks VIEW_ID --all
"$CU" view delete VIEW_ID
```

Named configure performs full read-modify-write and verification while
preserving unknown nested settings.

## Portfolio Audit

```bash
"$CU" audit portfolio WORKSPACE_ID LIST_ID
"$CU" audit portfolio WORKSPACE_ID LIST_ID \
  --expect '{"tasks":{"count":35},"views":{"count":14}}'
```

The audit is read-only, exhausts task/View pagination, reports unresolved
checklists and parent gaps, and compares an optional partial expected manifest.
Read [verification.md](verification.md) before defining broad acceptance.

## Execute A Mutation

```bash
"$CU" api POST /v2/list/LIST_ID/task --body '{"name":"Example"}'
```

The command executes immediately. Resolve the target first when identity,
current values, or valid field/status options affect correctness, and re-read
the changed object afterward.

## Custom Task IDs

For a custom ID, include both flags on named update/delete commands:

```bash
"$CU" task update CUSTOM-123 --custom-id --workspace-id WORKSPACE_ID \
  --body '{"status":"in progress"}'
"$CU" task delete CUSTOM-123 --custom-id --workspace-id WORKSPACE_ID
```

## MCP Equivalents

In Claude Code these tools are usually deferred: load every schema you need
with one ToolSearch `select:` call before invoking any of them.

- `clickup_control_api_get`: generic JSON read.
- `clickup_control_api_write`: execute a generic JSON mutation; supports
  `query_json` and `body_json`.
- `clickup_control_hierarchy`, `clickup_control_search_tasks`,
  `clickup_control_get_task`: frequent reads.
- `clickup_control_create_task`, `clickup_control_update_task`,
  `clickup_control_delete_task`: named direct-write flows.
- `clickup_control_list_views`, `clickup_control_get_view`,
  `clickup_control_create_view`, `clickup_control_configure_view`,
  `clickup_control_delete_view`, `clickup_control_get_view_tasks`: named View
  lifecycle and visible-task flows.
- `clickup_control_audit_portfolio`: read-only persistence audit with optional
  partial expected manifest.

Never pass the personal API token to these tools; the runtime resolves it.
