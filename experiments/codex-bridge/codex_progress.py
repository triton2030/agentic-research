"""Живой прогресс Codex-хода: поток нотификаций → ledger + снимок для heartbeat.

Зачем модуль существует. `Thread.run()` в SDK — это сахар над
`Thread.turn()` + `TurnHandle.run()`, а тот по своей же docstring
«consume the turn stream and return its completed result»: поток из 65 типов
нотификаций уже течёт через наш процесс, и `run()` выбрасывает его целиком,
оставляя только финальный `TurnResult`. Из-за этого heartbeat мог сказать
«жив», но никогда «движется» — многочасовой прогон был неотличим от
зависшего.

Здесь поток проходит через tee: каждая нотификация попадает в ledger (в
сжатой проекции) и в счётчики, а сам поток дальше отдаётся штатному
сборщику SDK — то есть `TurnResult` собирается ровно тем же кодом, что и
раньше. Приёмка прогона не меняется.

Проекция намеренно защитная: схема движка дрейфует под запиненным SDK (см.
`codex_sdk_compat.py`), поэтому поля читаются через `getattr`, а любая ошибка
журналирования гасится — журнал не имеет права уронить оплаченный ход.
"""
from __future__ import annotations

import threading
import time
from typing import Any, AsyncIterator, Callable, Iterator

from codex_run_ledger import append_event, append_jsonl, utc_now, write_json

# Нотификации-дельты идут потоком токенов: в ledger они дали бы мегабайты шума,
# поэтому их только считаем. В журнал пишем границы шагов и события, меняющие
# картину прогона.
LEDGER_METHODS = frozenset(
    {
        "item/started",
        "item/completed",
        "error",
        "turn/failed",
        "account/rateLimits/updated",
    }
)

DETAIL_LIMIT = 200


