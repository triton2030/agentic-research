"""Recall wrapper forwards the caller's explicit run directory."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import codex_recall  # noqa: E402


class RecallRunDirTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = Path(self.enterContext(tempfile.TemporaryDirectory()))
        corpus = self.project / "_ops/chat-recall"
        corpus.mkdir(parents=True)
        (corpus / "quote.md").write_text("цитата", encoding="utf-8")
        self.argv = ["codex_recall.py", "вопрос", "--project", str(self.project)]

    def test_missing_run_dir_refuses_without_starting_child(self) -> None:
        err = io.StringIO()
        with mock.patch.object(sys, "argv", self.argv), mock.patch.object(
            codex_recall.subprocess, "run"
        ) as launch, contextlib.redirect_stderr(err):
            self.assertEqual(codex_recall.main(), 2)
        launch.assert_not_called()
        self.assertIn("Требуется --run-dir", err.getvalue())
        self.assertFalse((self.project / "_workspace").exists())

    def test_explicit_run_dir_is_forwarded_and_exit_code_preserved(self) -> None:
        run_dir = self.project / "_workspace/work-artifacts/2026-10-05-probe/agents/codex-artifacts/stamp-recall"
        with mock.patch.object(sys, "argv", self.argv + ["--run-dir", str(run_dir)]), mock.patch.object(
            codex_recall.subprocess, "run", return_value=mock.Mock(returncode=7)
        ) as launch:
            self.assertEqual(codex_recall.main(), 7)
        command = launch.call_args.args[0]
        self.assertEqual(command[command.index("--run-dir") + 1], str(run_dir))
        self.assertEqual(command[command.index("--project") + 1], str(self.project.resolve()))

    def test_print_prompt_needs_no_run_dir_and_starts_no_child(self) -> None:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", self.argv + ["--print-prompt"]), mock.patch.object(
            codex_recall.subprocess, "run"
        ) as launch, contextlib.redirect_stdout(out):
            self.assertEqual(codex_recall.main(), 0)
        launch.assert_not_called()
        self.assertIn("ВОПРОС: вопрос", out.getvalue())
        self.assertFalse((self.project / "_workspace").exists())
