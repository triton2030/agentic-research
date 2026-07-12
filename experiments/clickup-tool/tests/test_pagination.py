from __future__ import annotations

from collections.abc import Mapping

from clickup_control.client import ApiResponse
from clickup_control.pagination import collect_task_pages


class PagingClient:
    def __init__(self, pages: list[object]) -> None:
        self.pages = pages
        self.calls: list[tuple[str, Mapping[str, object] | None]] = []

    def get(
        self,
        path: str,
        query: Mapping[str, object] | None = None,
    ) -> ApiResponse:
        self.calls.append((path, query))
        return ApiResponse(200, self.pages.pop(0), {})


def test_collect_task_pages_reads_until_empty_and_deduplicates() -> None:
    client = PagingClient(
        [
            {"tasks": [{"id": "1"}, {"id": "2"}]},
            {"tasks": [{"id": "2"}, {"id": "3"}]},
            {"tasks": []},
        ]
    )

    result = collect_task_pages(
        client,  # type: ignore[arg-type]
        "/v2/view/view-1/task",
        {"include_closed": "true"},
    )

    assert [task["id"] for task in result["data"]["tasks"]] == ["1", "2", "3"]  # type: ignore[index]
    assert result["data"]["pages_read"] == 3  # type: ignore[index]
    assert result["data"]["stop_reason"] == "empty_page"  # type: ignore[index]
    assert client.calls[1][1] == {"include_closed": "true", "page": 1}


def test_collect_task_pages_honors_last_page() -> None:
    client = PagingClient([{"tasks": [{"id": "1"}], "last_page": True}])

    result = collect_task_pages(client, "/v2/team/42/task")  # type: ignore[arg-type]

    assert result["data"]["pages_read"] == 1  # type: ignore[index]
    assert result["data"]["stop_reason"] == "last_page"  # type: ignore[index]
