"""Tests for chat_capture.py: session files, inventory upkeep, dedup."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_capture.py"
SESSION_ENV_VARS = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID", "CODEX_THREAD_ID", "CODEX_SESSION_ID")


class ChatCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = str(uuid.uuid4())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_capture(
        self, quote: str, type_: str, topic: str,
        session: str | None = None, expect_ok: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if k not in SESSION_ENV_VARS}
        if session:
            env["CLAUDE_CODE_SESSION_ID"] = session
        result = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--quote", quote, "--type", type_, "--topic", topic,
                "--project", str(self.root),
            ],
            capture_output=True, text=True, env=env,
        )
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def recall_files(self) -> list[Path]:
        return sorted((self.root / "_ops" / "chat-recall").glob("*.md"))

    def test_creates_session_file_with_frontmatter_and_entry(self) -> None:
        self.run_capture("Первое решение", "решение", "1codex", session=self.session)
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        short = self.session.split("-")[0]
        self.assertRegex(
            files[0].name,
            rf"^\d{{4}}-\d{{2}}-\d{{2}}-\d{{6}}-claude-{short}\.md$",
        )
        text = files[0].read_text(encoding="utf-8")
        self.assertIn(f"session: {self.session}", text)
        self.assertIn("  - решение", text)
        self.assertIn("  - 1codex", text)
        self.assertRegex(
            text, r'\* \d\d:\d\d:\d\d — "Первое решение" — тип: решение \| тема: 1codex'
        )

    def test_appends_to_same_file_and_extends_inventory(self) -> None:
        self.run_capture("Первое решение", "решение", "1codex", session=self.session)
        self.run_capture("Про меня", "обо-мне", "мой-workflow", session=self.session)
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        text = files[0].read_text(encoding="utf-8")
        front = text.split("---")[1]
        for item in ("  - решение", "  - обо-мне", "  - 1codex", "  - мой-workflow"):
            self.assertIn(item, front)
        self.assertEqual(text.count("* "), 2)

    def test_duplicate_quote_is_skipped(self) -> None:
        self.run_capture("Одна мысль", "идея", "1codex", session=self.session)
        result = self.run_capture("Одна мысль", "идея", "1codex", session=self.session)
        self.assertIn("already present", result.stdout)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertEqual(text.count('"Одна мысль"'), 1)

    def test_unknown_type_is_rejected(self) -> None:
        result = self.run_capture(
            "Что-то", "мысль", "1codex", session=self.session, expect_ok=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_refuses_foreign_file_without_frontmatter(self) -> None:
        self.run_capture("Первое", "решение", "1codex", session=self.session)
        target = self.recall_files()[0]
        target.write_text("просто заметка без шапки\n", encoding="utf-8")
        result = self.run_capture(
            "Второе", "решение", "1codex", session=self.session, expect_ok=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("no frontmatter", result.stderr)
        self.assertEqual(
            target.read_text(encoding="utf-8"), "просто заметка без шапки\n"
        )

    def test_without_session_uses_one_day_file_per_agent(self) -> None:
        self.run_capture("Первое", "решение", "1codex")
        self.run_capture("Второе", "идея", "1codex")
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].name.endswith("-claude-nosession.md"))
        self.assertNotIn("session:", files[0].read_text(encoding="utf-8").split("---")[1])


if __name__ == "__main__":
    unittest.main()
