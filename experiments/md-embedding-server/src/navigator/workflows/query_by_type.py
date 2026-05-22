from __future__ import annotations


def query_by_type(*args, **kwargs):
    from navigator.api import query_by_type as public_query_by_type

    return public_query_by_type(*args, **kwargs)
