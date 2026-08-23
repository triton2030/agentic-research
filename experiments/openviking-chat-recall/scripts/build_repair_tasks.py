#!/usr/bin/env python3
"""Правка находок аудита: модель формулирует, скрипт заменяет ровно названное.

Автор, правящий свою работу по чужому замечанию, незаметно смягчает замечание —
поэтому формулировку даёт не автор. Но и волю модели над файлом расширять
незачем: она возвращает пару «старый фрагмент дословно -> новый», и скрипт
делает точную замену либо отказывается. Ненайденный фрагмент — отказ, а не
приблизительная правка.

Структурные находки (`разрезано`, `смешано`) сюда не идут: они требуют решения
о составе страниц, а не о словах.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import defaultdict

ART = "experiments/openviking-chat-recall/artifacts"
WIKI = f"{ART}/wiki-v1"
WORDS = {"лишнее", "модальность", "потеряно"}


def findings(runs: str) -> tuple[dict[str, list[tuple[str, str, str, str]]], list[tuple[str, str, str, str]]]:
    wording: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    structural: list[tuple[str, str, str, str]] = []
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        topic = os.path.basename(path)[:-5]
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        if not payload.get("ok"):
            continue
        for line in (payload.get("response") or "").splitlines():
            if line.count("\t") < 3:
                continue
            page, kind, what, evidence = [p.strip().strip("`") for p in line.split("\t", 3)]
            kind = kind.lower()
            if kind == "чисто":
                continue
            if kind in WORDS and os.path.exists(os.path.join(WIKI, page)):
                wording[topic].append((page, kind, what, evidence))
            else:
                structural.append((topic, page, kind, what))
    return wording, structural


def main(runs: str, out_dir: str) -> int:
    wording, structural = findings(runs)
    os.makedirs(out_dir, exist_ok=True)
    for topic, items in sorted(wording.items()):
        pages = sorted({page for page, *_ in items})
        bodies = "\n\n".join(
            f"### `{page}`\n\n```\n{open(os.path.join(WIKI, page), encoding='utf-8').read().strip()}\n```"
            for page in pages
        )
        listing = "\n\n".join(
            f"{i}. страница `{page}` · вид `{kind}`\n   что не так: {what}\n   опора: {evidence}"
            for i, (page, kind, what, evidence) in enumerate(items, start=1)
        )
        source = f"_ops/chat-recall-topics/{topic}.md"
        open(os.path.join(out_dir, f"{topic}.txt"), "w", encoding="utf-8").write(
            f"""Роль: редактор, исправляющий страницы библиотеки по замечаниям проверяющего.
Замечания уже вынесены другим агентом; твоя работа — сформулировать правку, а не
пересматривать замечание.

Три вида замечаний и что с каждым делать:

- `лишнее` — страница утверждает то, чего нет в источнике. Убери именно этот
  элемент, не трогая остальное предложение. Часто это оговорка «…, а не X»:
  её надо снять целиком, а не переписать мягче;
- `модальность` — критерий подан как решение, идея как правило. Верни ту
  модальность, которую называет источник;
- `потеряно` — факта источника нет ни на одной странице. Дай пункт для той
  страницы, которая ближе всего по вопросу.

## Источник темы

{open(source, encoding='utf-8').read().strip() if os.path.exists(source) else '(файл темы не найден)'}

## Страницы

{bodies}

## Замечания ({len(items)})

{listing}

## Формат ответа

Только строки TSV, по одной на замечание, без шапки и пояснений. Четыре
колонки:

```
<путь страницы>\t<старый фрагмент дословно, одной строкой>\t<новый фрагмент>\t<чем правка обеспечена в источнике>
```

Старый фрагмент копируется со страницы **посимвольно** — по нему скрипт найдёт
место. Не совпал хоть один знак — правка будет отвергнута целиком, поэтому
бери короткий и точный кусок, а не абзац. Для `потеряно` в старом фрагменте
поставь `—`, и пункт будет добавлен в конец тела страницы.

Новый фрагмент пустой — значит фрагмент удаляется. Так и пиши: пусто.

## Стоп

Файлы не открывай и не правь — весь материал выше. Ровно {len(items)} строк TSV.
""")
    print(f"заданий на правку: {len(wording)} тем, {sum(len(v) for v in wording.values())} замечаний -> {out_dir}")
    if structural:
        with open(f"{ART}/audit-structural.tsv", "w", encoding="utf-8") as out:
            for row in structural:
                out.write("\t".join(row) + "\n")
        print(f"структурных находок (решаются отдельно): {len(structural)} -> {ART}/audit-structural.tsv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "_workspace/ox-audit/runs",
                          sys.argv[2] if len(sys.argv) > 2 else "_workspace/ox-repair/tasks"))
