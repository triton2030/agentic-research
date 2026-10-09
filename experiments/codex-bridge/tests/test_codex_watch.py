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


class LookJsonTests(unittest.TestCase):
    """`look --json` кормит панель-мод: состояние каждого прогона из его файлов."""

    @staticmethod
    def _run(project: Path, name: str, last_ts: str, result: dict | None = None) -> Path:
        run_dir = project / "_workspace" / "work-artifacts" / "2026-10-09-w" / "agents" / "codex-artifacts" / name
        run_dir.mkdir(parents=True)
        (run_dir / "manifest.json").write_text(json.dumps({
            "codex": {"model": "gpt-6-luna", "effort": "max"}, "runtime": {"heartbeat_sec": 120},
        }), encoding="utf-8")
        (run_dir / "prompt.md").write_text("роль\n===== ЗАДАНИЕ =====\n# Заголовок\nПочинить витрину\n", encoding="utf-8")
        (run_dir / "events.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in [
            {"ts": "2026-01-01T00:00:00+00:00", "event": "codex_start"},
            {"ts": last_ts, "event": "codex", "method": "item/completed", "kind": "agentMessage",
             "detail": "12 симв.: читаю журнал"},
        ]) + "\n", encoding="utf-8")
        if result is not None:
            (run_dir / "result.json").write_text(json.dumps(result), encoding="utf-8")
        return run_dir

    def test_states_and_fields(self) -> None:
        from datetime import datetime, timezone
        import os
        fresh = datetime.now(timezone.utc).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self._run(project, "a-live", fresh)
            self._run(project, "b-lost", "2026-01-01T00:01:00+00:00")
            self._run(project, "c-ok", fresh, {"ok": True})
            old = self._run(project, "d-old", "2026-01-01T00:01:00+00:00", {"ok": False})
            os.utime(old / "result.json", (0, 0))
            self._run(project, "e-stopping", fresh, {"provisional": True})

            data = codex_watch.look_json(project, recent_min=30)
            runs = {r["name"]: r for r in data["runs"]}
            self.assertNotIn("d-old", runs)
            self.assertEqual(runs["a-live"]["state"], "live")
            self.assertEqual(runs["b-lost"]["state"], "lost")
            self.assertEqual(runs["c-ok"]["state"], "ok")
            self.assertEqual(runs["e-stopping"]["state"], "live")
            self.assertEqual(runs["a-live"]["tier"], "gpt-6-luna/max")
            self.assertEqual(runs["a-live"]["task"], "Починить витрину")
            self.assertEqual(runs["a-live"]["last_words"], "читаю журнал")
            self.assertEqual(runs["a-live"]["work"], "2026-10-09-w")
            self.assertIsNone(runs["c-ok"]["quiet_s"])
            self.assertEqual(data["runs"][-1]["name"], "c-ok")  # закончившиеся — после живых

            named = codex_watch.look_json(project, recent_min=30, names=frozenset({"d-old"}))
            self.assertIn("d-old", {r["name"] for r in named["runs"]})  # прогон сессии — за любое время

    def test_story_has_words_thoughts_failures_and_linked_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run(Path(tmp), "s-1", "2026-01-01T00:00:30+00:00", {"ok": True})
            with (run_dir / "events.jsonl").open("a", encoding="utf-8") as f:
                for e in [
                    {"ts": "2026-01-01T00:01:00+00:00", "event": "codex", "method": "item/completed",
                     "kind": "reasoning", "detail": "9 симв.: думаю тут"},
                    {"ts": "2026-01-01T00:01:10+00:00", "event": "codex", "method": "error",
                     "detail": "stream disconnected before completion"},
                ]:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
            (run_dir / "out").mkdir()
            (run_dir / "out" / "report.md").write_text("Вердикт: держится", encoding="utf-8")
            (run_dir / "final.md").write_text(f"[Отчёт]({run_dir / 'out' / 'report.md'})", encoding="utf-8")

            story = codex_watch.story_json(run_dir)
            self.assertEqual([i["kind"] for i in story["items"]], ["words", "thought", "fail"])
            self.assertEqual(story["items"][0], {"t": 30, "kind": "words", "text": "читаю журнал"})
            self.assertIn("обрыв связи", story["items"][2]["text"])
            self.assertEqual(story["report"], "Вердикт: держится")
            self.assertEqual(story["task"], "# Заголовок\nПочинить витрину")
            self.assertEqual(story["state"], "ok")

    def test_story_ignores_links_outside_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = self._run(Path(tmp), "s-2", "2026-01-01T00:00:30+00:00", {"ok": True})
            outside = Path(tmp) / "secret.md"
            outside.write_text("не показывать", encoding="utf-8")
            (run_dir / "final.md").write_text(f"[x]({outside})", encoding="utf-8")
            self.assertEqual(codex_watch.story_json(run_dir)["report"], "")

    def test_cli_prints_json_without_runs_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(BACKEND / "codex_watch.py"), "look", "--json", tmp],
                capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(json.loads(proc.stdout)["runs"], [])


if __name__ == "__main__":
    unittest.main()
