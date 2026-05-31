"""Public Python API for md-tools navigator capabilities.

Dual nature of module-backed public names
------------------------------------------
Most public names (`check`, `cluster`, `status`, …) live only in
`navigator.api` and are re-exported here as plain callables. A handful
(`search`, `audit`, `index`, `overlaps`, `repeated_concepts`,
`importance`, `coherence_audit`, `corpus_scan`, `walk`) also have a
backing module on disk (`navigator/search.py`, …). For those, the public
name resolves to the **real module object**, made callable by delegating
`__call__` to the matching `navigator.api` function.

This keeps two contracts working at once:

- `navigator.search(corpus, query, …)` calls `api.search` (function form,
  used by handlers and most tests).
- `from navigator import search as search_mod` then
  `monkeypatch.setattr(search_mod, "rerank_documents", fake)` patches the
  symbol on the actual `navigator/search.py` module that the search code
  path reads (see `tests/test_rerank.py`, `tests/test_contract_fixes.py`,
  `tests/conftest.py`).

Because the public name *is* the on-disk module, module-attribute access,
monkeypatching, and introspection all behave like a normal module — no
proxy object stands in between. The only addition is a callable
`__class__` so the function form keeps working.
"""

from __future__ import annotations

import types
from typing import Any

from . import workflows
from .api import (
    audit,
    check,
    cluster,
    coherence_audit,
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
    read_related,
    repeated_concepts,
    scan,
    search,
    search_read,
    status,
    strip,
    toc,
    walk,
)

__all__ = [
    "audit",
    "check",
    "cluster",
    "coherence_audit",
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
    "read_related",
    "repeated_concepts",
    "scan",
    "search",
    "search_read",
    "status",
    "strip",
    "toc",
    "walk",
    "workflows",
]


class _CallableModule(types.ModuleType):
    """A real module that is also callable, delegating to a bound api func.

    Used for public names that have a backing `navigator/<name>.py` module
    so that `from navigator import <name>` yields the module on disk
    (module attributes, monkeypatching) while `navigator.<name>(...)` still
    calls the corresponding `navigator.api.<name>` function."""

    _api_func: Any

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return type(self)._api_func(*args, **kwargs)


def _bind_callable_module(name: str, api_func: Any) -> None:
    """Make `navigator/<name>.py` callable and bind it as the public name.

    Leaves the real module object in place — only swaps its class to a
    callable subclass carrying the api delegate. Function-only public names
    (no backing module) keep the plain `from .api import <name>` binding."""
    from importlib import import_module

    module = import_module(f"{__name__}.{name}")
    callable_cls = type(
        f"_Callable_{name}",
        (_CallableModule,),
        {"_api_func": staticmethod(api_func)},
    )
    module.__class__ = callable_cls
    globals()[name] = module


# Public names that ALSO have a backing module on disk. They must stay
# callable (function form) yet resolve to the real module (attribute access
# / monkeypatch). The remaining public names live only in `navigator.api`
# and are already bound as plain callables by the import above.
for _name, _func in (
    ("audit", audit),
    ("coherence_audit", coherence_audit),
    ("corpus_scan", corpus_scan),
    ("importance", importance),
    ("index", index),
    ("overlaps", overlaps),
    ("repeated_concepts", repeated_concepts),
    ("search", search),
    ("walk", walk),
):
    _bind_callable_module(_name, _func)

del _name, _func
