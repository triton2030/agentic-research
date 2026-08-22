"""Read-only Hermes session evidence and boundary inspection."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

import _ox_policy as ox

UsageKey = tuple[str, str, str, str, str]


def read_metadata(
    hermes_bin: str, session_id: str, cwd: Path
) -> tuple[dict[str, Any], str | None]:
    command = [
        hermes_bin,
        "sessions",
        "export",
        "-",
        "--format",
        "jsonl",
        "--session-id",
        session_id,
        "--redact",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {}, f"session metadata export failed: {exc}"
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit {completed.returncode}"
        return {}, f"session metadata export failed: {detail}"
    for line in completed.stdout.splitlines():
        if not line.lstrip().startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(record.get("id") or "") == session_id:
            return record, None
    return {}, "session metadata record not found"


def compact_metadata(
    record: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    model_config: dict[str, Any] = {}
    raw_model_config = record.get("model_config")
    if isinstance(raw_model_config, str) and raw_model_config:
        try:
            parsed = json.loads(raw_model_config)
            if isinstance(parsed, dict):
                model_config = parsed
        except json.JSONDecodeError:
            pass
    elif isinstance(raw_model_config, dict):
        model_config = raw_model_config
    resolved = {
        "model": record.get("model"),
        "provider": record.get("billing_provider"),
        "reasoning": model_config.get("reasoning_config"),
        "max_turns": model_config.get("max_iterations"),
    }
    session = {
        "id": record.get("id"),
        "source": record.get("source"),
        "message_count": record.get("message_count"),
        "tool_call_count": record.get("tool_call_count"),
        "end_reason": record.get("end_reason"),
    }
    usage = {
        "scope": "session_cumulative",
        "input_tokens": record.get("input_tokens"),
        "output_tokens": record.get("output_tokens"),
        "reasoning_tokens": record.get("reasoning_tokens"),
        "cache_read_tokens": record.get("cache_read_tokens"),
        "cache_write_tokens": record.get("cache_write_tokens"),
        "api_calls": record.get("api_call_count"),
        "estimated_cost_usd": record.get("estimated_cost_usd"),
        "actual_cost_usd": record.get("actual_cost_usd"),
        "cost_status": record.get("cost_status"),
    }
    return resolved, session, usage


def final_assistant_content(record: dict[str, Any]) -> str | None:
    """Return the last completed assistant message, excluding tool-call turns."""
    messages = record.get("messages")
    if not isinstance(messages, list):
        return None
    for message in reversed(messages):
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        if message.get("tool_calls"):
            continue
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return None


def resume_runtime(record: dict[str, Any]) -> tuple[str, str, str] | None:
    resolved, _, _ = compact_metadata(record)
    model = resolved.get("model")
    provider = resolved.get("provider")
    reasoning = resolved.get("reasoning")
    if not isinstance(model, str) or not model.strip():
        return None
    if not isinstance(provider, str) or not provider.strip():
        return None
    if not isinstance(reasoning, dict):
        return None
    if reasoning.get("enabled") is False:
        effort = "none"
    else:
        effort = reasoning.get("effort")
        if not isinstance(effort, str) or not effort.strip():
            return None
    return model.strip(), provider.strip(), effort.strip()


def session_usage_snapshot(
    session_id: str,
) -> tuple[dict[UsageKey, int] | None, str | None]:
    hermes_home = os.environ.get("HERMES_HOME")
    root = Path(hermes_home).expanduser() if hermes_home else Path.home() / ".hermes"
    state_db = root / "state.db"
    if not state_db.is_file():
        return None, f"Hermes usage database is missing: {state_db}"
    try:
        connection = sqlite3.connect(f"file:{state_db}?mode=ro", uri=True)
        try:
            rows = connection.execute(
                """
                SELECT model, billing_provider, billing_base_url, billing_mode,
                       task, SUM(api_call_count)
                FROM session_model_usage
                WHERE session_id = ?
                GROUP BY model, billing_provider, billing_base_url, billing_mode, task
                """,
                (session_id,),
            ).fetchall()
        finally:
            connection.close()
    except sqlite3.Error as exc:
        return None, f"Hermes usage evidence is unreadable: {exc}"
    return {
        (
            str(model),
            str(provider),
            str(base_url).rstrip("/"),
            str(mode),
            str(task),
        ): int(calls)
        for model, provider, base_url, mode, task, calls in rows
    }, None


def runtime_usage_evidence(
    before: dict[UsageKey, int],
    after: dict[UsageKey, int],
    *,
    model: str,
    provider: str,
    ox_alpha: bool,
) -> tuple[dict[str, Any], bool]:
    delta = {
        key: count - before.get(key, 0)
        for key, count in after.items()
        if count - before.get(key, 0) > 0
    }
    if ox_alpha:
        exact_route = (ox.MODEL, ox.PROVIDER, ox.BASE_URL, ox.BILLING_MODE)
        exact_calls = sum(
            count
            for key, count in delta.items()
            if key[:4] == exact_route and key[4] == ""
        )
        unexpected = {
            key: count for key, count in delta.items() if key[:4] != exact_route
        }
    else:
        main_calls = {key: count for key, count in delta.items() if key[4] == ""}
        exact_calls = sum(
            count
            for key, count in main_calls.items()
            if key[0] == model and key[1] == provider
        )
        unexpected = {
            key: count
            for key, count in main_calls.items()
            if key[0] != model or key[1] != provider
        }
    mismatch = exact_calls < 1 or bool(unexpected)
    evidence = {
        "verified": not mismatch,
        "model": model,
        "provider": provider,
        "billing_base_url": ox.BASE_URL if ox_alpha else None,
        "billing_mode": ox.BILLING_MODE if ox_alpha else None,
        "new_main_api_calls": exact_calls,
        "unexpected_main_calls": [
            {
                "model": key[0],
                "provider": key[1],
                "billing_base_url": key[2],
                "billing_mode": key[3],
                "api_calls": count,
            }
            for key, count in sorted(unexpected.items())
        ],
    }
    return evidence, mismatch

