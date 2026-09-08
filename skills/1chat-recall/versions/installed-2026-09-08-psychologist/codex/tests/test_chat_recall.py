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
        self.temp = tempfile.TemporaryDirectory()
        self.codex_home = Path(self.temp.name) / ".codex"
        self.sessions = self.codex_home / "sessions" / "2026" / "07" / "22"
        self.sessions.mkdir(parents=True)
        self.thread = str(uuid.uuid4())

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def row(type_: str, payload: dict[str, Any], timestamp: str) -> dict[str, Any]:
        return {"timestamp": timestamp, "type": type_, "payload": payload}

    def write(self, records: list[dict[str, Any]]) -> None:
        transcript = self.sessions / f"rollout-test-{self.thread}.jsonl"
        transcript.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )

    def call(
        self, *args: str, expect_ok: bool = True
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CODEX_HOME"] = str(self.codex_home)
        env["CODEX_THREAD_ID"] = self.thread
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=self.temp.name,
            check=False,
        )
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def fixture(self, *, malformed_plan: bool = False) -> list[dict[str, Any]]:
        old_turn = str(uuid.uuid4())
        discarded_turn = str(uuid.uuid4())
        current_turn = str(uuid.uuid4())
        questions = {
            "questions": [
                {
                    "header": "Маршрут",
                    "id": "route",
                    "question": "Какой путь?",
                    "options": [
                        {"label": "Точный", "description": "Сохраняет границы"},
                        {"label": "Быстрый", "description": "Меньше проверки"},
                    ],
                }
            ]
        }
        answers = "{broken" if malformed_plan else json.dumps(
            {"answers": {"route": {"answers": ["Точный"]}}},
            ensure_ascii=False,
        )
        return [
            self.row("session_meta", {"id": self.thread}, "2026-07-22T00:00:00Z"),
            self.row(
                "event_msg",
                {"type": "task_started", "turn_id": old_turn},
                "2026-07-22T00:00:01Z",
            ),
            self.row(
                "event_msg",
                {"type": "user_message", "message": "Сохрани 42 точно."},
                "2026-07-22T00:00:02Z",
            ),
            self.row(
                "response_item",
                {
                    "type": "function_call",
                    "name": "request_user_input",
                    "call_id": "call-1",
                    "arguments": json.dumps(questions, ensure_ascii=False),
                },
                "2026-07-22T00:00:03Z",
            ),
            self.row(
                "response_item",
                {
                    "type": "function_call_output",
                    "call_id": "call-1",
                    "output": answers,
                },
                "2026-07-22T00:00:04Z",
            ),
            self.row(
                "event_msg",
                {"type": "context_compacted"},
                "2026-07-22T00:00:05Z",
            ),
            self.row(
                "event_msg",
                {"type": "task_complete", "turn_id": old_turn},
                "2026-07-22T00:00:06Z",
            ),
            self.row(
                "event_msg",
                {"type": "task_started", "turn_id": discarded_turn},
                "2026-07-22T00:00:07Z",
            ),
            self.row(
                "event_msg",
                {"type": "user_message", "message": "Эту ветку откатили."},
                "2026-07-22T00:00:08Z",
            ),
            self.row(
                "event_msg",
                {"type": "task_complete", "turn_id": discarded_turn},
                "2026-07-22T00:00:09Z",
            ),
            self.row(
                "event_msg",
                {"type": "thread_rolled_back", "num_turns": 1},
                "2026-07-22T00:00:10Z",
            ),
            self.row(
                "event_msg",
                {"type": "task_started", "turn_id": current_turn},
                "2026-07-22T00:00:11Z",
            ),
            self.row(
                "event_msg",
                {"type": "user_message", "message": "Текущий ход."},
                "2026-07-22T00:00:12Z",
            ),
        ]

    def test_help_calls_transcript_results_candidates_not_owner_evidence(self) -> None:
        result = self.call("--help")
        help_text = " ".join(result.stdout.split()).lower()
        self.assertIn("user-message candidates", help_text)
        self.assertNotIn("user evidence", help_text)
        self.assertNotIn("owner evidence", help_text)

    def test_recovers_plan_after_compaction_and_filters_inactive_turns(self) -> None:
        self.write(self.fixture())
        result = self.call("read", "--scope", "user", "--limit", "all", "--json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["meta"]["returned"], 2)
        self.assertEqual(payload["meta"]["total"], 2)
        self.assertEqual(payload["meta"]["compactions"], 1)
        self.assertTrue(payload["meta"]["current_turn_excluded"])
        self.assertEqual(
            [record["kind"] for record in payload["records"]],
            ["chat_message", "planning_selection"],
        )
        self.assertEqual(
            payload["records"][0]["timestamp"],
            "2026-07-22T00:00:02Z",
        )
        self.assertEqual(payload["records"][0]["text"], "Сохрани 42 точно.")
        self.assertEqual(payload["records"][1]["answers"], ["Точный"])
        rendered = json.dumps(payload["records"], ensure_ascii=False)
        self.assertNotIn("Эту ветку откатили", rendered)
        self.assertNotIn("Текущий ход", rendered)

    def test_response_item_user_message_keeps_direct_and_rejects_carriers(self) -> None:
        turn = str(uuid.uuid4())
        timestamp = "2026-07-22T01:00:00Z"

        def response_message(text: str, **extra: Any) -> dict[str, Any]:
            payload: dict[str, Any] = {
                "type": "message",
                "id": "msg-current-shape",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
                "internal_chat_message_metadata_passthrough": {
                    "turn_id": turn,
                    "content_item_kinds": ["user.text"],
                },
            }
            payload.update(extra)
            return self.row("response_item", payload, timestamp)

        self.write(
            [
                self.row(
                    "session_meta", {"id": self.thread}, "2026-07-22T00:00:00Z"
                ),
                self.row(
                    "event_msg",
                    {"type": "task_started", "turn_id": turn},
                    "2026-07-22T00:00:01Z",
                ),
                response_message("Сохрани эту цитату."),
                response_message(
                    "<codex_delegation>\n"
                    "<source_thread_id>11111111-1111-4111-8111-111111111111</source_thread_id>\n"
                    "<input>Сохрани эту цитату.</input>\n"
                    "</codex_delegation>"
                ),
                response_message("Сохрани эту цитату.", origin={"kind": "controller"}),
                response_message(
                    "Сохрани эту цитату.",
                    internal_chat_message_metadata_passthrough={
                        "turn_id": turn,
                        "content_item_kinds": ["user.text"],
                        "audit": {"origin": {"type": "controller"}},
                    },
                ),
                response_message(
                    "Сохрани эту цитату.",
                    origin=["user", "controller"],
                ),
                self.row(
                    "event_msg",
                    {"type": "task_complete", "turn_id": turn},
                    "2026-07-22T01:00:01Z",
                ),
            ]
        )

        result = self.call(
            "read", "--scope", "messages", "--limit", "all", "--include-current-turn", "--json"
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["meta"]["returned"], 1)
        self.assertEqual(payload["records"][0]["text"], "Сохрани эту цитату.")
        self.assertGreaterEqual(
            payload["meta"]["warnings"].count(
                "Ignored a response_item user message without direct-user provenance"
            ),
            4,
        )

    def test_legacy_user_message_rejects_delegation_and_controller_carriers(self) -> None:
        turn = str(uuid.uuid4())
        self.write(
            [
                self.row(
                    "session_meta", {"id": self.thread}, "2026-07-22T00:00:00Z"
                ),
                self.row(
                    "event_msg",
                    {"type": "task_started", "turn_id": turn},
                    "2026-07-22T00:00:01Z",
                ),
                self.row(
                    "event_msg",
                    {"type": "user_message", "message": "Прямые слова владельца."},
                    "2026-07-22T00:00:02Z",
                ),
                self.row(
                    "event_msg",
                    {
                        "type": "user_message",
                        "message": (
                            "<codex_delegation>\n<input>Не слова владельца.</input>\n"
                            "</codex_delegation>"
                        ),
                    },
                    "2026-07-22T00:00:03Z",
                ),
                self.row(
                    "event_msg",
                    {
                        "type": "user_message",
                        "message": "User-visible follow-up другого агента.",
                        "origin": {"kind": "controller"},
                    },
                    "2026-07-22T00:00:04Z",
                ),
                self.row(
                    "event_msg",
                    {"type": "task_complete", "turn_id": turn},
                    "2026-07-22T00:00:05Z",
                ),
            ]
        )

        result = self.call(
            "read", "--scope", "messages", "--limit", "all", "--json"
        )
        payload = json.loads(result.stdout)
        self.assertEqual(
            [record["text"] for record in payload["records"]],
            ["Прямые слова владельца."],
        )
        self.assertEqual(
            payload["meta"]["warnings"].count(
                "Ignored an event_msg user message without direct-user provenance"
            ),
            2,
        )

    def test_deep_response_item_jsonl_fails_closed_without_recursion(self) -> None:
        turn = str(uuid.uuid4())
        timestamp = "2026-07-22T01:00:00Z"
        nested = json.dumps({"kind": "controller"}, ensure_ascii=False)
        for _ in range(1200):
            nested = '{"audit":' + nested + "}"

        payload = {
            "type": "message",
            "id": "msg-deep-carrier",
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Не принимать глубокий carrier."}
            ],
            "internal_chat_message_metadata_passthrough": {
                "turn_id": turn,
                "content_item_kinds": ["user.text"],
            },
        }
        payload_json = json.dumps(payload, ensure_ascii=False)
        payload_json = payload_json[:-1] + ',"audit":' + nested + "}"
        rows = [
            json.dumps(
                self.row("session_meta", {"id": self.thread}, timestamp),
                ensure_ascii=False,
            ),
            json.dumps(
                self.row(
                    "event_msg",
                    {"type": "task_started", "turn_id": turn},
                    timestamp,
                ),
                ensure_ascii=False,
            ),
            json.dumps(
                {"timestamp": timestamp, "type": "response_item"},
                ensure_ascii=False,
            )[:-1]
            + ',"payload":'
            + payload_json
            + "}",
            json.dumps(
                self.row(
                    "event_msg",
                    {"type": "user_message", "message": "Обычный ход."},
                    timestamp,
                ),
                ensure_ascii=False,
            ),
            json.dumps(
                self.row(
                    "event_msg", {"type": "task_complete", "turn_id": turn}, timestamp
                ),
                ensure_ascii=False,
            ),
        ]
        transcript = self.sessions / f"rollout-test-{self.thread}.jsonl"
        transcript.write_text("\n".join(rows) + "\n", encoding="utf-8")

        result = self.call(
            "read", "--scope", "messages", "--limit", "all", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("RecursionError", result.stderr)
        payload = json.loads(result.stdout)
        texts = [record["text"] for record in payload["records"]]
        self.assertEqual(payload["meta"]["returned"], 1)
        self.assertEqual(texts, ["Обычный ход."])
        self.assertIn(
            "Ignored a response_item user message without direct-user provenance",
            payload["meta"]["warnings"],
        )

    def test_malformed_plan_fails_closed(self) -> None:
        self.write(self.fixture(malformed_plan=True))
        result = self.call("read", "--json", expect_ok=False)

        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid request_user_input output", result.stderr)

    def test_missing_timestamp_timezone_fails_closed(self) -> None:
        records = self.fixture()
        records[2]["timestamp"] = "2026-07-22T00:00:02"
        self.write(records)
        result = self.call("read", "--json", expect_ok=False)

        self.assertEqual(result.returncode, 2)
        self.assertIn("has no timezone", result.stderr)

    def test_repair_session_explicitly_reads_historical_transcript(self) -> None:
        historical = str(uuid.uuid4())
        records = self.fixture()
        records[0]["payload"]["id"] = historical
        transcript = self.sessions / f"rollout-test-{historical}.jsonl"
        transcript.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        recall = Path(self.temp.name) / "_ops" / "chat-recall"
        recall.mkdir(parents=True)
        (recall / "historical.md").write_text(
            f"---\nsession: {historical}\n---\n", encoding="utf-8"
        )

        result = self.call(
            "--repair-session",
            historical,
            "search",
            "Сохрани 42",
            "--include-current-turn",
            "--json",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["meta"]["returned"], 1)
        self.assertEqual(payload["records"][0]["text"], "Сохрани 42 точно.")

    def test_repair_session_allows_owner_requested_backfill(self) -> None:
        historical = str(uuid.uuid4())
        records = self.fixture()
        records[0]["payload"]["id"] = historical
        transcript = self.sessions / f"rollout-test-{historical}.jsonl"
        transcript.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        recall = Path(self.temp.name) / "_ops" / "chat-recall"
        recall.mkdir(parents=True)
        (recall / "body-only.md").write_text(
            f"---\nsession: {self.thread}\n---\n\n"
            f"* unknown — \"body says session: {historical}\" "
            "— type: факт | topic: test\n",
            encoding="utf-8",
        )
        result = self.call("--repair-session", historical, "read", "--json")
        payload = json.loads(result.stdout)
        self.assertGreater(payload["meta"]["returned"], 0)

    def test_repair_session_rejects_duplicate_holders(self) -> None:
        historical = str(uuid.uuid4())
        records = self.fixture()
        records[0]["payload"]["id"] = historical
        transcript = self.sessions / f"rollout-test-{historical}.jsonl"
        transcript.write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
            encoding="utf-8",
        )
        recall = Path(self.temp.name) / "_ops" / "chat-recall"
        recall.mkdir(parents=True)
        for name in ("first.md", "second.md"):
            (recall / name).write_text(
                f"---\nsession: {historical}\n---\n", encoding="utf-8"
            )

        result = self.call(
            "--repair-session", historical, "read", "--json", expect_ok=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate holders", result.stderr)


if __name__ == "__main__":
    unittest.main()
