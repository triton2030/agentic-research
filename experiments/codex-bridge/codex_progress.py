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

from codex_run_ledger import append_event

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
    for raw in events_path.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(raw)
        except Exception:  # noqa: BLE001
            continue
        if event.get("event") == "codex":
            activity.append(event)
        elif event.get("event") == "heartbeat":
            last_beat = event

    if last_beat:
        parts = [f"elapsed={last_beat.get('elapsed_sec')}s"]
        for key in ("steps", "idle_sec", "active", "stalest", "stalest_idle_sec"):
            if last_beat.get(key) is not None:
                parts.append(f"{key}={last_beat[key]}")
        lines.append("пульс: " + " ".join(parts))

    lines.append(f"шагов записано: {len(activity)}")
    for event in activity[-tail:]:
        worker = f"[{event['worker']}] " if event.get("worker") else ""
        detail = _short(event.get("detail", ""), 90)
        lines.append(f"  {worker}{event.get('kind') or event.get('method')}: {detail}")
    return "\n".join(lines)


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
    stream = handle.stream()
    try:
        return await collect_async(
            _atee(stream, tracker, run_dir, extra), turn_id=handle.id
        )
    finally:
        await stream.aclose()


def main() -> int:
    """`python codex_progress.py RUN_DIR [--tail N]` — заглянуть в прогон.

    Единственная ручка «посмотреть, что там агент делает». По умолчанию
    активность скрыта: она на диске, а не в контекстном окне оркестратора.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Компактная сводка идущего или завершённого Codex-прогона."
    )
    parser.add_argument("run_dir", help="Путь к run_dir прогона")
    parser.add_argument(
        "--tail", type=int, default=6, help="Сколько последних шагов показать"
    )
    args = parser.parse_args()
    print(digest(args.run_dir, tail=args.tail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
