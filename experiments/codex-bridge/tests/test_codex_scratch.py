"""Копия проекта для проверяющего: настоящий cp -c, без Codex и трат."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import codex_scratch  # noqa: E402


class ScratchCopyTests(unittest.TestCase):
    def test_copy_carries_uncommitted_and_ignored_files_and_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            project = root / "proj"
            (project / "node_modules").mkdir(parents=True)
            (project / "node_modules" / "dep.js").write_text("dep")
            (project / "draft.md").write_text("не закоммичено")
            with mock.patch.object(codex_scratch, "SCRATCH_HOME", root / "scratch"):
                workspace = codex_scratch.plan_scratch(project, "run1")
                codex_scratch.make_scratch_copy(workspace)
            copy = Path(workspace["cwd"])
            self.assertEqual(workspace["copy_status"], "copied")
            self.assertEqual((copy / "draft.md").read_text(), "не закоммичено")
            self.assertEqual((copy / "node_modules" / "dep.js").read_text(), "dep")
            (copy / "draft.md").write_text("правка в копии")
            self.assertEqual((project / "draft.md").read_text(), "не закоммичено")
            codex_scratch.remove_scratch_copy(workspace)
            self.assertEqual(workspace["cleanup_status"], "removed")
            self.assertFalse(copy.parent.exists())

    def test_failed_copy_leaves_nothing_and_says_so(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with mock.patch.object(codex_scratch, "SCRATCH_HOME", root / "scratch"):
                workspace = codex_scratch.plan_scratch(root / "нет-такого", "run1")
                with self.assertRaises(RuntimeError):
                    codex_scratch.make_scratch_copy(workspace)
            self.assertEqual(workspace["copy_status"], "failed")
            self.assertFalse((root / "scratch" / "run1").exists())


if __name__ == "__main__":
    unittest.main()
