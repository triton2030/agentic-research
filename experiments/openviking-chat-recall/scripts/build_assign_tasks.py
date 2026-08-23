#!/usr/bin/env python3
"""Назначение темы разговорам, которых карта тем ещё не знает.

`apply_update.py` такие разговоры пропускает и называет — по построению, потому
что дописывать пункт некуда. Их накапливается тем больше, чем дольше живёт
корпус: половина первой дельты обновления пришлась именно на них.

Решение отдаётся агенту, а не эвристике: сорок существующих тем даются с их
`why` — границей темы, — и агент выбирает одну либо честно предлагает новую.
Механика (кто в списке, что подставить, куда положить) остаётся здесь.

    python3 build_assign_tasks.py <папка заданий> [<папка прогонов обновления>]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ART = "experiments/openviking-chat-recall/artifacts"
CORPUS = "_ops/chat-recall"
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")


def known_files(topics: list[dict]) -> set[str]:
    return {f for t in topics for f in t["files"]}


def main(out_dir: str, runs: str | None) -> int:
    topics = json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))["topics"]
    placed = known_files(topics)

    # Кандидаты — разговоры корпуса, которых нет ни в одной теме. Список
    # прогонов обновления сюда не нужен: он говорит о записях, а тема
    # назначается файлу целиком.
    fresh = [os.path.basename(p) for p in sorted(glob.glob(f"{CORPUS}/*.md"))
             if os.path.basename(p) != "README.md" and os.path.basename(p) not in placed]
    if not fresh:
        print("разговоров без темы нет")
        return 0

    catalog = "\n".join(f"- `{t['id']}` — {t['title']}. Граница: {t['why']}" for t in topics)
    os.makedirs(out_dir, exist_ok=True)
    for name in fresh:
        text = open(os.path.join(CORPUS, name), encoding="utf-8").read()
        rows = [l for l in text.splitlines() if l.startswith("* ") and TYPE.search(l)]
        body = "\n".join(rows)
        open(os.path.join(out_dir, name[:-3] + ".txt"), "w", encoding="utf-8").write(
            f"""Роль: библиотекарь слоя тем. У тебя один разговор и сорок существующих тем.
Вопрос ровно один: **в какую тему этот разговор попадает.**

Тема — предмет, а не проект и не дата. Разговор целиком идёт в одну тему: он
уже разобран построчно на другом шаге, и здесь решается только адрес файла.

## Существующие темы

{catalog}

## Когда предлагать новую тему

Только если предмет разговора не помещается ни в одну границу выше **и**
захватывает больше одной реплики. Одна случайная реплика новой темы не
оправдывает: она уходит в ближайшую по предмету. Новая тема называется так же,
как существующие: короткое латинское имя через дефис.

## Разговор `{name}`

```
{body}
```

## Ответ

Ровно три строки, без пояснений вокруг:

```
тема: <id существующей темы ИЛИ новое имя>
новая: <да|нет>
почему: <одно предложение о предмете, не о проекте>
```
""")
    print(f"заданий назначения: {len(fresh)} -> {out_dir}")
    return 0


if __name__ == "__main__":
    plain = [a for a in sys.argv[1:] if not a.startswith("--")]
    raise SystemExit(main(plain[0] if plain else "_workspace/ox-assign/tasks",
                          plain[1] if len(plain) > 1 else None))
