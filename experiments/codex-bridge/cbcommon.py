"""Общая логика codex-bridge: гарантия биллинга через ChatGPT-аккаунт.

Одна правда для всех входов: перед запуском дочернего codex-процесса
убираем переменные, которые увели бы Codex на платный API вместо подписки.
SDK делает os.environ.copy() для дочернего процесса и лишь дополняет его
config.env, поэтому удалять ключи надо в родительском окружении.

Здесь же живут мелкие помощники, общие для всех входов: держать их копии в
каждом entrypoint значит чинить дефект дважды.
"""
from __future__ import annotations

import os
from typing import Any

# Переменные, способные увести codex на API-биллинг вместо ChatGPT-аккаунта.
BILLING_LEAK_VARS = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")


def scrub_billing_env() -> list[str]:
    """Убрать из окружения ключи API-биллинга. Возвращает список вырезанных."""
    removed = []
    for var in BILLING_LEAK_VARS:
        if os.environ.pop(var, None) is not None:
            removed.append(var)
    return removed


def first_nonblank(*values: str | None) -> str | None:
    """Первое значение, непустое после strip. Защищает от задания из одних
    пробелов ('   '): оно truthy, но по смыслу пустое и жгло бы кредиты впустую."""
    for value in values:
        if value and value.strip():
            return value.strip()
    return None


class UsageError(Exception):
    """Ошибка вызова или контракта входа; отдаётся кодом выхода 2."""


COMPLETED_CODEX_STATUS = "completed"


def codex_status_value(status: Any) -> str:
    value = getattr(status, "value", None)
    if isinstance(value, str):
        return value
    return str(status)


def codex_turn_completed(status: Any, error: Any) -> bool:
    """Успешный ход Codex — только явный completed без ошибки."""
    return not error and codex_status_value(status) == COMPLETED_CODEX_STATUS
