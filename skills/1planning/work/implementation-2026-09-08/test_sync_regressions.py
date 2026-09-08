"""Regressions found by exercising the completed checker, beyond happy fixtures."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_check_plans import Fixture, check_plans


class SyncRegressions(unittest.TestCase):
    def test_null_launch_is_invalid_and_progress_evidence_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            original = fixture.epic.read_text()
            fixture.epic.write_text(original.replace('evidence: ""', 'evidence: "task evidence so far"'))
            self.assertTrue(check_plans.validate_root(fixture.root).ok)
            fixture.epic.write_text(original.replace('запуск: true', 'запуск: null'))
            report = check_plans.validate_root(fixture.root)
            self.assertFalse(report.ok)
            self.assertIn("'запуск' must be boolean", " ".join(issue.message for issue in report.issues))

    def test_alias_rewrite_failure_preserves_every_file(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            task = fixture.task.read_text().replace("порядок: 1", "порядок: &n 1")
            task = task.replace("подзадач: 3", "подзадач: *n")
            fixture.task.write_text(task)
            fixture.epic.write_text(fixture.epic.read_text().replace("задач: 1", "задач: 0"))
            before = {path: path.read_bytes() for path in (fixture.epic, fixture.task)}
            self.assertTrue(check_plans.validate_root(fixture.root, include_derived=False).ok)
            report, changed = check_plans.sync_root(fixture.root)
            self.assertFalse(report.ok)
            self.assertEqual(changed, 0)
            self.assertEqual(before, {path: path.read_bytes() for path in before})
            self.assertIn("cannot safely rewrite", " ".join(issue.message for issue in report.issues))

    def test_project_link_index_is_built_once_per_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            original = Path.rglob
            root_scans = []

            def counted(path, pattern, *args, **kwargs):
                if path.resolve() == fixture.root.resolve():
                    root_scans.append(path)
                return original(path, pattern, *args, **kwargs)

            with patch.object(Path, "rglob", counted):
                self.assertTrue(check_plans.validate_root(fixture.root).ok)
            self.assertEqual(len(root_scans), 1)


if __name__ == "__main__":
    unittest.main()
