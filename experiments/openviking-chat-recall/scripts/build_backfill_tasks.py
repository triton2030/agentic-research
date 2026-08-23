#!/usr/bin/env python3
"""Брифы добора: одна тема — один агент, свои записи и свои страницы.

Агенту даётся ровно то, что нужно для трёх решений, и ничего сверх: пропущенные
записи его темы дословно и список уже написанных страниц. Ни корпуса целиком,
ни чужих тем — лишний вход здесь не безобиден, он приглашает переписать то,
что уже проверено.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import skip_done
from collections import defaultdict

ART = "experiments/openviking-chat-recall/artifacts"
CONTRACT = "experiments/openviking-chat-recall/prompts/backfill-missed.v1.md"
PAGE = re.compile(r"^- `([^`]+)` \[(\w+)\] \*\*(.+?)\*\* — (.*)$")


def pages_by_topic(catalog: str) -> dict[str, list[tuple[str, str, str, str]]]:
    found: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    topic = None
    for line in open(catalog, encoding="utf-8"):
        head = re.match(r"^## (\S+) — ", line)
        if head:
            topic = head.group(1)
            continue
        row = PAGE.match(line.rstrip("\n"))
        if row and topic:
            found[topic].append(row.groups())
    return found


def main(out_dir: str, runs_dir: str | None, redo: bool) -> int:
    topics = json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))["topics"]
    topic_of = {name: t["id"] for t in topics for name in t["files"]}
    title_of = {t["id"]: t["title"] for t in topics}
    pages = pages_by_topic(f"{ART}/wiki-v1-catalog.md")
    contract = open(CONTRACT, encoding="utf-8").read()

    gaps: dict[str, list[list[str]]] = defaultdict(list)
    for row in open(f"{ART}/coverage-gaps.tsv", encoding="utf-8"):
        name, line, kind, quote = row.rstrip("\n").split("\t", 3)
        gaps[topic_of[name]].append([f"{name}#L{line}", kind, quote])

    os.makedirs(out_dir, exist_ok=True)
    keep = set(skip_done(sorted(gaps), runs_dir, redo))
    for topic, records in sorted((k, v) for k, v in gaps.items() if k in keep):
        listing = "\n".join(
            f"- `{path}` [{kind}] **{title}** — {desc}" for path, kind, title, desc in pages.get(topic, [])
        ) or "(в этой теме страниц ещё нет — все записи получат судьбу `new` или `skip`)"
        missed = "\n\n".join(
            f"{i}. якорь `{anchor}`\n   type: `{kind}`\n   цитата: «{quote}»"
            for i, (anchor, kind, quote) in enumerate(records, start=1)
        )
        brief = f"""Роль: редактор библиотеки знаний. Тема «{topic} — {title_of.get(topic, topic)}».

Библиотека лежит в {ART}/wiki-v1/. Ниже — контракт работы, затем страницы этой
темы, затем записи корпуса, которые до библиотеки не дошли.

Ты можешь открывать страницы этой темы, чтобы понять, что на них уже сказано.
Ничего не правь: ответ — только TSV.

{contract}

## Страницы этой темы ({len(pages.get(topic, []))})

{listing}

## Записи, не дошедшие до библиотеки ({len(records)})

{missed}

## Ответ

Верни ровно {len(records)} строк TSV и ничего больше.
"""
        open(os.path.join(out_dir, f"{topic}.txt"), "w", encoding="utf-8").write(brief)
    total = sum(len(v) for v in gaps.values())
    print(f"брифов: {len(gaps)} | записей: {total} | -> {out_dir}")
    return 0


if __name__ == "__main__":
    plain = [a for a in sys.argv[1:] if not a.startswith("--")]
    raise SystemExit(main(plain[0] if plain else "_workspace/ox-backfill/tasks",
                          plain[1] if len(plain) > 1 else None,
                          "--redo" in sys.argv))
