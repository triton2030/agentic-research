"""The one boundary between Graphiti prompts and the local Codex CLI."""

from __future__ import annotations

import asyncio
import copy
import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

from graphiti_core.llm_client.client import LLMClient
from graphiti_core.llm_client.config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
from graphiti_core.prompts.models import Message
from jsonschema import Draft202012Validator
from openai_codex import ApprovalMode, AsyncCodex, CodexConfig, Sandbox
from openai_codex.generated.v2_all import ReasoningEffort
from pydantic import BaseModel

CODEX_MODEL = "gpt-5.6-luna"
CODEX_EFFORT = "low"
CODEX_MAX_PARALLEL_TURNS = 4
DEFAULT_TIMEOUT_SECONDS = 180.0
BILLING_LEAK_VARS = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")
CHATGPT_CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
CODEX_DISABLED_FEATURES = (
    "apps",
    "browser_use",
    "browser_use_external",
    "browser_use_full_cdp_access",
    "computer_use",
    "goals",
    "hooks",
    "image_generation",
    "in_app_browser",
    "memories",
    "multi_agent",
    "plugins",
    "remote_plugin",
    "shell_tool",
    "skill_mcp_dependency_install",
    "skill_search",
    "tool_suggest",
    "view_image",
    "workspace_dependencies",
)
CODEX_CONTEXT_CONFIG = (
    "skills.include_instructions=false",
    "include_permissions_instructions=false",
    "include_apps_instructions=false",
    "include_collaboration_mode_instructions=false",
    "include_environment_context=false",
    "project_doc_max_bytes=0",
    "mcp_servers={}",
)
ALLOWED_CODEX_ITEM_TYPES = {"userMessage", "agentMessage", "reasoning"}


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


class CodexTurnRunner(Protocol):
    """Completion-like transport consumed by the Graphiti LLM client."""

    async def run(self, messages: list[Message], schema: dict[str, Any]) -> dict[str, Any]: ...

    async def aclose(self) -> None: ...


class CodexAppServer:
    """Reuse one Codex app-server while isolating every Graphiti call in a new thread."""

    def __init__(
        self,
        *,
        binary: str | None = None,
        model: str = CODEX_MODEL,
        effort: str = CODEX_EFFORT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        client_factory: Callable[[CodexConfig], AsyncCodex] = AsyncCodex,
    ) -> None:
        self.binary = binary or resolve_codex_binary()
        self.model = model
        self.effort = effort
        self.timeout_seconds = timeout_seconds
        self._client_factory = client_factory
        self._client: AsyncCodex | None = None
        self._client_lock = asyncio.Lock()
        self._workdir_owner = tempfile.TemporaryDirectory(prefix="graphiti-codex-")
        self.workdir = Path(self._workdir_owner.name)
        self._closed = False

    def command(self) -> list[str]:
        """Build the long-lived app-server command with API billing variables removed."""

        command = ["/usr/bin/env"]
        for name in BILLING_LEAK_VARS:
            command.extend(("-u", name))
        command.append(self.binary)
        for feature in CODEX_DISABLED_FEATURES:
            command.extend(("--disable", feature))
        for setting in (f'model_reasoning_effort="{self.effort}"', *CODEX_CONTEXT_CONFIG):
            command.extend(("-c", setting))
        command.extend(("app-server", "--listen", "stdio://"))
        return command

    @staticmethod
    def prompt_for(messages: list[Message]) -> str:
        """Serialize Graphiti messages without adding an adapter instruction."""

        return json.dumps(
            [message.model_dump(mode="json") for message in messages],
            ensure_ascii=False,
        )

    async def _get_client(self) -> AsyncCodex:
        if self._closed:
            raise CodexInvocationError("Codex app-server is closed")
        if self._client is not None:
            return self._client
        async with self._client_lock:
            if self._client is None:
                config = CodexConfig(
                    launch_args_override=tuple(self.command()),
                    cwd=str(self.workdir),
                )
                client = self._client_factory(config)
                await client.__aenter__()
                self._client = client
        return self._client

    @staticmethod
    def _decode_result(result: Any) -> dict[str, Any]:
        status = getattr(result.status, "value", result.status)
        if status != "completed" or result.error is not None:
            raise CodexInvocationError(f"Codex turn ended with status {status}")

        item_types: list[str] = []
        answer_count = 0
        for item in result.items:
            payload = getattr(item, "root", item)
            item_type = getattr(payload, "type", None)
            item_types.append(str(item_type or "missing item type"))
            if item_type == "agentMessage":
                answer_count += 1
        forbidden = [
            item_type for item_type in item_types if item_type not in ALLOWED_CODEX_ITEM_TYPES
        ]
        if forbidden:
            raise CodexInvocationError(f"Codex emitted a forbidden item: {forbidden[0]}")
        if answer_count != 1:
            raise CodexInvocationError(
                f"Codex emitted {answer_count} completed answers; expected one"
            )
        if not isinstance(result.final_response, str):
            raise CodexInvocationError("Codex did not emit a completed agent message")

        try:
            decoded = json.loads(result.final_response)
        except json.JSONDecodeError as error:
            raise CodexInvocationError("Codex final message was not a JSON object") from error
        if not isinstance(decoded, dict):
            raise CodexInvocationError("Codex final JSON must be an object")
        return decoded

    async def run(self, messages: list[Message], schema: dict[str, Any]) -> dict[str, Any]:
        client = await self._get_client()
        prompt = self.prompt_for(messages)
        try:
            thread = await client.thread_start(
                cwd=str(self.workdir),
                sandbox=Sandbox.read_only,
                approval_mode=ApprovalMode.deny_all,
                model=self.model,
                ephemeral=True,
            )
            try:
                result = await asyncio.wait_for(
                    thread.run(
                        prompt,
                        model=self.model,
                        effort=ReasoningEffort(self.effort),
                        output_schema=strict_codex_schema(schema),
                        sandbox=Sandbox.read_only,
                        approval_mode=ApprovalMode.deny_all,
                    ),
                    timeout=self.timeout_seconds,
                )
            except TimeoutError as error:
                raise CodexInvocationError(
                    f"Codex exceeded {self.timeout_seconds:g}s timeout"
                ) from error
        except CodexInvocationError:
            raise
        except Exception as error:
            raise CodexInvocationError(f"Codex app-server turn failed: {error}") from error

        decoded = self._decode_result(result)
        Draft202012Validator(schema).validate(decoded)
        return decoded

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        async with self._client_lock:
            client, self._client = self._client, None
        if client is not None:
            await client.close()
        self._workdir_owner.cleanup()


class CodexLLMClient(LLMClient):
    """Graphiti LLM client backed by bounded turns on one Codex app-server."""

    def __init__(
        self,
        *,
        runner: CodexTurnRunner | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_parallel_turns: int = CODEX_MAX_PARALLEL_TURNS,
    ) -> None:
        if max_parallel_turns < 1:
            raise ValueError("max_parallel_turns must be at least 1")
        super().__init__(
            LLMConfig(model=CODEX_MODEL, small_model=CODEX_MODEL),
            cache=False,
        )
        self.runner = runner or CodexAppServer(timeout_seconds=timeout_seconds)
        self._turn_slots = asyncio.Semaphore(max_parallel_turns)

    async def aclose(self) -> None:
        await self.runner.aclose()

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
