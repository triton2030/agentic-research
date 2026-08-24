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

CYR = re.compile(r"[а-яА-ЯёЁ]")
LAT = re.compile(r"[A-Za-z]")

MIN_RESPONSE = 500
LANGUAGE_FLOOR = 0.5


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


def main(tasks: str, *answers: str) -> int:
    wanted = sorted(os.path.basename(p)[:-4]
                    for p in glob.glob(os.path.join(tasks, "*.txt")))
    ready: dict[str, str] = {}
    refused: dict[str, str] = {}
    for folder in answers:
        for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
            name = os.path.basename(path)[:-5]
            payload, why = run_verdict(path)
            if payload is None:
                refused.setdefault(name, why)
                continue
            body = payload["response"]
            ready[name] = f"{len(body)} симв · кириллицы {cyr_share(body):.0%}"
    for name in wanted:
        if name in ready:
            print(f"  {name}: готов · {ready[name]}")
        else:
            print(f"  {name}: {refused.get(name, 'ответа нет')}")
    print(f"готово: {len(set(wanted) & set(ready))} из {len(wanted)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
