#!/usr/bin/env python3
"""Сверяет цитаты карты с источниками.

Цитата в карте: `путь/от/корня:строка` «дословный текст».
Пропуск внутри цитаты обозначается «…»; вложенные кавычки — „“.
Сравнение терпит переносы строк, регистр, разметку Markdown,
виды кавычек и тире, букву ё.
Строка со словом «записано» без цитаты в этом формате получает «без цитаты»;
цитата короче MIN_QUOTE знаков — «коротко»: такую нельзя проверить.
Код выхода: 0 — все цитаты найдены; 1 — есть любой другой статус, кроме
«другая строка»; 2 — в карте нет ни одной цитаты в этом формате.
"""

import argparse
import re
import sys
from pathlib import Path

CITE = re.compile(r"`([^`\n]+?):(\d+)(?:[-–]\d+)?`[^«\n]{0,12}«([^»\n]+)»")
OMISSION = re.compile(r"…|\.\.\.")
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
WIKI = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")
FOOTNOTE_REF = re.compile(r"\[\^[^\]]+\]")
BLOCKQUOTE = re.compile(r"^\s*(?:>\s*)+")
DROP = set("*_`«»“”„\"'’‘")
DASHES = set("—–‑‒−")
NEAR = 3  # строк допуска вокруг указанной
SPAN = 3000  # предел расстояния между частями цитаты с «…»
MIN_QUOTE = 12  # знаков после нормализации
RECORDED = re.compile(r"записано", re.IGNORECASE)


def norm_char(ch):
    if ch in DROP:
        return ""
    if ch.isspace():
        return " "
    if ch in DASHES:
        return "-"
    return ch.casefold().replace("ё", "е")


def normalize(lines):
    """Нормализованный текст и номер исходной строки для каждого его знака."""
    chars, owners = [], []
    for number, raw in enumerate(lines, 1):
        line = BLOCKQUOTE.sub(
            "", LINK.sub(r"\1", WIKI.sub(r"\1", FOOTNOTE_REF.sub("", raw)))
        )
        for ch in line + "\n":
            for c in norm_char(ch):
                if c == " " and (not chars or chars[-1] == " "):
                    continue
                chars.append(c)
                owners.append(number)
    return "".join(chars), owners


def find(text, owners, fragments, cited):
    """Лучшее вхождение всех частей цитаты по порядку: (расстояние до строки, строка)."""
    best = None
    start = text.find(fragments[0])
    while start != -1:
        end = start + len(fragments[0])
        for fragment in fragments[1:]:
            j = text.find(fragment, end)
            if j == -1 or j - end > SPAN:
                break
            end = j + len(fragment)
        else:
            first, last = owners[start], owners[end - 1]
            if first - NEAR <= cited <= last + NEAR:
                distance = 0
            else:
                distance = min(abs(cited - first), abs(cited - last))
            if best is None or distance < best[0]:
                best = (distance, first)
        start = text.find(fragments[0], start + 1)
    return best


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("map", help="файл карты")
    parser.add_argument(
        "--root", required=True, help="корень проекта, от которого считаются пути"
    )
    args = parser.parse_args()

    root = Path(args.root)
    source = Path(args.map).read_text(encoding="utf-8")
    cache = {}
    counts = {
        "ок": 0,
        "другая строка": 0,
        "не найдено": 0,
        "нет файла": 0,
        "коротко": 0,
        "без цитаты": 0,
    }
    cited_lines = set()

    for match in CITE.finditer(source):
        raw_path, cited, quote = (
            match.group(1).strip(),
            int(match.group(2)),
            match.group(3),
        )
        map_line = source.count("\n", 0, match.start()) + 1
        cited_lines.add(map_line)
        path = Path(raw_path) if Path(raw_path).is_absolute() else root / raw_path
        fragments = [normalize([part])[0].strip() for part in OMISSION.split(quote)]
        fragments = [f for f in fragments if f]

        if not path.is_file():
            status, key = "нет файла", "нет файла"
        elif sum(len(f) for f in fragments) < MIN_QUOTE:
            status, key = "коротко", "коротко"
        else:
            if path not in cache:
                cache[path] = normalize(
                    path.read_text(encoding="utf-8", errors="replace").splitlines()
                )
            hit = find(*cache[path], fragments, cited)
            if hit is None:
                status, key = "не найдено", "не найдено"
            elif hit[0] == 0:
                status, key = "ок", "ок"
            else:
                status, key = f"другая строка: {hit[1]}", "другая строка"
        counts[key] += 1
        short = quote if len(quote) <= 70 else quote[:67] + "..."
        print(f"{status}\tкарта:{map_line}\t{raw_path}:{cited}\t«{short}»")

    for number, line in enumerate(source.splitlines(), 1):
        if RECORDED.search(line) and number not in cited_lines:
            counts["без цитаты"] += 1
            short = (
                line.strip() if len(line.strip()) <= 70 else line.strip()[:67] + "..."
            )
            print(f"без цитаты\tкарта:{number}\t\t{short}")

    total = sum(counts.values())
    if total == 0:
        print("В карте нет цитат в формате `путь:строка` «текст».")
        sys.exit(2)
    print(
        "Итого: "
        + "; ".join(f"{k} — {v}" for k, v in counts.items())
        + f"; всего — {total}"
    )
    failed = sum(v for k, v in counts.items() if k not in ("ок", "другая строка"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
