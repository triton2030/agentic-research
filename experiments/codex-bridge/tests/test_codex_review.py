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

# Ретрай-хелперы берём из настоящего SDK: тест проверяет наш контракт с
# первичкой, а не с имитацией её поведения. Без SDK (системный python) —
# минимальное зеркало, чтобы модуль оставался импортируемым.
try:
    from openai_codex.errors import ServerBusyError, is_retryable_error
    from openai_codex.retry import retry_on_overload
except ImportError:  # pragma: no cover — окружение без SDK
    class ServerBusyError(Exception):  # type: ignore[no-redef]
        pass

    def is_retryable_error(exc):  # type: ignore[no-redef] # noqa: ANN001
        return isinstance(exc, ServerBusyError)

    def retry_on_overload(op, *, max_attempts=3, **_kw):  # type: ignore[no-redef] # noqa: ANN001
        for attempt in range(1, max_attempts + 1):
            try:
                return op()
            except Exception as exc:  # noqa: BLE001
                if attempt >= max_attempts or not is_retryable_error(exc):
                    raise


def _overloaded() -> Exception:
    """Ровно та ошибка, на которой SDK разрешает повтор (см. errors.py)."""
    return ServerBusyError(-32000, "server overloaded", "server_overloaded")


def _install_fake_openai_codex(
    captured: dict,
    *,
    status: str = "completed",
    start_failures: int = 0,
) -> list[str]:
    """Stub `openai_codex` in sys.modules so main()'s lazy SDK import resolves to
    a fake that records thread_start kwargs instead of launching a real Codex.

    `start_failures` — сколько первых thread_start падают transient-перегрузкой:
    так проверяется ретрай старта, не трогая потребление потока."""

    class _Sandbox:
        read_only = "read_only"
        workspace_write = "workspace_write"

    class _ApprovalMode:
        deny_all = "deny_all"
        auto_review = "auto_review"

    def _fake_result():
        return types.SimpleNamespace(
            error=None,
            status=status,
            usage=None,
            duration_ms=5,
            final_response="REVIEW-OK",
        )

    def _fake_notification(method, item=None):
        payload = types.SimpleNamespace(item=item) if item is not None else types.SimpleNamespace()
        return types.SimpleNamespace(method=method, payload=payload)

    class _FakeHandle:
        """Модель настоящего TurnHandle: поток нотификаций + control-методы."""

        id = "turn-fake-1"

        def stream(self):
            captured["stream_consumed"] = True
            yield _fake_notification(
                "item/started",
                types.SimpleNamespace(type="commandExecution", command="rg -n probe"),
            )
            yield _fake_notification(
                "item/completed",
                types.SimpleNamespace(type="commandExecution", command="rg -n probe"),
            )
            yield _fake_notification("item/reasoning/textDelta")
            yield _fake_notification("turn/completed")

        def run(self):
            captured["handle_run_fallback"] = True
            return _fake_result()

        def interrupt(self):
            captured["interrupted"] = True

    class _FakeThread:
        id = "thread-fake-1"

        def set_name(self, name):  # noqa: ANN001
            captured["thread_name"] = name

        def turn(self, prompt, **kwargs):  # noqa: ANN001
            captured["run_prompt"] = prompt
            captured["run_kwargs"] = dict(kwargs)
            return _FakeHandle()

        def run(self, prompt, **kwargs):  # noqa: ANN001
            captured["run_prompt"] = prompt
            captured["run_kwargs"] = dict(kwargs)
            return _fake_result()

    class _FakeClient:
        """Сырой RPC-канал: mode=diff зовёт review/start мимо высокого API."""

        def _request_raw(self, method, params=None):  # noqa: ANN001
            captured.setdefault("rpc", []).append((method, params))
            if method == "review/start":
                return {
                    "reviewThreadId": "review-thread-1",
                    "turn": {"id": "turn-fake-1"},
                }
            return {}

    class _FakeCodex:
        def __init__(self, config=None):  # noqa: ANN001
            self.config = config
            self._client = _FakeClient()

        def __enter__(self):
            return self

        def __exit__(self, *exc):  # noqa: ANN002
            return False

        def thread_start(self, **kwargs):  # noqa: ANN003
            captured["thread_start_called"] = True
            captured["thread_start_attempts"] = captured.get("thread_start_attempts", 0) + 1
            if captured["thread_start_attempts"] <= start_failures:
                raise _overloaded()
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

    def _collect(stream, *, turn_id):  # noqa: ANN001 — сигнатура SDK
        captured["collected"] = [getattr(ev, "method", None) for ev in stream]
        captured["collect_turn_id"] = turn_id
        return _fake_result()

    async def _collect_async(stream, *, turn_id):  # noqa: ANN001
        collected = []
        async for event in stream:
            collected.append(getattr(event, "method", None))
        captured["collected"] = collected
        captured["collect_turn_id"] = turn_id
        return _fake_result()

    mod = types.ModuleType("openai_codex")
    mod.Sandbox = _Sandbox
    mod.ApprovalMode = _ApprovalMode
    mod.Codex = _FakeCodex
    mod.CodexConfig = _CodexConfig
    # codex_retry берёт хелперы отсюда: без них мост тихо работал бы без ретрая.
    mod.retry_on_overload = retry_on_overload
    mod.is_retryable_error = is_retryable_error
    gen = types.ModuleType("openai_codex.generated")
    v2 = types.ModuleType("openai_codex.generated.v2_all")
    v2.ReasoningEffort = lambda value: value
    gen.v2_all = v2
    # `_run` держит штатные сборщики TurnResult: без него codex_progress уходит
    # в fallback и потоковый путь в тестах не проверялся бы вовсе.
    run_mod = types.ModuleType("openai_codex._run")
    run_mod._collect_turn_result = _collect
    run_mod._collect_async_turn_result = _collect_async
    # `api` нужен ветке mode=diff: она собирает TurnHandle вручную. Без него
    # диф-путь в тестах был бы недостижим — ложное зелёное на новой механике.
    api_mod = types.ModuleType("openai_codex.api")

    class _TurnHandle:
        def __init__(self, client, thread_id, turn_id):  # noqa: ANN001
            captured["handle_args"] = (thread_id, turn_id)
            self.id = turn_id
            self.thread_id = thread_id

        def stream(self):
            return _FakeHandle().stream()

        def run(self):
            captured["handle_run_fallback"] = True
            return _fake_result()

    api_mod.TurnHandle = _TurnHandle
    sys.modules["openai_codex.api"] = api_mod
    names = [
        "openai_codex",
        "openai_codex.generated",
        "openai_codex.generated.v2_all",
        "openai_codex._run",
        "openai_codex.api",
    ]
    sys.modules["openai_codex"] = mod
    sys.modules["openai_codex.generated"] = gen
    sys.modules["openai_codex.generated.v2_all"] = v2
    sys.modules["openai_codex._run"] = run_mod
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
    def test_default_run_auto_creates_project_local_audit_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "Проверь audit owner",
                    "--project",
                    str(root),
                    "--dry-run",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            artifacts_root = root.resolve() / "_workspace" / "codex-artifacts"
            run_dirs = [path for path in artifacts_root.iterdir() if path.is_dir()]
            self.assertEqual(len(run_dirs), 1)
            result = json.loads((run_dirs[0] / "result.json").read_text())
            self.assertEqual(result["run_dir"], str(run_dirs[0]))
            self.assertTrue((run_dirs[0] / "manifest.json").exists())
            self.assertTrue((run_dirs[0] / "events.jsonl").exists())

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
            self.assertEqual(payload["codex"]["effort"], "medium")
            self.assertIsNone(payload["codex"]["service_tier"])
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
                artifacts_root = root / "_workspace" / "codex-artifacts"
                run_dirs = [path for path in artifacts_root.iterdir() if path.is_dir()]
                self.assertEqual(len(run_dirs), 1)
                result = json.loads((run_dirs[0] / "result.json").read_text())
            self.assertEqual(rc, 0)
            self.assertEqual(result["status"], "completed")
            self.assertTrue(result["ok"])
            self.assertIs(captured.get("ephemeral"), True)
            self.assertEqual(captured.get("sandbox"), "read_only")
            self.assertIsNone(captured.get("service_tier"))
            self.assertEqual(
                captured["codex_config"].get("codex_bin"), "/sentinel/chatgpt/codex"
            )
            self.assertNotIn(
                "features.fast_mode=true",
                captured["codex_config"].get("config_overrides") or (),
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
            # Тема уходит в движок, а не только в наш реестр: без имени
            # персистентный тред виден в Desktop и thread/list безымянным.
            self.assertTrue(captured.get("thread_name"))
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
            self.assertIsNone(resume_kwargs.get("service_tier"))
            # Роль уходит повторно СВОИМ каналом: resume её принимает, роль
            # идемпотентна, а вклейка в текст реплики меняла бы рамку на ходу.
            self.assertEqual(
                resume_kwargs.get("developer_instructions"), codex_review.TASK_ROLE
            )
            run_kwargs = captured.get("run_kwargs") or {}
            self.assertEqual(run_kwargs.get("sandbox"), "read_only")
            self.assertEqual(run_kwargs.get("approval_mode"), "deny_all")
            self.assertEqual(run_kwargs.get("model"), "gpt-5.6-sol")
            self.assertEqual(run_kwargs.get("effort"), "medium")
            self.assertIsNone(run_kwargs.get("service_tier"))
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
                registry_lines = [
                    json.loads(line)
                    for line in (
                        Path(tmp) / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
                    ).read_text().splitlines()
                ]
                self.assertEqual(registry_lines[-1]["event"], "continue")
                # усыновлённый foreign-тред получает тему для доски статусов
                self.assertEqual(registry_lines[-1]["topic"], "уточнение")
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_archive_event_does_not_legalize_thread(self) -> None:
        """archive-событие в реестре не даёт provenance: иначе архивация чужого
        треда «легализовала» бы его для --continue без --continue-foreign."""
        import codex_review

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reg = root / "_workspace" / "codex-artifacts" / "dialog-threads.jsonl"
            reg.parent.mkdir(parents=True, exist_ok=True)
            reg.write_text(
                json.dumps({"event": "archive", "thread_id": "t-x"}) + "\n",
                encoding="utf-8",
            )
            self.assertFalse(codex_review._dialog_thread_known(root, "t-x"))
            reg.write_text(
                json.dumps({"event": "continue", "thread_id": "t-y"}) + "\n",
                encoding="utf-8",
            )
            self.assertTrue(codex_review._dialog_thread_known(root, "t-y"))

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
            self.assertIsNone(captured.get("service_tier"))
            self.assertEqual(
                captured["codex_config"].get("codex_bin"), "/sentinel/chatgpt/codex"
            )
            self.assertNotIn(
                "features.fast_mode=true",
                captured["codex_config"].get("config_overrides") or (),
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

    def test_heavy_effort_turns_into_dialog_and_no_dialog_opts_out(self) -> None:
        """Ярусы вызова: тяжёлое усилие — разговор, а не выстрел.

        xhigh/max/ultra долго читают и думают, ценность приходит во втором
        обмене, поэтому такой прогон сам заводит персистентный тред. Дефолтный
        medium остаётся эфемерным одиночным вызовом."""
        import codex_review

        for effort, expect_persistent in (("medium", False), ("xhigh", True), ("max", True)):
            captured: dict = {}
            fake_names = _install_fake_openai_codex(captured)
            saved_argv = sys.argv[:]
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    sys.argv = [
                        "codex_review.py", "--task", "вопрос",
                        "--project", tmp, "--effort", effort,
                    ]
                    with contextlib.redirect_stdout(io.StringIO()):
                        rc = codex_review.main()
                    self.assertEqual(rc, 0, effort)
                    self.assertIs(
                        captured.get("ephemeral"), not expect_persistent, effort
                    )
            finally:
                sys.argv = saved_argv
                for name in fake_names:
                    sys.modules.pop(name, None)

        # --no-dialog возвращает одиночный эфемерный выстрел на том же усилии.
        captured = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                sys.argv = [
                    "codex_review.py", "--task", "вопрос",
                    "--project", tmp, "--effort", "xhigh", "--no-dialog",
                ]
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = codex_review.main()
                self.assertEqual(rc, 0)
                self.assertIs(captured.get("ephemeral"), True)
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_diff_mode_targets(self) -> None:
        """Четыре формы git-таргета для нативного review/start."""
        import types as _t

        from codex_review import _review_target

        def a(**kw):
            return _t.SimpleNamespace(**{"base": None, "commit": None, **kw})

        self.assertEqual(_review_target(a(), None), {"type": "uncommittedChanges"})
        self.assertEqual(
            _review_target(a(base="main"), None), {"type": "baseBranch", "branch": "main"}
        )
        self.assertEqual(
            _review_target(a(commit="abc123"), None), {"type": "commit", "sha": "abc123"}
        )
        # custom принимает инструкции — официальный плагин OpenAI от этого отказывается.
        self.assertEqual(
            _review_target(a(), "смотри только на гонки"),
            {"type": "custom", "instructions": "смотри только на гонки"},
        )
        # Явный таргет сильнее свободного текста.
        self.assertEqual(
            _review_target(a(commit="abc"), "текст"), {"type": "commit", "sha": "abc"}
        )

    def test_diff_mode_calls_native_review_and_reports_inherited_effort(self) -> None:
        """mode=diff идёт через review/start, а не через промпт, и НЕ врёт про effort."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                sys.argv = [
                    "codex_review.py", "--mode", "diff", "--base", "main",
                    "--project", str(root), "--effort", "xhigh",
                ]
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    rc = codex_review.main()
                self.assertEqual(rc, 0)

                rpc = dict((m, p) for m, p in captured.get("rpc", []))
                self.assertIn("review/start", rpc)
                self.assertEqual(rpc["review/start"]["delivery"], "inline")
                self.assertEqual(
                    rpc["review/start"]["target"], {"type": "baseBranch", "branch": "main"}
                )
                # TurnHandle собран на треде ревью и turn id из ответа.
                self.assertEqual(captured["handle_args"], ("review-thread-1", "turn-fake-1"))
                # Промпт в этом режиме не отправляется вовсе.
                self.assertNotIn("run_kwargs", captured)
                # Роли тоже нет: контракт ревью несёт сам движок.
                self.assertIsNone(captured.get("developer_instructions"))

                result = json.loads(
                    next((root / "_workspace" / "codex-artifacts").glob("*/result.json"))
                    .read_text(encoding="utf-8")
                )
                # Ledger обязан говорить правду: усилие наследуется, не применяется.
                self.assertEqual(result["codex"]["effort"], "inherit")
                self.assertIn("НЕ применяется", err.getvalue())
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_turn_activity_lands_in_ledger(self) -> None:
        """Ход обязан идти через turn()+stream(): активность Codex попадает в
        events.jsonl, а не выбрасывается вместе с потоком, как делал run()."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
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
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = codex_review.main()
                self.assertEqual(rc, 0)
                # Поток реально потреблён, а не обойдён через handle.run().
                self.assertIs(captured.get("stream_consumed"), True)
                self.assertNotIn("handle_run_fallback", captured)
                self.assertEqual(captured.get("collect_turn_id"), "turn-fake-1")

                events = [
                    json.loads(line)
                    for line in (
                        next(
                            (root / "_workspace" / "codex-artifacts").glob("*/events.jsonl")
                        )
                    ).read_text(encoding="utf-8").splitlines()
                ]
                activity = [e for e in events if e.get("event") == "codex"]
                methods = {e["method"] for e in activity}
                self.assertIn("item/started", methods)
                self.assertIn("item/completed", methods)
                # Дельты — шум: считаются, но в журнал не пишутся.
                self.assertNotIn("item/reasoning/textDelta", methods)
                completed = next(e for e in activity if e["method"] == "item/completed")
                self.assertEqual(completed.get("kind"), "commandExecution")
                self.assertEqual(completed.get("detail"), "rg -n probe")
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_progress_snapshot_reports_activity_and_idle(self) -> None:
        """Пульс должен говорить «чем занят», а не только «жив»."""
        import types

        from codex_progress import ProgressTracker

        tracker = ProgressTracker()
        self.assertEqual(tracker.snapshot()["steps"], 0)

        item = types.SimpleNamespace(type="fileChange", changes=[
            types.SimpleNamespace(path="a.md"), types.SimpleNamespace(path="b.md"),
        ])
        record = tracker.observe(
            types.SimpleNamespace(
                method="item/completed", payload=types.SimpleNamespace(item=item)
            )
        )
        self.assertEqual(record["kind"], "fileChange")
        self.assertEqual(record["detail"], "a.md, b.md")

        self.assertIsNone(
            tracker.observe(
                types.SimpleNamespace(
                    method="item/reasoning/textDelta", payload=types.SimpleNamespace()
                )
            )
        )
        snap = tracker.snapshot()
        self.assertEqual(snap["steps"], 1)
        self.assertEqual(snap["last"], "fileChange")
        self.assertEqual(snap["deltas"], 1)
        self.assertIn("idle_sec", snap)

    def test_role_travels_developer_channel_not_user_prompt(self) -> None:
        """Инвариантная роль уходит каналом developer_instructions при
        thread_start, а user-промпт остаётся заданием: дубль роли в тексте
        конкурировал бы с заданием за внимание и врал бы про prompt_chars."""
        import codex_review

        cases = (
            ("task", ("--task", "посмотри на codex_review.py"), codex_review.TASK_ROLE),
            ("ask", ("--mode", "ask", "--question", "где дыра?"), codex_review.ASK_ROLE),
        )
        for label, argv_tail, expected_role in cases:
            with self.subTest(mode=label):
                captured: dict = {}
                fake_names = _install_fake_openai_codex(captured)
                saved_argv = sys.argv[:]
                try:
                    with tempfile.TemporaryDirectory() as tmp:
                        root = Path(tmp)
                        transcript = root / "session.jsonl"
                        write_transcript(transcript)
                        sys.argv = [
                            "codex_review.py",
                            "--project", str(root),
                            "--transcript", str(transcript),
                            *argv_tail,
                        ]
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                            io.StringIO()
                        ):
                            rc = codex_review.main()
                        artifacts = root / "_workspace" / "codex-artifacts"
                        run_dir = next(p for p in artifacts.iterdir() if p.is_dir())
                        prompt_md = (run_dir / "prompt.md").read_text(encoding="utf-8")
                        manifest = json.loads((run_dir / "manifest.json").read_text())
                    self.assertEqual(rc, 0)
                    self.assertEqual(
                        captured.get("developer_instructions"), expected_role
                    )
                    user_prompt = captured.get("run_prompt") or ""
                    self.assertNotIn(expected_role, user_prompt)
                    # prompt.md обязан показывать ПОЛНУЮ эффективную инструкцию:
                    # иначе по run_dir не восстановить, что видел Codex.
                    self.assertIn("DEVELOPER INSTRUCTIONS", prompt_md)
                    self.assertIn(expected_role, prompt_md)
                    self.assertIn(user_prompt, prompt_md)
                    self.assertEqual(manifest["prompt_chars"], len(user_prompt))
                    self.assertEqual(
                        manifest["developer_instructions_chars"], len(expected_role)
                    )
                finally:
                    sys.argv = saved_argv
                    for name in fake_names:
                        sys.modules.pop(name, None)

    def test_transient_overload_on_start_is_retried_and_logged(self) -> None:
        """Перегрузка движка на СТАРТЕ теряла оплаченный ход целиком. Ретрай
        обязан быть слышимым: событие `retry` в ledger, а не тихий повтор."""
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured, start_failures=1)
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                sys.argv = [
                    "codex_review.py",
                    "--task", "проверь ретрай",
                    "--project", str(root),
                    "--heartbeat-sec", "0",
                ]
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
                    io.StringIO()
                ):
                    rc = codex_review.main()
                run_dir = next(
                    p for p in (root / "_workspace" / "codex-artifacts").iterdir() if p.is_dir()
                )
                events = [
                    json.loads(line)
                    for line in (run_dir / "events.jsonl").read_text().splitlines()
                ]
            self.assertEqual(rc, 0)
            self.assertEqual(captured.get("thread_start_attempts"), 2)
            retries = [e for e in events if e.get("event") == "retry"]
            self.assertEqual(len(retries), 1)
            self.assertEqual(retries[0]["operation"], "thread_start")
            self.assertEqual(retries[0]["attempt"], 1)
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_non_retryable_start_error_is_not_retried(self) -> None:
        """Ретрай — только на transient-перегрузке: обычная ошибка старта обязана
        падать сразу, иначе мост множит бесполезные попытки на чужих дефектах."""
        import codex_retry

        calls = {"n": 0}

        def op():
            calls["n"] += 1
            raise ValueError("bad params")

        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            fake_names = _install_fake_openai_codex({})
            try:
                with self.assertRaises(ValueError):
                    codex_retry.retry_start(op, run_dir=run_dir, operation="thread_start")
            finally:
                for name in fake_names:
                    sys.modules.pop(name, None)
            self.assertEqual(calls["n"], 1)
            self.assertFalse((run_dir / "events.jsonl").exists())

    def test_interrupted_turn_is_failed_and_recorded(self) -> None:
        import codex_review

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured, status="interrupted")
        saved_argv = sys.argv[:]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                sys.argv = [
                    "codex_review.py",
                    "проверь статус",
                    "--project",
                    str(root),
                    "--heartbeat-sec",
                    "0",
                    "--summary-stdout",
                ]
                out = io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(
                    io.StringIO()
                ), mock.patch.object(
                    codex_review,
                    "resolve_codex_bin",
                    return_value="/sentinel/chatgpt/codex",
                ):
                    rc = codex_review.main()
                payload = json.loads(out.getvalue())
                full = json.loads(Path(payload["paths"]["result"]).read_text())
                events = Path(payload["paths"]["events"]).read_text()
            self.assertEqual(rc, 1)
            self.assertEqual(payload["status"], "interrupted")
            self.assertFalse(payload["ok"])
            self.assertIn("did not complete", full["error"])
            self.assertIn('"event": "failed"', events)
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)


if __name__ == "__main__":
    unittest.main()
