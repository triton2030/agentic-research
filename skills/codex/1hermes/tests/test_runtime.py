#!/usr/bin/env python3
"""Contract tests for the 1hermes wrapper and health reporter."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ADVISOR = SKILL_ROOT / "scripts" / "hermes_advisor.py"
MODEL = "moonshotai/kimi-k3"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

ADVISOR_SPEC = importlib.util.spec_from_file_location(
    "hermes_advisor_under_test", ADVISOR
)
assert ADVISOR_SPEC and ADVISOR_SPEC.loader
ADVISOR_MODULE = importlib.util.module_from_spec(ADVISOR_SPEC)
ADVISOR_SPEC.loader.exec_module(ADVISOR_MODULE)


FAKE_HERMES = r'''#!/usr/bin/env python3
import json
import os
import sqlite3
import subprocess
import sys

args = sys.argv[1:]
if args == ["--version"]:
    print("Hermes Agent v0.20.0 (test)")
    raise SystemExit(0)
if args[:2] == ["chat", "--help"]:
    flags = [
        "--query", "--model", "--provider", "--reasoning", "--resume",
        "--toolsets", "--skills", "--max-turns", "--checkpoints",
        "--worktree", "--source", "--quiet",
        "--ignore-user-config",
    ]
    if os.environ.get("FAKE_MODE") == "missing-query":
        flags.remove("--query")
    print(" ".join(flags))
    raise SystemExit(0)
if args[:3] == ["sessions", "export", "--help"]:
    print("--session-id --redact --format")
    raise SystemExit(0)
if args[:2] == ["portal", "info"]:
    print("Auth: logged in\nModel: using Nous as inference provider")
    raise SystemExit(0)
if args[:2] == ["tools", "list"]:
    print("enabled  web\nenabled  file")
    raise SystemExit(0)
if args[:2] == ["sessions", "export"]:
    mode = os.environ.get("FAKE_MODE", "normal")
    effort = "medium"
    argv_file = os.environ.get("FAKE_ARGV_FILE")
    chat_args = []
    if argv_file and os.path.exists(argv_file):
        with open(argv_file, encoding="utf-8") as handle:
            chat_args = json.load(handle)
        if "--reasoning" in chat_args:
            effort = chat_args[chat_args.index("--reasoning") + 1]
    reasoning = "high" if mode == "malformed-reasoning" else {"enabled": True, "effort": effort}
    record_id = "other-session" if mode == "missing-record" else "fake-session"
    model = chat_args[chat_args.index("--model") + 1] if "--model" in chat_args else "moonshotai/kimi-k3"
    if mode.startswith("ox-"):
        model = "stealth/ox-alpha"
    provider = chat_args[chat_args.index("--provider") + 1] if "--provider" in chat_args else "nous"
    if mode == "ox-unknown-provider":
        provider = "mystery"
    if mode == "malformed-model":
        model = {"id": "moonshotai/kimi-k3"}
    if mode == "missing-provider":
        provider = None
    messages = []
    record = {
        "id": record_id,
        "model": model,
        "billing_provider": provider,
        "model_config": json.dumps({"reasoning_config": reasoning, "max_iterations": 48}),
        "source": "tool",
        "message_count": 2,
        "tool_call_count": len(messages),
        "end_reason": "completed",
        "input_tokens": 10,
        "output_tokens": 2,
        "reasoning_tokens": 1,
        "api_call_count": 1,
        "estimated_cost_usd": 0.001,
        "messages": messages,
    }
    print(json.dumps(record))
    raise SystemExit(0)
if args and args[0] == "chat":
    argv_file = os.environ.get("FAKE_ARGV_FILE")
    if argv_file:
        with open(argv_file, "w", encoding="utf-8") as handle:
            json.dump(args, handle)
    safe_root_file = os.environ.get("FAKE_SAFE_ROOT_FILE")
    if safe_root_file:
        with open(safe_root_file, "w", encoding="utf-8") as handle:
            handle.write(os.environ.get("HERMES_WRITE_SAFE_ROOT", ""))
    session_id = args[args.index("--resume") + 1] if "--resume" in args else "fake-session"
    model = args[args.index("--model") + 1] if "--model" in args else "z-ai/glm-5.2"
    if os.environ.get("FAKE_MODE") == "resume-drift":
        model = "z-ai/glm-5.2"
    provider = args[args.index("--provider") + 1] if "--provider" in args else "nous"
    base_url = "https://inference-api.nousresearch.com/v1" if provider == "nous" else "https://unexpected.invalid/v1"
    state_db = os.path.join(os.environ["HERMES_HOME"], "state.db")
    connection = sqlite3.connect(state_db)
    connection.execute(
        """
        INSERT INTO session_model_usage (
            session_id, model, billing_provider, billing_base_url,
            billing_mode, task, api_call_count
        ) VALUES (?, ?, ?, ?, '', '', 1)
        ON CONFLICT(session_id, model, billing_provider, billing_base_url, billing_mode, task)
        DO UPDATE SET api_call_count = api_call_count + 1
        """,
        (session_id, model, provider, base_url),
    )
    if os.environ.get("FAKE_MODE") == "mixed-route":
        connection.execute(
            """
            INSERT INTO session_model_usage (
                session_id, model, billing_provider, billing_base_url,
                billing_mode, task, api_call_count
            ) VALUES (?, 'z-ai/glm-5.2', 'openrouter', 'https://openrouter.ai/api/v1', '', '', 1)
            """,
            (session_id,),
        )
    connection.commit()
    connection.close()
    if os.environ.get("FAKE_MODE") == "worktree-commit":
        with open("result.txt", "w", encoding="utf-8") as handle:
            handle.write("done\n")
    print(os.environ.get("FAKE_RESPONSE", "review-ok"))
    print("session_id: fake-session", file=sys.stderr)
    raise SystemExit(0)
print("unsupported fake command: " + repr(args), file=sys.stderr)
raise SystemExit(2)
'''


class HermesRuntimeTests(unittest.TestCase):
    def test_final_assistant_content_ignores_reasoning_and_tool_turns(self):
        record = {
            "messages": [
                {"role": "assistant", "content": "", "tool_calls": [{"function": {}}]},
                {
                    "role": "assistant",
                    "content": " OX_READ_OK \n",
                    "reasoning": "internal trace",
                },
            ]
        }
        self.assertEqual(
            ADVISOR_MODULE.evidence.final_assistant_content(record), "OX_READ_OK"
        )

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.project, check=True)
        subprocess.run(
            ["git", "config", "user.email", "hermes-test@example.invalid"],
            cwd=self.project,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Hermes Test"], cwd=self.project, check=True
        )
        (self.project / "seed.txt").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "add", "seed.txt"], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.project, check=True)
        subprocess.run(
            ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
            cwd=self.project,
            check=True,
        )
        self.hermes_home = self.root / "hermes-home"
        (self.hermes_home / "cache").mkdir(parents=True)
        connection = sqlite3.connect(self.hermes_home / "state.db")
        connection.execute(
            """
            CREATE TABLE session_model_usage (
                session_id TEXT NOT NULL,
                model TEXT NOT NULL,
                billing_provider TEXT NOT NULL DEFAULT '',
                billing_base_url TEXT NOT NULL DEFAULT '',
                billing_mode TEXT NOT NULL DEFAULT '',
                task TEXT NOT NULL DEFAULT '',
                api_call_count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (
                    session_id, model, billing_provider, billing_base_url,
                    billing_mode, task
                )
            )
            """
        )
        connection.commit()
        connection.close()
        catalog = {
            "updated_at": "2026-08-05T00:00:00Z",
            "providers": {"nous": {"models": [{"id": MODEL}]}},
        }
        (self.hermes_home / "cache" / "model_catalog.json").write_text(
            json.dumps(catalog), encoding="utf-8"
        )
        self.fake = self.root / "hermes"
        self.fake.write_text(textwrap.dedent(FAKE_HERMES), encoding="utf-8")
        self.fake.chmod(0o755)
        self.argv_file = self.root / "chat-argv.json"
        self.safe_root_file = self.root / "safe-root.txt"
        self.env = os.environ.copy()
        self.env["HERMES_HOME"] = str(self.hermes_home)
        self.env["FAKE_ARGV_FILE"] = str(self.argv_file)
        self.env["FAKE_SAFE_ROOT_FILE"] = str(self.safe_root_file)

    def chat_argv(self) -> list[str]:
        return json.loads(self.argv_file.read_text(encoding="utf-8"))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def advisor(
        self,
        *extra: str,
        mode: str = "normal",
        response: str = "review-ok",
    ) -> subprocess.CompletedProcess[str]:
        env = self.env | {"FAKE_MODE": mode, "FAKE_RESPONSE": response}
        command = [
            sys.executable,
            str(ADVISOR),
            "--cwd",
            str(self.project),
            "--hermes-bin",
            str(self.fake),
            *extra,
        ]
        return subprocess.run(
            command,
            input="private-test-brief",
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_default_run_uses_owner_runtime(self) -> None:
        completed = self.advisor()
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["requested"]["toolsets"], "file,web")
        self.assertEqual(payload["requested"]["reasoning"], "medium")
        self.assertEqual(payload["requested"]["max_turns"], 2000)

    def test_ox_pricing_gate_requires_every_component_to_be_zero(self) -> None:
        free_catalog = {
            "data": [
                {
                    "id": "stealth/ox-alpha",
                    "pricing": {
                        "prompt": "0",
                        "completion": 0,
                        "internal_reasoning": "0.000",
                    },
                }
            ]
        }
        self.assertTrue(ADVISOR_MODULE._ox_alpha_pricing_is_free(free_catalog)[0])
        for bad_value in ("0.01", "unknown", None, True):
            paid_or_unknown = json.loads(json.dumps(free_catalog))
            paid_or_unknown["data"][0]["pricing"]["request"] = bad_value
            self.assertFalse(
                ADVISOR_MODULE._ox_alpha_pricing_is_free(paid_or_unknown)[0]
            )
        self.assertEqual(
            ADVISOR_MODULE._ox_alpha_catalog_url("nous"),
            "https://inference-api.nousresearch.com/v1/models",
        )
        self.assertEqual(
            ADVISOR_MODULE._ox_alpha_catalog_url("openrouter"),
            None,
        )

    def test_ox_requires_exact_nous_and_max_before_chat(self) -> None:
        self.assertIsNone(
            ADVISOR_MODULE._ox_alpha_admission_error(
                "nous", "max", allow_fallback=False
            )
        )
        for provider, reasoning in (("openrouter", "max"), ("nous", "high")):
            with self.subTest(provider=provider, reasoning=reasoning):
                error = ADVISOR_MODULE._ox_alpha_admission_error(
                    provider, reasoning, allow_fallback=False
                )
                self.assertIsNotNone(error)

    def test_ox_has_full_agent_rights_and_only_the_billing_gate(self) -> None:
        """Ox работает как любая другая роль: terminal, execution и запись
        проходят общий контроль. Отдельным остаётся только гейт денег."""
        import _advisor_contract as contract
        import _ox_policy as ox

        args = argparse.Namespace(
            model=ox.MODEL,
            provider="nous",
            reasoning="max",
            toolsets="file,terminal,web",
            allow_execution_tools=True,
            allow_write=True,
            worktree=False,
            allow_fallback=False,
            skill=[],
            resume=None,
        )
        runtime = (ox.MODEL, "nous", "max")
        original = ox.live_pricing_is_free
        try:
            ox.live_pricing_is_free = lambda: (True, "test: every component is zero")
            self.assertIsNone(contract.ox_gate(args, runtime))

            ox.live_pricing_is_free = lambda: (False, "test: pricing is unreadable")
            paid = contract.ox_gate(args, runtime)
            self.assertIsNotNone(paid)
            self.assertIn("Ox Alpha disabled", paid)

            ox.live_pricing_is_free = lambda: (True, "test: every component is zero")
            off_route = contract.ox_gate(args, (ox.MODEL, "openrouter", "max"))
            self.assertIsNotNone(off_route)
        finally:
            ox.live_pricing_is_free = original

    def test_ox_cost_evidence_must_prove_zero_after_the_run(self) -> None:
        """Каталог доказывает цену до старта, сессия — после. Между ними часы."""
        import _runtime_evidence as evidence

        live_shape = {
            "estimated_cost_usd": 0.0,
            "actual_cost_usd": None,
            "cost_status": "unknown",
        }
        self.assertTrue(evidence.ox_cost_verdict(live_shape)[0])

        for rejected in (
            {"estimated_cost_usd": 0.001, "actual_cost_usd": None},
            {"estimated_cost_usd": 0.0, "actual_cost_usd": 0.02},
            {"estimated_cost_usd": None, "actual_cost_usd": None},
            {"estimated_cost_usd": "0", "actual_cost_usd": None},
        ):
            with self.subTest(usage=rejected):
                verdict, reason = evidence.ox_cost_verdict(rejected)
                self.assertFalse(verdict)
                self.assertTrue(reason)

    def test_ox_route_evidence_rejects_mixed_or_shadow_endpoint(self) -> None:
        exact = (
            "stealth/ox-alpha",
            "nous",
            "https://inference-api.nousresearch.com/v1",
            "",
            "",
        )
        shadow = (
            "stealth/ox-alpha",
            "nous",
            "https://shadow.invalid/v1",
            "",
            "title_generation",
        )
        evidence, mismatch = ADVISOR_MODULE._runtime_usage_evidence(
            {}, {exact: 1, shadow: 1}, model=exact[0], provider=exact[1], ox_alpha=True
        )
        self.assertTrue(mismatch)
        self.assertFalse(evidence["verified"])
        self.assertEqual(
            evidence["unexpected_main_calls"][0]["billing_base_url"], shadow[2]
        )

    def test_ox_resume_rejects_fallback_before_chat(self) -> None:
        completed = self.advisor(
            "--resume", "fake-session", "--allow-fallback", mode="ox-session"
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("forbids --allow-fallback", payload["error"])
        self.assertFalse(self.argv_file.exists())

    def test_resume_requires_exact_model_and_provider_before_chat(self) -> None:
        for mode in ("missing-record", "malformed-model", "missing-provider"):
            with self.subTest(mode=mode):
                completed = self.advisor("--resume", "fake-session", mode=mode)
                payload = json.loads(completed.stdout)
                self.assertEqual(completed.returncode, 2)
                self.assertIn(
                    "exact saved model, provider, and reasoning", payload["error"]
                )
                self.assertFalse(self.argv_file.exists())

    def test_resume_pins_and_proves_saved_runtime(self) -> None:
        completed = self.advisor("--resume", "fake-session")
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["resume_runtime"]["verified"])
        self.assertEqual(payload["resume_runtime"]["new_main_api_calls"], 1)
        argv = self.chat_argv()
        self.assertEqual(argv[argv.index("--model") + 1], "moonshotai/kimi-k3")
        self.assertEqual(argv[argv.index("--provider") + 1], "nous")
        self.assertEqual(argv[argv.index("--reasoning") + 1], "medium")

    def test_resume_fails_when_usage_proves_model_drift(self) -> None:
        completed = self.advisor("--resume", "fake-session", mode="resume-drift")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["resume_runtime"]["verified"])
        self.assertEqual(
            payload["resume_runtime"]["unexpected_main_calls"][0]["model"],
            "z-ai/glm-5.2",
        )
        self.assertEqual(completed.returncode, payload["exit_code"])

    def test_ox_resume_rejects_unknown_provider_before_chat(self) -> None:
        completed = self.advisor("--resume", "fake-session", mode="ox-unknown-provider")
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("requires --provider nous", payload["error"])
        self.assertFalse(self.argv_file.exists())

    def test_unknown_or_composite_toolset_fails_closed(self) -> None:
        completed = self.advisor("--toolsets", "hermes-cron")
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(payload["ok"])
        self.assertIn("--allow-execution-tools", payload["error"])

    def test_read_only_run_uses_host_write_safe_root_outside_project(self) -> None:
        completed = self.advisor()
        self.assertEqual(completed.returncode, 0)
        safe_root = Path(self.safe_root_file.read_text(encoding="utf-8"))
        self.assertNotEqual(safe_root, self.project)
        self.assertFalse(safe_root.is_relative_to(self.project))
        self.assertFalse(safe_root.exists())

    def test_execution_tools_require_write_permission(self) -> None:
        completed = self.advisor("--toolsets", "terminal", "--allow-execution-tools")
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("requires --allow-write", payload["error"])
        self.assertFalse(self.argv_file.exists())

    def test_malformed_reasoning_never_passes_with_fallback(self) -> None:
        completed = self.advisor("--allow-fallback", mode="malformed-reasoning")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertIn("metadata is malformed", " ".join(payload["warnings"]))

    def test_worktree_boundary_requires_local_unpushed_commit(self) -> None:
        completed = self.advisor("--allow-write", "--worktree", mode="worktree-commit")
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["worktree"]["clean"])
        self.assertGreaterEqual(payload["worktree"]["unpushed_commits"], 1)
        self.assertEqual(
            self.safe_root_file.read_text(encoding="utf-8"), payload["worktree"]["path"]
        )
        argv = self.chat_argv()
        prompt = argv[argv.index("-q") + 1]
        self.assertIn("the host creates the commit", prompt)

    def test_commit_failure_preserves_recovery_path(self) -> None:
        hook = self.project / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        hook.chmod(0o755)
        completed = self.advisor("--allow-write", "--worktree", mode="worktree-commit")
        payload = json.loads(completed.stdout)
        receipt = payload["worktree"]
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(receipt["exists"])
        self.assertTrue(receipt["dirty"])
        self.assertTrue(receipt["recovery_required"])
        self.assertTrue(Path(receipt["path"]).is_dir())
        subprocess.run(
            ["git", "worktree", "remove", "--force", receipt["path"]],
            cwd=self.project,
            check=True,
        )
        subprocess.run(
            ["git", "branch", "-D", receipt["branch"]],
            cwd=self.project,
            check=True,
            capture_output=True,
        )

    def test_worktree_without_remote_tracking_ref_fails_before_run(self) -> None:
        subprocess.run(
            ["git", "update-ref", "-d", "refs/remotes/origin/main"],
            cwd=self.project,
            check=True,
        )
        completed = self.advisor("--allow-write", "--worktree")
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 2)
        self.assertFalse(payload["ok"])
        self.assertIn("remote-tracking ref", payload["error"])
        self.assertFalse(self.argv_file.exists())

    def test_cleaned_worktree_cannot_pass_as_success(self) -> None:
        completed = self.advisor("--allow-write", "--worktree")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertIn("no file changes", " ".join(payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
