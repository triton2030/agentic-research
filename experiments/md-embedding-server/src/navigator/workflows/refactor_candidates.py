from __future__ import annotations


def refactor_candidates(*args, **kwargs):
    from navigator.api import refactor_candidates as public_refactor_candidates

    return public_refactor_candidates(*args, **kwargs)