def _short(text: Any, limit: int = DETAIL_LIMIT) -> str:
    value = " ".join(str(text or "").split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _item_projection(item: Any) -> tuple[str, str]:
    """(kind, detail) для элемента хода. Схему не валидируем — читаем терпимо."""
    node = getattr(item, "root", item)
    kind = str(getattr(node, "type", "") or "item")

    if kind == "commandExecution":
        return kind, _short(getattr(node, "command", ""))
    if kind == "fileChange":
        paths = [
            str(getattr(change, "path", "?"))
            for change in (getattr(node, "changes", None) or [])
        ]
        return kind, _short(", ".join(paths))
    if kind == "plan":
        return kind, _short(getattr(node, "text", ""))
    if kind == "webSearch":
        return kind, _short(getattr(node, "query", ""))
    if kind == "mcpToolCall":
        server = getattr(node, "server", "") or ""
        tool = getattr(node, "tool", "") or ""
        return kind, _short(f"{server}/{tool}".strip("/"))
    if kind in {"agentMessage", "reasoning", "userMessage"}:
        text = getattr(node, "text", "") or ""
        return kind, f"{len(text)} симв."
    return kind, ""


class ProgressTracker:
    """Счётчики и последняя активность хода. Читается heartbeat-потоком."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._steps = 0
        self._by_kind: dict[str, int] = {}
        self._last_kind: str | None = None
        self._last_detail: str = ""
        self._last_monotonic = time.monotonic()
        self._deltas = 0
        self._errors = 0

    def observe(self, event: Any) -> dict[str, Any] | None:
        """Учесть нотификацию. Вернуть запись для ledger или None (шум)."""
        method = str(getattr(event, "method", "") or "")
        payload = getattr(event, "payload", None)

        if method.endswith("Delta") or method.endswith("delta"):
            with self._lock:
                self._deltas += 1
                self._last_monotonic = time.monotonic()
            return None

        if method not in LEDGER_METHODS:
            return None

        record: dict[str, Any] = {"method": method}

        if method in {"item/started", "item/completed"}:
            kind, detail = _item_projection(getattr(payload, "item", None))
            record["kind"] = kind
            if detail:
                record["detail"] = detail
            with self._lock:
                self._last_kind = kind
                self._last_detail = detail
                self._last_monotonic = time.monotonic()
                if method == "item/completed":
                    self._steps += 1
                    self._by_kind[kind] = self._by_kind.get(kind, 0) + 1
        else:
            message = getattr(payload, "message", None) or getattr(payload, "error", None)
            if message is not None:
                record["detail"] = _short(message)
            with self._lock:
                self._last_monotonic = time.monotonic()
                if method in {"error", "turn/failed"}:
                    self._errors += 1

        return record

    def snapshot(self) -> dict[str, Any]:
        """Компактный срез для heartbeat: чем занят и давно ли молчит."""
        with self._lock:
            idle = int(time.monotonic() - self._last_monotonic)
            data: dict[str, Any] = {"steps": self._steps, "idle_sec": idle}
            if self._last_kind:
                data["last"] = self._last_kind
                if self._last_detail:
                    data["last_detail"] = self._last_detail
            if self._deltas:
                data["deltas"] = self._deltas
            if self._errors:
                data["errors"] = self._errors
            return data


class ProgressRegistry:
    """Сводка по параллельным ходам флота: кто ещё жив и давно ли молчит."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._trackers: dict[str, ProgressTracker] = {}
        self._done: set[str] = set()

    def tracker(self, worker_id: str) -> ProgressTracker:
        with self._lock:
            tracker = self._trackers.get(worker_id)
            if tracker is None:
                tracker = ProgressTracker()
                self._trackers[worker_id] = tracker
            return tracker

    def finish(self, worker_id: str) -> None:
        with self._lock:
            self._done.add(worker_id)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            active = {
                wid: tracker
                for wid, tracker in self._trackers.items()
                if wid not in self._done
            }
        if not active:
            return {"active": 0}
        snaps = {wid: tracker.snapshot() for wid, tracker in active.items()}
        stalest = max(snaps.items(), key=lambda kv: kv[1].get("idle_sec", 0))
        return {
            "active": len(active),
            "steps": sum(snap.get("steps", 0) for snap in snaps.values()),
            # Молчащий дольше всех — то, ради чего пульс вообще читают.
            "stalest": stalest[0],
            "stalest_idle_sec": stalest[1].get("idle_sec", 0),
            "stalest_last": stalest[1].get("last"),
        }


def _load_collectors() -> tuple[Callable[..., Any] | None, Callable[..., Any] | None]:
    """Штатные сборщики SDK. Отсутствуют → работаем без прогресса, но работаем."""
    try:
        from openai_codex._run import (  # noqa: PLC0415 — импорт после scrub_billing_env
            _collect_async_turn_result,
            _collect_turn_result,
        )
    except Exception:  # noqa: BLE001 — приватная функция SDK могла переехать
        return None, None
    return _collect_turn_result, _collect_async_turn_result


def _tee(
    stream: Iterator[Any],
    tracker: ProgressTracker,
    run_dir: Any | None,
    extra: dict[str, Any] | None = None,
) -> Iterator[Any]:
    for event in stream:
        try:
            record = tracker.observe(event)
            if record is not None and run_dir is not None:
                append_event(run_dir, "codex", **{**(extra or {}), **record})
        except Exception:  # noqa: BLE001 — журнал не роняет оплаченный ход
            pass
        yield event


async def _atee(
    stream: AsyncIterator[Any],
    tracker: ProgressTracker,
    run_dir: Any | None,
    extra: dict[str, Any] | None = None,
) -> AsyncIterator[Any]:
    async for event in stream:
        try:
            record = tracker.observe(event)
            if record is not None and run_dir is not None:
                append_event(run_dir, "codex", **{**(extra or {}), **record})
        except Exception:  # noqa: BLE001
            pass
        yield event


GOAL_HEADINGS = ("цель", "задача", "goal", "objective")


def _task_line(root: Any) -> str:
    """Исходное задание одной строкой — то, с чем сравнивают последние шаги.

    Без него сводка честно отвечает «что он делает», но не «туда ли идёт»:
    сравнивать приходится с памятью вызывающего, а у свежего окна её нет.
    """
    import json

    prompt_path = root / "prompt.md"
    if prompt_path.is_file():
        try:
            text = prompt_path.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            return ""
        marker = "===== USER PROMPT ====="
        if marker in text:
            text = text.split(marker, 1)[1]
        rows = [row.strip() for row in text.splitlines()]
        # Задание почти всегда начинается служебной рамкой (запреты, каналы), а
        # сравнивают шаги с целью: если автор её озаглавил, берём её.
        for index, row in enumerate(rows):
            if row.startswith("#") and row.lstrip("# ").strip().lower() in GOAL_HEADINGS:
                for below in rows[index + 1 :]:
                    if below:
                        return _short(below, 160)
        for row in rows:
            if row and not row.startswith("#"):
                return _short(row, 160)
        return ""

    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        try:
            tasks = json.loads(manifest_path.read_text(encoding="utf-8")).get("tasks") or []
        except Exception:  # noqa: BLE001
            return ""
        if tasks:
            names = ", ".join(str(task.get("id")) for task in tasks[:6])
            return _short(f"{len(tasks)} воркеров: {names}" + ("…" if len(tasks) > 6 else ""), 160)
    return ""


def digest(run_dir: Any, *, tail: int = 6) -> str:
    """Компактная сводка прогона для оркестратора: несколько строк, не журнал.

    Существует потому, что смысл субагента — беречь контекстное окно: активность
    живёт на диске и по умолчанию скрыта, а сюда заглядывают по подозрению на
    зависание. Сырой `events.jsonl` в окно не читать — он и есть то, от чего
    субагент избавляет.
    """
    import json
    from pathlib import Path

    root = Path(run_dir)
    lines: list[str] = [f"run_dir: {root}"]
    task = _task_line(root)
    if task:
        lines.append(f"задание: {task}")

    result_path = root / "result.json"
    if result_path.is_file():
        try:
            data = json.loads(result_path.read_text(encoding="utf-8"))
            lines.append(f"status: {data.get('status')} ok={data.get('ok')}")
        except Exception:  # noqa: BLE001
            lines.append("status: result.json нечитаем")
    else:
        lines.append("status: идёт (result.json ещё нет)")

    events_path = root / "events.jsonl"
    if not events_path.is_file():
        lines.append("активность: журнала нет")
        return "\n".join(lines)

    activity: list[dict[str, Any]] = []
    last_beat: dict[str, Any] | None = None
    steer: list[dict[str, Any]] = []
    for raw in events_path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(raw)
        except Exception:  # noqa: BLE001
            continue
        name = event.get("event")
        if name == "codex":
            activity.append(event)
        elif name == "heartbeat":
            last_beat = event
        elif name in ("steer_requested", "steer_accepted", "steer_rejected"):
            # Судьба реплики обязана быть видна ЗДЕСЬ: посылать за ней в сырой
            # events.jsonl значит отправлять в окно то, ради экономии которого
            # сводка и существует.
            steer.append(event)

    if last_beat:
        parts = [f"elapsed={last_beat.get('elapsed_sec')}s"]
        for key in ("steps", "idle_sec", "active", "stalest", "stalest_idle_sec"):
            if last_beat.get(key) is not None:
                parts.append(f"{key}={last_beat[key]}")
        lines.append("пульс: " + " ".join(parts))

    for event in steer:
        mark = {
            "steer_requested": "в ящике",
            "steer_accepted": "принята движком (не значит «послушался»)",
            "steer_rejected": "отвергнута",
        }[event["event"]]
        who = f"[{event['worker']}] " if event.get("worker") else ""
        why = f" — {_short(event.get('error', ''), 90)}" if event.get("error") else ""
        lines.append(f"реплика {who}{event.get('request_id')}: {mark}{why}")

    lines.append(f"шагов записано: {len(activity)}")
    for event in activity[-tail:]:
        worker = f"[{event['worker']}] " if event.get("worker") else ""
        detail = _short(event.get("detail", ""), 90)
        lines.append(f"  {worker}{event.get('kind') or event.get('method')}: {detail}")
    return "\n".join(lines)


def board(project: Any, *, limit: int = 12) -> str:
    """Одна строка на прогон — доска оркестратора, ведущего несколько Codex разом.

    `digest()` отвечает на «что делает ЭТОТ прогон», а оркестратору с тремя
    фоновыми запусками нужен другой вопрос: «кто из них ещё жив и кто встал».
    Три вызова digest на это отвечали ценой трёх выхлопов в контекстное окно —
    ровно то, от чего субагент должен избавлять.
    """
    import json
    from pathlib import Path

    root = Path(project) / "_workspace" / "codex-artifacts"
    if not root.is_dir():
        return f"прогонов нет: {root} не существует"

    runs = sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)[:limit]
    if not runs:
        return f"прогонов нет: {root} пуст"

    lines = [f"прогоны в {root} (свежие сверху, показано {len(runs)}):"]
    for run in runs:
        result = run / "result.json"
        state = "идёт"
        detail = ""
        if result.is_file():
            try:
                data = json.loads(result.read_text(encoding="utf-8"))
                state = "ok" if data.get("ok") else "провал"
                for key in ("worker_status", "scope_status", "verification_status"):
                    if data.get(key):
                        detail += f" {key.split('_')[0]}={data[key]}"
                wave = data.get("wave") or {}
                if wave.get("integration_status"):
                    detail += f" влито={len(wave.get('merged') or [])}"
                    if wave.get("kept_branches"):
                        detail += f" ВЕТОК={len(wave['kept_branches'])}"
                    if wave.get("cleanup_done") is False:
                        detail += " ДЕРЕВЬЯ-ВИСЯТ"
            except Exception:  # noqa: BLE001
                state = "result.json нечитаем"

        beat: dict[str, Any] | None = None
        events = run / "events.jsonl"
        if events.is_file():
            for raw in events.read_text(encoding="utf-8").splitlines():
                try:
                    event = json.loads(raw)
                except Exception:  # noqa: BLE001
                    continue
                if event.get("event") == "heartbeat":
                    beat = event
        if state == "идёт" and beat:
            # Растущий idle при живом процессе — единственный честный признак
            # зависания; для флота важнее не агрегат, а самый молчащий воркер.
            detail += f" elapsed={beat.get('elapsed_sec')}s"
            for key in ("steps", "idle_sec", "active", "stalest"):
                if beat.get(key) is not None:
                    detail += f" {key}={beat[key]}"

        lines.append(f"  {run.name}  {state}{detail}")
    return "\n".join(lines)


