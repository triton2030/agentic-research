#!/usr/bin/env python3
"""Call Muse Wonder as a subagent through Muse Code (muse exec).

The brief comes on stdin. The answer goes to stdout, a one-line receipt to
stderr. Bare `muse exec` accepts an unknown model id without an error, imports
the owner's Claude Code and Codex rules and skills, and waits forever on an
action that needs approval; this wrapper closes all three.
"""
import argparse
import collections
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

MODEL = "muse-wonder-1.0"
EFFORT = "high"
CATALOG = "~/.local/share/muse/model-catalog/*.json"

COMMON_NOTE = (
    "Do not launch workflows or subagents and do not call other agents unless the "
    "brief asks for it. Cite files as path:line.\n\n"
)
READ_ONLY_NOTE = (
    "[Runtime note] You run headless as a read-only subagent of another agent. "
    "You can read files, search and use the web. File writes and the shell are "
    "disabled for this run: if the task needs them, say so in the answer. "
) + COMMON_NOTE
WRITE_NOTE = (
    "[Runtime note] You run headless as a subagent of another agent. You may edit "
    "files in the working folder and run shell commands in the sandbox; nobody "
    "confirms them. Do only what the brief asks and touch nothing outside it. "
) + COMMON_NOTE

EXIT_RUNTIME, EXIT_USAGE, EXIT_TIMEOUT = 1, 2, 4


def fail(code, message):
    print(f"[muse] FAILED: {message}", file=sys.stderr)
    sys.exit(code)


def seconds(text):
    match = re.fullmatch(r"(\d+)([smh])", text)
    if not match:
        fail(EXIT_USAGE, f"--timeout wants a number with s, m or h (9m, 90s), got {text!r}")
    return int(match.group(1)) * {"s": 1, "m": 60, "h": 3600}[match.group(2)]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", help="working folder; in --write mode Muse edits files only here (default: current folder)")
    parser.add_argument("--write", action="store_true", help="let Muse edit files in the working folder and run sandboxed shell commands")
    parser.add_argument("--project-rules", action="store_true", help="trust the working folder for this run: load its AGENTS.md, skills and hooks")
    parser.add_argument("--resume", metavar="ID", help="continue the session with this id; needs the same --dir")
    parser.add_argument("--image", action="append", default=[], metavar="PATH", help="attach an image to the brief (repeatable)")
    parser.add_argument("--schema", help="JSON schema (string or file path); stdout becomes the parsed object")
    parser.add_argument("--timeout", default="9m", help="wall-clock limit; muse exec has none of its own (default: 9m)")
    return parser.parse_args()


def check_catalog():
    """Muse serves an unknown model id without an error, so the pin is checked against the local catalog."""
    known = set()
    for path in glob.glob(os.path.expanduser(CATALOG)):
        try:
            with open(path, encoding="utf-8") as handle:
                known.update(row.get("model_id") for row in json.load(handle).get("rows", []))
        except (OSError, ValueError):
            continue
    if known and MODEL not in known:
        fail(EXIT_RUNTIME, f"the pinned model {MODEL} is not in the Muse catalog; do not substitute another, the owner picks the replacement")


def run_muse(args, brief, cwd, scratch):
    muse = shutil.which("muse")
    if not muse:
        fail(EXIT_RUNTIME, "muse (Muse Code) is not in PATH")
    prompt_file = os.path.join(scratch, "brief.txt")
    with open(prompt_file, "w", encoding="utf-8") as handle:
        handle.write((WRITE_NOTE if args.write else READ_ONLY_NOTE) + brief)
    command = [muse, "exec", "--json", "--model", MODEL, "--reasoning-effort", EFFORT,
               "--no-foreign-personal-context", "--prompt-file", prompt_file]
    command += ["--disable-approval"] if args.write else ["--disable-write", "--disable-shell"]
    if args.project_rules:
        command.append("--trust-workspace")
    if args.resume:
        command += ["--session-id", args.resume]
    for path in args.image:
        command += ["--image", os.path.abspath(path)]
    if args.schema:
        schema_file = args.schema
        if not os.path.isfile(schema_file):
            schema_file = os.path.join(scratch, "schema.json")
            with open(schema_file, "w", encoding="utf-8") as handle:
                handle.write(args.schema)
        command += ["--output-schema", os.path.abspath(schema_file)]
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=True)

    def stop_with_muse(signum, _frame):  # Muse runs in its own session, so it would outlive a killed wrapper
        os.killpg(process.pid, signal.SIGTERM)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, stop_with_muse)
    signal.signal(signal.SIGINT, stop_with_muse)
    try:
        stdout, stderr = process.communicate(timeout=seconds(args.timeout))
        timed_out = False
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        stdout, stderr = process.communicate()
        timed_out = True
    return process.returncode, stdout, stderr, timed_out, time.monotonic() - started


