#!/usr/bin/env python3
"""Смысловой аудит страниц против файла темы — инвариант 7 протокола.

«Проверяет не тот, кто делал» до сих пор оставался словами: форму проверяли
скрипты, покрытие — арифметика, а вот сказала ли страница больше своего
источника, не проверял никто. Это ровно те провалы, ради которых писался
ACCEPTANCE: сдвинутая модальность и разрезанный ответ.

Один агент — одна тема: файл темы целиком и все страницы, из него собранные.

    python3 build_audit_tasks.py <папка заданий> [--only-clean]
"""
from __future__ import annotations

import glob
import json
import os
import sys

ART = "experiments/openviking-chat-recall/artifacts"


def main(out_dir: str, only_clean: bool) -> int:
    topics = json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))["topics"]
    topic_of = {name: t["id"] for t in topics for name in t["files"]}
    touched = {topic_of[row.split("\t")[0]]
               for row in open(f"{ART}/coverage-gaps.tsv", encoding="utf-8")}

    pages_by_topic: dict[str, list[str]] = {}
    for path in sorted(glob.glob(f"{ART}/wiki-v1/**/*.md", recursive=True)):
        if os.path.basename(path) == "index.md":
            continue
        text = open(path, encoding="utf-8").read()
        head = text.split("---", 2)[1] if text.startswith("---") else ""
        for line in head.splitlines():
            if line.startswith("topic:"):
                pages_by_topic.setdefault(line.split(":", 1)[1].strip().strip('"'), []).append(path)

    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for topic in sorted(pages_by_topic):
        if only_clean and topic in touched:
            continue
        source = f"{ART}/flatten-v1/topics/{topic}.md"
        if not os.path.exists(source):
            continue
        pages = pages_by_topic[topic]
        bodies = "\n\n".join(
            f"### Страница `{os.path.relpath(p, f'{ART}/wiki-v1')}`\n\n"
            + open(p, encoding="utf-8").read().strip()
            for p in pages
        )
        open(os.path.join(out_dir, f"{topic}.txt"), "w", encoding="utf-8").write(
            f"""Роль: строгий проверяющий, который эту работу не делал. Перед тобой источник —
файл темы с проверенными фактами и якорями — и страницы библиотеки, собранные
из него. Страницы должны раскладывать источник по вопросам и **ничего к нему не
добавлять**.

Ищи ровно пять видов расхождения и ничего больше:

- `лишнее` — страница утверждает то, чего в источнике нет: новый участник,
  предмет, граница, причинная связь, оценка или статус;
- `модальность` — критерий подан как решение, идея как правило, намерение как
  сделанное. Источник называет модальность прямо, угадывать не надо;
- `разрезано` — полный ответ на один вопрос лежит на двух страницах, и с
  каждой из них уходишь с половиной, не зная об этом;
- `смешано` — одна страница отвечает на два разных вопроса, которые будут
  искать порознь;
- `потеряно` — факт источника не попал ни на одну страницу.

Чего искать не надо: стиль, длину, порядок разделов, формулировки заголовков.

## Источник темы

{open(source, encoding='utf-8').read().strip()}

## Страницы, собранные из него ({len(pages)})

{bodies}

## Формат ответа

Только строки TSV, по одной на расхождение, без шапки и пояснений. Четыре
колонки:

```
<путь страницы или «—» для потерянного>\t<лишнее|модальность|разрезано|смешано|потеряно>\t<что именно, одной фразой>\t<чем в источнике это опровергается: якорь или «в источнике нет»>
```

Расхождений не нашёл — верни одну строку: `—\tчисто\tрасхождений нет\t—`.
Пустой ответ и рассуждения вокруг таблицы не принимаются.

## Стоп

Файлы не открывай и не правь — весь материал выше.
""")
        written += 1
    print(f"заданий аудита: {written} -> {out_dir}"
          + (f" (пропущено тронутых добором: {len(touched)})" if only_clean else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "_workspace/ox-audit/tasks",
                          "--only-clean" in sys.argv))
