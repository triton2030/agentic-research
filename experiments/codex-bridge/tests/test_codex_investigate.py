from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import types
import unittest
import uuid
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


def _install_fake_openai_codex(captured: dict) -> list[str]:
    """Stub `openai_codex` in sys.modules so main()'s lazy SDK import resolves to
    a fake that records thread_start/CodexConfig kwargs instead of launching a
    real Codex."""

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
                final_response="INVESTIGATE-OK",
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
            captured["codex_config"] = kwargs

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


class CodexInvestigateSdkContractTests(unittest.TestCase):
    def test_thread_start_ephemeral_and_codex_bin_recorded(self) -> None:
        """SDK call contract: the investigator starts its thread ephemerally,
        launches Codex with the resolve_codex_bin() engine, and the ledger
        records which binary source served the run."""
        import codex_investigate
        from codex_defaults import codex_bin_source, resolve_codex_bin

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        billing_keys = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")
        saved_env = {key: os.environ.get(key) for key in billing_keys}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                run_dir = root / ".runs" / uuid.uuid4().hex
                sys.argv = [
                    "codex_investigate.py",
                    "--task", "изучи проект и собери отчёт",
                    "--project", str(root),
                    "--run-dir", str(run_dir),
                    "--heartbeat-sec", "0",
                ]
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = codex_investigate.main()
                result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
            self.assertEqual(rc, 0)
            self.assertIs(captured.get("ephemeral"), True)
            self.assertEqual(captured.get("sandbox"), "workspace_write")
            expected_bin = resolve_codex_bin()
            self.assertEqual(captured["codex_config"].get("codex_bin"), expected_bin)
            self.assertEqual(result["codex"]["codex_bin"], expected_bin)
            self.assertEqual(
                result["codex"]["binary_source"], codex_bin_source(expected_bin)
            )
            self.assertIn("INVESTIGATE-OK", buf.getvalue())
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
