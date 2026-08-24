#!/usr/bin/env python3
"""Одноразовый ремонт якорей слоя после переразметки тем записей.

Отпечаток `reanchor.py` — хеш всей строки записи, а переразметка сменила в
строках значение `topic:`. Поэтому карта отпечатков ослепла разом на весь
корпус, и лечить её надо не по отпечаткам, а по содержанию: старая строка
берётся из git-блоба базового коммита (до применения переразметки), маскируется
её тема, и та же замаскированная строка ищется в живом файле. Совпадение по
n-му вхождению снимает коллизии одинаковых строк.

После этого скрипта обязателен `reanchor.py map`: он пересоберёт отпечатки от
живых строк и вылечит карту.

    python3 fix_anchors_after_retopic.py <базовый коммит> [--write]
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_retopic_tasks import TOPIC_FIELD, meta_at
from reanchor import ANCHOR, CORPUS, ROOTS, library_files


def masked(line: str) -> str:
    """Строка с вычеркнутой темой служебного хвоста, а не любой `topic:`.

    Глобальная замена вычеркнула бы и `topic:` внутри самой реплики, и тогда
    две разные записи выглядели бы одинаково — якорь встал бы на соседнюю.
    """
    line = line.strip()
    meta = meta_at(line)
    if meta is None:
        return line
    field = TOPIC_FIELD.search(line, meta)
    if not field:
        return line
    return line[: field.start()] + field.group(1) + "@" + field.group(3) + line[field.end():]


def blob(commit: str, path: str) -> list[str] | None:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"], capture_output=True, text=True
    )
    return proc.stdout.splitlines() if proc.returncode == 0 else None


def main(base: str, write: bool) -> int:
    remap: dict[tuple[str, int], int] = {}
    lost: list[str] = []
    names = {name for path in library_files()
             for name, _ in ANCHOR.findall(open(path, encoding="utf-8").read())}
    for name in sorted(names):
        old = blob(base, f"{CORPUS}/{name}")
        if old is None:
            continue  # файла не было в базе — его якорей не могло быть в слое
        new = open(f"{CORPUS}/{name}", encoding="utf-8").read().splitlines()
        positions: dict[str, list[int]] = defaultdict(list)
        for number, line in enumerate(new, 1):
            positions[masked(line)].append(number)
        seen: dict[str, int] = defaultdict(int)
        for number, line in enumerate(old, 1):
            key = masked(line)
            rank = seen[key]
            seen[key] += 1
            candidates = positions.get(key, [])
            if rank < len(candidates):
                remap[(name, number)] = candidates[rank]
            else:
                remap[(name, number)] = -1

    moved = kept = missing = 0
    for path in library_files():
        text = open(path, encoding="utf-8").read()

        def swap(hit: re.Match) -> str:
            nonlocal moved, kept, missing
            target = remap.get((hit.group(1), int(hit.group(2))))
            if target is None or target == -1:
                missing += 1
                lost.append(hit.group(0))
                return hit.group(0)
            if target == int(hit.group(2)):
                kept += 1
                return hit.group(0)
            moved += 1
            return f"{hit.group(1)}#L{target}"

        fresh = ANCHOR.sub(swap, text)
        if write and fresh != text:
            open(path, "w", encoding="utf-8").write(fresh)
    verb = "переставлено" if write else "переставилось бы"
    print(f"{verb}: {moved} | на месте: {kept} | не найдено: {missing}")
    for key in lost[:10]:
        print(f"  потерян: {key}")
    return 1 if missing else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--write"]
    if not args:
        print("нужен базовый коммит", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(args[0], "--write" in sys.argv))
