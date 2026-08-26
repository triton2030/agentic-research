"""Regression tests for projection manifest hygiene."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("sync_simple_projections.py")
SPEC = importlib.util.spec_from_file_location("sync_simple_projections", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import sync_simple_projections.py")
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class ProjectionManifestTests(unittest.TestCase):
    def test_generated_python_cache_is_not_package_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts" / "__pycache__").mkdir(parents=True)
            (root / "scripts" / "owner.py").write_text("owner\n", encoding="utf-8")
            (root / "scripts" / "__pycache__" / "owner.cpython-312.pyc").write_bytes(
                b"generated"
            )
            (root / "standalone.pyc").write_bytes(b"generated")

            self.assertEqual(set(SYNC.files_under(root)), {"scripts/owner.py"})


if __name__ == "__main__":
    unittest.main()
