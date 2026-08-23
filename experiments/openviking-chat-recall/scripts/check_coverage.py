#!/usr/bin/env python3
"""Провал П5 из ACCEPTANCE.md — исчерпывающе, а не выборкой, и с адресом потери.

«Молчаливая неполнота» задумывалась выборкой: берём случайные записи корпуса и
ищем их в библиотеке. Но у каждой записи есть точный адрес `файл.md#Lстрока`, а
каждая стадия конвейера носит эти же адреса. Значит отсутствие не оценивается,
а считается — и считается постадийно: разность множеств называет не только
сколько потеряно, но и где.

Корпус живёт дальше и после сборки, поэтому судить его состоянием на диске
нечестно вдвойне: появились новые разговоры, а старые доросли новыми строками.
Правду о том, что библиотека вообще видела, хранит git — снимок читается из
коммита сборки.

    python3 check_coverage.py [<коммит-снимка>]
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys
from collections import Counter

CORPUS = "_ops/chat-recall"
ART = "experiments/openviking-chat-recall/artifacts"

# Разделитель перед `type:` за год поменялся: ранние записи пишут `— type:`,
# поздние — `| type:`. Оба формата остаются живыми записями корпуса.
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
QUOTE = re.compile(r'—\s*"(.*?)"\s*—', re.S)
# Якорь одинаков во всех трёх записях: голый в темах, в ссылке на страницах.
ANCHOR = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")

Address = tuple[str, int]


def blob_at(rev: str, path: str) -> str | None:
    done = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def as_of_snapshot(name: str, rev: str) -> str:
    """Разговор в том виде, в каком его взяла сборка.

    Копия на диске взята из рабочего дерева, а часть разговоров попала в git
    позже неё — в том числе разговор, который сессия сборки писала про себя
    же. Для таких берём первый коммит, где файл появился: ближайшее к снимку
    зафиксированное состояние. Читать их сегодняшними — приписать библиотеке
    пропуск строк, которых на момент сборки не существовало.
    """
    text = blob_at(rev, f"{CORPUS}/{name}")
    if text is not None:
        return text
    added = subprocess.run(
        ["git", "log", "--format=%H", "--diff-filter=A", "--", f"{CORPUS}/{name}"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    if added:
        text = blob_at(added[-1], f"{CORPUS}/{name}")
        if text is not None:
            return text
    return open(os.path.join(CORPUS, name), encoding="utf-8").read()


def snapshot(rev: str) -> dict[Address, str]:
    """Записи корпуса на момент сборки: адрес -> строка целиком.

    Состав снимка задаёт не git, а сама сборка: имена файлов в `flat/`.
    """
    records: dict[Address, str] = {}
    for path in sorted(glob.glob(f"{ART}/flatten-v1/flat/*.md")):
        name = os.path.basename(path)
        for number, line in enumerate(as_of_snapshot(name, rev).splitlines(), start=1):
            if line.startswith("* ") and TYPE.search(line):
                records[(name, number)] = line.strip()
    return records


def flat_anchors() -> set[Address]:
    """Стадия 1 адресует строки числом `L20`, а файл называет в шапке."""
    found: set[Address] = set()
    for path in glob.glob(f"{ART}/flatten-v1/flat/*.md"):
        text = open(path, encoding="utf-8").read()
        head = re.search(r"^source:\s*(\S+)", text, re.M)
        source = head.group(1) if head else os.path.basename(path)
        for line in text.splitlines():
            if line.startswith("- "):
                found |= {(source, int(n)) for n in re.findall(r"L(\d+)", line)}
    return found


# Слой тем держит рядом свой контракт для агентов; пример якоря внутри него
# засчитался бы покрытой записью и молча выбросил её из дельты обновления.
NOT_A_TOPIC = {"AGENTS.md", "README.md"}


def anchors(pattern: str) -> set[Address]:
    found: set[Address] = set()
    for path in glob.glob(pattern, recursive=True):
        if os.path.basename(path) in NOT_A_TOPIC:
            continue
        text = open(path, encoding="utf-8").read()
        found |= {(name, int(n)) for name, n in ANCHOR.findall(text)}
    return found


def main(rev: str) -> int:
    records = snapshot(rev)
    known = set(records)
    # Конечный продукт — слой тем. Стадия страниц снята 2026-08-24, и пока она
    # стояла здесь последней, вердикт «ничего не потеряно» выносился по снятой
    # библиотеке: проверка честно судила продукт, которым никто не пользуется.
    stages = [
        ("1  снимок -> сжатые файлы", flat_anchors()),
        ("3  сжатые -> темы", anchors("_ops/chat-recall-topics/*.md")),
    ]

    print(f"снимок {rev}: {len(records)} записей корпуса\n")
    seen = known
    for label, reached in stages:
        print(f"стадия {label:28s} адресов {len(reached):5d}"
              f" | дошло {len(reached & known):5d} | потеряно {len(seen - reached):4d}")
        seen = reached & known

    library = stages[-1][1]  # слой тем
    # Запись без адреса в библиотеке бывает двух разных вещей, и мешать их
    # нельзя: пропущенная молча — дефект, а признанная не несущей знания —
    # результат работы. Весь смысл добора в том, чтобы вторых не оставалось
    # без имени, поэтому они считаются отдельно и в дефект не идут.
    declared: dict[Address, str] = {}
    decisions = f"{ART}/coverage-decisions.tsv"
    if os.path.exists(decisions):
        for row in open(decisions, encoding="utf-8"):
            anchor, verdict = row.split("\t", 2)[:2]
            name, _, number = anchor.rpartition("#L")
            if number.isdigit():
                declared[(name, int(number))] = verdict
    silent = sorted(a for a in known - library if declared.get(a) in (None, "без-решения"))
    named = sorted(a for a in known - library if declared.get(a) not in (None, "без-решения"))
    uncovered = silent
    dangling = sorted(library - known)
    accounted = len(records) - len(silent)
    print(f"\nстоит в слое тем: {len(known & library)} из {len(records)}"
          f" ({100 * len(known & library) / max(len(records), 1):.1f}%)")
    print(f"учтено — в теме либо названо: {accounted}"
          f" ({100 * accounted / max(len(records), 1):.1f}%)")
    print(f"НЕ покрыто молча (П5): {len(silent)}")
    print(f"названо не несущим знания (не дефект): {len(named)}")
    print(f"адрес слоя не указывает на запись снимка: {len(dangling)}")

    if uncovered:
        print("\nнепокрытые по типу записи:",
              dict(Counter(TYPE.search(records[a]).group(1) for a in uncovered).most_common()))
        gaps = f"{ART}/coverage-gaps.tsv"
        with open(gaps, "w", encoding="utf-8") as out:
            for name, number in uncovered:
                line = records[(name, number)]
                quote = QUOTE.search(line)
                out.write(f"{name}\t{number}\t{TYPE.search(line).group(1)}\t"
                          f"{(quote.group(1) if quote else line)}\n")
        print(f"все непокрытые адреса с цитатами -> {gaps}")
    if dangling:
        print("\nвисячие адреса слоя:")
        for name, number in dangling:
            print(f"  {name}#L{number}")

    # Горизонт библиотеки. Проверка выше судит только то, что сборка видела, —
    # иначе она наказывала бы за разговоры, которых на момент сборки не было.
    # Но у этой честности есть цена: провалиться на свежих записях она не может
    # по построению, а именно там и живёт опасность. Библиотека, ставшая
    # рекомендуемым маршрутом, всегда отстаёт от разговора, и отставание растёт
    # молча. Поэтому горизонт считается отдельным числом и печатается всегда.
    live: set[Address] = set()
    for path in sorted(glob.glob(f"{CORPUS}/*.md")):
        name = os.path.basename(path)
        if name == "README.md":
            continue
        for number, line in enumerate(open(path, encoding="utf-8").read().splitlines(), start=1):
            if line.startswith("* ") and TYPE.search(line):
                live.add((name, number))
    beyond = len(live) - len(records)
    print(f"\nгоризонт: сборка видела {len(records)} записей, в корпусе сейчас {len(live)}")
    print(f"новее сборки: {beyond} записей"
          f" ({100 * beyond / max(len(live), 1):.1f}%) — библиотека их не видела никогда")
    fresh = sorted({name for name, _ in live} - {name for name, _ in records})
    if fresh:
        print(f"разговоров целиком вне сборки: {len(fresh)}")
        for name in fresh[:10]:
            print(f"  {name}")
    return 1 if silent or dangling else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "dd1ff113"))
