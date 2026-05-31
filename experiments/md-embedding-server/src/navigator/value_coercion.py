from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def coerce_string_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, Mapping) or not isinstance(value, Iterable):
        raise TypeError("Expected a string or iterable of strings.")
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and "," in item:
            out.extend(part.strip() for part in item.split(",") if part.strip())
        elif item:
            out.append(str(item))
    return out
