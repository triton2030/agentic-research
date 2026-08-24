#!/usr/bin/env python3
"""Раскладка стадий 3 и 4 со сверкой баланса на месте.

Обе стадии однажды уронили записи молча — слияние в первой редакции, письмо
страниц в четвёртой. Инвариант 9 требует считать вход и выход в одних единицах,
и место для этого счёта здесь: пока результат ещё не смешался с соседними.

    python3 apply_stage.py merge <прогоны> <flat> <темы>
    python3 apply_stage.py pages <прогоны> <темы> <вики>
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import expand_corpus_links, strip_fence

SHORT = re.compile(r"L(\d+)")
FULL = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")
BLOCK = re.compile(r"^=== ФАЙЛ (\S+\.md)\s*$", re.M)


def flat_anchors(flat: str, names: list[str]) -> set[tuple[str, str]]:
    want: set[tuple[str, str]] = set()
    for name in names:
        path = os.path.join(flat, name)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        source = (re.search(r"^source:\s*(\S+)", text, re.M) or [None, name])[1]
        for line in text.splitlines():
            if line.startswith("- "):
                want |= {(source, n) for n in SHORT.findall(line)}
    return want


def main(stage: str, runs: str, material: str, out_dir: str, corpus: str) -> int:
    os.makedirs(out_dir, exist_ok=True)
    topics = None
    if stage == "merge":
        topics = {t["id"]: t["files"] for t in json.load(
            open(os.path.join(os.path.dirname(material.rstrip("/")), "topics.json"),
                 encoding="utf-8"))["topics"]}
    taken = refused = 0
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        topic = os.path.basename(path)[:-5]
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            print(f"  {topic}: нет JSON"); refused += 1; continue
        if not payload.get("ok"):
            print(f"  {topic}: прогон не принят"); refused += 1; continue
        body = strip_fence(payload.get("response") or "")

        if stage == "merge":
            if not body.startswith("---"):
                print(f"  {topic}: ответ не похож на файл темы"); refused += 1; continue
            want = flat_anchors(material, topics.get(topic, []))
            got = set(FULL.findall(body))
            lost, fake = want - got, got - want
            if lost or fake:
                print(f"  {topic}: якоря не сходятся — потеряно {len(lost)}, лишних {len(fake)}")
                refused += 1
                continue
            open(os.path.join(out_dir, topic + ".md"), "w", encoding="utf-8").write(body + "\n")
        else:
            source = os.path.join(material, topic + ".md")
            text = open(source, encoding="utf-8").read() if os.path.exists(source) else ""
            head = text.split("## Отменено", 1)[0]
            want = set(FULL.findall(head))
            parts = BLOCK.split(body)
            pages = list(zip(parts[1::2], parts[2::2]))
            if not pages:
                print(f"  {topic}: в ответе нет блоков страниц"); refused += 1; continue
            got: set[tuple[str, str]] = set()
            for _, page_text in pages:
                got |= set(FULL.findall(page_text))
            lost, fake = want - got, got - want
            if lost or fake:
                print(f"  {topic}: якоря не сходятся — потеряно {len(lost)}, лишних {len(fake)}")
                refused += 1
                continue
            for rel, page_text in pages:
                target = os.path.join(out_dir, rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                body = expand_corpus_links(strip_fence(page_text), target, corpus)
                open(target, "w", encoding="utf-8").write(body + "\n")
        taken += 1
    print(f"тем принято: {taken} | отвергнуто: {refused}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                          sys.argv[5] if len(sys.argv) > 5 else "_ops/chat-recall/raw"))
