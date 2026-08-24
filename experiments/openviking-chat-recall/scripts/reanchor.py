#!/usr/bin/env python3
"""Самоизлечение ссылок: адрес остаётся кликабельным, но перестаёт протухать.

Номер строки — единственная форма адреса, по которой ссылка открывается в
редакторе и на GitHub. И он же ломается, как только файл разговора дорастает
шапкой: все записи съезжают вниз, а ссылка тихо указывает на соседнюю. Правка
руками не помогает — через неделю то же самое.

Поэтому у ссылки два адреса: номер строки для человека и отпечаток записи для
машины. Отпечатком служит хеш самой строки записи — он не зависит ни от места
в файле, ни от соседей.

Первая версия брала за отпечаток timestamp записи, и это было неверно: 27%
записей корпуса делят timestamp с соседом, потому что владелец говорит
несколько тезисов в одну минуту. Проверка уникальности до применения стоила бы
одной команды; вместо неё 845 ссылок схлопнулись в первые попавшиеся строки и
были откачены git-ом.

    python3 reanchor.py map    — снять карту «якорь -> отпечаток» по живому корпусу
    python3 reanchor.py fix    — пересчитать номера строк по карте и живому корпусу
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys

CORPUS = "_ops/chat-recall/raw"
ART = "experiments/openviking-chat-recall/artifacts"
MAP = f"{ART}/anchor-map.json"
# Только живой слой. Пока сюда входил `wiki-v1`, починка якорей
# дописывала замороженное evidence снятой ветки.
ROOTS = ["_ops/chat-recall/topics"]

TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")


def fingerprint(line: str) -> str:
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()[:12]


def records() -> dict[str, dict[int, str]]:
    """Разговор -> {номер строки: отпечаток записи} по живому корпусу."""
    found: dict[str, dict[int, str]] = {}
    for path in sorted(glob.glob(f"{CORPUS}/*.md")):
        name = os.path.basename(path)
        if name == "README.md":
            continue
        rows: dict[int, str] = {}
        for number, line in enumerate(open(path, encoding="utf-8").read().splitlines(), start=1):
            if line.startswith("* ") and TYPE.search(line):
                rows[number] = fingerprint(line)
        found[name] = rows
    return found


def library_files() -> list[str]:
    return [p for root in ROOTS for p in glob.glob(os.path.join(root, "**", "*.md"), recursive=True)]


def build_map() -> int:
    live = records()
    mapped: dict[str, str] = {}
    missing: list[str] = []
    for path in library_files():
        for name, number in ANCHOR.findall(open(path, encoding="utf-8").read()):
            key = f"{name}#L{number}"
            mark = live.get(name, {}).get(int(number))
            if mark:
                mapped[key] = f"{name}@{mark}"
            elif key not in missing:
                missing.append(key)
    # Отпечаток обязан быть уникален внутри разговора, иначе пересчёт схлопнет
    # соседей. Проверяем до записи карты, а не после первой порчи.
    for name, rows in live.items():
        marks = list(rows.values())
        if len(marks) != len(set(marks)):
            print(f"ОТКАЗ: в {name} отпечатки не уникальны — карта не записана")
            return 1
    json.dump(mapped, open(MAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"якорей в карте: {len(mapped)} -> {MAP}")
    print(f"не попали ни в одну живую запись: {len(missing)}")
    for key in missing[:12]:
        print(f"  {key}")
    return 0


def fix() -> int:
    if not os.path.exists(MAP):
        print("карты нет — сначала `map`")
        return 1
    mapped = json.load(open(MAP, encoding="utf-8"))
    live = records()
    # отпечаток -> текущий номер строки; коллизия внутри файла означает, что
    # пересчёт неоднозначен, и тогда лучше не трогать ничего
    where: dict[str, int] = {}
    clash: set[str] = set()
    for name, rows in live.items():
        for number, mark in rows.items():
            key = f"{name}@{mark}"
            if key in where:
                clash.add(key)
            where[key] = number
    if clash:
        print(f"ОТКАЗ: неоднозначных отпечатков {len(clash)} — ничего не трогаю")
        return 1

    moved = lost = 0
    for path in library_files():
        text = open(path, encoding="utf-8").read()

        def swap(hit: re.Match) -> str:
            nonlocal moved, lost
            key = f"{hit.group(1)}#L{hit.group(2)}"
            mark = mapped.get(key)
            if not mark:
                return hit.group(0)
            number = where.get(mark)
            if number is None:
                lost += 1
                return hit.group(0)
            if number != int(hit.group(2)):
                moved += 1
            return f"{hit.group(1)}#L{number}"

        fresh = ANCHOR.sub(swap, text)
        if fresh != text:
            open(path, "w", encoding="utf-8").write(fresh)
    print(f"ссылок пересчитано: {moved} | запись по отпечатку не найдена: {lost}")
    return 0


if __name__ == "__main__":
    # Раньше любое слово, кроме `map`, запускало `fix()` — и он пишет. Вызов
    # `reanchor.py check`, сделанный ради проверки, молча переставил десять
    # якорей и уехал в чужой коммит. Незнакомый глагол теперь отказывает.
    command = sys.argv[1] if len(sys.argv) > 1 else "map"
    if command not in {"map", "fix"}:
        print(f"неизвестная команда {command!r}: только map (читает) или fix (пишет)", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(build_map() if command == "map" else fix())
