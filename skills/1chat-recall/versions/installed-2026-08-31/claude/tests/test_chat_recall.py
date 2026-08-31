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
DEFAULT_TIMESTAMP = "2001-02-03T04:05:06.789Z"


class ChatRecallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config = Path(self.temp.name) / ".claude"
        self.project = self.config / "projects" / "-test"
        self.project.mkdir(parents=True)
        self.session = str(uuid.uuid4())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def record(
        self,
        record_uuid: str,
        parent: str | None,
        record_type: str,
        message: dict[str, Any],
        **extra: Any,
    ) -> dict[str, Any]:
        timestamp = extra.pop("timestamp", DEFAULT_TIMESTAMP)
        return {
            "sessionId": self.session,
            "uuid": record_uuid,
            "parentUuid": parent,
            "timestamp": timestamp,
            "type": record_type,
            "message": message,
            **extra,
        }

    def write(self, records: list[dict[str, Any]]) -> None:
        path = self.project / f"{self.session}.jsonl"
        path.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )

    def call(self, *args: str, ok: bool = True) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CLAUDE_CONFIG_DIR"] = str(self.config)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--session-id", self.session, *args],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if ok and result.returncode:
            self.fail(result.stderr)
        return result

    def test_filters_runtime_noise_current_turn_and_marks_images(self) -> None:
        first, meta, tool, result, current = (str(uuid.uuid4()) for _ in range(5))
        self.write(
            [
                self.record(
                    first,
                    None,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {}},
                            {"type": "text", "text": "Keep 42 exact."},
                        ],
                    },
                ),
                self.record(
                    meta,
                    first,
                    "user",
                    {"role": "user", "content": "skill expansion"},
                    isMeta=True,
                ),
                self.record(
                    tool,
                    meta,
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
                    result,
                    tool,
                    "user",
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "toolu_bash",
                                "content": "noise",
                            }
                        ],
                    },
                    sourceToolAssistantUUID=tool,
                ),
                self.record(
                    current,
                    result,
                    "user",
                    {"role": "user", "content": "Run recall."},
                ),
            ]
        )

        output = self.call().stdout
        self.assertIn("Prior user input: 1/1", output)
        self.assertIn("Keep 42 exact.", output)
        self.assertIn(
            "source_timestamp: 2001-02-03T04:05:06.789000+00:00",
            output,
        )
        self.assertIn("1 image block(s) omitted", output)
        self.assertNotIn("skill expansion", output)
        self.assertNotIn("Run recall", output)
        self.assertNotIn("noise", output)

        with_current = self.call("--include-current-turn").stdout
        self.assertIn("User input: 2/2; current turn included", with_current)
        self.assertIn("Run recall.", with_current)

    def test_keeps_active_branch_and_verified_question_answer(self) -> None:
        root, ask, answer, discarded, current = (str(uuid.uuid4()) for _ in range(5))
        self.write(
            [
                self.record(
                    root, None, "user", {"role": "user", "content": "Root intent."}
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
                                "id": "toolu_ask",
                                "input": {},
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
                    toolUseResult={"answers": {"Which path?": ["Simple", "Local"]}},
                ),
                self.record(
                    discarded,
                    root,
                    "user",
                    {"role": "user", "content": "Discarded branch."},
                ),
                self.record(
                    current,
                    answer,
                    "user",
                    {"role": "user", "content": "Continue here."},
                ),
            ]
        )

        output = self.call("--all").stdout
        self.assertIn("Root intent.", output)
        self.assertIn("Question from Claude: Which path?", output)
        self.assertIn("Recorded answer: Simple, Local", output)
        self.assertNotIn("Discarded branch", output)
        self.assertNotIn("Continue here", output)

    def test_default_is_bounded_and_all_is_complete(self) -> None:
        records: list[dict[str, Any]] = []
        parent: str | None = None
        for number in range(12):
            record_uuid = str(uuid.uuid4())
            records.append(
                self.record(
                    record_uuid,
                    parent,
                    "user",
                    {"role": "user", "content": f"message-{number}"},
                )
            )
            parent = record_uuid
        current = str(uuid.uuid4())
        records.append(
            self.record(
                current,
                parent,
                "user",
                {"role": "user", "content": "current"},
            )
        )
        self.write(records)

        bounded = self.call().stdout
        self.assertIn("Prior user input: 10/12", bounded)
        self.assertNotIn("message-0\n", bounded)
        self.assertIn("message-11", bounded)

        complete = self.call("--all").stdout
        self.assertIn("Prior user input: 12/12", complete)
        self.assertIn("message-0", complete)

    def test_unknown_human_schema_and_session_mismatch_fail_closed(self) -> None:
        unknown = self.record(
            str(uuid.uuid4()),
            None,
            "user",
            {"role": "user", "content": {"future": True}},
        )
        self.write([unknown])
        self.assertIn("unknown direct user content schema", self.call(ok=False).stderr)

        unknown["message"] = {"role": "user", "content": "text"}
        unknown["sessionId"] = str(uuid.uuid4())
        self.write([unknown])
        self.assertIn("session mismatch", self.call(ok=False).stderr)

    def test_missing_or_invalid_source_timestamp_fails_closed(self) -> None:
        old = self.record(
            str(uuid.uuid4()),
            None,
            "user",
            {"role": "user", "content": "Old evidence."},
            timestamp="not-a-timestamp",
        )
        current = self.record(
            str(uuid.uuid4()),
            old["uuid"],
            "user",
            {"role": "user", "content": "Current turn."},
        )
        self.write([old, current])

        result = self.call(ok=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid source timestamp", result.stderr)


if __name__ == "__main__":
    unittest.main()
