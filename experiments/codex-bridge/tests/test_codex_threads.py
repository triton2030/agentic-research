from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import codex_threads  # noqa: E402


def _write_registry(project: Path, lines: list[dict]) -> None:
    reg = project / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
        "\n".join(json.dumps(line, ensure_ascii=False) for line in lines) + "\n",
        encoding="utf-8",
    )


class CollapseTests(unittest.TestCase):
    def test_collapse_merges_events_and_legacy_lines(self) -> None:
        events = [
            # legacy-строка без "event" — читается как start
            {"thread_id": "t-legacy", "run_id": "r0", "created_at": "2026-07-10T10:00:00+00:00"},
            {"event": "start", "thread_id": "t-1", "run_id": "r1",
             "created_at": "2026-07-11T10:00:00+00:00", "topic": "аудит скила", "session": "aaaa1111"},
            {"event": "continue", "thread_id": "t-1", "run_id": "r2",
             "at": "2026-07-12T09:00:00+00:00", "session": "bbbb2222"},
            {"event": "archive", "thread_id": "t-legacy", "at": "2026-07-12T10:00:00+00:00"},
        ]
        threads = {t["thread_id"]: t for t in codex_threads.collapse(events)}

        t1 = threads["t-1"]
        self.assertEqual(t1["topic"], "аудит скила")
        self.assertEqual(t1["turns"], 2)
        self.assertEqual(t1["last_at"], "2026-07-12T09:00:00+00:00")
        self.assertEqual(t1["last_run_id"], "r2")
        self.assertEqual(t1["last_session"], "bbbb2222")
        self.assertFalse(t1["archived"])

        legacy = threads["t-legacy"]
        self.assertEqual(legacy["turns"], 1)
        self.assertTrue(legacy["archived"])

    def test_stale_ids_respects_threshold_and_archive(self) -> None:
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        threads = codex_threads.collapse([
            {"event": "start", "thread_id": "old", "run_id": "r1",
             "created_at": "2026-07-09T10:00:00+00:00", "topic": "x"},
            {"event": "start", "thread_id": "fresh", "run_id": "r2",
             "created_at": "2026-07-12T09:00:00+00:00", "topic": "y"},
            {"event": "start", "thread_id": "old-archived", "run_id": "r3",
             "created_at": "2026-07-01T10:00:00+00:00", "topic": "z"},
            {"event": "archive", "thread_id": "old-archived", "at": "2026-07-02T10:00:00+00:00"},
        ])
        self.assertEqual(codex_threads.stale_ids(threads, now, 48), ["old"])


