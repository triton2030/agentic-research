#!/usr/bin/env python3
"""Дешёвые проекции recall-лога: инвентарь тем и построчный digest цитат.

Без флагов — инвентарь (карта корпуса за сотни токенов). Любой фильтр или
--digest — построчная проекция с адресами файл:строка для точечного возврата
к полной цитате. Сырые файлы читать не нужно.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

QUOTE_LINE = re.compile(
    r'^\* (?P<ts>\S+) — "(?P<quote>.*)" — type: (?P<type>[^|]+)\| topic: (?P<topic>.+)$'
)


def load(corpus: Path) -> tuple[list[dict], int]:
    """Все цитаты корпуса + счётчик строк-звёздочек, не прошедших парсинг."""
    rows: list[dict] = []
    unparsed = 0
    for path in sorted(corpus.glob("*.md")):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            if not line.startswith("* "):
                continue
            match = QUOTE_LINE.match(line)
            if not match:
                unparsed += 1
                continue
            rows.append(
                {
                    "file": path.name,
                    "line": lineno,
                    "date": match.group("ts")[:10],
                    "type": match.group("type").strip(),
                    "topic": match.group("topic").strip(),
                    "quote": match.group("quote"),
                }
            )
    return rows, unparsed


def inventory(rows: list[dict], unparsed: int) -> str:
    topics: dict[str, dict] = defaultdict(
        lambda: {"n": 0, "types": defaultdict(int), "first": "9999", "last": "0000"}
    )
    type_totals: dict[str, int] = defaultdict(int)
    for row in rows:
        entry = topics[row["topic"]]
        entry["n"] += 1
        entry["types"][row["type"]] += 1
        entry["first"] = min(entry["first"], row["date"])
        entry["last"] = max(entry["last"], row["date"])
        type_totals[row["type"]] += 1
    lines = []
    for name, entry in sorted(topics.items(), key=lambda kv: -kv[1]["n"]):
        mix = " ".join(
            f"{t}:{n}" for t, n in sorted(entry["types"].items(), key=lambda kv: -kv[1])
        )
        lines.append(f'{entry["n"]:4d}  {name:22s} {entry["first"]}…{entry["last"]}  {mix}')
    totals = " ".join(f"{t}:{n}" for t, n in sorted(type_totals.items(), key=lambda kv: -kv[1]))
    lines.append(f"---- всего {len(rows)} цитат / {len(topics)} topics; {totals}")
    if unparsed:
        lines.append(f"---- ВНИМАНИЕ: {unparsed} строк не распарсено (формат разошёлся со скриптом)")
    return "\n".join(lines)


def digest(rows: list[dict], head: int) -> str:
    lines = []
    current_file = None
    for row in rows:
        if row["file"] != current_file:
            current_file = row["file"]
            lines.append(f"=== {current_file}")
        quote = row["quote"]
        clipped = quote[:head] + ("…" if len(quote) > head else "")
        lines.append(
            f'L{row["line"]} {row["date"][5:]} {row["type"][:4]}/{row["topic"]} · {clipped}'
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path, help="папка _ops/chat-recall проекта")
    parser.add_argument("--digest", action="store_true", help="построчная проекция вместо инвентаря")
    parser.add_argument("--type", dest="types", help="фильтр по типам, через запятую")
    parser.add_argument("--topic", dest="topics", help="фильтр по topics, через запятую")
    parser.add_argument("--grep", help="regex по тексту цитаты, без регистра")
    parser.add_argument("--since", help="только цитаты с даты YYYY-MM-DD")
    parser.add_argument("--head", type=int, default=110, help="символов цитаты в digest (default 110)")
    args = parser.parse_args()

    if not args.corpus.is_dir():
        print(f"нет папки: {args.corpus}", file=sys.stderr)
        return 2
    rows, unparsed = load(args.corpus)
    if not rows:
        print(f"в {args.corpus} нет распознанных цитат", file=sys.stderr)
        return 1

    filtered = rows
    if args.types:
        wanted = {t.strip() for t in args.types.split(",")}
        filtered = [r for r in filtered if r["type"] in wanted]
    if args.topics:
        wanted = {t.strip() for t in args.topics.split(",")}
        filtered = [r for r in filtered if r["topic"] in wanted]
    if args.grep:
        pattern = re.compile(args.grep, re.IGNORECASE)
        filtered = [r for r in filtered if pattern.search(r["quote"])]
    if args.since:
        filtered = [r for r in filtered if r["date"] >= args.since]

    wants_digest = args.digest or args.types or args.topics or args.grep or args.since
    text = digest(filtered, args.head) if wants_digest else inventory(filtered, unparsed)
    print(text)
    print(
        f"--- {len(filtered)}/{len(rows)} цитат, {len(text)} символов (~{len(text) // 4} токенов)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
