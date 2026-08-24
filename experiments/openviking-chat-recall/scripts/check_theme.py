#!/usr/bin/env python3
"""Сверка одного файла темы с его материалом — поимённо, чтобы можно было чинить.

Тот же судья, что у раскладки (`theme_gap`), но с развёрнутым ответом: гейт
говорит «потеряно 2», а исполнителю нужно знать, какие именно. Без этого он
правит вслепую и выдумывает якоря — а выдуманный якорь хуже отсутствующего:
он подписывает чужой цитатой чужой разговор.

    python3 check_theme.py <flat> <тема> <файл>
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave_ready import FULL, cyr_share, flat_anchors, flat_text, theme_gap, topic_files

SHOW = 12


def main(flat: str, theme: str, path: str) -> int:
    names = topic_files(flat).get(theme)
    if names is None:
        print(f"темы {theme} нет в карте тем")
        return 2
    body = open(path, encoding="utf-8").read()
    gap = theme_gap(body, flat, names)
    if not gap:
        print(f"готово · {len(body)} симв · кириллицы {cyr_share(body):.0%} · "
              f"якорей {len(set(FULL.findall(body)))}")
        return 0

    print(f"НЕ ПРИНЯТО: {gap}")
    if not body.startswith("---"):
        print("  файл обязан начинаться с шапки `---`")
        return 1
    want, got = flat_anchors(flat, names), set(FULL.findall(body))
    lost, fake = sorted(want - got), sorted(got - want)
    if lost:
        print(f"  потеряно {len(lost)} — эти пункты материала не доехали:")
        for source, line in lost[:SHOW]:
            print(f"    [{source}#L{line}]")
        if len(lost) > SHOW:
            print(f"    … и ещё {len(lost) - SHOW}")
    if fake:
        print(f"  лишних {len(fake)} — таких якорей в материале нет:")
        for source, line in fake[:SHOW]:
            print(f"    [{source}#L{line}]")
        if len(fake) > SHOW:
            print(f"    … и ещё {len(fake) - SHOW}")
    if lost and fake:
        print("  частая причина: номер строки взят из одного файла, имя — из соседнего")
    if not lost and not fake:
        print(f"  доля кириллицы в материале {cyr_share(flat_text(flat, names)):.0%}, "
              f"в файле {cyr_share(body):.0%}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
