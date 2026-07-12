from __future__ import annotations

from collections.abc import Mapping

from .client import ClickUpClient
from .safety import PreviewStore


def mutate_with_preview(
    client: ClickUpClient,
    method: str,
    path: str,
    *,
    query: Mapping[str, object] | None = None,
    body: object | None = None,
    before: object | None = None,
    confirmation_token: str | None = None,
    preview_store: PreviewStore | None = None,
) -> dict[str, object]:
    store = preview_store or PreviewStore()
    if not confirmation_token:
        current = client.get(path, query).as_dict() if method.upper() == "DELETE" else before
        return store.create(method, path, query, body, before=current).as_dict()
    store.consume(confirmation_token, method, path, query, body)
    return client.request(method, path, query=query, body=body).as_dict()
