#!/usr/bin/env python3
"""Перенос якорей одного разговора со снимка на живой корпус — по тексту строки.

Файл `7756c5b8` получил две строки в шапке уже после снимка, по которому
собирался слой, и 38 якорей стали указывать на заголовок, пустую строку и
чужие реплики. Двигать их «на два» нельзя: сдвиг у шапки и у записей разный.
Соответствие берётся по совпадению текста строки, а каждая замена проверяется
обратным чтением живого файла.
"""
import collections, pathlib, re, subprocess, sys

MAVO = pathlib.Path("/Users/triton/Documents/My_projects/mavo-short2")
SNAP, SRC = "13738dd5", "2026-08-24-130300-claude-7756c5b8.md"
TOPICS = MAVO / "_ops/chat-recall/topics"
FLAT = pathlib.Path("experiments/openviking-chat-recall/artifacts/mavo-short2/flat")
write = "--write" in sys.argv

snap = subprocess.run(["git", "-C", str(MAVO), "show", f"{SNAP}:_ops/chat-recall/raw/{SRC}"],
                      capture_output=True, text=True).stdout.splitlines()
live = (MAVO / "_ops/chat-recall/raw" / SRC).read_text(encoding="utf-8").splitlines()
index = collections.defaultdict(list)
for i, l in enumerate(live, start=1):
    index[l].append(i)
mapping = {i: index[l][0] for i, l in enumerate(snap, start=1)
           if l.strip() and len(index.get(l, [])) == 1}

moved = skipped = 0
for path in sorted(TOPICS.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    def repl(m):
        global moved, skipped
        old = int(m.group(1))
        new = mapping.get(old)
        if new is None or live[new - 1] != snap[old - 1]:
            skipped += 1
            return m.group(0)
        moved += 1
        return f"{SRC}#L{new}"
    fixed = re.sub(re.escape(SRC) + r"#L(\d+)", repl, text)
    if fixed != text and write:
        path.write_text(fixed, encoding="utf-8")

flat_moved = 0
for path in sorted(FLAT.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    if f"source: {SRC}" not in text:
        continue
    def short(m):
        global flat_moved
        old = int(m.group(1))
        new = mapping.get(old)
        if new is None:
            return m.group(0)
        flat_moved += 1
        return f"L{new}"

    def span(m):
        # Только внутри квадратных скобок: `L` встречается и в обычной речи,
        # и слепая замена по всему тексту правила бы прозу владельца.
        return "[" + re.sub(r"\bL(\d+)\b", short, m.group(1)) + "]"
    fixed = re.sub(r"\[([^\]]*)\]", span, text)
    if fixed != text and write:
        path.write_text(fixed, encoding="utf-8")

print(f"{'ЗАПИСАНО' if write else 'вхолостую'}: якорей слоя перенесено {moved}, "
      f"пропущено {skipped}; коротких якорей материала {flat_moved}")
