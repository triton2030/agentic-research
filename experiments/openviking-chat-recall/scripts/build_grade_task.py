#!/usr/bin/env python3
"""Оценка рукавов приёмки вслепую: судья не знает, какой ответ чей.

Судить самому нельзя: я библиотеку и строил, и любое «ну тут же по сути верно»
пойдёт в её пользу совершенно искренне. Но и назвать судье рукава честными
именами нельзя — знание, где чей ответ, смещает оценку само по себе. Поэтому
рукава переименованы в буквы, а их порядок в каждом вопросе выбирается
детерминированным жребием от номера вопроса. Расшифровка остаётся здесь.
"""
from __future__ import annotations

import json
import os
import sys

ART = "experiments/openviking-chat-recall/artifacts"
ARMS = ["library", "topics", "digest", "corpus"]
RUNS = "_workspace/ox-answer/runs"


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


def main(runs: str, out_dir: str) -> int:
    gold = [line.rstrip("\n").split("\t") for line in open(f"{ART}/accept-questions.tsv", encoding="utf-8")]
    got = {arm: answers(os.path.join(runs, f"{arm}.json")) for arm in ARMS}

    blocks, key = [], {}
    letters = "ABCD"
    for i, row in enumerate(gold, start=1):
        question, right, anchors, types = (row + ["", "", ""])[:4]
        # Жребий детерминирован номером вопроса: воспроизводим и не подбираем.
        order = ARMS[i % len(ARMS):] + ARMS[:i % len(ARMS)]
        key[i] = order
        shown = []
        for letter, arm in zip(letters, order):
            cell = got[arm].get(i)
            if cell is None:
                shown.append(f"   {letter}: (ответа нет)")
            else:
                text, opened, count, sure = cell
                shown.append(f"   {letter}: {text}\n      открыл файлов: {count} · {sure}")
        blocks.append(
            f"{i}. Вопрос: {question}\n   Верный ответ: {right}\n"
            f"   Модальность записей: {types}\n" + "\n".join(shown))

    os.makedirs(out_dir, exist_ok=True)
    brief = f"""Роль: строгий проверяющий. Ты сравниваешь четыре набора ответов на одни и те же
вопросы. Что стоит за буквами `A`, `B`, `C`, `D`, тебе не сообщается и угадывать
не надо: у разных вопросов порядок разный.

## Что сделать

По каждому вопросу вынеси два вердикта на каждую букву.

**Совпадение с верным ответом:**

- `совпал` — по существу то же самое, пусть другими словами;
- `частично` — верно, но потеряна существенная часть верного ответа;
- `разошёлся` — сказано другое, в том числе правдоподобное, но не то;
- `нет` — ответа нет или сказано «не нашёл».

`разошёлся` — самый важный вердикт, не смягчай его до `частично`: уверенно
сказанное не то опаснее честного «не нашёл».

**Модальность.** Указана модальность записей владельца: решение, критерий,
коррекция, идея, предпочтение, правило-кандидат. Ответ обязан её сохранить.
`верна` или `сдвинута`.

Отдельно следи за одним сдвигом: решение владельца, поданное как уже
сделанное. «Строка внесена» вместо «владелец решил внести строку» — это
`сдвинута`, даже если все слова взяты из источника.

## Формат ответа

Только строки TSV, по одной на вопрос, без шапки и пояснений. Десять колонок:

```
<номер>\t<A: совпал|частично|разошёлся|нет>\t<B>\t<C>\t<D>\t<A: верна|сдвинута>\t<B>\t<C>\t<D>\t<одна фраза: чем ответы отличались по существу>
```

## Материал

{chr(10).join(blocks)}

## Стоп

Ничего не правь и никаких файлов не открывай — весь материал выше. Ответ —
ровно {len(gold)} строк TSV.
"""
    open(os.path.join(out_dir, "grade.txt"), "w", encoding="utf-8").write(brief)
    json.dump(key, open(f"{ART}/accept-blinding.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"вопросов {len(gold)} | рукавов {len(ARMS)} | задание -> {out_dir}/grade.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else RUNS,
                          sys.argv[2] if len(sys.argv) > 2 else "_workspace/ox-grade/tasks"))
