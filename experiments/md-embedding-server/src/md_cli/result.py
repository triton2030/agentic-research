from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    payload: dict[str, Any] | None
    exit_code: int = 0
    lock: dict[str, Any] | None = None

