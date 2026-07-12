from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .auth import resolve_token, token_file_mode
from .capabilities import CAPABILITY_MAP
from .client import ClickUpClient, normalize_api_path
from .diagnostics import live_diagnostics, workspace_directory
from .operations import execute_mutation
from .views import configure_view, create_view, delete_view, get_view, get_view_tasks, list_views

mcp = FastMCP(
    "ClickUp Control",
    instructions=(
        "Use namespaced tools for deterministic ClickUp Public API access. "
        "Prefer the official ClickUp connector for semantic search. Execute requested "
        "mutations directly and verify their result."
    ),
    json_response=True,
)


def _object(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object")
    return parsed


def _json_value(value: str | None) -> Any:
    return None if value is None else json.loads(value)


@mcp.tool()
def clickup_control_capabilities() -> dict[str, list[str]]:
    """Return the routing boundary across official MCP, Public API, and desktop UI."""
    return CAPABILITY_MAP


@mcp.tool()
def clickup_control_doctor(live: bool = False) -> dict[str, object]:
    """Check credential resolution and optionally verify read-only API access."""
    token = resolve_token()
    result: dict[str, object] = {
        "ok": True,
        "token_source": token.source,
        "token_file_mode": token_file_mode(),
        "token_exposed": False,
    }
    if live:
        result["live"] = live_diagnostics(ClickUpClient(token.value))
    return result


@mcp.tool()
def clickup_control_api_get(path: str, query_json: str = "{}") -> dict[str, object]:
    """Read a documented JSON ClickUp v2/v3 endpoint using a relative API path."""
    return ClickUpClient().get(normalize_api_path(path), _object(query_json)).as_dict()


@mcp.tool()
def clickup_control_api_write(
    method: str,
    path: str,
    query_json: str = "{}",
    body_json: str = "{}",
) -> dict[str, object]:
    """Execute a JSON mutation against an official ClickUp v2/v3 endpoint."""
    normalized_path = normalize_api_path(path)
    return execute_mutation(
        ClickUpClient(),
        method,
        normalized_path,
        query=_object(query_json),
        body=_json_value(body_json),
    )


@mcp.tool()
def clickup_control_workspaces() -> dict[str, object]:
    """List authorized Workspace IDs and names without member profile data."""
    return workspace_directory(ClickUpClient())


@mcp.tool()
def clickup_control_hierarchy(
    workspace_id: str,
    include_archived: bool = False,
) -> dict[str, object]:
    """Build a Space, Folder, and List tree from the Public API."""
    return ClickUpClient().workspace_tree(workspace_id, include_archived)


@mcp.tool()
def clickup_control_get_task(
    task_id: str,
    custom_task_id: bool = False,
    workspace_id: str | None = None,
) -> dict[str, object]:
    """Get full task details from a regular or custom task ID."""
    query = {
        "custom_task_ids": str(custom_task_id).lower(),
        "team_id": workspace_id,
        "include_subtasks": "true",
    }
    return ClickUpClient().get(f"/v2/task/{task_id}", query).as_dict()


@mcp.tool()
def clickup_control_search_tasks(
    workspace_id: str,
    page: int = 0,
    include_closed: bool = False,
    subtasks: bool = True,
) -> dict[str, object]:
    """Retrieve Workspace tasks with pagination and closed/subtask controls."""
    query = {
        "page": page,
        "include_closed": str(include_closed).lower(),
        "subtasks": str(subtasks).lower(),
    }
    return ClickUpClient().get(f"/v2/team/{workspace_id}/task", query).as_dict()


@mcp.tool()
def clickup_control_create_task(
    list_id: str,
    name: str,
    body_json: str = "{}",
) -> dict[str, object]:
    """Create a task directly in the selected List."""
    path = normalize_api_path(f"/v2/list/{list_id}/task")
    body = _object(body_json)
    body["name"] = name
    return execute_mutation(
        ClickUpClient(),
        "POST",
        path,
        body=body,
    )


@mcp.tool()
def clickup_control_update_task(
    task_id: str,
    body_json: str,
    custom_task_id: bool = False,
    workspace_id: str | None = None,
) -> dict[str, object]:
    """Update a regular or custom task directly."""
    path = normalize_api_path(f"/v2/task/{task_id}")
    query = {
        "custom_task_ids": str(custom_task_id).lower(),
        "team_id": workspace_id,
    }
    return execute_mutation(
        ClickUpClient(),
        "PUT",
        path,
        query=query,
        body=_object(body_json),
    )


@mcp.tool()
def clickup_control_delete_task(
    task_id: str,
    custom_task_id: bool = False,
    workspace_id: str | None = None,
) -> dict[str, object]:
    """Delete a regular or custom task directly."""
    path = normalize_api_path(f"/v2/task/{task_id}")
    query = {
        "custom_task_ids": str(custom_task_id).lower(),
        "team_id": workspace_id,
    }
    return execute_mutation(
        ClickUpClient(),
        "DELETE",
        path,
        query=query,
    )


@mcp.tool()
def clickup_control_list_views(parent_type: str, parent_id: str) -> dict[str, object]:
    """List Views attached to a Workspace, Space, Folder, or List."""
    return list_views(ClickUpClient(), parent_type, parent_id)


@mcp.tool()
def clickup_control_get_view(view_id: str) -> dict[str, object]:
    """Get a View including grouping, sorting, filters, columns, and settings."""
    return get_view(ClickUpClient(), view_id)


@mcp.tool()
def clickup_control_create_view(
    parent_type: str,
    parent_id: str,
    name: str,
    view_type: str,
    config_json: str = "{}",
) -> dict[str, object]:
    """Create and verify a List, Board, Table, Calendar, Gantt, or other task View."""
    return create_view(
        ClickUpClient(),
        parent_type,
        parent_id,
        name,
        view_type,
        _object(config_json),
    )


@mcp.tool()
def clickup_control_configure_view(view_id: str, patch_json: str) -> dict[str, object]:
    """Merge grouping, sorting, filters, columns, or settings into a View and verify it."""
    return configure_view(ClickUpClient(), view_id, _object(patch_json))


@mcp.tool()
def clickup_control_delete_view(view_id: str) -> dict[str, object]:
    """Delete a task View and verify that it no longer exists."""
    return delete_view(ClickUpClient(), view_id)


@mcp.tool()
def clickup_control_get_view_tasks(view_id: str, page: int = 0) -> dict[str, object]:
    """Get the tasks currently visible through a View's saved filters and sorting."""
    return get_view_tasks(ClickUpClient(), view_id, page)


def main() -> None:
    mcp.run(transport="stdio")
