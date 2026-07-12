from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from .client import ClickUpClient
from .pagination import collect_task_pages
from .views import list_views


def _counter(values: list[object]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def _data_object(response: Mapping[str, object], label: str) -> dict[str, Any]:
    data = response.get("data")
    if not isinstance(data, dict):
        raise ValueError(f"{label} response did not contain a JSON object")
    return data


def _task_summary(tasks: list[dict[str, object]]) -> dict[str, object]:
    task_ids = {str(task.get("id")) for task in tasks if task.get("id") is not None}
    missing_parents: list[dict[str, object]] = []
    unresolved_checklists: list[dict[str, object]] = []
    dependency_edges: set[tuple[str, str]] = set()

    for task in tasks:
        task_id = str(task.get("id", ""))
        parent = task.get("parent")
        if parent is not None and str(parent) not in task_ids:
            missing_parents.append(
                {"task_id": task_id, "name": task.get("name"), "parent": str(parent)}
            )
        for dependency in task.get("dependencies") or []:
            if not isinstance(dependency, dict):
                continue
            dependent = dependency.get("task_id")
            depends_on = dependency.get("depends_on")
            if dependent is not None and depends_on is not None:
                dependency_edges.add((str(dependent), str(depends_on)))
        for checklist in task.get("checklists") or []:
            if not isinstance(checklist, dict):
                continue
            for item in checklist.get("items") or []:
                if isinstance(item, dict) and not item.get("resolved", False):
                    unresolved_checklists.append(
                        {
                            "task_id": task_id,
                            "task_name": task.get("name"),
                            "checklist": checklist.get("name"),
                            "item_id": item.get("id"),
                            "item": item.get("name"),
                        }
                    )

    return {
        "count": len(tasks),
        "root_count": sum(task.get("parent") is None for task in tasks),
        "status_counts": _counter(
            [
                status.get("status")
                for task in tasks
                if isinstance((status := task.get("status")), dict)
            ]
        ),
        "task_type_counts": _counter([task.get("custom_item_id", 0) for task in tasks]),
        "missing_parents": missing_parents,
        "dependency_edge_count": len(dependency_edges),
        "unresolved_checklists": unresolved_checklists,
    }


def _compare_expected(
    actual: object,
    expected: object,
    path: str = "$",
) -> list[dict[str, object]]:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            return [{"path": path, "expected": expected, "actual": actual}]
        mismatches: list[dict[str, object]] = []
        for key, value in expected.items():
            child_path = f"{path}.{key}"
            if key not in actual:
                mismatches.append({"path": child_path, "expected": value, "actual": None})
                continue
            mismatches.extend(_compare_expected(actual[key], value, child_path))
        return mismatches
    if actual != expected:
        return [{"path": path, "expected": expected, "actual": actual}]
    return []


def audit_portfolio(
    client: ClickUpClient,
    workspace_id: str,
    list_id: str,
    expected: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build a read-only, persistence-backed portfolio report."""
    list_response = client.get(f"/v2/list/{list_id}").as_dict()
    list_data = _data_object(list_response, "List")
    task_pages = collect_task_pages(
        client,
        f"/v2/list/{list_id}/task",
        {"include_closed": "true", "subtasks": "true"},
    )
    task_data = _data_object(task_pages, "Task pages")
    tasks = [task for task in task_data["tasks"] if isinstance(task, dict)]

    views_response = list_views(client, "list", list_id)
    views_data = _data_object(views_response, "Views")
    views = views_data.get("views", [])
    view_report: dict[str, object] = {}
    for view in views:
        if not isinstance(view, dict) or view.get("id") is None:
            continue
        view_tasks_response = collect_task_pages(
            client,
            f"/v2/view/{view['id']}/task",
        )
        visible_data = _data_object(view_tasks_response, "View tasks")
        visible_tasks = [
            task for task in visible_data["tasks"] if isinstance(task, dict)
        ]
        filters = view.get("filters") if isinstance(view.get("filters"), dict) else {}
        filter_fields = filters.get("fields") if isinstance(filters, dict) else []
        view_report[str(view.get("name"))] = {
            "id": str(view["id"]),
            "type": view.get("type"),
            "saved_filter_count": len(filter_fields) if isinstance(filter_fields, list) else 0,
            "saved_filters": filter_fields if isinstance(filter_fields, list) else [],
            "visible_task_count": len(visible_tasks),
            "visible_task_type_counts": _counter(
                [task.get("custom_item_id", 0) for task in visible_tasks]
            ),
            "pages_read": visible_data["pages_read"],
        }

    goals = client.get(f"/v2/team/{workspace_id}/goal").as_dict()
    goal_data = _data_object(goals, "Goals")
    templates = client.get(
        f"/v2/team/{workspace_id}/taskTemplate", {"page": 0}
    ).as_dict()
    template_data = _data_object(templates, "Task templates")
    docs = client.get(f"/v3/workspaces/{workspace_id}/docs").as_dict()
    doc_data = _data_object(docs, "Docs")
    fields = client.get(f"/v2/list/{list_id}/field").as_dict()
    field_data = _data_object(fields, "Custom Fields")
    task_types = client.get(f"/v2/team/{workspace_id}/custom_item").as_dict()
    task_type_data = _data_object(task_types, "Task types")

    statuses = list_data.get("statuses", [])
    report: dict[str, object] = {
        "target": {
            "workspace_id": workspace_id,
            "list_id": list_id,
            "list_name": list_data.get("name"),
            "space_id": (list_data.get("space") or {}).get("id")
            if isinstance(list_data.get("space"), dict)
            else None,
        },
        "tasks": {
            **_task_summary(tasks),
            "pages_read": task_data["pages_read"],
        },
        "views": {"count": len(view_report), "by_name": view_report},
        "statuses": {
            "count": len(statuses) if isinstance(statuses, list) else 0,
            "names": [status.get("status") for status in statuses if isinstance(status, dict)],
        },
        "custom_fields": {
            "count": len(field_data.get("fields", [])),
            "names": [
                field.get("name")
                for field in field_data.get("fields", [])
                if isinstance(field, dict)
            ],
        },
        "task_types": {
            "count": len(task_type_data.get("custom_items", [])),
            "by_name": {
                str(item.get("name")): item.get("id")
                for item in task_type_data.get("custom_items", [])
                if isinstance(item, dict)
            },
        },
        "goals": {"count": len(goal_data.get("goals", []))},
        "task_templates": {"count": len(template_data.get("templates", []))},
        "docs": {
            "count": len(doc_data.get("docs", [])),
            "by_name": {
                str(doc.get("name")): {
                    "id": doc.get("id"),
                    "type": doc.get("type"),
                    "parent": doc.get("parent"),
                }
                for doc in doc_data.get("docs", [])
                if isinstance(doc, dict)
            },
        },
    }
    mismatches = _compare_expected(report, expected or {})
    return {
        "status": 200,
        "report": report,
        "expectation": {
            "provided": expected is not None,
            "matched": not mismatches,
            "mismatches": mismatches,
        },
        "structural_ok": not report["tasks"]["missing_parents"],  # type: ignore[index]
    }
