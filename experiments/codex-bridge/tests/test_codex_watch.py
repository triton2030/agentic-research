"""codex_watch.py: журнал по байтам, provisional не финал, смерть pid закрывает витрину."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import codex_watch  # noqa: E402


class JournalTests(unittest.TestCase):
    def test_torn_utf8_tail_is_left_for_next_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            full = json.dumps({"event": "codex", "kind": "agentMessage", "detail": "привет"}, ensure_ascii=False) + "\n"
            second = json.dumps({"event": "done", "detail": "я"}, ensure_ascii=False).encode("utf-8")
            path.write_bytes(full.encode("utf-8") + second[:-3])  # рвём внутри «я»
            journal = codex_watch.Journal(path)
            events = list(journal.new_events())
            self.assertEqual([e["event"] for e in events], ["codex"])
            path.write_bytes(path.read_bytes() + second[-3:] + b"\n")
            events = list(journal.new_events())
            self.assertEqual([e["event"] for e in events], ["done"])


class FinalityTests(unittest.TestCase):
    def test_provisional_result_is_not_final(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "result.json").write_text(json.dumps({"status": "interrupt_requested", "provisional": True}))
            self.assertFalse(codex_watch._result_is_final(run_dir))
            (run_dir / "result.json").write_text(json.dumps({"status": "completed", "ok": True}))
            self.assertTrue(codex_watch._result_is_final(run_dir))

    def test_dead_pid_closes_watch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "events.jsonl").write_text(json.dumps({"ts": "2026-01-01T00:00:00+00:00", "event": "codex_start"}) + "\n")
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            child.wait()
            proc = subprocess.run(
                [sys.executable, str(BACKEND / "codex_watch.py"), "watch", str(run_dir), "--poll", "1", "--pid", str(child.pid)],
                capture_output=True, text=True, timeout=30,
            )
            self.assertIn("ПРОЦЕСС ПРОГОНА ЗАВЕРШИЛСЯ", proc.stdout)
            self.assertIn("КОНЕЦ", proc.stdout)


if __name__ == "__main__":
    unittest.main()
