from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
SCRIPT = BACKEND / "codex_orchestrate.py"
sys.path.insert(0, str(BACKEND))

from codex_orchestrate_contract import (  # noqa: E402
    UsageError,
    path_allowed,
    worker_status_from_codex_status,
)
from codex_orchestrate_state import (  # noqa: E402
    capture_git_snapshot,
    compare_scope,
    prepare_run_dir,
)


def run_cli(
    project: Path,
    tasks: object,
    *args: str,
    dry_run: bool = True,
) -> subprocess.CompletedProcess[str]:
    run_dir = project / ".runs" / uuid.uuid4().hex
    command = [
        sys.executable,
        str(SCRIPT),
        "--project",
        str(project),
        "--run-dir",
        str(run_dir),
    ]
    if dry_run:
        command.append("--dry-run")
    command.extend(args)
    return subprocess.run(
        command,
        input=json.dumps(tasks),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(project: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class CodexOrchestrateCliTests(unittest.TestCase):
    def temp_project(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory()

    def write(self, root: Path, rel: str, text: str = "x\n") -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def init_repo(self, root: Path) -> None:
        git(root, "init")
        git(root, "config", "user.email", "test@example.com")
        git(root, "config", "user.name", "Test User")

    def test_valid_task_dry_run(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"id": "t1", "prompt": "touch a", "files": ["a.md"]}])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload["git"]["available"])
            self.assertEqual(payload["tasks"][0]["files"], ["a.md"])

    def test_overlapping_files_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "same.md")
            tasks = [
                {"id": "a", "prompt": "x", "files": ["same.md"]},
                {"id": "b", "prompt": "y", "files": ["same.md"]},
            ]
            proc = run_cli(root, tasks)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("overlap", proc.stderr)

    def test_files_required_and_list(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            cases = [
                [{"prompt": "x"}],
                [{"prompt": "x", "files": "a.md"}],
                [{"prompt": "x", "files": []}],
            ]
            for tasks in cases:
                with self.subTest(tasks=tasks):
                    proc = run_cli(root, tasks)
                    self.assertEqual(proc.returncode, 2)
                    self.assertIn("files", proc.stderr)

    def test_absolute_and_parent_paths_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            cases = [
                [{"prompt": "x", "files": ["/tmp/outside.md"]}],
                [{"prompt": "x", "files": ["../escape.md"]}],
            ]
            for tasks in cases:
                with self.subTest(tasks=tasks):
                    proc = run_cli(root, tasks)
                    self.assertEqual(proc.returncode, 2)

    def test_unknown_cwd_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"prompt": "x", "files": ["a.md"], "cwd": "/tmp"}])
            self.assertEqual(proc.returncode, 2)
            self.assertIn("unsupported keys", proc.stderr)

    def test_concurrency_zero_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"prompt": "x", "files": ["a.md"]}], "--concurrency", "0")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("concurrency", proc.stderr)

    def test_strict_optional_fields_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            cases = [
                ([{"prompt": "x", "files": ["a.md"], "allow_create": "false"}], "allow_create"),
                ([{"prompt": "x", "files": ["a.md"], "allow_create": 1}], "allow_create"),
                ([{"id": [], "prompt": "x", "files": ["a.md"]}], "id"),
            ]
            for tasks, needle in cases:
                with self.subTest(tasks=tasks):
                    proc = run_cli(root, tasks)
                    self.assertEqual(proc.returncode, 2)
                    self.assertIn(needle, proc.stderr)

    def test_dirty_overlap_rejected_and_non_overlap_allowed(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            self.write(root, "target.md", "clean\n")
            self.write(root, "other.md", "clean\n")
            git(root, "add", ".")
            git(root, "commit", "-m", "init")

            self.write(root, "target.md", "dirty\n")
            proc = run_cli(root, [{"prompt": "x", "files": ["target.md"]}])
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Dirty files overlap", proc.stderr)

            proc = run_cli(root, [{"prompt": "x", "files": ["other.md"]}])
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_allow_create_allows_missing_file(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            proc = run_cli(root, [{"prompt": "create", "files": ["new.md"], "allow_create": True}])
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_git_snapshot_required_rejects_non_git_project(self) -> None:
        with self.temp_project() as tmp:
            with self.assertRaises(UsageError):
                capture_git_snapshot(Path(tmp), required=True)

    def test_dirty_snapshot_detects_changed_non_overlap_dirty_file(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            self.write(root, "target.md", "clean\n")
            self.write(root, "other.md", "clean\n")
            git(root, "add", ".")
            git(root, "commit", "-m", "init")

            self.write(root, "other.md", "dirty-before\n")
            before = capture_git_snapshot(root, required=True)
            self.write(root, "other.md", "dirty-after\n")
            after = capture_git_snapshot(root, required=True)
            scope = compare_scope(before, after, {"target.md"})

            self.assertEqual(scope.out_of_scope_files, ("other.md",))
            self.assertFalse(scope.passed)

    def test_file_allowlist_is_exact_not_prefix(self) -> None:
        self.assertTrue(path_allowed("new.md", {"new.md"}))
        self.assertFalse(path_allowed("new.md/child.md", {"new.md"}))

    def test_dirty_paths_are_nul_safe_for_spaces_and_unicode(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            self.write(root, "space name.md", "clean\n")
            self.write(root, "тест.md", "clean\n")
            git(root, "add", ".")
            git(root, "commit", "-m", "init")

            self.write(root, "space name.md", "dirty\n")
            self.write(root, "тест.md", "dirty\n")
            snapshot = capture_git_snapshot(root, required=True)

            self.assertIn("space name.md", snapshot.dirty_files)
            self.assertIn("тест.md", snapshot.dirty_files)

    def test_worker_status_requires_exact_completed(self) -> None:
        self.assertEqual(worker_status_from_codex_status("completed", None), "completed")
        self.assertEqual(worker_status_from_codex_status("not_completed", None), "failed")
        self.assertEqual(worker_status_from_codex_status("partially_completed", None), "failed")

    def test_run_dir_must_be_fresh(self) -> None:
        with self.temp_project() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            with self.assertRaises(UsageError):
                prepare_run_dir(str(run_dir))


if __name__ == "__main__":
    unittest.main()
