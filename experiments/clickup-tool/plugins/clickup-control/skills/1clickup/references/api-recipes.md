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
"$CU" task get TASK_ID
```

`doctor` returns redacted health only. Use `workspaces` or a targeted endpoint
when actual IDs/names are required.

## Generic JSON Reads

```bash
"$CU" api GET /v2/team/WORKSPACE_ID/goal
"$CU" api GET /v2/team/WORKSPACE_ID/view
"$CU" api GET /v2/team/WORKSPACE_ID/webhook
"$CU" api GET /v2/task/TASK_ID/time_in_status
```

Confirm each path against current official docs. Some endpoint families use the
legacy API term `team` for Workspace.

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

- `clickup_control_api_get`: generic JSON read.
- `clickup_control_api_write`: execute a generic JSON mutation; supports
  `query_json` and `body_json`.
- `clickup_control_hierarchy`, `clickup_control_search_tasks`,
  `clickup_control_get_task`: frequent reads.
- `clickup_control_create_task`, `clickup_control_update_task`,
  `clickup_control_delete_task`: named direct-write flows.

Never pass the personal API token to these tools; the runtime resolves it.
