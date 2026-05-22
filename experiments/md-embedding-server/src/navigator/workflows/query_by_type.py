"""Thin re-export: real composition lives in navigator.api.query_by_type.

Surface kept here for navigator.workflows.* uniformity (5/5 workflow tools
resolvable through this submodule). Implementation stays in api.py because
it composes private helpers (open_profile_db + profile_unprofiled_sections +
profile_rows) tightly coupled to the section-profile module internals.

When a future caller actually needs `from navigator.workflows.query_by_type
import <helper>` — then move composition here. Until then, indirection cost
outweighs the abstraction value.
"""
from __future__ import annotations


def query_by_type(*args, **kwargs):
    from navigator.api import query_by_type as public_query_by_type

    return public_query_by_type(*args, **kwargs)