class _InterruptOnSignal:
    """SIGINT/SIGTERM → `turn/interrupt`, а не смерть процесса на полуслове.

    Раньше остановка долгого прогона означала убийство процесса: движок
    продолжал турн, а мы теряли и `TurnResult`, и `result.json`. Штатный
    interrupt закрывает ход по протоколу, поток отдаёт terminal-событие, и
    приёмка получает честный не-`completed` статус вместо пустоты.
    """

    def __init__(self, handle: Any, run_dir: Any | None) -> None:
        self._handle = handle
        self._run_dir = run_dir
        self._previous: dict[int, Any] = {}
        self._fired = False

    def _on_signal(self, signum: int, _frame: Any) -> None:
        if self._fired:
            return
        self._fired = True
        # Порядок намеренный: сперва фиксируем факт на диске, потом просим
        # движок остановиться. Если он висит (например, внутри MCP-вызова) и
        # процесс потом убьют, audit-запись уже существует.
        if self._run_dir is not None:
            try:
                append_event(self._run_dir, "interrupt_requested", signal=signum)
                write_json(
                    self._run_dir / "result.json",
                    {
                        "status": "interrupt_requested",
                        "ok": False,
                        "error": f"Прогон остановлен сигналом {signum}; "
                        "движок не подтвердил завершение хода.",
                        "provisional": True,
                    },
                )
            except Exception:  # noqa: BLE001
                pass
        try:
            self._handle.interrupt()
        except Exception:  # noqa: BLE001 — на выходе не мешаем остановке
            pass

    def __enter__(self) -> _InterruptOnSignal:
        import signal

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                self._previous[sig] = signal.signal(sig, self._on_signal)
            except ValueError:
                # Не главный поток — обработчики недоступны, это не ошибка.
                pass
        return self

    def __exit__(self, *_exc: Any) -> None:
        import signal

        for sig, previous in self._previous.items():
            try:
                signal.signal(sig, previous)
            except ValueError:
                pass


