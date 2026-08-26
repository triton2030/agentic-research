#!/usr/bin/env python3
"""Брифы стадий 3 и 4: слияние тем и сборка страниц.

Обе стадии устроены одинаково — контракт плюс входной материал темы, — и обе
раньше делались руками. Пока они не были скриптами, протокол нельзя было
применить к чужой папке, а значит нельзя было и проверить, переносим ли он.

    python3 build_stage_tasks.py merge <карта.json> <flat> <задания>
    python3 build_stage_tasks.py pages <карта.json> <темы>  <задания>
"""
from __future__ import annotations

import json
import os
import sys

PROMPTS = "experiments/openviking-chat-recall/prompts"
CONTRACT = {"merge": f"{PROMPTS}/merge-topic.v1.md", "pages": f"{PROMPTS}/pages-from-topic.v1.md"}

HEAD = {
    "merge": """Роль: редактор библиотеки знаний. Ниже контракт слияния, затем все сжатые файлы
одной темы. Собери из них один файл темы.

Якоря в этих файлах записаны коротко — `[L21]`, — и относятся к файлу, названному
в его же поле `source`. В файле темы каждый якорь пишется полностью:
`[<имя файла источника>#L21]`. Это перенос, а не набор по памяти: имя берётся из
шапки того файла, откуда пришёл пункт.""",
    "pages": """Роль: редактор библиотеки знаний. Ниже контракт сборки страниц, затем один файл
темы. Разложи его на страницы.""",
}

TAIL = {
    "merge": """## Формат ответа

Сначала верни содержимое файла темы — от `---` до последней строки, без
пояснений вокруг и без markdown-обёртки. Если старый пункт отменён более поздним, удали его
из topic и не создавай раздел `## Отменено` или другой tombstone.

После последней строки topic добавь технический блок учёта. Он остаётся в
`response` run JSON и writer удаляет его перед записью reader-facing topic:

```
<!-- TOPIC_ANCHOR_ACCOUNTING
{{"superseded":[{{"anchor":"<old-file>#L<line>","by":"<surviving-file>#L<line>"}}],"unresolved":[{{"anchor":"<file>#L<line>","reason":"chronology or scope cannot resolve"}}]}}
-->
```

Если ничего не superseded или unresolved, оставь соответствующие массивы
пустыми. При unresolved conflict опубликуй только один neutral marker в
разделе `## Не разрешено`; обе конфликтующие формулировки остаются в
raw/run evidence. В учёт попадают только исчезнувшие или unresolved входные
якоря; схлопнутые дубли остаются видимыми в topic. Класть файл на место не твоя
работа.

Шапка файла темы:

```
---
topic: {topic}
title: {topic} — <имя темы одной строкой>
sources: {count}
---
# {topic} — <то же имя темы>
```""",
    "pages": """## Формат ответа

По одному блоку на страницу, в таком виде и без пояснений между блоками:

```
=== ФАЙЛ <тип>/<слаг>.md
<полное содержимое страницы от `---` до последней строки>
```

Число страниц не ограничено. Класть файлы на место не твоя работа.""",
}


def main(stage: str, map_path: str, material: str, out_dir: str) -> int:
    topics = json.load(open(map_path, encoding="utf-8"))["topics"]
    contract = open(CONTRACT[stage], encoding="utf-8").read()
    prepared: dict[str, list[tuple[str, str]]] = {}
    if stage == "merge":
        for topic in topics:
            sources: list[tuple[str, str]] = []
            for name in topic["files"]:
                path = os.path.join(material, name)
                try:
                    source = open(path, encoding="utf-8").read().strip()
                except OSError:
                    print(
                        f"  {topic['id']}: входной материал отсутствует или исчез: {name}"
                    )
                    return 1
                sources.append((name, source))
            prepared[topic["id"]] = sources
    os.makedirs(out_dir, exist_ok=True)
    written = 0
    for topic in topics:
        if stage == "merge":
            parts = []
            for name, source in prepared[topic["id"]]:
                parts.append(f"### `{name}`\n\n```\n{source}\n```")
            body = f"## Сжатые файлы темы ({len(parts)})\n\n" + "\n\n".join(parts)
            count = len(parts)
        else:
            path = os.path.join(material, topic["id"] + ".md")
            if not os.path.exists(path):
                print(f"  нет файла темы: {topic['id']}")
                continue
            body = f"## Файл темы\n\n```\n{open(path, encoding='utf-8').read().strip()}\n```"
            count = 0
        open(os.path.join(out_dir, topic["id"] + ".txt"), "w", encoding="utf-8").write(
            f"{HEAD[stage]}\n\n{contract}\n\n{body}\n\n"
            + TAIL[stage].format(topic=topic["id"], count=count)
            + "\n\n## Стоп\n\nФайлы не открывай и не правь — весь материал выше.\n")
        written += 1
    print(f"заданий стадии {stage}: {written} -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
