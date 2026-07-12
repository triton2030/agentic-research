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
from unittest import mock


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
        id = "thread-fake-1"

        def run(self, prompt, **kwargs):  # noqa: ANN001
            captured["run_prompt"] = prompt
            captured["run_kwargs"] = dict(kwargs)
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
            captured["thread_start_called"] = True
            captured.update(kwargs)
            return _FakeThread()

        def thread_resume(self, thread_id, **kwargs):  # noqa: ANN001, ANN003
            captured["resumed_thread_id"] = thread_id
            captured["thread_resume_kwargs"] = dict(kwargs)
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


def _seed_dialog_registry(project: Path, thread_id: str) -> None:
    reg = project / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(json.dumps({"thread_id": thread_id}) + "\n", encoding="utf-8")


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
            self.assertEqual(payload["codex"]["model"], "gpt-5.6-sol")
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
                # Sentinel вместо среды: на машине без ChatGPT.app обе стороны
                # сравнения были бы None и потеря kwarg осталась бы зелёной.
                with contextlib.redirect_stdout(buf), mock.patch.object(
                    codex_review, "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
            self.assertEqual(rc, 0)
            self.assertIs(captured.get("ephemeral"), True)
            self.assertEqual(captured.get("sandbox"), "read_only")
            self.assertEqual(
                captured["codex_config"].get("codex_bin"), "/sentinel/chatgpt/codex"
            )
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
    def test_dialog_starts_persistent_thread(self) -> None:
        """--dialog обязан выключить ephemeral (resume работает только по rollout
        на диске) и объявить thread_id в stderr — иначе диалог не продолжить."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                sys.argv = [
                    "codex_review.py",
                    "--task", "вопрос советнику",
                    "--project", tmp,
                    "--dialog",
                ]
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(
                    err
                ), mock.patch.object(
                    codex_review, "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
            self.assertEqual(rc, 0)
            self.assertIs(captured.get("ephemeral"), False)
            self.assertIn("thread_id=thread-fake-1", err.getvalue())
            self.assertIn("--continue thread-fake-1", err.getvalue())
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_continue_resumes_thread_without_role_wrap(self) -> None:
        """--continue должен звать thread_resume с переданным id и слать реплику
        как есть (повторная обёртка TASK_ROLE ломала бы диалог сменой роли), а
        каждый resumed turn обязан заново получить read-only sandbox/approval."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                _seed_dialog_registry(Path(tmp), "thread-abc")
                sys.argv = [
                    "codex_review.py",
                    "--task", "уточни пункт два",
                    "--project", tmp,
                    "--continue", "thread-abc",
                ]
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(
                    io.StringIO()
                ), mock.patch.object(
                    codex_review, "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
                registry_lines = [
                    json.loads(line)
                    for line in (
                        Path(tmp) / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
                    ).read_text().splitlines()
                ]
            self.assertEqual(rc, 0)
            self.assertEqual(captured.get("resumed_thread_id"), "thread-abc")
            self.assertNotIn("thread_start_called", captured)
            self.assertEqual(captured.get("run_prompt"), "уточни пункт два")
            self.assertEqual(registry_lines[-1]["event"], "continue")
            self.assertEqual(registry_lines[-1]["thread_id"], "thread-abc")
            resume_kwargs = captured.get("thread_resume_kwargs") or {}
            self.assertEqual(resume_kwargs.get("sandbox"), "read_only")
            self.assertEqual(resume_kwargs.get("approval_mode"), "deny_all")
            run_kwargs = captured.get("run_kwargs") or {}
            self.assertEqual(run_kwargs.get("sandbox"), "read_only")
            self.assertEqual(run_kwargs.get("approval_mode"), "deny_all")
            self.assertEqual(run_kwargs.get("model"), "gpt-5.6-sol")
            self.assertEqual(run_kwargs.get("effort"), "xhigh")
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_continue_blank_id_fails_closed(self) -> None:
        """Пустой $THREAD_ID молча запускал бы НОВЫЙ ephemeral-тред вместо
        продолжения — потеря контекста без ошибки. Отказ до любых SDK-вызовов."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                for blank in ("", "   "):
                    sys.argv = [
                        "codex_review.py",
                        "--task", "уточнение",
                        "--project", tmp,
                        "--continue", blank,
                    ]
                    err = io.StringIO()
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                        rc = codex_review.main()
                    self.assertEqual(rc, 2)
                    self.assertIn("пустой THREAD_ID", err.getvalue())
            self.assertNotIn("thread_start_called", captured)
            self.assertNotIn("resumed_thread_id", captured)
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_continue_requires_registry_or_explicit_override(self) -> None:
        """Provenance fail-closed: чужой thread_id (не из dialog-threads.jsonl
        проекта) отклоняется; --continue-foreign — осознанный override."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                sys.argv = [
                    "codex_review.py",
                    "--task", "уточнение",
                    "--project", tmp,
                    "--continue", "thread-foreign",
                ]
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    rc = codex_review.main()
                self.assertEqual(rc, 2)
                self.assertIn("реестре диалогов", err.getvalue())
                self.assertNotIn("resumed_thread_id", captured)

                sys.argv.append("--continue-foreign")
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                    io.StringIO()
                ), mock.patch.object(
                    codex_review, "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
                self.assertEqual(rc, 0)
                self.assertEqual(captured.get("resumed_thread_id"), "thread-foreign")
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_dialog_auto_creates_run_dir_and_registers_thread(self) -> None:
        """Персистентный диалог без audit owner запрещён: --dialog обязан сам
        создать project-local run_dir и вписать тред в provenance-реестр."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                sys.argv = [
                    "codex_review.py",
                    "--task", "вопрос советнику",
                    "--project", tmp,
                    "--dialog",
                    "--topic", "дизайн реестра",
                ]
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                    io.StringIO()
                ), mock.patch.object(
                    codex_review, "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
                self.assertEqual(rc, 0)

                artifacts = root / "_workspace" / "codex-artifacts"
                registry = artifacts / "dialog-threads.jsonl"
                self.assertTrue(registry.exists(), "dialog-threads.jsonl не создан")
                entry = json.loads(registry.read_text().splitlines()[0])
                self.assertEqual(entry["thread_id"], "thread-fake-1")
                self.assertEqual(entry["event"], "start")
                self.assertEqual(entry["topic"], "дизайн реестра")

                run_dirs = [p for p in artifacts.iterdir() if p.is_dir()]
                self.assertEqual(len(run_dirs), 1, "авто-run_dir не создан")
                result = json.loads((run_dirs[0] / "result.json").read_text())
                self.assertEqual(result["codex"]["thread_id"], "thread-fake-1")
                self.assertTrue(result["codex"]["thread_persistent"])
                self.assertFalse(result["codex"]["thread_ephemeral"])
                events = (run_dirs[0] / "events.jsonl").read_text()
                self.assertIn('"thread"', events)
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_continue_rejects_transcript_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcript = root / "session.jsonl"
            write_transcript(transcript)
            proc = run_review(root, transcript, "--continue", "thread-abc")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("--continue несовместим", proc.stderr)

            command = [
                sys.executable, str(SCRIPT),
                "--mode", "review",
                "--project", str(root),
                "--transcript", str(transcript),
                "--continue", "thread-abc",
            ]
            proc2 = subprocess.run(
                command, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            )
            self.assertEqual(proc2.returncode, 2)
            self.assertIn("--continue несовместим", proc2.stderr)

    def test_sdk_bundle_fallback_warns_and_lands_in_ledger(self) -> None:
        """Fallback contract: без ChatGPT.app entrypoint предупреждает в stderr,
        а ledger фиксирует codex_bin=None + binary_source=sdk-bundle — тихий
        откат на старый движок оставлял бы ложную runtime-картину."""
        import codex_review
        from codex_defaults import SDK_BUNDLE_WARNING

        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                transcript = root / "session.jsonl"
                write_transcript(transcript)
                run_dir = root / ".runs" / uuid.uuid4().hex
                sys.argv = [
                    "codex_review.py",
                    "--mode", "ask",
                    "--question", "dry?",
                    "--project", str(root),
                    "--transcript", str(transcript),
                    "--dry-run",
                    "--run-dir", str(run_dir),
                    "--summary-stdout",
                ]
                out = io.StringIO()
                err = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(
                    err
                ), mock.patch.object(
                    codex_review, "resolve_codex_bin", return_value=None
                ):
                    rc = codex_review.main()
                result = json.loads(
                    (run_dir / "result.json").read_text(encoding="utf-8")
                )
            self.assertEqual(rc, 0)
            self.assertIn(SDK_BUNDLE_WARNING, err.getvalue())
            self.assertIsNone(result["codex"]["codex_bin"])
            self.assertEqual(result["codex"]["binary_source"], "sdk-bundle")
        finally:
            sys.argv = saved_argv

    def test_task_mode_needs_no_transcript(self) -> None:
        """Режим task (default) не подхватывает транскрипт: вызов проходит даже
        когда .jsonl сессии нет, а собранный prompt не содержит блока транскрипта."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / ".runs" / uuid.uuid4().hex
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "Проверь паттерн ABC в модуле XYZ",
                    "--project",
                    str(root),
                    "--dry-run",
                    "--run-dir",
                    str(run_dir),
                    "--summary-stdout",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["mode"], "task")

            prompt_text = Path(payload["paths"]["prompt"]).read_text()
            self.assertIn("Проверь паттерн ABC", prompt_text)
            self.assertNotIn("ТРАНСКРИПТ", prompt_text)

            manifest = json.loads(Path(payload["paths"]["manifest"]).read_text())
            self.assertIsNone(manifest["transcript"])

    def test_task_mode_requires_a_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--project", str(root), "--dry-run"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("task", proc.stderr.lower())

    def test_task_mode_rejects_blank_task(self) -> None:
        """Задание из одних пробелов truthy, но по смыслу пусто — не должно
        уйти в Codex и сжечь кредиты (нашёл Codex-ревьюер)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "   ", "--project", str(root), "--dry-run"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("task", proc.stderr.lower())

    def test_task_mode_thread_start_ephemeral_readonly(self) -> None:
        """Новый дефолтный режим обязан держать тот же инвариант, что reviewer:
        thread стартует ephemeral + read_only, без всякого транскрипта."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        billing_keys = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")
        saved_env = {key: os.environ.get(key) for key in billing_keys}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                sys.argv = [
                    "codex_review.py",
                    "--task",
                    "посмотри на codex_review.py",
                    "--project",
                    str(root),
                ]
                buf = io.StringIO()
                # Sentinel вместо среды: на машине без ChatGPT.app обе стороны
                # сравнения были бы None и потеря kwarg осталась бы зелёной.
                with contextlib.redirect_stdout(buf), mock.patch.object(
                    codex_review, "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
            self.assertEqual(rc, 0)
            self.assertIs(captured.get("ephemeral"), True)
            self.assertEqual(captured.get("sandbox"), "read_only")
            self.assertEqual(
                captured["codex_config"].get("codex_bin"), "/sentinel/chatgpt/codex"
            )
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
