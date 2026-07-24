#!/usr/bin/env python3
"""Статусная доска диалоговых тредов Codex: list / archive / unarchive.

Источник — append-only реестр `<project>/_workspace/codex-artifacts/
dialog-threads.jsonl` (события start/continue/archive/unarchive; legacy-строки
без "event" читаются как start). `list` не трогает SDK и Codex — чистое
чтение; `archive`/`unarchive` зовут штатные SDK-вызовы (env scrub перед
импортом SDK — биллинг-инвариант), никаких ручных удалений в `~/.codex`.

Зачем: новый или параллельный агент видит тематику и свежесть чужих диалогов,
не читая переписку; «где остановились» — final.md последнего run (упавший ход
— result.json там же); продолжить — `codex_review.py "..." --continue ID`.

Границы: реестр append-only без межпроцессных локов — правило «чужой ЖИВОЙ
тред не трогай» обеспечивается дисциплиной агента (references/threads.md
скила 1codex), не backend-ом.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cbcommon import scrub_billing_env
from codex_defaults import resolve_codex_bin
from codex_sdk_compat import harden_sdk_enums
from codex_review import _append_registry_event, _dialog_registry_path

STALE_HOURS_DEFAULT = 48  # правило владельца: диалог старше двух дней можно архивировать


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(value)
    except ValueError:
        return None
    if ts.tzinfo is None:
        # legacy/naive-метки считаем UTC, не роняем доску на сравнении
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def read_events(project_cwd: Path) -> tuple[list[dict], int]:
    """(события, число повреждённых строк). Повреждённая строка — не JSON,
    не-объект или объект без thread_id."""
    path = _dialog_registry_path(project_cwd)
    if not path.is_file():
        return [], 0
    events: list[dict] = []
    bad = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        if not isinstance(obj, dict) or not obj.get("thread_id"):
            bad += 1
            continue
        events.append(obj)
    return events, bad


def collapse(events: list[dict]) -> list[dict]:
    """События реестра → текущий статус на тред (в порядке появления)."""
    threads: dict[str, dict] = {}
    for ev in events:
        tid = ev["thread_id"]
        kind = ev.get("event") or "start"
        entry = threads.setdefault(tid, {
            "thread_id": tid,
            "topic": None,
            "created_at": None,
            "last_at": None,
            "last_run_id": None,
            "last_run_dir": None,
            "turns": 0,
            "last_session": None,
            "archived": False,
        })
        # Тема берётся из любого события (усыновлённый foreign-тред несёт её
        # в continue), но первое слово не перебивается.
        entry["topic"] = entry["topic"] or ev.get("topic")
        ts = ev.get("created_at") or ev.get("at")
        if kind == "archive":
            entry["archived"] = True
            continue
        if kind == "unarchive":
            entry["archived"] = False
            continue
        if kind == "start":
            entry["created_at"] = ts or entry["created_at"]
        entry["turns"] += 1
        if ts:
            entry["last_at"] = ts
        entry["last_run_id"] = ev.get("run_id") or entry["last_run_id"]
        entry["last_run_dir"] = ev.get("run_dir") or entry["last_run_dir"]
        entry["last_session"] = ev.get("session") or entry["last_session"]
    return list(threads.values())


def stale_ids(threads: list[dict], now: datetime, older_hours: int) -> list[str]:
    cutoff = now - timedelta(hours=older_hours)
    out = []
    for t in threads:
        if t["archived"]:
            continue
        last = _parse_ts(t["last_at"])
        if last is not None and last < cutoff:
            out.append(t["thread_id"])
    return out


def _fmt_age(last_at: str | None, now: datetime) -> str:
    last = _parse_ts(last_at)
    if last is None:
        return "?"
    hours = (now - last).total_seconds() / 3600
    return f"{hours / 24:.1f}д" if hours >= 48 else f"{hours:.0f}ч"


def cmd_list(project_cwd: Path, as_json: bool, older_hours: int) -> int:
    events, bad = read_events(project_cwd)
    threads = collapse(events)
    now = datetime.now(timezone.utc)
    stale = set(stale_ids(threads, now, older_hours))
    if bad:
        print(f"[codex-threads] повреждённых строк реестра: {bad} — доска может быть неполной.", file=sys.stderr)
    if as_json:
        for t in threads:
            t["stale"] = t["thread_id"] in stale
        print(json.dumps({"threads": threads, "bad_lines": bad}, ensure_ascii=False, indent=2))
        return 0
    if not threads:
        print(f"Реестр пуст: {_dialog_registry_path(project_cwd)}")
        return 0
    for t in threads:
        flags = "".join([
            " [archived]" if t["archived"] else "",
            " [stale]" if t["thread_id"] in stale else "",
        ])
        run_ref = t["last_run_dir"] or t["last_run_id"] or "?"
        print(
            f"{t['thread_id']}{flags}\n"
            f"  тема: {t['topic'] or '—'}\n"
            f"  ходов: {t['turns']}  последний: {t['last_at'] or '?'} "
            f"({_fmt_age(t['last_at'], now)} назад)  сессия: {t['last_session'] or '?'}\n"
            f"  run: {run_ref}"
        )
    print(
        "\n«Где остановились» — final.md последнего run (упавший ход — result.json"
        ' там же). Продолжить: codex_review.py "..." --continue THREAD_ID'
    )
    return 0


def _open_sdk(project_cwd: Path):
    scrub_billing_env()
    from openai_codex import Codex, CodexConfig

    # Дрейф движка ChatGPT.app под запиненным SDK: новые enum-значения в
    # ответах не должны ронять archive/unarchive (см. codex_sdk_compat.py).
    harden_sdk_enums()
    return Codex(CodexConfig(cwd=str(project_cwd), codex_bin=resolve_codex_bin()))


def cmd_archive(
    project_cwd: Path, thread_id: str | None, stale: bool, older_hours: int
) -> int:
    events, bad = read_events(project_cwd)
    threads = collapse(events)
    if stale:
        if bad:
            # fail closed: по повреждённой доске нельзя судить о свежести
            print(
                f"[codex-threads] archive --stale отклонён: {bad} повреждённых строк реестра — "
                "почини dialog-threads.jsonl или архивируй точечно по THREAD_ID.",
                file=sys.stderr,
            )
            return 2
        targets = stale_ids(threads, datetime.now(timezone.utc), older_hours)
    else:
        targets = [thread_id]
    if not targets:
        print("Нечего архивировать.")
        return 0

    archived, failed = [], []
    with _open_sdk(project_cwd) as codex:
        for tid in targets:
            try:
                codex.thread_archive(tid)
            except Exception as exc:  # noqa: BLE001 — per-target, батч не обрываем
                failed.append(tid)
                print(f"archive FAILED: {tid}: {exc}", file=sys.stderr)
                continue
            _append_registry_event(project_cwd, {
                "event": "archive",
                "thread_id": tid,
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            archived.append(tid)
            print(f"archived: {tid}")
    print(
        f"Итого: archived={len(archived)} failed={len(failed)}. "
        "Обратимо: codex_threads.py unarchive THREAD_ID."
    )
    return 1 if failed else 0


def cmd_unarchive(project_cwd: Path, thread_id: str) -> int:
    with _open_sdk(project_cwd) as codex:
        try:
            codex.thread_unarchive(thread_id)
        except Exception as exc:  # noqa: BLE001
            print(f"unarchive FAILED: {thread_id}: {exc}", file=sys.stderr)
            return 1
    _append_registry_event(project_cwd, {
        "event": "unarchive",
        "thread_id": thread_id,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    print(f"unarchived: {thread_id}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "archive", "unarchive"))
    parser.add_argument("thread_id", nargs="?", help="THREAD_ID для archive/unarchive.")
    parser.add_argument("--project", default=".", help="Корень проекта (default cwd).")
    parser.add_argument("--stale", action="store_true", help="archive: все треды старше --older-hours.")
    parser.add_argument(
        "--older-hours", type=int, default=STALE_HOURS_DEFAULT,
        help=f"Порог свежести в часах (default {STALE_HOURS_DEFAULT} — правило «старше двух дней»).",
    )
    parser.add_argument("--json", action="store_true", help="list: JSON вместо текста.")
    args = parser.parse_args()

    if args.older_hours <= 0:
        print("--older-hours должен быть > 0.", file=sys.stderr)
        return 2
    if args.command == "list" and args.thread_id:
        print("list не принимает THREAD_ID.", file=sys.stderr)
        return 2
    if args.command == "archive" and bool(args.thread_id) == args.stale:
        print("archive: укажи ровно одно из THREAD_ID или --stale.", file=sys.stderr)
        return 2
    if args.command == "unarchive" and (not args.thread_id or args.stale):
        print("unarchive: нужен THREAD_ID, --stale не применим.", file=sys.stderr)
        return 2

    project_cwd = Path(args.project).expanduser().resolve()
    if args.command == "list":
        return cmd_list(project_cwd, args.json, args.older_hours)
    if args.command == "archive":
        return cmd_archive(project_cwd, args.thread_id, args.stale, args.older_hours)
    return cmd_unarchive(project_cwd, args.thread_id)


if __name__ == "__main__":
    raise SystemExit(main())
