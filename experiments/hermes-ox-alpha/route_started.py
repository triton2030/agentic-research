#!/usr/bin/env python3
"""Стартовал ли маршрут Ox в этом прогоне.

Наблюдаемый отпечаток вероятностного отказа: провайдер не разрешился и не
сделано ни одного вызова API. Приходит примерно раз на четыре прогона, не
зависит ни от размера брифа, ни от его содержания, и проходит на повторе.

Код возврата: 0 — маршрут стартовал (повтор не нужен), 1 — не стартовал.
"""
from __future__ import annotations

import json
import sys


def route_started(result: dict) -> bool:
    usage = result.get("usage") or {}
    resolved = result.get("resolved") or {}
    stalled = resolved.get("provider") is None and (usage.get("api_calls") or 0) == 0
    return not stalled


if __name__ == "__main__":
    try:
        payload = json.load(open(sys.argv[1], encoding="utf-8"))
    except Exception:
        sys.exit(1)
    sys.exit(0 if route_started(payload) else 1)
