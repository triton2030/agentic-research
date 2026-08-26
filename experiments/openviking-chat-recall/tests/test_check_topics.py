"""Falsifying checks for current-only topic provenance."""

from __future__ import annotations

import builtins
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "experiments/openviking-chat-recall/scripts/check_topics.py"
BUILDER = ROOT / "experiments/openviking-chat-recall/scripts/build_stage_tasks.py"
APPLIER = ROOT / "experiments/openviking-chat-recall/scripts/apply_stage.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD_MODULE = load_module("build_stage_tasks_under_test", BUILDER)
APPLY_MODULE = load_module("apply_stage_under_test", APPLIER)


class CheckTopicsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.base = self.root / "artifact"
        self.flat = self.base / "flat"
        self.topics = self.root / "topics"
        self.runs = self.root / "runs"
        self.source = "2026-01-01-alpha.md"
        for path in (self.flat, self.topics, self.runs):
            path.mkdir(parents=True)
        (self.flat / self.source).write_text(
            f"---\nsource: {self.source}\n---\n"
            "- Старое решение заменено. [L1]\n"
            "- Новое решение живёт. [L2]\n",
            encoding="utf-8",
        )
        (self.base / "topics.json").write_text(
            json.dumps({"topics": [{"id": "alpha", "files": [self.source]}]}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(self.base),
                str(self.topics),
                str(self.runs),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def run_apply(self, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(APPLIER),
                "merge",
                str(self.runs),
                str(self.flat),
                str(output),
                str(self.root / "raw"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def run_builder(self, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "merge",
                str(self.base / "topics.json"),
                str(self.flat),
                str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def write_pair(self, response: str, topic: str | None = None) -> None:
        body = topic or response.split("\n<!-- TOPIC_ANCHOR_ACCOUNTING", 1)[0]
        (self.topics / "alpha.md").write_text(body + "\n", encoding="utf-8")
        (self.runs / "alpha.json").write_text(
            json.dumps({"ok": True, "response": response}),
            encoding="utf-8",
        )

    def test_run_receipt_accounts_for_removed_anchor_without_topic_tombstone(self) -> None:
        body = (
            "---\ntopic: alpha\n---\n# alpha\n\n"
            f"- Новое решение живёт. [{self.source}#L2]\n"
            + " Дополнительный текущий контекст. " * 40
        )
        footer = (
            "\n<!-- TOPIC_ANCHOR_ACCOUNTING\n"
            + json.dumps(
                {
                    "superseded": [
                        {
                            "anchor": f"{self.source}#L1",
                            "by": f"{self.source}#L2",
                        }
                    ],
                    "unresolved": [],
                }
            )
            + "\n-->"
        )
        self.write_pair(body + footer)

        accepted = self.run_check()

        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        published = self.root / "published"
        applied = self.run_apply(published)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        published_body = (published / "alpha.md").read_text(encoding="utf-8")
        self.assertEqual(published_body.rstrip(), body.rstrip())
        self.assertNotIn("TOPIC_ANCHOR_ACCOUNTING", published_body)

        self.write_pair(body)
        rejected = self.run_check()

        self.assertEqual(rejected.returncode, 1)
        self.assertIn("учёт якорей не сходится", rejected.stdout)

    def test_apply_stage_refuses_missing_merge_input_without_topic_output(self) -> None:
        self.flat.joinpath(self.source).unlink()
        body = (
            "---\ntopic: alpha\n---\n# alpha\n\n"
            "- Новое решение живёт.\n"
            + " Контекст. " * 50
        )
        self.write_pair(body)
        output = self.root / "published"

        result = self.run_apply(output)

        self.assertEqual(result.returncode, 1)
        self.assertIn("входной материал отсутствует", result.stdout)
        self.assertFalse(output.exists())
        self.assertFalse((output / "alpha.md").exists())

    def test_builder_refuses_missing_merge_input_without_task_output(self) -> None:
        self.flat.joinpath(self.source).unlink()
        output = self.root / "stage-tasks"

        result = self.run_builder(output)

        self.assertEqual(result.returncode, 1)
        self.assertIn("входной материал отсутствует", result.stdout)
        self.assertFalse(output.exists())
        self.assertFalse((output / "alpha.txt").exists())

    def test_apply_stage_race_refuses_before_output_mkdir(self) -> None:
        output = self.root / "race-published"

        with patch.object(
            APPLY_MODULE,
            "read_flat",
            side_effect=FileNotFoundError(self.source),
        ):
            result = APPLY_MODULE.main(
                "merge",
                str(self.runs),
                str(self.flat),
                str(output),
                str(self.root / "raw"),
            )

        self.assertEqual(result, 1)
        self.assertFalse(output.exists())

    def test_builder_race_reads_before_output_mkdir(self) -> None:
        output = self.root / "race-tasks"
        original_open = builtins.open
        source_path = os.fspath(self.flat / self.source)

        def vanish_on_read(path, *args, **kwargs):
            if os.fspath(path) == source_path:
                raise FileNotFoundError(path)
            return original_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=vanish_on_read):
            result = BUILD_MODULE.main(
                "merge",
                str(self.base / "topics.json"),
                str(self.flat),
                str(output),
            )

        self.assertEqual(result, 1)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
