#!/usr/bin/env python3
"""Вписать назначенные темы в карту тем.

Прогон возвращает решение тремя строками; сюда попадает только раскладка.
Новая тема заводится с пустым файлом — наполнит его обычное обновление.

    python3 apply_assign.py [--dry] [<папка прогонов>]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave import strip_fence

ART = "experiments/openviking-chat-recall/artifacts"
TOPICS = "_ops/chat-recall/topics"
FIELD = re.compile(r"^(тема|новая|заголовок|почему):\s*(.+)$", re.M)


def main(runs: str, dry: bool) -> int:
    data = json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))
    by_id = {t["id"]: t for t in data["topics"]}
    added = created = refused = 0

    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        name = os.path.basename(path)[:-5] + ".md"
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            refused += 1
            continue
        body = strip_fence(payload.get("response") or "")
        fields = dict(FIELD.findall(body))
        topic = (fields.get("тема") or "").strip().strip("`")
        if not payload.get("ok") or not topic:
            print(f"  не принят: {name}")
            refused += 1
            continue
        if topic not in by_id:
            # Новое имя принимается только когда прогон сам объявил его новым:
            # иначе опечатка в существующем id молча заводила бы тему-двойник.
            if (fields.get("новая") or "").strip().lower() not in {"да", "yes"}:
                print(f"  тема `{topic}` не существует и не объявлена новой: {name}")
                refused += 1
                continue
            title = (fields.get("заголовок") or "").strip().strip("-—").strip()
            by_id[topic] = {"id": topic, "title": title or topic,
                            "why": (fields.get("почему") or "").strip(), "files": []}
            data["topics"].append(by_id[topic])
            created += 1
            print(f"  новая тема: {topic}")
        # Заголовок-заглушка держится ровно до первого прогона, который его
        # назвал: иначе шапка темы навсегда остаётся slug-ом и расходится с
        # контрактом слияния.
        named = (fields.get("заголовок") or "").strip().strip("-—").strip()
        if named and by_id[topic]["title"] == topic:
            by_id[topic]["title"] = named
        if name not in by_id[topic]["files"]:
            by_id[topic]["files"].append(name)
            added += 1
        print(f"  {name} -> {topic}")

    print(f"назначено: {added} | новых тем: {created} | не принято: {refused}")
    if dry:
        return 0
    json.dump(data, open(f"{ART}/flatten-v1/topics.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for topic in data["topics"]:
        path = os.path.join(TOPICS, topic["id"] + ".md")
        if not os.path.exists(path):
            # `sources` — число разговоров темы, как в контракте слияния; ноль
            # в свежем файле разошёлся бы с картой в тот же миг.
            open(path, "w", encoding="utf-8").write(
                f"---\ntopic: {topic['id']}\ntitle: {topic['title']}\n"
                f"sources: {len(topic['files'])}\n---\n"
                f"# {topic['title']}\n\nГраница темы: {topic['why']}\n")
            print(f"  заведён файл темы: {topic['id']}.md")
    print("карта тем обновлена")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-assign/runs", "--dry" in sys.argv))
