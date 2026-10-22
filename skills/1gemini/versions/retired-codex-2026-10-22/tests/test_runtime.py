#!/usr/bin/env python3
"""Contract tests for the 1gemini Antigravity wrapper."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ADVISOR = SKILL_ROOT / "scripts" / "gemini_advisor.py"
MODEL = "gemini-3.1-pro-high"


FAKE_AGY = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import re
import sys
import time

args = sys.argv[1:]
if args == ["--version"]:
    print("1.1.15-test")
    raise SystemExit(0)
log = os.environ.get("FAKE_ARGS_LOG")
if log:
    Path(log).write_text(json.dumps(args), encoding="utf-8")
stream_input = sys.stdin.read()
stdin_log = os.environ.get("FAKE_STDIN_LOG")
if stdin_log:
    Path(stdin_log).write_text(stream_input, encoding="utf-8")
env_log = os.environ.get("FAKE_ENV_LOG")
if env_log:
    Path(env_log).write_text(json.dumps(dict(os.environ)), encoding="utf-8")
mode = os.environ.get("FAKE_MODE", "normal")
if mode == "structured-nonzero":
    print("generic stderr warning", file=sys.stderr)
    print(json.dumps({
        "event": "result",
        "result": {
            "conversation_id": "",
            "status": "ERROR",
            "response": "",
            "error": "synthetic structured failure",
        },
    }))
    raise SystemExit(8)
if mode == "nonzero":
    print("synthetic failure", file=sys.stderr)
    raise SystemExit(7)
if mode == "timeout":
    time.sleep(10)
    raise SystemExit(0)
model = args[args.index("--model") + 1]
if mode == "model-mismatch":
    model = "gemini-wrong"
conversation = (
    args[args.index("--conversation") + 1]
    if "--conversation" in args
    else "fake-conversation"
)
if mode == "resume-mismatch":
    conversation = "unexpected-conversation"
cwd = os.getcwd()
if mode == "cwd-mismatch":
    cwd = "/tmp/wrong-cwd"
init = {
    "event": "init",
    "conversation_id": conversation,
    "init": {"model": model, "cwd": cwd, "permission_mode": "request-review"},
}
print(json.dumps(init))
message = json.loads(stream_input.strip())
prompt = message["message"]["content"]
match = re.search(r"The exact staged media path is: (.+)\n", prompt)
if match and mode != "media-unseen":
    state = "DENIED" if mode == "permission-failure" else "DONE"
    update = {
        "event": "step_update",
        "step_update": {
            "step_type": "tool",
            "tool_name": "view_file",
            "state": state,
            "tool_info": {"parameters": {"AbsolutePath": match.group(1)}},
        },
    }
    print(json.dumps(update))
if match and mode in ("extra-media-path", "missing-media-path"):
    print(json.dumps({
        "event": "step_update",
        "step_update": {
            "step_type": "tool", "tool_name": "view_file", "state": "DONE",
            "tool_info": ({"parameters": {"AbsolutePath": "/tmp/unrequested.mp4"}}
                          if mode == "extra-media-path" else {}),
        },
    }))
if mode == "nested":
    print(json.dumps({
        "event": "step_update",
        "step_update": {
            "step_type": "tool", "tool_name": "invoke_subagent", "state": "DONE"
        },
    }))
if mode == "write-tool":
    print(json.dumps({
        "event": "step_update",
        "step_update": {
            "step_type": "tool", "tool_name": "write_to_file", "state": "DONE"
        },
    }))
if mode == "unknown-tool":
    print(json.dumps({
        "event": "step_update",
        "step_update": {
            "step_type": "tool", "tool_name": "edit_file", "state": "DONE"
        },
    }))
status = "ERROR" if mode == "error-status" else "SUCCESS"
response = "" if mode == "empty-response" else "gemini-ok"
result_conversation = "other" if mode == "conversation-mismatch" else conversation
result = {
    "event": "result",
    "result": {
        "conversation_id": result_conversation,
        "status": status,
        "response": response,
        "duration_seconds": 1.25,
        "num_turns": 1,
        "usage": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
    },
}
if mode != "missing-result":
    print(json.dumps(result))
if mode == "duplicate-result":
    print(json.dumps(result))
'''

FAKE_FFMPEG = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
log = os.environ.get("FAKE_FFMPEG_ARGS_LOG")
if log:
    Path(log).write_text(json.dumps(args), encoding="utf-8")
if os.environ.get("FAKE_FFMPEG_FAIL") == "1":
    print("synthetic transcode failure", file=sys.stderr)
    raise SystemExit(9)
Path(args[-1]).write_bytes(b"synthetic-mp4-carrier")
'''


class GeminiRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.home = self.root / "home"
        settings = self.home / ".gemini" / "antigravity-cli" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text('{"modelProvider": null}', encoding="utf-8")
        self.fake_agy = self.root / "agy"
        self.fake_agy.write_text(textwrap.dedent(FAKE_AGY), encoding="utf-8")
        self.fake_agy.chmod(0o755)
        self.fake_ffmpeg = self.root / "ffmpeg"
        self.fake_ffmpeg.write_text(textwrap.dedent(FAKE_FFMPEG), encoding="utf-8")
        self.fake_ffmpeg.chmod(0o755)
        self.args_log = self.root / "args.json"
        self.ffmpeg_args_log = self.root / "ffmpeg-args.json"
        self.stdin_log = self.root / "stdin.jsonl"
        self.env_log = self.root / "env.json"
        self.env = os.environ.copy() | {
            "HOME": str(self.home),
            "FAKE_ARGS_LOG": str(self.args_log),
            "ONE_GEMINI_TEST_HARNESS": "1",
            "ONE_GEMINI_AGY_BIN": str(self.fake_agy),
            "ONE_GEMINI_FFMPEG_BIN": str(self.fake_ffmpeg),
            "ONE_GEMINI_TIMEOUT_SEC": "1",
            "FAKE_STDIN_LOG": str(self.stdin_log),
            "FAKE_ENV_LOG": str(self.env_log),
            "FAKE_FFMPEG_ARGS_LOG": str(self.ffmpeg_args_log),
            "OLDPWD": str(self.project),
            "INIT_CWD": str(self.project),
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def advisor(
        self,
        *extra: str,
        mode: str = "normal",
    ) -> subprocess.CompletedProcess[str]:
        env = self.env | {"FAKE_MODE": mode}
        command = [
            sys.executable,
            str(ADVISOR),
            "--cwd",
            str(self.project),
            *extra,
        ]
        return subprocess.run(
            command,
            input="analyze this",
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def assert_failed(self, completed: subprocess.CompletedProcess[str], text: str) -> None:
        payload = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(payload["ok"])
        self.assertIn(text, payload["error"])

    def test_text_success_has_runtime_evidence(self) -> None:
        completed = self.advisor()
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["resolved"]["model"], MODEL)
        self.assertEqual(payload["resolved"]["mode"], "isolated-text")
        self.assertFalse(payload["isolation"]["source_project_workspace_attached"])
        self.assertFalse(
            payload["isolation"]["source_project_access_guaranteed_blocked"]
        )
        self.assertFalse(Path(payload["resolved"]["cwd"]).exists())
        self.assertEqual(payload["session"]["conversation_id"], "fake-conversation")
        self.assertEqual(payload["session"]["duration_source"], "agy-result")
        self.assertIsInstance(payload["session"]["wrapper_elapsed_seconds"], float)
        self.assertGreaterEqual(payload["session"]["wrapper_elapsed_seconds"], 0)
        self.assertEqual(payload["usage_scope"], "agy-result")
        self.assertNotIn("media_viewed", payload)

    def test_prompt_uses_stream_json_stdin(self) -> None:
        completed = self.advisor()
        self.assertEqual(completed.returncode, 0)
        args = json.loads(self.args_log.read_text(encoding="utf-8"))
        self.assertNotIn("-p", args)
        self.assertIn("--disable-slash-commands", args)
        self.assertNotIn("--mode", args)
        self.assertEqual(args[args.index("--input-format") + 1], "stream-json")
        message = json.loads(self.stdin_log.read_text(encoding="utf-8"))
        self.assertEqual(message["event"], "user")
        self.assertIn("analyze this", message["message"]["content"])

    def test_source_path_environment_is_not_forwarded(self) -> None:
        completed = self.advisor()
        self.assertEqual(completed.returncode, 0)
        environment = json.loads(self.env_log.read_text(encoding="utf-8"))
        self.assertNotIn("OLDPWD", environment)
        self.assertNotIn("INIT_CWD", environment)
        self.assertNotEqual(environment.get("PWD"), str(self.project))

    def test_resume_reaches_official_flag(self) -> None:
        completed = self.advisor("--resume", "conversation-123")
        self.assertEqual(completed.returncode, 0)
        args = json.loads(self.args_log.read_text(encoding="utf-8"))
        self.assertEqual(args[args.index("--conversation") + 1], "conversation-123")
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["session"]["conversation_id"], "conversation-123")
        self.assertEqual(
            payload["usage_scope"],
            "agy-result; turn-vs-conversation scope is not documented for resume",
        )

    def test_resume_mismatch_is_rejected(self) -> None:
        self.assert_failed(
            self.advisor(
                "--resume", "conversation-123", mode="resume-mismatch"
            ),
            "resume mismatch",
        )

    def test_video_is_staged_and_observed(self) -> None:
        source = self.root / "private.mp4"
        source.write_bytes(b"video-original")
        completed = self.advisor("--media", str(source))
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["media"]["viewed"])
        self.assertEqual(payload["media"]["source_kind"], "video")
        self.assertTrue(payload["media"]["conversation_artifacts_may_persist"])
        self.assertTrue(payload["media"]["source_sha256_unchanged"])
        self.assertEqual(source.read_bytes(), b"video-original")
        self.assertFalse(Path(payload["resolved"]["cwd"]).exists())
        args = json.loads(self.args_log.read_text(encoding="utf-8"))
        self.assertIn("--log-file", args)

    def test_audio_is_staged_as_mp4_carrier(self) -> None:
        source = self.root / "private.mp3"
        source.write_bytes(b"audio-original")
        completed = self.advisor("--media", str(source))
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(payload["media"]["viewed"])
        self.assertEqual(payload["media"]["source_kind"], "audio")
        self.assertEqual(payload["media"]["staged_suffix"], ".mp4")
        self.assertEqual(payload["media"]["delivery"], "audio-mp4-carrier")
        self.assertTrue(payload["media"]["audio_transcoded_for_delivery"])
        self.assertEqual(source.read_bytes(), b"audio-original")
        ffmpeg_args = json.loads(self.ffmpeg_args_log.read_text(encoding="utf-8"))
        self.assertIn("libx264", ffmpeg_args)
        self.assertIn("aac", ffmpeg_args)

    def test_audio_carrier_failure_is_reported(self) -> None:
        source = self.root / "private.wav"
        source.write_bytes(b"audio-original")
        self.env["FAKE_FFMPEG_FAIL"] = "1"
        self.assert_failed(
            self.advisor("--media", str(source)), "synthetic transcode failure"
        )

    def test_api_provider_is_rejected(self) -> None:
        settings = self.home / ".gemini" / "antigravity-cli" / "settings.json"
        settings.write_text('{"modelProvider": "gemini"}', encoding="utf-8")
        self.assert_failed(self.advisor(), "modelProvider='gemini'")

    def test_non_gemini_model_is_rejected(self) -> None:
        self.assert_failed(self.advisor("--model", "claude-opus"), "non-Gemini")

    def test_unsupported_media_is_rejected(self) -> None:
        source = self.root / "private.txt"
        source.write_text("not media", encoding="utf-8")
        self.assert_failed(self.advisor("--media", str(source)), "unsupported media")

    def test_model_and_cwd_mismatch_are_rejected(self) -> None:
        self.assert_failed(self.advisor(mode="model-mismatch"), "model mismatch")
        self.assert_failed(self.advisor(mode="cwd-mismatch"), "cwd mismatch")

    def test_terminal_contract_failures_are_rejected(self) -> None:
        for mode, text in (
            ("error-status", "terminal status"),
            ("empty-response", "empty response"),
            ("conversation-mismatch", "conversation_id"),
            ("missing-result", "one terminal result"),
            ("duplicate-result", "one terminal result"),
            ("nonzero", "agy failed"),
        ):
            with self.subTest(mode=mode):
                self.assert_failed(self.advisor(mode=mode), text)

    def test_structured_nonzero_error_is_preserved(self) -> None:
        completed = self.advisor(mode="structured-nonzero")
        self.assert_failed(completed, "synthetic structured failure")
        payload = json.loads(completed.stdout)
        self.assertIn("generic stderr warning", payload["error"])

    def test_media_requires_completed_view_file(self) -> None:
        source = self.root / "private.mp4"
        source.write_bytes(b"video")
        self.assert_failed(
            self.advisor("--media", str(source), mode="media-unseen"),
            "without viewing",
        )
        self.assert_failed(
            self.advisor("--media", str(source), mode="permission-failure"),
            "tool failures",
        )

    def test_additional_media_path_is_rejected(self) -> None:
        source = self.root / "private.mp4"
        source.write_bytes(b"video")
        for mode in ("extra-media-path", "missing-media-path"):
            with self.subTest(mode=mode):
                self.assert_failed(
                    self.advisor("--media", str(source), mode=mode),
                    "outside the staged media path",
                )

    def test_nested_agents_are_rejected(self) -> None:
        self.assert_failed(self.advisor(mode="nested"), "outside the advisor")

    def test_mutation_tools_are_rejected(self) -> None:
        self.assert_failed(self.advisor(mode="write-tool"), "outside the advisor")
        self.assert_failed(self.advisor(mode="unknown-tool"), "outside the advisor")

    def test_process_timeout_is_rejected(self) -> None:
        self.assert_failed(
            self.advisor(mode="timeout"),
            "1-second timeout",
        )


if __name__ == "__main__":
    unittest.main()
