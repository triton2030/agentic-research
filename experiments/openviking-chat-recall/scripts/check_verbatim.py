#!/usr/bin/env python3
"""Дословность переноса: пункт без схлопывания обязан совпасть с материалом.

Якорный гейт сторожит происхождение, но молчит о тексте. Замер 2026-08-25:
тема `planning`, принятая по якорям, несла дописанное «Владелец решил:» там,
где в источнике этого нет, слитые в один пункт разные модальности и молча
исправленную опечатку в словах владельца. Три дефекта, ноль сигналов.

Пункт с одним якорем схлопыванию не подвергался, значит контракт требует от
него дословности — это и проверяется. Пункт с несколькими якорями пропускается:
там слияние законно, и судить его может только человек.

    python3 check_verbatim.py <flat> <тема> <файл>
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave_ready import FULL, read_flat, topic_files

ANCHOR = re.compile(r"\[[^\]]*#?L\d+[^\]]*\]")
SHOW = 40


def material_items(flat: str, names: list[str]) -> dict[tuple[str, str], list[str]]:
    """(источник, строка) -> тексты пунктов материала. Список, а не строка.

    Одна запись разговора даёт несколько сухих пунктов, и все они несут один
    якорь. Первая редакция этой пробы держала по одному тексту на якорь и
    объявила дрейфом каждое второе такое место — десять процентов ложной
    тревоги на всех темах сразу, включая заведомо честные.
    """
    items: dict[tuple[str, str], list[str]] = {}
    for name in names:
        text = read_flat(flat, name)
        if not text:
            continue
        source = (re.search(r"^source:\s*(\S+)", text, re.M) or [None, name])[1]
        current: list[str] = []
        for line in text.splitlines() + ["- "]:
            if line.startswith("- "):
                if current:
                    body = " ".join(current)
                    for num in re.findall(r"\[L(\d+)\]", body):
                        items.setdefault((source, num), []).append(normal(body))
                current = [line[2:]]
            elif current and line.strip() and not line.startswith("#"):
                current.append(line.strip())
            elif current:
                body = " ".join(current)
                for num in re.findall(r"\[L(\d+)\]", body):
                    items.setdefault((source, num), []).append(normal(body))
                current = []
    return items


def normal(text: str) -> str:
    return re.sub(r"\s+", " ", ANCHOR.sub("", text)).strip(" .;·—-").strip()


def theme_items(path: str) -> list[tuple[list[tuple[str, str]], str]]:
    out: list[tuple[list[tuple[str, str]], str]] = []
    current: list[str] = []
    for line in open(path, encoding="utf-8").read().splitlines() + ["- "]:
        if line.startswith("- "):
            if current:
                body = " ".join(current)
                out.append((FULL.findall(body), normal(body)))
            current = [line[2:]]
        elif current and line.strip() and not line.startswith("#"):
            current.append(line.strip())
        elif current:
            body = " ".join(current)
            out.append((FULL.findall(body), normal(body)))
            current = []
    return out


def main(flat: str, theme: str, path: str) -> int:
    names = topic_files(flat).get(theme)
    if names is None:
        print(f"темы {theme} нет в карте тем")
        return 2
    source_items = material_items(flat, names)
    same = collapsed = missing = 0
    drift: list[tuple[str, str, str]] = []
    for anchors, text in theme_items(path):
        if len(anchors) != 1:
            collapsed += 1
            continue
        key = anchors[0]
        origins = source_items.get(key)
        if not origins:
            missing += 1
            continue
        if text in origins:
            same += 1
        elif all(o in text for o in origins):
            # Одна запись разговора дала несколько сухих пунктов; тема схлопнула
            # их в один, и якорь у неё честно один. Это законное слияние, а не
            # дрейф: весь текст источников присутствует целиком.
            collapsed += 1
        else:
            closest = max(origins, key=lambda o: len(os.path.commonprefix([o, text])))
            drift.append((f"{key[0]}#L{key[1]}", closest, text))
    total = same + len(drift)
    print(f"{theme}: дословных {same} из {total} одиночных · схлопнутых {collapsed}"
          + (f" · без пары в материале {missing}" if missing else ""))
    for anchor, origin, text in drift[:SHOW]:
        # Расхождение чаще всего в хвосте — оговорка отброшена или дописана, —
        # а окно вокруг первого несовпадающего символа показывает тогда два
        # одинаковых начала и ничего не объясняет.
        head = next((i for i, (a, b) in enumerate(zip(origin, text)) if a != b), min(len(origin), len(text)))
        print(f"  {anchor} · материал {len(origin)} симв, в теме {len(text)}")
        print(f"    материал: …{origin[max(0, head - 15):head + 90]}")
        print(f"    в теме  : …{text[max(0, head - 15):head + 90]}")
    if len(drift) > SHOW:
        print(f"  … и ещё {len(drift) - SHOW} расхождений")
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
