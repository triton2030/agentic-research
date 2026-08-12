#!/usr/bin/env python3
"""Ask a reading model about the owner-quote corpus; one call for Claude and Codex.

Owns the recall prompt template so both runtimes ask the same way. Search
tactics are deliberately NOT prescribed: a measured run on 2026-08-12 showed a
dictated «select files, read them whole» protocol cost twice as much and found
no more than the model's own strategy.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW = HERE / "codex_review.py"
PYTHON = HERE / ".venv" / "bin" / "python"
DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_CORPUS = "_ops/chat-recall"

TEMPLATE = """Цель: ответить на вопрос владельца проекта по корпусу его сохранённых цитат.

ВОПРОС: {question}

КОРПУС: {corpus} — Markdown-файлы, один файл = один разговор с владельцем,
то есть связная история одной работы. Имя файла: <дата>-<время>-<агент>-<session8>.md.
В шапке frontmatter с полями types: и topics: — инвентарь разговора без чтения тела.

ФОРМАТ ЗАПИСИ — одна строка на реплику:
* <timestamp> — "<текст>" — [kind: …] | type: … | topic: … | context-note: <заметка агента>
Без поля kind в кавычках дословная речь владельца. kind: selection — вариант,
который написал агент, а владелец лишь выбрал: это НЕ его прямая речь.
context-note писал агент; там часто стоят имена скилов, файлов и дат, которых
сам владелец не произносил — он называет вещи своими словами («эта штука»,
«свежие глаза», а не 1fresh-eyes).

СПОСОБ ПОИСКА выбираешь сам — он не предписан. Полезно знать: владелец
формулирует вариативно и приблизительно, поэтому узкая фраза из вопроса обычно
не находится дословно; короткий корень слова может сидеть внутри чужих слов.

EVIDENCE RULES:
- Отвечай только тем, что есть в корпусе; не достраивай из общих соображений.
- Каждое утверждение — с дословной цитатой и адресом файл.md:строка.
- Даты решают: более позднее слово владельца вытесняет более раннее. Отмена
  звучит буднично («снимаем», «убираем») — сверяй с датой и соседними репликами.
- Чего в корпусе нет — так и напиши. Пустота честнее достройки.

ФОРМА ВЫХОДА:
1. Прямой ответ на вопрос — что действует сейчас, 3-5 предложений.
2. Хронология: дата | что сказано | адрес | вытеснило ли предыдущее.
3. Что осталось неясным по корпусу.

ОГРАНИЧЕНИЯ: только чтение, ничего не меняй. Не вызывай инструменты claude-mcp —
работай файлами и shell."""


def build_prompt(question: str, corpus: Path) -> str:
    return TEMPLATE.format(question=question.strip(), corpus=corpus)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="Вопрос владельца по корпусу цитат.")
    parser.add_argument("--project", default=os.getcwd(), help="Корень проекта (default: cwd).")
    parser.add_argument("--corpus", help=f"Папка корпуса (default: <project>/{DEFAULT_CORPUS}).")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Модель (default: {DEFAULT_MODEL}).")
    parser.add_argument("--effort", default="xhigh", help="Reasoning effort (default: xhigh).")
    parser.add_argument("--print-prompt", action="store_true", help="Показать промпт и выйти.")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    corpus = Path(args.corpus).resolve() if args.corpus else project / DEFAULT_CORPUS
    if not corpus.is_dir():
        print(f"codex-recall: error: corpus not found: {corpus}", file=sys.stderr)
        return 2
    if not any(corpus.glob("*.md")):
        print(f"codex-recall: error: no .md records in {corpus}", file=sys.stderr)
        return 2

    prompt = build_prompt(args.question, corpus)
    if args.print_prompt:
        print(prompt)
        return 0

    python = PYTHON if PYTHON.exists() else Path(sys.executable)
    command = [
        str(python), str(REVIEW), prompt,
        "--model", args.model,
        "--effort", args.effort,
        "--project", str(project),
        "--no-dialog",
    ]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
