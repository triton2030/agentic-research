"""Журнал прогона: run_dir, события, пульс, атомарная запись, финал.

Единственный audit-владелец любого прогона моста — его `run_dir` в
`<проект>/_workspace/work-artifacts/<дата-тема>/agents/codex-artifacts/<стамп>-<имя>/`.
Путь задаёт вызывающий через --run-dir. Общий `~/.codex` шарится с
Codex Desktop и audit surface НЕ является. Раз владелец один, здесь же лежит
и форма его артефактов: `prompt.md` (`render_prompt_document`) и финал прогона
(`RunResult`).

Модуль SDK-free: dry-run и валидация флагов не поднимают Codex-рантайм.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from cbcommon import UsageError

BACKEND_DIR = Path(__file__).resolve().parent


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]


RUN_DIR_REQUIRED_MESSAGE = (
    "Требуется --run-dir: укажи свежую папку прогона внутри рабочей папки работы: "
    "<project>/_workspace/work-artifacts/<дата-тема>/agents/codex-artifacts/<стамп>-<имя>."
)


def prepare_run_dir(raw_run_dir: str | None, *, project: Path | None = None) -> tuple[str, Path]:
    """Свежий явный run_dir; с проектом отсутствие пути — ошибка.
    Без project сохраняется backend runs/ для внутренних вызовов."""
    run_id = make_run_id()
    if raw_run_dir:
        run_dir = Path(raw_run_dir).expanduser().resolve()
    elif project is not None:
        raise UsageError(RUN_DIR_REQUIRED_MESSAGE)
    else:
        run_dir = BACKEND_DIR / "runs" / run_id
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise UsageError(f"Run dir already exists; choose a fresh --run-dir: {run_dir}") from exc
    return run_id, run_dir



def _warn_stderr(message: str) -> None:
    # Журнал — телеметрия: его отказ не должен ронять прогон; и само
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
    # иначе журнальная запись убивает прогон и теряет оплаченный результат.
    line = json.dumps(data, ensure_ascii=False) + "\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
    except OSError as exc:
        _warn_stderr(f"[bridge] журнал недоступен ({path}): {exc}; запись пропущена")


def append_event(run_dir: Path, event: str, **data: Any) -> None:
    append_jsonl(run_dir / "events.jsonl", {"ts": utc_now(), "event": event, **data})


def render_prompt_document(prompt: str, developer_instructions: str | None = None) -> str:
    """Полная ЭФФЕКТИВНАЯ инструкция хода одним текстом — для `prompt.md`.

    Роль и политика уходят в движок отдельным каналом (`developer_instructions`
    у thread_start/thread_resume), а не вклеиваются в реплику. Audit-владелец
    обязан показывать обе части: иначе по run_dir нельзя восстановить, что
    именно видел Codex, и аудит врал бы усечённой правдой.
    """
    if not developer_instructions:
        return prompt
    return (
        "===== DEVELOPER INSTRUCTIONS (канал thread_start) =====\n"
        f"{developer_instructions}\n\n"
        "===== USER PROMPT =====\n"
        f"{prompt}"
    )


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


@dataclass
class RunResult:
    """Финал прогона одним ходом: `result.json` + событие + compact stdout.

    Каждая ветка входа (dry-run, недоступный SDK, исключение, завершённый ход)
    собирала свой почти одинаковый payload и повторяла те же три вызова подряд;
    расхождения между копиями были вопросом времени, а не гипотезой. Здесь
    остаётся один `finish()`, а ветка отдаёт ровно то, чем отличается: статус,
    вердикт, свои поля и имя события.

    Форма payload фиксирована и одинакова у всех входов: постоянная голова
    (`base`), затем поля ветки (`extra`), затем общий хвост
    (`codex`/`paths`/`prompt_chars`). Блок `codex` снимается на момент финала —
    вход дописывает в него `thread_id` уже после старта треда.
    """

    run_dir: Path
    base: dict[str, Any]
    codex_runtime: dict[str, Any]
    paths: dict[str, str]
    prompt_chars: int
    compact_keys: tuple[str, ...]
    summary_stdout: bool = False

    def compact(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Проекция для stdout фонового прогона: контекстное окно оркестратора
        читает несколько ключей, полные данные остаются в run_dir."""
        return {key: payload[key] for key in self.compact_keys if key in payload}

    def finish(
        self,
        *,
        status: str,
        ok: bool,
        event: str,
        extra: dict[str, Any] | None = None,
        event_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            **self.base,
            "status": status,
            "ok": ok,
            **(extra or {}),
            "codex": dict(self.codex_runtime),
            "paths": self.paths,
            "prompt_chars": self.prompt_chars,
        }
        write_json(self.run_dir / "result.json", payload)
        append_event(self.run_dir, event, **(event_fields or {}))
        if self.summary_stdout:
            # Компактный stdout печатает владелец записи: иначе каждая ветка
            # каждого входа повторяла бы одну и ту же сериализацию.
            print(json.dumps(self.compact(payload), ensure_ascii=False, indent=2))
        return payload
