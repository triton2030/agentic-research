"""Tests for chat_capture.py: session files, env routing, inventory, dedup."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shlex
import shutil
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
DEFAULT_CONTEXT_NOTE = "Test source situation outside the quote."
DEFAULT_SESSION_CONTEXT = (
    "chat recall capture; session files; owner-memory metadata"
)
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


RUNTIME_ROOT_LINE = 'ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"'
RUNTIME_AGENT = "codex"


class ChatCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.session = str(uuid.uuid4())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_capture(
        self, quote: str, type_: str, topic: str,
        agent: str | None = "claude",
        env: dict[str, str] | None = None,
        kind: str | None = None,
        context_note: str | None = DEFAULT_CONTEXT_NOTE,
        session_context: str | None = DEFAULT_SESSION_CONTEXT,
        session: str | None = None,
        source_timestamp: str | None = DEFAULT_SOURCE_TIMESTAMP,
        json_output: bool = False,
        expect_ok: bool = True,
        new_topic: str | None = None,
        supersedes: str | None = None,
        contested: str | None = None,
        ensure_topic_map: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        topic_map = self.root / "_ops" / "chat-recall" / "topics.md"
        if (
            ensure_topic_map
            and re.fullmatch(r"[\w.\-/]+", topic)
            and topic != CHAT_CAPTURE.REPAIR_TOPIC
        ):
            if not topic_map.exists():
                self.write_topic_map(f"- `{topic}` — Тема тестовой записи")
            elif f"`{topic}`" not in topic_map.read_text(encoding="utf-8") and not new_topic:
                with topic_map.open("a", encoding="utf-8") as stream:
                    stream.write(f"- `{topic}` — Тема тестовой записи\n")
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
        if kind == "note" and context_note == DEFAULT_CONTEXT_NOTE:
            context_note = None
        if kind == "note" and session_context == DEFAULT_SESSION_CONTEXT:
            session_context = None
        if context_note is not None:
            command += ["--context-note", context_note]
        if session_context is not None:
            command += ["--session-context", session_context]
        if session:
            command += ["--session", session]
        if new_topic:
            command += ["--new-topic", new_topic]
        if supersedes:
            command += ["--supersedes", supersedes]
        if contested:
            command += ["--contested", contested]
        if json_output:
            command.append("--json")
        result = subprocess.run(
            command, capture_output=True, text=True, env=clean_env, check=False
        )
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def recall_files(self) -> list[Path]:
        return sorted(
            path
            for path in (self.root / "_ops" / "chat-recall").glob("*.md")
            if path.stem not in {"AGENTS", "CLAUDE", "README", "INDEX", "topics"}
        )

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
        self.assertIn(
            'session-context: "chat recall capture; session files; '
            'owner-memory metadata"',
            text,
        )
        self.assertIn("  - решение", text)
        self.assertIn("  - агенты-и-ии", text)
        self.assertIn(
            '* 2001-02-03T04:05:06.789000+00:00 — "Первое решение" '
            "— type: решение | topic: агенты-и-ии",
            text,
        )

    def test_context_note_is_inline_metadata(self) -> None:
        result = self.run_capture(
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
        self.assertIn(CHAT_CAPTURE.CONTEXT_NOTE_REMINDER, result.stdout)

    def test_context_note_has_no_arbitrary_character_limit(self) -> None:
        context = "Внешняя сцена " + "уточнена подробно " * 30
        self.assertGreater(len(context), 300)

        self.run_capture(
            "Длинная контекстная дельта допустима",
            "критерий",
            "документация-и-знания",
            env=self.claude_env(),
            context_note=context,
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn("context-note: " + context.strip(), text)

    def test_quote_without_context_note_is_rejected(self) -> None:
        result = self.run_capture(
            "Контекст нельзя опускать",
            "коррекция",
            "документация-и-знания",
            env=self.claude_env(),
            context_note=None,
            expect_ok=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--context-note is required for --kind quote", result.stderr)
        self.assertIn("never repeat or paraphrase the quote", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_selection_without_context_note_is_rejected(self) -> None:
        result = self.run_capture(
            "Выбрал локальный путь",
            "решение",
            "документация-и-знания",
            env=self.claude_env(),
            kind="selection",
            context_note=None,
            expect_ok=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "--context-note is required for --kind quote and --kind selection",
            result.stderr,
        )
        self.assertEqual(self.recall_files(), [])

    def test_quote_and_selection_without_session_context_are_rejected(self) -> None:
        for kind in ("quote", "selection"):
            with self.subTest(kind=kind):
                result = self.run_capture(
                    "Карточку сессии нельзя опускать",
                    "решение",
                    "документация-и-знания",
                    env=self.claude_env(),
                    kind=kind,
                    session_context=None,
                    expect_ok=False,
                )

                self.assertEqual(result.returncode, 2)
                self.assertIn(
                    "--session-context is required for --kind quote and "
                    "--kind selection",
                    result.stderr,
                )
                self.assertEqual(self.recall_files(), [])

    def test_help_promotes_context_note_check(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = " ".join(result.stdout.split())
        self.assertIn(
            "preserve its non-inferable context",
            help_text,
        )
        self.assertIn("caller-confirmed owner excerpt", help_text)
        self.assertIn("shorten only by deletion", help_text)
        self.assertIn("--context-note CONTEXT_NOTE", help_text)
        self.assertIn("--session-context SESSION_CONTEXT", help_text)
        self.assertIn(
            "required for --kind quote",
            help_text,
        )
        self.assertIn(
            "never repeat or paraphrase the quote",
            help_text,
        )
        self.assertIn("complete current card, not a delta", help_text)

    def test_agent_is_required(self) -> None:
        result = self.run_capture(
            "Runtime должен быть явным",
            "факт",
            "документация-и-знания",
            agent=None,
            env=self.claude_env(),
            expect_ok=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "the following arguments are required: --agent",
            result.stderr,
        )
        self.assertEqual(self.recall_files(), [])

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
        self.assertNotIn(CHAT_CAPTURE.CONTEXT_NOTE_REMINDER, result.stdout)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertEqual(text.count('"Одна мысль"'), 1)

    def test_duplicate_quote_still_replaces_complete_session_context(self) -> None:
        self.run_capture(
            "Одна мысль",
            "идея",
            "агенты-и-ии",
            env=self.claude_env(),
            session_context="chat recall capture; session files",
        )
        result = self.run_capture(
            "Одна мысль",
            "идея",
            "агенты-и-ии",
            env=self.claude_env(),
            session_context=(
                "chat recall capture; session files; hybrid retrieval; BM25"
            ),
        )

        self.assertIn("quote already present; session-context updated", result.stdout)
        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertEqual(text.count('"Одна мысль"'), 1)
        self.assertIn(
            'session-context: "chat recall capture; session files; '
            'hybrid retrieval; BM25"',
            text,
        )
        self.assertNotIn('session-context: "chat recall capture; session files"\n', text)

    def test_json_receipt_addresses_the_saved_raw_record(self) -> None:
        result = self.run_capture(
            "Адресуемая мысль",
            "решение",
            "агенты-и-ии",
            env=self.claude_env(),
            json_output=True,
        )

        receipt = json.loads(result.stdout)
        holder = self.recall_files()[0]
        line_number = next(
            number
            for number, line in enumerate(
                holder.read_text(encoding="utf-8").splitlines(), start=1
            )
            if '"Адресуемая мысль"' in line
        )
        self.assertEqual(receipt["status"], "written")
        self.assertEqual(receipt["anchor"], f"{holder.name}#L{line_number}")
        self.assertEqual(receipt["session"], self.session)
        self.assertEqual(receipt["topic"], "агенты-и-ии")
        self.assertRegex(receipt["record_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn(CHAT_CAPTURE.CONTEXT_NOTE_REMINDER, result.stdout)

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

    def test_append_extends_legacy_holder_without_touching_old_lines(self) -> None:
        self.run_capture(
            "Legacy quote",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
        )
        legacy_path = self.recall_files()[0]
        legacy_text = re.sub(
            r'(^\* .* — "Legacy quote" — .*$)',
            r'\1 | source: turn-context | precision: minute',
            legacy_path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
        legacy_path.write_text(legacy_text, encoding="utf-8")

        self.run_capture(
            "New quote",
            "идея",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp="2026-08-12",
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn(
            '"Legacy quote" — type: факт | topic: документация-и-знания'
            " | context-note: Test source situation outside the quote."
            " | source: turn-context | precision: minute",
            text,
        )
        self.assertIn('"New quote"', text)
        new_entry = next(
            line for line in text.splitlines() if '"New quote"' in line
        )
        self.assertNotIn("source:", new_entry)
        self.assertNotIn("precision:", new_entry)

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
        ), self.assertRaisesRegex(OSError, "simulated rewrite failure"):
            CHAT_CAPTURE.append_entry(
                old_path,
                "claude",
                self.session,
                "идея",
                "документация-и-знания",
                "Earlier quote",
                CHAT_CAPTURE.source_timestamp(earlier),
                session_card=DEFAULT_SESSION_CONTEXT,
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

    def test_atomic_rewrite_preserves_existing_permissions(self) -> None:
        self.run_capture(
            "Existing quote",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
        )
        holder = self.recall_files()[0]
        holder.chmod(0o640)

        self.run_capture(
            "Next quote",
            "идея",
            "документация-и-знания",
            env=self.claude_env(),
        )

        self.assertEqual(holder.stat().st_mode & 0o777, 0o640)

    def test_timestamp_accepts_date_and_minute_rejects_unknown_for_quote(self) -> None:
        omitted = self.run_capture(
            "Без даты",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
            source_timestamp=None,
        )
        self.assertEqual(omitted.returncode, 0)
        self.assertIn("used the write time", omitted.stdout)
        self.assertIn("for backfill pass --source-timestamp", omitted.stdout)
        written = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertRegex(written, r"\* \d{4}-\d{2}-\d{2}T[\d:]+[+-]\d{2}:\d{2} — \"Без даты\"")
        for path in self.recall_files():
            path.unlink()

        for label, value in (
            ("minute", "2001-02-03T04:05:06"),
            ("date", "2001-02-03"),
        ):
            with self.subTest(label=label):
                self.run_capture(
                    f"Приблизительная дата {label}",
                    "факт",
                    "документация-и-знания",
                    env=self.claude_env(),
                    session=str(uuid.uuid4()),
                    source_timestamp=value,
                )
        self.assertEqual(len(self.recall_files()), 2)

        rejected = self.run_capture(
            "Дата unknown",
            "факт",
            "документация-и-знания",
            env=self.claude_env(),
            session=str(uuid.uuid4()),
            source_timestamp="unknown",
            expect_ok=False,
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("unknown timestamp is repair-only", rejected.stderr)

    def test_removed_timestamp_provenance_flags_are_rejected_before_write(self) -> None:
        env = self.claude_env()
        base = [
            sys.executable,
            str(SCRIPT),
            "--agent",
            "claude",
            "--quote",
            "Выбрал локальный путь",
            "--type",
            "решение",
            "--topic",
            "документация-и-знания",
            "--kind",
            "selection",
            "--source-timestamp",
            DEFAULT_SOURCE_TIMESTAMP,
            "--project",
            str(self.root),
        ]
        for flag, value in (
            ("--timestamp-source", "turn-context"),
            ("--timestamp-precision", "minute"),
            ("--source-ref", "msg-native-123"),
        ):
            with self.subTest(flag=flag):
                result = subprocess.run(
                    [*base, flag, value],
                    capture_output=True,
                    text=True,
                    env=env,
                    check=False,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(f"unrecognized arguments: {flag}", result.stderr)
                self.assertEqual(self.recall_files(), [])

    def test_selection_and_note_use_only_exact_record_metadata(self) -> None:
        self.run_capture(
            "Выбрал локальный путь",
            "решение",
            "документация-и-знания",
            env=self.claude_env(),
            kind="selection",
        )
        self.run_capture(
            "Восстановление подтверждено exact source",
            "неопределено",
            "без-темы",
            env=self.claude_env(),
            kind="note",
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertIn("kind: selection", text)
        self.assertIn("kind: note", text)
        self.assertIn("context-note: " + DEFAULT_CONTEXT_NOTE, text)
        self.assertNotIn("source:", text)
        self.assertNotIn("precision:", text)
        self.assertNotIn("source-ref:", text)

    def test_repair_note_can_leave_legacy_holder_without_session_context(self) -> None:
        self.run_capture(
            "Repair-only note",
            "неопределено",
            "без-темы",
            env=self.claude_env(),
            kind="note",
        )

        text = self.recall_files()[0].read_text(encoding="utf-8")
        self.assertNotIn("session-context:", text)

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

    def test_topic_present_in_map_is_accepted(self) -> None:
        self.run_capture(
            "Что-то",
            "решение",
            "mockup-zone-editor",
            env=self.claude_env(),
        )
        again = self.run_capture(
            "Другая цитата про тот же предмет",
            "решение",
            "mockup-zone-editor",
            env=self.claude_env(),
        )
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn(
            "topic: mockup-zone-editor",
            self.recall_files()[0].read_text(encoding="utf-8"),
        )

    def test_topic_that_is_not_a_plain_handle_is_rejected(self) -> None:
        result = self.run_capture(
            "Что-то", "решение", "foo: bar", env=self.claude_env(), expect_ok=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("plain handle", result.stderr)
        self.assertEqual(self.recall_files(), [])

    def test_capture_without_topic_map_is_rejected_without_corpus_scan(self) -> None:
        argv = [
            str(SCRIPT),
            "--quote", "Delta без inventory scan",
            "--context-note", DEFAULT_CONTEXT_NOTE,
            "--session-context", DEFAULT_SESSION_CONTEXT,
            "--source-timestamp", DEFAULT_SOURCE_TIMESTAMP,
            "--type", "решение",
            "--topic", "delta-topic",
            "--agent", "claude",
            "--project", str(self.root),
            "--session", self.session,
        ]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            CHAT_CAPTURE,
            "corpus_topics",
            side_effect=AssertionError("ordinary capture must not scan raw corpus"),
        ):
            result = CHAT_CAPTURE.main()

        self.assertEqual(result, 2)
        self.assertEqual(self.recall_files(), [])

    def test_metadata_vocabulary_lists_corpus_topics(self) -> None:
        empty = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-metadata", "--project", str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(empty.returncode, 0, empty.stderr)
        self.assertIn("Types:\n  решение:", empty.stdout)
        self.assertIn("none recorded yet", empty.stdout)
        self.assertNotIn("--new-topic", empty.stdout)

        self.run_capture(
            "Первое решение", "решение", "агенты-и-ии", env=self.claude_env()
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-metadata", "--project", str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("агенты-и-ии [1]", result.stdout)
        self.assertIn("repair-only sentinel", result.stdout)

    def write_topic_map(self, *rows: str, retired: str = "") -> Path:
        path = self.root / "_ops" / "chat-recall" / "topics.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "# Карта тем\n\n## Темы\n\n" + "\n".join(rows) + "\n"
        if retired:
            body += f"\n## Не переиспользовать\n\n- `{retired}` — поглощена\n"
        path.write_text(body, encoding="utf-8")
        return path

    def test_topic_map_owns_the_vocabulary(self) -> None:
        self.write_topic_map(
            "- `chat-recall-corpus` — Фиксация и формат корпуса",
            retired="deep-agents",
        )
        listed = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-metadata", "--project", str(self.root)],
            capture_output=True, text=True, check=False,
        )
        self.assertIn("chat-recall-corpus [0] — Фиксация и формат корпуса", listed.stdout)
        self.assertIn("Retired (do not reuse): deep-agents", listed.stdout)

        unknown = self.run_capture(
            "Реплика", "решение", "выдуманная-тема",
            env=self.claude_env(), expect_ok=False, ensure_topic_map=False,
        )
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("is not in", unknown.stderr)
        self.assertEqual(self.recall_files(), [])

        retired = self.run_capture(
            "Реплика", "решение", "deep-agents",
            env=self.claude_env(), expect_ok=False, ensure_topic_map=False,
        )
        self.assertEqual(retired.returncode, 2)
        self.assertIn("is retired", retired.stderr)

        self.run_capture(
            "Реплика", "решение", "chat-recall-corpus", env=self.claude_env()
        )
        self.assertEqual(len(self.recall_files()), 1)

    def test_new_topic_adds_its_row_to_the_map(self) -> None:
        topic_map = self.write_topic_map("- `chat-recall-corpus` — Формат корпуса")
        self.run_capture(
            "Реплика про новое", "решение", "html-artifacts",
            env=self.claude_env(), new_topic="Быстрые HTML-артефакты",
        )
        self.assertIn(
            "- `html-artifacts` — Быстрые HTML-артефакты",
            topic_map.read_text(encoding="utf-8"),
        )
        self.run_capture(
            "Вторая реплика", "решение", "html-artifacts", env=self.claude_env()
        )
        self.assertEqual(
            topic_map.read_text(encoding="utf-8").count("html-artifacts"), 1
        )

    def test_new_topic_failure_leaves_map_and_holder_unchanged(self) -> None:
        topic_map = self.root / "_ops" / "chat-recall" / "topics.md"
        topic_map.parent.mkdir(parents=True, exist_ok=True)
        topic_map.write_text("# Карта тем\n\n## Темы\n", encoding="utf-8")
        before = topic_map.read_text(encoding="utf-8")

        result = self.run_capture(
            "Реплика про новое",
            "решение",
            "html-artifacts",
            env=self.claude_env(),
            new_topic="Быстрые HTML-артефакты",
            expect_ok=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("topic map has no topic rows to extend", result.stderr)
        self.assertEqual(topic_map.read_text(encoding="utf-8"), before)
        self.assertEqual(self.recall_files(), [])

    def test_new_topic_rename_failure_restores_map_and_both_holders(self) -> None:
        topic_map = self.write_topic_map(
            "- `chat-recall-corpus` — Формат корпуса"
        )
        self.run_capture(
            "Исходная реплика",
            "решение",
            "chat-recall-corpus",
            env=self.claude_env(),
            source_timestamp="2010-06-15T12:00:00Z",
        )
        old_path = self.recall_files()[0]
        holder_before = old_path.read_text(encoding="utf-8")
        map_before = topic_map.read_text(encoding="utf-8")
        real_unlink = Path.unlink
        failed = False

        def fail_old_holder_once(path: Path, *args: object, **kwargs: object) -> None:
            nonlocal failed
            if path.resolve() == old_path.resolve() and not failed:
                failed = True
                raise OSError("simulated old-holder unlink failure")
            real_unlink(path, *args, **kwargs)

        argv = [
            str(SCRIPT),
            "--quote", "Восстановленная ранняя реплика",
            "--type", "решение",
            "--topic", "html-artifacts",
            "--new-topic", "Быстрые HTML-артефакты",
            "--context-note", DEFAULT_CONTEXT_NOTE,
            "--session-context", DEFAULT_SESSION_CONTEXT,
            "--source-timestamp", "1999-01-02T03:04:05Z",
            "--agent", "claude",
            "--project", str(self.root),
            "--session", self.session,
            "--json",
        ]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(
            Path, "unlink", new=fail_old_holder_once
        ):
            self.assertEqual(CHAT_CAPTURE.main(), 2)

        self.assertTrue(failed)
        self.assertEqual(topic_map.read_text(encoding="utf-8"), map_before)
        self.assertEqual(self.recall_files(), [old_path])
        self.assertEqual(old_path.read_text(encoding="utf-8"), holder_before)

    def test_supersedes_binds_the_address_to_a_fingerprint(self) -> None:
        self.write_topic_map("- `chat-recall-corpus` — Формат корпуса")
        self.run_capture(
            "Старая позиция", "решение", "chat-recall-corpus", env=self.claude_env()
        )
        target = self.recall_files()[0]
        lines = target.read_text(encoding="utf-8").splitlines()
        line_number = next(
            index for index, line in enumerate(lines, start=1)
            if line.startswith("* ")
        )
        self.run_capture(
            "Новая позиция отменяет старую", "коррекция", "chat-recall-corpus",
            env=self.claude_env(), source_timestamp="2001-02-04T04:05:06.789Z",
            supersedes=f"{target.name}#L{line_number}",
        )
        written = target.read_text(encoding="utf-8")
        self.assertRegex(written, rf"supersedes: {target.name}:{line_number} sha:\w{{8}}")

        digest_spec = importlib.util.spec_from_file_location(
            "chat_digest_capture_boundary", SCRIPT.parent / "chat_digest.py"
        )
        if digest_spec is None or digest_spec.loader is None:
            raise RuntimeError("cannot load chat_digest.py for capture boundary test")
        digest = importlib.util.module_from_spec(digest_spec)
        digest_spec.loader.exec_module(digest)
        records, _ = digest.load(self.root / "_ops" / "chat-recall")
        digest.link_supersessions(records)
        old_record = next(record for record in records if record["text"] == "Старая позиция")
        self.assertEqual(old_record["superseded_by"], [
            record["address"]
            for record in records
            if record["text"] == "Новая позиция отменяет старую"
        ])

        missing = self.run_capture(
            "Ещё реплика", "коррекция", "chat-recall-corpus",
            env=self.claude_env(), supersedes=f"{target.name}#L999", expect_ok=False,
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("does not address a record line", missing.stderr)
        self.assertIn(f"{target.name}:", missing.stderr)

        malformed = self.run_capture(
            "И ещё", "коррекция", "chat-recall-corpus",
            env=self.claude_env(), contested="просто текст", expect_ok=False,
        )
        self.assertEqual(malformed.returncode, 2)
        self.assertIn("<file>.md:<line>", malformed.stderr)

    def test_runtime_owner_documents_metadata_vocabulary(self) -> None:
        capture_text = (SKILL.parent / "references" / "capture.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("--list-metadata", capture_text)
        self.assertIn("карту тем", capture_text)
        self.assertLess(capture_text.index("--list-metadata"), capture_text.index("--help"))
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--list-metadata", "--project", str(self.root)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for value in (
            *CHAT_CAPTURE.TYPE_DESCRIPTIONS,
            CHAT_CAPTURE.REPAIR_TYPE,
            CHAT_CAPTURE.REPAIR_TOPIC,
        ):
            self.assertIn(f"  {value}:", result.stdout)

    def test_body_owns_judgement_and_delegates_mechanics_to_help(self) -> None:
        skill_text = SKILL.read_text(encoding="utf-8")
        normalized_skill = " ".join(skill_text.split())
        self.assertIn("Правда о механике живёт в `--help`", normalized_skill)
        self.assertIn(
            "Скилу принадлежат только суждения, которые код вынести не может",
            normalized_skill,
        )
        self.assertIn("носитель авторства не доказывает", normalized_skill)
        self.assertIn("Найденное — не то же, что действующее", normalized_skill)
        self.assertIn("найти и поверить", normalized_skill)
        self.assertIn("запись важнее поиска", normalized_skill)
        self.assertIn("без истории этого разговора", normalized_skill)
        self.assertIn("`_ops/chat-recall/`", skill_text)
        self.assertIn("references/capture.md", skill_text)
        self.assertIn("references/retrieval.md", skill_text)
        self.assertIn("references/integrity.md", skill_text)
        self.assertIn(
            "изменение или удаление существующей — только по его слову",
            normalized_skill,
        )

    def test_capture_contract_gates_on_materiality(self) -> None:
        capture_text = (SKILL.parent / "references" / "capture.md").read_text(
            encoding="utf-8"
        )
        repair_text = (SKILL.parent / "references" / "integrity.md").read_text(
            encoding="utf-8"
        )
        normalized_capture = " ".join(capture_text.split())
        normalized_repair = " ".join(repair_text.split())
        self.assertIn("восстановимая сцена", normalized_capture)
        self.assertIn("Отдели речь владельца от материала-носителя", normalized_capture)
        self.assertIn("вставленный документ", normalized_capture)
        self.assertIn("вывод другого агента", normalized_capture)
        self.assertIn("При неясном авторстве верни gap", normalized_capture)
        self.assertIn("только вычёркиванием", normalized_capture)
        self.assertIn("`quote` — дословная речь владельца", normalized_capture)
        self.assertIn("`selection` — сделанный им выбор", normalized_capture)
        self.assertIn("`note` — твоё объяснение", normalized_capture)
        self.assertIn("не записываются вовсе", normalized_capture)
        self.assertIn("Полностью прочитай текущую карту тем", normalized_capture)
        self.assertIn("по смыслу предмета, а не по совпадению слов", normalized_capture)
        self.assertIn("описывает весь разговор", normalized_capture)
        self.assertIn("одну Capture-операцию", normalized_capture)
        self.assertIn("пометь конфликт вместо молчаливого выбора", normalized_capture)
        self.assertIn("квитанция helper-а и её адрес", normalized_capture)
        self.assertIn("timestamp исходной записи транскрипта", normalized_capture)
        self.assertNotIn("простое assent пропусти", capture_text)
        self.assertNotIn("topic_reconcile.py", capture_text)
        self.assertNotIn("--new-topic-boundary", capture_text)
        self.assertIn("`capture-needed`", repair_text)
        self.assertIn("только явной просьбой владельца", normalized_repair)
        self.assertIn("ни разу не став их автором", normalized_repair)
        self.assertIn("не авторство каждого фрагмента", normalized_repair)
        self.assertIn("Иначе транскрипт не читай и верни gap", normalized_repair)
        self.assertIn("явной просьбы владельца в текущем ходе", normalized_repair)
        self.assertIn("Текст записи не переписывается", normalized_repair)
        self.assertIn("создаёт двойника", normalized_repair)
        self.assertNotIn("references/capture.md", repair_text)
        self.assertNotIn("source address", repair_text)

    def test_retrieval_contract_keeps_metadata_routes_and_full_holder_read(self) -> None:
        retrieval_text = (SKILL.parent / "references" / "retrieval.md").read_text(
            encoding="utf-8"
        )
        normalized_retrieval = " ".join(retrieval_text.split())
        self.assertIn("`topic_candidates`", retrieval_text)
        self.assertIn("`holders`", retrieval_text)
        self.assertIn("скоры не смешиваются", normalized_retrieval)
        self.assertIn("ранжирует, но не судит", normalized_retrieval)
        self.assertIn("прочитай выбранный holder целиком", normalized_retrieval)
        self.assertIn("в хронологическом порядке", normalized_retrieval)
        self.assertIn("три вытеснения", normalized_retrieval)
        self.assertIn("жив ли сегодня носитель цитаты", normalized_retrieval)
        self.assertIn("_ops/findings/", retrieval_text)
        self.assertIn("--lexical", retrieval_text)
        self.assertIn("--prepare", retrieval_text)
        self.assertIn("ровно одного дешёвого", normalized_retrieval)
        self.assertIn("нативный механизм текущего runtime", normalized_retrieval)
        self.assertIn("не только в начале, но и по ходу работы", normalized_retrieval)
        self.assertIn("самую дешёвую доступную модель", normalized_retrieval)
        self.assertIn("Не жди его", normalized_retrieval)
        self.assertIn("read-only corpus-only", normalized_retrieval)
        self.assertIn("address, date, age и gaps", normalized_retrieval)
        self.assertIn("не подменяй его дорогим", normalized_retrieval)
        self.assertIn("абсолютную дату и относительный возраст", normalized_retrieval)
        self.assertIn("в часах или днях", normalized_retrieval)
        self.assertNotIn("можно передать", retrieval_text)
        self.assertNotIn("chat_recall.py", retrieval_text)
        self.assertNotIn("native transcript", retrieval_text)

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

    def test_capture_and_retrieval_resolve_the_same_target_corpus(self) -> None:
        """Capture must not write to one project while retrieval reads another.

        Retrieval and integrity address the corpus as
        `${TARGET_PROJECT_ROOT:-$PWD}/_ops/chat-recall`. Without `--project`,
        capture has to land in exactly that folder.
        """
        other = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, other, True)
        (other / "_ops" / "chat-recall").mkdir(parents=True)
        (other / "_ops" / "chat-recall" / "topics.md").write_text(
            "- `агенты-и-ии` — Тема тестовой записи\n", encoding="utf-8"
        )
        clean_env = {k: v for k, v in os.environ.items() if k not in SESSION_ENV_VARS}
        clean_env.update(self.claude_env())
        clean_env["TARGET_PROJECT_ROOT"] = str(other)
        command = [
            sys.executable, str(SCRIPT),
            "--quote", "Целевой проект берётся из окружения",
            "--type", "решение", "--topic", "агенты-и-ии",
            "--context-note", DEFAULT_CONTEXT_NOTE,
            "--session-context", DEFAULT_SESSION_CONTEXT,
            "--agent", "claude",
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, check=False,
            env=clean_env, cwd=str(self.root),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        retrieval_dir = other / "_ops" / "chat-recall"
        written = [p for p in retrieval_dir.glob("*.md") if p.name != "topics.md"]
        self.assertEqual(len(written), 1, f"ожидался один файл в {retrieval_dir}")
        self.assertIn(
            "Целевой проект берётся из окружения",
            written[0].read_text(encoding="utf-8"),
        )
        self.assertEqual(
            [], list((self.root / "_ops" / "chat-recall").glob("2*.md")),
            "запись не должна попадать в текущую папку, когда задан TARGET_PROJECT_ROOT",
        )

    def test_explicit_project_outranks_target_project_root(self) -> None:
        other = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, other, True)
        (other / "_ops" / "chat-recall").mkdir(parents=True)
        self.run_capture(
            "Явный project побеждает переменную",
            "решение",
            "агенты-и-ии",
            env={**self.claude_env(), "TARGET_PROJECT_ROOT": str(other)},
        )
        self.assertEqual(len(self.recall_files()), 1)
        self.assertEqual(
            [], list((other / "_ops" / "chat-recall").glob("*.md")),
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
        self.write_topic_map("- `документация-и-знания` — Тема тестовой записи")
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
                "--agent",
                shlex.quote("claude"),
                "--quote",
                shlex.quote("Separate shell quote"),
                "--type",
                shlex.quote("факт"),
                "--topic",
                shlex.quote("документация-и-знания"),
                "--source-timestamp",
                shlex.quote(DEFAULT_SOURCE_TIMESTAMP),
                "--context-note",
                shlex.quote("Captured through a separate shell command."),
                "--session-context",
                shlex.quote(DEFAULT_SESSION_CONTEXT),
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
