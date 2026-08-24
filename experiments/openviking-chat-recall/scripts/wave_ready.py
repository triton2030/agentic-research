#!/usr/bin/env python3
"""Готовность волны и язык её ответов — один предикат на всех потребителей.

Два бортика, оба куплены ошибками 2026-08-24:

1. **Готовность — предикат, а не файловая система.** Пустая квитанция прогона
   весит те же ~1769 байт, что и короткий честный ответ, поэтому `ls | wc -l`
   и `wc -c` врут одинаково правдоподобно. За одну сессию счёт собранных тем
   был объявлен владельцу неверно дважды.
2. **Язык вывода обязан совпадать с языком материала.** Тема `html-artifacts`
   пришла целиком по-английски при русском корпусе, прошла приёмку по `ok` и
   якорям и была поймана случайно. Гейт сравнивает долю кириллицы в ответе с
   долей в его же материале: порог не абсолютный, потому что корпус может быть
   любым, а вот расхождение с собственным материалом — всегда дефект.

    python3 wave_ready.py <папка заданий> <папка ответов> [<ещё папка>...]

Папок ответов может быть несколько, и это не удобство: принятое переносится в
`good/`, а `runs/` — проходящая, её файл затирается следующей попыткой той же
темы. Счёт по одной папке занижает результат ровно так же уверенно, как счёт
по размеру файла его завышал.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence

CYR = re.compile(r"[а-яА-ЯёЁ]")
LAT = re.compile(r"[A-Za-z]")
SHORT = re.compile(r"L(\d+)")
FULL = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")

MIN_RESPONSE = 500
LANGUAGE_FLOOR = 0.5

_material: dict[str, str] = {}


def read_flat(flat: str, name: str) -> str:
    path = os.path.join(flat, name)
    if path not in _material:
        _material[path] = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    return _material[path]


def topic_files(flat: str) -> dict[str, list[str]]:
    """Карта тема -> её сжатые файлы; лежит рядом с папкой flat."""
    path = os.path.join(os.path.dirname(flat.rstrip("/")), "topics.json")
    return {t["id"]: t["files"] for t in json.load(open(path, encoding="utf-8"))["topics"]}


def flat_anchors(flat: str, names: list[str]) -> set[tuple[str, str]]:
    """Якоря, которые обязаны доехать: короткие `[L21]` плюс имя из поля source."""
    want: set[tuple[str, str]] = set()
    for name in names:
        text = read_flat(flat, name)
        if not text:
            continue
        source = (re.search(r"^source:\s*(\S+)", text, re.M) or [None, name])[1]
        for line in text.splitlines():
            if line.startswith("- "):
                want |= {(source, n) for n in SHORT.findall(line)}
    return want


def flat_text(flat: str, names: list[str]) -> str:
    return "\n".join(read_flat(flat, n) for n in names)


def theme_gap(body: str, flat: str, names: list[str]) -> str | None:
    """Единственный владелец слова «готова» для темы: форма, язык, происхождение.

    Раздельные проверки уже дважды разошлись между собой: доска считала тему
    готовой по непустому ответу, а раскладка отвергала её по якорям — счёт
    владельцу назывался на четыре темы больше настоящего.
    """
    if not body.startswith("---"):
        return "ответ не похож на файл темы"
    gap = language_gap(body, flat_text(flat, names))
    if gap:
        return gap
    want, got = flat_anchors(flat, names), set(FULL.findall(body))
    lost, fake = want - got, got - want
    if lost or fake:
        return f"якоря не сходятся — потеряно {len(lost)}, лишних {len(fake)}"
    return None


def cyr_share(text: str) -> float:
    """Доля кириллицы среди букв: 1.0 — чистый русский, 0.0 — чистая латиница."""
    cyr, lat = len(CYR.findall(text)), len(LAT.findall(text))
    return cyr / (cyr + lat) if cyr + lat else 0.0


def language_gap(body: str, material: str) -> str | None:
    """Причина отказа по языку либо None. Нерусский материал гейт не судит."""
    want = cyr_share(material)
    if want < LANGUAGE_FLOOR:
        return None
    got = cyr_share(body)
    if got < want * LANGUAGE_FLOOR:
        return (f"язык разошёлся с материалом: кириллицы {got:.0%} в ответе "
                f"против {want:.0%} в материале")
    return None


def run_verdict(path: str) -> tuple[dict | None, str]:
    """Принят ли прогон. Первый элемент — payload, второй — причина отказа."""
    try:
        payload = json.load(open(path, encoding="utf-8"))
    except Exception as error:
        return None, f"нет JSON ({error.__class__.__name__})"
    if not payload.get("ok"):
        return None, "прогон не принят обёрткой"
    body = payload.get("response") or ""
    if len(body) < MIN_RESPONSE:
        return None, f"ответ пуст или короток ({len(body)} симв)"
    return payload, ""


def survey(tasks: str, answers: tuple[str, ...], flat: str | None
           ) -> tuple[list[str], dict[str, str], dict[str, str]]:
    """Что заказано, что готово и почему остальное — нет. Одна правда на всех."""
    wanted = sorted(os.path.basename(p)[:-4]
                    for p in glob.glob(os.path.join(tasks, "*.txt")))
    files = topic_files(flat) if flat else {}
    ready: dict[str, str] = {}
    refused: dict[str, str] = {}
    for folder in answers:
        for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
            name = os.path.basename(path)[:-5]
            payload, why = run_verdict(path)
            if payload is None:
                refused.setdefault(name, why)
                continue
            body = strip_fence(payload["response"])
            gap = theme_gap(body, flat, files.get(name, [])) if flat else None
            if gap:
                refused[name] = gap
                continue
            refused.pop(name, None)
            ready[name] = f"{len(body) // 1000}к · {cyr_share(body):.0%} рус"
    return wanted, ready, refused


def main(tasks: str, *rest: str) -> int:
    answers = tuple(a for a in rest if not a.startswith("--"))
    flat = next((a.split("=", 1)[1] for a in rest if a.startswith("--flat=")), None)
    wanted, ready, refused = survey(tasks, answers, flat)
    for name in wanted:
        if name in ready:
            print(f"  {name}: готов · {ready[name]}")
        else:
            print(f"  {name}: {refused.get(name, 'ответа нет')}")
    print(f"готово: {len(set(wanted) & set(ready))} из {len(wanted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
