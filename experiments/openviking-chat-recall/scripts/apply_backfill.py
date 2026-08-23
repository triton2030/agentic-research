#!/usr/bin/env python3
"""Применение решений добора: модель судит, скрипт правит.

Разделение не косметическое. Провенанс уже один раз испортился ровно там, где
модель набирала якорь руками: переписанная по памяти ссылка выглядит
правдоподобно и проходит глазами. Поэтому модель возвращает только выбор —
судьбу записи и текст факта, — а адрес, путь и глубину ссылки подставляет
скрипт из проверенного входа.

    python3 apply_backfill.py [--dry] [<папка прогонов>]
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from collections import defaultdict

ART = "experiments/openviking-chat-recall/artifacts"
WIKI = f"{ART}/wiki-v1"
PREFIX = "../../../../../_ops/chat-recall"
TYPES = {"entity", "concept", "method", "comparison", "analysis"}
# Агент работает по-русски и естественно переводит служебное слово вердикта.
# Отвергать суждение из-за словаря — терять оплаченную работу на пустом месте:
# решение принято, названо иначе. Нормализуем вход, а не спорим с ним.
VERDICT = {
    "add": "add", "добавить": "add", "дополнить": "add",
    "new": "new", "новая": "new", "создать": "new", "новую": "new",
    "skip": "skip", "пропустить": "skip", "отказ": "skip", "пропуск": "skip",
}


def expected() -> dict[str, tuple[str, str]]:
    """Якорь -> (type записи, цитата). Единственный источник допустимых ключей."""
    found = {}
    for row in open(f"{ART}/coverage-gaps.tsv", encoding="utf-8"):
        name, line, kind, quote = row.rstrip("\n").split("\t", 3)
        found[f"{name}#L{line}"] = (kind, quote)
    return found


def decisions(runs: str, allowed: dict[str, tuple[str, str]]) -> tuple[list, list]:
    taken, refused = [], []
    for path in sorted(glob.glob(os.path.join(runs, "*.json"))):
        topic = os.path.basename(path)[:-5]
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            refused.append((topic, "—", "прогон не отдал JSON"))
            continue
        if not payload.get("ok") or not payload.get("response"):
            refused.append((topic, "—", f"прогон не принят: ok={payload.get('ok')}"))
            continue
        for raw in payload["response"].splitlines():
            if raw.count("\t") < 4:
                continue
            anchor, verdict, target, text, label = raw.split("\t", 4)
            anchor = anchor.strip().strip("`*")
            verdict = VERDICT.get(verdict.strip().strip("`*").lower(), verdict.strip())
            if anchor not in allowed:
                refused.append((topic, anchor, "якоря нет во входе"))
            elif verdict not in {"add", "new", "skip"}:
                refused.append((topic, anchor, f"неизвестная судьба {verdict!r}"))
            elif verdict == "add" and not os.path.exists(os.path.join(WIKI, target.strip())):
                refused.append((topic, anchor, f"страницы нет: {target.strip()}"))
            elif verdict == "new" and (target.count("|") != 2
                                       or target.split("/", 1)[0].strip() not in TYPES):
                refused.append((topic, anchor, f"плохое описание новой страницы: {target[:60]}"))
            elif not text.strip():
                refused.append((topic, anchor, "пустой текст"))
            else:
                taken.append((topic, anchor, verdict, target.strip(), text.strip(), label.strip()))
    return taken, refused


def link(anchor: str, label: str) -> str:
    return f"[{label or 'источник'}]({PREFIX}/{anchor})"


def add_to_page(path: str, bullet: str, source: str) -> None:
    text = open(path, encoding="utf-8").read()
    head, sep, tail = text.partition("\n## Источники")
    body = f"{head.rstrip()}\n{bullet}\n"
    open(path, "w", encoding="utf-8").write(body + sep + tail.rstrip("\n") + f"\n{source}\n")


def create_page(spec: str, topic: str, rows: list[tuple[str, str, str]]) -> str:
    slug, title, description = [part.strip() for part in spec.split("|", 2)]
    path = os.path.join(WIKI, slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    kind = slug.split("/", 1)[0]
    bullets = "\n".join(f"- {text} {link(anchor, label)}" for anchor, text, label in rows)
    sources = "\n".join(f"- {link(anchor, label)}" for anchor, _, label in rows)
    open(path, "w", encoding="utf-8").write(
        f"---\ntype: {kind}\ntitle: {title}\ndescription: {description}\ntopic: {topic}\n---\n"
        f"# {title}\n\n{rows[0][1]}\n\n{bullets}\n\n## Источники\n{sources}\n"
    )
    return path


def main(runs: str, dry: bool) -> int:
    allowed = expected()
    taken, refused = decisions(runs, allowed)
    seen = {anchor for _, anchor, *_ in taken}

    added = [row for row in taken if row[2] == "add"]
    fresh: dict[tuple[str, str], list] = defaultdict(list)
    skipped = [row for row in taken if row[2] == "skip"]
    for topic, anchor, verdict, target, text, label in taken:
        if verdict == "new":
            fresh[(topic, target)].append((anchor, text, label))

    print(f"решений принято: {len(taken)} | отвергнуто строк: {len(refused)}")
    print(f"  add {len(added)} | new {len(fresh)} страниц из "
          f"{sum(len(v) for v in fresh.values())} записей | skip {len(skipped)}")
    missing = sorted(set(allowed) - seen)
    print(f"записей без решения: {len(missing)}")
    for topic, anchor, why in refused[:15]:
        print(f"  отвергнуто {topic} {anchor}: {why}")
    if dry:
        return 0

    for _, anchor, _, target, text, label in added:
        add_to_page(os.path.join(WIKI, target), f"- {text} {link(anchor, label)}",
                    f"- {link(anchor, label)}")
    for (topic, spec), rows in fresh.items():
        create_page(spec, topic, rows)
    with open(f"{ART}/coverage-decisions.tsv", "w", encoding="utf-8") as out:
        for topic, anchor, verdict, target, text, label in taken:
            out.write(f"{anchor}\t{verdict}\t{target}\t{text}\n")
        for anchor in missing:
            out.write(f"{anchor}\tбез-решения\t—\t{allowed[anchor][1][:120]}\n")
    print(f"судьбы записаны -> {ART}/coverage-decisions.tsv")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry"]
    raise SystemExit(main(args[0] if args else "_workspace/ox-backfill/runs", "--dry" in sys.argv))
