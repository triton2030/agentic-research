#!/usr/bin/env python3
"""Провенанс слияния: у каждого якоря входа ровно одна судьба.

Якорь либо стоит при пункте, либо назван отменённым в разделе `## Отменено`.
Якорь, которого нет во входе, — выдуманная ссылка.

Инвариант 6 протокола quotes-to-wiki: ничего не исчезает молча. Проверка
механическая, потому что переписанный по памяти якорь выглядит правдоподобно.
"""
from __future__ import annotations

import json
import os
import re
import sys

BULLET = re.compile(r"^- .+$", re.M)
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],]+\.md)#L(\d+)")
LINE = re.compile(r"L(\d+)")


def flat_anchors(base: str, name: str) -> set[tuple[str, str]]:
    text = open(os.path.join(base, "flat", name), encoding="utf-8").read()
    return {(name, n) for b in BULLET.findall(text) for n in LINE.findall(b)}


def check(base: str) -> list[str]:
    topics = json.load(open(os.path.join(base, "topics.json"), encoding="utf-8"))["topics"]
    problems: list[str] = []
    for topic in topics:
        want: set[tuple[str, str]] = set()
        for name in topic["files"]:
            want |= flat_anchors(base, name)
        path = os.path.join(base, "topics", topic["id"] + ".md")
        if not os.path.exists(path):
            problems.append(f"{topic['id']}: файла темы нет")
            continue
        text = open(path, encoding="utf-8").read()
        got = {m for b in BULLET.findall(text) for m in ANCHOR.findall(b)}
        superseded = set()
        if "## Отменено" in text:
            tail = text.split("## Отменено", 1)[1]
            superseded = set(ANCHOR.findall(tail))
        lost, fake = want - got - superseded, (got | superseded) - want
        if lost:
            problems.append(f"{topic['id']}: потеряно якорей {len(lost)} из {len(want)}")
        if fake:
            problems.append(f"{topic['id']}: якорей нет в источнике {len(fake)}")
    return problems


if __name__ == "__main__":
    found = check(sys.argv[1])
    for line in found:
        print(line)
    print(f"проблем: {len(found)}")
    sys.exit(1 if found else 0)
