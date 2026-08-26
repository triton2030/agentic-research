"""Pure request construction and acceptance rules for the 1hermes advisor."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import _ox_policy as ox

NON_EXECUTION_TOOLSETS = frozenset(
    {
        "browser",
        "clarify",
        "context_engine",
        "file",
        "memory",
        "search",
        "session_search",
        "skills",
        "todo",
        "web",
        "x_search",
    }
)


def validate(args: argparse.Namespace) -> tuple[Path | None, list[str], str | None]:
    if args.max_turns < 1 or args.timeout_sec < 1:
        return None, [], "--max-turns and --timeout-sec must be positive"
    toolsets = [
        item.strip().lower() for item in args.toolsets.split(",") if item.strip()
    ]
    if not toolsets:
        return None, [], "--toolsets must name at least one toolset"
    extended = sorted(set(toolsets) - NON_EXECUTION_TOOLSETS)
    if extended and not args.allow_execution_tools:
        return (
            None,
            [],
            "Execution-capable or unknown toolsets require --allow-execution-tools: "
            + ", ".join(extended),
        )
    if args.allow_execution_tools and not args.allow_write:
        return None, [], "--allow-execution-tools requires --allow-write"
    if args.worktree and not args.allow_write:
        return None, [], "--worktree requires --allow-write"
    if args.worktree and args.resume:
        return None, [], "--worktree cannot be combined with --resume"
    if args.resume and (args.model or args.provider or args.reasoning):
        return None, [], "Do not switch model/provider/reasoning on --resume"
    if getattr(args, "isolated", False) and args.skill:
        return None, [], "--skill cannot be combined with --isolated"
    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        return None, [], f"--cwd is not a directory: {cwd}"
    return cwd, toolsets, None


def requested_runtime(
    args: argparse.Namespace,
    resumed: tuple[str, str, str] | None,
    *,
    default_model: str,
    default_provider: str,
    default_reasoning: str,
) -> tuple[str, str | None, str]:
    if resumed:
        return resumed
    model = args.model or default_model
    provider = args.provider or (default_provider if args.model is None else None)
    return model, provider, args.reasoning or default_reasoning


def ox_gate(
    args: argparse.Namespace, runtime: tuple[str, str | None, str]
) -> str | None:
    model, provider, reasoning = runtime
    if model != ox.MODEL:
        return None
    error = ox.admission_error(provider, reasoning, allow_fallback=args.allow_fallback)
    if error:
        return error
    # Права Ox равны правам любой другой роли: terminal, code_execution и запись
    # проходят общий контроль в validate(). Здесь остаётся только то, что
    # относится к деньгам, — пин маршрута выше и живой каталог цен ниже.
    free, reason = ox.live_pricing_is_free()
    return None if free else f"Ox Alpha disabled: {reason}"


def boundary_prompt(args: argparse.Namespace, prompt: str) -> str:
    if not args.worktree:
        return prompt
    return prompt + "\n\nHost constraint: Edit the worktree; the host creates the commit."


def command(
    args: argparse.Namespace,
    hermes_bin: str,
    query_file: Path,
    toolsets: list[str],
    runtime: tuple[str, str | None, str],
) -> list[str]:
    model, provider, reasoning = runtime
    result = [hermes_bin, "chat", "--query-file", str(query_file)]
    if args.resume:
        result.extend(["--resume", args.resume])
    result.extend(["--model", model, "--reasoning", reasoning])
    if provider:
        result.extend(["--provider", provider])
    result.extend(
        [
            "--toolsets",
            ",".join(toolsets),
            "--max-turns",
            str(args.max_turns),
            "--source",
            "tool",
            "-Q",
        ]
    )
    if model == ox.MODEL:
        result.append("--ignore-user-config")
    if getattr(args, "isolated", False):
        result.append("--ignore-rules")
    for skill in args.skill:
        if skill.strip():
            result.extend(["--skills", skill.strip()])
    if args.allow_write:
        result.append("--checkpoints")
    return result


def runtime_verdict(
    requested: tuple[str, str | None, str],
    resolved: dict[str, Any],
    allow_fallback: bool,
) -> tuple[list[str], bool, list[str]]:
    model, provider, reasoning = requested
    warnings: list[str] = []
    mismatch = False
    for label, expected, actual in (
        ("model", model, resolved.get("model")),
        ("provider", provider, resolved.get("provider")),
    ):
        if expected and actual and actual != expected:
            mismatch = mismatch or not allow_fallback
            warnings.append(
                f"runtime mismatch: requested {label} {expected}, got {actual}"
            )
        elif label == "provider" and expected is None and actual:
            # Свежий прогон с --model без --provider: ожидание не зафиксировано,
            # сравнивать не с чем, но биллинг зависит от провайдера — молчать
            # нельзя, поэтому предупреждение без вердикта mismatch.
            warnings.append(
                f"requested provider is unpinned; session resolved {actual}"
            )
    resolved_reasoning = resolved.get("reasoning")
    if not isinstance(resolved_reasoning, dict):
        mismatch = True
        warnings.append("runtime mismatch: reasoning metadata is malformed")
    else:
        actual = (
            "none"
            if resolved_reasoning.get("enabled") is False
            else resolved_reasoning.get("effort")
        )
        if actual != reasoning:
            mismatch = mismatch or not allow_fallback
            warnings.append(
                f"runtime mismatch: requested reasoning {reasoning}, got {actual}"
            )
    missing = [
        label
        for label, value in (
            ("model", resolved.get("model")),
            ("provider", resolved.get("provider")),
            ("reasoning", resolved_reasoning),
        )
        if value is None
    ]
    if missing:
        warnings.append("session metadata lacks resolved " + ", ".join(missing))
    return warnings, mismatch, missing
