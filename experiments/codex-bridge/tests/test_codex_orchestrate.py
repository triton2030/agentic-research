from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
import types
import unittest
import uuid
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
SCRIPT = BACKEND / "codex_orchestrate.py"
sys.path.insert(0, str(BACKEND))

from codex_orchestrate_contract import (  # noqa: E402
    UsageError,
    codex_turn_completed,
    normalize_tasks,
    path_allowed,
    worker_status_from_codex_status,
)
from codex_run_ledger import (
    append_heartbeat,
    append_jsonl,
    prepare_run_dir,
)
from codex_git_scope import (
    capture_git_snapshot,
    compare_scope,
)


# Предикат retryable берём из настоящего SDK: async-ретрай флота делит с ним
# именно его (backoff у нас свой — async-хелпера SDK не даёт).
try:
    from openai_codex.errors import ServerBusyError, is_retryable_error
except ImportError:  # pragma: no cover — окружение без SDK
    class ServerBusyError(Exception):  # type: ignore[no-redef]
        pass

    def is_retryable_error(exc):  # type: ignore[no-redef] # noqa: ANN001
        return isinstance(exc, ServerBusyError)


def _install_fake_openai_codex(captured: dict, *, start_failures: int = 0) -> list[str]:
    """Put a fake `openai_codex` into sys.modules so the worker's lazy SDK import
    resolves to a stub that records thread_start kwargs instead of launching a
    real Codex process. Returns the module names to pop in teardown.

    `start_failures` — сколько первых thread_start падают transient-перегрузкой."""

    class _Sandbox:
        read_only = "read_only"
        workspace_write = "workspace_write"

    class _ApprovalMode:
        deny_all = "deny_all"
        auto_review = "auto_review"

    def _fake_result():
        return types.SimpleNamespace(
            status="completed", error=None, final_response="done", usage=None
        )

    class _FakeHandle:
        id = "turn-fake-1"

        async def stream(self):
            captured["stream_consumed"] = True
            yield types.SimpleNamespace(
                method="item/completed",
                payload=types.SimpleNamespace(
                    item=types.SimpleNamespace(
                        type="fileChange",
                        changes=[types.SimpleNamespace(path="a.md")],
                    )
                ),
            )
            yield types.SimpleNamespace(
                method="turn/completed", payload=types.SimpleNamespace()
            )

        async def run(self):
            captured["handle_run_fallback"] = True
            return _fake_result()

    class _FakeThread:
        async def turn(self, prompt, **kwargs):  # noqa: ANN001
            captured["run_prompt"] = prompt
            captured["run_kwargs"] = dict(kwargs)
            return _FakeHandle()

        async def run(self, prompt, **kwargs):  # noqa: ANN001
            captured["run_prompt"] = prompt
            captured["run_kwargs"] = dict(kwargs)
            return _fake_result()

    class _FakeCodex:
        async def thread_start(self, **kwargs):  # noqa: ANN003
            captured["thread_start_attempts"] = captured.get("thread_start_attempts", 0) + 1
            if captured["thread_start_attempts"] <= start_failures:
                raise ServerBusyError(-32000, "server overloaded", "server_overloaded")
            captured.update(kwargs)
            return _FakeThread()

    class _CodexConfig:
        def __init__(self, **kwargs):  # noqa: ANN003
            self.kwargs = kwargs
            captured["codex_config"] = kwargs

    class _AsyncCodex:
        def __init__(self, config=None):  # noqa: ANN001
            self.config = config

        async def __aenter__(self):
            return _FakeCodex()

        async def __aexit__(self, *exc):  # noqa: ANN002
            return False

    mod = types.ModuleType("openai_codex")
    mod.Sandbox = _Sandbox
    mod.ApprovalMode = _ApprovalMode
    mod.FakeCodex = _FakeCodex
    mod.CodexConfig = _CodexConfig
    mod.AsyncCodex = _AsyncCodex
    mod.is_retryable_error = is_retryable_error
    gen = types.ModuleType("openai_codex.generated")
    v2 = types.ModuleType("openai_codex.generated.v2_all")
    v2.ReasoningEffort = lambda value: value
    gen.v2_all = v2

    async def _collect_async(stream, *, turn_id):  # noqa: ANN001 — сигнатура SDK
        collected = []
        async for event in stream:
            collected.append(getattr(event, "method", None))
        captured["collected"] = collected
        return _fake_result()

    run_mod = types.ModuleType("openai_codex._run")
    run_mod._collect_async_turn_result = _collect_async
    run_mod._collect_turn_result = _collect_async
    sys.modules["openai_codex._run"] = run_mod
    names = [
        "openai_codex",
        "openai_codex.generated",
        "openai_codex.generated.v2_all",
        "openai_codex._run",
    ]
    sys.modules["openai_codex"] = mod
    sys.modules["openai_codex.generated"] = gen
    sys.modules["openai_codex.generated.v2_all"] = v2
    return names


