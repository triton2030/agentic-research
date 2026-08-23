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
    horizon = {}
    horizon_path = "_ops/chat-recall-topics/horizon.json"
    if os.path.exists(horizon_path):
        horizon = json.load(open(horizon_path, encoding="utf-8"))
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
        f"**Горизонт: {horizon.get('date', 'дата снимка не проставлена')}.** "
        "Разговоров и решений новее этой даты здесь нет и быть не может: "
        "библиотека — снимок, а корпус растёт каждый день. Прежде чем "
        "действовать по найденному, спроси корпус про то же самое с "
        f"`--since {horizon.get('date', '<дата снимка>')}` — свежая поправка "
        "владельца сильнее любой страницы.", "",
    ]
    # Двухуровневый на самом деле, а не на словах. Корневой файл читают все и
    # всегда, поэтому в нём только сорок разделов с подсказками: шесть
    # килобайт вместо шестидесяти семи. Список страниц раздела живёт в файле
    # раздела, и его открывает лишь тот, кто этот раздел выбрал.
    os.makedirs(os.path.join(WIKI, "sections"), exist_ok=True)
    for section in sections:
        order, name, cue = named.get(section["topic"], (999, section["title"], ""))
        rel = f"sections/{section['topic']}.md"
        body.append(f"- **[{name}]({rel})** — {cue or section['title']}"
                    f" · страниц {len(section['pages'])}")
        rows = [f"- [{page['title']}](../{page['path']}) — {page['description']}"
                for page in section["pages"]]
        open(os.path.join(WIKI, rel), "w", encoding="utf-8").write(
            f"---\ntype: index\ntitle: {name}\ndescription: {cue or section['title']}\n"
            f"topic: {section['topic']}\n---\n# {name}\n\n{cue}\n\n" + "\n".join(rows) + "\n")
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
