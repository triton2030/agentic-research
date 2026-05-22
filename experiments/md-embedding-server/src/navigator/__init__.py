"""Public Python API for md-tools navigator capabilities."""

import importlib
import sys
import types
from collections.abc import Callable
from typing import Any

from .api import (
    audit,
    changed,
    check,
    corpus_scan,
    cycles,
    deps,
    extract,
    health,
    impact,
    importance,
    index,
    init,
    ls,
    overlaps,
    ping,
    preflight,
    profile_sections,
    query_by_type,
    read_related,
    refactor_candidates,
    repeated_concepts,
    scan,
    search,
    status,
    strip,
    toc,
)
from . import workflows

__all__ = [
    "audit",
    "changed",
    "check",
    "corpus_scan",
    "cycles",
    "deps",
    "extract",
    "health",
    "impact",
    "importance",
    "index",
    "init",
    "ls",
    "overlaps",
    "ping",
    "preflight",
    "profile_sections",
    "query_by_type",
    "read_related",
    "refactor_candidates",
    "repeated_concepts",
    "scan",
    "search",
    "status",
    "strip",
    "toc",
    "workflows",
]

_PUBLIC_API = {name: globals()[name] for name in __all__ if name != "workflows"}
_PUBLIC_PROXY_CACHE: dict[str, object] = {}


class _CallableModuleProxy:
    def __init__(self, func: Callable[..., Any], module: types.ModuleType) -> None:
        object.__setattr__(self, "_func", func)
        object.__setattr__(self, "_module", module)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._module, name, value)


class _NavigatorPackage(types.ModuleType):
    def __getattribute__(self, name: str):
        public = types.ModuleType.__getattribute__(self, "_PUBLIC_API")
        if name in public:
            cache = types.ModuleType.__getattribute__(self, "_PUBLIC_PROXY_CACHE")
            if name in cache:
                return cache[name]
            try:
                module = importlib.import_module(f"{__name__}.{name}")
            except ModuleNotFoundError:
                return public[name]
            proxy = _CallableModuleProxy(public[name], module)
            cache[name] = proxy
            return proxy
        return types.ModuleType.__getattribute__(self, name)


sys.modules[__name__].__class__ = _NavigatorPackage
