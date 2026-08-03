#!/usr/bin/env python3
"""Run the pinned Russian paraphrase regression against a recall corpus."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
CASES = Path(__file__).with_name("retrieval_cases.json")
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("chat_digest_eval", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import chat_digest.py")
DIGEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIGEST)


def _ranking(corpus: Path, query: str, *, lexical: bool) -> list[str]:
    if lexical:
        command = [sys.executable, str(SCRIPT)]
    else:
        command = [
            "uv",
            "run",
            "--offline",
            "--locked",
            "--script",
            str(SCRIPT),
        ]
    command.extend(
        (
            str(corpus),
            "--query",
            query,
            "--json",
            "--limit",
            "10",
            "--max-chars",
            "200000",
        )
    )
    if lexical:
        command.append("--lexical")
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise RuntimeError(f"cannot start retrieval command: {error}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"retrieval command failed: {detail}")
    payload = json.loads(completed.stdout)
    return [record["record_id"] for record in payload["records"]]


def _metrics(
    cases: list[dict[str, Any]], rankings: list[list[str]]
) -> tuple[dict[str, float], list[str]]:
    positions: list[float] = []
    failed_at_five: list[str] = []
    for case, ranking in zip(cases, rankings, strict=True):
        found = [
            ranking.index(record_id) + 1
            for record_id in case["relevant"]
            if record_id in ranking
        ]
        position = min(found) if found else math.inf
        positions.append(position)
        if position > 5:
            failed_at_five.append(case["id"])
    count = len(cases)
    return (
        {
            "hit@1": round(sum(position <= 1 for position in positions) / count, 3),
            "hit@5": round(sum(position <= 5 for position in positions) / count, 3),
            "hit@10": round(sum(position <= 10 for position in positions) / count, 3),
            "mrr@10": round(
                sum(0.0 if position > 10 else 1.0 / position for position in positions)
                / count,
                3,
            ),
        },
        failed_at_five,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--cases", type=Path, default=CASES)
    parser.add_argument("--min-hit-at-five", type=float, default=0.90)
    args = parser.parse_args()

    records, _ = DIGEST.load(args.corpus)
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    known = {record["record_id"] for record in records}
    missing = sorted(
        record_id
        for case in cases
        for record_id in case["relevant"]
        if record_id not in known
    )
    if missing:
        print(json.dumps({"error": "missing-targets", "record_ids": missing}))
        return 2

    lexical_rankings: list[list[str]] = []
    hybrid_rankings: list[list[str]] = []
    for case in cases:
        lexical_rankings.append(_ranking(args.corpus, case["query"], lexical=True))
        hybrid_rankings.append(_ranking(args.corpus, case["query"], lexical=False))

    lexical, lexical_failed = _metrics(cases, lexical_rankings)
    hybrid, hybrid_failed = _metrics(cases, hybrid_rankings)
    passed = (
        hybrid["hit@5"] >= args.min_hit_at_five
        and hybrid["hit@5"] > lexical["hit@5"]
    )
    print(
        json.dumps(
            {
                "records": len(records),
                "cases": len(cases),
                "model": DIGEST.EMBEDDING_MODEL,
                "revision": DIGEST.EMBEDDING_REVISION,
                "hybrid_depth": DIGEST.HYBRID_DEPTH,
                "lexical": lexical,
                "hybrid": hybrid,
                "delta_hit@5": round(hybrid["hit@5"] - lexical["hit@5"], 3),
                "failed_at_five": {
                    "lexical": lexical_failed,
                    "hybrid": hybrid_failed,
                },
                "threshold": {"min_hybrid_hit@5": args.min_hit_at_five},
                "passed": passed,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
