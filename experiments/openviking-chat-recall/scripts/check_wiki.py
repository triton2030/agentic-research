#!/usr/bin/env python3
"""Механическая проверка вики: то немногое из старого валидатора, что реально ловило брак.

Судит форму, не смысл: ссылки, шапку, единственный H1, раздел источников и
достижимость каждой страницы из индекса ровно один раз.
"""
from __future__ import annotations

import glob
import os
import re
import sys

LINK = re.compile(r"\]\(([^)]+)\)")
H1 = re.compile(r"^# (.+)$", re.M)
TITLE = re.compile(r'^title:\s*"?(.+?)"?\s*$', re.M)


def check(wiki_root: str) -> list[str]:
    problems: list[str] = []
    pages = sorted(glob.glob(os.path.join(wiki_root, "**", "*.md"), recursive=True))
    index_path = os.path.join(wiki_root, "index.md")
    # Указатель собирается последним, а ссылки ломаются с первой же страницы.
    # Ранний выход отсюда отключал разом все проверки формы на всё время сборки:
    # 1693 битые ссылки прожили сорок прогонов именно так. Отсутствие индекса —
    # одна проблема из списка, а не причина ничего не проверять.
    has_index = index_path in pages
    if not has_index:
        problems.append(f"{wiki_root}: нет index.md")

    linked: list[str] = []
    for path in pages:
        rel = os.path.relpath(path, wiki_root)
        text = open(path, encoding="utf-8").read()
        is_index = rel == "index.md"

        if not text.startswith("---\n"):
            problems.append(f"{rel}: нет YAML-шапки")
        else:
            head = text.split("---", 2)[1]
            for field in ("type:", "title:", "description:"):
                if field not in head:
                    problems.append(f"{rel}: в шапке нет {field.rstrip(':')}")

        titles = TITLE.findall(text.split("---", 2)[1]) if "---" in text else []
        h1s = H1.findall(text)
        if len(h1s) != 1:
            problems.append(f"{rel}: заголовков первого уровня {len(h1s)}, нужен ровно один")
        elif titles and h1s[0].strip() != titles[0].strip():
            problems.append(f"{rel}: H1 не совпадает с title")

        # Заголовок считается строкой целиком: `## Источники для изучения` —
        # содержательный раздел страницы, а не второй раздел провенанса.
        sources = len(re.findall(r"^## Источники\s*$", text, re.M))
        if is_index and sources:
            problems.append("index.md: индекс не должен иметь раздел Источники")
        if not is_index and sources != 1:
            problems.append(f"{rel}: разделов Источники {sources}, нужен ровно один")

        for target in LINK.findall(text):
            target = target.split("#")[0]
            if target.startswith("http") or not target.endswith(".md"):
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(resolved):
                problems.append(f"{rel}: битая ссылка {target}")
            if is_index and "_ops/" not in target:
                linked.append(os.path.normpath(os.path.join(wiki_root, target)))

    for path in pages if has_index else []:
        if path == index_path:
            continue
        count = linked.count(os.path.normpath(path))
        if count != 1:
            rel = os.path.relpath(path, wiki_root)
            problems.append(f"{rel}: маршрутов из индекса {count}, нужен ровно один")
    return problems


if __name__ == "__main__":
    found = check(sys.argv[1])
    for line in found:
        print(line)
    print(f"страниц: {len(glob.glob(os.path.join(sys.argv[1], '**', '*.md'), recursive=True))}, проблем: {len(found)}")
    sys.exit(1 if found else 0)
