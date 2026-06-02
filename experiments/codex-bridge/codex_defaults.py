"""Shared Codex runtime defaults for bridge entrypoints.

Keep this module SDK-free so dry-run validation stays cheap and does not start
or import the Codex runtime.
"""
from __future__ import annotations

DEFAULT_CODEX_MODEL = "gpt-5.5"
DEFAULT_CODEX_EFFORT = "xhigh"

REASONING_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")

REVIEW_SANDBOX = "read_only"
REVIEW_APPROVAL_MODE = "deny_all"
WORKER_SANDBOX = "workspace_write"
WORKER_APPROVAL_MODE = "auto_review"

