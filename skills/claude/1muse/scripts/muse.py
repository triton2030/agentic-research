#!/usr/bin/env python3
"""Call a Muse model as a subagent through Muse Code (muse exec).

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

DEFAULT_MODEL = "muse-wonder-1.0"
DEFAULT_EFFORT = "high"
CATALOG = "~/.local/share/muse/model-catalog/*.json"

SHARED_RULES = (
    "Shared rules: do not commit unless the brief asks; leave edits that are not "
    "yours alone and never revert them; do not launch workflows or subagents and "
    "do not call other agents (Claude, Codex, Gemini) unless the brief asks; this "
    "brief and your replies come from an agent, so do not record them anywhere as "
    "the owner's words. Cite files as path:line.\n\n"
)
WRITER_NOTE = (
    "[Runtime note] You run headless as a subagent of another agent. You may edit "
    "files in the working folder and run shell commands in the sandbox; nobody "
    "confirms them. What you may change is set by the words of the brief: if it "
    "says to change no files, change none. "
) + SHARED_RULES
READ_ONLY_NOTE = (
    "[Runtime note] You run headless as a read-only subagent of another agent. "
    "You can read files, search and use the web. File writes and the shell are "
    "disabled for this run: if the task needs them, say so in the answer. "
) + SHARED_RULES

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
    parser.add_argument("--dir", help="working folder; Muse edits files only here (default: current folder)")
    parser.add_argument("--read-only", action="store_true", help="disable file writes and the shell for this run")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"model id from the Muse catalog (default: {DEFAULT_MODEL})")
    parser.add_argument("--effort", default=DEFAULT_EFFORT, help=f"reasoning effort (default: {DEFAULT_EFFORT})")
    parser.add_argument("--project-rules", action="store_true", help="trust the working folder for this run: load its AGENTS.md, skills and hooks")
    parser.add_argument("--resume", metavar="ID", help="continue the session with this id; needs the same --dir")
    parser.add_argument("--image", action="append", default=[], metavar="PATH", help="attach an image to the brief (repeatable)")
    parser.add_argument("--schema", help="JSON schema (string or file path); stdout becomes the parsed object")
    parser.add_argument("--timeout", default="9m", help="wall-clock limit; muse exec has none of its own (default: 9m)")
    return parser.parse_args()


def check_catalog(model, effort):
    """Muse serves an unknown model id without an error, so the choice is checked against the local catalog."""
    rows = {}
    for path in glob.glob(os.path.expanduser(CATALOG)):
        try:
            with open(path, encoding="utf-8") as handle:
                rows.update({row.get("model_id"): row for row in json.load(handle).get("rows", [])})
        except (OSError, ValueError):
            continue
    if not rows:
        return
    if model not in rows:
        visible = ", ".join(sorted(name for name, row in rows.items() if row.get("visibility") == "visible"))
        advice = "the owner picks the replacement for the default" if model == DEFAULT_MODEL else f"available: {visible}"
        fail(EXIT_RUNTIME, f"model {model} is not in the Muse catalog, and Muse would answer under that name with some other model; {advice}")
    tiers = [variant.get("tier") for variant in rows[model].get("reasoning_effort_variants") or []]
    if tiers and effort not in tiers:
        fail(EXIT_USAGE, f"effort {effort} is not offered for {model}; available: {', '.join(tiers)}")


def run_muse(args, brief, cwd, scratch):
    muse = shutil.which("muse")
    if not muse:
        fail(EXIT_RUNTIME, "muse (Muse Code) is not in PATH")
    prompt_file = os.path.join(scratch, "brief.txt")
    with open(prompt_file, "w", encoding="utf-8") as handle:
        handle.write((READ_ONLY_NOTE if args.read_only else WRITER_NOTE) + brief)
    command = [muse, "exec", "--json", "--model", args.model, "--reasoning-effort", args.effort,
               "--no-foreign-personal-context", "--prompt-file", prompt_file]
    command += ["--disable-write", "--disable-shell"] if args.read_only else ["--disable-approval"]
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
    """List files in the working folder touched after `since`: the observable trace of what Muse wrote."""
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
    check_catalog(args.model, args.effort)

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
    if seen["model"] != args.model:
        fail(EXIT_RUNTIME, f"muse ran {seen['model']} instead of {args.model}; the answer is discarded")
    answer = (terminal.get("text") or "").strip()
    if not answer:
        fail(EXIT_RUNTIME, f"muse completed with an empty answer. muse stderr: {' | '.join(notices)[:800] or 'empty'}")

    if args.schema:
        try:
            answer = json.dumps(json.loads(answer), ensure_ascii=False, indent=2)
        except ValueError:
            pass
    print(answer)

    receipt = ["ok", f"{args.model}/{args.effort}", f"{elapsed:.0f}s", f"session {seen['session']}",
               "tools: " + (", ".join(f"{name}×{count}" for name, count in seen["tools"].items()) or "none")]
    if seen["read"]:
        receipt.append("read: " + short(seen["read"], cwd))
    if not args.read_only:
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
