#!/usr/bin/env python3
"""Провенанс слияния: у каждого якоря входа ровно одна судьба.

Якорь либо стоит при текущем пункте, либо его superseded/unresolved судьба
названа в техническом run-receipt. Reader-facing topic не хранит tombstone.

Инвариант 6 протокола quotes-to-wiki: ничего не исчезает молча. Проверка
механическая, потому что переписанный по памяти якорь выглядит правдоподобно.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave_ready import (
    TOMBSTONE_HEADING,
    accounting_gap,
    answer_details,
    unresolved_marker_gap,
)

BULLET = re.compile(r"^- .+$", re.M)
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],]+\.md)#L(\d+)")
LINE = re.compile(r"L(\d+)")


def flat_anchors(base: str, name: str) -> set[tuple[str, str]]:
    text = open(os.path.join(base, "flat", name), encoding="utf-8").read()
    return {(name, n) for b in BULLET.findall(text) for n in LINE.findall(b)}


# Слой тем уехал из `base/topics/` в отдельную папку рядом с корпусом
# (решение владельца 2026-08-24), а `flat/` и карта остались в мастерской.
# Пока адрес был один, проверка провенанса падала на отсутствующей папке.
TOPICS = "_ops/chat-recall/topics"


def check(
    base: str,
    topics_dir: str = TOPICS,
    runs_dir: str | None = None,
) -> list[str]:
    topics = json.load(open(os.path.join(base, "topics.json"), encoding="utf-8"))["topics"]
    problems: list[str] = []
    for topic in topics:
        want: set[tuple[str, str]] = set()
        for name in topic["files"]:
            want |= flat_anchors(base, name)
        path = os.path.join(topics_dir, topic["id"] + ".md")
        if not os.path.exists(path):
            problems.append(f"{topic['id']}: файла темы нет")
            continue
        text = open(path, encoding="utf-8").read()
        got = {m for b in BULLET.findall(text) for m in ANCHOR.findall(b)}
        if TOMBSTONE_HEADING.search(text):
            problems.append(
                f"{topic['id']}: reader-facing topic содержит запрещённый раздел ## Отменено"
            )

        accounting: dict[str, object] | None = None
        if runs_dir is not None:
            answer_path = os.path.join(runs_dir, topic["id"] + ".json")
            if not os.path.exists(answer_path):
                answer_path = os.path.join(runs_dir, topic["id"] + ".md")
            if not os.path.exists(answer_path):
                problems.append(f"{topic['id']}: нет run-receipt")
            else:
                body, accounting, why = answer_details(answer_path)
                if body is None:
                    problems.append(f"{topic['id']}: {why}")
                elif body.rstrip() != text.rstrip():
                    problems.append(
                        f"{topic['id']}: topic не совпадает с принятым response"
                    )

        gap = accounting_gap(accounting, want, got)
        if gap:
            problems.append(f"{topic['id']}: {gap}")
        gap = unresolved_marker_gap(text, accounting)
        if gap:
            problems.append(f"{topic['id']}: {gap}")
    return problems


if __name__ == "__main__":
    found = check(
        sys.argv[1],
        sys.argv[2] if len(sys.argv) > 2 else TOPICS,
        sys.argv[3] if len(sys.argv) > 3 else None,
    )
    for line in found:
        print(line)
    print(f"проблем: {len(found)}")
    sys.exit(1 if found else 0)
