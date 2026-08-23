#!/usr/bin/env python3
"""Скелет указателя: механика отдельно от суждения.

Пути, типы и принадлежность теме уже решены предыдущими стадиями — их незачем
угадывать модели. Скрипт собирает их из шапок страниц и выдаёт двухуровневый
скелет: тема как раздел, страницы внутри. Подсказки и слияние дублей остаются
модели, потому что это суждение, а не перенос.

Плоский список из трёхсот записей формально полон и практически бесполезен,
поэтому уровня именно два.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys

FIELD = {name: re.compile(rf'^{name}:\s*"?(.+?)"?\s*$', re.M) for name in ("type", "title", "description", "topic")}


def read_page(path: str, wiki_root: str) -> dict:
    text = open(path, encoding="utf-8").read()
    head = text.split("---", 2)[1] if text.startswith("---") else ""
    page = {name: (pattern.search(head).group(1).strip() if pattern.search(head) else "") for name, pattern in FIELD.items()}
    page["path"] = os.path.relpath(path, wiki_root)
    return page


def build(wiki_root: str, topics_path: str) -> dict:
    titles = {t["id"]: t["title"] for t in json.load(open(topics_path, encoding="utf-8"))["topics"]}
    pages = [read_page(p, wiki_root) for p in sorted(glob.glob(os.path.join(wiki_root, "**", "*.md"), recursive=True))
             if os.path.basename(p) != "index.md"]
    grouped: dict[str, list[dict]] = collections.defaultdict(list)
    for page in pages:
        grouped[page["topic"] or "без-темы"].append(page)
    sections = [
        {"topic": topic, "title": titles.get(topic, topic), "pages": sorted(items, key=lambda p: p["title"])}
        for topic, items in sorted(grouped.items(), key=lambda kv: -len(kv[1]))
    ]
    return {
        "page_count": len(pages),
        "section_count": len(sections),
        "types": dict(collections.Counter(p["type"] for p in pages)),
        "missing_title": [p["path"] for p in pages if not p["title"]],
        "missing_description": [p["path"] for p in pages if not p["description"]],
        "sections": sections,
    }


if __name__ == "__main__":
    result = build(sys.argv[1], sys.argv[2])
    json.dump(result, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"страниц {result['page_count']}, разделов {result['section_count']}, типы {result['types']}")
    for key in ("missing_title", "missing_description"):
        if result[key]:
            print(f"{key}: {len(result[key])}")
