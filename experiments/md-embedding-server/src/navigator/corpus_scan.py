from __future__ import annotations

from pathlib import Path


def corpus_scan(root: str | Path = ".") -> dict[str, object]:
    raise NotImplementedError("Corpus scan handler implemented in Phase 2")


def ping() -> dict[str, object]:
    return {"name": "md-tools", "version": "0.7.0"}
