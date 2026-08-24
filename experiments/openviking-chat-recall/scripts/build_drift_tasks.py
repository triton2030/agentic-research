#!/usr/bin/env python3
"""Задания на разбор дрейфа якорей: смысл проверяет модель, арифметику — скрипт.

Скрипт умеет сказать, что якорь не попадает ни в одну запись. Он не умеет
сказать, что якорь попал в настоящую запись, но не в ту: сдвинутая на две
строки ссылка выглядит безупречно. Это и есть «правдоподобный сосед» — провал
П3 на уровне провенанса, и различить его может только чтение.

Один разговор — один агент: он видит записи этого разговора целиком и все
факты библиотеки, которые на него ссылаются.
"""
from __future__ import annotations

import glob
import os
import re
import sys
from collections import defaultdict

ART = "experiments/openviking-chat-recall/artifacts"
CORPUS = "_ops/chat-recall/raw"
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
# Страницы ссылаются двумя способами: якорь внутри пункта и якорь в разделе
# источников, где текста перед ссылкой нет вовсе. Оба несут утверждение —
# в первом случае это сам пункт, во втором метка ссылки. Берём оба, иначе
# шесть разговоров из четырнадцати выпадают из проверки молча.
TOPICS = "_ops/chat-recall/topics"
NOT_A_TOPIC = {"AGENTS.md", "README.md"}
BARE = re.compile(r"\[?([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],]+\.md)#L(\d+)")
CITED = re.compile(r"\[([^\]]*)\]\(\.\./[^)]*?/([0-9]{4}-[^)/]+\.md)#L(\d+)\)")


def cited_facts() -> dict[str, list[tuple[int, str, str]]]:
    """Разговор -> [(строка, текст факта, файл темы)].

    Читает живой слой тем. Пока здесь стояла снятая библиотека страниц, разбор
    дрейфа честно отвечал «на него никто не ссылается» по продукту, которым
    никто не пользуется.
    """
    found: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    for path in sorted(glob.glob(f"{TOPICS}/*.md")):
        page = os.path.basename(path)
        if page in NOT_A_TOPIC:
            continue
        for line in open(path, encoding="utf-8"):
            stripped = line.rstrip("\n")
            # Страница носила якорь markdown-ссылкой, тема носит его голым.
            # Пока здесь стояла только первая форма, слой был невидим.
            head = stripped.split("[", 1)[0].lstrip("- ").strip()
            for label, name, number in CITED.findall(stripped):
                found[name].append((int(number), head or label.strip(), page))
            for name, number in BARE.findall(stripped):
                if head:
                    found[name].append((int(number), head, page))
    return found


def main(names: list[str], out_dir: str) -> int:
    facts = cited_facts()
    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for name in names:
        rows = facts.get(name)
        if not rows:
            print(f"{name}: ни один факт библиотеки на него не ссылается")
            continue
        records = []
        for number, line in enumerate(open(os.path.join(CORPUS, name), encoding="utf-8"), start=1):
            if line.startswith("* ") and TYPE.search(line):
                records.append(f"L{number}: {line.strip()}")
        unique = sorted({(number, text, page) for number, text, page in rows})
        claims = "\n\n".join(
            f"{i}. якорь L{number} · страница `{page}`\n   факт: {text}"
            for i, (number, text, page) in enumerate(unique, start=1)
        )
        rows = unique
        open(os.path.join(out_dir, name.replace(".md", "") + ".txt"), "w", encoding="utf-8").write(
            f"""Роль: проверяющий провенанс. Один разговор владельца и все факты библиотеки,
которые на него ссылаются. Шапка файла разговора со временем росла, и часть
ссылок могла съехать на соседнюю запись, оставшись при этом правдоподобной.

## Записи этого разговора ({len(records)})

{chr(10).join(records)}

## Факты библиотеки, ссылающиеся сюда ({len(rows)})

{claims}

## Что сделать

По каждому факту скажи, подтверждает ли его запись, на которую он ссылается.
Не «похоже» — подтверждает ли по существу. Если нет, найди среди записей выше
ту, которая подтверждает, и назови её строку. Такой записи нет — так и скажи.

Сдвинутый якорь почти всегда попадает в настоящую запись, поэтому «выглядит
осмысленно» проверкой не является: сравнивай предмет факта с предметом записи.

## Формат ответа

Только строки TSV, по одной на факт, без шапки и пояснений. Четыре колонки:

```
<номер факта>\t<якорь как есть>\t<верный якорь или то же значение>\t<совпал|исправлен|не найден>
```

## Стоп

Файлы не открывай и не правь — весь материал выше. Ровно {len(rows)} строк TSV.
""")
        written += 1
    print(f"заданий на разбор дрейфа: {written} -> {out_dir}")
    return 0


if __name__ == "__main__":
    names = sys.argv[2:] if len(sys.argv) > 2 else []
    raise SystemExit(main(names, sys.argv[1] if len(sys.argv) > 1 else "_workspace/ox-drift/tasks"))
