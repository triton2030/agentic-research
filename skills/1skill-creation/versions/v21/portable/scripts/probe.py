#!/usr/bin/env python3
"""Sandbox for skill probes and the order of a probe agent's actions.

init  — copy a skill version and a pristine case into a fresh folder
        under /tmp, so each run starts from the same input.
order — print a subagent's tool calls in order from its transcript
        (the JSONL output file), so the order is observed, not reported.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def init(args: argparse.Namespace) -> None:
    run = Path(args.out) / args.run
    if run.exists():
        sys.exit(f"{run} already exists: pick a new run name")
    shutil.copytree(args.skill, run / "skill")
    if args.case:
        shutil.copytree(args.case, run / "case")
    print(f"skill: {run / 'skill'}")
    if args.case:
        print(f"case:  {run / 'case'}")


def short(value: object, width: int) -> str:
    return " ".join(str(value).split())[:width]


def order(args: argparse.Namespace) -> None:
    step = 0
    with open(args.transcript, encoding="utf-8") as lines:
        for line in lines:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "assistant":
                continue
            for part in entry.get("message", {}).get("content") or []:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "tool_use":
                    step += 1
                    data = part.get("input") or {}
                    target = (
                        data.get("file_path")
                        or data.get("command")
                        or data.get("pattern")
                        or ""
                    )
                    print(f"{step:3} {part.get('name')}\t{short(target, args.width)}")
                elif part.get("type") == "text":
                    step += 1
                    print(f"{step:3} TEXT {len(part.get('text', ''))} chars")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)

    p_init = commands.add_parser(
        "init", help="copy a skill version and a case into OUT/RUN"
    )
    p_init.add_argument("skill", help="skill folder to copy (the version under test)")
    p_init.add_argument(
        "--case", help="pristine case folder; never point probes at it directly"
    )
    p_init.add_argument(
        "--out",
        default="/tmp/skill-probe",
        help="sandbox root (default: /tmp/skill-probe)",
    )
    p_init.add_argument("--run", required=True, help="run name, e.g. old-a or new-b")
    p_init.set_defaults(func=init)

    p_order = commands.add_parser("order", help="list a subagent's tool calls in order")
    p_order.add_argument("transcript", help="subagent output file (JSONL)")
    p_order.add_argument("--width", type=int, default=160, help="max chars per target")
    p_order.set_defaults(func=order)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
