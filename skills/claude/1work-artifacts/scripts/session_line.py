#!/usr/bin/env python3
"""Add this session's line, or an archive-list mark, to <work folder>/agents/sessions.md."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HEADER = """# Sessions

One line per session that worked in this folder, so another session can ask it about the work.
How to message a session from its line: skill `1work-artifacts`, file `references/reach-a-session.md`.

"""

# A child process inherits its parent's variables too, so the agent names
# itself and only its own variable is read.
SESSION_ENV = {"claude": "CLAUDE_CODE_SESSION_ID", "codex": "CODEX_THREAD_ID"}
LISTED = "listed for the owner's archive decision"
KEPT = "kept by the owner"
MARKS = (LISTED, KEPT)


def t3_cli() -> str | None:
    found = os.environ.get("T3CODE_CLI_PATH") or shutil.which("t3")
    if found:
        return found
    default = Path.home() / ".t3" / "bin" / "t3"
    return str(default) if default.is_file() else None


def t3_provider(thread: str) -> tuple[str | None, str | None]:
    """Return the provider T3 runs the thread with, or a note why it is unknown."""
    cli = t3_cli()
    if not cli:
        return None, "no t3 command"
    try:
        shown = subprocess.run(
            [cli, "thread", "show", thread, "--json", "--messages", "0"],
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
        return json.loads(shown.stdout)["thread"]["providerInstanceId"] or "", None
    except (
        OSError,
        subprocess.SubprocessError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        return None, exc.__class__.__name__


def t3_userdata() -> Path:
    return Path(os.environ.get("T3CODE_HOME") or Path.home() / ".t3") / "userdata"


def t3_thread_of_codex(codex_id: str) -> tuple[str | None, str | None]:
    """Find the T3 thread that runs this Codex session in T3's own records.

    T3 gives Codex no T3CODE_THREAD_ID and has no command for this, so the
    lookup reads T3's state database; a change there leaves the line without it.
    """
    database = t3_userdata() / "statev2.sqlite"
    if not database.is_file():
        return None, None
    try:
        with sqlite3.connect(
            f"file:{database}?mode=ro", uri=True, timeout=5
        ) as connection:
            rows = connection.execute(
                "select distinct thread_id from orchestration_v2_projection_provider_threads "
                "where provider_instance_id like '%codex%' and payload_json like ?",
                (f"%{codex_id}%",),
            ).fetchall()
    except sqlite3.Error as exc:
        return None, f"T3 thread of this Codex session not found: {exc}"
    if len(rows) != 1:
        return None, f"T3 thread of this Codex session not found: {len(rows)} matches"
    return rows[0][0], None


def t3_log_names(thread: str, session: str) -> bool | None:
    """Whether T3's provider log of the thread names this session; None if no log."""
    name = thread.replace(":", "-")
    logs = sorted((t3_userdata() / "logs" / "provider").glob(f"events.{name}.log*"))
    if not logs:
        return None
    return any(
        session in log.read_text(encoding="utf-8", errors="replace") for log in logs
    )


def own_t3_thread(
    agent: str, session: str | None, given: str | None
) -> tuple[str | None, str | None]:
    """Return this session's T3 thread id and a note.

    A process started from another session's shell inherits that session's
    T3CODE_THREAD_ID; a message sent there would reach the parent instead.
    Codex under T3 gets no T3CODE_THREAD_ID; its thread is looked up instead.
    """
    thread = given or os.environ.get("T3CODE_THREAD_ID")
    looked_up = False
    if not thread and agent == "codex" and session:
        thread, problem = t3_thread_of_codex(session)
        looked_up = True
        if not thread:
            return None, problem
    if not thread:
        return None, None
    provider, problem = t3_provider(thread)
    if provider is None:
        return thread, f"T3 thread kept unchecked: {problem}"
    if agent not in provider.lower():
        return None, f"T3 thread {thread} runs {provider}, not {agent}: left out"
    if not (given or looked_up) and session and t3_log_names(thread, session) is False:
        return None, f"T3 thread {thread} belongs to another {agent} session: left out"
    return thread, None


def add_thread_to_own_line(
    lines: list[str], own_id: str, thread: str | None, agent: str, session: str | None
) -> bool | None:
    """Give this session's existing line its T3 thread; None if it has no line yet."""
    for index, line in enumerate(lines):
        if own_id in line and not any(mark in line for mark in MARKS):
            if not thread or "T3 thread" in line or not session:
                return False
            lines[index] = line.replace(
                f" · {agent} session {session}",
                f" · T3 thread {thread} · {agent} session {session}",
                1,
            )
            return True
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="the work folder")
    parser.add_argument("--agent", choices=sorted(SESSION_ENV), required=True)
    parser.add_argument("--model", required=True, help="your model id")
    parser.add_argument(
        "--t3-thread",
        help="your T3 thread id, when you know it and the script cannot find it",
    )
    line_kind = parser.add_mutually_exclusive_group(required=True)
    line_kind.add_argument("--does", help="what this session does in the folder")
    line_kind.add_argument(
        "--listed",
        action="store_true",
        help="instead of a session line, mark the folder as listed for the owner's archive decision",
    )
    line_kind.add_argument(
        "--kept",
        metavar="REASON",
        help="instead of a session line, record that the owner chose to keep the folder, and why",
    )
    args = parser.parse_args()

    does = " ".join((args.does or "").split())
    reason = " ".join((args.kept or "").split())
    if (args.does is not None and not does) or (args.kept is not None and not reason):
        print("the text after --does or --kept is empty", file=sys.stderr)
        return 2
    if not args.folder.is_dir():
        print(f"no such folder: {args.folder}", file=sys.stderr)
        return 2
    session = os.environ.get(SESSION_ENV[args.agent])
    thread, note = own_t3_thread(args.agent, session, args.t3_thread)
    if not session and not thread:
        print(
            f"no {SESSION_ENV[args.agent]} or T3 thread: "
            "write the line by hand with how to reach you",
            file=sys.stderr,
        )
        return 2

    sessions = args.folder / "agents" / "sessions.md"
    text = sessions.read_text(encoding="utf-8") if sessions.is_file() else ""
    own_id = session or thread
    if does:
        lines = text.splitlines(keepends=True)
        added = add_thread_to_own_line(lines, own_id, thread, args.agent, session)
        if added:
            sessions.write_text("".join(lines), encoding="utf-8")
            print(f"added T3 thread {thread} to your line in {sessions}")
            return 0
        if added is False:
            print(f"already listed in {sessions}")
            return 0

    who = [f"{args.agent.capitalize()} {args.model}"]
    if thread:
        who.append(f"T3 thread {thread}")
    if session:
        who.append(f"{args.agent} session {session}")
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    if args.listed:
        parts = [now, LISTED, "by " + ", ".join(who)]
    elif reason:
        parts = [now, KEPT, reason, "by " + ", ".join(who)]
    else:
        parts = [now, *who, does]
    line = "- " + " · ".join(parts) + "\n"

    sessions.parent.mkdir(exist_ok=True)
    with sessions.open("a", encoding="utf-8") as output:
        if not text:
            output.write(HEADER)
        output.write(line)
    print(line.rstrip())
    if note:
        print(note, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