class RobustnessTests(unittest.TestCase):
    def test_naive_timestamps_do_not_crash(self) -> None:
        """Naive ISO-метка (без timezone) считается UTC, не роняет доску."""
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        threads = codex_threads.collapse([
            {"event": "start", "thread_id": "naive", "run_id": "r1",
             "created_at": "2026-07-09T10:00:00", "topic": "x"},
        ])
        self.assertEqual(codex_threads.stale_ids(threads, now, 48), ["naive"])
        self.assertTrue(codex_threads._fmt_age("2026-07-09T10:00:00", now).endswith("д"))

    def test_read_events_counts_bad_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reg = root / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
            reg.parent.mkdir(parents=True, exist_ok=True)
            reg.write_text(
                '{"event": "start", "thread_id": "ok", "created_at": "2026-07-01T10:00:00+00:00"}\n'
                "не json вовсе\n"
                "[1, 2, 3]\n"
                '{"event": "start", "no_thread_id": true}\n',
                encoding="utf-8",
            )
            events, bad = codex_threads.read_events(root)
            self.assertEqual(len(events), 1)
            self.assertEqual(bad, 3)

    def test_archive_stale_fails_closed_on_corrupt_registry(self) -> None:
        """По повреждённой доске нельзя судить о свежести — SDK не зовём."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reg = root / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
            reg.parent.mkdir(parents=True, exist_ok=True)
            reg.write_text(
                '{"event": "start", "thread_id": "old", "created_at": "2026-07-01T10:00:00+00:00"}\n'
                "битая строка\n",
                encoding="utf-8",
            )
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = codex_threads.cmd_archive(root, None, stale=True, older_hours=48)
            self.assertEqual(rc, 2)
            self.assertIn("повреждённых строк", err.getvalue())
            self.assertNotIn("openai_codex", sys.modules)

    def test_adopted_foreign_thread_topic_from_continue(self) -> None:
        threads = codex_threads.collapse([
            {"event": "continue", "thread_id": "adopted", "run_id": "r1",
             "at": "2026-07-12T09:00:00+00:00", "topic": "усыновлённая тема"},
        ])
        self.assertEqual(threads[0]["topic"], "усыновлённая тема")

    def test_unarchive_event_clears_flag(self) -> None:
        threads = codex_threads.collapse([
            {"event": "start", "thread_id": "t", "created_at": "2026-07-01T10:00:00+00:00"},
            {"event": "archive", "thread_id": "t", "at": "2026-07-03T10:00:00+00:00"},
            {"event": "unarchive", "thread_id": "t", "at": "2026-07-04T10:00:00+00:00"},
        ])
        self.assertFalse(threads[0]["archived"])


class ArchiveTests(unittest.TestCase):
    def test_archive_stale_calls_sdk_and_appends_events(self) -> None:
        archived: list[str] = []

        class _FakeCodex:
            def __init__(self, config=None):  # noqa: ANN001
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):  # noqa: ANN002
                return False

            def thread_archive(self, thread_id):  # noqa: ANN001
                archived.append(thread_id)

        mod = types.ModuleType("openai_codex")
        mod.Codex = _FakeCodex
        mod.CodexConfig = lambda **kw: None
        sys.modules["openai_codex"] = mod
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_registry(root, [
                    {"event": "start", "thread_id": "old", "run_id": "r1",
                     "created_at": "2026-07-01T10:00:00+00:00", "topic": "старый"},
                ])
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = codex_threads.cmd_archive(root, None, stale=True, older_hours=48)
                self.assertEqual(rc, 0)
                self.assertEqual(archived, ["old"])
                events = [
                    json.loads(line)
                    for line in (root / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl")
                    .read_text().splitlines()
                ]
                self.assertEqual(events[-1]["event"], "archive")
                self.assertEqual(events[-1]["thread_id"], "old")
                # повторный --stale уже ничего не берёт: archive-событие учтено
                threads = codex_threads.collapse(events)
                self.assertEqual(
                    codex_threads.stale_ids(threads, datetime.now(timezone.utc), 48), []
                )
        finally:
            sys.modules.pop("openai_codex", None)

    def test_archive_partial_failure_continues_batch(self) -> None:
        """Ошибка SDK на одном треде не обрывает батч и даёт rc=1;
        archive-событие пишется только за успешные."""
        archived: list[str] = []

        class _FakeCodex:
            def __init__(self, config=None):  # noqa: ANN001
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):  # noqa: ANN002
                return False

            def thread_archive(self, thread_id):  # noqa: ANN001
                if thread_id == "bad":
                    raise RuntimeError("no rollout found")
                archived.append(thread_id)

        mod = types.ModuleType("openai_codex")
        mod.Codex = _FakeCodex
        mod.CodexConfig = lambda **kw: None
        sys.modules["openai_codex"] = mod
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_registry(root, [
                    {"event": "start", "thread_id": "bad", "run_id": "r1",
                     "created_at": "2026-07-01T10:00:00+00:00"},
                    {"event": "start", "thread_id": "good", "run_id": "r2",
                     "created_at": "2026-07-01T11:00:00+00:00"},
                ])
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = codex_threads.cmd_archive(root, None, stale=True, older_hours=48)
                self.assertEqual(rc, 1)
                self.assertEqual(archived, ["good"])
                self.assertIn("archive FAILED: bad", err.getvalue())
                events = [
                    json.loads(line)
                    for line in (root / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl")
                    .read_text().splitlines()
                ]
                archive_events = [e for e in events if e.get("event") == "archive"]
                self.assertEqual([e["thread_id"] for e in archive_events], ["good"])
        finally:
            sys.modules.pop("openai_codex", None)

    def test_unarchive_calls_sdk_and_appends_event(self) -> None:
        unarchived: list[str] = []

        class _FakeCodex:
            def __init__(self, config=None):  # noqa: ANN001
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):  # noqa: ANN002
                return False

            def thread_unarchive(self, thread_id):  # noqa: ANN001
                unarchived.append(thread_id)

        mod = types.ModuleType("openai_codex")
        mod.Codex = _FakeCodex
        mod.CodexConfig = lambda **kw: None
        sys.modules["openai_codex"] = mod
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_registry(root, [
                    {"event": "start", "thread_id": "t", "run_id": "r1",
                     "created_at": "2026-07-01T10:00:00+00:00"},
                    {"event": "archive", "thread_id": "t", "at": "2026-07-03T10:00:00+00:00"},
                ])
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = codex_threads.cmd_unarchive(root, "t")
                self.assertEqual(rc, 0)
                self.assertEqual(unarchived, ["t"])
                events, bad = codex_threads.read_events(root)
                self.assertEqual(bad, 0)
                self.assertFalse(codex_threads.collapse(events)[0]["archived"])
        finally:
            sys.modules.pop("openai_codex", None)


class CliValidationTests(unittest.TestCase):
    def _run_main(self, argv: list[str]) -> tuple[int, str]:
        saved = sys.argv[:]
        sys.argv = ["codex_threads.py", *argv]
        err = io.StringIO()
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = codex_threads.main()
        finally:
            sys.argv = saved
        return rc, err.getvalue()

    def test_ambiguous_and_invalid_combinations_rejected(self) -> None:
        rc, err = self._run_main(["archive", "t-1", "--stale"])
        self.assertEqual(rc, 2)
        self.assertIn("ровно одно", err)

        rc, err = self._run_main(["archive"])
        self.assertEqual(rc, 2)

        rc, err = self._run_main(["list", "t-1"])
        self.assertEqual(rc, 2)
        self.assertIn("не принимает", err)

        rc, err = self._run_main(["list", "--older-hours", "0"])
        self.assertEqual(rc, 2)
        self.assertIn("> 0", err)

        rc, err = self._run_main(["unarchive", "--stale", "t-1"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
