from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Iterable

from .value_coercion import coerce_string_list


def _list(value: Any) -> list[str]:
    return coerce_string_list(value)


def _ns(**kwargs: Any) -> SimpleNamespace:
    return SimpleNamespace(**kwargs)


def _default_paths(paths: Iterable[str] | str | None) -> list[str]:
    values = _list(paths)
    return values or ["."]


def _exit(payload: dict[str, Any], code: int) -> dict[str, Any]:
    result = dict(payload)
    result["_exit_code"] = code
    return result


def _clean_args(args: dict[str, Any]) -> dict[str, Any]:
    def should_drop(value: Any) -> bool:
        return (
            value is None
            or value is False
            or (isinstance(value, (list, tuple, set, dict)) and not value)
        )

    return {
        key: value
        for key, value in args.items()
        if not should_drop(value)
    }


def _read_next(tool: str, args: dict[str, Any], reason: str) -> dict[str, Any]:
    return {"tool": tool, "args": _clean_args(args), "reason": reason}


def _reject_unknown_kwargs(name: str, kwargs: dict[str, Any], allowed: set[str]) -> None:
    unknown = sorted(set(kwargs) - allowed)
    if unknown:
        joined = ", ".join(unknown)
        raise TypeError(f"{name} got unexpected keyword argument(s): {joined}")
