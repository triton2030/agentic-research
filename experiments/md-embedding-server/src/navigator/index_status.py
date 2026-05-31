"""Status corpus-root resolution re-export.

The status state machine lives in `status_core`; the public entry point is
`navigator.api.status`. This module re-exports `find_corpus_root_for` for
callers that resolve a corpus root from an anchor path.
"""

from __future__ import annotations

from .status_core import find_corpus_root_for


__all__ = [
    "find_corpus_root_for",
]
