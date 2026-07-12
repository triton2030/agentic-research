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

## Preview And Execute A Mutation

First call without `--confirm`:

```bash
"$CU" api POST /v2/list/LIST_ID/task --body '{"name":"Example"}'
```

The result shows method, path, query, body, digest, expiry, and a one-use token.
Show the intended delta to the user but do not echo the token. After the user
approves that exact preview, repeat the identical request locally:

```bash
"$CU" api POST /v2/list/LIST_ID/task --body '{"name":"Example"}' \
  --confirm 'PREVIEW_TOKEN'
```

Changing method, path, query, or body invalidates the token. Tokens expire after
15 minutes and are consumed once. Named task create/delete previews also fetch
the target/current object; generic mutations require an explicit pre-read.

## Custom Task IDs

For a custom ID, include both flags on named update/delete commands:

```bash
"$CU" task update CUSTOM-123 --custom-id --workspace-id WORKSPACE_ID \
  --body '{"status":"in progress"}'
"$CU" task delete CUSTOM-123 --custom-id --workspace-id WORKSPACE_ID
```

The first call produces a preview; repeat with its token only after approval.

## MCP Equivalents

- `clickup_control_api_get`: generic JSON read.
- `clickup_control_api_write`: preview/execute generic JSON mutation; supports
  `query_json`, `body_json`, and `confirmation_token`.
- `clickup_control_hierarchy`, `clickup_control_search_tasks`,
  `clickup_control_get_task`: frequent reads.
- `clickup_control_create_task`, `clickup_control_update_task`,
  `clickup_control_delete_task`: named preview/execute flows.

Never pass the personal API token to these tools; the runtime resolves it.
