#!/usr/bin/env python3
"""Сдвинуть горизонт слоя тем: докуда он знает корпус.

Горизонт был ручным шагом в конце обновления, и ручные шаги в этой системе
стабильно забывают: слой, обещающий меньше, чем знает, безобиден, а слой,
знающий меньше обещанного, врёт читателю уверенно. Поэтому число считается
из тех же файлов, что и всё остальное, а не проставляется рукой.

    python3 set_horizon.py [--dry]
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
from datetime import date

CORPUS = "_ops/chat-recall/raw"
TOPICS = "_ops/chat-recall/topics"
HORIZON = f"{TOPICS}/horizon.json"
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
NOT_A_TOPIC = {"AGENTS.md", "README.md"}
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")


def main(dry: bool) -> int:
    records = conversations = 0
    for path in sorted(glob.glob(f"{CORPUS}/*.md")):
        if os.path.basename(path) == "README.md":
            continue
        conversations += 1
        records += sum(1 for line in open(path, encoding="utf-8")
                       if line.startswith("* ") and TYPE.search(line))

    covered: set[tuple[str, int]] = set()
    topics = 0
    for path in sorted(glob.glob(f"{TOPICS}/*.md")):
        if os.path.basename(path) in NOT_A_TOPIC:
            continue
        topics += 1
        covered |= {(n, int(i)) for n, i in ANCHOR.findall(open(path, encoding="utf-8").read())}

    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    horizon = {
        "commit": head,
        "date": date.today().isoformat(),
        "records": records,
        "conversations": conversations,
        "topics": topics,
        "anchors_in_layer": len(covered),
    }
    print(json.dumps(horizon, ensure_ascii=False, indent=1))
    if dry:
        return 0
    json.dump(horizon, open(HORIZON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"горизонт сдвинут -> {HORIZON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--dry" in sys.argv))
