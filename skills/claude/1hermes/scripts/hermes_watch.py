#!/usr/bin/env python3
"""Витрина прогонов Hermes: завершения будят, снимок отвечает по запросу.

Зачем модуль существует. Обёртка блокирует до терминального результата, а
`~/.hermes/logs/agent.log` общий на всю установку и `run_id` в него не попадает
ни разу — связка по времени даёт единственного кандидата меньше чем в половине
случаев, связка по началу промпта бесполезна (на 880 прогонов всего 92 разных
начала). Значит промежуточного наблюдения за содержанием прогона нет и не будет.
Зато у каждого прогона есть адрес на диске, и его хватает на три факта, которые
владелец и просил: когда начался, когда кончился и чем.

Два режима:

- `watch` — команда для нативного `Monitor`: одна строка на каждый прогон,
  который кончился. По любой причине.
- `look` — одноразовый снимок живых прогонов по запросу владельца.

Что здесь принципиально и почему:

1. **Смерть — тоже завершение.** `_emit` пишет `result.json` атомарным rename,
   но ловит только `Exception`: SIGKILL, отмена и смерть родительской сессии
   оставляют каталог незакрытым навсегда. В корпусе таких 29 из 880 (3.3%) —
   это не теория. Признак смерти один: pid из `run_id` больше не живёт.
2. **Pid проверяется не только на живость.** Пространство pid заворачивается за
   сутки (6 повторов на 880 прогонов), поэтому живой pid засчитывается, только
   если это действительно наша обёртка.
3. **Имя модели в строку не идёт.** Product Frame `1hermes`, тайбрейкер 1:
   «модель и usage не оглашаются». Владелец просил число вызванных инструментов
   и длительность — их и печатаем.
4. **Молчание не считается успехом.** Любой отказ наблюдателя печатается
   строкой: `Monitor` не показывает stderr вовсе, и тихо упавший наблюдатель
   неотличим от наблюдателя, которому нечего сказать.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUNS_DIR = Path.home() / ".hermes" / "1hermes-runs"
POLL_SEC = 20
MAX_HOURS = 6
# Прогон без живого pid и без результата объявляем мёртвым не сразу: между
# выходом процесса и появлением result.json есть узкое окно.
DEATH_CONFIRMATIONS = 2
# Волна кончилась, когда живых не осталось; лишний круг страхует от паузы
# между запусками соседних прогонов.
IDLE_ROUNDS_TO_EXIT = 3


def emit(line: str) -> None:
    print(line, flush=True)


def _dur(seconds: float) -> str:
    seconds = int(max(seconds, 0))
    if seconds < 60:
        return f"{seconds}с"
    if seconds < 3600:
        return f"{seconds // 60}м"
    return f"{seconds // 3600}ч{(seconds % 3600) // 60:02d}м"


def _opened_at(run: Path) -> float:
    """`opened_at` манифеста → epoch; иначе mtime самого манифеста."""
    manifest = run / "manifest.json"
    try:
        raw = json.loads(manifest.read_text(encoding="utf-8")).get("opened_at")
        return datetime.strptime(str(raw), "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc
        ).timestamp()
    except Exception:  # noqa: BLE001
        try:
            return manifest.stat().st_mtime
        except OSError:
            return 0.0


def _pid_alive(run_id: str) -> bool:
    """Наша ли обёртка держит pid из `run_id`.

    Живого pid мало: за сутки номера заворачиваются, и чужой процесс выдал бы
    мёртвый прогон за живой. Поэтому сверяем командную строку.
    """
    parts = run_id.split("-")
    if len(parts) < 2 or not parts[1].isdigit():
        return False
    pid = int(parts[1])
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, ValueError):
        return False
    except PermissionError:
        return True
    try:
        out = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout
    except Exception:  # noqa: BLE001
        return True  # не смогли опровергнуть — живым считать безопаснее
    return "hermes_advisor" in out


def _finish_line(run: Path) -> str:
    began = _opened_at(run)
    result = run / "result.json"
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
    except Exception as err:  # noqa: BLE001
        return f"КОНЕЦ {run.name} · result.json нечитаем — {err}"

    # Времени завершения в квитанции нет вовсе — только метка файла.
    span = _dur(result.stat().st_mtime - began) if began else "?"
    session = data.get("session") or {}
    steps = session.get("message_count")
    tools = session.get("tool_call_count")
    detail = f" · {steps}ш" if steps is not None else ""
    detail += f" · {tools} инстр" if tools is not None else ""
    if data.get("ok"):
        return f"OK {run.name} · {span}{detail}"
    reason = data.get("error") or f"exit={data.get('exit_code')}"
    return f"ПРОВАЛ {run.name} · {span}{detail} · {reason}"


def _runs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    # Каталог опознаём по манифесту: он пишется до первого платного вызова,
    # поэтому есть даже у прогона, который умер сразу.
    return [p for p in root.iterdir() if p.is_dir() and (p / "manifest.json").is_file()]


def watch(root: Path, poll: int, max_hours: float) -> int:
    if not root.is_dir():
        emit(f"НАБЛЮДЕНИЕ НЕ ВСТАЛО: нет каталога {root}")
        return 2

    # Всё, что уже закрыто к моменту старта, — чужая история: о ней не сообщаем.
    reported = {run.name for run in _runs(root) if (run / "result.json").is_file()}
    suspect: dict[str, int] = {}
    deadline = time.time() + max_hours * 3600
    idle_rounds = 0
    seen_any = False

    while True:
        live = 0
        for run in _runs(root):
            if run.name in reported:
                continue
            if (run / "result.json").is_file():
                reported.add(run.name)
                suspect.pop(run.name, None)
                seen_any = True
                emit(_finish_line(run))
                continue
            if _pid_alive(run.name):
                suspect.pop(run.name, None)
                live += 1
                continue
            hits = suspect.get(run.name, 0) + 1
            suspect[run.name] = hits
            if hits >= DEATH_CONFIRMATIONS:
                reported.add(run.name)
                seen_any = True
                began = _opened_at(run)
                span = _dur(time.time() - began) if began else "?"
                emit(f"УМЕР {run.name} · без результата · шёл {span}")
            else:
                live += 1

        if live:
            idle_rounds = 0
        else:
            idle_rounds += 1
            if seen_any and idle_rounds >= IDLE_ROUNDS_TO_EXIT:
                emit(f"ВСЁ · прогонов Hermes больше не идёт · закрыто {len(reported)}")
                return 0

        if time.time() > deadline:
            emit(f"НАБЛЮДЕНИЕ ВЫШЛО ПО ПОТОЛКУ: {max_hours}ч · живых {live}")
            return 0
        time.sleep(poll)


def look(root: Path) -> int:
    now = time.time()
    live = []
    for run in _runs(root):
        if (run / "result.json").is_file():
            continue
        began = _opened_at(run)
        live.append((began or now, run))

    if not live:
        emit(f"живых прогонов Hermes нет: {root}")
        return 0

    emit(f"живых прогонов Hermes: {len(live)}")
    for began, run in sorted(live):
        state = "идёт" if _pid_alive(run.name) else "МЁРТВ"
        # Содержания прогона на диске нет: обёртка не пишет промежуточных
        # шагов, а общий agent.log к run_id не привязывается. Честный максимум —
        # жив ли он и сколько идёт.
        emit(f"  {run.name} · {state} {_dur(now - began)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Витрина прогонов Hermes: watch — поток завершений для Monitor,"
        " look — снимок живых прогонов по запросу."
    )
    parser.add_argument("mode", choices=("watch", "look"))
    parser.add_argument("--runs-dir", default=str(RUNS_DIR))
    parser.add_argument("--poll", type=int, default=POLL_SEC)
    parser.add_argument("--max-hours", type=float, default=MAX_HOURS)
    args = parser.parse_args(argv)

    root = Path(args.runs_dir).expanduser()
    if args.mode == "look":
        return look(root)
    return watch(root, args.poll, args.max_hours)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        emit("НАБЛЮДЕНИЕ ПРЕРВАНО вручную")
        sys.exit(130)
    except Exception as err:  # noqa: BLE001
        emit(f"НАБЛЮДЕНИЕ УПАЛО: {type(err).__name__}: {err}")
        sys.exit(1)
