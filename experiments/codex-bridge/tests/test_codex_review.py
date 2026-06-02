from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
SCRIPT = BACKEND / "codex_review.py"


def write_transcript(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "type": "user",
                "message": {"content": "Проверь мост Codex."},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def run_review(
    project: Path,
    transcript: Path,
    *args: str,
    run_dir: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    if run_dir is None:
        run_dir = project / ".runs" / uuid.uuid4().hex
    command = [
        sys.executable,
        str(SCRIPT),
        "--mode",
        "ask",
        "--question",
        "dry run?",
        "--project",
        str(project),
        "--transcript",
        str(transcript),
        "--dry-run",
        "--run-dir",
        str(run_dir),
        *args,
    ]
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class CodexReviewCliTests(unittest.TestCase):
    def test_dry_run_summary_stdout_writes_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = root / "session.jsonl"
            write_transcript(transcript)

            proc = run_review(root, transcript, "--summary-stdout")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)

            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["status"], "validated")
            self.assertEqual(payload["mode"], "ask")
            self.assertEqual(payload["codex"]["model"], "gpt-5.5")
            self.assertEqual(payload["codex"]["effort"], "xhigh")
            self.assertNotIn("final_response", payload)

            paths = payload["paths"]
            self.assertTrue(Path(paths["manifest"]).exists())
            self.assertTrue(Path(paths["events"]).exists())
            self.assertTrue(Path(paths["prompt"]).exists())
            self.assertTrue(Path(paths["result"]).exists())
            self.assertIn("dry run?", Path(paths["prompt"]).read_text())

            full = json.loads(Path(paths["result"]).read_text())
            self.assertEqual(full["prompt_chars"], payload["prompt_chars"])

    def test_existing_run_dir_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = root / "session.jsonl"
            write_transcript(transcript)
            run_dir = root / "existing"
            run_dir.mkdir()

            proc = run_review(root, transcript, "--summary-stdout", run_dir=run_dir)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Run dir already exists", proc.stderr)


if __name__ == "__main__":
    unittest.main()
