from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass

from .auth import resolve_token

API_BASE_URL = "https://api.clickup.com/api"


class InvalidApiPathError(ValueError):
    """Raised when a path could escape the ClickUp API host."""


class ClickUpApiError(RuntimeError):
    def __init__(self, status: int, payload: object, rate_limit: Mapping[str, str | None]):
        super().__init__(f"ClickUp API returned HTTP {status}: {payload}")
        self.status = status
        self.payload = payload
        self.rate_limit = dict(rate_limit)


@dataclass(frozen=True)
class ApiResponse:
    status: int
    data: object
    rate_limit: Mapping[str, str | None]

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "data": self.data,
            "rate_limit": dict(self.rate_limit),
        }


def normalize_api_path(path: str) -> str:
    candidate = path.strip()
    if "://" in candidate or ".." in candidate.split("/"):
        raise InvalidApiPathError(
            "Use a relative ClickUp API path; hosts and traversal are forbidden"
        )
    if candidate.startswith("/api/"):
        candidate = candidate[4:]
    if not candidate.startswith("/"):
        candidate = f"/{candidate}"
    if not (candidate == "/v2" or candidate.startswith("/v2/") or candidate.startswith("/v3/")):
        raise InvalidApiPathError("ClickUp API path must begin with /v2/ or /v3/")
    return candidate


def _decode_payload(raw: bytes) -> object:
    if not raw:
        return None
    text = raw.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _rate_limit(headers: Mapping[str, str]) -> dict[str, str | None]:
    return {
        "limit": headers.get("X-RateLimit-Limit"),
        "remaining": headers.get("X-RateLimit-Remaining"),
        "reset": headers.get("X-RateLimit-Reset"),
    }


class ClickUpClient:
    def __init__(self, token: str | None = None, timeout: float = 30.0):
        self._token = token or resolve_token().value
        self._timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        query: Mapping[str, object] | None = None,
        body: object | None = None,
    ) -> ApiResponse:
        normalized_path = normalize_api_path(path)
        query_string = urllib.parse.urlencode(
            {key: value for key, value in (query or {}).items() if value is not None},
            doseq=True,
        )
        url = f"{API_BASE_URL}{normalized_path}"
        if query_string:
            url = f"{url}?{query_string}"
        encoded_body = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=encoded_body,
            method=method.upper(),
            headers={
                "Authorization": self._token,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "clickup-control/0.1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                headers = dict(response.headers.items())
                return ApiResponse(
                    status=response.status,
                    data=_decode_payload(response.read()),
                    rate_limit=_rate_limit(headers),
                )
        except urllib.error.HTTPError as error:
            headers = dict(error.headers.items()) if error.headers else {}
            raise ClickUpApiError(
                error.code,
                _decode_payload(error.read()),
                _rate_limit(headers),
            ) from error

    def get(self, path: str, query: Mapping[str, object] | None = None) -> ApiResponse:
        return self.request("GET", path, query=query)

    def workspace_tree(
        self,
        workspace_id: str,
        include_archived: bool = False,
    ) -> dict[str, object]:
        archived = str(include_archived).lower()
        spaces_response = self.get(f"/v2/team/{workspace_id}/space", {"archived": archived})
        spaces = (
            spaces_response.data.get("spaces", [])
            if isinstance(spaces_response.data, dict)
            else []
        )
        tree: list[dict[str, object]] = []
        for space in spaces:
            if not isinstance(space, dict) or "id" not in space:
                continue
            space_id = str(space["id"])
            folder_response = self.get(f"/v2/space/{space_id}/folder", {"archived": archived})
            list_response = self.get(f"/v2/space/{space_id}/list", {"archived": archived})
            folders = (
                folder_response.data.get("folders", [])
                if isinstance(folder_response.data, dict)
                else []
            )
            folder_nodes: list[dict[str, object]] = []
            for folder in folders:
                if not isinstance(folder, dict) or "id" not in folder:
                    continue
                lists_response = self.get(f"/v2/folder/{folder['id']}/list", {"archived": archived})
                folder_nodes.append(
                    {
                        "id": folder["id"],
                        "name": folder.get("name"),
                        "lists": lists_response.data.get("lists", [])
                        if isinstance(lists_response.data, dict)
                        else [],
                    }
                )
            tree.append(
                {
                    "id": space_id,
                    "name": space.get("name"),
                    "folders": folder_nodes,
                    "folderless_lists": list_response.data.get("lists", [])
                    if isinstance(list_response.data, dict)
                    else [],
                }
            )
        return {"workspace_id": workspace_id, "spaces": tree}
