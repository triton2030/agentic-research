from __future__ import annotations

from collections.abc import Mapping

from clickup_control.audit import audit_portfolio
from clickup_control.client import ApiResponse


class AuditClient:
    def __init__(self) -> None:
        self.view_page = 0
        self.task_page = 0

    def get(
        self,
        path: str,
        query: Mapping[str, object] | None = None,
    ) -> ApiResponse:
        if path == "/v2/list/list-1":
            return ApiResponse(
                200,
                {
                    "id": "list-1",
                    "name": "Portfolio",
                    "space": {"id": "space-1"},
                    "statuses": [{"status": "todo"}, {"status": "done"}],
                },
                {},
            )
        if path == "/v2/list/list-1/task":
            page = int((query or {}).get("page", 0))
            if page == 0:
                return ApiResponse(
                    200,
                    {
                        "tasks": [
                            {
                                "id": "p1",
                                "name": "Project",
                                "parent": None,
                                "custom_item_id": 1001,
                                "status": {"status": "todo"},
                                "checklists": [
                                    {
                                        "name": "Proof",
                                        "items": [
                                            {
                                                "id": "item-1",
                                                "name": "Readback",
                                                "resolved": False,
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                "id": "d1",
                                "name": "Decision",
                                "parent": "p1",
                                "custom_item_id": 1005,
                                "status": {"status": "done"},
                            },
                        ],
                        "last_page": True,
                    },
                    {},
                )
        if path == "/v2/list/list-1/view":
            return ApiResponse(
                200,
                {
                    "views": [
                        {
                            "id": "view-1",
                            "name": "Decisions",
                            "type": "list",
                            "filters": {"fields": []},
                        }
                    ]
                },
                {},
            )
        if path == "/v2/view/view-1/task":
            page = int((query or {}).get("page", 0))
            if page == 0:
                return ApiResponse(
                    200,
                    {
                        "tasks": [
                            {"id": "p1", "custom_item_id": 1001},
                            {"id": "d1", "custom_item_id": 1005},
                        ],
                        "last_page": True,
                    },
                    {},
                )
        if path == "/v2/team/workspace-1/goal":
            return ApiResponse(200, {"goals": []}, {})
        if path == "/v2/team/workspace-1/taskTemplate":
            return ApiResponse(200, {"templates": []}, {})
        if path == "/v3/workspaces/workspace-1/docs":
            return ApiResponse(200, {"docs": [{"id": "doc-1", "name": "Runbook", "type": 1}]}, {})
        if path == "/v2/list/list-1/field":
            return ApiResponse(200, {"fields": [{"name": "Department"}]}, {})
        if path == "/v2/team/workspace-1/custom_item":
            return ApiResponse(200, {"custom_items": [{"name": "Project", "id": 1001}]}, {})
        raise AssertionError(f"Unexpected GET {path} {query}")


def test_audit_portfolio_reports_persistence_and_expectation_mismatches() -> None:
    result = audit_portfolio(
        AuditClient(),  # type: ignore[arg-type]
        "workspace-1",
        "list-1",
        {
            "tasks": {"count": 2, "root_count": 1},
            "views": {
                "by_name": {
                    "Decisions": {
                        "saved_filter_count": 1,
                        "visible_task_count": 1,
                    }
                }
            },
        },
    )

    report = result["report"]  # type: ignore[assignment]
    assert report["tasks"]["dependency_edge_count"] == 0  # type: ignore[index]
    assert len(report["tasks"]["unresolved_checklists"]) == 1  # type: ignore[index]
    assert report["views"]["by_name"]["Decisions"]["visible_task_count"] == 2  # type: ignore[index]
    mismatches = result["expectation"]["mismatches"]  # type: ignore[index]
    assert [item["path"] for item in mismatches] == [
        "$.views.by_name.Decisions.saved_filter_count",
        "$.views.by_name.Decisions.visible_task_count",
    ]
