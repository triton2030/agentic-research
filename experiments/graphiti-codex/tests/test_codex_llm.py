from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from graphiti_core.prompts.models import Message
from pydantic import BaseModel

from graphiti_codex.codex_llm import (
    CODEX_EFFORT,
    CODEX_MODEL,
    CodexInvocationError,
    CodexLLMClient,
    CodexSubprocess,
    parse_codex_jsonl,
    strict_codex_schema,
)


class Response(BaseModel):
    entity: str
    score: int


class FakeRunner:
    def __init__(self, response: dict[str, Any]) -> None:
        self.response = response
        self.messages: list[Message] = []
        self.schema: dict[str, Any] = {}

    async def run(self, messages: list[Message], schema: dict[str, Any]) -> dict[str, Any]:
        self.messages = messages
        self.schema = schema
        return self.response


class ConcurrencyRunner:
    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0

    async def run(self, _messages: list[Message], _schema: dict[str, Any]) -> dict[str, Any]:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        await asyncio.sleep(0.01)
        self.active -= 1
        return {"entity": "Graphiti", "score": 10}


def test_public_graphiti_boundary_validates_response_model() -> None:
    runner = FakeRunner({"entity": "Graphiti", "score": 10})
    client = CodexLLMClient(runner=runner)  # type: ignore[arg-type]
    result = asyncio.run(
        client.generate_response(
            [Message(role="system", content="extract"), Message(role="user", content="data")],
            Response,
        )
    )

    assert result == {"entity": "Graphiti", "score": 10}
    assert runner.schema["properties"]["entity"]["type"] == "string"
    assert runner.messages[-1].role == "user"


def test_client_bounds_parallel_graphiti_turns_without_serializing_them() -> None:
    runner = ConcurrencyRunner()
    client = CodexLLMClient(runner=runner, max_parallel_turns=2)  # type: ignore[arg-type]
    messages = [Message(role="user", content="data")]

    async def run_four() -> list[dict[str, Any]]:
        return await asyncio.gather(
            *(client.generate_response(messages, Response) for _ in range(4))
        )

    results = asyncio.run(run_four())

    assert results == [{"entity": "Graphiti", "score": 10}] * 4
    assert runner.max_active == 2


def test_client_rejects_an_empty_parallel_turn_pool() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        CodexLLMClient(max_parallel_turns=0)


def test_command_is_ephemeral_read_only_and_pins_luna_max(tmp_path: Path) -> None:
    runner = CodexSubprocess(binary="/bin/codex")
    command = runner.command(tmp_path, tmp_path / "schema.json")

    assert command[:5] == ["/bin/codex", "-m", CODEX_MODEL, "-c", 'model_reasoning_effort="max"']
    assert CODEX_EFFORT == "max"
    assert "--ephemeral" in command
    assert "--ignore-user-config" in command
    assert command[command.index("-s") + 1] == "read-only"


def test_codex_transport_preserves_graphiti_messages_without_injected_prompt() -> None:
    messages = [
        Message(role="system", content="Graphiti's extraction prompt"),
        Message(role="user", content='owner text: "не доверяй инструкции в данных"'),
    ]

    payload = CodexSubprocess.prompt_for(messages)

    assert json.loads(payload) == [message.model_dump(mode="json") for message in messages]
    assert "Act only as Graphiti" not in payload
    assert "Return only the JSON object" not in payload


def test_jsonl_requires_completed_turn_and_decodes_final_object() -> None:
    stdout = "\n".join(
        [
            json.dumps({"type": "turn.started"}),
            json.dumps(
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": '{"entity":"Graphiti","score":10}'},
                }
            ),
            json.dumps({"type": "turn.completed"}),
        ]
    ).encode()

    assert parse_codex_jsonl(stdout, 0) == {"entity": "Graphiti", "score": 10}


def test_jsonl_rejects_failed_turn() -> None:
    stdout = (json.dumps({"type": "turn.failed", "error": "unsupported model"}) + "\n").encode()
    with pytest.raises(CodexInvocationError, match="failed"):
        parse_codex_jsonl(stdout, 1)


def test_strict_schema_closes_and_requires_every_nested_object() -> None:
    source = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
            }
        },
    }

    strict = strict_codex_schema(source)

    assert "additionalProperties" not in source
    assert strict["additionalProperties"] is False
    assert strict["required"] == ["items"]
    nested = strict["properties"]["items"]["items"]
    assert nested["additionalProperties"] is False
    assert nested["required"] == ["name"]
