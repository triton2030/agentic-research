from __future__ import annotations

import hashlib
import json
import secrets
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

READ_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PREVIEW_DIR = PROJECT_ROOT / ".state" / "previews"
PREVIEW_TTL_SECONDS = 15 * 60


class ConfirmationRequiredError(ValueError):
    """Raised when a mutation lacks a valid transaction-scoped preview token."""


def _canonical_payload(
    method: str,
    path: str,
    query: Mapping[str, object] | None,
    body: object | None,
) -> str:
    return json.dumps(
        {
            "method": method.upper(),
            "path": path,
            "query": dict(query or {}),
            "body": body,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def mutation_digest(
    method: str,
    path: str,
    query: Mapping[str, object] | None,
    body: object | None,
) -> str:
    canonical = _canonical_payload(method, path, query, body)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MutationPreview:
    token: str
    method: str
    path: str
    query: Mapping[str, object]
    body: object | None
    digest: str
    expires_at: int
    before: object | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "preview_required": True,
            "confirmation_token": self.token,
            "method": self.method,
            "path": self.path,
            "query": dict(self.query),
            "body": self.body,
            "digest": self.digest,
            "expires_at": self.expires_at,
            "expires_at_iso": datetime.fromtimestamp(self.expires_at, UTC).isoformat(),
            "before": self.before,
        }


class PreviewStore:
    def __init__(self, root: Path = DEFAULT_PREVIEW_DIR, ttl_seconds: int = PREVIEW_TTL_SECONDS):
        self.root = root
        self.ttl_seconds = ttl_seconds

    def create(
        self,
        method: str,
        path: str,
        query: Mapping[str, object] | None,
        body: object | None,
        *,
        before: object | None = None,
    ) -> MutationPreview:
        normalized_method = method.upper()
        if normalized_method not in WRITE_METHODS:
            raise ValueError(f"Preview is only valid for mutations, got {normalized_method}")
        token = secrets.token_urlsafe(24)
        expires_at = int(time.time()) + self.ttl_seconds
        preview = MutationPreview(
            token=token,
            method=normalized_method,
            path=path,
            query=dict(query or {}),
            body=body,
            digest=mutation_digest(normalized_method, path, query, body),
            expires_at=expires_at,
            before=before,
        )
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        preview_path = self.root / f"{token}.json"
        preview_path.write_text(json.dumps(preview.as_dict()), encoding="utf-8")
        preview_path.chmod(0o600)
        return preview

    def consume(
        self,
        token: str,
        method: str,
        path: str,
        query: Mapping[str, object] | None,
        body: object | None,
    ) -> None:
        if not token or "/" in token or ".." in token:
            raise ConfirmationRequiredError("Mutation requires a valid preview token")
        preview_path = self.root / f"{token}.json"
        try:
            payload = json.loads(preview_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as error:
            raise ConfirmationRequiredError(
                "Preview token is missing, invalid, or already used"
            ) from error
        if int(payload.get("expires_at", 0)) < int(time.time()):
            preview_path.unlink(missing_ok=True)
            raise ConfirmationRequiredError("Preview token expired; create a new preview")
        expected = mutation_digest(method, path, query, body)
        if not secrets.compare_digest(str(payload.get("digest", "")), expected):
            raise ConfirmationRequiredError(
                "Preview token does not match this method/path/query/body"
            )
        preview_path.unlink()


def is_read_method(method: str) -> bool:
    normalized_method = method.upper()
    if normalized_method in READ_METHODS:
        return True
    if normalized_method not in WRITE_METHODS:
        raise ValueError(f"Unsupported HTTP method: {normalized_method}")
    return False
