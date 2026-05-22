"""Guard against dead module resurrection.

`src/md_cli/decorators.py` was removed in the 2026-05-22 cleanup pass:
- it contained a broken `from .transactions import INTENT_KEYS` import
  (INTENT_KEYS never existed there), and
- nothing in the codebase ever imported it. The mutating-tool transaction
  flow lives in `md_cli.handlers._generic`.

If someone re-creates a `md_cli.decorators` module without auditing the
transaction layer, this test catches the regression early.
"""
from __future__ import annotations

import importlib

import pytest


def test_decorators_module_removed() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("md_cli.decorators")
