#!/usr/bin/env python3
"""Вписать переразмеченные темы в записи корпуса.

Меняется ровно поле `topic:` каждой записи и инвентарь `topics:` в шапке.
Всё остальное — текст цитаты, timestamp, type, context-note — охраняется
проверкой: файл с замаскированными значениями тем обязан совпасть до и после,
иначе прогон отвергается целиком.

Прогон принимается только при полном покрытии: каждая запись файла с полем
`topic` получила тему, каждая тема существует в каталоге слоя либо объявлена
новой в том же прогоне.

    python3 apply_retopic.py [--dry] [<папка прогонов>]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence
from build_retopic_tasks import META_START, TOPIC_FIELD, star_blocks, topic_of

ART = "experiments/openviking-chat-recall/artifacts"
CORPUS = "_ops/chat-recall/raw"
ROW = re.compile(r"^L(\d+):\s*`?([\w.\-/]+)`?\s*$", re.M)
NEW = re.compile(r"^новая-тема:\s*`?([\w.\-/]+)`?\s*(?:—|-)\s*(.+)$", re.M)
REPAIR_TOPIC = "без-темы"


def retopic_block(block: str, topic: str) -> str:
    meta = META_START.search(block)
    field = TOPIC_FIELD.search(block, meta.end())
    return block[: field.start()] + f"{field.group(1)}{topic}{field.group(3)}" + block[field.end():]


def masked(text: str) -> str:
    """Файл с вычеркнутыми значениями тем: инвариант всего остального."""
    body = TOPIC_FIELD.sub(r"\1@\3", text)
    lines = []
    in_topics = in_front = False
    for line in body.splitlines():
        if line.strip() == "---":
            in_front = not in_front
            in_topics = False
        if in_front and line.startswith("topics:"):
            in_topics = True
            continue
        if in_topics and line.startswith("  - "):
            continue
        in_topics = in_topics and line.startswith("  - ")
        lines.append(line)
    return "\n".join(lines)


def rewrite_inventory(lines: list[str], ordered_topics: list[str]) -> list[str]:
    end = lines[1:].index("---") + 1
    head = lines[: end + 1]
    keep: list[str] = []
    in_topics = False
    for line in head:
        if line.startswith("topics:"):
            in_topics = True
            continue
        if in_topics and line.startswith("  - "):
            continue
        in_topics = False
        keep.append(line)
    closing = len(keep) - 1
    inventory = ["topics:"] + [f"  - {t}" for t in ordered_topics]
    return keep[:closing] + inventory + keep[closing:] + lines[end + 1:]


def main(runs: str, dry: bool) -> int:
    known = {t["id"] for t in
             json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))["topics"]}
    done = refused = records = 0
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        name = os.path.basename(path)[:-5] + ".md"
        target = os.path.join(CORPUS, name)
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            print(f"  не читается: {name}")
            refused += 1
            continue
        body = strip_fence(payload.get("response") or "")
        mapping = {int(n): t for n, t in ROW.findall(body)}
        declared = {n for n, _ in NEW.findall(body)}
        if not payload.get("ok") or not mapping or not os.path.exists(target):
            print(f"  не принят: {name}")
            refused += 1
            continue
        text = open(target, encoding="utf-8").read()
        lines = text.splitlines()
        blocks = {n: block for n, block in star_blocks(lines) if topic_of(block)}
        expected = set(blocks)
        bad_topics = {t for t in mapping.values()
                      if t not in known and t not in declared and t != REPAIR_TOPIC}
        if set(mapping) != expected or bad_topics:
            missing = sorted(expected - set(mapping))
            alien = sorted(set(mapping) - expected)
            print(f"  отвергнут {name}: покрытие {len(mapping)}/{len(expected)}"
                  + (f", нет строк {missing[:3]}" if missing else "")
                  + (f", чужие строки {alien[:3]}" if alien else "")
                  + (f", неизвестные темы {sorted(bad_topics)[:3]}" if bad_topics else ""))
            refused += 1
            continue
        new_text = text
        for n in sorted(blocks, reverse=True):
            old_block = blocks[n]
            new_block = retopic_block(old_block, mapping[n])
            new_text = new_text.replace(old_block, new_block, 1)
        ordered: list[str] = []
        for n, block in star_blocks(new_text.splitlines()):
            t = topic_of(block)
            if t and t not in ordered:
                ordered.append(t)
        new_lines = rewrite_inventory(new_text.splitlines(), ordered)
        new_text = "\n".join(new_lines) + "\n"
        if masked(text) != masked(new_text):
            print(f"  отвергнут {name}: изменилось что-то кроме тем")
            refused += 1
            continue
        records += len(blocks)
        done += 1
        if not dry:
            open(target, "w", encoding="utf-8").write(new_text)
    verdict = "применено" if not dry else "применилось бы"
    print(f"{verdict}: файлов {done}, записей {records} | не принято: {refused}")
    return 0 if refused == 0 else 1


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-retopic/runs", "--dry" in sys.argv))
