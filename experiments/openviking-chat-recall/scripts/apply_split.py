#!/usr/bin/env python3
"""Раскладка структурных правок и немедленная сверка провенанса.

Правка состава — единственная, где пункт переезжает между файлами, поэтому
сверка стоит прямо здесь: множество якорей до и после обязано совпасть. Пункт,
потерявший при переезде свою ссылку, выглядит нормальным текстом.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

WIKI = "experiments/openviking-chat-recall/artifacts/wiki-v1"
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")
BLOCK = re.compile(r"^=== ФАЙЛ (\S+\.md)\s*$", re.M)


def anchors(text: str) -> set[tuple[str, str]]:
    return set(ANCHOR.findall(text))


def main(runs: str, dry: bool) -> int:
    done = skipped = refused = 0
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        name = os.path.basename(path)[:-5]
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            print(f"  {name}: нет JSON")
            continue
        if not payload.get("ok"):
            print(f"  {name}: прогон не принят")
            continue
        body = payload.get("response") or ""
        if "находка неверна" in body.split("\n", 1)[0]:
            print(f"  {name}: {body.split(chr(10), 1)[0].strip()}")
            skipped += 1
            continue
        parts = BLOCK.split(body)
        pages = list(zip(parts[1::2], parts[2::2]))
        if not pages:
            print(f"  {name}: в ответе нет блоков файлов")
            refused += 1
            continue
        was = set()
        for rel, _ in pages:
            target = os.path.join(WIKI, rel)
            if os.path.exists(target):
                was |= anchors(open(target, encoding="utf-8").read())
        now = set()
        for _, text in pages:
            now |= anchors(text)
        lost, fake = was - now, now - was
        if lost or fake:
            print(f"  {name}: провенанс не сходится — потеряно {len(lost)}, лишних {len(fake)}")
            refused += 1
            continue
        for rel, text in pages:
            target = os.path.join(WIKI, rel)
            if not dry:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                open(target, "w", encoding="utf-8").write(text.strip() + "\n")
        print(f"  {name}: страниц {len(pages)} ({', '.join(rel for rel, _ in pages)})")
        done += 1
    print(f"правок применено: {done} | находка отклонена агентом: {skipped} | отвергнуто: {refused}"
          + (" (сухой прогон)" if dry else ""))
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-split/runs", "--dry" in sys.argv))
