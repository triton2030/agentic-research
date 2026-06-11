#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from navigator.canon.evalkit import load_cases, render_markdown, run_case  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate md canon-check retrieval modes.")
    parser.add_argument("--corpus", default="/Users/triton/Documents/MAVO")
    parser.add_argument("--cases", default=None)
    parser.add_argument("--modes", default="A,B,C,D")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()

    corpus = Path(args.corpus).expanduser().resolve()
    cases_path = Path(args.cases).expanduser() if args.cases else corpus / "_workspace/eval/canon-cases.json"
    cases = load_cases(cases_path)
    modes = [mode.strip() for mode in args.modes.split(",") if mode.strip()]

    results = []
    command = " ".join(sys.argv)

    def write_report() -> None:
        report = render_markdown(results, command=command)
        if args.out == "-":
            return
        Path(args.out).write_text(report, encoding="utf-8")

    for mode in modes:
        for case in cases:
            try:
                results.append(run_case(corpus, case, mode, limit=args.limit))
            except RuntimeError as exc:
                print(exc, file=sys.stderr)
                write_report()
                return 1
    report = render_markdown(results, command=command)
    if args.out == "-":
        print(report, end="")
    else:
        Path(args.out).write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
