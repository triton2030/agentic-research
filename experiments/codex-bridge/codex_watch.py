"""Витрина фоновых прогонов Codex: завершения будят, снимок отвечает по запросу.

Зачем модуль существует. `codex_progress.py` отвечает на два вопроса — «что
делает ЭТОТ прогон» (`digest`) и «кто из прогонов ещё жив» (`board`). Обоих не
хватило для третьего вопроса, который задал владелец: «когда каждый отдельный
агент заканчивает». Ни digest, ни board не дают per-worker разреза, а
`completed/total` из heartbeat не печатают вовсе, и машиночитаемого выхода у них
нет. Поэтому здесь свой читатель журнала, а не обёртка над сводкой.

Два режима, и они отвечают на разные вопросы:

- `watch` — команда для нативного `Monitor`. Каждая строка stdout становится
  нотификацией: одна строка на завершившегося агента, по любой причине. Молчит,
  пока никто не кончился.
- `look` — одноразовый снимок по всем живым агентам, по запросу владельца
  «глянь, над чем они там». Печатает и выходит.

Три свойства, купленные ценой кода, и каждое лечит известный отказ:

1. **Читаем по байтовому offset.** `events.jsonl` строго append-only
   (`codex_run_ledger.append_jsonl`), поэтому прирост даёт каждое событие ровно
   один раз — без дублей и без повторного разбора мегабайтного журнала.
2. **Сверяем стартовавших с отметившимися.** `worker_done` пишется в `except`,
   а не в `finally`: Ctrl-C, отмена и SIGKILL не оставляют записи. Значит
   «нет worker_done» не доказывает «работает», и на закрытии прогона каждый
   несошедшийся агент получает свою строку.
3. **Молчание не считается успехом.** Любой отказ самого наблюдателя —
   пропавший каталог, нечитаемый журнал, потолок по времени — печатается
   строкой. Тихо умереть он не имеет права: тишина здесь означает ровно одно —
   «идёт и не кончилось».

Стандартная библиотека и ничего больше: наблюдатель обязан пережить окружение,
в котором сам мост уже сломан.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Iterator

POLL_SEC = 20
MAX_HOURS = 6
DETAIL_LIMIT = 60

# Шаги воркера считаем по границам завершённых item-ов: `item/started` без пары
# посчитал бы незаконченную работу дважды.
STEP_METHOD = "item/completed"
FAILURE_METHODS = frozenset({"error", "turn/failed"})


def _short(text: Any, limit: int = DETAIL_LIMIT) -> str:
    value = " ".join(str(text or "").split())
    return value[:limit] if len(value) <= limit else value[: limit - 1] + "…"


def _dur(seconds: float) -> str:
    seconds = int(max(seconds, 0))
    if seconds < 60:
        return f"{seconds}с"
    if seconds < 3600:
        return f"{seconds // 60}м"
    return f"{seconds // 3600}ч{(seconds % 3600) // 60:02d}м"


def _ts(value: Any) -> float:
    """ISO-8601 с точностью до секунды → epoch. Мусор не роняет наблюдателя."""
    try:
        from datetime import datetime

        return datetime.fromisoformat(str(value)).timestamp()
    except Exception:  # noqa: BLE001
        return 0.0


def emit(line: str) -> None:
    """Одна строка = одна нотификация. Без flush она осядет в буфере пайпа."""
    print(line, flush=True)


class Journal:
    """Приростное чтение append-only журнала по байтовому offset."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.offset = 0

    def new_events(self) -> Iterator[dict[str, Any]]:
        if not self.path.is_file():
            return
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                handle.seek(self.offset)
                chunk = handle.read()
                # Хвостовая неполная строка: писатель мог не дописать её в этот
                # момент. Оставляем её следующему кругу, offset не двигаем.
                cut = chunk.rfind("\n")
                if cut == -1:
                    return
                self.offset += len(chunk[: cut + 1].encode("utf-8"))
                body = chunk[: cut + 1]
        except OSError as err:
            emit(f"НАБЛЮДЕНИЕ СЛОМАНО: журнал не читается — {err}")
            return
        for raw in body.splitlines():
            try:
                yield json.loads(raw)
            except Exception:  # noqa: BLE001
                continue


