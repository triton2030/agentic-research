#!/usr/bin/env python3
"""Рукав действующего маршрута: поиск выбирает файлы, агент читает holder-ы.

Скил `1chat-recall` ходит к корпусу не глазами по папке, а гибридным поиском:
`chat_digest.py` отдаёт до десяти holder-карточек, из которых агент читает
три-четыре целиком. Чтобы сравнение было честным, этот рукав воспроизводит
именно такой ход: поиск здесь запускает скрипт, а читает и отвечает агент.

Даём агенту не сырой JSON, а то же, что видит главный агент скила: карточку
разговора, его свежесть и сильнейшую цитату.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

DIGEST = "/Users/triton/.claude/skills/1chat-recall/scripts/chat_digest.py"
ART = "experiments/openviking-chat-recall/artifacts"


def ask(corpus: str, query: str) -> list[dict]:
    done = subprocess.run(
        ["uv", "run", "--locked", "--script", DIGEST, corpus, "--query", query, "--json"],
        capture_output=True, text=True,
    )
    if done.returncode != 0:
        return []
    try:
        return json.loads(done.stdout).get("holders", [])
    except Exception:
        return []


def main(corpus: str, out_dir: str) -> int:
    questions = [line.rstrip("\n").split("\t")[0]
                 for line in open(f"{ART}/accept-questions.tsv", encoding="utf-8")]
    blocks = []
    for i, question in enumerate(questions, start=1):
        cards = ask(corpus, question)
        rows = []
        for card in cards:
            strongest = (card.get("strongest_quote") or {}).get("text") or "—"
            rows.append(
                f"   - `{card['file']}` · {card.get('age', '')} · ранг {card.get('semantic_rank')}\n"
                f"     о чём разговор: {card.get('session_context', '')[:300]}\n"
                f"     сильнейшая цитата: {strongest[:220]}")
        blocks.append(f"{i}. {question}\n" + ("\n".join(rows) if rows else "   (поиск ничего не вернул)"))
        print(f"  {i:2d}. holder-ов найдено: {len(cards)}")

    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "digest.txt"), "w", encoding="utf-8").write(
        f"""Роль: агент, который начинает работу в проекте и должен опереться на прежние
решения владельца. Рабочая папка — корпус разговоров, файл на разговор.

Ты уже сделал первый шаг штатного маршрута: по каждому вопросу запущен поиск
скила `1chat-recall`, и ниже приведена его выдача — до десяти карточек
разговоров, отсортированных по свежести, с рангом релевантности, строкой «о чём
разговор» и сильнейшей цитатой.

**Карточка ответом не является.** Позицию владельца доказывает только его текст,
прочитанный в файле разговора от первой строки до последней. Открывай те
файлы, которые действительно нужны, и считай их честно.

## Что сделать

Ответь на {len(questions)} вопросов. По каждому — имя файла и номер строки, где нашёл ответ.

- отвечай **только тем, что нашёл**. Не нашёл — пиши `нет ответа`;
- не меняй модальность: критерий остаётся критерием, идея идеей;
- считай, сколько файлов открыл, включая открытые и оказавшиеся ненужными;
- уверенность одним словом: `уверен` или `сомневаюсь`.

## Формат ответа

Только строки TSV, по одной на вопрос, без шапки. Пять колонок:

```
<номер>\t<ответ одним-двумя предложениями>\t<файлы, которые открыл, через запятую>\t<сколько файлов открыл>\t<уверен|сомневаюсь>
```

## Вопросы и выдача поиска

{chr(10).join(blocks)}

## Стоп

Ничего не правь. Ответ — ровно {len(questions)} строк TSV.
""")
    print(f"задание рукава digest -> {out_dir}/digest.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "_ops/chat-recall",
                          sys.argv[2] if len(sys.argv) > 2 else "_workspace/ox-answer/digest-task"))
