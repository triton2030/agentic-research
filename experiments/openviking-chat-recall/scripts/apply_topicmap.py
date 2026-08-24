#!/usr/bin/env python3
"""Стадия 2: раскладка карты тем и проверка, что она вообще карта.

Карта обязана быть разбиением: каждый файл ровно в одной теме, ни одного файла
мимо. Проверять это глазами бессмысленно — потерянный файл выглядит как файл,
которого просто не назвали.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict


def main(run_path: str, flat: str, out_path: str) -> int:
    payload = json.load(open(run_path, encoding="utf-8"))
    if not payload.get("ok"):
        print(f"прогон не принят: ok={payload.get('ok')}")
        return 1
    seen: dict[str, list[str]] = defaultdict(list)
    titles: dict[str, str] = {}
    twice: list[str] = []
    assigned: set[str] = set()
    for line in (payload.get("response") or "").splitlines():
        if line.count("\t") < 2:
            continue
        name, topic, title = [p.strip().strip("`") for p in line.split("\t", 2)]
        # Строка, чья первая колонка не имя файла, размещением не является:
        # ответ бывает с шапкой или обрывком темы сверху. Инвариант разбиения
        # это не ослабляет — он считается по живым файлам ниже.
        if not name.endswith(".md"):
            continue
        if name in assigned:
            twice.append(name)
            continue
        assigned.add(name)
        seen[topic].append(name)
        titles.setdefault(topic, title)

    on_disk = {f for f in os.listdir(flat) if f.endswith(".md")}
    missing = sorted(on_disk - assigned)
    unknown = sorted(assigned - on_disk)
    print(f"тем: {len(seen)} | файлов разложено: {len(assigned)} из {len(on_disk)}")
    if twice:
        print(f"названы дважды: {twice}")
    if missing:
        print(f"НЕ попали ни в одну тему: {len(missing)} — {missing[:10]}")
    if unknown:
        print(f"названы файлы, которых нет: {unknown[:10]}")
    if missing or unknown or twice:
        print("карта не является разбиением — не записываю")
        return 1
    json.dump({"topics": [{"id": t, "title": titles[t], "files": sorted(f)}
                          for t, f in sorted(seen.items())]},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"карта записана -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
