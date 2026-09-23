"""Копия проекта для проверяющего с правом записи (`codex_review.py --scratch`).

Зачем. Проверяющий читает проект в `read_only`, и тесты, сборки, линтеры с
кэшами у него падают: проверка остаётся чтением. Владелец 2026-09-23 выбрал
больше пользы от Codex ценой меньшей безопасности
(`_ops/chat-recall/2026-09-23-051553-claude-483a304e.md#recall-94036c7a45b24ae2aa0cbdeaa094b974`).
Копия даёт проверяющему запись, не давая её проекту.

Почему полная APFS-копия (`cp -cR`, clonefile), а не worktree или выборка
(совет Codex astra 2026-09-23, `_workspace/codex-artifacts/20260923T164405Z-advisor-loosen`):
она несёт незакоммиченные правки, индекс и игнорируемые зависимости как есть,
ничего не угадывая. Цена — время: 127 тыс. файлов копируются ~30 с, поэтому
копия — флаг по задаче, а не дефолт. Место на диске почти не тратится: блоки
общие, пока их не перепишут.

Копия не гарантирует работоспособность среды: `.venv` с абсолютными путями,
симлинки наружу и `.git`-файл linked worktree ведут в исходник. Чинить это
здесь не пытаемся — проверяющий видит отказ и называет его.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

SCRATCH_HOME = Path.home() / ".codex-bridge" / "scratch"


def plan_scratch(project: Path, run_id: str) -> dict[str, Any]:
    """Где будет копия — известно до копирования: роль и manifest пишутся раньше."""
    return {
        "source": str(project),
        "cwd": str(SCRATCH_HOME / run_id / project.name),
        "copy_status": "planned",
        "copy_duration_ms": None,
        "cleanup_status": "pending",
    }


def make_scratch_copy(workspace: dict[str, Any]) -> None:
    """Скопировать проект вне его самого. Бросает RuntimeError при отказе cp."""
    dest = Path(workspace["cwd"])
    dest.parent.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    # -c: clonefile на APFS; без поддержки cp падает, и тогда копия честно не
    # делается — полная физическая копия гигабайтов молча дороже отказа.
    try:
        proc = subprocess.run(
            ["cp", "-cR", workspace["source"], str(dest)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        reason = (proc.stderr or proc.stdout).strip()[:500] if proc.returncode != 0 else None
    except OSError as exc:
        reason = str(exc)
    workspace["copy_duration_ms"] = int((time.monotonic() - started) * 1000)
    if reason is not None:
        shutil.rmtree(dest.parent, ignore_errors=True)
        workspace["copy_status"] = "failed"
        workspace["cleanup_status"] = "removed" if not dest.parent.exists() else "stuck"
        raise RuntimeError(f"копия проекта не создана: {reason}")
    workspace["copy_status"] = "copied"


def remove_scratch_copy(workspace: dict[str, Any]) -> None:
    """Убрать копию; итог уборки — факт с диска, а не намерение."""
    home = Path(workspace["cwd"]).parent
    shutil.rmtree(home, ignore_errors=True)
    workspace["cleanup_status"] = "removed" if not home.exists() else "stuck"


def scratch_note(workspace: dict[str, Any]) -> str:
    """Абзац для роли проверяющего: где он и что ему можно."""
    return (
        "\n\nКОПИЯ (вместо read-only). Ты работаешь в копии проекта "
        f"{workspace['cwd']} (исходник — {workspace['source']}). В копии можно "
        "писать: запускай тесты, сборки и линтеры, чтобы проверять делом, а не "
        "чтением. Исходник не меняй. Адреса в ответе давай относительно корня "
        "проекта. Копия удаляется после ответа, и следующий ход получит свежую — "
        "твои правки в ней не сохранятся. Зависимости скопированы как файлы, но "
        "могут ссылаться на исходник абсолютными путями: отказ среды назови "
        "дословно. По каждой проверке — команда и её exit code."
    )
