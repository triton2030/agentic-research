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


if __name__ == "__main__":
    unittest.main()
