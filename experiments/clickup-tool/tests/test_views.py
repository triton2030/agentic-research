from __future__ import annotations

from collections.abc import Mapping

import pytest

from clickup_control.client import ApiResponse, ClickUpApiError
from clickup_control.views import configure_view, create_view, delete_view


def _response(data: object, status: int = 200) -> ApiResponse:
    return ApiResponse(status, data, {})


class ViewClient:
    def __init__(self, responses: list[ApiResponse | Exception]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str, object, object]] = []

    def _next(self) -> ApiResponse:
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, object] | None = None,
        body: object | None = None,
    ) -> ApiResponse:
        self.calls.append((method, path, query, body))
        return self._next()

    def get(self, path: str, query: Mapping[str, object] | None = None) -> ApiResponse:
        return self.request("GET", path, query=query)


def _view(**overrides: object) -> dict[str, object]:
    view: dict[str, object] = {
        "id": "view-1",
        "name": "Board",
        "type": "board",
        "parent": {"id": "list-1", "type": 6},
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
        "settings": {"show_images": True, "card_size": 2, "colored_columns": False},
        "orderindex": 4,
    }
    view.update(overrides)
    return view


def test_configure_view_merges_full_put_and_preserves_live_settings() -> None:
    current = _view()
    verified = _view(
        sorting={
            "fields": [
                {"field": "priority", "dir": 1, "idx": 0, "determinor": "priority"}
            ]
        },
        settings={"show_images": False, "card_size": 2, "colored_columns": False},
    )
    client = ViewClient([_response(current), _response({"id": "view-1"}), _response(verified)])

    result = configure_view(
        client,  # type: ignore[arg-type]
        "view-1",
        {
            "sorting": {"fields": [{"field": "priority", "dir": 1, "idx": 0}]},
            "settings": {"show_images": False},
        },
    )

    put_body = client.calls[1][3]
    assert isinstance(put_body, dict)
    assert put_body["settings"] == {
        "show_images": False,
        "card_size": 2,
        "colored_columns": False,
    }
    assert "orderindex" not in put_body
    assert result["verified_updated"] is True


def test_create_view_uses_documented_defaults_and_verifies() -> None:
    client = ViewClient(
        [
            _response({"view": {"id": "view-2"}}),
            _response(_view(id="view-2", name="Analysis", type="table")),
        ]
    )

    result = create_view(
        client,  # type: ignore[arg-type]
        "list",
        "list-1",
        "Analysis",
        "table",
        {"sorting": {"fields": [{"field": "dueDate", "dir": 1}]}},
    )

    post_body = client.calls[0][3]
    assert isinstance(post_body, dict)
    assert post_body["name"] == "Analysis"
    assert post_body["type"] == "table"
    assert post_body["sorting"] == {
        "fields": [{"field": "dueDate", "dir": 1, "idx": 0}]
    }
    assert post_body["filters"] == {
        "op": "AND",
        "fields": [],
        "search": "",
        "show_closed": False,
    }
    assert result["verified_created"] is True


def test_delete_view_verifies_not_found() -> None:
    not_found = ClickUpApiError(404, {"err": "View not found"}, {})
    client = ViewClient([_response(_view()), _response(None), not_found])

    result = delete_view(client, "view-1")  # type: ignore[arg-type]

    assert result["verified_deleted"] is True


def test_configure_view_rejects_response_only_fields_before_http() -> None:
    client = ViewClient([])

    with pytest.raises(ValueError, match="orderindex"):
        configure_view(client, "view-1", {"orderindex": 10})  # type: ignore[arg-type]

    assert client.calls == []
