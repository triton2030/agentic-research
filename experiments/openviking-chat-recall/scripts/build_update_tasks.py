#!/usr/bin/env python3
"""Обновление библиотеки: только то, чего слой тем ещё не видел.

Протокол умел собирать всё с нуля и не умел догонять. А корпус растёт каждый
день: между сборкой и этим прогоном накопилось 223 записи в 35 разговорах.
Полная пересборка их бы забрала, но заодно переписала бы 1100 уже проверенных
фактов — дорого и бессмысленно.

Поэтому агент получает разговор целиком (иначе реплика без соседей теряет
предмет), но отвечает **только за перечисленные строки**. Всё остальное в
файле для него контекст, а не задание.

    python3 build_update_tasks.py <папка заданий>
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ART = "experiments/openviking-chat-recall/artifacts"
CORPUS = "_ops/chat-recall"
CONTRACT = "experiments/openviking-chat-recall/prompts/flatten-file.v1.md"
TYPE = re.compile(r"(?:—|\|)\s*type:\s*([^\s|]+)")
ANCH = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}-[^\s#\],)]+\.md)#L(\d+)")


def delta() -> dict[str, list[int]]:
    covered: set[tuple[str, int]] = set()
    for path in glob.glob(f"_ops/chat-recall/topics/*.md"):
        covered |= {(n, int(i)) for n, i in ANCH.findall(open(path, encoding="utf-8").read())}
    fresh: dict[str, list[int]] = {}
    for path in sorted(glob.glob(f"{CORPUS}/*.md")):
        name = os.path.basename(path)
        if name == "README.md":
            continue
        rows = [i for i, line in enumerate(open(path, encoding="utf-8").read().splitlines(), 1)
                if line.startswith("* ") and TYPE.search(line) and (name, i) not in covered]
        if rows:
            fresh[name] = rows
    return fresh


def main(out_dir: str) -> int:
    contract = open(CONTRACT, encoding="utf-8").read()
    topic_of = {f: t["id"] for t in json.load(open(f"{ART}/flatten-v1/topics.json", encoding="utf-8"))["topics"]
                for f in t["files"]}
    os.makedirs(out_dir, exist_ok=True)
    fresh = delta()
    for name, rows in fresh.items():
        text = open(os.path.join(CORPUS, name), encoding="utf-8").read()
        numbered = "\n".join(f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1))
        known = topic_of.get(name)
        place = (f"Этот разговор уже отнесён к теме `{known}`."
                 if known else "Этот разговор в темы ещё не попадал: тему для него назовут отдельно.")
        open(os.path.join(out_dir, name[:-3] + ".txt"), "w", encoding="utf-8").write(
            f"""Роль: редактор, превращающий запись разговора в сухое знание. Ниже контракт
работы, затем разговор целиком с пронумерованными строками.

**Отвечаешь только за перечисленные строки.** Остальной разговор дан как
контекст: без соседей реплика теряет предмет, и именно поэтому файл идёт
целиком. Но пункты пиши только по этим строкам — прочее уже разобрано раньше.

Строки задания: {", ".join(f"L{i}" for i in rows)}

{place}

{contract}

## Разговор `{name}`

```
{numbered}
```

## Ответ

Верни только содержимое выходного файла — от `---` до последнего пункта, без
пояснений и markdown-обёртки. Пунктов ровно столько, сколько самостоятельных
знаний нашлось в перечисленных строках; повтор внутри них схлопывается.
""")
    print(f"заданий обновления: {len(fresh)} разговоров, {sum(len(v) for v in fresh.values())} записей -> {out_dir}")
    json.dump({n: rows for n, rows in fresh.items()},
              open(f"{ART}/update-delta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "_workspace/ox-update/tasks"))
