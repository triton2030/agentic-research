"""The one boundary between Graphiti prompts and the local Codex CLI."""

from __future__ import annotations

import asyncio
import copy
import json
import os
import shutil
import signal
import tempfile
from pathlib import Path
from typing import Any

from graphiti_core.llm_client.client import LLMClient
from graphiti_core.llm_client.config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
from graphiti_core.prompts.models import Message
from jsonschema import Draft202012Validator
from pydantic import BaseModel

CODEX_MODEL = "gpt-5.6-luna"
CODEX_EFFORT = "max"
CODEX_MAX_PARALLEL_TURNS = 4
DEFAULT_TIMEOUT_SECONDS = 180.0
BILLING_LEAK_VARS = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")
CHATGPT_CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")


class CodexInvocationError(RuntimeError):
    """Codex did not produce a completed schema-valid turn."""


def strict_codex_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Adapt Pydantic's schema to the strict object subset Codex accepts."""
    strict = copy.deepcopy(schema)

    def visit(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                visit(item)
            return
        if not isinstance(node, dict):
            return

        properties = node.get("properties")
        if node.get("type") == "object" or isinstance(properties, dict):
            node["additionalProperties"] = False
            if isinstance(properties, dict):
                node["required"] = list(properties)
        for value in node.values():
            visit(value)

    visit(strict)
    return strict


def resolve_codex_binary() -> str:
    """Prefer the current ChatGPT.app binary, then the active PATH binary."""
    if CHATGPT_CODEX.is_file():
        return str(CHATGPT_CODEX)
    active = shutil.which("codex")
    if active:
        return active
    raise CodexInvocationError("Codex CLI not found; install or open ChatGPT.app")


def parse_codex_jsonl(stdout: bytes, returncode: int) -> dict[str, Any]:
    """Extract the final structured object from Codex JSONL events."""
    completed = False
    final_text: str | None = None
    fatal: str | None = None

    for raw_line in stdout.decode("utf-8", errors="replace").splitlines():
        if not raw_line.strip():
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError as error:
            raise CodexInvocationError("Codex emitted non-JSON output in --json mode") from error

        event_type = event.get("type")
        if event_type in {"error", "turn.failed"}:
            fatal = str(event.get("message") or event.get("error") or event_type)
        elif event_type == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                final_text = item["text"]
        elif event_type == "turn.completed":
            completed = True

    if fatal:
        raise CodexInvocationError(f"Codex turn failed: {fatal}")
    if returncode != 0:
        raise CodexInvocationError(
            f"Codex exited with status {returncode} without a terminal event"
        )
    if not completed or final_text is None:
        raise CodexInvocationError("Codex did not emit a completed agent message")

    try:
        decoded = json.loads(final_text)
    except json.JSONDecodeError as error:
        raise CodexInvocationError("Codex final message was not a JSON object") from error
    if not isinstance(decoded, dict):
        raise CodexInvocationError("Codex final JSON must be an object")
    return decoded


class CodexSubprocess:
    """Run one ephemeral, read-only Codex turn with a JSON Schema."""

    def __init__(
        self,
        *,
        binary: str | None = None,
        model: str = CODEX_MODEL,
        effort: str = CODEX_EFFORT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.binary = binary or resolve_codex_binary()
        self.model = model
        self.effort = effort
        self.timeout_seconds = timeout_seconds

    def command(self, workdir: Path, schema_path: Path) -> list[str]:
        return [
            self.binary,
            "-m",
            self.model,
            "-c",
            f'model_reasoning_effort="{self.effort}"',
            "-a",
            "never",
            "-s",
            "read-only",
            "-C",
            str(workdir),
            "exec",
            "--strict-config",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--output-schema",
            str(schema_path),
            "--color",
            "never",
            "--json",
            "-",
        ]

    @staticmethod
    def prompt_for(messages: list[Message]) -> str:
        """Serialize Graphiti messages without adding an adapter instruction."""

        return json.dumps(
            [message.model_dump(mode="json") for message in messages],
            ensure_ascii=False,
        )

    async def run(self, messages: list[Message], schema: dict[str, Any]) -> dict[str, Any]:
        prompt = self.prompt_for(messages)
        env = os.environ.copy()
        for name in BILLING_LEAK_VARS:
            env.pop(name, None)

        with tempfile.TemporaryDirectory(prefix="graphiti-codex-") as raw_workdir:
            workdir = Path(raw_workdir)
            schema_path = workdir / "response.schema.json"
            schema_path.write_text(
                json.dumps(strict_codex_schema(schema), ensure_ascii=False), encoding="utf-8"
            )
            process = await asyncio.create_subprocess_exec(
                *self.command(workdir, schema_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                start_new_session=True,
            )
            try:
                stdout, _stderr = await asyncio.wait_for(
                    process.communicate(prompt.encode("utf-8")),
                    timeout=self.timeout_seconds,
                )
            except TimeoutError as error:
                await self._stop_process_group(process)
                raise CodexInvocationError(
                    f"Codex exceeded {self.timeout_seconds:g}s timeout"
                ) from error

        result = parse_codex_jsonl(stdout, process.returncode or 0)
        Draft202012Validator(schema).validate(result)
        return result

    @staticmethod
    async def _stop_process_group(process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        os.killpg(process.pid, signal.SIGTERM)
        try:
            await asyncio.wait_for(process.wait(), timeout=3)
        except TimeoutError:
            os.killpg(process.pid, signal.SIGKILL)
            await process.wait()


class CodexLLMClient(LLMClient):
    """Graphiti LLM client backed by serialized Codex subprocess turns."""

    def __init__(
        self,
        *,
        runner: CodexSubprocess | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_parallel_turns: int = CODEX_MAX_PARALLEL_TURNS,
    ) -> None:
        if max_parallel_turns < 1:
            raise ValueError("max_parallel_turns must be at least 1")
        super().__init__(
            LLMConfig(model=CODEX_MODEL, small_model=CODEX_MODEL),
            cache=False,
        )
        self.runner = runner or CodexSubprocess(timeout_seconds=timeout_seconds)
        self._turn_slots = asyncio.Semaphore(max_parallel_turns)

    async def _generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, Any]:
        del max_tokens, model_size
        if response_model is None:
            raise CodexInvocationError("Graphiti call did not provide a response model")
        schema = response_model.model_json_schema()
        async with self._turn_slots:
            result = await self.runner.run(messages, schema)
        return response_model.model_validate(result).model_dump(mode="json")
