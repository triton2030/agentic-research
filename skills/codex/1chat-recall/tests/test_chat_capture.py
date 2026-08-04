"""Tests for chat_capture.py: session files, env routing, inventory, dedup."""

from __future__ import annotations

import importlib.util
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_capture.py"
SKILL = SCRIPT.parents[1] / "SKILL.md"
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
DEFAULT_SOURCE_TIMESTAMP = "2001-02-03T04:05:06.789Z"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "chat_capture_under_test",
    SCRIPT,
)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError("cannot load chat_capture.py for failure-mode tests")
CHAT_CAPTURE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(CHAT_CAPTURE)
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
        kind: str | None = None,
        context_note: str | None = None,
        session: str | None = None,
        source_timestamp: str | None = DEFAULT_SOURCE_TIMESTAMP,
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
        if source_timestamp is not None:
            command += ["--source-timestamp", source_timestamp]
        if agent:
            command += ["--agent", agent]
        if kind:
            command += ["--kind", kind]
        if context_note:
            command += ["--context-note", context_note]
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
        self.run_capture(
            "Первое решение",
            "решение",
            "агенты-и-ии",
            env=self.claude_env(),
        )
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        short = self.session.split("-")[0]
        local_when = datetime.fromisoformat(DEFAULT_SOURCE_TIMESTAMP).astimezone()
        self.assertEqual(
            files[0].name,
            f"{local_when:%Y-%m-%d-%H%M%S}-claude-{short}.md",
        )
        text = files[0].read_text(encoding="utf-8")
        self.assertIn(f"date: {local_when:%Y-%m-%d}", text)
        self.assertIn(f"session: {self.session}", text)
        self.assertIn("  - решение", text)
        self.assertIn("  - агенты-и-ии", text)
        self.assertIn(
            '* 2001-02-03T04:05:06.789000+00:00 — "Первое решение" '
            "— type: решение | topic: агенты-и-ии",
            text,
        )

    def test_context_note_is_inline_metadata(self) -> None:
        self.run_capture(
            "Цитата сама остаётся полезной единицей знания",
            "критерий",
            "документация-и-знания",
            env=self.claude_env(),
            context_note="Речь о критерии записи в chat recall.",
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn(
            "topic: документация-и-знания | "
            "context-note: Речь о критерии записи в chat recall.",
            text,
        )

    def test_context_note_rejects_links_delimiters_and_note_on_note(self) -> None:
        cases = (
            ("Ссылка", "https://example.com", None, "not a link"),
            ("Разделитель", "Контекст | продолжение", None, "delimiter"),
            ("Заметка", "Контекст заметки", "note", "cannot be attached"),
        )
        for quote, context, kind, error in cases:
            with self.subTest(quote=quote):
                result = self.run_capture(
                    quote,
                    "факт",
                    "документация-и-знания",
                    env=self.claude_env(),
                    kind=kind,
                    context_note=context,
                    expect_ok=False,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(error, result.stderr)

    def test_appends_to_same_file_and_extends_inventory(self) -> None:
        self.run_capture(
            "Первое решение",
            "решение",
            "агенты-и-ии",
            env=self.claude_env(),
        )
        self.run_capture(
            "Про меня",
            "обо-мне",
            "обо-мне-и-предпочтения",
            env=self.claude_env(),
        )
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        text = files[0].read_text(encoding="utf-8")
        front = text.split("---")[1]
        for item in (
            "  - решение",
            "  - обо-мне",
            "  - агенты-и-ии",
            "  - обо-мне-и-предпочтения",
        ):
            self.assertIn(item, front)
        self.assertEqual(text.count("* "), 2)

    def test_duplicate_quote_is_skipped(self) -> None:
        self.run_capture(
            "Одна мысль",
            "идея",
            "агенты-и-ии",
            env=self.claude_env(),
        )
        result = self.run_capture(
            "Одна мысль",
            "идея",
            "агенты-и-ии",
            env=self.claude_env(),
        )
        self.assertIn("already present", result.stdout)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertEqual(text.count('"Одна мысль"'), 1)

    def test_earlier_source_quote_redates_the_single_session_file(self) -> None:
        later = "2010-06-15T12:00:00+00:00"
        earlier = "1999-01-02T03:04:05+00:00"
        self.run_capture(
            "Поздняя мысль",
            "идея",
            "агенты-и-ии",
            env=self.claude_env(),
            source_timestamp=later,
        )
        self.run_capture(
            "Более ранняя мысль",
            "решение",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp=earlier,
        )

        files = self.recall_files()
        self.assertEqual(len(files), 1)
        local_earlier = datetime.fromisoformat(earlier).astimezone()
        self.assertTrue(
            files[0].name.startswith(f"{local_earlier:%Y-%m-%d-%H%M%S}-")
        )
        text = files[0].read_text(encoding="utf-8")
        self.assertIn(f"date: {local_earlier:%Y-%m-%d}", text)
        self.assertIn(f"# Chat recall — {local_earlier:%Y-%m-%d} —", text)
        self.assertIn("2010-06-15T12:00:00+00:00", text)
        self.assertIn("1999-01-02T03:04:05+00:00", text)

    def test_legacy_entry_is_preserved_when_appending_repaired_record(self) -> None:
        self.run_capture(
            "Legacy quote",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
        )
        legacy_path = self.recall_files()[0]
        legacy_text = re.sub(
            r'^\* \S+ — "',
            '* 04:05:06 — "',
            legacy_path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
        legacy_path.write_text(legacy_text, encoding="utf-8")

        result = self.run_capture(
            "New quote",
            "идея",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp="1999-01-02T03:04:05Z",
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(self.recall_files()), 1)
        repaired = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn('* 04:05:06 — "Legacy quote"', repaired)
        self.assertIn('"New quote"', repaired)

    def test_failed_atomic_rewrite_leaves_original_file_unchanged(self) -> None:
        later = "2010-06-15T12:00:00Z"
        earlier = "1999-01-02T03:04:05Z"
        self.run_capture(
            "Existing quote",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp=later,
        )
        old_path = self.recall_files()[0]

        with mock.patch.object(
            CHAT_CAPTURE,
            "write_atomic",
            side_effect=OSError("simulated rewrite failure"),
        ):
            with self.assertRaisesRegex(OSError, "simulated rewrite failure"):
                CHAT_CAPTURE.append_entry(
                    old_path,
                    "claude",
                    self.session,
                    "идея",
                    "документация-и-знания",
                    "Earlier quote",
                    CHAT_CAPTURE.source_timestamp(earlier),
                )

        files_after_failure = self.recall_files()
        self.assertEqual(files_after_failure, [old_path])
        self.assertIn(
            "Existing quote",
            files_after_failure[0].read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "Earlier quote",
            files_after_failure[0].read_text(encoding="utf-8"),
        )

        self.run_capture(
            "Earlier quote",
            "идея",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp=earlier,
        )
        self.assertEqual(len(self.recall_files()), 1)
        recovered = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn("Existing quote", recovered)
        self.assertIn("Earlier quote", recovered)

    def test_timestamp_requires_value_and_approximate_source(self) -> None:
        missing = self.run_capture(
            "Без даты",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp=None,
            expect_ok=False,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("--source-timestamp", missing.stderr)

        naive = self.run_capture(
            "Неоднозначная дата",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp="2001-02-03T04:05:06",
            expect_ok=False,
        )
        self.assertEqual(naive.returncode, 2)
        self.assertIn("--timestamp-source", naive.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_derived_sources_cannot_claim_exact_precision(self) -> None:
        env = {key: value for key, value in os.environ.items() if key not in SESSION_ENV_VARS}
        env.update(self.claude_env())
        base = [
            sys.executable,
            str(SCRIPT),
            "--quote",
            "Наблюдаемая реплика",
            "--type",
            "факт",
            "--topic",
            "документация-и-знания",
            "--source-timestamp",
            DEFAULT_SOURCE_TIMESTAMP,
            "--timestamp-source",
            "turn-context",
            "--project",
            str(self.root),
        ]
        rejected = subprocess.run(base, capture_output=True, text=True, env=env)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("cannot be source-exact", rejected.stderr)
        accepted = subprocess.run(
            [*base, "--timestamp-precision", "minute"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn(
            "source: turn-context | precision: minute",
            self.recall_files()[0].read_text(encoding="utf-8"),
        )
        for derived in ("filename", "frontmatter", "raw-time", "unknown"):
            candidate = subprocess.run(
                [
                    *base,
                    "--quote",
                    f"Источник {derived}",
                    "--timestamp-source",
                    derived,
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(candidate.returncode, 2)
            self.assertIn("cannot be source-exact", candidate.stderr)

    def test_date_only_unknown_and_selection_are_marked_inline(self) -> None:
        clean_env = self.claude_env()
        command = [
            sys.executable,
            str(SCRIPT),
            "--quote",
            "Выбрал локальный путь",
            "--type",
            "решение",
            "--topic",
            "документация-и-знания",
            "--kind",
            "selection",
            "--source-timestamp",
            "2001-02-03",
            "--timestamp-source",
            "repaired",
            "--timestamp-precision",
            "date",
            "--source-ref",
            "session.jsonl",
            "--project",
            str(self.root),
        ]
        env = {key: value for key, value in os.environ.items() if key not in SESSION_ENV_VARS}
        env.update(clean_env)
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn("kind: selection", text)
        self.assertIn("source: repaired | precision: date", text)
        self.assertIn("source-ref: session.jsonl", text)

        unknown = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--quote",
                "Дата источника не восстановлена",
                "--type",
                "неопределено",
                "--topic",
                "без-темы",
                "--kind",
                "note",
                "--source-timestamp",
                "unknown",
                "--timestamp-source",
                "unknown",
                "--timestamp-precision",
                "unknown",
                "--project",
                str(self.root),
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(unknown.returncode, 0, unknown.stderr)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn(
            '* unknown — "Дата источника не восстановлена" '
            "— kind: note | type: неопределено | topic: без-темы "
            "| source: unknown | precision: unknown",
            text,
        )

    def test_unknown_type_is_rejected(self) -> None:
        result = self.run_capture(
            "Что-то",
            "мысль",
            "агенты-и-ии",
            env=self.claude_env(),
            expect_ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("type is outside the controlled vocabulary", result.stderr)

    def test_unknown_and_unsafe_topics_are_rejected(self) -> None:
        unknown = self.run_capture(
            "Что-то",
            "решение",
            "mockup-zone-editor",
            env=self.claude_env(),
            expect_ok=False,
        )
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("topic is outside the controlled vocabulary", unknown.stderr)

        result = self.run_capture(
            "Что-то", "решение", "foo: bar", env=self.claude_env(), expect_ok=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("plain handle", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_metadata_vocabulary_is_listed_without_capture_arguments(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-metadata"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Types:\n  решение:", result.stdout)
        self.assertIn("Topics:\n  цели-и-приоритеты:", result.stdout)
        self.assertIn("  обо-мне-и-предпочтения:", result.stdout)
        self.assertIn("repair-only sentinel", result.stdout)

    def test_skill_documents_twenty_russian_global_topics(self) -> None:
        topics = CHAT_CAPTURE.TOPIC_DESCRIPTIONS
        self.assertEqual(len(topics), 20)
        for topic in topics:
            self.assertRegex(topic, r"^[а-яё]+(?:-[а-яё]+)*$")

        skill_text = SKILL.read_text(encoding="utf-8")
        for value in (
            *CHAT_CAPTURE.TYPE_DESCRIPTIONS,
            *topics,
            CHAT_CAPTURE.REPAIR_TYPE,
            CHAT_CAPTURE.REPAIR_TOPIC,
        ):
            self.assertIn(f"`{value}`", skill_text)

    def test_repair_sentinels_are_independent_and_note_only(self) -> None:
        fresh_unknown_type = self.run_capture(
            "Неизвестный type",
            "неопределено",
            "документация-и-знания",
            env=self.claude_env(),
            expect_ok=False,
        )
        self.assertEqual(fresh_unknown_type.returncode, 2)
        self.assertIn("requires --kind note", fresh_unknown_type.stderr)

        fresh_unknown_topic = self.run_capture(
            "Неизвестный topic",
            "факт",
            "без-темы",
            env=self.claude_env(),
            expect_ok=False,
        )
        self.assertEqual(fresh_unknown_topic.returncode, 2)
        self.assertIn("requires --kind note", fresh_unknown_topic.stderr)

        self.run_capture(
            "Неизвестный type",
            "неопределено",
            "документация-и-знания",
            env=self.claude_env(),
            kind="note",
        )
        self.run_capture(
            "Неизвестный topic",
            "факт",
            "без-темы",
            env=self.claude_env(),
            kind="note",
        )

    def test_env_is_scoped_by_agent(self) -> None:
        codex_thread = str(uuid.uuid4())
        both = {**self.claude_env(), "CODEX_THREAD_ID": codex_thread}
        self.run_capture(
            "Слова через Codex",
            "решение",
            "агенты-и-ии",
            agent="codex",
            env=both,
        )
        files = self.recall_files()
        self.assertEqual(len(files), 1)
        self.assertIn(f"-codex-{codex_thread.split('-')[0]}", files[0].name)
        self.assertIn(f"session: {codex_thread}", files[0].read_text(encoding="utf-8"))

    def test_documented_claude_session_id_precedes_code_session_id(self) -> None:
        code_session = str(uuid.uuid4())
        env = {
            "CLAUDE_SESSION_ID": self.session,
            "CLAUDE_CODE_SESSION_ID": code_session,
        }
        self.run_capture(
            "Текущая сессия",
            "факт",
            "документация-и-знания",
            env=env,
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn(f"session: {self.session}", text)
        self.assertNotIn(code_session, text)

    def test_explicit_session_overrides_conflicting_environment(self) -> None:
        other_session = str(uuid.uuid4())
        env = {
            "CLAUDE_SESSION_ID": other_session,
            "CLAUDE_CODE_SESSION_ID": other_session,
        }
        self.run_capture(
            "Явная сессия",
            "факт",
            "документация-и-знания",
            env=env,
            session=self.session,
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn(f"session: {self.session}", text)
        self.assertNotIn(other_session, text)

    def test_separate_shell_commands_resolve_the_same_claude_session(self) -> None:
        other_session = str(uuid.uuid4())
        clean_env = {
            key: value
            for key, value in os.environ.items()
            if key not in SESSION_ENV_VARS
        }
        clean_env.update(
            {
                "CLAUDE_SESSION_ID": self.session,
                "CLAUDE_CODE_SESSION_ID": other_session,
            }
        )
        substitution = '${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-}}'
        resolved = subprocess.run(
            ["/bin/sh", "-c", f'printf "%s" "{substitution}"'],
            capture_output=True,
            text=True,
            env=clean_env,
            check=True,
        )
        self.assertEqual(resolved.stdout, self.session)

        command = " ".join(
            [
                shlex.quote(sys.executable),
                shlex.quote(str(SCRIPT)),
                "--quote",
                shlex.quote("Separate shell quote"),
                "--type",
                shlex.quote("факт"),
                "--topic",
                shlex.quote("документация-и-знания"),
                "--source-timestamp",
                shlex.quote(DEFAULT_SOURCE_TIMESTAMP),
                "--project",
                shlex.quote(str(self.root)),
                "--session",
                f'"{substitution}"',
            ]
        )
        captured = subprocess.run(
            ["/bin/sh", "-c", command],
            capture_output=True,
            text=True,
            env=clean_env,
            check=False,
        )
        self.assertEqual(captured.returncode, 0, captured.stderr)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn(f"session: {self.session}", text)
        self.assertNotIn(other_session, text)

    def test_same_prefix_sessions_get_separate_files(self) -> None:
        session_a = "abcd1234-aaaa-4aaa-8aaa-111111111111"
        session_b = "abcd1234-bbbb-4bbb-8bbb-222222222222"
        self.run_capture(
            "Первый разговор",
            "решение",
            "агенты-и-ии",
            env=self.claude_env(session_a),
        )
        self.run_capture(
            "Второй разговор",
            "идея",
            "агенты-и-ии",
            env=self.claude_env(session_b),
        )
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
        result = self.run_capture(
            "Без сессии",
            "решение",
            "агенты-и-ии",
            expect_ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("session id unknown", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_invalid_explicit_session_is_rejected(self) -> None:
        result = self.run_capture(
            "Чужой путь",
            "решение",
            "агенты-и-ии",
            session="../../../../../escape",
            expect_ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("session must be a canonical UUID", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_foreign_file_is_left_alone(self) -> None:
        self.run_capture(
            "Первое",
            "решение",
            "агенты-и-ии",
            env=self.claude_env(),
        )
        foreign = self.recall_files()[0]
        foreign.write_text("просто заметка без шапки\n", encoding="utf-8")
        self.run_capture(
            "Второе",
            "решение",
            "агенты-и-ии",
            env=self.claude_env(),
        )
        files = self.recall_files()
        self.assertEqual(len(files), 2)
        self.assertEqual(
            foreign.read_text(encoding="utf-8"), "просто заметка без шапки\n"
        )


if __name__ == "__main__":
    unittest.main()
