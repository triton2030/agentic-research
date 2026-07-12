from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .client import ClickUpApiError, ClickUpClient

VIEW_PARENT_PATHS = {
    "workspace": "team",
    "team": "team",
    "everything": "team",
    "space": "space",
    "folder": "folder",
    "list": "list",
}

VIEW_TYPES = {
    "list",
    "board",
    "calendar",
    "table",
    "timeline",
    "workload",
    "activity",
    "map",
    "conversation",
    "gantt",
}

UPDATE_FIELDS = (
    "name",
    "type",
    "parent",
    "grouping",
    "divide",
    "sorting",
    "filters",
    "columns",
    "team_sidebar",
    "settings",
)

MUTABLE_FIELDS = {
    "name",
    "grouping",
    "divide",
    "sorting",
    "filters",
    "columns",
    "team_sidebar",
    "settings",
}


def _parent_path(parent_type: str, parent_id: str) -> str:
    normalized_type = parent_type.strip().lower()
    api_type = VIEW_PARENT_PATHS.get(normalized_type)
    if api_type is None:
        supported = ", ".join(sorted(VIEW_PARENT_PATHS))
        raise ValueError(f"Unsupported View parent type {parent_type!r}; use one of: {supported}")
    if not parent_id.strip():
        raise ValueError("View parent ID cannot be empty")
    return f"/v2/{api_type}/{parent_id}/view"


def _view_data(response: Mapping[str, object]) -> dict[str, Any]:
    data = response.get("data")
    if not isinstance(data, dict):
        raise ValueError("ClickUp View response did not contain a JSON object")
    nested_view = data.get("view")
    if isinstance(nested_view, dict):
        return nested_view
    return data


def _deep_merge(base: Mapping[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    merged = deepcopy(dict(base))
    for key, value in patch.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, Mapping):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _contains_patch(actual: object, expected: object) -> bool:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            return False
        return all(
            key in actual and _contains_patch(actual[key], value)
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            return False
        pairs = zip(actual, expected, strict=True)
        return all(
            _contains_patch(actual_item, expected_item)
            for actual_item, expected_item in pairs
        )
    return actual == expected


def _normalize_config(config: Mapping[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(dict(config))
    for block_name in ("sorting", "columns"):
        block = normalized.get(block_name)
        if not isinstance(block, dict) or not isinstance(block.get("fields"), list):
            continue
        fields: list[object] = []
        for index, field in enumerate(block["fields"]):
            if isinstance(field, Mapping):
                normalized_field = deepcopy(dict(field))
                normalized_field.setdefault("idx", index)
                fields.append(normalized_field)
            else:
                fields.append(field)
        block["fields"] = fields
    return normalized


def _validate_config_keys(config: Mapping[str, Any], allowed: set[str]) -> None:
    unsupported = sorted(set(config) - allowed)
    if unsupported:
        raise ValueError(f"Unsupported View configuration fields: {', '.join(unsupported)}")


def default_view_config() -> dict[str, object]:
    return {
        "grouping": {"field": "status", "dir": 1, "collapsed": [], "ignore": False},
        "divide": {"field": None, "dir": None, "collapsed": []},
        "sorting": {"fields": []},
        "filters": {"op": "AND", "fields": [], "search": "", "show_closed": False},
        "columns": {"fields": []},
        "team_sidebar": {
            "assignees": [],
            "assigned_comments": False,
            "unassigned_tasks": False,
        },
        "settings": {
            "show_task_locations": False,
            "show_subtasks": 3,
            "show_subtask_parent_names": False,
            "show_closed_subtasks": False,
            "show_assignees": True,
            "show_images": True,
            "collapse_empty_columns": None,
            "me_comments": True,
            "me_subtasks": True,
            "me_checklists": True,
        },
    }


def list_views(client: ClickUpClient, parent_type: str, parent_id: str) -> dict[str, object]:
    return client.get(_parent_path(parent_type, parent_id)).as_dict()


def get_view(client: ClickUpClient, view_id: str) -> dict[str, object]:
    return client.get(f"/v2/view/{view_id}").as_dict()


def create_view(
    client: ClickUpClient,
    parent_type: str,
    parent_id: str,
    name: str,
    view_type: str,
    config: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    normalized_type = view_type.strip().lower()
    if normalized_type not in VIEW_TYPES:
        supported = ", ".join(sorted(VIEW_TYPES))
        raise ValueError(f"Unsupported View type {view_type!r}; use one of: {supported}")
    provided_config = config or {}
    _validate_config_keys(provided_config, set(default_view_config()))
    normalized_config = _normalize_config(provided_config)
    body = _deep_merge(default_view_config(), normalized_config)
    body.update({"name": name, "type": normalized_type})
    created = client.request(
        "POST",
        _parent_path(parent_type, parent_id),
        body=body,
    ).as_dict()
    created_data = _view_data(created)
    view_id = created_data.get("id")
    verified = get_view(client, str(view_id)) if view_id else None
    verified_data = _view_data(verified) if verified else {}
    verified_parent = verified_data.get("parent")
    verified_parent_id = verified_parent.get("id") if isinstance(verified_parent, dict) else None
    verified_created = (
        verified_data.get("id") == view_id
        and verified_data.get("name") == name
        and verified_data.get("type") == normalized_type
        and str(verified_parent_id) == parent_id
    )
    if not verified_created:
        raise ValueError("Created View did not match its requested ID, name, type, and parent")
    return {
        "status": created["status"],
        "view": verified_data,
        "verified_created": True,
        "rate_limit": created["rate_limit"],
    }


def configure_view(
    client: ClickUpClient,
    view_id: str,
    patch: Mapping[str, Any],
) -> dict[str, object]:
    _validate_config_keys(patch, MUTABLE_FIELDS)
    normalized_patch = _normalize_config(patch)
    current = get_view(client, view_id)
    current_data = _view_data(current)
    merged = _deep_merge(current_data, normalized_patch)
    missing = [field for field in UPDATE_FIELDS if field not in merged]
    if missing:
        raise ValueError(f"View response is missing required update fields: {', '.join(missing)}")
    body = {field: merged[field] for field in UPDATE_FIELDS}
    updated = client.request("PUT", f"/v2/view/{view_id}", body=body).as_dict()
    verified = get_view(client, view_id)
    verified_updated = _contains_patch(_view_data(verified), normalized_patch)
    if not verified_updated:
        raise ValueError("ClickUp did not preserve the requested View configuration patch")
    return {
        "status": updated["status"],
        "applied_patch": normalized_patch,
        "view": _view_data(verified),
        "verified_updated": True,
        "rate_limit": updated["rate_limit"],
    }


def delete_view(client: ClickUpClient, view_id: str) -> dict[str, object]:
    target = get_view(client, view_id)
    deleted = client.request("DELETE", f"/v2/view/{view_id}").as_dict()
    try:
        remaining = get_view(client, view_id)
    except ClickUpApiError as error:
        if error.status == 404:
            target_data = _view_data(target)
            return {
                "status": deleted["status"],
                "deleted_view": {
                    "id": target_data.get("id"),
                    "name": target_data.get("name"),
                    "type": target_data.get("type"),
                },
                "verified_deleted": True,
                "rate_limit": deleted["rate_limit"],
            }
        raise
    raise ValueError(f"View {view_id} still exists after deletion: {remaining}")


def get_view_tasks(client: ClickUpClient, view_id: str, page: int = 0) -> dict[str, object]:
    if page < 0:
        raise ValueError("View task page cannot be negative")
    return client.get(f"/v2/view/{view_id}/task", {"page": page}).as_dict()
