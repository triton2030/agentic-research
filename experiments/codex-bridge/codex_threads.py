#!/usr/bin/env python3
"""Статусная доска диалоговых тредов Codex: list / archive.

Источник — append-only реестр `<project>/_workspace/codex-artifacts/
dialog-threads.jsonl` (события start/continue/archive; legacy-строки без
"event" читаются как start). `list` не трогает SDK и Codex — чистое чтение;
`archive` зовёт штатный SDK `thread_archive` (обратимо: `thread_unarchive`),
никаких ручных удалений в `~/.codex`.

Зачем: новый или параллельный агент видит тематику и свежесть чужих диалогов,
не читая переписку; «где остановились» — final.md последнего run; продолжить —
`codex_review.py "..." --continue THREAD_ID`.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cbcommon import scrub_billing_env
from codex_defaults import resolve_codex_bin
from codex_review import _append_registry_event, _dialog_registry_path

STALE_HOURS_DEFAULT = 48  # правило владельца: диалог старше двух дней можно архивировать


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def read_events(project_cwd: Path) -> list[dict]:
    path = _dialog_registry_path(project_cwd)
    if not path.is_file():
        return []
    events: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def collapse(events: list[dict]) -> list[dict]:
    """События реестра → текущий статус на тред (в порядке появления)."""
    threads: dict[str, dict] = {}
    for ev in events:
        tid = ev.get("thread_id")
        if not tid:
            continue
        kind = ev.get("event") or "start"
        entry = threads.setdefault(tid, {
            "thread_id": tid,
            "topic": None,
            "created_at": None,
            "last_at": None,
            "last_run_id": None,
            "turns": 0,
            "last_session": None,
            "archived": False,
        })
        ts = ev.get("created_at") or ev.get("at")
        if kind == "start":
            entry["topic"] = ev.get("topic") or entry["topic"]
            entry["created_at"] = ts or entry["created_at"]
        if kind == "archive":
            entry["archived"] = True
            continue
        entry["turns"] += 1
        if ts:
            entry["last_at"] = ts
        entry["last_run_id"] = ev.get("run_id") or entry["last_run_id"]
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
    threads = collapse(read_events(project_cwd))
    now = datetime.now(timezone.utc)
    stale = set(stale_ids(threads, now, older_hours))
    if as_json:
        for t in threads:
            t["stale"] = t["thread_id"] in stale
        print(json.dumps(threads, ensure_ascii=False, indent=2))
        return 0
    if not threads:
        print(f"Реестр пуст: {_dialog_registry_path(project_cwd)}")
        return 0
    for t in threads:
        flags = "".join([
            " [archived]" if t["archived"] else "",
            " [stale]" if t["thread_id"] in stale else "",
        ])
        print(
            f"{t['thread_id']}{flags}\n"
            f"  тема: {t['topic'] or '—'}\n"
            f"  ходов: {t['turns']}  последний: {t['last_at'] or '?'} "
            f"({_fmt_age(t['last_at'], now)} назад)  сессия: {t['last_session'] or '?'}"
            f"  run: {t['last_run_id'] or '?'}"
        )
    print(
        "\n«Где остановились» — final.md последнего run "
        "(_workspace/codex-artifacts/<run_id>/final.md). "
        'Продолжить: codex_review.py "..." --continue THREAD_ID'
    )
    return 0


def cmd_archive(
    project_cwd: Path, thread_id: str | None, stale: bool, older_hours: int
) -> int:
    threads = collapse(read_events(project_cwd))
    if stale:
        targets = stale_ids(threads, datetime.now(timezone.utc), older_hours)
    elif thread_id:
        targets = [thread_id]
    else:
        print("archive: укажи THREAD_ID или --stale.", file=sys.stderr)
        return 2
    if not targets:
        print("Нечего архивировать.")
        return 0

    scrub_billing_env()
    from openai_codex import Codex, CodexConfig

    config = CodexConfig(cwd=str(project_cwd), codex_bin=resolve_codex_bin())
    archived = []
    with Codex(config) as codex:
        for tid in targets:
            codex.thread_archive(tid)
            _append_registry_event(project_cwd, {
                "event": "archive",
                "thread_id": tid,
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            archived.append(tid)
            print(f"archived: {tid}")
    print(f"Итого: {len(archived)}. Обратимо: SDK thread_unarchive(THREAD_ID).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "archive"))
    parser.add_argument("thread_id", nargs="?", help="THREAD_ID для archive.")
    parser.add_argument("--project", default=".", help="Корень проекта (default cwd).")
    parser.add_argument("--stale", action="store_true", help="archive: все треды старше --older-hours.")
    parser.add_argument(
        "--older-hours", type=int, default=STALE_HOURS_DEFAULT,
        help=f"Порог свежести в часах (default {STALE_HOURS_DEFAULT} — правило «старше двух дней»).",
    )
    parser.add_argument("--json", action="store_true", help="list: JSON вместо текста.")
    args = parser.parse_args()

    project_cwd = Path(args.project).expanduser().resolve()
    if args.command == "list":
        return cmd_list(project_cwd, args.json, args.older_hours)
    return cmd_archive(project_cwd, args.thread_id, args.stale, args.older_hours)


if __name__ == "__main__":
    raise SystemExit(main())
