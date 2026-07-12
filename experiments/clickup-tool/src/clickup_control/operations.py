from __future__ import annotations

from collections.abc import Mapping

from .client import ClickUpClient


def execute_mutation(
    client: ClickUpClient,
    method: str,
    path: str,
    *,
    query: Mapping[str, object] | None = None,
    body: object | None = None,
) -> dict[str, object]:
    return client.request(method, path, query=query, body=body).as_dict()
