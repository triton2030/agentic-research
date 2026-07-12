from __future__ import annotations

from .client import ClickUpClient


def live_diagnostics(client: ClickUpClient) -> dict[str, object]:
    user_response = client.get("/v2/user")
    workspace_response = client.get("/v2/team")
    teams = (
        workspace_response.data.get("teams", [])
        if isinstance(workspace_response.data, dict)
        else []
    )
    return {
        "authenticated": user_response.status == 200,
        "user_status": user_response.status,
        "workspace_status": workspace_response.status,
        "workspace_count": len(teams),
    }


def workspace_directory(client: ClickUpClient) -> dict[str, object]:
    response = client.get("/v2/team")
    teams = response.data.get("teams", []) if isinstance(response.data, dict) else []
    workspaces = [
        {"id": team.get("id"), "name": team.get("name")}
        for team in teams
        if isinstance(team, dict)
    ]
    return {"status": response.status, "workspaces": workspaces}
