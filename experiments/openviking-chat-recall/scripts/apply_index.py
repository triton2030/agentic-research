#!/usr/bin/env python3
"""Сборка index.md: имена разделов от модели, пути и состав от скелета."""
from __future__ import annotations

import json
import os
import sys

ART = "experiments/openviking-chat-recall/artifacts"
WIKI = f"{ART}/wiki-v1"


def main(skeleton_path: str, run_path: str) -> int:
    skeleton = json.load(open(skeleton_path, encoding="utf-8"))
    payload = json.load(open(run_path, encoding="utf-8"))
    if not payload.get("ok"):
        print(f"прогон не принят: ok={payload.get('ok')}")
        return 1
    named: dict[str, tuple[int, str, str]] = {}
    for line in (payload.get("response") or "").splitlines():
        if line.count("\t") < 3:
            continue
        order, topic, name, cue = [p.strip().strip("`") for p in line.split("\t", 3)]
        if order.isdigit():
            named[topic] = (int(order), name, cue)

    sections = sorted(skeleton["sections"], key=lambda s: named.get(s["topic"], (999,))[0])
    missing = [s["topic"] for s in sections if s["topic"] not in named]
    body = [
        "---", "type: index",
        "title: О чём эта библиотека",
        "description: Двухуровневый указатель: разделы по предметам, внутри — вопросы страниц.",
        "---", "# О чём эта библиотека", "",
        f"Знание владельца, собранное из его разговоров: {skeleton['page_count']} страниц "
        f"в {skeleton['section_count']} разделах. Заголовок страницы — вопрос, "
        "на который она отвечает.", "",
        "**Это обзорный слой, а не доказательство позиции.** Страница показывает "
        "итог без даты и без отменённого, поэтому проверку отмены по ней "
        "исполнить нельзя. Нашёл ответ и цена ошибки высока — открой разговор "
        "по ссылке внизу страницы и проверь его тремя источниками отмены, как "
        "предписывает скил `1chat-recall`.", "",
    ]
    for section in sections:
        order, name, cue = named.get(section["topic"], (999, section["title"], ""))
        body.append(f"## {name}")
        if cue:
            body.append("")
            body.append(cue)
        body.append("")
        for page in section["pages"]:
            body.append(f"- [{page['title']}]({page['path']}) — {page['description']}")
        body.append("")
    open(os.path.join(WIKI, "index.md"), "w", encoding="utf-8").write("\n".join(body).rstrip() + "\n")
    print(f"указатель собран: {skeleton['page_count']} страниц, {len(sections)} разделов")
    if missing:
        print(f"разделы без имени от модели (взято рабочее): {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(
        sys.argv[1] if len(sys.argv) > 1 else f"{ART}/index-skeleton.json",
        sys.argv[2] if len(sys.argv) > 2 else "_workspace/ox-index2/runs/index.json"))
