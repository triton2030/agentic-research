#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["fastembed==0.8.0"]
# ///
"""Покрытие производных слоёв корпусом: сколько долгоживущих правил вообще
имеет опору в словах владельца.

Знаменатель берётся ВНЕ корпуса — правила из глобальной инструкции, AGENTS.md
и файлов памяти. Это не приёмка ретривала (та в `evaluate_anchors.py`), а
вопрос захвата: «что толку от чтения того, чего нет».

Единица измерения — session holder, а не цитата: скил отдаёт до десяти файлов
и агент читает выбранные целиком. Поэтому «опора есть» означает, что позиция
владельца лежит в одном из выданных файлов, а «опоры нет» — что скил отдал
десять сессий и ни в одной её нет.

Поиск идёт по полному dense-тексту записи (цитата + `context-note`): note
называет вещи своими именами, когда цитата сформулирована как попало, и для
этого он и написан. Судить опору по note нельзя: его писал агент, а не
владелец, — вердикт всегда ссылается на строку с цитатой.

Прогон: `python3 evaluate_capture.py <repo>` — печатает доли по слоям и
список правил без опоры. Вердикты хранятся в `capture_cases.json` и
проверяются здесь же: адрес обязан существовать и быть цитатой владельца.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
CASES = Path(__file__).with_name("capture_cases.json")
HOLDER_LIMIT = 10
READING_DEPTH = 4  # обычная глубина погружения по контракту скила

if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
_SPEC = importlib.util.spec_from_file_location("chat_digest_capture", SCRIPT)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot import chat_digest.py")
DIGEST = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(DIGEST)


def _holders(records: list[dict[str, Any]], query: str) -> list[str]:
    """Десятка session-holder файлов — ровно то, что скил отдаёт агенту."""
    args = DIGEST.build_parser().parse_args(
        [".", "--query", query, "--limit", str(HOLDER_LIMIT)]
    )
    ranking, _, cards, _ = DIGEST._retrieve(records, args)
    selected, _ = DIGEST._select_holders(ranking, cards, HOLDER_LIMIT)
    return [record["file"] for record in selected]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--min-supported", type=float, default=None)
    parser.add_argument("--dump", type=Path, help="выгрузить выдачу для судейства")
    args = parser.parse_args()

    records, _ = DIGEST.load(args.repo / "_ops/chat-recall")
    by_address = {record["address"]: record for record in records}
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    rules = cases["rules"]

    bad: list[str] = []
    dump: list[dict[str, Any]] = []
    for rule in rules:
        holders = _holders(records, rule["rule"])
        short = rule.get("query_short")
        holders_short = _holders(records, short) if short else []
        rule["_holders"] = holders
        evidence = rule.get("evidence")
        if rule["verdict"] in {"опора", "частичная"}:
            if not evidence:
                bad.append(f"{rule['id']}: вердикт без адреса")
                continue
            record = by_address.get(evidence)
            if record is None:
                bad.append(f"{rule['id']}: адрес {evidence} не существует")
            elif record["kind"] not in {"quote", "selection"}:
                bad.append(f"{rule['id']}: {evidence} — не слова владельца")
            else:
                owner_file = record["file"]
                rule["_in_holders"] = owner_file in holders
                rule["_in_holders_short"] = owner_file in holders_short
                rule["_holder_rank"] = (
                    holders.index(owner_file) + 1 if owner_file in holders else None
                )
        if args.dump:
            dump.append(
                {
                    "id": rule["id"],
                    "rule": rule["rule"],
                    "holders": holders,
                    "quotes": [
                        {"a": r["address"], "q": r["text"][:300]}
                        for r in records
                        if r["file"] in holders[:READING_DEPTH]
                    ],
                }
            )

    if args.dump:
        args.dump.write_text(
            json.dumps(dump, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    def share(subset: list[dict[str, Any]], *, strict: bool) -> float:
        if not subset:
            return 0.0
        good = {"опора"} if strict else {"опора", "частичная"}
        return sum(1 for r in subset if r["verdict"] in good) / len(subset)

    report: dict[str, Any] = {"total": len(rules), "layers": {}, "classes": {}}
    for key, field in (("layers", "layer"), ("classes", "class")):
        for name in sorted({rule[field] for rule in rules}):
            subset = [rule for rule in rules if rule[field] == name]
            report[key][name] = {
                "n": len(subset),
                "verdicts": dict(Counter(r["verdict"] for r in subset)),
                "supported": round(share(subset, strict=True), 3),
                "supported_or_partial": round(share(subset, strict=False), 3),
            }

    owner = [rule for rule in rules if rule["class"] == "owner-attributed"]
    reachable = [rule for rule in owner if rule.get("_in_holders")]
    within_depth = [
        rule
        for rule in reachable
        if rule.get("_holder_rank") and rule["_holder_rank"] <= READING_DEPTH
    ]
    report["owner_rules"] = {
        "n": len(owner),
        "supported": round(share(owner, strict=True), 3),
        "supported_or_partial": round(share(owner, strict=False), 3),
        "unsupported": [rule["id"] for rule in owner if rule["verdict"] == "нет"],
        "contradicted": [
            rule["id"] for rule in rules if rule["verdict"] == "противоречие"
        ],
    }
    dual = [rule for rule in rules if rule.get("query_short") and rule.get("evidence")]
    hit_long = sum(1 for r in dual if r.get("_in_holders"))
    hit_short = sum(1 for r in dual if r.get("_in_holders_short"))
    hit_union = sum(
        1 for r in dual if r.get("_in_holders") or r.get("_in_holders_short")
    )
    report["retrieval_of_support"] = {
        "note": (
            "опора записана — находит ли её продукт. Две формулировки одного "
            "предмета находят РАЗНЫЕ сессии, поэтому один запрос недостаточен."
        ),
        "in_top10": len(reachable),
        "in_top4": len(within_depth),
        "of_supported": sum(
            1 for r in owner if r["verdict"] in {"опора", "частичная"}
        ),
        "two_queries": {
            "n": len(dual),
            "rule_wording": round(hit_long / len(dual), 3) if dual else 0.0,
            "short_wording": round(hit_short / len(dual), 3) if dual else 0.0,
            "union": round(hit_union / len(dual), 3) if dual else 0.0,
        },
    }
    report["integrity"] = bad
    report["passed"] = not bad and (
        args.min_supported is None
        or report["owner_rules"]["supported_or_partial"] >= args.min_supported
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