CONTROL_INBOX_NAME = "control.jsonl"
CONTROL_POLL_SEC = 2.0


def file_steer_request(run_dir: Any, text: str, *, worker: str | None = None) -> dict[str, Any]:
    """Положить реплику в ящик идущего прогона. Кредитов не стоит, хода не начинает.

    Ящик существует потому, что прогон — отдельный процесс: SDK-ручка хода
    принадлежит ему, и снаружи её не позвать. Диск — единственный носитель,
    общий у оркестратора и прогона.
    """
    from pathlib import Path
    import uuid as _uuid

    request = {
        "id": _uuid.uuid4().hex[:12],
        "text": text,
        "worker": worker,
        "created_at": utc_now(),
    }
    append_jsonl(Path(run_dir) / CONTROL_INBOX_NAME, request)
    append_event(run_dir, "steer_requested", request_id=request["id"], worker=worker)
    return request


class _ControlInbox:
    """Читатель ящика для одного адресата: отдаёт новые реплики, ведёт приём.

    Событие приёма называется `steer_accepted`, а не `applied`: движок
    подтверждает получение реплики, но не смену курса. Курс проверяется
    следующими шагами прогона, и подменять эту проверку записью в журнал —
    ровно тот самоотчёт, который здесь нигде не считается доказательством.
    """

    def __init__(self, run_dir: Any, worker: str | None = None) -> None:
        from pathlib import Path

        self._path = Path(run_dir) / CONTROL_INBOX_NAME
        self._run_dir = run_dir
        self._worker = worker
        self._seen: set[str] = set()

    def pending(self) -> list[dict[str, Any]]:
        """Непрочитанные реплики, адресованные этому ходу."""
        import json

        if not self._path.is_file():
            return []
        fresh: list[dict[str, Any]] = []
        try:
            raw_lines = self._path.read_text(encoding="utf-8").splitlines()
        except Exception:  # noqa: BLE001 — ящик не имеет права уронить ход
            return []
        for raw in raw_lines:
            try:
                request = json.loads(raw)
            except Exception:  # noqa: BLE001
                continue
            request_id = str(request.get("id") or "")
            if not request_id or request_id in self._seen:
                continue
            # Безадресная реплика достаётся только одиночному ходу: в волне
            # «кому-нибудь» означало бы всем сразу.
            if request.get("worker") != self._worker:
                continue
            self._seen.add(request_id)
            fresh.append(request)
        return fresh

    def accepted(self, request: dict[str, Any], response: Any) -> None:
        append_event(
            self._run_dir,
            "steer_accepted",
            request_id=request.get("id"),
            worker=self._worker,
            turn_id=getattr(response, "turn_id", None),
        )

    def rejected(self, request: dict[str, Any], error: BaseException) -> None:
        append_event(
            self._run_dir,
            "steer_rejected",
            request_id=request.get("id"),
            worker=self._worker,
            error=f"{type(error).__name__}: {error}",
        )


