"""Run-dir policy at the shared ledger boundary."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import codex_run_ledger  # noqa: E402
from cbcommon import UsageError  # noqa: E402


class RunDirTests(unittest.TestCase):
    def test_project_requires_explicit_run_dir_without_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            with self.assertRaisesRegex(UsageError, "Требуется --run-dir"):
                codex_run_ledger.prepare_run_dir(None, project=project)
            self.assertEqual(list(project.iterdir()), [])

    def test_no_project_keeps_backend_runs_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(codex_run_ledger, "BACKEND_DIR", Path(tmp)):
                run_id, run_dir = codex_run_ledger.prepare_run_dir(None)
            self.assertEqual(run_dir, Path(tmp) / "runs" / run_id)
            self.assertTrue(run_dir.is_dir())

    def test_explicit_work_run_dir_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            target = project / "_workspace/work-artifacts/2026-10-05-probe/agents/codex-artifacts/stamp-probe"
            _, run_dir = codex_run_ledger.prepare_run_dir(str(target), project=project)
            self.assertEqual(run_dir, target.resolve())
            self.assertTrue(run_dir.is_dir())
            self.assertFalse((project / "_workspace/codex-artifacts").exists())
