from clickup_control.client import ApiResponse
from clickup_control.diagnostics import live_diagnostics, workspace_directory


class FakeClient:
    def get(self, path: str) -> ApiResponse:
        if path == "/v2/user":
            return ApiResponse(200, {"user": {"email": "must-not-leak@example.com"}}, {})
        return ApiResponse(200, {"teams": [{"id": "1"}, {"id": "2"}]}, {})


def test_live_diagnostics_reports_health_without_identity_payload() -> None:
    result = live_diagnostics(FakeClient())  # type: ignore[arg-type]
    assert result == {
        "authenticated": True,
        "user_status": 200,
        "workspace_status": 200,
        "workspace_count": 2,
    }


def test_workspace_directory_strips_member_profiles() -> None:
    result = workspace_directory(FakeClient())  # type: ignore[arg-type]
    assert result == {
        "status": 200,
        "workspaces": [{"id": "1", "name": None}, {"id": "2", "name": None}],
    }