def read_events(stdout):
    """Pick the model, session id, tool results, pending tool call and last terminal event out of Muse's JSONL."""
    seen = {"model": None, "session": None, "terminal": None, "pending": {},
            "tools": collections.Counter(), "read": [], "failed": []}
    for line in stdout.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        kind, payload = record.get("payload_type", ""), record.get("payload") or {}
        if (record.get("stream") or {}).get("kind") == "session":
            seen["session"] = seen["session"] or record["stream"].get("id")
        if kind == "run.model.configured":
            seen["model"] = payload.get("model_id")
        elif kind.startswith("run.terminal"):
            seen["terminal"] = payload
        elif kind.startswith("task.lifecycle"):
            event = payload.get("event") or {}
            if event.get("kind") == "proposed" and str(event.get("task_kind", "")).startswith("tool."):
                seen["pending"][event.get("task_id")] = event["task_kind"]
            elif event.get("kind") in ("accepted", "completed"):
                seen["pending"].pop(event.get("task_id"), None)
        elif kind == "tool.result":
            facts, text = payload.get("correlation_facts") or {}, payload.get("text") or ""
            name = facts.get("tool_name", "?")
            if facts.get("outcome") != "success":
                if name == "bash":  # a non-zero exit is ordinary work, e.g. a test run before the fix
                    seen["tools"]["bash"] += 1
                    continue
                seen["failed"].append(f"{name} — {text.splitlines()[0].split('; resolved candidate')[0][:200] if text else 'no message'}")
                continue
            seen["tools"][name] += 1
            target = re.match(r"Read \w+ file `([^`]+)`", text)
            if target and target.group(1) not in seen["read"]:
                seen["read"].append(target.group(1))
    return seen


def changed_files(cwd, since):
    """List files in the working folder touched after `since`: the observable trace of a --write run."""
    listed = subprocess.run(["git", "ls-files", "-m", "-o", "--exclude-standard"], cwd=cwd, capture_output=True, text=True, check=False)
    if listed.returncode == 0:
        candidates = [os.path.join(cwd, name) for name in listed.stdout.splitlines()]
    else:
        candidates = []
        for folder, subfolders, names in os.walk(cwd):
            subfolders[:] = [name for name in subfolders if name not in (".git", "node_modules", ".venv")]
            candidates += [os.path.join(folder, name) for name in names]
            if len(candidates) > 20000:
                return None
    return [path for path in candidates if os.path.isfile(path) and os.path.getmtime(path) >= since]


def short(paths, cwd):
    """Show paths under the working folder as relative."""
    roots = (cwd + os.sep, os.path.realpath(cwd) + os.sep)
    return ", ".join(path.removeprefix(roots[0]).removeprefix(roots[1]) for path in paths[:20])


def main():
    args = parse_args()
    brief = sys.stdin.read()
    if not brief.strip():
        fail(EXIT_USAGE, "the brief is empty; pass it on stdin")
    cwd = os.path.abspath(args.dir or os.getcwd())
    if not os.path.isdir(cwd):
        fail(EXIT_USAGE, f"--dir is not a folder: {cwd}")
    check_catalog()

    wall_start = time.time() - 1
    with tempfile.TemporaryDirectory(prefix="muse-brief-") as scratch:
        code, stdout, stderr, timed_out, elapsed = run_muse(args, brief, cwd, scratch)
    seen = read_events(stdout)
    notices = [line for line in stderr.splitlines() if "Skills:" not in line and "skills" not in line and "workspace root" not in line]
    resume_hint = f" Session {seen['session']} keeps the work done so far: --resume it with the same --dir." if seen["session"] else ""

    if timed_out:
        waiting = ", ".join(sorted(set(seen["pending"].values())))
        cause = f"Muse was inside {waiting}: a long command, or an approval nobody can give" if waiting else "the work did not finish"
        fail(EXIT_TIMEOUT, f"stopped after {args.timeout}: {cause}. Raise --timeout or narrow the brief.{resume_hint}")
    terminal = seen["terminal"] or {}
    if code != 0 or terminal.get("terminal") != "completed":
        reason = terminal.get("reason") or terminal.get("text") or "\n".join(notices) or f"muse exited {code} without a result"
        fail(EXIT_RUNTIME, f"{str(reason).strip()[:1500]}.{resume_hint}")
    if seen["model"] != MODEL:
        fail(EXIT_RUNTIME, f"muse ran {seen['model']} instead of {MODEL}; the answer is discarded")
    answer = (terminal.get("text") or "").strip()
    if not answer:
        fail(EXIT_RUNTIME, f"muse completed with an empty answer. muse stderr: {' | '.join(notices)[:800] or 'empty'}")

    if args.schema:
        try:
            answer = json.dumps(json.loads(answer), ensure_ascii=False, indent=2)
        except ValueError:
            pass
    print(answer)

    receipt = ["ok", f"{MODEL}/{EFFORT}", f"{elapsed:.0f}s", f"session {seen['session']}",
               "tools: " + (", ".join(f"{name}×{count}" for name, count in seen["tools"].items()) or "none")]
    if seen["read"]:
        receipt.append("read: " + short(seen["read"], cwd))
    if args.write:
        changed = changed_files(cwd, wall_start)
        receipt.append("changed: " + ("too many files to list" if changed is None else short(sorted(changed), cwd) or "nothing"))
    print("[muse] " + " · ".join(receipt), file=sys.stderr)
    for line in seen["failed"]:
        hint = " PDF, audio and other binary files do not open; text and images do." if "not valid UTF-8" in line else ""
        print(f"[muse] WARNING: tool call failed: {line}.{hint}", file=sys.stderr)
    for line in notices:
        if "warning" in line.lower():
            print(f"[muse] {line.removeprefix('muse: ')}", file=sys.stderr)


if __name__ == "__main__":
    main()
