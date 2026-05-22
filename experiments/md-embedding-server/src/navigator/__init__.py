"""Public Python API for md-tools navigator capabilities.

Proxy notice
------------
`_CallableModuleProxy` + `_NavigatorPackage` give every public name dual nature:
`navigator.search(...)` calls `api.search` (function), while `navigator.search.X`
routes to attributes of the `navigator/search.py` module (e.g. mocks, constants,
private helpers).

This is load-bearing — see ``tests/test_rerank.py``:
``monkeypatch.setattr(search_mod, "rerank_documents", fake)`` requires module
attribute access to install the monkeypatch. Removing the proxy would break
those fixtures and any downstream callers doing
``from navigator import X as mod; mod.helper(...)``.

Known limits / when safe to remove:
- mypy, pickling, and `inspect.getmembers` may behave unexpectedly on the
  proxy objects.
- Removal becomes safe once all callers move to explicit
  ``from navigator.api import X`` for callable form and
  ``from navigator import X`` for module-attribute access. Until then, keep.

See ``docs/navigator-public-api.md`` (Proxy magic section) for the full
rationale.
"""

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
