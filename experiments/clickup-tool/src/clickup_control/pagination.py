from __future__ import annotations

from collections.abc import Mapping

from .client import ClickUpClient


def collect_task_pages(
    client: ClickUpClient,
    path: str,
    query: Mapping[str, object] | None = None,
    *,
    max_pages: int = 1000,
) -> dict[str, object]:
    """Collect every task page without trusting one pagination convention."""
    if max_pages < 1:
        raise ValueError("max_pages must be positive")

    tasks: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    pages_read = 0
    last_status = 200
    last_rate_limit: Mapping[str, str | None] = {}
    stop_reason = "max_pages"

    for page in range(max_pages):
        page_query = dict(query or {})
        page_query["page"] = page
        response = client.get(path, page_query)
        last_status = response.status
        last_rate_limit = response.rate_limit
        pages_read += 1

        data = response.data
        if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
            raise ValueError("ClickUp task page did not contain a tasks array")

        raw_tasks = data["tasks"]
        if not raw_tasks:
            stop_reason = "empty_page"
            break

        added = 0
        for task in raw_tasks:
            if not isinstance(task, dict):
                continue
            task_id = str(task.get("id", ""))
            if not task_id or task_id in seen_ids:
                continue
            seen_ids.add(task_id)
            tasks.append(task)
            added += 1

        if data.get("last_page") is True:
            stop_reason = "last_page"
            break
        if added == 0:
            stop_reason = "repeated_page"
            break

    return {
        "status": last_status,
        "data": {
            "tasks": tasks,
            "pages_read": pages_read,
            "stop_reason": stop_reason,
        },
        "rate_limit": dict(last_rate_limit),
    }
