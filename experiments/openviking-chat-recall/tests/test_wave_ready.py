from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "experiments/openviking-chat-recall/scripts/wave_ready.py"


class WaveReadyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.tasks = self.root / "tasks"
        self.runs = self.root / "runs"
        self.good = self.root / "good"
        for folder in (self.tasks, self.runs, self.good):
            folder.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_task(self, name: str) -> None:
        (self.tasks / f"{name}.txt").write_text("task\n", encoding="utf-8")

    @staticmethod
    def write_answer(folder: Path, name: str, *, ok: bool = True, response: str | None = None) -> None:
        payload = {"ok": ok, "response": response or ("accepted answer " * 80)}
        (folder / f"{name}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def run_checker(self, *args: Path | str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *(str(arg) for arg in args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_empty_task_set_fails_closed(self) -> None:
        result = self.run_checker(self.tasks, self.runs)

        self.assertEqual(result.returncode, 1)
        self.assertIn("готово: 0 из 0", result.stdout)

    def test_partial_wave_with_missing_answer_fails_closed(self) -> None:
        self.write_task("alpha")
        self.write_task("beta")
        self.write_answer(self.runs, "alpha")

        result = self.run_checker(self.tasks, self.runs)

        self.assertEqual(result.returncode, 1)
        self.assertIn("готово: 1 из 2", result.stdout)
        self.assertIn("beta: ответа нет", result.stdout)

    def test_refused_answer_fails_closed(self) -> None:
        self.write_task("alpha")
        self.write_answer(self.runs, "alpha", ok=False)

        result = self.run_checker(self.tasks, self.runs)

        self.assertEqual(result.returncode, 1)
        self.assertIn("alpha: прогон не принят обёрткой", result.stdout)

    def test_complete_wave_accepts_runs_good_and_positional_flat(self) -> None:
        names = ("alpha", "beta")
        flat = self.root / "flat"
        flat.mkdir()
        topics = []
        responses: dict[str, str] = {}
        for index, name in enumerate(names, start=1):
            self.write_task(name)
            source = f"2026-01-0{index}-{name}.md"
            phrase = f"Владелец выбрал честный барьер {name}"
            (flat / f"{name}.md").write_text(
                f"---\nsource: {source}\n---\n- {phrase} [L1]\n",
                encoding="utf-8",
            )
            topics.append({"id": name, "files": [f"{name}.md"]})
            responses[name] = (
                f"---\ntopic: {name}\n---\n# {name}\n\n"
                f"- {phrase} [{source}#L1]\n"
                + " Дополнительный контекст сохраняет смысл. " * 40
            )
        (self.root / "topics.json").write_text(
            json.dumps({"topics": topics}), encoding="utf-8"
        )
        self.write_answer(self.runs, "alpha", response=responses["alpha"])
        self.write_answer(self.good, "beta", response=responses["beta"])

        result = self.run_checker(
            self.tasks,
            self.runs,
            self.good,
            f"--flat={flat}",
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("готово: 2 из 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
