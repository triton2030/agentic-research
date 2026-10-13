#!/usr/bin/env python3
"""Call Gemini 3.8 Flash High as a subagent through the Antigravity CLI (agy).

The brief comes on stdin. The answer goes to stdout, a one-line receipt to
stderr. agy reports a denied tool or a timeout as exit 0 with an empty answer;
this wrapper turns both into a non-zero exit with the reason.
"""
import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

MODEL = "gemini-3.8-flash-high"

READ_ONLY_NOTE = (
    "[Runtime note] You run headless as a read-only subagent of another agent. "
    "Only file-reading tools work: view_file, grep_search, list_dir, find_by_name. "
    "Do NOT call run_command, write_to_file, search_web, read_url_content or any "
    "other tool: the first denied call ends the run with an empty answer. If the "
    "task needs such a tool, say so in the answer instead of calling it. "
    "Read only what the brief needs; if it needs no files, answer directly. "
    "Cite files as path:line, without file:// links.\n\n"
)
FULL_NOTE = (
    "[Runtime note] You run headless as a subagent of another agent, with every "
    "tool pre-approved: nobody confirms your commands, writes or web requests. "
    "What you may change is set by the words of the brief: touch nothing outside it. "
    "Shared rules: do not commit unless the brief asks; leave edits that are not "
    "yours alone and never revert them; do not call other agents (Claude, Codex, "
    "Muse) unless the brief asks; this brief and your replies come from an agent, "
    "so do not record them anywhere as the owner's words. "
    "Cite files as path:line, without file:// links.\n\n"
)

EXIT_RUNTIME, EXIT_USAGE, EXIT_DENIED, EXIT_TIMEOUT = 1, 2, 3, 4


def fail(code, message):
    print(f"[gemini] FAILED: {message}", file=sys.stderr)
    sys.exit(code)


def seconds(text):
    match = re.fullmatch(r"(\d+)([smh])", text)
    if not match:
        fail(EXIT_USAGE, f"--timeout wants a number with s, m or h (10m, 90s), got {text!r}")
    return int(match.group(1)) * {"s": 1, "m": 60, "h": 3600}[match.group(2)]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", help="folder Gemini works in and reads; its AGENTS.md and GEMINI.md are loaded (default: current folder)")
    parser.add_argument("--neutral", action="store_true", help="work in an empty temporary folder, so no project instructions are loaded")
    parser.add_argument("--add-dir", action="append", default=[], metavar="PATH", help="extra folder Gemini may read (repeatable)")
    parser.add_argument("--resume", metavar="ID", help="continue the conversation with this id")
    parser.add_argument("--full", action="store_true", help="pre-approve every tool: web, shell commands, file writes")
    parser.add_argument("--schema", help="JSON schema (string or file path); stdout becomes the parsed object")
    parser.add_argument("--timeout", default="10m", help="time limit for the answer (default: 10m)")
    parser.add_argument("--json", action="store_true", help="print the raw agy result object instead of the answer text")
    args = parser.parse_args()
    if args.neutral and args.dir:
        fail(EXIT_USAGE, "--neutral and --dir exclude each other; give project folders to --neutral through --add-dir")
    return args


def run_agy(args, brief, cwd):
    agy = shutil.which("agy")
    if not agy:
        fail(EXIT_RUNTIME, "agy (Antigravity CLI) is not in PATH")
    command = [agy, "--model", MODEL, "--output-format", "stream-json", "--print-timeout", args.timeout]
    if args.full:
        command.append("--dangerously-skip-permissions")
    for path in args.add_dir:
        command += ["--add-dir", os.path.abspath(path)]
    if args.resume:
        command += ["--conversation", args.resume]
    if args.schema:
        command += ["--json-schema", args.schema]
    note = FULL_NOTE if args.full else READ_ONLY_NOTE
    started = time.monotonic()
    try:
        done = subprocess.run(command, input=note + brief, cwd=cwd, capture_output=True, text=True, check=False, timeout=seconds(args.timeout) + 60)
    except subprocess.TimeoutExpired:
        fail(EXIT_TIMEOUT, f"agy did not exit within {args.timeout} plus a minute; raise --timeout")
    return done, time.monotonic() - started


