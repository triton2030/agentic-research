#!/usr/bin/env python3
"""Калибровка гейта поддержки: запросы по делу против запросов вне корпуса.

Считает `dense_top1` обоими полюсами и проверяет, что действующие
SUPPORT_STRONG / SUPPORT_WEAK не отсекают материал, который в корпусе есть.
Пороги привязаны к модели: после смены EMBEDDING_MODEL прогон обязателен.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
POSITIVE = Path(__file__).with_name("retrieval_cases.json")
NEGATIVE = Path(__file__).with_name("support_cases.json")
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("chat_digest_support", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import chat_digest.py")
DIGEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIGEST)


def _probe(corpus: Path, query: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            "uv", "run", "--offline", "--locked", "--script", str(SCRIPT),
            str(corpus), "--query", query, "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"digest failed for {query!r}: {result.stderr[-400:]}")
    payload = json.loads(result.stdout)
    support = payload.get("support")
    if support is None and not payload.get("matched"):
        # Лексический канал не нашёл ничего, dense не запускался: выдача пуста,
        # и это сильнейшая форма «в корпусе нет».
        support = "unsupported"
    return {
        "query": query,
        "top1": payload.get("dense_top1"),
        "support": support,
        "matched": payload.get("matched", 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()

    positives = [case["query"] for case in json.loads(POSITIVE.read_text())["cases"]]
    negatives = json.loads(NEGATIVE.read_text())["unsupported_queries"]

    hits = [_probe(args.corpus, query) for query in positives]
    misses = [_probe(args.corpus, query) for query in negatives]
    unresolved = [row for row in hits + misses if row["support"] is None]
    if unresolved:
        print(
            json.dumps(
                {
                    "error": "нет вердикта поддержки; hybrid-путь недоступен",
                    "queries": [row["query"] for row in unresolved],
                },
                ensure_ascii=False,
            )
        )
        return 2

    false_abstain = [row for row in hits if row["support"] == "unsupported"]
    false_support = [row for row in misses if row["support"] == "supported"]
    report = {
        "thresholds": {
            "strong": DIGEST.SUPPORT_STRONG,
            "weak": DIGEST.SUPPORT_WEAK,
        },
        "positive": {
            "n": len(hits),
            "top1_min": round(min(row["top1"] for row in hits if row["top1"] is not None), 4),
            "top1_median": round(
                sorted(row["top1"] for row in hits if row["top1"] is not None)[
                    sum(1 for row in hits if row["top1"] is not None) // 2
                ],
                4,
            ),
            "supported": sum(1 for row in hits if row["support"] == "supported"),
            "weak": sum(1 for row in hits if row["support"] == "weak"),
            "unsupported": len(false_abstain),
        },
        "negative": {
            "n": len(misses),
            "top1_max": round(
                max(
                    (row["top1"] for row in misses if row["top1"] is not None),
                    default=0.0,
                ),
                4,
            ),
            "empty_result": sum(1 for row in misses if not row["matched"]),
            "supported": len(false_support),
            "weak": sum(1 for row in misses if row["support"] == "weak"),
            "unsupported": sum(1 for row in misses if row["support"] == "unsupported"),
        },
        "false_abstain": [row["query"] for row in false_abstain],
        "false_support": [row["query"] for row in false_support],
        "passed": not false_abstain and not false_support,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
