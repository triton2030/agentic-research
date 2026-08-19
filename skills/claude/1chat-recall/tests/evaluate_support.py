#!/usr/bin/env python3
"""Калибровка query_domain на трёх полюсах.

Проверяемое утверждение узкое: сырой косинус ближайшей записи различает
«запрос про предмет проекта» и «запрос про постороннее». Третья группа,
`in_domain_absent`, держится в наборе не как проверка, а как предъявленный
предел: эти вопросы в лексике проекта, ответа на них в корпусе нет, и порог
их не отделяет. Прогон печатает их вердикты, чтобы предел был виден, а не
подразумевался. Пороги привязаны к модели: после смены EMBEDDING_MODEL
прогон обязателен.
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
CASES = Path(__file__).with_name("support_cases.json")
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
    verdict = payload.get("query_domain")
    if verdict is None and not payload.get("matched"):
        # Лексический канал не нашёл ничего, dense не запускался: выдача пуста.
        verdict = "off-domain"
    holders = payload.get("holders") or []
    return {
        "query": query,
        "top1": payload.get("dense_top1"),
        "verdict": verdict,
        "files": [holder["file"] for holder in holders],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()
    cases = json.loads(CASES.read_text(encoding="utf-8"))

    off = [_probe(args.corpus, query) for query in cases["off_domain"]]
    present = [
        {**_probe(args.corpus, case["q"]), "holder": case["holder"]}
        for case in cases["in_domain_present"]
    ]
    for row in present:
        row["found"] = row["holder"] in row["files"]
    absent = [_probe(args.corpus, case["q"]) for case in cases["in_domain_absent"]]

    scored = [row for row in present if row["top1"] is not None]
    leak = [row for row in off if row["verdict"] == "in-domain"]
    miss = [row for row in present if row["verdict"] != "in-domain"]
    lost = [row for row in present if not row["found"]]

    report = {
        "thresholds": {"strong": DIGEST.DOMAIN_STRONG, "weak": DIGEST.DOMAIN_WEAK},
        "off_domain": {
            "n": len(off),
            "top1_max": round(
                max((row["top1"] for row in off if row["top1"] is not None), default=0.0),
                4,
            ),
            "leaked_as_in_domain": [row["query"] for row in leak],
        },
        "in_domain_present": {
            "n": len(present),
            "top1_min": round(min(row["top1"] for row in scored), 4),
            "not_in_domain": [row["query"] for row in miss],
            "holder_not_returned": [row["query"] for row in lost],
        },
        "in_domain_absent": {
            "n": len(absent),
            "note": "предел метода: порог эту группу не отделяет",
            "verdicts": {row["query"]: row["verdict"] for row in absent},
            "top1_range": [
                round(min(row["top1"] for row in absent if row["top1"] is not None), 4),
                round(max(row["top1"] for row in absent if row["top1"] is not None), 4),
            ],
            "above_present_minimum": sum(
                1
                for row in absent
                if row["top1"] is not None
                and row["top1"] >= min(item["top1"] for item in scored)
            ),
        },
        "passed": not leak and not miss and not lost,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
