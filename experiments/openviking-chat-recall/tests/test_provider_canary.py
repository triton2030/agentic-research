from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


EXPERIMENT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
import run_provider_canary as canary  # noqa: E402


class ProviderCanaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw_secret = "f4-secret-test-only"
        self.request = canary.build_synthetic_request(
            "f4-public-0123456789abcdef", self.raw_secret
        )

    def test_redaction_happens_before_provider_boundary(self) -> None:
        self.assertNotIn(self.raw_secret, self.request.prompt)
        self.assertIn(canary.REDACTED, self.request.prompt)
        self.assertNotIn(self.raw_secret, json.dumps(self.request.payload))
        adapter = canary.FakeProviderAdapter(
            [canary.FakeOutcome("success", {"nonce": self.request.nonce}, canary.Usage(1, 2, 3))]
        )
        canary.execute_with_retry(adapter, self.request)
        self.assertEqual(len(adapter.requests), 1)
        self.assertNotIn(self.raw_secret, adapter.requests[0].prompt)

    def test_success_counts_one_request_and_aggregates_usage(self) -> None:
        run = canary.execute_with_retry(
            canary.FakeProviderAdapter(
                [
                    canary.FakeOutcome(
                        "success", {"nonce": self.request.nonce}, canary.Usage(11, 7, 18)
                    )
                ]
            ),
            self.request,
        )
        self.assertEqual(run.status, "success")
        self.assertEqual(run.attempts, 1)
        self.assertEqual(run.usage, canary.Usage(11, 7, 18))
        self.assertEqual(run.logs[-1]["event"], "request.completed")

    def test_one_transient_retry_then_success_is_deterministic(self) -> None:
        adapter = canary.FakeProviderAdapter(
            [
                canary.FakeOutcome("transient"),
                canary.FakeOutcome(
                    "success", {"nonce": self.request.nonce}, canary.Usage(5, 3, 8)
                ),
            ]
        )
        run = canary.execute_with_retry(adapter, self.request)
        self.assertEqual(run.status, "success")
        self.assertEqual(run.attempts, 2)
        self.assertEqual(len(adapter.requests), 2)
        self.assertEqual(run.usage, canary.Usage(5, 3, 8))
        self.assertEqual(
            [event["event"] for event in run.logs],
            [
                "request.started",
                "request.failed",
                "request.retrying",
                "request.started",
                "request.completed",
            ],
        )

    def test_terminal_failure_is_not_retried(self) -> None:
        adapter = canary.FakeProviderAdapter([canary.FakeOutcome("terminal")])
        run = canary.execute_with_retry(adapter, self.request)
        self.assertEqual(run.status, "terminal_failure")
        self.assertEqual(run.attempts, 1)
        self.assertEqual(len(adapter.requests), 1)
        self.assertIsNone(run.usage)

    def test_timeout_is_not_retried(self) -> None:
        adapter = canary.FakeProviderAdapter([canary.FakeOutcome("timeout")])
        run = canary.execute_with_retry(adapter, self.request)
        self.assertEqual(run.status, "timeout")
        self.assertEqual(run.attempts, 1)
        self.assertEqual(len(adapter.requests), 1)

    def test_fake_log_schema_is_structured_and_redacted(self) -> None:
        runs = canary.fake_probe_matrix(self.request)
        for run in runs.values():
            for event in run.logs:
                self.assertIsInstance(event, dict)
                self.assertIsInstance(event["event"], str)
                self.assertIsInstance(event["attempt"], int)
                self.assertNotIn(self.raw_secret, json.dumps(event))

    def test_json_event_parser_keeps_only_sanitized_summaries(self) -> None:
        transcript = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "thread-abc"}),
                json.dumps({"type": "turn.started", "model": "gpt-5.6-luna"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "agent_message",
                            "text": json.dumps(
                                {"nonce": self.request.nonce, "redacted_marker": canary.REDACTED}
                            ),
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "turn.completed",
                        "usage": {"input_tokens": 13, "output_tokens": 9, "total_tokens": 22},
                    }
                ),
            ]
        )
        parsed = canary.parse_json_event_stream(transcript, self.raw_secret)
        self.assertEqual(parsed.line_count, 4)
        self.assertEqual(parsed.invalid_line_count, 0)
        self.assertEqual(parsed.usage, canary.Usage(13, 9, 22))
        self.assertEqual(parsed.event_model, "gpt-5.6-luna")
        self.assertEqual(parsed.run_address, {"thread_id": "thread-abc"})
        self.assertFalse(parsed.raw_secret_seen)
        result = canary.parse_structured_result(parsed.response_text, self.request.nonce)
        self.assertEqual(
            result,
            {"nonce": self.request.nonce, "redacted_marker": canary.REDACTED},
        )

    def test_missing_usage_remains_unknown_not_zero(self) -> None:
        transcript = json.dumps(
            {
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": json.dumps(
                        {"nonce": self.request.nonce, "redacted_marker": canary.REDACTED}
                    ),
                },
            }
        )
        parsed = canary.parse_json_event_stream(transcript, self.raw_secret)
        self.assertIsNone(parsed.usage)

    def test_real_adapter_contract_with_non_billing_fake_codex(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_codex = Path(temp_dir) / "codex"
            fake_codex.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "events = [\n"
                " {'type': 'thread.started', 'thread_id': 'thread-fake'},\n"
                " {'type': 'turn.started', 'model': 'gpt-5.6-luna'},\n"
                " {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': json.dumps({'nonce': 'f4-public-0123456789abcdef', 'redacted_marker': '[REDACTED]'})}},\n"
                " {'type': 'turn.completed', 'usage': {'input_tokens': 21, 'output_tokens': 8, 'total_tokens': 29}},\n"
                "]\n"
                "for event in events:\n"
                " print(json.dumps(event))\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            result = canary.run_real_canary(
                self.request,
                self.raw_secret,
                codex_path=str(fake_codex),
                timeout_seconds=5,
            )
        self.assertEqual(result.status, "completed")
        self.assertTrue(result.auth_completed)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.usage, canary.Usage(21, 8, 29))
        self.assertEqual(result.structured_result["nonce"], self.request.nonce)
        self.assertFalse(result.raw_secret_seen)

    def test_receipt_render_is_byte_identical(self) -> None:
        result = {"nonce": self.request.nonce, "redacted_marker": canary.REDACTED}
        first = canary.canonical_bytes(canary.render_captured_result(result))
        second = canary.canonical_bytes(canary.render_captured_result(result))
        self.assertEqual(first, second)

    def test_missing_event_model_cannot_be_a_pass(self) -> None:
        parsed = canary.ParsedEventStream(
            event_types={"item.completed": 1},
            response_text=json.dumps(
                {"nonce": self.request.nonce, "redacted_marker": canary.REDACTED}
            ),
            usage=canary.Usage(3, 2, 5),
            run_address={"thread_id": "thread-test"},
            event_model=None,
            line_count=1,
            invalid_line_count=0,
            raw_secret_seen=False,
        )
        real_run = canary.RealRun(
            status="completed",
            attempts=1,
            elapsed_category="lt_5s",
            usage=parsed.usage,
            parsed=parsed,
            structured_result={"nonce": self.request.nonce, "redacted_marker": canary.REDACTED},
            raw_secret_seen=False,
            auth_completed=True,
            error_category=None,
        )
        receipt = canary.build_receipt(
            cli_version="codex-cli test",
            envelope={},
            command_digest="a" * 64,
            config_digest="b" * 64,
            request=self.request,
            fake_runs=canary.fake_probe_matrix(self.request),
            real_run=real_run,
            captured_result_saved=True,
            render_identical=True,
            artifact_scan={"status": "pass", "files_scanned": [], "violations": []},
        )
        self.assertEqual(receipt["verdict"], "UNKNOWN")

    def test_public_scan_rejects_raw_secret_and_private_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "bad.json").write_text(
                json.dumps({"value": self.raw_secret, "path": "records.jsonl"}),
                encoding="utf-8",
            )
            scan = canary.scan_public_texts(root, self.raw_secret)
            self.assertEqual(scan["status"], "fail")
            self.assertTrue(any("raw-secret" in item for item in scan["violations"]))
            self.assertTrue(any("forbidden-fragment" in item for item in scan["violations"]))

            (root / "records.jsonl").write_text("{}\n", encoding="utf-8")
            scan = canary.scan_public_texts(root, self.raw_secret)
            self.assertTrue(any("forbidden-path" in item for item in scan["violations"]))

    def test_generated_root_symlink_and_unrelated_file_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "provider-canary"
            root.mkdir()
            sentinel = root / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            canary.prepare_artifact_root(root)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

            outside = Path(temp_dir) / "outside.json"
            outside.write_text("outside", encoding="utf-8")
            (root / canary.PUBLIC_RECEIPT).symlink_to(outside)
            with self.assertRaises(canary.CanaryError):
                canary.prepare_artifact_root(root)
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside")

    def test_relative_artifact_root_writes_inside_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "provider-canary"
            canary.prepare_artifact_root(root)
            path = canary.write_owned_json(
                root, canary.PUBLIC_RECEIPT, {"schema": canary.SCHEMA}
            )
            self.assertEqual(path.read_text(encoding="utf-8"), '{"schema":"openviking-chat-recall/provider-canary.v1"}\n')

    def test_validate_receipt_rejects_unknown_usage_as_zero(self) -> None:
        receipt = {
            "schema": canary.SCHEMA,
            "selected_model": canary.DEFAULT_MODEL,
            "thinking": canary.DEFAULT_THINKING,
            "cli_version": "codex-cli test",
            "envelope": {},
            "command_digest": "a" * 64,
            "config_digest": "b" * 64,
            "real_call": {
                "status": "completed",
                "attempts": 1,
                "elapsed_category": "lt_5s",
                "usage": None,
                "usage_status": "unknown",
                "request_count": 1,
                "error_category": None,
            },
            "auth": {
                "completed_real_call": True,
                "config_inspection_only": False,
                "nonce_round_trip": "exact",
            },
            "egress": {
                "synthetic_only": True,
                "provider_input": "public_nonce_and_redacted_payload",
                "repo_paths_opened": [],
                "restricted_source_paths_opened": [],
            },
            "redaction": {
                "provider_input_contains_marker": True,
                "provider_input_contains_raw_secret": False,
                "subprocess_env_contains_canary": False,
            },
            "usage_accounting": {
                "addressable": False,
                "token_usage": None,
                "dollar_cost": 0,
            },
            "output": {"raw_transcript_saved": False},
            "captured_result": {},
            "fake_probes": {},
            "opened_paths": [],
            "artifact_privacy_scan": {},
            "verdict": "UNKNOWN",
        }
        with self.assertRaisesRegex(canary.CanaryError, "zero cost"):
            canary.validate_receipt(receipt)

    def test_unknown_recovery_writes_no_fake_result_or_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "provider-canary"
            with patch.object(canary, "read_cli_version", return_value="codex-cli test"):
                receipt = canary.record_unknown_after_local_error(root)
            self.assertEqual(receipt["verdict"], "UNKNOWN")
            self.assertEqual(receipt["real_call"]["attempts"], 1)
            self.assertIsNone(receipt["real_call"]["usage"])
            self.assertIsNone(receipt["output"]["nonce_digest"])
            self.assertIsNone(receipt["output"]["run_address"])
            self.assertEqual(
                [item["path"] for item in receipt["opened_paths"]],
                [
                    "<temporary-root>/output-schema.json",
                    "<temporary-root>/provider-canary-receipt.json",
                ],
            )
            self.assertFalse((root / canary.CAPTURED_RESULT).exists())
            self.assertFalse((root / canary.RENDER_ONE).exists())
            self.assertFalse((root / canary.RENDER_TWO).exists())
            self.assertEqual(canary.validate_artifact_dir(root)["status"], "pass")


if __name__ == "__main__":
    unittest.main()
