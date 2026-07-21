from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_recall.py"


class ChatRecallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / ".claude"
        self.project_dir = self.config_dir / "projects" / "-tmp-project"
        self.project_dir.mkdir(parents=True)
        self.session_id = str(uuid.uuid4())

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def record(
        self,
        record_uuid: str | None,
        parent_uuid: str | None,
        record_type: str,
        message: dict[str, Any] | None = None,
        **extra: Any,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "sessionId": self.session_id,
            "type": record_type,
            "timestamp": "2026-07-21T10:00:00.000Z",
        }
        if record_uuid is not None:
            result["uuid"] = record_uuid
            result["parentUuid"] = parent_uuid
        if message is not None:
            result["message"] = message
        result.update(extra)
        return result

    def write(self, records: list[dict[str, Any]]) -> None:
        transcript = self.project_dir / f"{self.session_id}.jsonl"
        transcript.write_text(
            "".join(
                json.dumps(record, ensure_ascii=False) + "\n" for record in records
            ),
            encoding="utf-8",
        )

    def call(
        self, *arguments: str, expect_success: bool = True
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["CLAUDE_CONFIG_DIR"] = str(self.config_dir)
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--session-id", self.session_id, *arguments],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        if expect_success and completed.returncode != 0:
            self.fail(f"command failed: {completed.stderr}")
        return completed

    def test_direct_messages_exclude_current_and_all_runtime_noise(self) -> None:
        user_one = str(uuid.uuid4())
        meta = str(uuid.uuid4())
        notification = str(uuid.uuid4())
        tool_call = str(uuid.uuid4())
        tool_result = str(uuid.uuid4())
        current = str(uuid.uuid4())
        self.write(
            [
                self.record(
                    user_one,
                    None,
                    "user",
                    {"role": "user", "content": "Remember 42 exactly."},
                ),
                self.record(
                    meta,
                    user_one,
                    "user",
                    {"role": "user", "content": "skill expansion"},
                    isMeta=True,
                ),
                self.record(
                    notification,
                    meta,
                    "user",
                    {"role": "user", "content": "background task done"},
                    origin={"kind": "task-notification"},
                ),
                self.record(
                    tool_call,
                    notification,
                    "assistant",
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Bash",
                                "id": "toolu_bash",
                                "input": {},
                            }
                        ],
                    },
                ),
                self.record(
                    tool_result,
                    tool_call,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_bash",
                                "content": "42",
                            }
                        ],
                    },
                    sourceToolAssistantUUID=tool_call,
                    toolUseResult="42",
                ),
                self.record(
                    current,
                    tool_result,
                    "user",
                    {"role": "user", "content": "Run chat recall now."},
                ),
            ]
        )

        output = self.call("--json", "read", "--limit", "all")
        payload = json.loads(output.stdout)
        self.assertTrue(payload["verified_session"])
        self.assertTrue(payload["current_turn_excluded"])
        self.assertEqual(payload["returned"], 1)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["records"][0]["text"], "Remember 42 exactly.")

        search = json.loads(self.call("--json", "search", "remember").stdout)
        record_id = search["records"][0]["id"]
        shown = json.loads(self.call("--json", "show", record_id).stdout)
        self.assertEqual(shown["records"][0]["text"], "Remember 42 exactly.")

    def test_structured_question_answers_preserve_selection_and_free_text_provenance(
        self,
    ) -> None:
        first = str(uuid.uuid4())
        ask = str(uuid.uuid4())
        answer = str(uuid.uuid4())
        bash_call = str(uuid.uuid4())
        bash_result = str(uuid.uuid4())
        current = str(uuid.uuid4())
        questions = [
            {
                "question": "Priority?",
                "options": [{"label": "Speed"}, {"label": "Quality"}],
                "multiSelect": False,
            },
            {
                "question": "Channels?",
                "options": [{"label": "Web"}, {"label": "Mobile"}],
                "multiSelect": True,
            },
            {"question": "Constraint?", "options": [], "multiSelect": False},
        ]
        self.write(
            [
                self.record(first, None, "user", {"role": "user", "content": "Start."}),
                self.record(
                    ask,
                    first,
                    "assistant",
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "AskUserQuestion",
                                "id": "toolu_ask",
                                "input": {"questions": questions},
                            }
                        ],
                    },
                ),
                self.record(
                    answer,
                    ask,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_ask",
                                "content": "answered",
                            }
                        ],
                    },
                    sourceToolAssistantUUID=ask,
                    toolUseResult={
                        "questions": questions,
                        "answers": {
                            "Priority?": "Quality",
                            "Channels?": ["Web", "Mobile"],
                            "Constraint?": "No vendor lock-in",
                        },
                    },
                ),
                self.record(
                    bash_call,
                    answer,
                    "assistant",
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Bash",
                                "id": "toolu_bash",
                                "input": {},
                            }
                        ],
                    },
                ),
                self.record(
                    bash_result,
                    bash_call,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_bash",
                                "content": "ignored",
                            }
                        ],
                    },
                    sourceToolAssistantUUID=bash_call,
                    toolUseResult="ignored legacy result for another tool",
                ),
                self.record(
                    current,
                    bash_result,
                    "user",
                    {"role": "user", "content": "Continue."},
                ),
            ]
        )

        payload = json.loads(
            self.call("--json", "read", "--scope", "questions", "--limit", "all").stdout
        )
        self.assertEqual(payload["returned"], 1)
        answers = payload["records"][0]["answers"]
        self.assertEqual(answers[0]["selections"], ["Quality"])
        self.assertEqual(answers[0]["free_text"], [])
        self.assertEqual(answers[1]["selections"], ["Web", "Mobile"])
        self.assertEqual(answers[2]["free_text"], ["No vendor lock-in"])

    def test_rewind_branch_is_excluded_by_active_ancestry(self) -> None:
        root = str(uuid.uuid4())
        common = str(uuid.uuid4())
        discarded = str(uuid.uuid4())
        discarded_reply = str(uuid.uuid4())
        current = str(uuid.uuid4())
        self.write(
            [
                self.record(
                    root, None, "user", {"role": "user", "content": "Root requirement."}
                ),
                self.record(
                    common,
                    root,
                    "assistant",
                    {"role": "assistant", "content": "Acknowledged."},
                ),
                self.record(
                    discarded,
                    common,
                    "user",
                    {"role": "user", "content": "Discarded branch."},
                ),
                self.record(
                    discarded_reply,
                    discarded,
                    "assistant",
                    {"role": "assistant", "content": "Old reply."},
                ),
                self.record(
                    current,
                    common,
                    "user",
                    {"role": "user", "content": "Current branch."},
                ),
            ]
        )

        default_payload = json.loads(
            self.call("--json", "read", "--limit", "all").stdout
        )
        self.assertEqual(
            [record["text"] for record in default_payload["records"]],
            ["Root requirement."],
        )

        included = json.loads(
            self.call(
                "--json", "read", "--limit", "all", "--include-current-turn"
            ).stdout
        )
        self.assertEqual(
            [record["text"] for record in included["records"]],
            ["Root requirement.", "Current branch."],
        )

    def test_image_and_text_message_keeps_text_with_visible_omission(self) -> None:
        screenshot = str(uuid.uuid4())
        current = str(uuid.uuid4())
        self.write(
            [
                self.record(
                    screenshot,
                    None,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": "fixture",
                                },
                            },
                            {"type": "text", "text": "Inspect this exact caption."},
                        ],
                    },
                ),
                self.record(
                    current,
                    screenshot,
                    "user",
                    {"role": "user", "content": "Run recall."},
                ),
            ]
        )

        payload = json.loads(self.call("--json", "read", "--limit", "all").stdout)
        self.assertEqual(payload["records"][0]["text"], "Inspect this exact caption.")
        self.assertEqual(
            payload["records"][0]["omissions"], ["1 image block(s) omitted"]
        )
        self.assertTrue(payload["warnings"])

        search = json.loads(self.call("--json", "search", "exact caption").stdout)
        self.assertEqual(search["returned"], 1)
        self.assertTrue(search["warnings"])

    def test_unanswered_question_on_active_branch_is_not_user_input(self) -> None:
        root = str(uuid.uuid4())
        ask = str(uuid.uuid4())
        discarded_answer = str(uuid.uuid4())
        current = str(uuid.uuid4())
        question = [
            {
                "question": "Discarded choice?",
                "options": [{"label": "Old"}],
                "multiSelect": False,
            }
        ]
        self.write(
            [
                self.record(
                    root, None, "user", {"role": "user", "content": "Root input."}
                ),
                self.record(
                    ask,
                    root,
                    "assistant",
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "AskUserQuestion",
                                "id": "toolu_discarded",
                                "input": {"questions": question},
                            }
                        ],
                    },
                ),
                self.record(
                    discarded_answer,
                    ask,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_discarded",
                                "content": "Old",
                            }
                        ],
                    },
                    sourceToolAssistantUUID=ask,
                    toolUseResult={
                        "questions": question,
                        "answers": {"Discarded choice?": "Old"},
                    },
                ),
                self.record(
                    current,
                    ask,
                    "user",
                    {"role": "user", "content": "New active branch."},
                ),
            ]
        )

        payload = json.loads(self.call("--json", "read", "--limit", "all").stdout)
        self.assertEqual([item["kind"] for item in payload["records"]], ["message"])
        self.assertEqual(payload["records"][0]["text"], "Root input.")

    def test_unknown_human_content_schema_fails_closed(self) -> None:
        unknown = str(uuid.uuid4())
        self.write(
            [
                self.record(
                    unknown,
                    None,
                    "user",
                    {"role": "user", "content": {"future_schema": True}},
                )
            ]
        )
        completed = self.call("read", expect_success=False)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("unknown direct human content schema", completed.stderr)

    def test_legacy_question_result_fails_closed(self) -> None:
        first = str(uuid.uuid4())
        ask = str(uuid.uuid4())
        answer = str(uuid.uuid4())
        current = str(uuid.uuid4())
        question = [
            {"question": "Ready?", "options": [{"label": "Yes"}], "multiSelect": False}
        ]
        self.write(
            [
                self.record(first, None, "user", {"role": "user", "content": "Start."}),
                self.record(
                    ask,
                    first,
                    "assistant",
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "AskUserQuestion",
                                "id": "toolu_legacy",
                                "input": {"questions": question},
                            }
                        ],
                    },
                ),
                self.record(
                    answer,
                    ask,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_legacy",
                                "content": "Yes",
                            }
                        ],
                    },
                    sourceToolAssistantUUID=ask,
                    toolUseResult="Yes",
                ),
                self.record(
                    current, answer, "user", {"role": "user", "content": "Continue."}
                ),
            ]
        )
        completed = self.call("read", expect_success=False)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("legacy AskUserQuestion result", completed.stderr)

    def test_session_mismatch_fails_closed(self) -> None:
        record = self.record(
            str(uuid.uuid4()),
            None,
            "user",
            {"role": "user", "content": "Wrong session."},
        )
        record["sessionId"] = str(uuid.uuid4())
        self.write([record])
        completed = self.call("read", expect_success=False)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("session mismatch", completed.stderr)


if __name__ == "__main__":
    unittest.main()
