"""Tests for chat_capture.py: session files, env routing, inventory, dedup."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_capture.py"
SESSION_ENV_VARS = (
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_SESSION_ID",
    "CODEX_THREAD_ID",
    "CODEX_SESSION_ID",
)


class ChatCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = str(uuid.uuid4())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_capture(
        self, quote: str, type_: str, topic: str,
        agent: str | None = None,
        env: dict[str, str] | None = None,
        session: str | None = None,
        expect_ok: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        clean_env = {k: v for k, v in os.environ.items() if k not in SESSION_ENV_VARS}
        if env:
            clean_env.update(env)
        command = [
            sys.executable, str(SCRIPT),
            "--quote", quote, "--type", type_, "--topic", topic,
            "--project", str(self.root),
        ]
        if agent:
            command += ["--agent", agent]
        if session:
            command += ["--session", session]
        result = subprocess.run(command, capture_output=True, text=True, env=clean_env)
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def recall_files(self) -> list[Path]:
        return sorted((self.root / "_ops" / "chat-recall").glob("*.md"))

    def claude_env(self, session: str | None = None) -> dict[str, str]:
        return {"CLAUDE_CODE_SESSION_ID": session or self.session}

    def test_creates_session_file_with_frontmatter_and_entry(self) -> None:
        self.run_capture("Первое решение", "решение", "1codex", env=self.claude_env())
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
            text, r'\* \d\d:\d\d:\d\d — "Первое решение" — type: решение \| topic: 1codex'
        )

    def test_appends_to_same_file_and_extends_inventory(self) -> None:
        self.run_capture("Первое решение", "решение", "1codex", env=self.claude_env())
        self.run_capture("Про меня", "обо-мне", "мой-workflow", env=self.claude_env())
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        text = files[0].read_text(encoding="utf-8")
        front = text.split("---")[1]
        for item in ("  - решение", "  - обо-мне", "  - 1codex", "  - мой-workflow"):
            self.assertIn(item, front)
        self.assertEqual(text.count("* "), 2)

    def test_duplicate_quote_is_skipped(self) -> None:
        self.run_capture("Одна мысль", "идея", "1codex", env=self.claude_env())
        result = self.run_capture("Одна мысль", "идея", "1codex", env=self.claude_env())
        self.assertIn("already present", result.stdout)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertEqual(text.count('"Одна мысль"'), 1)

    def test_unknown_type_is_rejected(self) -> None:
        result = self.run_capture(
            "Что-то", "мысль", "1codex", env=self.claude_env(), expect_ok=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_unsafe_topic_is_rejected(self) -> None:
        result = self.run_capture(
            "Что-то", "решение", "foo: bar", env=self.claude_env(), expect_ok=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("plain handle", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_env_is_scoped_by_agent(self) -> None:
        codex_thread = str(uuid.uuid4())
        both = {**self.claude_env(), "CODEX_THREAD_ID": codex_thread}
        self.run_capture("Слова через Codex", "решение", "1codex", agent="codex", env=both)
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        self.assertIn(f"-codex-{codex_thread.split('-')[0]}", files[0].name)
        self.assertIn(f"session: {codex_thread}", files[0].read_text(encoding="utf-8"))

    def test_same_prefix_sessions_get_separate_files(self) -> None:
        session_a = "abcd1234-aaaa-4aaa-8aaa-111111111111"
        session_b = "abcd1234-bbbb-4bbb-8bbb-222222222222"
        self.run_capture("Первый разговор", "решение", "1codex", env=self.claude_env(session_a))
        self.run_capture("Второй разговор", "идея", "1codex", env=self.claude_env(session_b))
        files = self.recall_files()
        self.assertEqual(len(files), 2)
        texts = [f.read_text(encoding="utf-8") for f in files]
        joined = "\n".join(texts)
        self.assertIn(f"session: {session_a}", joined)
        self.assertIn(f"session: {session_b}", joined)
        for text in texts:
            if session_a in text:
                self.assertIn("Первый разговор", text)
                self.assertNotIn("Второй разговор", text)

    def test_missing_session_id_errors(self) -> None:
        result = self.run_capture("Без сессии", "решение", "1codex", expect_ok=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("session id unknown", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_invalid_explicit_session_is_rejected(self) -> None:
        result = self.run_capture(
            "Чужой путь",
            "решение",
            "1codex",
            session="../../../../../escape",
            expect_ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("session must be a canonical UUID", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_foreign_file_is_left_alone(self) -> None:
        self.run_capture("Первое", "решение", "1codex", env=self.claude_env())
        foreign = self.recall_files()[0]
        foreign.write_text("просто заметка без шапки\n", encoding="utf-8")
        self.run_capture("Второе", "решение", "1codex", env=self.claude_env())
        files = self.recall_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(
            foreign.read_text(encoding="utf-8"), "просто заметка без шапки\n"
        )


if __name__ == "__main__":
    unittest.main()