class Run:
    """Состояние одного прогона, собранное только из его журнала."""

    def __init__(self, run_dir: Path) -> None:
        self.dir = run_dir
        self.journal = Journal(run_dir / "events.jsonl")
        self.started: dict[str, float] = {}
        self.done: set[str] = set()
        self.steps: dict[str, int] = {}
        self.last_seen: dict[str, float] = {}
        self.last_kind: dict[str, str] = {}
        self.run_start = 0.0
        self.last_ts = 0.0
        self.finished = False

    @property
    def live(self) -> list[str]:
        return [wid for wid in self.started if wid not in self.done]

    def absorb(self, event: dict[str, Any]) -> Iterator[str]:
        """Событие журнала → ноль или одна строка витрины."""
        kind = event.get("event")
        stamp = _ts(event.get("ts"))
        if stamp:
            self.last_ts = stamp
            if not self.run_start:
                self.run_start = stamp

        if kind == "worker_start":
            self.started[str(event.get("id"))] = stamp
            return
        if kind == "worker_done":
            wid = str(event.get("id"))
            self.done.add(wid)
            status = event.get("worker_status") or "?"
            ms = event.get("duration_ms")
            span = _dur(ms / 1000) if isinstance(ms, (int, float)) else "?"
            mark = "OK" if status == "completed" else status.upper()
            yield f"{mark} {wid} · {span} · {self.steps.get(wid, 0)}ш"
            return
        if kind == "codex":
            worker = str(event.get("worker") or "")
            if stamp:
                self.last_seen[worker] = stamp
            if event.get("kind"):
                self.last_kind[worker] = str(event["kind"])
            if event.get("method") == STEP_METHOD:
                self.steps[worker] = self.steps.get(worker, 0) + 1
            elif event.get("method") in FAILURE_METHODS:
                who = f"{worker} · " if worker else ""
                yield f"СБОЙ {who}{_short(event.get('detail') or event['method'])}"
            return
        if kind == "done":
            self.finished = True

    def closing_lines(self) -> Iterator[str]:
        """Прогон кончился — договорить то, чего журнал не сказал сам."""
        for wid in self.live:
            # `worker_done` живёт в `except`, а не в `finally`: убитый воркер
            # уходит молча. Без этой сверки он выглядел бы вечно работающим.
            began = self.started.get(wid) or self.last_ts
            age = (self.last_ts or time.time()) - began
            yield f"ПРОПАЛ {wid} · без записи о завершении · шёл {_dur(age)}"

        result = self.dir / "result.json"
        if not result.is_file():
            yield f"КОНЕЦ {self.dir.name} · без result.json"
            return
        try:
            data = json.loads(result.read_text(encoding="utf-8"))
        except Exception as err:  # noqa: BLE001
            yield f"КОНЕЦ {self.dir.name} · result.json нечитаем — {err}"
            return
        state = "OK" if data.get("ok") else "ПРОВАЛ"
        span = _dur(self.last_ts - self.run_start) if self.run_start else "?"
        if self.started:
            good = sum(1 for wid in self.started if wid in self.done)
            yield f"{state} волна {self.dir.name} · {good}/{len(self.started)} · {span}"
        else:
            # Одиночный прогон: воркеров нет, финиш прогона и есть финиш агента.
            steps = sum(self.steps.values())
            yield f"{state} {self.dir.name} · {span} · {steps}ш"


def watch(run_dir: Path, poll: int, max_hours: float) -> int:
    if not run_dir.is_dir():
        emit(f"НАБЛЮДЕНИЕ НЕ ВСТАЛО: нет каталога {run_dir}")
        return 2

    run = Run(run_dir)
    deadline = time.time() + max_hours * 3600
    while True:
        for event in run.journal.new_events():
            for line in run.absorb(event):
                emit(line)

        if run.finished or (run_dir / "result.json").is_file():
            # Ещё круг чтения: `done` и `result.json` могли обогнать хвост
            # журнала, а недосчитанный `worker_done` дал бы ложный «ПРОПАЛ».
            time.sleep(1)
            for event in run.journal.new_events():
                for line in run.absorb(event):
                    emit(line)
            for line in run.closing_lines():
                emit(line)
            return 0

        if time.time() > deadline:
            emit(f"НАБЛЮДЕНИЕ ВЫШЛО ПО ПОТОЛКУ: {run_dir.name} · {max_hours}ч")
            return 0
        time.sleep(poll)


def look(project: Path, limit: int = 12) -> int:
    """Снимок по запросу: над чем сейчас работает каждый живой агент."""
    root = project / "_workspace" / "codex-artifacts"
    if not root.is_dir():
        emit(f"прогонов нет: {root} не существует")
        return 0

    now = time.time()
    shown = 0
    for run_dir in sorted((p for p in root.iterdir() if p.is_dir()), reverse=True):
        # Каталог артефактов копит и чужие папки. Прогон опознаём по манифесту:
        # ledger пишет его первым, поэтому он есть даже у прогона без единого
        # события. Без этого фильтра мусорная папка выглядит вечно живой.
        if not (run_dir / "manifest.json").is_file():
            continue
        if (run_dir / "result.json").is_file():
            continue
        run = Run(run_dir)
        for event in run.journal.new_events():
            list(run.absorb(event))

        live = run.live
        if not live and run.started:
            continue
        span = _dur(now - run.run_start) if run.run_start else "?"
        emit(f"{run_dir.name} · идёт {span} · живых {len(live) or 1}")
        # Одиночный прогон воркеров не заводит; его агент — сам прогон.
        for wid in live or [""]:
            quiet = _dur(now - run.last_seen[wid]) if run.last_seen.get(wid) else "?"
            emit(
                f"  {wid or 'одиночный'} · {run.steps.get(wid, 0)}ш"
                f" · тихо {quiet} · {run.last_kind.get(wid, '?')}"
            )
        shown += 1
        if shown >= limit:
            break

    if not shown:
        emit(f"живых прогонов нет: {root}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Витрина Codex-прогонов: watch — поток завершений для Monitor,"
        " look — снимок живых агентов по запросу."
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    watcher = sub.add_parser("watch", help="поток строк о завершении агентов")
    watcher.add_argument("run_dir")
    watcher.add_argument("--poll", type=int, default=POLL_SEC)
    watcher.add_argument("--max-hours", type=float, default=MAX_HOURS)

    snapshot = sub.add_parser("look", help="снимок живых агентов и их шагов")
    snapshot.add_argument("project", nargs="?", default=".")

    args = parser.parse_args(argv)
    if args.mode == "watch":
        return watch(Path(args.run_dir), args.poll, args.max_hours)
    return look(Path(args.project))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        emit("НАБЛЮДЕНИЕ ПРЕРВАНО вручную")
        sys.exit(130)
    except Exception as err:  # noqa: BLE001
        # Наблюдатель, упавший молча, неотличим от наблюдателя, которому нечего
        # сказать. Стек уходит в stderr, а Monitor stderr не показывает вовсе.
        emit(f"НАБЛЮДЕНИЕ УПАЛО: {type(err).__name__}: {err}")
        sys.exit(1)
