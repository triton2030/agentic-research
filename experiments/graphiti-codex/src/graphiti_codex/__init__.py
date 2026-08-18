"""Graphiti experiment backed by Codex and local storage."""

from __future__ import annotations

import os

# Graphiti reads this setting during import. The experiment never emits
# anonymous PostHog telemetry unless the owner deliberately overrides it.
os.environ.setdefault("GRAPHITI_TELEMETRY_ENABLED", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
