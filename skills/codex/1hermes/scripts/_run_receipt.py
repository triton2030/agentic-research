"""Долговечная квитанция одного прогона Hermes.

Прогон стоит времени и денег, а его результат существовал только как строка
в stdout: любое исключение после оплаченного вызова — и результата нет нигде.
Квитанция создаётся до запуска процесса и финализируется всегда, включая
аварийный путь, поэтому у каждого прогона есть адрес на диске.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _root() -> Path:
    hermes_home = os.environ.get("HERMES_HOME")
    base = Path(hermes_home).expanduser() if hermes_home else Path.home() / ".hermes"
    return base / "1hermes-runs"


def _write_private(path: Path, text: str, *, exclusive: bool = False) -> None:
    """Create receipt data without a world-readable umask window."""
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            stream.write(text)
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def open_receipt(requested: dict[str, Any], prompt: str) -> dict[str, Any] | None:
    """Создать каталог прогона до первого платного вызова.

    Возвращает None, если каталог создать не удалось: отсутствие квитанции
    останавливать работу не должно — она свидетель, а не гейт.
    """
    stamp = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    run_id = f"{stamp}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
    try:
        path = _root() / run_id
        path.mkdir(parents=True, mode=0o700, exist_ok=False)
        path.chmod(0o700)
        _write_private(path / "prompt.md", prompt, exclusive=True)
        _write_private(
            path / "manifest.json",
            json.dumps(
                {"run_id": run_id, "opened_at": stamp, "requested": requested},
                ensure_ascii=False,
                indent=2,
            ),
            exclusive=True,
        )
    except OSError:
        return None
    return {"run_id": run_id, "path": str(path)}


def close_receipt(receipt: dict[str, Any] | None, payload: dict[str, Any]) -> None:
    """Записать терминальный результат. Вызывается на любом исходе."""
    if not receipt:
        return
    try:
        target = Path(receipt["path"]) / "result.json"
        tmp = target.with_suffix(".json.part")
        _write_private(tmp, json.dumps(payload, ensure_ascii=False, indent=2))
        tmp.replace(target)
    except OSError:
        return
