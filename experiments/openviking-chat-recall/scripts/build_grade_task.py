#!/usr/bin/env python3
"""Оценка двух наборов ответов вслепую: судья не знает, где библиотека.

Судить самому нельзя: я библиотеку и строил, и любое «ну тут же по сути верно»
пойдёт в её пользу. Но и назвать судье колонки честными именами нельзя —
знание, какой ответ чей, само по себе смещает оценку. Поэтому источники
переименованы в `A` и `B`, а их порядок в каждом вопросе выбирается
детерминированным жребием от номера вопроса. Расшифровка остаётся здесь.
"""
from __future__ import annotations

import json
import os
import sys

ART = "experiments/openviking-chat-recall/artifacts"


def answers(path: str) -> dict[int, list[str]]:
    payload = json.load(open(path, encoding="utf-8"))
    if not payload.get("ok") or not payload.get("response"):
        raise SystemExit(f"{path}: прогон не принят (ok={payload.get('ok')})")
    rows: dict[int, list[str]] = {}
    for line in payload["response"].splitlines():
        if line.count("\t") < 4:
            continue
        parts = line.split("\t")
        number = "".join(ch for ch in parts[0] if ch.isdigit())
        if number:
            rows[int(number)] = [p.strip() for p in parts[1:5]]
    return rows


def main(library: str, corpus: str, out_dir: str) -> int:
    gold = [line.rstrip("\n").split("\t") for line in open(f"{ART}/accept-questions.tsv", encoding="utf-8")]
    lib, cor = answers(library), answers(corpus)

    blocks, key = [], {}
    for i, row in enumerate(gold, start=1):
        question, right, anchors, types = (row + ["", "", ""])[:4]
        # Жребий детерминирован номером вопроса: воспроизводим и не подбираем.
        first_is_library = i % 2 == 1
        pair = [("library", lib.get(i)), ("corpus", cor.get(i))]
        if not first_is_library:
            pair.reverse()
        key[i] = [name for name, _ in pair]
        shown = []
        for label, (_, got) in zip("AB", pair):
            if got is None:
                shown.append(f"   {label}: (ответа нет)")
            else:
                text, opened, count, sure = got
                shown.append(f"   {label}: {text}\n      открыл файлов: {count} ({opened}) · {sure}")
        blocks.append(
            f"{i}. Вопрос: {question}\n   Верный ответ: {right}\n"
            f"   Модальность записей: {types}\n" + "\n".join(shown)
        )

    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "grade.txt"), "w", encoding="utf-8").write(f"""Роль: строгий проверяющий. Ты сравниваешь два набора ответов на одни и те же
вопросы. Что за источники стоят за `A` и `B`, тебе не сообщается и угадывать не
надо: разные вопросы могут иметь разный порядок.

## Что сделать

По каждому вопросу вынеси три вердикта.

**Совпадение с верным ответом** — отдельно для A и для B:

- `совпал` — по существу то же самое, пусть другими словами;
- `частично` — верно, но потеряна существенная часть верного ответа;
- `разошёлся` — сказано другое, в том числе правдоподобное, но не то;
- `нет` — ответа нет или сказано «не нашёл».

`разошёлся` — самый важный вердикт, не смягчай его до `частично`: уверенно
сказанное не то опаснее, чем честное «не нашёл».

**Модальность** — отдельно для A и для B. Указана модальность записей
владельца: решение, критерий, коррекция, идея, предпочтение, правило-кандидат.
Ответ обязан её сохранить. `верна` или `сдвинута`, и если сдвинута — куда.

## Формат ответа

Только строки TSV, по одной на вопрос, без шапки и пояснений. Шесть колонок:

```
<номер>\t<A: совпал|частично|разошёлся|нет>\t<B: то же>\t<A: верна|сдвинута>\t<B: то же>\t<одна фраза: чем ответы отличались по существу>
```

## Материал

{chr(10).join(blocks)}

## Стоп

Ничего не правь и никаких файлов не открывай — весь материал выше. Ответ —
ровно {len(gold)} строк TSV.
""", encoding="utf-8")
    json.dump(key, open(f"{ART}/accept-blinding.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"вопросов {len(gold)} | ответов библиотеки {len(lib)} | ответов корпуса {len(cor)}")
    print(f"задание -> {out_dir}/grade.txt | расшифровка -> {ART}/accept-blinding.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(
        sys.argv[1] if len(sys.argv) > 1 else "_workspace/ox-answer/runs/library.json",
        sys.argv[2] if len(sys.argv) > 2 else "_workspace/ox-answer/runs/corpus.json",
        sys.argv[3] if len(sys.argv) > 3 else "_workspace/ox-grade/tasks",
    ))
