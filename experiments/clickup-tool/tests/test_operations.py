from __future__ import annotations

from clickup_control import cli
from clickup_control.client import ApiResponse
from clickup_control.operations import execute_mutation


class RecordingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, object, object]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        query: object = None,
        body: object = None,
    ) -> ApiResponse:
        self.calls.append((method, path, query, body))
        return ApiResponse(200, {"ok": True}, {})


def test_mutation_executes_immediately_once() -> None:
    client = RecordingClient()

    result = execute_mutation(
        client,  # type: ignore[arg-type]
        "POST",
        "/v2/list/42/task",
        query={"custom": "yes"},
        body={"name": "Direct"},
    )

    assert result["status"] == 200
    assert client.calls == [
        ("POST", "/v2/list/42/task", {"custom": "yes"}, {"name": "Direct"})
    ]


def test_generic_cli_api_executes_requested_method(monkeypatch: object) -> None:
    client = RecordingClient()
    monkeypatch.setattr(cli, "ClickUpClient", lambda: client)  # type: ignore[attr-defined]
    parser = cli._build_parser()

    result = cli.run(
        parser.parse_args(
            [
                "api",
                "PATCH",
                "/v2/task/abc",
                "--query",
                '{"custom_task_ids": "false"}',
                "--body",
                '{"status": "done"}',
            ]
        )
    )

    assert result["status"] == 200  # type: ignore[index]
    assert client.calls == [
        (
            "PATCH",
            "/v2/task/abc",
            {"custom_task_ids": "false"},
            {"status": "done"},
        )
    ]


def test_generic_cli_api_accepts_top_level_json_array(monkeypatch: object) -> None:
    client = RecordingClient()
    monkeypatch.setattr(cli, "ClickUpClient", lambda: client)  # type: ignore[attr-defined]
    parser = cli._build_parser()

    cli.run(
        parser.parse_args(
            [
                "api",
                "PATCH",
                "/v3/workspaces/42/time_estimates_by_user",
                "--body",
                '[{"user_id": 7, "time_estimate": 3600000}]',
            ]
        )
    )

    assert client.calls[0][3] == [{"user_id": 7, "time_estimate": 3600000}]
