"""codex_launch.py: короткая команда, витрина в stdout, владение остановкой."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]

FAKE_BRIDGE = textwrap.dedent(
    """
    import json, signal, sys, time
    from pathlib import Path
    args = sys.argv[1:]
    run_dir = Path(args[args.index("--run-dir") + 1])
    prompt = args[0] if not args[0].startswith("--") else ""
    run_dir.mkdir(parents=True)
    (run_dir / "prompt.md").write_text("===== ЗАДАНИЕ =====\\n" + prompt, encoding="utf-8")
    (run_dir / "manifest.json").write_text(json.dumps({"codex": {"model": "m", "effort": "e"}}))
    ev = run_dir / "events.jsonl"
    def line(**kw):
        with ev.open("a") as f: f.write(json.dumps({"ts": "2026-01-01T00:00:00+00:00", **kw}, ensure_ascii=False) + "\\n")
    line(event="codex_start")
    line(event="codex", method="item/completed", kind="agentMessage", detail="5 симв.: привет")
    line(event="codex", method="item/completed", kind="commandExecution", detail="ls")
    def on_term(*_):
        line(event="interrupt_requested", signal=15)
        (run_dir / "result.json").write_text(json.dumps({"status": "interrupted", "ok": False}))
        line(event="done")
        sys.exit(130)
    signal.signal(signal.SIGTERM, on_term)
    time.sleep(float(sys.argv[sys.argv.index("--sleep") + 1]) if "--sleep" in sys.argv else 0.2)
    (run_dir / "result.json").write_text(json.dumps({"status": "completed", "ok": True}))
    line(event="done")
    print("bridge summary")
    """
)


class LaunchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.fake_backend = self.tmp / "backend"
        self.fake_backend.mkdir()
        (self.fake_backend / "codex_review.py").write_text(FAKE_BRIDGE, encoding="utf-8")
        shutil.copy(BACKEND / "codex_watch.py", self.fake_backend / "codex_watch.py")
        # launcher резолвит соседей через HERE = папка своего файла
        shutil.copy(BACKEND / "codex_launch.py", self.fake_backend / "codex_launch.py")
        self.project = self.tmp / "project"
        self.project.mkdir()
        self.prompt = self.tmp / "task.md"
        self.prompt.write_text("Задание для пробы", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _cmd(self, *extra: str) -> list[str]:
        return [
            sys.executable, str(self.fake_backend / "codex_launch.py"), "review",
            "--name", "probe", "--prompt-file", str(self.prompt),
            "--project", str(self.project), "--poll", "1", *extra,
        ]

    def test_card_shows_header_words_and_finish(self) -> None:
        proc = subprocess.run(self._cmd(), capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = proc.stdout
        self.assertIn("RUN_DIR=", out)
        self.assertIn("m/e", out)  # модель/усилие из манифеста в заголовке
        self.assertIn("Задание для пробы", out)
        self.assertIn("привет", out)  # слова Codex
        self.assertNotIn("ls", out.split("\n", 3)[-1].replace("launch.log", ""))  # команды скрыты
        self.assertRegex(out, r"OK \S+-probe")
        run_dir = Path(out.split("RUN_DIR=", 1)[1].split("\n", 1)[0])
        self.assertTrue((run_dir / "result.json").is_file())
        self.assertIn("bridge summary", Path(f"{run_dir}.launch.log").read_text())

    def test_sigterm_reaches_bridge_and_run_is_interrupted(self) -> None:
        proc = subprocess.Popen(
            self._cmd("--", "--sleep", "30"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        run_dir = None
        deadline = time.time() + 20
        while time.time() < deadline and run_dir is None:
            for d in (self.project / "_workspace" / "codex-artifacts").glob("*-probe"):
                if (d / "events.jsonl").is_file():
                    run_dir = d
            time.sleep(0.2)
        self.assertIsNotNone(run_dir, "прогон не стартовал")
        time.sleep(1.5)
        proc.send_signal(signal.SIGTERM)
        out, _ = proc.communicate(timeout=30)
        events = [json.loads(l) for l in (run_dir / "events.jsonl").read_text().splitlines()]
        self.assertIn("interrupt_requested", [e["event"] for e in events])
        self.assertEqual(json.loads((run_dir / "result.json").read_text())["status"], "interrupted")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ПРОВАЛ", out)

    def test_existing_run_dir_refused(self) -> None:
        stamp_dirs = self.project / "_workspace" / "codex-artifacts"
        stamp_dirs.mkdir(parents=True)
        proc = subprocess.run(
            [sys.executable, str(self.fake_backend / "codex_launch.py"), "orchestrate",
             "--name", "x", "--prompt-file", str(self.prompt), "--project", str(self.project)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("orchestrate не берёт --prompt-file", proc.stderr)


if __name__ == "__main__":
    unittest.main()
