"""codex_watch.py: журнал по байтам, provisional не финал, смерть pid закрывает витрину."""
from __future__ import annotations

import json
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


class SoloRunTests(unittest.TestCase):
    def test_pulse_and_closing_line_keep_solo_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            run = codex_watch.Run(run_dir, pulse=True)
            event = {
                "ts": "2026-01-01T00:00:00+00:00", "event": "codex",
                "method": "item/completed", "kind": "agentMessage",
                "detail": "6 симв.: привет",
            }
            self.assertEqual(list(run.absorb(event)), ["   0с привет"])
            (run_dir / "result.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
            self.assertEqual(list(run.closing_lines()), [f"OK {run_dir.name} · 0с · 1ш"])

    def test_look_shows_one_live_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            run_dir = project / "_workspace" / "work-artifacts" / "2026-10-05-probe" / "agents" / "codex-artifacts" / "run-1"
            run_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text("{}", encoding="utf-8")
            (run_dir / "events.jsonl").write_text(
                json.dumps({"ts": "2026-01-01T00:00:00+00:00", "event": "codex",
                            "method": "item/completed", "kind": "agentMessage"}) + "\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [sys.executable, str(BACKEND / "codex_watch.py"), "look", str(project)],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("run-1 · идёт", proc.stdout)
            self.assertIn("одиночный · 1ш", proc.stdout)


if __name__ == "__main__":
    unittest.main()
