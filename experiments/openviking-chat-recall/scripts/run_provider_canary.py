#!/usr/bin/env python3
"""Run the Wave 6 F4 synthetic-provider canary.

The canary has one small effect boundary: ``ProviderAdapter``.  The fake
adapter exercises failure and usage policy without a network call; the Codex
adapter is the only path that can start the one real synthetic request.
Nothing below reads the chat-recall corpus or the F1-F3 build inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence


SCHEMA = "openviking-chat-recall/provider-canary.v1"
CAPTURE_SCHEMA = "openviking-chat-recall/provider-canary-capture.v1"
REDACTED = "[REDACTED]"
DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_THINKING = "max"
DEFAULT_TIMEOUT_SECONDS = 90.0
DEFAULT_ARTIFACT_DIR = Path(
    "experiments/openviking-chat-recall/artifacts/full-build/provider-canary"
)
PUBLIC_NONCE_RE = re.compile(r"^f4-public-[0-9a-f]{16}$")
SAFE_ADDRESS_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,256}$")

PUBLIC_RECEIPT = "provider-canary-receipt.json"
CAPTURED_RESULT = "captured-result.json"
RENDER_ONE = "receipt-render-1.json"
RENDER_TWO = "receipt-render-2.json"
OWNED_ARTIFACT_NAMES = frozenset(
    {PUBLIC_RECEIPT, CAPTURED_RESULT, RENDER_ONE, RENDER_TWO}
)

# These are intentionally short path/content fragments.  The canary never
# opens them; the scanner uses them to fail closed if a future change leaks a
# private source address or deterministic evidence file into a public receipt.
FORBIDDEN_PUBLIC_FRAGMENTS = (
    "_ops/chat-recall/raw",
    "records.jsonl",
    "coverage-input.json",
    "partition-manifest.json",
    "input.jsonl",
    "source-01.md",
    "source-02.md",
)
FORBIDDEN_PUBLIC_KEYS = (
    "prompt",
    "transcript",
    "raw_events",
    "raw_jsonl",
    "credentials",
    "environment",
    "response_prose",
)
SAFE_ENV_NAMES = frozenset(
    {
        "PATH",
        "HOME",
        "CODEX_HOME",
        "TMPDIR",
        "LANG",
        "LC_ALL",
        "TERM",
        "NO_COLOR",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
    }
)
SECRET_ENV_RE = re.compile(
    r"(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTHORIZATION)",
    re.IGNORECASE,
)


class CanaryError(ValueError):
    """Raised for a local contract or public-artifact violation."""


class FakeTransientError(RuntimeError):
    """A deterministic retryable fake-provider failure."""


class FakeTerminalError(RuntimeError):
    """A deterministic terminal fake-provider failure."""


class FakeTimeoutError(TimeoutError):
    """A deterministic fake-provider timeout."""


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    requests: int = 1

    def __post_init__(self) -> None:
        for name in ("input_tokens", "output_tokens", "total_tokens", "requests"):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise CanaryError(f"usage.{name} must be a non-negative integer")

    def add(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
            self.total_tokens + other.total_tokens,
            self.requests + other.requests,
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "requests": self.requests,
        }


@dataclass(frozen=True)
class SyntheticRequest:
    nonce: str
    payload: Mapping[str, Any]
    prompt: str
    provider_input_digest: str


@dataclass(frozen=True)
class ProviderResult:
    output: Mapping[str, Any]
    usage: Usage | None


class ProviderAdapter(Protocol):
    """The only capability needed by retry/accounting policy."""

    def request(self, request: SyntheticRequest) -> ProviderResult:
        ...


@dataclass(frozen=True)
class FakeOutcome:
    kind: str
    output: Mapping[str, Any] | None = None
    usage: Usage | None = None


class FakeProviderAdapter:
    """Scriptable fake preserving request count and failure semantics."""

    def __init__(self, outcomes: Sequence[FakeOutcome]) -> None:
        self._outcomes = tuple(outcomes)
        self.requests: list[SyntheticRequest] = []

    def request(self, request: SyntheticRequest) -> ProviderResult:
        index = len(self.requests)
        self.requests.append(request)
        if index >= len(self._outcomes):
            raise FakeTerminalError("fake outcome sequence exhausted")
        outcome = self._outcomes[index]
        if outcome.kind == "success":
            if outcome.output is None:
                raise CanaryError("fake success must provide output")
            return ProviderResult(outcome.output, outcome.usage)
        if outcome.kind == "transient":
            raise FakeTransientError("synthetic transient failure")
        if outcome.kind == "terminal":
            raise FakeTerminalError("synthetic terminal failure")
        if outcome.kind == "timeout":
            raise FakeTimeoutError("synthetic timeout")
        raise CanaryError(f"unknown fake outcome: {outcome.kind!r}")


@dataclass(frozen=True)
class RetryPolicy:
    max_transient_retries: int = 1

    def __post_init__(self) -> None:
        if self.max_transient_retries < 0:
            raise CanaryError("max_transient_retries must be non-negative")


@dataclass(frozen=True)
class AdapterRun:
    status: str
    attempts: int
    usage: Usage | None
    logs: tuple[dict[str, Any], ...]
    output: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ParsedEventStream:
    event_types: Mapping[str, int]
    response_text: str | None
    usage: Usage | None
    run_address: Mapping[str, str] | None
    event_model: str | None
    line_count: int
    invalid_line_count: int
    raw_secret_seen: bool


@dataclass(frozen=True)
class RealRun:
    status: str
    attempts: int
    elapsed_category: str
    usage: Usage | None
    parsed: ParsedEventStream | None
    structured_result: dict[str, str] | None
    raw_secret_seen: bool
    auth_completed: bool
    error_category: str | None


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def redact_value(value: Any, secrets_to_redact: Iterable[str]) -> Any:
    """Return a recursively redacted copy without mutating caller data."""

    secrets_list = tuple(secret for secret in secrets_to_redact if secret)
    if isinstance(value, str):
        result = value
        for secret in secrets_list:
            result = result.replace(secret, REDACTED)
        return result
    if isinstance(value, Mapping):
        return {
            str(key): redact_value(item, secrets_list) for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_value(item, secrets_list) for item in value]
    if isinstance(value, tuple):
        return [redact_value(item, secrets_list) for item in value]
    return value


def build_synthetic_request(public_nonce: str, raw_secret: str) -> SyntheticRequest:
    if not PUBLIC_NONCE_RE.fullmatch(public_nonce):
        raise CanaryError("public nonce has an invalid format")
    if not raw_secret or raw_secret == public_nonce:
        raise CanaryError("raw secret canary must be non-empty and distinct")
    payload = {
        "protocol": "f4-synthetic-provider-canary-v1",
        "nonce": public_nonce,
        "payload": "public synthetic payload",
        "secret_canary": raw_secret,
    }
    redacted_payload = redact_value(payload, (raw_secret,))
    prompt_payload = json.dumps(
        redacted_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    prompt = (
        "Synthetic canary only. Return exactly one JSON object with no markdown or "
        "prose. Copy the public nonce exactly and copy the redacted marker exactly. "
        f"Input payload: {prompt_payload}\n"
        'Output shape: {"nonce":"<public nonce>","redacted_marker":"[REDACTED]"}'
    )
    if raw_secret in prompt or raw_secret in json.dumps(redacted_payload):
        raise CanaryError("raw secret survived redaction")
    return SyntheticRequest(
        nonce=public_nonce,
        payload=redacted_payload,
        prompt=prompt,
        provider_input_digest=sha256_text(prompt),
    )


def execute_with_retry(
    adapter: ProviderAdapter,
    request: SyntheticRequest,
    policy: RetryPolicy = RetryPolicy(),
) -> AdapterRun:
    """Apply one transient retry while keeping timeout/terminal failures final."""

    logs: list[dict[str, Any]] = []
    attempts = 0
    aggregate: Usage | None = None
    while True:
        attempts += 1
        logs.append({"event": "request.started", "attempt": attempts})
        try:
            result = adapter.request(request)
        except FakeTransientError:
            logs.append({"event": "request.failed", "attempt": attempts, "reason": "transient"})
            if attempts <= policy.max_transient_retries:
                logs.append({"event": "request.retrying", "attempt": attempts})
                continue
            return AdapterRun("terminal_failure", attempts, aggregate, tuple(logs))
        except FakeTimeoutError:
            logs.append({"event": "request.failed", "attempt": attempts, "reason": "timeout"})
            return AdapterRun("timeout", attempts, aggregate, tuple(logs))
        except FakeTerminalError:
            logs.append({"event": "request.failed", "attempt": attempts, "reason": "terminal"})
            return AdapterRun("terminal_failure", attempts, aggregate, tuple(logs))

        if result.usage is not None:
            aggregate = result.usage if aggregate is None else aggregate.add(result.usage)
        logs.append(
            {
                "event": "request.completed",
                "attempt": attempts,
                "status": "success",
                "usage": result.usage.as_dict() if result.usage else None,
            }
        )
        return AdapterRun("success", attempts, aggregate, tuple(logs), result.output)


def fake_probe_matrix(request: SyntheticRequest) -> dict[str, AdapterRun]:
    usage = Usage(input_tokens=11, output_tokens=7, total_tokens=18)
    return {
        "success": execute_with_retry(
            FakeProviderAdapter(
                [FakeOutcome("success", {"nonce": request.nonce}, usage)]
            ),
            request,
        ),
        "transient_retry_then_success": execute_with_retry(
            FakeProviderAdapter(
                [
                    FakeOutcome("transient"),
                    FakeOutcome("success", {"nonce": request.nonce}, usage),
                ]
            ),
            request,
        ),
        "terminal_failure": execute_with_retry(
            FakeProviderAdapter([FakeOutcome("terminal")]), request
        ),
        "timeout": execute_with_retry(
            FakeProviderAdapter([FakeOutcome("timeout")]), request
        ),
    }


def _safe_address(value: Any) -> str | None:
    if isinstance(value, str) and SAFE_ADDRESS_RE.fullmatch(value):
        return value
    return None


def _usage_from_mapping(value: Any) -> Usage | None:
    if not isinstance(value, Mapping):
        return None
    aliases = {
        "input_tokens": ("input_tokens", "prompt_tokens"),
        "output_tokens": ("output_tokens", "completion_tokens"),
        "total_tokens": ("total_tokens",),
    }
    values: dict[str, int] = {}
    for name, keys in aliases.items():
        for key in keys:
            candidate = value.get(key)
            if isinstance(candidate, int) and candidate >= 0:
                values[name] = candidate
                break
    if not all(name in values for name in aliases):
        return None
    return Usage(values["input_tokens"], values["output_tokens"], values["total_tokens"])


def _find_usage(event: Mapping[str, Any]) -> Usage | None:
    direct = _usage_from_mapping(event.get("usage"))
    if direct is not None:
        return direct
    for key in ("result", "response", "data"):
        child = event.get(key)
        if isinstance(child, Mapping):
            usage = _usage_from_mapping(child.get("usage"))
            if usage is not None:
                return usage
    return None


def _extract_agent_text(event: Mapping[str, Any]) -> str | None:
    item = event.get("item")
    if isinstance(item, Mapping) and item.get("type") in {
        "agent_message",
        "assistant_message",
        "message",
    }:
        text = item.get("text")
        if isinstance(text, str):
            return text
        content = item.get("content")
        if isinstance(content, str):
            return content
    for key in ("output_text", "final_message"):
        text = event.get(key)
        if isinstance(text, str):
            return text
    return None


def _extract_run_address(event: Mapping[str, Any]) -> dict[str, str] | None:
    address: dict[str, str] = {}
    for key in ("thread_id", "turn_id", "run_id", "id"):
        value = _safe_address(event.get(key))
        if value is not None and key != "id":
            address[key] = value
    return address or None


def _extract_event_model(event: Mapping[str, Any]) -> str | None:
    for key in ("model", "model_name", "model_id"):
        value = event.get(key)
        if isinstance(value, str) and SAFE_ADDRESS_RE.fullmatch(value):
            return value
    return None


def parse_json_event_stream(raw_jsonl: str, raw_secret: str | None = None) -> ParsedEventStream:
    """Parse JSONL in memory and retain only sanitized, addressable summaries."""

    event_types: Counter[str] = Counter()
    response_text: str | None = None
    usage: Usage | None = None
    run_address: dict[str, str] | None = None
    event_model: str | None = None
    invalid_lines = 0
    line_count = 0
    raw_secret_seen = bool(raw_secret and raw_secret in raw_jsonl)
    for line in raw_jsonl.splitlines():
        if not line.strip():
            continue
        line_count += 1
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            invalid_lines += 1
            continue
        if not isinstance(event, Mapping):
            invalid_lines += 1
            continue
        event_type = event.get("type")
        if isinstance(event_type, str):
            event_types[event_type] += 1
        candidate_text = _extract_agent_text(event)
        if candidate_text is not None:
            response_text = candidate_text
        candidate_usage = _find_usage(event)
        if candidate_usage is not None:
            usage = candidate_usage
        candidate_address = _extract_run_address(event)
        if candidate_address:
            run_address = candidate_address
        candidate_model = _extract_event_model(event)
        if candidate_model is not None:
            event_model = candidate_model
    return ParsedEventStream(
        event_types=dict(sorted(event_types.items())),
        response_text=response_text,
        usage=usage,
        run_address=run_address,
        event_model=event_model,
        line_count=line_count,
        invalid_line_count=invalid_lines,
        raw_secret_seen=raw_secret_seen,
    )


def parse_structured_result(text: str | None, expected_nonce: str) -> dict[str, str] | None:
    if not text:
        return None
    candidate = text.strip()
    if candidate.startswith("```") and candidate.endswith("```"):
        lines = candidate.splitlines()
        if len(lines) < 3:
            return None
        candidate = "\n".join(lines[1:-1]).strip()
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(value, Mapping):
        return None
    nonce = value.get("nonce")
    marker = value.get("redacted_marker")
    if not isinstance(nonce, str) or not isinstance(marker, str):
        return None
    return {"nonce": nonce, "redacted_marker": marker}


def _elapsed_category(seconds: float) -> str:
    if seconds < 5:
        return "lt_5s"
    if seconds < 30:
        return "5_30s"
    if seconds < 120:
        return "30_120s"
    return "gte_120s"


def build_child_env(temp_root: Path) -> dict[str, str]:
    """Pass only non-secret operational variables; never pass a canary secret."""

    child_env = {
        name: value
        for name, value in os.environ.items()
        if name in SAFE_ENV_NAMES and not SECRET_ENV_RE.search(name)
    }
    child_env["TMPDIR"] = str(temp_root)
    return child_env


def _schema_for_nonce(nonce: str) -> dict[str, Any]:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "additionalProperties": False,
        "required": ["nonce", "redacted_marker"],
        "properties": {
            "nonce": {"const": nonce},
            "redacted_marker": {"const": REDACTED},
        },
    }


def _sanitized_argv_shape() -> list[str]:
    return [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--model",
        DEFAULT_MODEL,
        "-c",
        'model_reasoning_effort="max"',
        "--sandbox",
        "read-only",
        "--cd",
        "<temporary-root>",
        "--output-schema",
        "<temporary-root>/output-schema.json",
        "--json",
        "-",
    ]


def _sanitized_envelope(timeout_seconds: float) -> dict[str, Any]:
    return {
        "command": "codex exec",
        "interactive": False,
        "ephemeral": True,
        "isolated_cwd": "<temporary-root>",
        "sandbox": "read-only",
        "output_schema": "<temporary-root>/output-schema.json",
        "json_events": True,
        "prompt_transport": "stdin",
        "timeout_seconds": timeout_seconds,
        "ignore_user_config": True,
        "model_flag": DEFAULT_MODEL,
        "thinking_config_key": "model_reasoning_effort",
        "thinking": DEFAULT_THINKING,
    }


def run_real_canary(
    request: SyntheticRequest,
    raw_secret: str,
    *,
    codex_path: str = "codex",
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> RealRun:
    if timeout_seconds <= 0:
        raise CanaryError("timeout must be positive")
    with tempfile.TemporaryDirectory(prefix="f4-provider-canary-") as temp_dir:
        temp_root = Path(temp_dir)
        schema_path = temp_root / "output-schema.json"
        schema_path.write_bytes(canonical_bytes(_schema_for_nonce(request.nonce)))
        argv = [
            codex_path,
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--model",
            DEFAULT_MODEL,
            "-c",
            'model_reasoning_effort="max"',
            "--sandbox",
            "read-only",
            "--cd",
            str(temp_root),
            "--output-schema",
            str(schema_path),
            "--json",
            "-",
        ]
        started = time.monotonic()
        try:
            completed = subprocess.run(
                argv,
                cwd=temp_root,
                env=build_child_env(temp_root),
                input=request.prompt,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            combined = ""
            for value in (exc.stdout, exc.stderr):
                if isinstance(value, bytes):
                    combined += value.decode("utf-8", errors="replace")
                elif isinstance(value, str):
                    combined += value
            raw_seen = raw_secret in combined
            return RealRun(
                status="timeout",
                attempts=1,
                elapsed_category="timeout",
                usage=None,
                parsed=None,
                structured_result=None,
                raw_secret_seen=raw_seen,
                auth_completed=False,
                error_category="timeout",
            )
        elapsed = time.monotonic() - started
        parsed = parse_json_event_stream(completed.stdout, raw_secret)
        raw_seen = parsed.raw_secret_seen or raw_secret in completed.stderr
        if parsed.invalid_line_count:
            return RealRun(
                status="invalid_event_stream",
                attempts=1,
                elapsed_category=_elapsed_category(elapsed),
                usage=parsed.usage,
                parsed=parsed,
                structured_result=None,
                raw_secret_seen=raw_seen,
                auth_completed=False,
                error_category="invalid_jsonl",
            )
        if completed.returncode != 0:
            return RealRun(
                status="provider_error",
                attempts=1,
                elapsed_category=_elapsed_category(elapsed),
                usage=parsed.usage,
                parsed=parsed,
                structured_result=None,
                raw_secret_seen=raw_seen,
                auth_completed=False,
                error_category="nonzero_exit",
            )
        structured = parse_structured_result(parsed.response_text, request.nonce)
        exact_round_trip = (
            structured is not None
            and structured.get("nonce") == request.nonce
            and structured.get("redacted_marker") == REDACTED
        )
        return RealRun(
            status="completed",
            attempts=1,
            elapsed_category=_elapsed_category(elapsed),
            usage=parsed.usage,
            parsed=parsed,
            structured_result=structured,
            raw_secret_seen=raw_seen,
            auth_completed=exact_round_trip and not raw_seen,
            error_category=None if exact_round_trip else "invalid_structured_output",
        )


def _relative_or_placeholder(path: Path, repo_root: Path | None = None) -> str:
    if repo_root is not None:
        try:
            return path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            pass
    return "<temporary-root>/" + path.name


def _ensure_no_symlink_path(root: Path, child: Path) -> None:
    root_lexical = root.absolute()
    child_lexical = child.absolute()
    try:
        relative = child_lexical.relative_to(root_lexical)
    except ValueError as exc:
        raise CanaryError("artifact path escapes generated root") from exc
    root_resolved = root.resolve(strict=False)
    child_resolved = child.resolve(strict=False)
    try:
        child_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise CanaryError("artifact path resolves outside generated root") from exc
    current = root_lexical
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise CanaryError(f"symlink in generated artifact path: {current.name}")


def prepare_artifact_root(root: Path) -> None:
    if root.exists() and root.is_symlink():
        raise CanaryError("generated artifact root is a symlink")
    root.mkdir(parents=True, exist_ok=True)
    if root.is_symlink():
        raise CanaryError("generated artifact root became a symlink")
    for name in OWNED_ARTIFACT_NAMES:
        path = root / name
        if path.is_symlink():
            raise CanaryError(f"owned artifact is a symlink: {name}")
        if path.exists() and not path.is_file():
            raise CanaryError(f"owned artifact is not a regular file: {name}")


def write_owned_json(root: Path, name: str, value: Any) -> Path:
    if name not in OWNED_ARTIFACT_NAMES:
        raise CanaryError(f"unowned artifact name: {name}")
    path = root / name
    _ensure_no_symlink_path(root, path)
    path.write_bytes(canonical_bytes(value))
    return path


def scan_public_texts(root: Path, raw_secret: str | None = None) -> dict[str, Any]:
    if not root.exists() or root.is_symlink():
        raise CanaryError("cannot scan missing or symlinked artifact root")
    files: list[str] = []
    violations: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            violations.append(f"symlink:{path.name}")
            continue
        if not path.is_file():
            continue
        relative_name = path.relative_to(root).as_posix()
        files.append(relative_name)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            violations.append(f"non-utf8:{path.name}")
            continue
        for fragment in FORBIDDEN_PUBLIC_FRAGMENTS:
            if fragment in relative_name:
                violations.append(f"forbidden-path:{relative_name}:{fragment}")
            if fragment in text:
                violations.append(f"forbidden-fragment:{path.name}:{fragment}")
        if raw_secret and raw_secret in text:
            violations.append(f"raw-secret:{path.name}")
        for key in FORBIDDEN_PUBLIC_KEYS:
            if re.search(rf'"{re.escape(key)}"\s*:', text):
                violations.append(f"forbidden-key:{path.name}:{key}")
    return {
        "status": "pass" if not violations else "fail",
        "files_scanned": files,
        "violations": violations,
    }


def _fake_summary(run: AdapterRun) -> dict[str, Any]:
    return {
        "status": run.status,
        "attempts": run.attempts,
        "requests": run.attempts,
        "usage": run.usage.as_dict() if run.usage else None,
        "log_schema": all(
            isinstance(event, Mapping)
            and isinstance(event.get("event"), str)
            and isinstance(event.get("attempt"), int)
            for event in run.logs
        ),
    }


def _safe_result(value: Mapping[str, Any] | None, expected_nonce: str) -> dict[str, str] | None:
    if value is None:
        return None
    parsed = parse_structured_result(json.dumps(value, ensure_ascii=False), expected_nonce)
    if parsed is None:
        return None
    return parsed


def render_captured_result(result: Mapping[str, str]) -> dict[str, Any]:
    return {
        "schema": CAPTURE_SCHEMA,
        "result": {
            "nonce": result["nonce"],
            "redacted_marker": result["redacted_marker"],
        },
        "result_digest": digest(result),
    }


def build_receipt(
    *,
    cli_version: str,
    envelope: Mapping[str, Any],
    command_digest: str,
    config_digest: str,
    request: SyntheticRequest | None,
    fake_runs: Mapping[str, AdapterRun],
    real_run: RealRun,
    captured_result_saved: bool,
    render_identical: bool | None,
    artifact_scan: Mapping[str, Any],
    repo_root: Path | None = None,
    artifact_root: Path | None = None,
    runtime_schema_opened: bool = True,
) -> dict[str, Any]:
    parsed = real_run.parsed
    result = real_run.structured_result
    nonce_round_trip = "not_available"
    if result is not None and request is not None:
        nonce_round_trip = (
            "exact"
            if result.get("nonce") == request.nonce
            and result.get("redacted_marker") == REDACTED
            else "not_exact"
        )
    usage_status = "addressable" if real_run.usage is not None else "unknown"
    fake_ok = all(
        (
            name == "success" and run.status == "success" and run.attempts == 1
        )
        or (
            name == "transient_retry_then_success"
            and run.status == "success"
            and run.attempts == 2
        )
        or (name == "terminal_failure" and run.status == "terminal_failure")
        or (name == "timeout" and run.status == "timeout")
        for name, run in fake_runs.items()
    )
    route_addressable = parsed is not None and parsed.event_model is not None
    route_drift = route_addressable and parsed.event_model != DEFAULT_MODEL
    if real_run.status == "completed" and real_run.auth_completed:
        if real_run.raw_secret_seen:
            verdict = "FAIL"
        elif route_drift:
            verdict = "FAIL"
        elif not route_addressable:
            verdict = "UNKNOWN"
        elif not fake_ok:
            verdict = "FAIL"
        elif real_run.usage is None:
            verdict = "UNKNOWN"
        elif not captured_result_saved or render_identical is not True:
            verdict = "FAIL"
        elif artifact_scan.get("status") != "pass":
            verdict = "FAIL"
        else:
            verdict = "PASS"
    elif real_run.status == "timeout":
        verdict = "UNKNOWN"
    elif real_run.status.startswith("unknown"):
        verdict = "UNKNOWN"
    else:
        verdict = "FAIL"

    opened_paths: list[dict[str, str]] = []
    if runtime_schema_opened:
        opened_paths.append(
            {
                "path": "<temporary-root>/output-schema.json",
                "operation": "runtime-schema",
            }
        )
    if artifact_root is not None:
        opened_paths.extend(
            {
                "path": _relative_or_placeholder(artifact_root / name, repo_root),
                "operation": "public-artifact-write",
            }
            for name in (CAPTURED_RESULT, RENDER_ONE, RENDER_TWO, PUBLIC_RECEIPT)
            if (
                name == PUBLIC_RECEIPT
                or captured_result_saved
            )
        )
    return {
        "schema": SCHEMA,
        "selected_model": DEFAULT_MODEL,
        "thinking": DEFAULT_THINKING,
        "cli_version": cli_version,
        "envelope": dict(envelope),
        "command_digest": command_digest,
        "config_digest": config_digest,
        "real_call": {
            "status": real_run.status,
            "attempts": real_run.attempts,
            "elapsed_category": real_run.elapsed_category,
            "usage": real_run.usage.as_dict() if real_run.usage else None,
            "usage_status": usage_status,
            "request_count": 1,
            "error_category": real_run.error_category,
        },
        "auth": {
            "completed_real_call": real_run.auth_completed,
            "config_inspection_only": False,
            "nonce_round_trip": nonce_round_trip,
        },
        "egress": {
            "synthetic_only": True,
            "provider_input": "public_nonce_and_redacted_payload",
            "repo_paths_opened": [],
            "restricted_source_paths_opened": [],
        },
        "redaction": {
            "marker": REDACTED,
            "provider_input_contains_marker": request is None or REDACTED in request.prompt,
            "provider_input_contains_raw_secret": False,
            "provider_output_contains_raw_secret": real_run.raw_secret_seen,
            "artifacts_contain_raw_secret": artifact_scan.get("status") != "pass",
            "subprocess_env_contains_canary": False,
        },
        "usage_accounting": {
            "addressable": real_run.usage is not None,
            "token_usage": real_run.usage.as_dict() if real_run.usage else None,
            "dollar_cost": None,
        },
        "output": {
            "output_digest": digest(result) if result else None,
            "nonce_digest": sha256_text(request.nonce) if request is not None else None,
            "run_address": parsed.run_address if parsed else None,
            "event_model": parsed.event_model if parsed else None,
            "event_line_count": parsed.line_count if parsed else 0,
            "event_type_counts": parsed.event_types if parsed else {},
            "raw_transcript_saved": False,
        },
        "captured_result": {
            "saved": captured_result_saved,
            "receipt_renders_byte_identical": render_identical,
        },
        "fake_probes": {name: _fake_summary(run) for name, run in fake_runs.items()},
        "opened_paths": opened_paths,
        "artifact_privacy_scan": dict(artifact_scan),
        "verdict": verdict,
    }


def validate_receipt(value: Mapping[str, Any]) -> None:
    required = {
        "schema",
        "selected_model",
        "thinking",
        "cli_version",
        "envelope",
        "command_digest",
        "config_digest",
        "real_call",
        "auth",
        "egress",
        "redaction",
        "usage_accounting",
        "output",
        "captured_result",
        "fake_probes",
        "opened_paths",
        "artifact_privacy_scan",
        "verdict",
    }
    if set(value) != required:
        raise CanaryError("public receipt schema drift")
    if value["schema"] != SCHEMA:
        raise CanaryError("public receipt schema version mismatch")
    if value["selected_model"] != DEFAULT_MODEL or value["thinking"] != DEFAULT_THINKING:
        raise CanaryError("selected model/thinking is not addressable")
    if not isinstance(value["cli_version"], str) or not value["cli_version"]:
        raise CanaryError("CLI version is not addressable")
    real_call = value["real_call"]
    if not isinstance(real_call, Mapping) or real_call.get("attempts") != 1:
        raise CanaryError("real canary must have exactly one attempt")
    usage = real_call.get("usage")
    if real_call.get("usage_status") == "unknown" and usage is not None:
        raise CanaryError("unknown usage must remain null")
    if value["auth"].get("config_inspection_only") is not False:
        raise CanaryError("auth cannot be config-only")
    if value["egress"].get("synthetic_only") is not True:
        raise CanaryError("egress is not synthetic-only")
    if value["egress"].get("repo_paths_opened") != []:
        raise CanaryError("repo inputs were opened")
    redaction = value["redaction"]
    if redaction.get("provider_input_contains_raw_secret") is not False:
        raise CanaryError("raw secret was present in provider input")
    if redaction.get("subprocess_env_contains_canary") is not False:
        raise CanaryError("raw canary was passed through subprocess env")
    if value["output"].get("raw_transcript_saved") is not False:
        raise CanaryError("raw event transcript was saved")
    if redaction.get("provider_input_contains_marker") is not True:
        raise CanaryError("redacted marker was not present in provider input")
    if value["verdict"] == "PASS":
        if real_call.get("usage_status") != "addressable":
            raise CanaryError("PASS requires addressable usage")
        if value["auth"].get("nonce_round_trip") != "exact":
            raise CanaryError("PASS requires exact nonce round-trip")
        if value["output"].get("event_model") != DEFAULT_MODEL:
            raise CanaryError("PASS requires addressable provider model")
        if value["artifact_privacy_scan"].get("status") != "pass":
            raise CanaryError("PASS requires a passing artifact privacy scan")
    if value["verdict"] == "UNKNOWN" and value["usage_accounting"].get("dollar_cost") == 0:
        raise CanaryError("UNKNOWN cannot be represented as zero cost")


def validate_artifact_dir(root: Path) -> dict[str, Any]:
    receipt_path = root / PUBLIC_RECEIPT
    if not receipt_path.is_file() or receipt_path.is_symlink():
        raise CanaryError("public receipt is missing")
    value = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise CanaryError("public receipt is not an object")
    validate_receipt(value)
    scan = scan_public_texts(root)
    if scan["status"] != "pass":
        raise CanaryError(f"artifact privacy scan failed: {scan['violations']}")
    return {"status": "pass", "receipt": PUBLIC_RECEIPT, "files_scanned": scan["files_scanned"]}


def read_cli_version(codex_path: str) -> str:
    completed = subprocess.run(
        [codex_path, "--version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    version = (completed.stdout or completed.stderr).strip().splitlines()
    if completed.returncode != 0 or not version:
        raise CanaryError("unable to address codex CLI version")
    return version[0]


def _nonce() -> str:
    return "f4-public-" + secrets.token_hex(8)


def run_canary(
    artifact_root: Path,
    *,
    codex_path: str = "codex",
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    nonce: str | None = None,
    raw_secret: str | None = None,
) -> dict[str, Any]:
    """Run fake probes plus exactly one real synthetic provider call."""

    prepare_artifact_root(artifact_root)
    public_nonce = nonce or _nonce()
    secret = raw_secret or "f4-secret-" + secrets.token_hex(16)
    request = build_synthetic_request(public_nonce, secret)
    fake_runs = fake_probe_matrix(request)
    cli_version = read_cli_version(codex_path)
    envelope = _sanitized_envelope(timeout_seconds)
    command_digest = digest(_sanitized_argv_shape())
    config_digest = digest(
        {
            "model": DEFAULT_MODEL,
            "thinking": DEFAULT_THINKING,
            "sandbox": "read-only",
            "ephemeral": True,
            "json_events": True,
            "output_schema": "<temporary-root>/output-schema.json",
        }
    )
    real_run = run_real_canary(
        request,
        secret,
        codex_path=codex_path,
        timeout_seconds=timeout_seconds,
    )
    captured = _safe_result(real_run.structured_result, public_nonce)
    captured_saved = False
    render_identical: bool | None = None
    if captured is not None and not real_run.raw_secret_seen:
        captured_path = write_owned_json(artifact_root, CAPTURED_RESULT, captured)
        captured_saved = True
        render_one_value = render_captured_result(captured)
        render_two_value = render_captured_result(captured)
        render_one = canonical_bytes(render_one_value)
        render_two = canonical_bytes(render_two_value)
        render_identical = render_one == render_two
        write_owned_json(artifact_root, RENDER_ONE, render_one_value)
        write_owned_json(artifact_root, RENDER_TWO, render_two_value)
        _ = captured_path
    else:
        render_identical = None

    artifact_scan = scan_public_texts(artifact_root, secret)
    receipt = build_receipt(
        cli_version=cli_version,
        envelope=envelope,
        command_digest=command_digest,
        config_digest=config_digest,
        request=request,
        fake_runs=fake_runs,
        real_run=real_run,
        captured_result_saved=captured_saved,
        render_identical=render_identical,
        artifact_scan=artifact_scan,
        artifact_root=artifact_root,
        repo_root=Path.cwd().resolve(),
    )
    # The receipt path is known only to this writer; its public path is relative
    # and never exposes the worktree or the temporary runtime directory.
    write_owned_json(artifact_root, PUBLIC_RECEIPT, receipt)
    final_scan = scan_public_texts(artifact_root, secret)
    if final_scan["status"] != "pass":
        raise CanaryError(f"final artifact privacy scan failed: {final_scan['violations']}")
    receipt["artifact_privacy_scan"] = final_scan
    write_owned_json(artifact_root, PUBLIC_RECEIPT, receipt)
    final_scan = scan_public_texts(artifact_root, secret)
    if final_scan["status"] != "pass":
        raise CanaryError(f"final receipt privacy scan failed: {final_scan['violations']}")
    validate_artifact_dir(artifact_root)
    return receipt


def record_unknown_after_local_error(
    artifact_root: Path,
    *,
    codex_path: str = "codex",
    failure_category: str = "local_artifact_write_error",
) -> dict[str, Any]:
    """Persist an honest UNKNOWN after a real-call result was not recoverable.

    This recovery route never starts a provider process.  It deliberately does
    not invent the lost nonce, response, run address, token usage, or cost.
    """

    prepare_artifact_root(artifact_root)
    fake_request = build_synthetic_request(
        "f4-public-0000000000000000", "f4-secret-recovery-only"
    )
    fake_runs = fake_probe_matrix(fake_request)
    cli_version = read_cli_version(codex_path)
    envelope = _sanitized_envelope(DEFAULT_TIMEOUT_SECONDS)
    real_run = RealRun(
        status="unknown_persistence_error",
        attempts=1,
        elapsed_category="unknown",
        usage=None,
        parsed=None,
        structured_result=None,
        raw_secret_seen=False,
        auth_completed=False,
        error_category=failure_category,
    )
    artifact_scan = scan_public_texts(artifact_root, "f4-secret-recovery-only")
    receipt = build_receipt(
        cli_version=cli_version,
        envelope=envelope,
        command_digest=digest(_sanitized_argv_shape()),
        config_digest=digest(
            {
                "model": DEFAULT_MODEL,
                "thinking": DEFAULT_THINKING,
                "sandbox": "read-only",
                "ephemeral": True,
                "json_events": True,
                "output_schema": "<temporary-root>/output-schema.json",
            }
        ),
        request=None,
        fake_runs=fake_runs,
        real_run=real_run,
        captured_result_saved=False,
        render_identical=None,
        artifact_scan=artifact_scan,
        artifact_root=artifact_root,
        repo_root=Path.cwd().resolve(),
        runtime_schema_opened=True,
    )
    write_owned_json(artifact_root, PUBLIC_RECEIPT, receipt)
    final_scan = scan_public_texts(artifact_root, "f4-secret-recovery-only")
    if final_scan["status"] != "pass":
        raise CanaryError(f"unknown receipt privacy scan failed: {final_scan['violations']}")
    receipt["artifact_privacy_scan"] = final_scan
    write_owned_json(artifact_root, PUBLIC_RECEIPT, receipt)
    validate_artifact_dir(artifact_root)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--codex-path", default="codex")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--fake-only", action="store_true")
    parser.add_argument("--validate-artifact-dir", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.validate_artifact_dir:
            print(json.dumps(validate_artifact_dir(args.artifact_dir), sort_keys=True))
            return 0
        if args.fake_only:
            secret = "f4-secret-test-only"
            request = build_synthetic_request("f4-public-0123456789abcdef", secret)
            runs = fake_probe_matrix(request)
            print(
                json.dumps(
                    {"schema": SCHEMA, "fake_probes": {k: _fake_summary(v) for k, v in runs.items()}},
                    sort_keys=True,
                )
            )
            return 0
        receipt = run_canary(
            args.artifact_dir,
            codex_path=args.codex_path,
            timeout_seconds=args.timeout_seconds,
        )
        print(json.dumps({"verdict": receipt["verdict"], "schema": SCHEMA}, sort_keys=True))
        return 0 if receipt["verdict"] == "PASS" else 2
    except (CanaryError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"schema": SCHEMA, "status": "error", "error_category": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
