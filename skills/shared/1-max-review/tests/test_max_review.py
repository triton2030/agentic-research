#!/usr/bin/env python3
"""Behavioral tests for the bounded max-review CLI wrapper."""

from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "portable/scripts/max_review.py"


FAKE_CODEX = r'''#!/usr/bin/env python3
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

if sys.argv[1:] == ["--version"]:
    print("codex-cli fake")
    raise SystemExit(0)
if sys.argv[1:] == ["login", "status"]:
    print(os.environ.get("FAKE_LOGIN_STATUS", "Logged in using ChatGPT"))
    raise SystemExit(int(os.environ.get("FAKE_LOGIN_EXIT", "0")))

state = Path(os.environ["FAKE_STATE"])
state.mkdir(exist_ok=True)
prompt = sys.stdin.read()
identifier = prompt.splitlines()[0]
(state / f"{identifier}.argv.json").write_text(json.dumps(sys.argv))
(state / f"{identifier}.env.json").write_text(json.dumps({
    key: os.environ.get(key) for key in [
        "CODEX_API_KEY", "OPENAI_API_KEY", "CODEX_THREAD_ID",
        "CODEX_SESSION_ID", "CODEX_APP_TOOLS_PIPE_PATH", "CODEX_PERMISSION_PROFILE"
    ]
}))
count_path = state / f"{identifier}.count"
count = int(count_path.read_text()) + 1 if count_path.exists() else 1
count_path.write_text(str(count))

lock = state / "counter.lock"
with lock.open("a+") as stream:
    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
    active_path, maximum_path = state / "active", state / "maximum"
    active = int(active_path.read_text()) + 1 if active_path.exists() else 1
    maximum = max(int(maximum_path.read_text()) if maximum_path.exists() else 0, active)
    active_path.write_text(str(active)); maximum_path.write_text(str(maximum))

try:
    if identifier.startswith("SLOW"):
        time.sleep(0.2)
    if identifier == "TIMEOUT":
        marker = state / "child-survived"
        subprocess.Popen([sys.executable, "-c", f"import time; time.sleep(2); open({str(marker)!r}, 'w').write('bad')"])
        time.sleep(10)
    if identifier == "CANCEL" and count == 1:
        marker = state / "cancel-child-survived"
        subprocess.Popen([sys.executable, "-c", f"import time; time.sleep(2); open({str(marker)!r}, 'w').write('bad')"])
        time.sleep(10)
    if identifier == "FAIL_ONCE" and count == 1:
        print("first attempt failed", file=sys.stderr)
        raise SystemExit(7)
    if identifier == "EMPTY":
        raise SystemExit(0)
    report = Path(sys.argv[sys.argv.index("-o") + 1])
    report.write_text(f"report for {identifier}\n")
    resolved_model = "gpt-6-sol" if identifier == "FALLBACK" else "gpt-6-luna"
    print(json.dumps({"type": "thread.started", "thread_id": "fake-thread", "model": resolved_model}))
    print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 2}}))
finally:
    with lock.open("a+") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        active_path = state / "active"
        active_path.write_text(str(int(active_path.read_text()) - 1))
'''


