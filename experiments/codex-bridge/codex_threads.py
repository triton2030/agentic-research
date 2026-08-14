#!/usr/bin/env python3
"""Статусная доска тредов Codex: list / mine / archive / unarchive.

Источник `list` — append-only реестр `<project>/_workspace/codex-artifacts/
dialog-threads.jsonl` (события start/continue/archive/unarchive; legacy-строки
без "event" читаются как start). `list` не трогает SDK и Codex — чистое
чтение; `archive`/`unarchive` зовут штатные SDK-вызовы (env scrub перед
импортом SDK — биллинг-инвариант), никаких ручных удалений в `~/.codex`.

`mine` — вторая, более широкая оптика: нативный `thread_list` движка, то есть
общий store `~/.codex`, включая сессии владельца в Codex Desktop и терминале,
которых в реестре моста нет вовсе. Только чтение, кредитов не тратит.

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
import subprocess
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


def _threads_with_active_writer(thread_ids: list[str]) -> set[str]:
    """Треды, право записи в которые сейчас занято (открытая вкладка Codex).

    Движок держит writer-lock на каждый тред, открытый в приложении, и
    отклоняет `--continue` в него: `already has an active writer`. Лок живёт,
    пока вкладка открыта, — не пока идёт работа, и не зависит от того, кто
    тред создал. Держатели читаются одним вызовом lsof; нет lsof — пустое
    множество (пометка исчезнет, поведение продолжения не изменится).
    """
    lock_dir = Path.home() / ".codex" / "thread-writer-locks"
    paths = {str(lock_dir / f"{tid}.lock"): tid for tid in thread_ids if tid}
    existing = [p for p in paths if Path(p).is_file()]
    if not existing:
        return set()
    try:
        out = subprocess.run(
            ["lsof", "-F", "n", "--", *existing],
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    return {paths[line[1:]] for line in out.splitlines() if line[1:] in paths}


def cmd_mine(project_cwd: Path, as_json: bool, limit: int, all_projects: bool) -> int:
    """Нативные треды движка — включая те, в которых владелец работает сам.

    Доска моста (`list`) знает только треды, заведённые мостом в этом проекте:
    сессии Codex Desktop и `codex` в терминале туда не попадают вообще. Здесь
    читается общий store `~/.codex` — тот же, что видит Desktop. Только чтение,
    кредитов не тратит.
    """
    with _open_sdk(project_cwd) as codex:
        resp = codex.thread_list(
            limit=limit, sort_key="updated_at", sort_direction="desc"
        )
    rows = []
    for item in resp.data:
        t = item.model_dump() if hasattr(item, "model_dump") else dict(item)
        cwd = str(t.get("cwd") or "")
        if not all_projects and cwd and not cwd.startswith(str(project_cwd)):
            continue
        rows.append({
            "thread_id": t.get("id"),
            "name": t.get("name"),
            "cwd": cwd,
            "branch": (t.get("git_info") or {}).get("branch"),
            "updated_at": _epoch_iso(t.get("updated_at") or t.get("created_at")),
            "ephemeral": t.get("ephemeral"),
            "forked_from_id": t.get("forked_from_id"),
        })

    busy = _threads_with_active_writer([r["thread_id"] for r in rows])
    for r in rows:
        r["writer_busy"] = r["thread_id"] in busy

    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not rows:
        scope = "во всём store" if all_projects else f"в {project_cwd}"
        print(f"Нативных тредов {scope} не найдено (показаны последние {limit}).")
        return 0
    print(f"Треды движка ({'все проекты' if all_projects else project_cwd}):\n")
    for r in rows:
        mark = " [ephemeral]" if r["ephemeral"] else ""
        mark += " [открыт в приложении: запись занята]" if r["writer_busy"] else ""
        fork = f"  ← форк {r['forked_from_id'][:8]}" if r["forked_from_id"] else ""
        print(
            f"{r['thread_id']}{mark}{fork}\n"
            f"  {r['name'] or '(без имени)'}\n"
            f"  {r['updated_at'] or '?'}  {r['cwd'] or '—'}"
            f"{' (' + r['branch'] + ')' if r['branch'] else ''}"
        )
    print(
        '\nЧужой тред продолжается только осознанно: codex_review.py "..." '
        "--continue THREAD_ID --continue-foreign. Живой тред другой сессии не трогай."
    )
    return 0


def _epoch_iso(value) -> str | None:
    """Движок отдаёт время треда unix-секундами; доска моста живёт в ISO."""
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), timezone.utc).astimezone().isoformat(
            timespec="minutes"
        )
    except (TypeError, ValueError, OSError):
        return str(value)


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
    parser.add_argument("command", choices=("list", "mine", "archive", "unarchive"))
    parser.add_argument("thread_id", nargs="?", help="THREAD_ID для archive/unarchive.")
    parser.add_argument("--project", default=".", help="Корень проекта (default cwd).")
    parser.add_argument("--stale", action="store_true", help="archive: все треды старше --older-hours.")
    parser.add_argument(
        "--older-hours", type=int, default=STALE_HOURS_DEFAULT,
        help=f"Порог свежести в часах (default {STALE_HOURS_DEFAULT} — правило «старше двух дней»).",
    )
    parser.add_argument("--json", action="store_true", help="list/mine: JSON вместо текста.")
    parser.add_argument(
        "--limit", type=int, default=25,
        help="mine: сколько последних тредов движка запросить (default 25).",
    )
    parser.add_argument(
        "--all-projects", action="store_true",
        help="mine: не фильтровать по текущему проекту.",
    )
    args = parser.parse_args()

    if args.older_hours <= 0:
        print("--older-hours должен быть > 0.", file=sys.stderr)
        return 2
    if args.command in ("list", "mine") and args.thread_id:
        print(f"{args.command} не принимает THREAD_ID.", file=sys.stderr)
        return 2
    if args.command == "mine" and args.limit <= 0:
        print("--limit должен быть > 0.", file=sys.stderr)
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
    if args.command == "mine":
        return cmd_mine(project_cwd, args.json, args.limit, args.all_projects)
    if args.command == "archive":
        return cmd_archive(project_cwd, args.thread_id, args.stale, args.older_hours)
    return cmd_unarchive(project_cwd, args.thread_id)


if __name__ == "__main__":
    raise SystemExit(main())