def run_cli(
    project: Path,
    tasks: object,
    *args: str,
    dry_run: bool = True,
) -> subprocess.CompletedProcess[str]:
    run_dir = project / ".runs" / uuid.uuid4().hex
    command = [
        sys.executable,
        str(SCRIPT),
        "--project",
        str(project),
        "--run-dir",
        str(run_dir),
    ]
    if dry_run:
        command.append("--dry-run")
    command.extend(args)
    return subprocess.run(
        command,
        input=json.dumps(tasks),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(project: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=project, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class CodexOrchestrateCliTests(unittest.TestCase):
    def temp_project(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory()

    def write(self, root: Path, rel: str, text: str = "x\n") -> None:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def init_repo(self, root: Path) -> None:
        git(root, "init")
        git(root, "config", "user.email", "test@example.com")
        git(root, "config", "user.name", "Test User")

    def test_valid_task_dry_run(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"id": "t1", "prompt": "touch a", "files": ["a.md"]}])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload["git"]["available"])
            self.assertEqual(payload["tasks"][0]["files"], ["a.md"])
            self.assertEqual(payload["codex"]["model"], "gpt-5.6-sol")
            self.assertEqual(payload["codex"]["effort"], "xhigh")
            self.assertIsNone(payload["codex"]["service_tier"])
            self.assertEqual(payload["codex"]["worker_sandbox"], "workspace_write")
            self.assertEqual(payload["codex"]["worker_approval_mode"], "auto_review")
            self.assertTrue(payload["codex"]["thread_ephemeral"])
            # Значение зависит от машины (есть ли ChatGPT.app) — контракт в том,
            # что dry-run ledger вообще фиксирует источник движка.
            self.assertIn(
                payload["codex"]["binary_source"], ("chatgpt-app", "sdk-bundle")
            )
            self.assertIn("binary=", proc.stderr)

    def test_summary_stdout_is_compact_but_result_json_keeps_plan(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(
                root,
                [{"id": "t1", "prompt": "touch a", "files": ["a.md"]}],
                "--summary-stdout",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["status"], "validated")
            self.assertEqual(payload["task_count"], 1)
            self.assertNotIn("tasks", payload)
            self.assertNotIn("results", payload)

            result_path = Path(payload["paths"]["result"])
            full = json.loads(result_path.read_text())
            self.assertEqual(full["tasks"][0]["id"], "t1")

    def test_model_and_effort_overrides_are_recorded(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(
                root,
                [{"prompt": "x", "files": ["a.md"]}],
                "--model",
                "gpt-5.4",
                "--effort",
                "high",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["codex"]["model"], "gpt-5.4")
            self.assertEqual(payload["codex"]["effort"], "high")

    def test_invalid_effort_rejected_before_codex(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"prompt": "x", "files": ["a.md"]}], "--effort", "extreme")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("invalid choice", proc.stderr)

    def test_heartbeat_zero_does_not_emit_dry_run_heartbeat(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"prompt": "x", "files": ["a.md"]}], "--heartbeat-sec", "0")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            events = Path(payload["run_dir"], "events.jsonl").read_text()
            self.assertNotIn('"event": "heartbeat"', events)

    def test_append_heartbeat_records_progress_without_sleeping(self) -> None:
        with self.temp_project() as tmp:
            run_dir = Path(tmp)
            append_heartbeat(run_dir, 0.0, completed=2, total=5)
            event = json.loads((run_dir / "events.jsonl").read_text())
            self.assertEqual(event["event"], "heartbeat")
            self.assertEqual(event["completed"], 2)
            self.assertEqual(event["total"], 5)
            self.assertIsInstance(event["elapsed_sec"], int)

    def test_overlapping_files_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "same.md")
            tasks = [
                {"id": "a", "prompt": "x", "files": ["same.md"]},
                {"id": "b", "prompt": "y", "files": ["same.md"]},
            ]
            proc = run_cli(root, tasks)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("overlap", proc.stderr)

    def test_files_required_and_list(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            cases = [
                [{"prompt": "x"}],
                [{"prompt": "x", "files": "a.md"}],
                [{"prompt": "x", "files": []}],
            ]
            for tasks in cases:
                with self.subTest(tasks=tasks):
                    proc = run_cli(root, tasks)
                    self.assertEqual(proc.returncode, 2)
                    self.assertIn("files", proc.stderr)

    def test_absolute_and_parent_paths_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            cases = [
                [{"prompt": "x", "files": ["/tmp/outside.md"]}],
                [{"prompt": "x", "files": ["../escape.md"]}],
            ]
            for tasks in cases:
                with self.subTest(tasks=tasks):
                    proc = run_cli(root, tasks)
                    self.assertEqual(proc.returncode, 2)

    def test_unknown_cwd_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"prompt": "x", "files": ["a.md"], "cwd": "/tmp"}])
            self.assertEqual(proc.returncode, 2)
            self.assertIn("unsupported keys", proc.stderr)

    def test_concurrency_zero_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            proc = run_cli(root, [{"prompt": "x", "files": ["a.md"]}], "--concurrency", "0")
            self.assertEqual(proc.returncode, 2)
            self.assertIn("concurrency", proc.stderr)

    def test_strict_optional_fields_rejected(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.write(root, "a.md")
            cases = [
                ([{"prompt": "x", "files": ["a.md"], "allow_create": "false"}], "allow_create"),
                ([{"prompt": "x", "files": ["a.md"], "allow_create": 1}], "allow_create"),
                ([{"id": [], "prompt": "x", "files": ["a.md"]}], "id"),
            ]
            for tasks, needle in cases:
                with self.subTest(tasks=tasks):
                    proc = run_cli(root, tasks)
                    self.assertEqual(proc.returncode, 2)
                    self.assertIn(needle, proc.stderr)

    def test_dirty_overlap_rejected_and_non_overlap_allowed(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            self.write(root, "target.md", "clean\n")
            self.write(root, "other.md", "clean\n")
            git(root, "add", ".")
            git(root, "commit", "-m", "init")

            self.write(root, "target.md", "dirty\n")
            proc = run_cli(root, [{"prompt": "x", "files": ["target.md"]}])
            self.assertEqual(proc.returncode, 2)
            self.assertIn("Dirty files overlap", proc.stderr)

            proc = run_cli(root, [{"prompt": "x", "files": ["other.md"]}])
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_allow_create_allows_missing_file(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            proc = run_cli(root, [{"prompt": "create", "files": ["new.md"], "allow_create": True}])
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_git_snapshot_required_rejects_non_git_project(self) -> None:
        with self.temp_project() as tmp:
            with self.assertRaises(UsageError):
                capture_git_snapshot(Path(tmp), required=True)

    def test_dirty_snapshot_detects_changed_non_overlap_dirty_file(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            self.write(root, "target.md", "clean\n")
            self.write(root, "other.md", "clean\n")
            git(root, "add", ".")
            git(root, "commit", "-m", "init")

            self.write(root, "other.md", "dirty-before\n")
            before = capture_git_snapshot(root, required=True)
            self.write(root, "other.md", "dirty-after\n")
            after = capture_git_snapshot(root, required=True)
            scope = compare_scope(before, after, {"target.md"})

            self.assertEqual(scope.out_of_scope_files, ("other.md",))
            self.assertFalse(scope.passed)

    def test_file_allowlist_is_exact_not_prefix(self) -> None:
        self.assertTrue(path_allowed("new.md", {"new.md"}))
        self.assertFalse(path_allowed("new.md/child.md", {"new.md"}))

    def test_dirty_paths_are_nul_safe_for_spaces_and_unicode(self) -> None:
        with self.temp_project() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            self.write(root, "space name.md", "clean\n")
            self.write(root, "тест.md", "clean\n")
            git(root, "add", ".")
            git(root, "commit", "-m", "init")

            self.write(root, "space name.md", "dirty\n")
            self.write(root, "тест.md", "dirty\n")
            snapshot = capture_git_snapshot(root, required=True)

            self.assertIn("space name.md", snapshot.dirty_files)
            self.assertIn("тест.md", snapshot.dirty_files)

    def test_worker_status_requires_exact_completed(self) -> None:
        self.assertTrue(codex_turn_completed("completed", None))
        self.assertFalse(codex_turn_completed("interrupted", None))
        self.assertFalse(codex_turn_completed("inProgress", None))
        self.assertFalse(codex_turn_completed("completed", "late error"))
        self.assertEqual(worker_status_from_codex_status("completed", None), "completed")
        self.assertEqual(worker_status_from_codex_status("not_completed", None), "failed")
        self.assertEqual(worker_status_from_codex_status("partially_completed", None), "failed")

    def test_run_dir_must_be_fresh(self) -> None:
        with self.temp_project() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            with self.assertRaises(UsageError):
                prepare_run_dir(str(run_dir))

    def test_worker_thread_start_passes_ephemeral(self) -> None:
        """SDK call contract: workers must start threads ephemerally so bridge
        runs never materialize into the shared ~/.codex session store."""
        import codex_orchestrate

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        try:
            with self.temp_project() as tmp:
                root = Path(tmp).resolve()  # CLI resolves --project; match it (macOS /tmp symlink)
                self.write(root, "a.md")
                tasks = normalize_tasks(root, [{"id": "t1", "prompt": "hi", "files": ["a.md"]}])
                run_dir = root / "run"
                run_dir.mkdir()
                defaults = {
                    "cwd": str(root),
                    "model": "gpt-5.6-sol",
                    "effort": "high",
                    "service_tier": None,
                    "run_dir": run_dir,
                    "progress": {"completed": 0, "total": 1},
                }
                fake_codex = sys.modules["openai_codex"].FakeCodex()
                record = asyncio.run(
                    codex_orchestrate._run_one(
                        fake_codex, asyncio.Semaphore(1), tasks[0], defaults
                    )
                )
            self.assertIs(captured.get("ephemeral"), True)
            self.assertEqual(captured.get("sandbox"), "workspace_write")
            self.assertIsNone(captured.get("service_tier"))
            self.assertIsNone((captured.get("run_kwargs") or {}).get("service_tier"))
            self.assertEqual(record["worker_status"], "completed")
        finally:
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_files_contract_travels_developer_channel(self) -> None:
        """Файловый allowlist — политика треда, а не задание: он уходит
        developer_instructions при thread_start, а воркер получает репликой
        чистый task.prompt. Enforcement остаётся в preflight/postflight."""
        import codex_orchestrate

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        try:
            with self.temp_project() as tmp:
                root = Path(tmp).resolve()
                self.write(root, "a.md")
                tasks = normalize_tasks(root, [{"id": "t1", "prompt": "перепиши шапку", "files": ["a.md"]}])
                run_dir = root / "run"
                run_dir.mkdir()
                defaults = {
                    "cwd": str(root),
                    "model": "gpt-5.6-sol",
                    "effort": "high",
                    "service_tier": None,
                    "run_dir": run_dir,
                    "progress": {"completed": 0, "total": 1},
                }
                fake_codex = sys.modules["openai_codex"].FakeCodex()
                asyncio.run(
                    codex_orchestrate._run_one(
                        fake_codex, asyncio.Semaphore(1), tasks[0], defaults
                    )
                )
            dev = captured.get("developer_instructions") or ""
            self.assertIn("ТОЛЬКО эти файлы: a.md", dev)
            self.assertEqual(captured.get("run_prompt"), "перепиши шапку")
        finally:
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_manifest_records_exact_developer_instructions_sent_to_worker(self) -> None:
        """Аудит-инвариант run_dir: инструкция, ушедшая мимо реплики (канал
        developer_instructions), обязана лежать в manifest дословно и до
        первого хода — иначе после правки backend-кода нельзя восстановить,
        что воркер реально получил. Сверяем текст из dry-run manifest с тем,
        что перехватил фейковый thread_start на том же задании."""
        import codex_orchestrate

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        raw_task = {"id": "t1", "prompt": "перепиши шапку", "files": ["a.md"]}
        try:
            with self.temp_project() as tmp:
                root = Path(tmp).resolve()
                self.write(root, "a.md")

                proc = run_cli(root, [raw_task])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                payload = json.loads(proc.stdout)
                manifest = json.loads(Path(payload["paths"]["manifest"]).read_text())

                tasks = normalize_tasks(root, [raw_task])
                run_dir = root / "run"
                run_dir.mkdir()
                defaults = {
                    "cwd": str(root),
                    "model": "gpt-5.6-sol",
                    "effort": "high",
                    "service_tier": None,
                    "run_dir": run_dir,
                    "progress": {"completed": 0, "total": 1},
                }
                fake_codex = sys.modules["openai_codex"].FakeCodex()
                asyncio.run(
                    codex_orchestrate._run_one(
                        fake_codex, asyncio.Semaphore(1), tasks[0], defaults
                    )
                )

            sent = captured["developer_instructions"]
            record = manifest["tasks"][0]
            self.assertEqual(record["id"], "t1")
            self.assertEqual(record["developer_instructions"], sent)
            self.assertEqual(record["developer_instructions_chars"], len(sent))
            # dry-run фиксирует план целиком: result.json не беднее manifest.
            self.assertEqual(payload["tasks"][0], record)
        finally:
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_worker_start_retried_on_transient_overload(self) -> None:
        """Флот стартует N тредов разом и упирается в overload раньше одиночных
        входов: старт воркера обязан переживать transient-ошибку, а повтор —
        оставлять след в ledger с именем воркера."""
        import codex_orchestrate

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured, start_failures=1)
        try:
            with self.temp_project() as tmp:
                root = Path(tmp).resolve()
                self.write(root, "a.md")
                tasks = normalize_tasks(root, [{"id": "t1", "prompt": "hi", "files": ["a.md"]}])
                run_dir = root / "run"
                run_dir.mkdir()
                defaults = {
                    "cwd": str(root),
                    "model": "gpt-5.6-sol",
                    "effort": "high",
                    "service_tier": None,
                    "run_dir": run_dir,
                    "progress": {"completed": 0, "total": 1},
                }
                fake_codex = sys.modules["openai_codex"].FakeCodex()
                record = asyncio.run(
                    codex_orchestrate._run_one(
                        fake_codex, asyncio.Semaphore(1), tasks[0], defaults
                    )
                )
                events = [
                    json.loads(line)
                    for line in (run_dir / "events.jsonl").read_text().splitlines()
                ]
            self.assertEqual(record["worker_status"], "completed")
            self.assertEqual(captured.get("thread_start_attempts"), 2)
            retries = [e for e in events if e.get("event") == "retry"]
            self.assertEqual(len(retries), 1)
            self.assertEqual(retries[0]["operation"], "thread_start")
            self.assertEqual(retries[0]["worker"], "t1")
        finally:
            for name in fake_names:
                sys.modules.pop(name, None)

    def test_run_fleet_passes_codex_bin_to_codex_config(self) -> None:
        """SDK call contract: the fleet must launch Codex with the binary chosen
        by resolve_codex_bin(); losing it silently reverts to the stale SDK
        bundle that rejects the default model."""
        import codex_orchestrate

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        try:
            with self.temp_project() as tmp:
                root = Path(tmp).resolve()
                self.write(root, "a.md")
                tasks = normalize_tasks(root, [{"id": "t1", "prompt": "hi", "files": ["a.md"]}])
                run_dir = root / "run"
                run_dir.mkdir()
                defaults = {
                    "cwd": str(root),
                    "model": "gpt-5.6-sol",
                    "effort": "high",
                    "service_tier": None,
                    "run_dir": run_dir,
                    "codex_bin": "/fake/chatgpt/codex",
                }
                results = asyncio.run(
                    codex_orchestrate._run_fleet(tasks, defaults, concurrency=1, heartbeat_sec=0)
                )
            self.assertEqual(results[0]["worker_status"], "completed")
            self.assertEqual(
                captured["codex_config"].get("codex_bin"), "/fake/chatgpt/codex"
            )
            self.assertNotIn(
                "features.fast_mode=true",
                captured["codex_config"].get("config_overrides") or (),
            )
        finally:
            for name in fake_names:
                sys.modules.pop(name, None)


class TelemetryResilienceTest(unittest.TestCase):
    """Телеметрия (журнал, прогресс-принты) не имеет права ронять флот:
    реальные случаи — чужой cleanup _workspace во время прогона (md-tools)
    и закрытый пайп (… 2>&1 | head -1)."""

    def test_append_jsonl_recreates_deleted_run_dir(self):
        import shutil

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            run_dir.mkdir()
            path = run_dir / "events.jsonl"
            append_jsonl(path, {"event": "one"})
            shutil.rmtree(run_dir)
            append_jsonl(path, {"event": "two"})  # не должно поднять OSError
            lines = path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(json.loads(lines[-1])["event"], "two")

    def test_append_jsonl_swallows_unrecoverable_oserror(self):
        with tempfile.TemporaryDirectory() as td:
            blocker = Path(td) / "blocker"
            blocker.write_text("", encoding="utf-8")
            # mkdir родителя невозможен: на его месте файл
            append_jsonl(blocker / "sub" / "events.jsonl", {"event": "x"})

    def test_safe_print_survives_closed_pipe(self):
        import os

        import codex_orchestrate

        read_fd, write_fd = os.pipe()
        os.close(read_fd)
        stream = os.fdopen(write_fd, "w", buffering=1)
        try:
            codex_orchestrate._safe_print("hello", stream=stream)  # не должно поднять
        finally:
            try:
                stream.close()
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