class _ControlWatcher:
    """Сторож рядом с ходом: доставляет реплики из ящика в живой turn.

    Живёт отдельным потоком, а не проверкой между событиями, намеренно: поток
    нотификаций молчит минутами, пока модель думает, и реплика приезжала бы
    ровно тогда, когда вмешиваться уже поздно.
    """

    def __init__(self, handle: Any, run_dir: Any | None, worker: str | None = None) -> None:
        self._handle = handle
        self._inbox = _ControlInbox(run_dir, worker) if run_dir is not None else None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _loop(self) -> None:
        while not self._stop.wait(CONTROL_POLL_SEC):
            assert self._inbox is not None
            for request in self._inbox.pending():
                try:
                    self._inbox.accepted(request, self._handle.steer(request["text"]))
                except Exception as exc:  # noqa: BLE001
                    # Отказ движка — нормальный ответ (ход уже сменился, вид
                    # хода не управляем), а не авария прогона.
                    self._inbox.rejected(request, exc)

    def __enter__(self) -> _ControlWatcher:
        if self._inbox is not None:
            self._thread = threading.Thread(
                target=self._loop, name="codex-control-watcher", daemon=True
            )
            self._thread.start()
        return self

    def __exit__(self, *_exc: Any) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=CONTROL_POLL_SEC + 1)


async def _watch_control_async(handle: Any, run_dir: Any, worker: str | None) -> None:
    """Тот же сторож для асинхронного хода флота: `steer` там — корутина."""
    import asyncio

    inbox = _ControlInbox(run_dir, worker)
    while True:
        await asyncio.sleep(CONTROL_POLL_SEC)
        for request in inbox.pending():
            try:
                inbox.accepted(request, await handle.steer(request["text"]))
            except Exception as exc:  # noqa: BLE001
                inbox.rejected(request, exc)


