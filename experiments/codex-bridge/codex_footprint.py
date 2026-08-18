"""След моста СНАРУЖИ его run_dir — то, чего не видит ни один наш тест.

Зачем. Тесты, отчёт волны и `git worktree list` смотрят внутрь: код мог быть
зелёным полтора месяца и всё это время сорить в чужом приложении. Так и вышло
2026-08-18: «проект» у Codex — это ПАПКА треда, папки воркеров одноразовые, и
список проектов владельца состоял из имён наших задач — нашёл он сам, глазами,
на телефоне. Диагностика обязана смотреть туда же, куда смотрит владелец.

Скан локальный и бесплатный: ни одного RPC, ни одного кредита. Он ничего не
чинит — только считает; уборка остаётся отдельной названной командой.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

# `CODEX_HOME` перекрывает `~/.codex` — движок читает его же.
CODEX_HOME = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))

# Наши прогоны движок метит так; фильтр по метке, а не по путям, переживает
# любую будущую смену раскладки папок моста.
BRIDGE_ORIGINATOR = "codex_python_sdk"

_PROJECT_ENTRY = re.compile(r'^\[projects\."(?P<path>.+)"\]\s*$')


def _session_meta(rollout: Path) -> dict[str, Any] | None:
    """Первая строка стора — session_meta; повреждённый файл не роняет скан."""
    try:
        with rollout.open(encoding="utf-8") as handle:
            payload = json.loads(handle.readline()).get("payload")
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def orphan_threads(sessions_home: Path | None = None) -> list[dict[str, str]]:
    """Треды моста, чья рабочая папка уже удалена.

    Каждый такой — карточка проекта в Codex, ведущая в никуда, и убрать её
    из приложения местами вообще нечем (openai/codex#26026).
    """
    home = sessions_home or (CODEX_HOME / "sessions")
    if not home.is_dir():
        return []
    found: list[dict[str, str]] = []
    for rollout in home.rglob("rollout-*.jsonl"):
        meta = _session_meta(rollout)
        if not meta or meta.get("originator") != BRIDGE_ORIGINATOR:
            continue
        cwd = meta.get("cwd") or ""
        if not cwd or Path(cwd).is_dir():
            continue
        thread_id = meta.get("id")
        if thread_id:
            found.append({"thread_id": thread_id, "cwd": cwd})
    return found


def dead_project_entries(config_path: Path | None = None) -> list[str]:
    """Записи `[projects."<путь>"]` на несуществующие папки.

    Движок дописывает их на каждый новый cwd. Косметика: в списке проектов их
    не видно, платного эффекта нет — поэтому считаем, но не трогаем (правка
    живого конфига владельца дороже мусора, который она уберёт).
    """
    path = config_path or (CODEX_HOME / "config.toml")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    dead = []
    for line in lines:
        match = _PROJECT_ENTRY.match(line)
        if match and not Path(match.group("path")).is_dir():
            dead.append(match.group("path"))
    return dead


def scan() -> dict[str, Any]:
    """Снимок следа для доктора: только числа и образцы, без вердикта."""
    threads = orphan_threads()
    dead = dead_project_entries()
    return {
        "orphan_threads": len(threads),
        "orphan_thread_samples": [t["cwd"] for t in threads[:3]],
        "dead_project_entries": len(dead),
    }
