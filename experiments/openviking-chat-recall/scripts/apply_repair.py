#!/usr/bin/env python3
"""Применение правок аудита: точная замена или отказ, середины нет."""
from __future__ import annotations

import glob
import json
import os
import sys

WIKI = "experiments/openviking-chat-recall/artifacts/wiki-v1"
EMPTY = {"пусто", "", "—", "-"}


def main(runs: str, dry: bool) -> int:
    applied = refused = added = 0
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        topic = os.path.basename(path)[:-5]
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            print(f"  {topic}: нет JSON")
            continue
        if not payload.get("ok"):
            print(f"  {topic}: прогон не принят")
            continue
        for line in (payload.get("response") or "").splitlines():
            if line.count("\t") < 3:
                continue
            page, was, now, why = [p.strip() for p in line.split("\t", 3)]
            target = os.path.join(WIKI, page.strip("`"))
            if not os.path.exists(target):
                print(f"  {topic}: страницы нет — {page}")
                refused += 1
                continue
            text = open(target, encoding="utf-8").read()
            if was.strip() in EMPTY:
                fresh = text.replace("\n## Источники", f"\n- {now}\n\n## Источники", 1)
                if fresh == text:
                    print(f"  {topic} · {page}: некуда добавить пункт")
                    refused += 1
                    continue
                added += 1
            elif was in text:
                fresh = text.replace(was, "" if now.strip() in EMPTY else now, 1)
                applied += 1
            else:
                print(f"  {topic} · {page}: фрагмент не найден дословно — {was[:70]}")
                refused += 1
                continue
            if not dry:
                open(target, "w", encoding="utf-8").write(fresh)
    print(f"правок применено: {applied} | пунктов добавлено: {added} | отвергнуто: {refused}"
          + (" (сухой прогон)" if dry else ""))
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-repair/runs", "--dry" in sys.argv))
