from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
import uuid
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
SCRIPT = BACKEND / "codex_review.py"
sys.path.insert(0, str(BACKEND))


def _install_fake_openai_codex(captured: dict) -> list[str]:
    """Stub `openai_codex` in sys.modules so main()'s lazy SDK import resolves to
    a fake that records thread_start kwargs instead of launching a real Codex."""

    class _Sandbox:
        read_only = "read_only"
        workspace_write = "workspace_write"

    class _ApprovalMode:
        deny_all = "deny_all"
        auto_review = "auto_review"

    class _FakeThread:
        def run(self, prompt, **kwargs):  # noqa: ANN001
            return types.SimpleNamespace(
                error=None,
                status="completed",
                usage=None,
                duration_ms=5,
                final_response="REVIEW-OK",
            )

    class _FakeCodex:
        def __init__(self, config=None):  # noqa: ANN001
            self.config = config

        def __enter__(self):
            return self

        def __exit__(self, *exc):  # noqa: ANN002
            return False

        def thread_start(self, **kwargs):  # noqa: ANN003
            captured.update(kwargs)
            return _FakeThread()

    class _CodexConfig:
        def __init__(self, **kwargs):  # noqa: ANN003
            self.kwargs = kwargs

    mod = types.ModuleType("openai_codex")
    mod.Sandbox = _Sandbox
    mod.ApprovalMode = _ApprovalMode
    mod.Codex = _FakeCodex
    mod.CodexConfig = _CodexConfig
    gen = types.ModuleType("openai_codex.generated")
    v2 = types.ModuleType("openai_codex.generated.v2_all")
    v2.ReasoningEffort = lambda value: value
    gen.v2_all = v2
    names = ["openai_codex", "openai_codex.generated", "openai_codex.generated.v2_all"]
    sys.modules["openai_codex"] = mod
    sys.modules["openai_codex.generated"] = gen
    sys.modules["openai_codex.generated.v2_all"] = v2
    return names


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
            self.assertTrue(payload["codex"]["thread_ephemeral"])
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

    def test_thread_start_passes_ephemeral(self) -> None:
        """SDK call contract: the reviewer must start its thread ephemerally so a
        review never materializes into the shared ~/.codex session store."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        billing_keys = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")
        saved_env = {key: os.environ.get(key) for key in billing_keys}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                transcript = root / "session.jsonl"
                write_transcript(transcript)
                sys.argv = [
                    "codex_review.py",
                    "--mode", "ask",
                    "--question", "where is the hole?",
                    "--project", str(root),
                    "--transcript", str(transcript),
                ]
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = codex_review.main()
            self.assertEqual(rc, 0)
            self.assertIs(captured.get("ephemeral"), True)
            self.assertEqual(captured.get("sandbox"), "read_only")
            self.assertIn("REVIEW-OK", buf.getvalue())
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
