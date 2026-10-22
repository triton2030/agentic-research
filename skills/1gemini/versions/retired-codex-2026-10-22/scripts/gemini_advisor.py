#!/usr/bin/env python3
"""Run one verified Gemini turn through the official Antigravity CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "gemini-3.1-pro-high"
DEFAULT_EFFORT = "high"
DEFAULT_TIMEOUT_SEC = 1800
TEST_HARNESS_ENV = "ONE_GEMINI_TEST_HARNESS"
VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".webm", ".avi", ".ogv"})
AUDIO_SUFFIXES = frozenset(
    {
        ".mp3",
        ".wav",
        ".aif",
        ".aiff",
        ".m4a",
        ".aac",
        ".flac",
        ".ogg",
        ".opus",
    }
)
GEMINI_MODEL_RE = re.compile(r"^gemini-[A-Za-z0-9._-]+$")
FAILURE_STATES = frozenset({"ERROR", "FAILED", "DENIED", "CANCELLED"})
API_ENV_VARS = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GEMINI_BASE_URL",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
)
PASSTHROUGH_ENV_VARS = frozenset(
    {
        "HOME",
        "PATH",
        "USER",
        "LOGNAME",
        "SHELL",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "TMPDIR",
        "TERM",
        "COLORTERM",
        "XDG_CONFIG_HOME",
    }
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read a brief from stdin, run official agy, and emit verified "
            "Gemini response evidence as JSON."
        )
    )
    parser.add_argument(
        "--cwd",
        default=os.getcwd(),
        help="Logical source project; it is not attached as the agy workspace",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Exact Gemini model")
    parser.add_argument("--resume", help="Resume a text conversation")
    parser.add_argument("--media", help="One audio or video file to analyze")
    return parser


def _emit(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _fail(message: str, *, exit_code: int = 2) -> int:
    _emit({"ok": False, "exit_code": exit_code, "error": message})
    return exit_code


def _resolve_executable(name: str) -> str | None:
    override = None
    if os.environ.get(TEST_HARNESS_ENV) == "1":
        override = os.environ.get(f"ONE_GEMINI_{name.upper()}_BIN")
    candidate = override or shutil.which(name)
    if not candidate:
        return None
    path = Path(candidate).expanduser().resolve()
    return str(path) if path.is_file() and os.access(path, os.X_OK) else None


def _runtime_timeout_sec() -> int:
    if os.environ.get(TEST_HARNESS_ENV) != "1":
        return DEFAULT_TIMEOUT_SEC
    raw = os.environ.get("ONE_GEMINI_TIMEOUT_SEC", str(DEFAULT_TIMEOUT_SEC))
    try:
        timeout = int(raw)
    except ValueError:
        return DEFAULT_TIMEOUT_SEC
    return timeout if timeout > 0 else DEFAULT_TIMEOUT_SEC


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stage_audio_carrier(
    *, source: Path, staged: Path, ffmpeg_bin: str, timeout_sec: int
) -> str | None:
    command = [
        ffmpeg_bin,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=320x240:r=1",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-shortest",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-tune",
        "stillimage",
        "-crf",
        "35",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(staged),
    ]
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            check=False,
            env=_sanitized_environment(),
        )
    except subprocess.TimeoutExpired:
        return f"ffmpeg exceeded the {timeout_sec}-second timeout"
    except OSError as exc:
        return f"cannot execute ffmpeg: {exc}"
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit {completed.returncode}"
        return f"ffmpeg audio carrier failed: {detail}"
    if not staged.is_file() or staged.stat().st_size == 0:
        return "ffmpeg audio carrier did not produce a file"
    return None


def _account_route_error() -> str | None:
    settings = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
    if not settings.exists():
        return None
    try:
        payload = json.loads(settings.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"cannot verify Antigravity account settings: {exc}"
    provider = payload.get("modelProvider") if isinstance(payload, dict) else None
    if provider not in (None, ""):
        return (
            f"Antigravity modelProvider={provider!r}; expected the account-backed "
            "default with modelProvider null"
        )
    return None


def _sanitized_environment() -> dict[str, str]:
    environment = {
        name: value
        for name, value in os.environ.items()
        if name in PASSTHROUGH_ENV_VARS and name not in API_ENV_VARS
    }
    if os.environ.get(TEST_HARNESS_ENV) == "1":
        environment.update(
            {
                name: value
                for name, value in os.environ.items()
                if name.startswith(("ONE_GEMINI_", "FAKE_"))
            }
        )
    environment["NO_COLOR"] = "1"
    return environment


def _cli_version(agy_bin: str) -> tuple[str | None, str | None]:
    try:
        completed = subprocess.run(
            [agy_bin, "--version"],
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
            env=_sanitized_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"cannot execute agy --version: {exc}"
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit {completed.returncode}"
        return None, f"agy --version failed: {detail}"
    return completed.stdout.strip(), None


def _parse_stream(
    stdout: str,
    *,
    requested_model: str,
    expected_cwd: Path,
    expected_conversation_id: str | None,
    media_path: Path | None,
) -> tuple[dict[str, Any] | None, str | None]:
    events: list[dict[str, Any]] = []
    for number, line in enumerate(stdout.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            return None, f"agy emitted invalid stream JSON on line {number}: {exc}"
        if not isinstance(event, dict):
            return None, f"agy emitted a non-object event on line {number}"
        events.append(event)

    init_events = [item for item in events if item.get("event") == "init"]
    result_events = [item for item in events if item.get("event") == "result"]
    if len(init_events) != 1:
        return None, f"expected one init event, received {len(init_events)}"
    if len(result_events) != 1:
        return None, f"expected one terminal result event, received {len(result_events)}"

    init_event = init_events[0]
    init = init_event.get("init")
    result = result_events[0].get("result")
    if not isinstance(init, dict) or not isinstance(result, dict):
        return None, "agy init or result payload is missing"

    resolved_model = str(init.get("model") or "")
    if resolved_model != requested_model:
        return None, (
            f"model mismatch: requested {requested_model!r}, resolved "
            f"{resolved_model!r}"
        )

    raw_cwd = str(init.get("cwd") or "")
    try:
        resolved_cwd = Path(raw_cwd).expanduser().resolve()
    except OSError as exc:
        return None, f"cannot resolve agy cwd {raw_cwd!r}: {exc}"
    if resolved_cwd != expected_cwd.resolve():
        return None, f"cwd mismatch: expected {expected_cwd}, resolved {resolved_cwd}"

    status = str(result.get("status") or "")
    if status != "SUCCESS":
        return None, f"agy terminal status is {status or 'missing'}, not SUCCESS"
    response = str(result.get("response") or "").strip()
    if not response:
        return None, "agy returned SUCCESS with an empty response"

    init_conversation = str(init_event.get("conversation_id") or "")
    result_conversation = str(result.get("conversation_id") or "")
    if not result_conversation or result_conversation != init_conversation:
        return None, "agy conversation_id is missing or inconsistent"
    if (
        expected_conversation_id is not None
        and result_conversation != expected_conversation_id
    ):
        return None, (
            f"resume mismatch: requested {expected_conversation_id!r}, returned "
            f"{result_conversation!r}"
        )

    observed_tools: list[dict[str, str]] = []
    media_viewed = media_path is None
    tool_failures: list[str] = []
    unexpected_tools: list[str] = []
    allowed_tools = {"view_file"} if media_path is not None else set()
    for event in events:
        update = event.get("step_update")
        if not isinstance(update, dict) or update.get("step_type") != "tool":
            continue
        tool_name = str(update.get("tool_name") or "")
        state = str(update.get("state") or "")
        if tool_name and {"name": tool_name, "state": state} not in observed_tools:
            observed_tools.append({"name": tool_name, "state": state})
        if tool_name not in allowed_tools:
            unexpected_tools.append(tool_name or "<missing>")
        if state.upper() in FAILURE_STATES:
            tool_failures.append(f"{tool_name or 'unknown'}:{state}")
        tool_info = update.get("tool_info")
        if isinstance(tool_info, dict):
            serialized = json.dumps(tool_info, ensure_ascii=False).lower()
            if "permission denied" in serialized or '"error"' in serialized:
                tool_failures.append(f"{tool_name or 'unknown'}:reported-error")
        if media_path is not None and tool_name == "view_file" and state == "DONE":
            parameters = tool_info.get("parameters") if isinstance(tool_info, dict) else None
            viewed = (
                parameters.get("AbsolutePath") or parameters.get("absolute_path")
                if isinstance(parameters, dict)
                else None
            )
            if not viewed or Path(str(viewed)).expanduser().resolve() != media_path.resolve():
                return None, "agy completed view_file outside the staged media path or without a path"
            media_viewed = True

    if unexpected_tools:
        return None, (
            "agy invoked tools outside the advisor contract: "
            f"{sorted(set(unexpected_tools))}"
        )
    if tool_failures:
        return None, f"agy reported tool failures: {sorted(set(tool_failures))}"
    if not media_viewed:
        return None, "agy returned SUCCESS without viewing the staged media file"

    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    return {
        "response": response,
        "resolved": {
            "model": resolved_model,
            "cwd": str(resolved_cwd),
            "permission_mode": init.get("permission_mode"),
        },
        "session": {
            "conversation_id": result_conversation,
            "status": status,
            "duration_seconds": result.get("duration_seconds"),
            "duration_source": "agy-result",
            "num_turns": result.get("num_turns"),
        },
        "usage": usage,
        "usage_scope": (
            "agy-result; turn-vs-conversation scope is not documented for resume"
            if expected_conversation_id is not None
            else "agy-result"
        ),
        "observed_tools": observed_tools,
        "media_viewed": media_viewed,
    }, None


def _stream_failure_detail(stdout: str) -> str | None:
    for line in reversed(stdout.splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("event") != "result":
            continue
        result = event.get("result")
        if not isinstance(result, dict):
            continue
        error = str(result.get("error") or "").strip()
        if error:
            return error
        status = str(result.get("status") or "").strip()
        if status and status != "SUCCESS":
            return f"terminal status {status}"
    return None


def _run_agy(
    *,
    agy_bin: str,
    prompt: str,
    run_cwd: Path,
    model: str,
    effort: str,
    resume: str | None,
    media_path: Path | None,
    timeout_sec: int,
) -> tuple[dict[str, Any] | None, str | None, str]:
    command = [agy_bin, "--model", model, "--effort", effort]
    command.extend(["--log-file", str(run_cwd / "agy.log")])
    if resume:
        command.extend(["--conversation", resume])
    command.append("--disable-slash-commands")
    if media_path is not None:
        command.append("--new-project")
    command.extend(
        [
            "--sandbox",
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--print-timeout",
            f"{max(1, math.ceil(timeout_sec / 60))}m",
        ]
    )
    stream_input = json.dumps(
        {"event": "user", "message": {"content": prompt}}, ensure_ascii=False
    ) + "\n"
    started = time.monotonic()
    try:
        environment = _sanitized_environment()
        environment["PWD"] = str(run_cwd)
        completed = subprocess.run(
            command,
            cwd=run_cwd,
            input=stream_input,
            text=True,
            capture_output=True,
            timeout=timeout_sec + 2,
            check=False,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return None, f"agy exceeded the {timeout_sec}-second timeout", ""
    except OSError as exc:
        return None, f"cannot execute agy: {exc}", ""

    stderr = completed.stderr.strip()
    wrapper_elapsed_seconds = round(time.monotonic() - started, 3)
    if completed.returncode != 0:
        detail = _stream_failure_detail(completed.stdout) or stderr
        detail = detail or f"exit {completed.returncode}"
        if stderr and stderr != detail:
            detail = f"{detail} (stderr: {stderr})"
        return None, f"agy failed: {detail}", stderr
    parsed, error = _parse_stream(
        completed.stdout,
        requested_model=model,
        expected_cwd=run_cwd,
        expected_conversation_id=resume,
        media_path=media_path,
    )
    if parsed is not None:
        parsed["session"]["wrapper_elapsed_seconds"] = wrapper_elapsed_seconds
    return parsed, error, stderr


def main() -> int:
    args = _parser().parse_args()
    brief = sys.stdin.read().strip()
    if not brief:
        return _fail("brief on stdin is empty")
    if not GEMINI_MODEL_RE.fullmatch(args.model):
        return _fail(f"refusing non-Gemini model {args.model!r}")
    if args.resume and args.media:
        return _fail("media calls are one-shot and cannot use --resume")

    project_cwd = Path(args.cwd).expanduser().resolve()
    if not project_cwd.is_dir():
        return _fail(f"project directory does not exist: {project_cwd}")
    route_error = _account_route_error()
    if route_error:
        return _fail(route_error)
    agy_bin = _resolve_executable("agy")
    if not agy_bin:
        return _fail("official agy executable not found")
    version, version_error = _cli_version(agy_bin)
    if version_error:
        return _fail(version_error)

    timeout_sec = _runtime_timeout_sec()

    if not args.media:
        with tempfile.TemporaryDirectory(prefix="1gemini-text-") as temporary:
            run_cwd = Path(temporary).resolve()
            prompt = (
                f"{brief}\n\nReturn the requested answer now. The source project "
                "is not your workspace; use only this brief and do not attempt to "
                "open other filesystem paths. "
                "Do not create an implementation plan unless the request explicitly "
                "asks for one."
            )
            parsed, error, stderr = _run_agy(
                agy_bin=agy_bin,
                prompt=prompt,
                run_cwd=run_cwd,
                model=args.model,
                effort=DEFAULT_EFFORT,
                resume=args.resume,
                media_path=None,
                timeout_sec=timeout_sec,
            )
            if error or parsed is None:
                return _fail(error or "agy result is missing")
            parsed.pop("media_viewed", None)
            parsed["ok"] = True
            parsed["requested"] = {
                "model": args.model,
                "context_root": str(project_cwd),
                "resume": args.resume,
                "media": None,
            }
            parsed["resolved"].update(
                {
                    "cli_path": agy_bin,
                    "cli_version": version,
                    "mode": "isolated-text",
                }
            )
            parsed["isolation"] = {
                "source_project_workspace_attached": False,
                "source_project_access_guaranteed_blocked": False,
                "path_bearing_environment_removed": True,
                "temporary_execution_deleted_after_call": True,
                "conversation_artifacts_may_persist": True,
            }
            parsed["warnings"] = [stderr] if stderr else []
            _emit(parsed)
            return 0

    source = Path(args.media).expanduser().resolve()
    if not source.is_file():
        return _fail(f"media file does not exist: {source}")
    suffix = source.suffix.lower()
    if suffix not in VIDEO_SUFFIXES | AUDIO_SUFFIXES:
        supported = ", ".join(sorted(VIDEO_SUFFIXES | AUDIO_SUFFIXES))
        return _fail(f"unsupported media suffix {suffix!r}; supported: {supported}")

    media_kind = "video" if suffix in VIDEO_SUFFIXES else "audio"
    ffmpeg_bin = None
    if media_kind == "audio":
        ffmpeg_bin = _resolve_executable("ffmpeg")
        if not ffmpeg_bin:
            return _fail("ffmpeg executable not found for reliable audio delivery")
    try:
        source_hash_before = _sha256(source)
    except OSError as exc:
        return _fail(f"cannot hash source media: {exc}")
    with tempfile.TemporaryDirectory(prefix="1gemini-media-") as temporary:
        run_cwd = Path(temporary).resolve()
        staged = run_cwd / ("media.mp4" if media_kind == "audio" else f"media{suffix}")
        if media_kind == "audio":
            carrier_error = _stage_audio_carrier(
                source=source,
                staged=staged,
                ffmpeg_bin=ffmpeg_bin or "",
                timeout_sec=timeout_sec,
            )
            if carrier_error:
                return _fail(carrier_error)
        else:
            try:
                shutil.copy2(source, staged)
            except OSError as exc:
                return _fail(f"cannot stage media: {exc}")

        prompt = (
            f"{brief}\n\nThe exact staged media path is: {staged}\n"
            "You must call view_file on that exact path before answering. "
            "If view_file fails, say so and do not infer unseen content. "
            + (
                "Analyze the audio. "
                if media_kind == "audio"
                else "Analyze the video and its audio track when present. "
            )
            + "Return the requested answer now; do not create a plan or files."
        )
        parsed, error, stderr = _run_agy(
            agy_bin=agy_bin,
            prompt=prompt,
            run_cwd=run_cwd,
            model=args.model,
            effort=DEFAULT_EFFORT,
            resume=None,
            media_path=staged,
            timeout_sec=timeout_sec,
        )
        if error or parsed is None:
            return _fail(error or "agy result is missing")
        try:
            source_hash_after = _sha256(source)
        except OSError as exc:
            return _fail(f"cannot verify source media after call: {exc}")
        if source_hash_after != source_hash_before:
            return _fail("source media changed during the Gemini call")
        parsed["ok"] = True
        parsed["requested"] = {
            "model": args.model,
            "context_root": str(project_cwd),
            "resume": None,
            "media": str(source),
        }
        parsed["resolved"].update(
            {"cli_path": agy_bin, "cli_version": version, "mode": "isolated-media"}
        )
        parsed["media"] = {
            "source_path": str(source),
            "source_kind": media_kind,
            "staged_suffix": staged.suffix,
            "delivery": (
                "audio-mp4-carrier" if media_kind == "audio" else "unchanged-video-copy"
            ),
            "audio_transcoded_for_delivery": media_kind == "audio",
            "viewed": parsed.pop("media_viewed"),
            "source_sha256_unchanged": True,
            "staged_file_deleted_after_call": True,
            "conversation_artifacts_may_persist": True,
        }
        parsed["warnings"] = [stderr] if stderr else []
        _emit(parsed)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
