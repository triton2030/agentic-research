#!/usr/bin/env python3
"""Целостность провенанса: указывает ли якорь `holder.md:N` на ту цитату,
которую документ приводит рядом.

Зачем: `chat_capture.py` дописывает новые пары `type`/`topic` во frontmatter
открытой сессии, и каждая вставка сдвигает все ранее записанные адреса вниз.
Съехавший на строку якорь остаётся «валидным» — он попадает на соседнюю
запись, — поэтому сверка по существованию строки его не ловит. Ловит только
сверка с текстом цитаты, приведённой в документе перед ссылкой.

Приёмка `evaluate_anchors.py` к строке слепа намеренно: она резолвит holder.
Этот прогон отвечает на другой вопрос — не «найдётся ли сессия», а «читает ли
агент, пришедший по адресу, те слова владельца, ради которых адрес поставлен».

Замер 2026-08-20 на первом прогоне: 2 верных из 30 проверяемых.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ANCHOR = re.compile(
    r"_ops/chat-recall/(\d{4}-\d{2}-\d{2}-\d{6}-[A-Za-z]+-[a-z0-9]+\.md):(\d+)"
)
QUOTE = re.compile(r"«([^»]{20,300})»")
SKIP = ("_ops/chat-recall", "_workspace", ".git", "node_modules", ".venv")
PROBE_WORDS = 5
LOOKBEHIND = 700


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower().replace("ё", "е")
    return " ".join(re.sub(r"[^\w\s]", " ", value).split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    corpus = args.repo / "_ops/chat-recall"
    holders = {
        path.name: path.read_text(encoding="utf-8").splitlines()
        for path in corpus.glob("*.md")
    }

    rot: list[dict[str, object]] = []
    right = 0
    unverifiable = 0
    for path in args.repo.rglob("*.md"):
        text_path = str(path)
        if any(part in text_path for part in SKIP):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in ANCHOR.finditer(text):
            name, lineno = match.group(1), int(match.group(2))
            lines = holders.get(name)
            if lines is None:
                continue
            quotes = QUOTE.findall(text[max(0, match.start() - LOOKBEHIND) : match.start()])
            words = _norm(quotes[-1]).split() if quotes else []
            if len(words) < PROBE_WORDS:
                unverifiable += 1
                continue
            probe = " ".join(words[:PROBE_WORDS])
            here = _norm(lines[lineno - 1]) if 0 < lineno <= len(lines) else ""
            if probe in here:
                right += 1
                continue
            actual = next(
                (index + 1 for index, line in enumerate(lines) if probe in _norm(line)),
                None,
            )
            rot.append(
                {
                    "document": str(path.relative_to(args.repo)),
                    "anchor": f"{name}:{lineno}",
                    "actual_line": actual,
                    "quote": quotes[-1][:80],
                }
            )

    report = {
        "verifiable": right + len(rot),
        "correct": right,
        "rotten": len(rot),
        "unverifiable_no_quote": unverifiable,
        "rows": rot,
        "passed": not rot,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(
            f"проверяемых якорей: {report['verifiable']} · верных: {right} · "
            f"на чужой строке: {len(rot)} · без цитаты рядом: {unverifiable}"
        )
        for row in rot:
            print(f"  {row['document']}\n     {row['anchor']} → {row['actual_line']}  «{row['quote']}»")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
