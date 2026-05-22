"""Thin re-export: real composition lives in navigator.api.refactor_candidates.

Surface kept here for navigator.workflows.* uniformity (5/5 workflow tools
resolvable through this submodule). Implementation stays in api.py because
it composes section profiles, originality scores, and owner-candidate ranking
through helpers tightly coupled to those modules' internals.

When a future caller actually needs `from navigator.workflows.refactor_candidates
import <helper>` — then move composition here. Until then, indirection cost
outweighs the abstraction value.
"""
from __future__ import annotations


def refactor_candidates(*args, **kwargs):
    from navigator.api import refactor_candidates as public_refactor_candidates

    return public_refactor_candidates(*args, **kwargs)
