#!/usr/bin/env python3
"""Живая доска волны: что собрано, что в работе, жив ли маршрут.

Витрина событий и доска решают разные задачи, и подменять одну другой дорого.
Витрина будит агента строкой на каждое завершение — значит её молчание стоит
токенов ноль, но и означает оно ровно ничего: прогон идёт, повис или маршрут
лёг, панель одинаково пуста. Замер 2026-08-25: витрина волны провисела перед
владельцем одиннадцать минут с надписью «No output yet», пока три прогона
работали.

Доска — обратное: печатает кадр каждую минуту в фоновую задачу, владелец видит
жизнь непрерывно, а в контекст агента это не идёт вовсе.

    python3 wave_board.py <задания> <прогоны> <принятое> [--watch 60] [--events]

`--events` — режим витрины: строка только на смену состава собранного, чтобы
разбудить агента полезной новостью, а не тишиной.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wave_ready import cyr_share, run_verdict

RECEIPTS = os.path.expanduser("~/.hermes/1hermes-runs")
BAR = 20
FRESH_MIN = 60


def elapsed_minutes(spec: str) -> int:
    """`ps etime` понимает четыре формы: MM:SS, HH:MM:SS, D-HH:MM:SS и пустую."""
    spec = spec.strip()
    if not spec:
        return 0
    days, _, rest = spec.rpartition("-")
    parts = [int(p) for p in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    hours, minutes, _ = parts
    return (int(days) if days else 0) * 1440 + hours * 60 + minutes


def running(runs: str) -> dict[str, int]:
    """Тема -> сколько минут идёт. Кто пишет в файл, тот его и держит открытым."""
    files = glob.glob(os.path.join(runs, "*.json"))
    if not files:
        return {}
    try:
        out = subprocess.run(["lsof", "-Fpn", "--", *files],
                             capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return {}
    pid, live = None, {}
    for line in out.splitlines():
        if line.startswith("p"):
            pid = line[1:]
        elif line.startswith("n") and pid:
            theme = os.path.basename(line[1:])[:-5]
            age = subprocess.run(["ps", "-o", "etime=", "-p", pid],
                                 capture_output=True, text=True).stdout
            live[theme] = max(live.get(theme, 0), elapsed_minutes(age))
    return live


def route_health() -> str:
    """Здоровье маршрута по квитанциям часа: пустой ответ — тоже исход."""
    answers = empty = 0
    last = None
    now = time.time()
    for d in glob.glob(os.path.join(RECEIPTS, "*", "result.json")):
        try:
            age = now - os.path.getmtime(d)
        except OSError:
            continue
        if age > FRESH_MIN * 60:
            continue
        try:
            payload = json.load(open(d, encoding="utf-8"))
        except Exception:
            empty += 1
            continue
        if payload.get("ok") and len(payload.get("response") or "") > 500:
            answers += 1
            last = age if last is None else min(last, age)
        else:
            empty += 1
    tail = f" · последний {int(last // 60)}м назад" if last is not None else ""
    return f"маршрут за час: ответов {answers} · впустую {empty}{tail}"


def circle() -> str:
    out = subprocess.run(["pgrep", "-f", "grind.sh"], capture_output=True, text=True).stdout
    if not out.strip():
        return "круг НЕ ИДЁТ"
    pid = out.split()[0]
    age = subprocess.run(["ps", "-o", "etime=", "-p", pid],
                         capture_output=True, text=True).stdout
    return f"круг идёт {elapsed_minutes(age)}м"


def state(tasks: str, runs: str, good: str) -> tuple[list[str], dict[str, str]]:
    wanted = sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(tasks, "*.txt")))
    ready: dict[str, str] = {}
    for folder in (good, runs):
        for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
            payload, _ = run_verdict(path)
            if payload is None:
                continue
            body = payload["response"]
            ready[os.path.basename(path)[:-5]] = f"{len(body) // 1000}к · {cyr_share(body):.0%} рус"
    return wanted, ready


def frame(tasks: str, runs: str, good: str) -> str:
    wanted, ready = state(tasks, runs, good)
    done = [t for t in wanted if t in ready]
    live = running(runs)
    lines = [f"══ {time.strftime('%H:%M')} · собрано {len(done)} из {len(wanted)} · {circle()} ══"]
    filled = round(BAR * len(done) / len(wanted)) if wanted else 0
    lines.append("█" * filled + "░" * (BAR - filled))
    for theme in sorted(live, key=lambda t: -live[t]):
        if theme in ready:
            continue
        mark = "⚠" if live[theme] >= FRESH_MIN else "▶"
        lines.append(f"{mark} {theme:<20}{live[theme]}м")
    waiting = [t for t in wanted if t not in ready and t not in live]
    if waiting:
        lines.append("… ждут: " + " · ".join(waiting))
    lines.append(route_health())
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    tasks, runs, good = args[0], args[1], args[2]
    events = "--events" in argv
    step = next((int(a.split("=")[1]) for a in argv if a.startswith("--watch=")), None)
    if "--watch" in argv and step is None:
        step = int(argv[argv.index("--watch") + 1])
    if not events and step is None:
        print(frame(tasks, runs, good), flush=True)
        return 0
    seen: set[str] = set()
    while True:
        if events:
            wanted, ready = state(tasks, runs, good)
            fresh = [t for t in wanted if t in ready and t not in seen]
            if seen:  # первый проход только знакомится с уже собранным
                for theme in fresh:
                    left = len([t for t in wanted if t not in ready])
                    print(f"✓ {theme} · {ready[theme]} · осталось {left}", flush=True)
            seen |= set(t for t in wanted if t in ready)
            if len(seen) == len(wanted):
                print("ВСЕ ТЕМЫ СОБРАНЫ", flush=True)
                return 0
        else:
            print(frame(tasks, runs, good), flush=True)
        time.sleep(step or 60)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