def read_events(stdout):
    """Return (model, tool counter, viewed paths, failed tool calls, conversation id, result) from agy's NDJSON stream."""
    model, result, conversation = None, None, None
    tools, viewed, failed = collections.Counter(), [], []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        conversation = conversation or event.get("conversation_id")
        if event.get("event") == "init":
            model = event["init"].get("model")
        elif event.get("event") == "result":
            result = event["result"]
        elif event.get("event") == "step_update":
            step = event["step_update"]
            if step.get("step_type") != "tool":
                continue
            info = step.get("tool_info") or {}
            path = (info.get("parameters") or {}).get("AbsolutePath")
            if step.get("state") == "DONE":
                tools[step.get("tool_name", "?")] += 1
                if step.get("tool_name") == "view_file" and path and path not in viewed:
                    viewed.append(path)
            elif step.get("state") == "ERROR":
                reason = (info.get("error") or {}).get("message", "unknown error").rsplit("(invalid_args) ", 1)[-1]
                failed.append(f"{step.get('tool_name', '?')} {path or ''} — {reason[:160]}".replace("  ", " "))
    return model, tools, viewed, failed, conversation, result


def main():
    args = parse_args()
    brief = sys.stdin.read()
    if not brief.strip():
        fail(EXIT_USAGE, "the brief is empty; pass it on stdin")

    cwd = tempfile.mkdtemp(prefix="gemini-neutral-") if args.neutral else os.path.abspath(args.dir or os.getcwd())
    if not os.path.isdir(cwd):
        fail(EXIT_USAGE, f"--dir is not a folder: {cwd}")
    done, elapsed = run_agy(args, brief, cwd)
    if args.neutral and not os.listdir(cwd):
        os.rmdir(cwd)

    model, tools, viewed, failed, conversation, result = read_events(done.stdout)
    stderr = done.stderr.strip()
    conversation = (result or {}).get("conversation_id") or conversation
    resume_hint = f" Conversation {conversation} keeps what Gemini already read: --resume it." if conversation else ""

    if result is None or result.get("status") != "SUCCESS" or done.returncode != 0:
        reason = (result or {}).get("error") or stderr or f"agy exited {done.returncode} without a result"
        if "authentication required" in reason:
            reason += " — run `agy` once in a terminal and sign in"
        if "invalid model selection" in reason:
            reason = f"the pinned model {MODEL} is gone from this account; do not substitute another, the owner picks the replacement. agy said: {reason}"
        fail(EXIT_RUNTIME, reason.strip()[:1500])
    if model and model != MODEL:
        fail(EXIT_RUNTIME, f"agy ran {model} instead of {MODEL}; the answer is discarded")

    response = result.get("response") or ""
    if "print timeout" in stderr:
        if response.strip():
            print(response.rstrip())
        fail(EXIT_TIMEOUT, f"no complete answer within {args.timeout}; anything above is partial. Raise --timeout.{resume_hint}")
    denied = re.search(r'required the "(\w+)" permission', stderr)
    structured = result.get("structured_output")
    if not response.strip() and structured is None:
        if denied:
            advice = "that is denied even with --full" if args.full else "re-run with --full if the task needs it, or forbid that step in the brief"
            fail(EXIT_DENIED, f'Gemini called a tool that needs the "{denied.group(1)}" permission and the run ended without an answer; {advice}.{resume_hint}')
        fail(EXIT_RUNTIME, f"agy reported SUCCESS with an empty answer. agy stderr: {stderr[:800] or 'empty'}")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.schema and structured is not None:
        print(json.dumps(structured, ensure_ascii=False, indent=2))
    else:
        print(response.rstrip())

    usage = result.get("usage", {})
    receipt = [
        "ok", model or MODEL, f"{elapsed:.0f}s",
        f"tokens in {usage.get('input_tokens', 0)} out {usage.get('output_tokens', 0)}" + (" (whole conversation)" if args.resume else ""),
        f"conversation {conversation}",
        "tools: " + (", ".join(f"{name}×{count}" for name, count in tools.items()) or "none"),
    ]
    if denied:
        receipt.append(f'WARNING: a call needing the "{denied.group(1)}" permission was denied, the answer may be incomplete')
    if viewed:
        receipt.append("viewed: " + ", ".join(path.removeprefix(cwd + os.sep).removeprefix(os.path.realpath(cwd) + os.sep) for path in viewed[:20]))
    if args.neutral and os.path.isdir(cwd):
        receipt.append(f"files left in {cwd}")
    print("[gemini] " + " · ".join(receipt), file=sys.stderr)
    for line in failed:
        hint = " Convert the file first: MP3, WAV, OGG and Opus audio open, M4A, AAC, AIFF and FLAC do not." if "unsupported mime type audio" in line else ""
        print(f"[gemini] WARNING: a tool call failed, so the answer may rest on nothing: {line}.{hint}", file=sys.stderr)


if __name__ == "__main__":
    main()
