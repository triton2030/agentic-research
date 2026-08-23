#!/usr/bin/env python3
"""Contract tests for the 1hermes wrapper and health reporter."""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

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
    if mode == "array-record":
        print(json.dumps(["unexpected", "shape"]))
        raise SystemExit(0)
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
    if mode in ("ox-unknown-provider", "divergent-provider"):
        provider = "mystery"
    if mode == "malformed-model":
        model = {"id": "moonshotai/kimi-k3"}
    if mode == "missing-provider":
        provider = None
    session_response = os.environ.get("FAKE_SESSION_RESPONSE") or os.environ.get(
        "FAKE_RESPONSE", "review-ok"
    )
    if mode == "no-assistant-message":
        messages = []
    else:
        messages = [{"role": "assistant", "content": session_response}]
    estimated_cost = 0.0 if mode.startswith("ox-") else 0.001
    if mode == "ox-paid":
        estimated_cost = 0.42
    cost_status = "unknown" if mode.startswith("ox-") else "estimated"
    if mode == "ox-cost-estimated":
        cost_status = "estimated"
    if mode == "ox-cost-status-missing":
        cost_status = None
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
        "estimated_cost_usd": estimated_cost,
        "actual_cost_usd": None,
        "cost_status": cost_status,
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
    if os.environ.get("FAKE_MODE") != "missing-session-id":
        print("session_id: fake-session", file=sys.stderr)
    if os.environ.get("FAKE_MODE") == "duplicate-session-id":
        print("session_id: fake-session-dup", file=sys.stderr)
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
        prompt: str = "private-test-brief",
        session_response: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = self.env | {"FAKE_MODE": mode, "FAKE_RESPONSE": response}
        if session_response is not None:
            env["FAKE_SESSION_RESPONSE"] = session_response
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
            input=prompt,
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

    def test_default_run_keeps_project_context(self) -> None:
        completed = self.advisor()
        payload = json.loads(completed.stdout)
        self.assertNotIn("--ignore-rules", self.chat_argv())
        self.assertFalse(payload["requested"]["isolated"])

    def test_isolated_opt_in_cuts_context_and_warns(self) -> None:
        completed = self.advisor("--isolated")
        payload = json.loads(completed.stdout)
        self.assertIn("--ignore-rules", self.chat_argv())
        self.assertTrue(payload["requested"]["isolated"])
        self.assertTrue(
            [item for item in payload["warnings"] if "isolated run" in item]
        )

    def test_skill_preload_rejects_isolation(self) -> None:
        completed = self.advisor("--isolated", "--skill", "github-pr-workflow")
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("--isolated", payload["error"])
        self.assertFalse(self.argv_file.exists())

    def test_skill_preload_allowed_by_default(self) -> None:
        completed = self.advisor("--skill", "github-pr-workflow")
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("--skills", self.chat_argv())

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

    def test_paid_run_survives_an_unexpected_crash_as_json_and_receipt(self) -> None:
        """Прогон стоит денег. Любой исход обязан стать адресуемым результатом,
        а не traceback-ом в stderr вызывающего агента."""
        completed = self.advisor(
            "--model", MODEL, "--reasoning", "medium", prompt="brief\x00tail"
        )
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("embedded null byte", payload["error"])
        receipt = Path(payload["run_dir"]) / "result.json"
        self.assertTrue(receipt.is_file())
        self.assertEqual(json.loads(receipt.read_text())["error"], payload["error"])

    def test_normal_run_leaves_an_addressable_receipt(self) -> None:
        completed = self.advisor("--model", MODEL, "--reasoning", "medium")
        payload = json.loads(completed.stdout)
        run_dir = Path(payload["run_dir"])
        self.assertTrue((run_dir / "manifest.json").is_file())
        self.assertTrue((run_dir / "prompt.md").is_file())
        self.assertEqual(
            json.loads((run_dir / "result.json").read_text())["ok"], payload["ok"]
        )

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

    def test_response_from_real_assistant_record_is_session_sourced(self) -> None:
        """Экспорт с настоящим assistant-message доказывает тело ответа store-ом."""
        completed = self.advisor(
            response="stdout-fallback-text",
            session_response="session-proven-answer",
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertNotEqual(
            payload["response"], "stdout-fallback-text"
        )
        self.assertEqual(payload["response"], "session-proven-answer")
        self.assertEqual(payload["response_source"], "session")

    def test_stdout_fallback_without_optin_is_not_ok(self) -> None:
        """Пустой экспорт: ответ берётся из stdout, ok=false без явного opt-in."""
        completed = self.advisor(mode="no-assistant-message")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["response_source"], "stdout")
        self.assertEqual(payload["response"], "review-ok")
        self.assertTrue(
            [
                item
                for item in payload["warnings"]
                if "response falls back to raw CLI stdout" in item
            ]
        )

    def test_array_export_record_yields_json_failure_not_traceback(self) -> None:
        """Мусорная строка-массив в экспорте не должна ронять обёртку в traceback."""
        completed = self.advisor("--model", MODEL, "--reasoning", "medium",
                                 mode="array-record")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertIn("run_dir", payload)
        self.assertNotIn("Traceback", completed.stderr)

    def test_missing_session_id_fails_closed(self) -> None:
        """Без session_id нет ни metadata, ни route-evidence — зелёного быть не может."""
        completed = self.advisor(mode="missing-session-id")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            [item for item in payload["warnings"] if "did not return a session_id" in item]
        )

    def test_duplicate_session_id_markers_fail_closed(self) -> None:
        """Несколько marker-ов в stderr нельзя угадывать: берём ни один."""
        completed = self.advisor(mode="duplicate-session-id")
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertTrue(
            [item for item in payload["warnings"] if "session_id markers" in item]
        )

    def test_ox_zero_cost_is_accepted_whatever_the_status_is_called(self) -> None:
        """Ярлык статуса меняется провайдером; ноль остаётся нулём.

        Регрессия 2026-08-23: белый список из одного "unknown" отклонил семь
        живых прогонов Ox, у которых стоимость была 0.0, а статус назывался
        "estimated". Гейт обязан судить сумму, а не словарь.
        """
        import _runtime_evidence as evidence

        for status in ("unknown", "estimated", "computed"):
            with self.subTest(status=status):
                ok, why = evidence.ox_cost_verdict(
                    {
                        "estimated_cost_usd": 0.0,
                        "actual_cost_usd": None,
                        "cost_status": status,
                    }
                )
                self.assertTrue(ok, why)
        ok, why = evidence.ox_cost_verdict(
            {"estimated_cost_usd": 0.0, "actual_cost_usd": None, "cost_status": None}
        )
        self.assertFalse(ok, why)
        ok, why = evidence.ox_cost_verdict(
            {"estimated_cost_usd": 0.42, "actual_cost_usd": None, "cost_status": "estimated"}
        )
        self.assertFalse(ok, why)

    def test_ox_post_hoc_cost_or_status_rejects_the_run(self) -> None:
        """Платный прогон или запись без статуса стоимости валят приёмку Ox.

        Незнакомое НАЗВАНИЕ статуса прогон не валит: словарь принадлежит
        провайдеру, а доказывает нулевую трату число. Живой Ox отдаёт и
        "unknown", и "estimated" — см. соседний тест.

        Гейт цены до старта патчится, как и в юните ox_gate выше: иначе тест
        упирается в живой каталог, а не в проверку уже потраченного.
        """
        import _ox_policy as ox

        for mode in ("ox-paid", "ox-cost-status-missing"):
            with self.subTest(mode=mode):
                args = argparse.Namespace(
                    model="stealth/ox-alpha",
                    provider="nous",
                    reasoning="max",
                    resume=None,
                    skill=[],
                    isolated=False,
                    max_turns=2000,
                    timeout_sec=600,
                    allow_write=False,
                    allow_execution_tools=False,
                    worktree=False,
                    allow_fallback=False,
                    allow_stdout_response=False,
                )
                original = ox.live_pricing_is_free
                ox.live_pricing_is_free = lambda: (True, "test: every component is zero")
                try:
                    with mock.patch.dict(
                        os.environ, self.env | {"FAKE_MODE": mode}
                    ), contextlib.redirect_stdout(io.StringIO()) as buffer:
                        exit_code = ADVISOR_MODULE._run(
                            args, "brief", self.project, ["file", "web"], str(self.fake)
                        )
                finally:
                    ox.live_pricing_is_free = original
                payload = json.loads(buffer.getvalue())
                self.assertNotEqual(exit_code, 0)
                self.assertFalse(payload["ok"])
                self.assertTrue(
                    [
                        item
                        for item in payload["warnings"]
                        if "Ox Alpha cost evidence rejected" in item
                    ]
                )

    def test_unpinned_provider_on_fresh_run_warns_about_resolved(self) -> None:
        """--model без --provider не задаёт ожидание провайдера — предупреждай."""
        completed = self.advisor(
            "--model", MODEL, "--reasoning", "medium", mode="divergent-provider"
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["resolved"]["provider"], "mystery")
        self.assertTrue(
            [
                item
                for item in payload["warnings"]
                if "requested provider is unpinned" in item
            ]
        )

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