def run_turn(
    handle: Any,
    *,
    run_dir: Any | None,
    tracker: ProgressTracker,
    extra: dict[str, Any] | None = None,
) -> Any:
    """Синхронный ход с журналом активности. Возвращает штатный `TurnResult`."""
    collect, _ = _load_collectors()
    if collect is None:
        return handle.run()
    stream = handle.stream()
    try:
        with _InterruptOnSignal(handle, run_dir), _ControlWatcher(handle, run_dir):
            return collect(_tee(stream, tracker, run_dir, extra), turn_id=handle.id)
    finally:
        stream.close()


async def run_async_turn(
    handle: Any,
    *,
    run_dir: Any | None,
    tracker: ProgressTracker,
    extra: dict[str, Any] | None = None,
) -> Any:
    """Асинхронный ход с журналом активности (флот)."""
    _, collect_async = _load_collectors()
    if collect_async is None:
        return await handle.run()
    import asyncio

    stream = handle.stream()
    watcher = (
        asyncio.ensure_future(
            _watch_control_async(handle, run_dir, (extra or {}).get("worker"))
        )
        if run_dir is not None
        else None
    )
    try:
        return await collect_async(
            _atee(stream, tracker, run_dir, extra), turn_id=handle.id
        )
    finally:
        if watcher is not None:
            watcher.cancel()
        await stream.aclose()


def main() -> int:
    """`python codex_progress.py RUN_DIR [--tail N]` — заглянуть в прогон.

    Единственная ручка «посмотреть, что там агент делает». По умолчанию
    активность скрыта: она на диске, а не в контекстном окне оркестратора.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Сводка идущего или завершённого Codex-прогона; --board — все прогоны разом."
    )
    parser.add_argument("run_dir", nargs="?", help="Путь к run_dir прогона")
    parser.add_argument(
        "--board",
        metavar="PROJECT",
        nargs="?",
        const=".",
        help="Доска: одна строка на прогон проекта (default: cwd). Для оркестратора "
        "с несколькими фоновыми запусками.",
    )
    parser.add_argument(
        "--tail", type=int, default=6, help="Сколько последних шагов показать"
    )
    parser.add_argument(
        "--steer",
        metavar="ТЕКСТ",
        help="Реплика в ИДУЩИЙ ход: положить в ящик прогона. Кредитов не стоит; "
        "движок подтверждает приём, но не смену курса — проверяй следующими шагами.",
    )
    parser.add_argument(
        "--worker",
        metavar="ID",
        help="Кому из воркеров волны адресована реплика (--steer). У одиночного прогона не нужен.",
    )
    args = parser.parse_args()
    if args.board is not None:
        print(board(args.board))
        return 0
    if not args.run_dir:
        parser.error("нужен RUN_DIR или --board [PROJECT]")
    if args.steer:
        return _steer_cli(args.run_dir, args.steer, args.worker)
    print(digest(args.run_dir, tail=args.tail))
    return 0


def _steer_cli(run_dir: Any, text: str, worker: str | None) -> int:
    """Отдать реплику ящику прогона, отказав честно, когда принимать её некому."""
    import json
    from pathlib import Path

    root = Path(run_dir)
    if not root.is_dir():
        print(f"нет такого прогона: {root}")
        return 2
    if (root / "result.json").is_file():
        print("прогон закончен — реплику принимать некому; чини следующим прогоном")
        return 2
    manifest = root / "manifest.json"
    if worker is None and manifest.is_file():
        try:
            tasks = json.loads(manifest.read_text(encoding="utf-8")).get("tasks") or []
        except Exception:  # noqa: BLE001
            tasks = []
        if tasks:
            names = ", ".join(str(task.get("id")) for task in tasks)
            print(f"это волна — назови адресата: --worker ID (есть: {names})")
            return 2
    request = file_steer_request(root, text, worker=worker)
    print(
        f"реплика {request['id']} в ящике; её судьба и курс — в сводке "
        f"`codex_progress.py {root}`"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
