from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import codex_progress  # noqa: E402


def _events(run_dir: Path) -> list[dict]:
    path = run_dir / "events.jsonl"
    if not path.is_file():
        return []
    return [json.loads(row) for row in path.read_text(encoding="utf-8").splitlines() if row]


class _FakeHandle:
    """Ручка хода: помнит доставленные реплики, умеет отказывать как движок."""

    def __init__(self, error: Exception | None = None) -> None:
        self.delivered: list[str] = []
        self._error = error

    def steer(self, text: str):  # noqa: ANN201
        if self._error is not None:
            raise self._error
        self.delivered.append(text)
        return type("Resp", (), {"turn_id": "turn-1"})()


class InboxTests(unittest.TestCase):
    def test_request_lands_in_inbox_and_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            request = codex_progress.file_steer_request(run_dir, "вернись к цели")
            inbox = (run_dir / codex_progress.CONTROL_INBOX_NAME).read_text(encoding="utf-8")
            self.assertIn("вернись к цели", inbox)
            kinds = [event.get("event") for event in _events(run_dir)]
            self.assertIn("steer_requested", kinds)
            self.assertTrue(request["id"])

    def test_pending_is_addressed_and_read_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            codex_progress.file_steer_request(run_dir, "всем", worker=None)
            codex_progress.file_steer_request(run_dir, "воркеру t1", worker="t1")

            solo = codex_progress._ControlInbox(run_dir)
            first = solo.pending()
            self.assertEqual([item["text"] for item in first], ["всем"])
            # Реплика читается один раз: иначе сторож слал бы её каждый круг.
            self.assertEqual(solo.pending(), [])

            worker = codex_progress._ControlInbox(run_dir, "t1")
            self.assertEqual([item["text"] for item in worker.pending()], ["воркеру t1"])

    def test_broken_line_does_not_break_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            codex_progress.file_steer_request(run_dir, "живая реплика")
            with (run_dir / codex_progress.CONTROL_INBOX_NAME).open("a", encoding="utf-8") as fh:
                fh.write("{не json\n")
            self.assertEqual(
                [item["text"] for item in codex_progress._ControlInbox(run_dir).pending()],
                ["живая реплика"],
            )


class WatcherTests(unittest.TestCase):
    def _run_watcher(self, handle: _FakeHandle, run_dir: Path) -> None:
        original = codex_progress.CONTROL_POLL_SEC
        codex_progress.CONTROL_POLL_SEC = 0.01
        try:
            with codex_progress._ControlWatcher(handle, run_dir):
                deadline = time.monotonic() + 2.0
                while time.monotonic() < deadline:
                    if [e for e in _events(run_dir) if e.get("event", "").startswith("steer_a")]:
                        break
                    if [e for e in _events(run_dir) if e.get("event") == "steer_rejected"]:
                        break
                    time.sleep(0.01)
        finally:
            codex_progress.CONTROL_POLL_SEC = original

    def test_watcher_delivers_and_records_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            handle = _FakeHandle()
            codex_progress.file_steer_request(run_dir, "хватит читать, отвечай")
            self._run_watcher(handle, run_dir)
            self.assertEqual(handle.delivered, ["хватит читать, отвечай"])
            accepted = [e for e in _events(run_dir) if e.get("event") == "steer_accepted"]
            self.assertEqual(len(accepted), 1)
            self.assertEqual(accepted[0]["turn_id"], "turn-1")
            # `applied` не существует: движок подтверждает приём, не смену курса.
            self.assertEqual([e for e in _events(run_dir) if e.get("event") == "steer_applied"], [])

    def test_engine_refusal_is_recorded_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            handle = _FakeHandle(error=RuntimeError("activeTurnNotSteerable"))
            codex_progress.file_steer_request(run_dir, "поздно")
            self._run_watcher(handle, run_dir)
            rejected = [e for e in _events(run_dir) if e.get("event") == "steer_rejected"]
            self.assertEqual(len(rejected), 1)
            self.assertIn("activeTurnNotSteerable", rejected[0]["error"])

    def test_watcher_without_run_dir_is_inert(self) -> None:
        handle = _FakeHandle()
        with codex_progress._ControlWatcher(handle, None):
            time.sleep(0.02)
        self.assertEqual(handle.delivered, [])


class SteerCliTests(unittest.TestCase):
    def _cli(self, *args) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = codex_progress._steer_cli(*args)
        return code, buffer.getvalue()

    def test_refuses_finished_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "result.json").write_text("{}", encoding="utf-8")
            code, out = self._cli(run_dir, "поздно", None)
            self.assertEqual(code, 2)
            self.assertIn("закончен", out)
            self.assertFalse((run_dir / codex_progress.CONTROL_INBOX_NAME).exists())

    def test_wave_requires_named_worker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "manifest.json").write_text(
                json.dumps({"tasks": [{"id": "t1"}, {"id": "t2"}]}), encoding="utf-8"
            )
            code, out = self._cli(run_dir, "поправка", None)
            self.assertEqual(code, 2)
            self.assertIn("t1", out)
            code, _ = self._cli(run_dir, "поправка", "t1")
            self.assertEqual(code, 0)

    def test_missing_run_dir_fails_cleanly(self) -> None:
        code, out = self._cli(Path("/nope/never"), "текст", None)
        self.assertEqual(code, 2)
        self.assertIn("нет такого прогона", out)


class TaskLineTests(unittest.TestCase):
    def test_goal_heading_wins_over_service_frame(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "prompt.md").write_text(
                "Не вызывай инструменты claude-mcp.\n\n# Цель\n\nСобрать карту зависимостей.\n",
                encoding="utf-8",
            )
            self.assertEqual(codex_progress._task_line(run_dir), "Собрать карту зависимостей.")

    def test_falls_back_to_first_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "prompt.md").write_text("Проверь ссылки в README.\n", encoding="utf-8")
            self.assertEqual(codex_progress._task_line(run_dir), "Проверь ссылки в README.")

    def test_wave_shows_workers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "manifest.json").write_text(
                json.dumps({"tasks": [{"id": "t1"}, {"id": "t2"}]}), encoding="utf-8"
            )
            self.assertIn("2 воркеров", codex_progress._task_line(run_dir))

    def test_digest_shows_task_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "prompt.md").write_text("# Цель\nПочинить сборку.\n", encoding="utf-8")
            self.assertIn("задание: Починить сборку.", codex_progress.digest(run_dir))


if __name__ == "__main__":
    unittest.main()
