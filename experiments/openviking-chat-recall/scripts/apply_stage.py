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
from wave_ready import FULL, answers_in, flat_anchors, read_answer, theme_gap, topic_files

BLOCK = re.compile(r"^=== ФАЙЛ (\S+\.md)\s*$", re.M)


def main(stage: str, runs: str, material: str, out_dir: str, corpus: str) -> int:
    os.makedirs(out_dir, exist_ok=True)
    topics = topic_files(material) if stage == "merge" else None
    taken = refused = 0
    for path in answers_in(runs):
        topic = os.path.splitext(os.path.basename(path))[0]
        body, why = read_answer(path)
        if body is None:
            print(f"  {topic}: {why}"); refused += 1; continue

        if stage == "merge":
            gap = theme_gap(body, material, topics.get(topic, []))
            if gap:
                print(f"  {topic}: {gap}"); refused += 1; continue
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
