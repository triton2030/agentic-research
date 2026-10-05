#!/usr/bin/env python3
"""Запуск прогона Codex одной короткой командой с витриной шагов в той же карточке.

Зачем модуль существует. Владелец смотрит на прогон в панели фоновых задач
приложения: карточка показывает команду и её stdout. Когда команда — это
многострочное задание плюс subshell плюс `watch`, карточка забита текстом
задания, а ход работы теряется внизу. Здесь команда короткая (`codex_launch.py
review --prompt-file …`), а stdout карточки — только витрина: заголовок с
заданием, строка на каждый шаг Codex, финал.

Что делает: принимает свежий `RUN_DIR` через обязательный `--run-dir`
(`<project>/_workspace/work-artifacts/<дата-тема>/agents/codex-artifacts/<стамп>-<имя>`),
запускает вход моста `codex_review.py` отдельным процессом с
выводом в `<RUN_DIR>.launch.log` и держит в своём stdout `codex_watch.py watch
RUN_DIR --pulse`. Завершается вместе с прогоном — одно уведомление агенту;
остановка карточки прерывает прогон штатно (interrupt), а не оставляет его
сиротой. Канон результата — `result.json` в `RUN_DIR`; сводка моста — в
`launch.log`.

Вход один — `agent`: Codex как субагент, роль и границы задаёт задание.
`review` — прежнее имя того же входа, оставлено для старых вызовов.

Задание берётся из `--prompt-file` (файл, не аргумент: длинный текст в
командной строке и есть мусор в карточке). Всё после `--` уходит входу моста
как есть (`--model`, `--effort`, `--mode`, `--dialog`, `--continue` …).
"""
from __future__ import annotations

import argparse
import signal
import subprocess
import sys
from pathlib import Path

from codex_run_ledger import RUN_DIR_REQUIRED_MESSAGE

HERE = Path(__file__).resolve().parent
ENTRIES = {
    "agent": "codex_review.py",
    "review": "codex_review.py",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("entry", choices=sorted(ENTRIES))
    parser.add_argument("--name", required=True, help="суффикс RUN_DIR и подпись карточки: роль-суть, без пробелов")
    parser.add_argument("--prompt-file", help="файл с заданием; без него — только режимы, которым задание не нужно (--mode diff/review)")
    parser.add_argument("--project", default=".", help="корень проекта (default cwd)")
    parser.add_argument("--run-dir", help="обязательный свежий RUN_DIR внутри рабочей папки работы")
    parser.add_argument("--poll", type=int, default=10, help="шаг опроса журнала витриной, с")
    parser.epilog = "после `--` — аргументы входа моста как есть"
    args, rest = parser.parse_known_args()

    project = Path(args.project).expanduser().resolve()
    if rest and rest[0] == "--":
        rest = rest[1:]
    if "--run-dir" in rest:
        print("--run-dir задаётся launcher'у, не входу моста: иначе витрина смотрит не туда", file=sys.stderr)
        return 2
    if not args.run_dir:
        print(RUN_DIR_REQUIRED_MESSAGE, file=sys.stderr)
        return 2
    run_dir = Path(args.run_dir).expanduser().resolve()
    if run_dir.exists():
        print(f"RUN_DIR уже существует: {run_dir}", file=sys.stderr)
        return 2
    run_dir.parent.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, str(HERE / ENTRIES[args.entry])]
    if args.prompt_file:
        cmd.append(Path(args.prompt_file).read_text(encoding="utf-8"))
    cmd += ["--project", str(project), "--run-dir", str(run_dir), "--summary-stdout", *rest]

    log_path = Path(f"{run_dir}.launch.log")
    with log_path.open("wb") as log:
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=str(project))
    print(f"RUN_DIR={run_dir}\nlaunch.log={log_path}  pid={proc.pid}", flush=True)

    # Остановка карточки останавливает и прогон — сам launcher, а не харнесс:
    # SIGTERM/SIGINT пересылаются входу моста, тот просит у движка штатный
    # interrupt и пишет provisional result.json (аудит Codex 2026-09-18:
    # надеяться на «харнесс гасит всё дерево» нельзя).
    def _forward(signum, _frame):  # noqa: ANN001
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, _forward)

    watch_rc = 1
    rc: int | None = None
    try:
        # Витрина получает pid прогона: умер прогон без result.json (rescue-путь
        # волны) — витрина закрывается сама, а не ждёт шесть часов (аудит Astra
        # 2026-09-19).
        watch = subprocess.Popen(
            [sys.executable, str(HERE / "codex_watch.py"), "watch", str(run_dir),
             "--pulse", "--poll", str(args.poll), "--pid", str(proc.pid)],
            cwd=str(project),
        )
        while True:
            try:
                watch_rc = watch.wait(timeout=5)
                break
            except subprocess.TimeoutExpired:
                if proc.poll() is not None:
                    # Прогон кончился, витрина дочитывает; дольше двух опросов
                    # ей нечего ждать.
                    try:
                        watch_rc = watch.wait(timeout=2 * args.poll + 5)
                    except subprocess.TimeoutExpired:
                        watch.terminate()
                        watch_rc = watch.wait(timeout=10)
                    break
        if watch_rc == 2:
            # Витрина не встала: каталог прогона не появился — запуск сорвался
            # до старта. Ждём недолго и гасим.
            try:
                rc = proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                print("прогон не встал за 30с после отказа витрины — прерываю", flush=True)
                proc.send_signal(signal.SIGTERM)
                rc = proc.wait(timeout=60)
        else:
            # Витрина закрылась раньше прогона (потолок часов) — поломка окна
            # не останавливает работу: пишущий агент, убитый посреди правки,
            # оставляет её недоделанной. Остановка — только явным TaskStop.
            if proc.poll() is None:
                print("витрина закрылась, прогон идёт — жду его завершения", flush=True)
            rc = proc.wait()
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
        # Витрина упала исключением, а прогон уже кончился — код берём у него
        # (замечание Codex 2026-09-19: иначе `rc` не инициализирован).
        rc = proc.returncode if rc is None else rc
    if rc != 0:
        print(f"вход моста завершился с кодом {rc} — читай {log_path}", flush=True)
    return rc or watch_rc


if __name__ == "__main__":
    raise SystemExit(main())
