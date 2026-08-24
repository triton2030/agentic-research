#!/usr/bin/env python3
"""Вливание новых фактов в существующие файлы тем.

Обновление отличается от сборки одним: файл темы уже проверен, и переписывать
его целиком нельзя. Новые пункты дописываются в конец своего файла, а решение
о схлопывании повтора и об отмене принимает отдельный прогон стадии слияния —
здесь только раскладка и счёт.

    python3 apply_update.py [--dry] [<папка прогонов>]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence
from build_retopic_tasks import star_blocks, topic_of

ART = "experiments/openviking-chat-recall/artifacts"
TOPICS = "_ops/chat-recall/topics"
CORPUS = "_ops/chat-recall/raw"
SHORT = re.compile(r"L(\d+)")


def record_topics(name: str) -> dict[int, str]:
    """Тема каждой записи разговора: с переразметки она позаписная.

    Карта тем размещает разговор целиком, и до 2026-08-24 этого хватало. После
    переразметки 93 разговора из 213 несут по нескольку тем, и holder-маршрут
    отправлял бы новый пункт в тему соседней реплики.
    """
    path = os.path.join(CORPUS, name)
    if not os.path.exists(path):
        return {}
    lines = open(path, encoding="utf-8").read().splitlines()
    found: dict[int, str] = {}
    for number, block in star_blocks(lines):
        topic = topic_of(block)
        if topic:
            found[number] = topic
    return found


def main(runs: str, dry: bool) -> int:
    delta = json.load(open(f"{ART}/update-delta.json", encoding="utf-8"))
    holder_of = {f: t["id"] for t in json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))["topics"]
                 for f in t["files"]}
    fresh: dict[str, list[str]] = defaultdict(list)
    taken = refused = orphan = 0
    covered: set[tuple[str, int]] = set()

    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        name = os.path.basename(path)[:-5] + ".md"
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            refused += 1
            continue
        body = strip_fence(payload.get("response") or "")
        if not payload.get("ok") or not body.startswith("---"):
            print(f"  не принят: {name}")
            refused += 1
            continue
        holder_topic = holder_of.get(name)
        by_record = record_topics(name)
        if holder_topic is None and not by_record:
            orphan += 1
            print(f"  разговор без темы, ждёт назначения: {name}")
            continue
        for line in body.splitlines():
            if line.startswith("- "):
                anchors = SHORT.findall(line)
                if not anchors:
                    continue
                # Пункт живёт в теме своей записи; тема разговора — только
                # запасной маршрут для корпуса, который ещё не переразмечен.
                topic = by_record.get(int(anchors[0])) or holder_topic
                if topic is None:
                    orphan += 1
                    continue
                full = ", ".join(f"[{name}#L{n}]" for n in anchors)
                text = re.sub(r"\s*\[L[^\]]*\]\s*$", "", line[2:]).strip()
                fresh[topic].append(f"- {text} {full}")
                covered |= {(name, int(n)) for n in anchors}
        taken += 1

    want = {(n, i) for n, rows in delta.items() for i in rows}
    print(f"прогонов принято: {taken} | не принято: {refused} | без темы: {orphan}")
    print(f"записей дельты: {len(want)} | покрыто новыми пунктами: {len(want & covered)}")
    print(f"тем затронуто: {len(fresh)} | новых пунктов: {sum(len(v) for v in fresh.values())}")
    if dry:
        return 0
    for topic, rows in sorted(fresh.items()):
        path = os.path.join(TOPICS, topic + ".md")
        if not os.path.exists(path):
            print(f"  файла темы нет: {topic}")
            continue
        text = open(path, encoding="utf-8").read().rstrip("\n")
        head, sep, tail = text.partition("\n## Отменено")
        block = "\n\n## Добавлено 2026-08-24\n\n" + "\n".join(rows) + "\n"
        open(path, "w", encoding="utf-8").write(head.rstrip() + block + sep + tail + "\n")
    print(f"влито в {len(fresh)} файлов тем")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-update/runs", "--dry" in sys.argv))
