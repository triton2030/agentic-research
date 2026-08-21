from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT.parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
SNAPSHOT_COMMIT = "6f98fcccdbf4b4de45ef787239ad101f70d106e2"

sys.path.insert(0, str(SCRIPT_DIR))
import freeze_corpus  # noqa: E402


class FreezeCorpusTests(unittest.TestCase):
    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and not path.is_symlink()
        }

    @staticmethod
    def _git(repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=repo, check=True, capture_output=True, text=True
        )
        return completed.stdout.strip()

    @classmethod
    def _make_repo(cls, root: Path, count: int = 184) -> tuple[Path, str]:
        repo = root / "repo"
        source = repo / "_ops/chat-recall"
        source.mkdir(parents=True)
        for index in range(count):
            (source / f"holder-{index:03d}.md").write_text(
                f"holder {index}\n", encoding="utf-8"
            )
        (source / "README.md").write_text("readme\n", encoding="utf-8")
        cls._git(repo, "init", "-q")
        cls._git(repo, "config", "user.email", "test@example.com")
        cls._git(repo, "config", "user.name", "Freeze tests")
        cls._git(repo, "add", "_ops/chat-recall")
        cls._git(repo, "commit", "-qm", "snapshot")
        return repo, cls._git(repo, "rev-parse", "HEAD")

    def test_snapshot_manifest_is_file_level_and_exact(self) -> None:
        manifest = freeze_corpus.build_manifest(REPO_ROOT, SNAPSHOT_COMMIT)
        self.assertEqual(manifest["count"], 184)
        self.assertEqual(len(manifest["files"]), 184)
        paths = [entry["path"] for entry in manifest["files"]]
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(paths[0], "2026-04-28-111714-claude-74356077.md")
        self.assertEqual(paths[-1], "2026-08-21-151338-codex-01a023cd.md")
        for entry in manifest["files"]:
            self.assertEqual(set(entry), {"path", "blob_oid", "sha256", "bytes"})
            self.assertIsInstance(entry["bytes"], int)
            self.assertRegex(entry["blob_oid"], r"^[0-9a-f]{40,64}$")
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
        serialized = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
        self.assertNotIn('"quote"', serialized)
        self.assertNotIn('"records"', serialized)

    def test_two_fresh_builds_are_byte_identical_and_preserve_unrelated_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            freeze_corpus.build(REPO_ROOT, SNAPSHOT_COMMIT, first)
            freeze_corpus.build(REPO_ROOT, SNAPSHOT_COMMIT, second)
            self.assertEqual(self._snapshot(first), self._snapshot(second))

            unrelated = first / "keep-unrelated.txt"
            unrelated.write_text("do not remove\n", encoding="utf-8")
            freeze_corpus.build(REPO_ROOT, SNAPSHOT_COMMIT, first)
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "do not remove\n")

            lock = json.loads((first / "source-lock.json").read_text(encoding="utf-8"))
            manifest_bytes = (first / "source-manifest.json").read_bytes()
            self.assertEqual(lock["corpus_commit"], SNAPSHOT_COMMIT)
            self.assertEqual(lock["holder_count"], 184)
            self.assertEqual(lock["source_root"], "_ops/chat-recall")
            self.assertEqual(lock["manifest_sha256"], hashlib.sha256(manifest_bytes).hexdigest())
            self.assertEqual(lock["owned_files"], ["source-manifest.json", "source-lock.json"])
            self.assertNotIn(str(REPO_ROOT), (first / "source-lock.json").read_text())

    def test_invalid_commit_forms_fail_closed(self) -> None:
        for value in ("HEAD", SNAPSHOT_COMMIT[:7], "0" * 40):
            with self.subTest(value=value):
                with self.assertRaises(freeze_corpus.FreezeError):
                    freeze_corpus.validate_commit(REPO_ROOT, value)

        manifest = freeze_corpus.build_manifest(REPO_ROOT, SNAPSHOT_COMMIT)
        blob_oid = manifest["files"][0]["blob_oid"]
        with self.assertRaisesRegex(freeze_corpus.FreezeError, "not a commit"):
            freeze_corpus.validate_commit(REPO_ROOT, blob_oid)

    def test_source_root_and_count_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, commit = self._make_repo(root, count=183)
            with self.assertRaisesRegex(freeze_corpus.FreezeError, "holder count drift"):
                freeze_corpus.build(repo, commit, root / "output")
            with self.assertRaises(freeze_corpus.FreezeError):
                freeze_corpus.build_manifest(REPO_ROOT, SNAPSHOT_COMMIT, "_ops/chat-recall/../chat-recall")

    def test_dirty_tree_and_path_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, commit = self._make_repo(root)
            dirty_holder = repo / "_ops/chat-recall/holder-000.md"
            dirty_holder.write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(freeze_corpus.FreezeError, "dirty"):
                freeze_corpus.build(repo, commit, root / "dirty-output")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, old_commit = self._make_repo(root)
            renamed = repo / "_ops/chat-recall/holder-000.md"
            renamed.rename(repo / "_ops/chat-recall/renamed-000.md")
            self._git(repo, "add", "_ops/chat-recall")
            self._git(repo, "commit", "-qm", "path drift")
            new_commit = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "checkout", "-q", old_commit)
            with self.assertRaisesRegex(freeze_corpus.FreezeError, "path drift"):
                freeze_corpus.build(repo, new_commit, root / "drift-output")

    def test_generated_root_symlink_escape_does_not_touch_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "output"
            outside = root / "outside.txt"
            output.mkdir()
            outside.write_text("must survive\n", encoding="utf-8")
            (output / "source-manifest.json").symlink_to(outside)
            with self.assertRaises(freeze_corpus.FreezeError):
                freeze_corpus.build(REPO_ROOT, SNAPSHOT_COMMIT, output)
            self.assertEqual(outside.read_text(encoding="utf-8"), "must survive\n")

    def test_generated_root_symlinked_parent_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "link" / "generated"
            outside = root / "outside"
            outside.mkdir()
            (root / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(freeze_corpus.FreezeError, "escaping symlink"):
                freeze_corpus.build(REPO_ROOT, SNAPSHOT_COMMIT, output)
            self.assertFalse((outside / "generated/source-manifest.json").exists())
            self.assertFalse((outside / "generated/source-lock.json").exists())

    def test_system_tmp_alias_is_environment_independent(self) -> None:
        if not Path("/tmp").is_symlink():
            self.skipTest("this regression requires the system /tmp alias")
        with tempfile.TemporaryDirectory(dir="/tmp", prefix="openviking-f1-root-") as temp_dir:
            output = Path(temp_dir) / "frozen"
            command = [
                sys.executable,
                str(SCRIPT_DIR / "freeze_corpus.py"),
                "--commit",
                SNAPSHOT_COMMIT,
                "--source-root",
                "_ops/chat-recall",
                "--output-dir",
                str(output),
                "--repo-root",
                str(REPO_ROOT),
            ]
            env_without_tmp_alias = os.environ.copy()
            env_without_tmp_alias["TMPDIR"] = str(REPO_ROOT)
            env_without_tmp_alias["PYTHONDONTWRITEBYTECODE"] = "1"
            first = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=env_without_tmp_alias,
                check=False,
                capture_output=True,
                text=True,
            )
            env_with_tmp_alias = env_without_tmp_alias.copy()
            env_with_tmp_alias["TMPDIR"] = "/tmp"
            second = subprocess.run(
                command,
                cwd=REPO_ROOT,
                env=env_with_tmp_alias,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)


if __name__ == "__main__":
    unittest.main()
