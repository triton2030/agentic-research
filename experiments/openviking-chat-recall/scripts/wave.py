#!/usr/bin/env python3
"""Сверка волны: построено · запущено · принято — и разница между ними.

Класс ошибки, ради которого это написано: рукав слепой приёмки был построен и
не запущен. Он пролежал файлом на диске, пока три соседних считались, и
заметил я это случайно, сверяя состояние глазами. Глаза — не механизм.

Разница множеств отвечает на вопрос, который иначе никто не задаёт: какие
задания не дошли до прогона и какие прогоны не были приняты.

    python3 wave.py <папка заданий> <папка прогонов>

Возвращает 1, пока разница не пуста: отчёт волны на непустой разнице закрывать
нельзя.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys


def accepted(runs_dir: str) -> set[str]:
    """Единицы, чей прогон прошёл гейт и принёс непустой ответ."""
    done: set[str] = set()
    for path in glob.glob(os.path.join(runs_dir, "*.json")):
        try:
            payload = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        body = (payload.get("response") or "").strip()
        if payload.get("ok") and body and body not in {"(empty)", "(пусто)"}:
            done.add(os.path.basename(path)[:-5])
    return done


def strip_fence(text: str) -> str:
    """Снять обёртку из тройных кавычек вокруг содержимого файла.

    Контракт просит вернуть файл без markdown-обёртки, и большинство прогонов
    так и делают. Десять страниц из шестидесяти двух пришли обёрнутыми — форма
    ответа модели колеблется на границе, и спорить с этим дороже, чем снять
    обёртку одной строкой. Отвергать содержательно верный результат из-за
    трёх обратных кавычек — та же ошибка, что отвергать вердикт из-за языка.
    """
    body = text.strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[1] if "\n" in body else ""
        if body.rstrip().endswith("```"):
            body = body.rstrip()[:-3]
    return body.strip()


def expand_corpus_links(text: str, page_path: str, corpus: str) -> str:
    """Раскрыть служебный префикс `corpus:` в путь от страницы до разговоров.

    Модель путей не считает — ни одна константа не верна для всех корпусов
    сразу. Считает скрипт, ровно один раз и в одном месте.
    """
    relative = os.path.relpath(os.path.abspath(corpus), os.path.dirname(os.path.abspath(page_path)))
    text = text.replace("](corpus:", f"]({relative}/")
    # Старые прогоны написаны до появления метки и несут посчитанный самой
    # моделью путь. Он неверен всюду, кроме родного репо, но узнаётся по
    # хвосту — и тогда чиниться должен так же, скриптом, а не перепрогоном.
    return re.sub(r"\]\((?:\.\./)+_ops/chat-recall/", f"]({relative}/", text)


def skip_done(names: list[str], runs_dir: str | None, redo: bool) -> list[str]:
    """Отсеять единицы, чей прогон уже принят.

    Билдер, не помнящий сделанного, покупает одну работу дважды: `build_audit`
    выдал сорок заданий на двадцать три нужные темы, и семнадцать пришлось
    снимать руками. При бесплатной модели это стоило только времени — привычка
    от этого безопаснее не становится.
    """
    if redo or not runs_dir or not os.path.isdir(runs_dir):
        return names
    done = accepted(runs_dir)
    kept = [name for name in names if name not in done]
    if len(kept) != len(names):
        print(f"уже принято и пропущено: {len(names) - len(kept)}")
    return kept


def main(tasks_dir: str, runs_dir: str) -> int:
    built = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(tasks_dir, "*.txt"))}
    launched = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(runs_dir, "*.json"))}
    taken = accepted(runs_dir)

    never = sorted(built - launched)
    rejected = sorted(launched - taken)
    orphan = sorted(launched - built)

    print(f"построено {len(built)} · запущено {len(launched)} · принято {len(taken)}")
    if never:
        print(f"\nПОСТРОЕНО И НЕ ЗАПУЩЕНО: {len(never)}")
        for name in never:
            print(f"  {name}")
    if rejected:
        print(f"\nзапущено и не принято: {len(rejected)}")
        for name in rejected[:20]:
            print(f"  {name}")
    if orphan:
        print(f"\nпрогоны без задания: {len(orphan)}")
        for name in orphan[:10]:
            print(f"  {name}")
    if not (never or rejected or orphan):
        print("разница пуста — волну можно закрывать")
    return 1 if (never or rejected or orphan) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
