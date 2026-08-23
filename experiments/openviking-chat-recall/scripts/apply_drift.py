#!/usr/bin/env python3
"""Правка съехавших якорей во всей библиотеке — одной одновременной заменой.

Замены нельзя делать по очереди. Сдвиг файла означает, что строка-приёмник
одной правки бывает строкой-источником другой: заменив L22 на L27, вторым
проходом получишь L27 -> L33 и испортишь верную ссылку. Поэтому таблица
применяется за один проход, а конфликт «один источник — два адресата» не
разрешается автоматически, а называется и оставляется человеку.

    python3 apply_drift.py [--dry] [<папка прогонов>]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict

WIKI = "experiments/openviking-chat-recall/artifacts/wiki-v1"
TOPICS = "_ops/chat-recall-topics"
LINE = re.compile(r"L(\d+)")


def table(runs: str) -> tuple[dict[str, dict[int, int]], list[str]]:
    moves: dict[str, dict[int, set[int]]] = defaultdict(lambda: defaultdict(set))
    notes: list[str] = []
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        name = os.path.basename(path)[:-5] + ".md"
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            notes.append(f"{name}: нет JSON")
            continue
        if not payload.get("ok"):
            notes.append(f"{name}: прогон не принят")
            continue
        for line in (payload.get("response") or "").splitlines():
            if line.count("\t") < 3:
                continue
            _, was, now, verdict = [p.strip() for p in line.split("\t", 3)]
            if "исправлен" not in verdict.lower():
                continue
            old, new = LINE.search(was), LINE.search(now)
            if old and new and old.group(1) != new.group(1):
                moves[name][int(old.group(1))].add(int(new.group(1)))
    clean: dict[str, dict[int, int]] = {}
    for name, pairs in moves.items():
        good = {}
        for old, targets in pairs.items():
            if len(targets) == 1:
                good[old] = targets.pop()
            else:
                notes.append(f"{name}#L{old}: два адресата {sorted(targets)} — не трогаю")
        if good:
            clean[name] = good
    return clean, notes


def rewrite(path: str, moves: dict[str, dict[int, int]]) -> int:
    text = open(path, encoding="utf-8").read()
    changed = 0

    def swap(hit: re.Match) -> str:
        nonlocal changed
        name, number = hit.group(1), int(hit.group(2))
        target = moves.get(name, {}).get(number)
        if target is None:
            return hit.group(0)
        changed += 1
        return f"{name}#L{target}"

    fresh = re.sub(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)", swap, text)
    if changed:
        open(path, "w", encoding="utf-8").write(fresh)
    return changed


def main(runs: str, dry: bool) -> int:
    moves, notes = table(runs)
    total = sum(len(v) for v in moves.values())
    print(f"разговоров с правками: {len(moves)} | якорей к переносу: {total}")
    for note in notes:
        print(f"  {note}")
    for name, pairs in sorted(moves.items()):
        print(f"  {name}: " + ", ".join(f"L{a}->L{b}" for a, b in sorted(pairs.items())))
    if dry:
        return 0
    touched = 0
    for root in (WIKI, TOPICS):
        for path in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
            touched += rewrite(path, moves)
    print(f"ссылок переписано: {touched}")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-drift/runs", "--dry" in sys.argv))