class MaxReviewTests(unittest.TestCase):
    def test_argument_errors_remain_machine_readable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "run", "--parallel", "invalid", "--json"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "error")
        self.assertEqual(result.stderr, "")

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.fake = self.bin / "codex"
        self.fake.write_text(FAKE_CODEX, encoding="utf-8")
        self.fake.chmod(0o755)
        self.fake_state = self.root / "fake-state"
        self.env = {
            **os.environ,
            "PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
            "FAKE_STATE": str(self.fake_state),
            "CODEX_API_KEY": "must-not-leak",
            "OPENAI_API_KEY": "must-not-leak",
            "CODEX_THREAD_ID": "parent",
            "CODEX_SESSION_ID": "parent",
            "CODEX_APP_TOOLS_PIPE_PATH": "/tmp/parent-pipe",
            "CODEX_PERMISSION_PROFILE": "dangerous",
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def prompt(self, identifier: str) -> Path:
        path = self.root / f"{identifier}.txt"
        path.write_text(f"{identifier}\nReview this file.\n", encoding="utf-8")
        return path

    def tasks(self, identifiers: list[str]) -> Path:
        path = self.root / "tasks.jsonl"
        rows = [
            {"id": identifier.lower().replace("_", "-"), "cwd": str(self.root), "prompt_file": str(self.prompt(identifier))}
            for identifier in identifiers
        ]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return path

    def cli(self, *arguments: object, timeout: float = 10) -> tuple[subprocess.CompletedProcess[str], dict]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", *(str(item) for item in arguments)],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
            timeout=timeout,
        )
        return process, json.loads(process.stdout)

    def test_doctor_requires_and_reports_chatgpt_login(self) -> None:
        process, payload = self.cli("doctor")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["chatgpt_login"])
        self.assertEqual(payload["auth_source"], "chatgpt")
        self.assertEqual(payload["model_requested"], "gpt-6-luna")

    def test_doctor_does_not_return_raw_non_chatgpt_login_output(self) -> None:
        self.env["FAKE_LOGIN_STATUS"] = "Bearer secret-value"
        process, payload = self.cli("doctor")
        self.assertEqual(process.returncode, 1)
        self.assertEqual(payload["auth_source"], "other_or_missing")
        self.assertNotIn("secret-value", process.stdout)

    def test_json_flag_is_accepted_after_subcommand(self) -> None:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), "doctor", "--json"],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["status"], "ready")

    def test_run_uses_fixed_safe_argv_copies_input_and_scrubs_environment(self) -> None:
        tasks = self.tasks(["ONE"])
        run_dir = self.root / "run"
        process, payload = self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 1, "--timeout", 3
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(payload["counts"]["succeeded"], 1)
        argv = json.loads((self.fake_state / "ONE.argv.json").read_text())
        self.assertEqual(argv[1], "exec")
        self.assertIn("--ignore-user-config", argv)
        self.assertIn("--skip-git-repo-check", argv)
        self.assertEqual(argv[argv.index("-m") + 1], "gpt-6-luna")
        self.assertIn('model_reasoning_effort="max"', argv)
        self.assertIn('approval_policy="never"', argv)
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        self.assertNotIn("--ignore-rules", argv)
        self.assertNotIn("--worktree", argv)
        environment = json.loads((self.fake_state / "ONE.env.json").read_text())
        self.assertTrue(all(value is None for value in environment.values()))
        state = json.loads((run_dir / "run.json").read_text())
        task = state["tasks"]["one"]
        prompt_copy = run_dir / task["prompt_copy"]
        self.assertEqual(prompt_copy.read_text(), "ONE\nReview this file.\n")
        self.assertEqual(task["attempts"][0]["model_resolved"], "gpt-6-luna")
        self.assertEqual(task["attempts"][0]["thread_id"], "fake-thread")
        self.assertEqual(task["attempts"][0]["usage"]["output_tokens"], 2)
        self.assertTrue((run_dir / task["attempts"][0]["events"]).is_file())
        self.assertTrue((run_dir / task["attempts"][0]["stderr"]).is_file())

    def test_parallel_limit_is_enforced(self) -> None:
        tasks = self.tasks(["SLOW1", "SLOW2", "SLOW3", "SLOW4"])
        process, payload = self.cli(
            "run", "--tasks", tasks, "--run-dir", self.root / "run", "--parallel", 2, "--timeout", 3
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(payload["counts"]["succeeded"], 4)
        self.assertEqual((self.fake_state / "maximum").read_text(), "2")

    def test_nonzero_and_empty_report_are_failures(self) -> None:
        tasks = self.tasks(["FAIL_ONCE", "EMPTY"])
        run_dir = self.root / "run"
        process, payload = self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 2, "--timeout", 3
        )
        self.assertEqual(process.returncode, 1)
        self.assertEqual(payload["counts"]["failed"], 2)
        state = json.loads((run_dir / "run.json").read_text())
        self.assertIn("status 7", state["tasks"]["fail-once"]["attempts"][0]["error"])
        self.assertIn("no final report", state["tasks"]["empty"]["attempts"][0]["error"])

    def test_observed_model_fallback_fails_and_preserves_report(self) -> None:
        tasks = self.tasks(["FALLBACK"])
        run_dir = self.root / "run"
        process, payload = self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 1, "--timeout", 3
        )
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(payload["counts"]["failed"], 1)
        state = json.loads((run_dir / "run.json").read_text())
        attempt = state["tasks"]["fallback"]["attempts"][0]
        self.assertEqual(attempt["model_requested"], "gpt-6-luna")
        self.assertEqual(attempt["model_resolved"], "gpt-6-sol")
        self.assertIn("does not match requested model", attempt["error"])
        self.assertEqual((run_dir / attempt["report"]).read_text(), "report for FALLBACK\n")

    def test_timeout_kills_process_group_and_records_failure(self) -> None:
        tasks = self.tasks(["TIMEOUT"])
        run_dir = self.root / "run"
        process, payload = self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 1, "--timeout", 1,
            timeout=5,
        )
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertEqual(payload["counts"]["failed"], 1)
        state = json.loads((run_dir / "run.json").read_text())
        self.assertTrue(state["tasks"]["timeout"]["attempts"][0]["timed_out"])
        time.sleep(1.2)
        self.assertFalse((self.fake_state / "child-survived").exists())

    def test_termination_cancels_process_group_and_records_failure(self) -> None:
        tasks = self.tasks(["CANCEL", "ONE"])
        run_dir = self.root / "run"
        process = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "--json",
                "run",
                "--tasks",
                str(tasks),
                "--run-dir",
                str(run_dir),
                "--parallel",
                "1",
                "--timeout",
                "20",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
        )
        deadline = time.monotonic() + 4
        started = self.fake_state / "CANCEL.argv.json"
        while not started.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(started.exists(), "fake codex job did not start")
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 2, stderr)
        self.assertEqual(json.loads(stdout)["status"], "error")
        state = json.loads((run_dir / "run.json").read_text())
        self.assertEqual(state["tasks"]["cancel"]["status"], "failed")
        self.assertEqual(state["tasks"]["cancel"]["attempts"][0]["error"], "cancelled")
        self.assertEqual(state["tasks"]["one"]["status"], "queued")
        time.sleep(1.2)
        self.assertFalse((self.fake_state / "cancel-child-survived").exists())
        retry, payload = self.cli("retry", run_dir, "--failed", "--parallel", 1)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertEqual(payload["counts"]["succeeded"], 2)
        self.assertEqual((self.fake_state / "CANCEL.count").read_text(), "2")
        self.assertEqual((self.fake_state / "ONE.count").read_text(), "1")

    def test_retry_preserves_attempts_and_does_not_rerun_success(self) -> None:
        tasks = self.tasks(["FAIL_ONCE", "ONE"])
        run_dir = self.root / "run"
        process, payload = self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 2, "--timeout", 3
        )
        self.assertEqual(process.returncode, 1)
        self.assertEqual(payload["counts"]["failed"], 1)
        process, payload = self.cli("retry", run_dir, "--failed", "--parallel", 1)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(payload["counts"]["succeeded"], 2)
        self.assertEqual((self.fake_state / "ONE.count").read_text(), "1")
        self.assertEqual((self.fake_state / "FAIL_ONCE.count").read_text(), "2")
        state = json.loads((run_dir / "run.json").read_text())
        self.assertEqual(len(state["tasks"]["fail-once"]["attempts"]), 2)
        self.assertTrue((run_dir / "attempts/fail-once/0001/stderr.txt").exists())
        self.assertTrue((run_dir / "attempts/fail-once/0002/report.txt").exists())

    def test_retry_refuses_a_stranded_running_task_with_a_live_process_group(self) -> None:
        tasks = self.tasks(["FAIL_ONCE"])
        run_dir = self.root / "run"
        self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 1, "--timeout", 3
        )
        state_path = run_dir / "run.json"
        state = json.loads(state_path.read_text())
        task = state["tasks"]["fail-once"]
        task["status"] = "running"
        task["attempts"][-1]["status"] = "running"
        task["attempts"][-1]["process_group_id"] = os.getpgrp()
        state_path.write_text(json.dumps(state), encoding="utf-8")
        process, payload = self.cli("retry", run_dir, "--failed", "--parallel", 1)
        self.assertEqual(process.returncode, 2)
        self.assertIn("live process group", payload["error"])
        self.assertEqual((self.fake_state / "FAIL_ONCE.count").read_text(), "1")

    def test_status_and_results_are_machine_readable(self) -> None:
        tasks = self.tasks(["ONE"])
        run_dir = self.root / "run"
        self.cli("run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 1, "--timeout", 3)
        process, status = self.cli("status", run_dir)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(status["task_ids"]["succeeded"], ["one"])
        process, results = self.cli("results", run_dir)
        self.assertEqual(process.returncode, 0)
        self.assertNotIn("report", results["results"][0])
        report_path = Path(results["results"][0]["report_path"])
        self.assertEqual(report_path.read_text(), "report for ONE\n")

    def test_output_schema_is_copied_and_passed_to_every_job(self) -> None:
        schema = self.root / "schema.json"
        schema.write_text('{"type":"object"}\n', encoding="utf-8")
        tasks = self.tasks(["ONE"])
        run_dir = self.root / "run"
        process, _ = self.cli(
            "run", "--tasks", tasks, "--run-dir", run_dir, "--parallel", 1,
            "--timeout", 3, "--output-schema", schema,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        argv = json.loads((self.fake_state / "ONE.argv.json").read_text())
        passed = Path(argv[argv.index("--output-schema") + 1])
        self.assertEqual(passed.resolve(), (run_dir / "inputs/output-schema.json").resolve())
        self.assertEqual(passed.read_text(), schema.read_text())

    def test_invalid_tasks_fail_before_starting_jobs(self) -> None:
        prompt = self.prompt("ONE")
        cases = [
            {"id": "../escape", "cwd": str(self.root), "prompt_file": str(prompt)},
            {"id": "one", "cwd": "relative", "prompt_file": str(prompt)},
            {"id": "one", "cwd": str(self.root), "prompt_file": "relative"},
        ]
        for index, row in enumerate(cases):
            with self.subTest(index=index):
                tasks = self.root / f"bad-{index}.jsonl"
                tasks.write_text(json.dumps(row) + "\n")
                process, payload = self.cli(
                    "run", "--tasks", tasks, "--run-dir", self.root / f"run-{index}",
                    "--parallel", 1, "--timeout", 3,
                )
                self.assertEqual(process.returncode, 2)
                self.assertEqual(payload["status"], "error")

    def test_writer_lock_rejects_second_writer(self) -> None:
        run_dir = self.root / "run"
        run_dir.mkdir()
        lock_path = run_dir / ".lock"
        with lock_path.open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            process, payload = self.cli(
                "run", "--tasks", self.tasks(["ONE"]), "--run-dir", run_dir,
                "--parallel", 1, "--timeout", 3,
            )
        self.assertEqual(process.returncode, 2)
        self.assertIn("another writer", payload["error"])


if __name__ == "__main__":
    unittest.main()
