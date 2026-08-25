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
TOPIC_FIELD = re.compile(r"(topic:\s*)([^|\n]+?)(\s*)(?=\||$)", re.MULTILINE)
TYPE_FIELD = re.compile(r"(?:^|\|)\s*type:\s*([^\s|]+)")


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


def meta_at(block: str) -> int | None:
    """Начало служебного хвоста записи — ПОСЛЕДНИЙ разделитель, не первый.

    Первый ломается о речь владельца: реплика «пиши так — topic: X» выглядит
    служебной с начала строки, и правка съедала бы остаток цитаты. Служебные
    поля стоят в конце записи, поэтому счёт идёт с конца.
    """
    starts = list(META_START.finditer(block))
    return starts[-1].end() if starts else None


def topic_of(block: str) -> str | None:
    meta = meta_at(block)
    if meta is None:
        return None
    field = TOPIC_FIELD.search(block, meta)
    return field.group(2).strip() if field else None


def is_typed_record(block: str) -> bool:
    """Return whether a block has a typed metadata tail.

    A missing ``topic`` is an input defect for retopic, not a reason to drop
    the record from the task denominator.  Keep this check separate from
    ``topic_of`` so callers can distinguish those two cases.
    """
    meta = meta_at(block)
    return meta is not None and TYPE_FIELD.search(block[meta:]) is not None


def typed_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """Return every typed record, including records whose topic is missing."""
    return [
        (number, block)
        for number, block in star_blocks(lines)
        if is_typed_record(block)
    ]


def topics_by_line(lines: list[str]) -> dict[int, str]:
    """Canonical per-record topic keyed by the record's 1-based start line."""
    return {
        number: topic
        for number, block in star_blocks(lines)
        if (topic := topic_of(block)) is not None
    }


def load_catalog(catalog_path: str) -> list[dict[str, object]]:
    """Load and validate the complete supplied topic catalog."""
    with open(catalog_path, encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"каталог тем не является объектом: {catalog_path}")
    topics = payload.get("topics")
    if not isinstance(topics, list):
        raise TypeError(f"каталог тем не содержит списка topics: {catalog_path}")

    seen: set[str] = set()
    for index, topic in enumerate(topics, 1):
        if not isinstance(topic, dict):
            raise TypeError(
                f"тема {index} в каталоге не является объектом: {catalog_path}"
            )
        topic_id = topic.get("id")
        title = topic.get("title")
        if not isinstance(topic_id, str) or not topic_id:
            raise ValueError(f"тема {index} не имеет непустого id: {catalog_path}")
        if not isinstance(title, str) or not title:
            raise ValueError(
                f"тема {topic_id!r} не имеет непустого title: {catalog_path}"
            )
        if topic_id in seen:
            raise ValueError(f"дублирующаяся тема {topic_id!r}: {catalog_path}")
        seen.add(topic_id)
    return topics


def main(out_dir: str, corpus: str = CORPUS, catalog_path: str | None = None) -> int:
    if not os.path.isdir(corpus):
        raise FileNotFoundError(f"корпус не найден или не папка: {corpus}")
    if catalog_path is None:
        if str(corpus) != CORPUS:
            raise ValueError("для внешнего корпуса каталог тем нужно передать явно")
        catalog_path = f"{ART}/flatten-v1/topics.json"
    topics = load_catalog(catalog_path)
    # Свежая карта стадии 2 несёт только заголовок; `why` появляется позже, у
    # тем, чью границу назвал исторический прогон сборки.
    catalog = "\n".join(
        f"- `{t['id']}` — {t['title']}."
        + (f" Граница: {t['why']}" if t.get("why") else "")
        for t in topics
    )
    os.makedirs(out_dir, exist_ok=True)
    built = skipped = 0
    for path in sorted(glob.glob(f"{corpus}/*.md")):
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        # The task denominator is every typed record.  In particular, a
        # typed record without a legacy topic must be shown to the agent so it
        # can be repaired or assigned; filtering on topic_of() silently lost
        # exactly those records.
        rows = typed_blocks(lines)
        if not rows:
            skipped += 1
            continue
        context = next((l for l in lines if l.startswith("session-context: ")), "")
        body = "\n\n".join(f"### L{n}\n```\n{block}\n```" for n, block in rows)
        task_path = os.path.join(out_dir, name[:-3] + ".txt")
        with open(task_path, "w", encoding="utf-8") as handle:
            handle.write(
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
