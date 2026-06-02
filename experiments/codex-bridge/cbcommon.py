"""Общая логика codex-bridge: гарантия биллинга через ChatGPT-аккаунт.

Одна правда для review и orchestrate: перед запуском дочернего codex-процесса
убираем переменные, которые увели бы Codex на платный API вместо подписки.
SDK делает os.environ.copy() для дочернего процесса и лишь дополняет его
config.env, поэтому удалять ключи надо в родительском окружении.
"""
from __future__ import annotations

import os

# Переменные, способные увести codex на API-биллинг вместо ChatGPT-аккаунта.
BILLING_LEAK_VARS = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")


def scrub_billing_env() -> list[str]:
    """Убрать из окружения ключи API-биллинга. Возвращает список вырезанных."""
    removed = []
    for var in BILLING_LEAK_VARS:
        if os.environ.pop(var, None) is not None:
            removed.append(var)
    return removed
