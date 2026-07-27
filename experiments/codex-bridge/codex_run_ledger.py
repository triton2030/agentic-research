"""Журнал прогона: run_dir, события, пульс, атомарная запись.

Единственный audit-владелец любого прогона моста — его `run_dir` в
`<проект>/_workspace/codex-artifacts/<run_id>/`. Общий `~/.codex` шарится с
Codex Desktop и audit surface НЕ является.

Модуль SDK-free: dry-run и валидация флагов не поднимают Codex-рантайм.
Раньше это жило в `codex_orchestrate_state.py` вместе с git-скоупом — имя
врало, потому что журналом пользуются все три входа, а не оркестратор.
Git-половина теперь в `codex_git_scope.py`.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from codex_orchestrate_contract import UsageError

BACKEND_DIR = Path(__file__).resolve().parent


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]


# Артефакты прогонов живут В ПРОЕКТЕ работы, не в backend-репо: иначе каждый
# вызов из чужого проекта сыплет мусор в codex-bridge/runs/. Это и рабочее
# место субагентов (заметки, архив, findings между кругами цикла).
PROJECT_ARTIFACTS_SUBDIR = Path("_workspace") / "codex-artifacts"


def prepare_run_dir(raw_run_dir: str | None, *, project: Path | None = None) -> tuple[str, Path]:
    """Свежий run_dir. Default — <project>/_workspace/codex-artifacts/<run_id>;
    без project (не должен случаться из штатных входов) — legacy backend runs/."""
    run_id = make_run_id()
    if raw_run_dir:
        run_dir = Path(raw_run_dir).expanduser().resolve()
    elif project is not None:
        run_dir = (project / PROJECT_ARTIFACTS_SUBDIR / run_id).resolve()
    else:
        run_dir = BACKEND_DIR / "runs" / run_id
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise UsageError(f"Run dir already exists; choose a fresh --run-dir: {run_dir}") from exc
    return run_id, run_dir



def _warn_stderr(message: str) -> None:
    # Журнал — телеметрия: его отказ не должен ронять флот; и само
    # предупреждение обязано пережить закрытый stderr (SIGPIPE/head).
    try:
        print(message, file=sys.stderr)
    except OSError:
        pass


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, data: Any) -> None:
    # run_dir может исчезнуть под ногами (чужой cleanup _workspace во время
    # прогона — реальный случай md-tools): пересоздаём и не поднимаем OSError,
    # иначе журнальная запись убивает флот и теряет готовые результаты воркеров.
    line = json.dumps(data, ensure_ascii=False) + "\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError as exc:
        _warn_stderr(f"[bridge] журнал недоступен ({path}): {exc}; запись пропущена")


def append_event(run_dir: Path, event: str, **data: Any) -> None:
    append_jsonl(run_dir / "events.jsonl", {"ts": utc_now(), "event": event, **data})


def append_heartbeat(
    run_dir: Path,
    started_monotonic: float,
    **data: Any,
) -> None:
    append_event(
        run_dir,
        "heartbeat",
        elapsed_sec=int(time.monotonic() - started_monotonic),
        **data,
    )


def start_heartbeat(
    run_dir: Path | None,
    heartbeat_sec: int,
    started_monotonic: float,
    *,
    thread_name: str = "codex-heartbeat",
    snapshot: Callable[[], dict[str, Any]] | None = None,
    **fields: Any,
) -> tuple[threading.Event, threading.Thread | None]:
    """Background ledger heartbeat shared by every bridge entrypoint.

    Returns (stop_event, thread). No-op (thread is None) when there is no run_dir
    or heartbeat is disabled, so callers can always .set()/.join() the pair.

    `snapshot` — необязательный колбэк живого состояния хода (см.
    `codex_progress.ProgressTracker.snapshot`): без него пульс говорит только
    «жив», с ним — чем ход занят и сколько секунд молчит.
    """
    stop = threading.Event()
    if run_dir is None or heartbeat_sec <= 0:
        return stop, None

    def loop() -> None:
        while not stop.wait(heartbeat_sec):
            extra = dict(fields)
            if snapshot is not None:
                try:
                    extra.update(snapshot())
                except Exception:  # noqa: BLE001 — пульс не роняет прогон
                    pass
            append_heartbeat(run_dir, started_monotonic, **extra)

    thread = threading.Thread(target=loop, name=thread_name, daemon=True)
    thread.start()
    return stop, thread
