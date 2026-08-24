#!/usr/bin/env python3
"""Переразметка тем у записей корпуса под словарь слоя тем.

Решение владельца 2026-08-24 (`_ops/chat-recall/raw/2026-08-24-125426-claude-832fc1f8.md`):
тема цитаты и файл слоя называют один предмет, поэтому поле `topic` каждой
записи переводится с прежнего фиксированного словаря на имена тем слоя.
Меняется только тема; текст записи, timestamp, type и context-note
неприкосновенны — их охраняет `apply_retopic.py`.

Одно задание — один разговор: агент видит все записи файла со строковыми
якорями и выбирает тему каждой записи из каталога слоя.

    python3 build_retopic_tasks.py <папка заданий> [<папка реплик> <каталог тем>]

Без второго и третьего аргументов работает над корпусом своего репозитория;
с ними — над любой чужой папкой реплик, как того требует RUNBOOK.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ART = "experiments/openviking-chat-recall/artifacts"
CORPUS = "_ops/chat-recall/raw"
META_KEYS = ("kind", "type", "topic", "context-note", "source", "precision", "source-ref")
META_START = re.compile(r"\s—\s(?=(?:" + "|".join(META_KEYS) + r"):)")
TOPIC_FIELD = re.compile(r"(topic:\s*)([^|\n]+?)(\s*)(?=\||$)", re.M)


def star_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """(1-based line of block start, full block text) for every `* ` block."""
    blocks: list[tuple[int, str]] = []
    start = None
    buff: list[str] = []
    for number, line in enumerate(lines, 1):
        if line.startswith("* "):
            if start is not None:
                blocks.append((start, "\n".join(buff).rstrip()))
            start, buff = number, [line]
        elif start is not None:
            buff.append(line)
    if start is not None:
        blocks.append((start, "\n".join(buff).rstrip()))
    return blocks


def topic_of(block: str) -> str | None:
    meta = META_START.search(block)
    if not meta:
        return None
    field = TOPIC_FIELD.search(block, meta.end())
    return field.group(2).strip() if field else None


def main(out_dir: str, corpus: str = CORPUS, catalog_path: str | None = None) -> int:
    catalog_path = catalog_path or f"{ART}/flatten-v1/topics.json"
    topics = json.load(open(catalog_path, encoding="utf-8"))["topics"]
    catalog = "\n".join(f"- `{t['id']}` — {t['title']}. Граница: {t['why']}" for t in topics)
    os.makedirs(out_dir, exist_ok=True)
    built = skipped = 0
    for path in sorted(glob.glob(f"{corpus}/*.md")):
        name = os.path.basename(path)
        lines = open(path, encoding="utf-8").read().splitlines()
        rows = [(n, block) for n, block in star_blocks(lines) if topic_of(block)]
        if not rows:
            skipped += 1
            continue
        context = next((l for l in lines if l.startswith("session-context: ")), "")
        body = "\n\n".join(f"### L{n}\n```\n{block}\n```" for n, block in rows)
        open(os.path.join(out_dir, name[:-3] + ".txt"), "w", encoding="utf-8").write(
            f"""Роль: библиотекарь слоя тем. У тебя один разговор, разобранный на записи,
и каталог существующих тем. Вопрос ровно один: **какая тема у каждой записи.**

Тема — предмет записи, а не проект, не дата и не тип высказывания. Записи
одного разговора свободно расходятся по разным темам. Прежнее значение
`topic:` внутри записи — старый словарь, оно не аргумент.

## Каталог тем

{catalog}

## Когда предлагать новую тему

Почти никогда. Только если предмет записи не помещается ни в одну границу выше
и в этом же разговоре таких записей больше одной. Одиночная запись уходит в
ближайшую по предмету тему. Новое имя — короткое латинское через дефис; объяви
его отдельной строкой до раскладки:

```
новая-тема: <имя> — <граница одним предложением>
```

## Разговор `{name}`

{context}

{body}

## Ответ

Только раскладка, по строке на каждую запись, без пояснений вокруг:

```
L<номер>: <id темы>
```

Покрой все записи из списка выше — пропуск строки делает ответ непринятым.
""")
        built += 1
    print(f"заданий переразметки: {built} -> {out_dir} | пропущено файлов без тем: {skipped}")
    return 0


if __name__ == "__main__":
    plain = [a for a in sys.argv[1:] if not a.startswith("--")]
    raise SystemExit(main(
        plain[0] if plain else "_workspace/ox-retopic/tasks",
        plain[1] if len(plain) > 1 else CORPUS,
        plain[2] if len(plain) > 2 else None,
    ))
