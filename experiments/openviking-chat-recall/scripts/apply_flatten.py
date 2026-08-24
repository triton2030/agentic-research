#!/usr/bin/env python3
"""Раскладка результатов стадии 1 по файлам и немедленная сверка баланса.

Инвариант 9: вход и выход стадии считаются в одних единицах. Проверка стоит
здесь, а не в конце сборки, потому что здесь она ещё дёшева — в первый раз эта
стадия молча уронила 90 записей из 1207, и узналось это через сутки.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence

TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")


def main(runs: str, corpus: str, out_dir: str) -> int:
    os.makedirs(out_dir, exist_ok=True)
    kept = dropped = refused = 0
    report = []
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        name = os.path.basename(path)[:-5] + ".md"
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            refused += 1
            continue
        # Забор ```…``` вокруг ответа снимают все остальные применялки; здесь
        # его отсутствие стоило двух честных прогонов из 170.
        body = strip_fence(payload.get("response") or "").strip()
        if not payload.get("ok") or not body.startswith("---"):
            report.append(f"  не принят: {name} (ok={payload.get('ok')})")
            refused += 1
            continue
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write(body + "\n")
        source = os.path.join(corpus, name)
        records = {i for i, line in enumerate(open(source, encoding="utf-8"), start=1)
                   if line.startswith("* ") and TYPE.search(line)}
        anchored = {int(n) for line in body.splitlines() if line.startswith("- ")
                    for n in re.findall(r"L(\d+)", line)}
        kept += len(records & anchored)
        lost = records - anchored
        dropped += len(lost)
        if lost:
            report.append(f"  {name}: не перенесено {len(lost)} из {len(records)}"
                          f" — строки {sorted(lost)}")
    print(f"файлов принято: {len(glob.glob(os.path.join(out_dir, '*.md')))}"
          f" | не принято прогонов: {refused}")
    print(f"записей перенесено: {kept} | уронено: {dropped}")
    for line in report[:20]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
