#!/usr/bin/env python3
"""Два одинаковых задания на один набор вопросов: библиотеке и разговорам.

Сравнивать библиотеку не с чем, кроме источника, из которого она сделана.
Поэтому вопросы задаются дважды и одинаково, а разной остаётся только папка,
в которой отвечающий живёт. Вопросы пишет третье окно, видевшее только
разговоры, — иначе язык вопроса подстроится под язык заголовков и проверка
измерит саму себя.
"""
from __future__ import annotations

import json
import os
import sys

ART = "experiments/openviking-chat-recall/artifacts"

BODY = """Роль: агент, который начинает работу в проекте и должен опереться на прежние
решения владельца. {where}

## Что сделать

Ответь на {count} вопросов ниже. По каждому — {mode}.

Правила, одинаковые для любого источника:

- отвечай **только тем, что нашёл**. Не нашёл — так и пиши `нет ответа`.
  Выдуманный правдоподобный ответ здесь хуже пустого: он не отличим от верного;
- не меняй модальность. Если владелец задал критерий, ответ говорит «задал
  критерий», а не «решил». Если это была идея — «высказал идею»;
- считай, сколько файлов ты открыл, чтобы ответить. Считай честно, включая
  открытые и оказавшиеся ненужными;
- назови свою уверенность одним словом: `уверен` или `сомневаюсь`.
  `сомневаюсь` не штрафуется — молчаливая ошибка штрафуется.

## Формат ответа

Только строки TSV, по одной на вопрос, без шапки и пояснений вокруг. Пять
колонок через табуляцию:

```
<номер вопроса>\t<ответ одним-двумя предложениями>\t<файлы, которые открыл, через запятую>\t<сколько файлов открыл>\t<уверен|сомневаюсь>
```

## Вопросы

{questions}

## Стоп

Ничего не правь. Ответ — ровно {count} строк TSV.
"""

WHERE = {
    "library": "Тебе доступна только библиотека знаний: рабочая папка и есть её корень. "
               "Начни с `index.md`, если он есть, иначе — с имён папок и файлов.",
    "corpus": "Тебе доступны только исходные разговоры с владельцем: рабочая папка и есть "
              "их корень. Каждый файл — один разговор, записи внутри датированы.",
}
MODE = {
    "library": "путь страницы, на которой нашёл ответ",
    "corpus": "имя файла и номер строки, где нашёл ответ",
}


def main(answers: str, out_dir: str) -> int:
    payload = json.load(open(answers, encoding="utf-8"))
    if not payload.get("ok") or not payload.get("response"):
        print(f"вопросы не готовы: ok={payload.get('ok')}")
        return 1
    rows = [line.split("\t") for line in payload["response"].splitlines() if line.count("\t") >= 3]
    if not rows:
        print("в ответе нет строк TSV")
        return 1
    os.makedirs(out_dir, exist_ok=True)
    listing = "\n".join(f"{i}. {row[0].strip()}" for i, row in enumerate(rows, start=1))
    for kind in ("library", "corpus"):
        open(os.path.join(out_dir, f"{kind}.txt"), "w", encoding="utf-8").write(
            BODY.format(where=WHERE[kind], mode=MODE[kind], count=len(rows), questions=listing)
        )
    with open(f"{ART}/accept-questions.tsv", "w", encoding="utf-8") as out:
        for row in rows:
            out.write("\t".join(part.strip() for part in row) + "\n")
    print(f"вопросов: {len(rows)} | задания -> {out_dir} | эталон -> {ART}/accept-questions.tsv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(
        sys.argv[1] if len(sys.argv) > 1 else "_workspace/ox-accept/runs/questions.json",
        sys.argv[2] if len(sys.argv) > 2 else "_workspace/ox-answer/tasks",
    ))
