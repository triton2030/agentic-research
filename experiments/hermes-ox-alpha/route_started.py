#!/usr/bin/env python3
"""Стоит ли принимать этот прогон Ox или надо повторить.

Началось с одного отпечатка: провайдер не разрешился и не сделано ни одного
вызова API. Но за день набрались ещё два класса, лечащиеся тем же повтором, —
сессия не доказала ответ ассистента и вызовы не подтвердили заявленный
маршрут. Пока предикат знал только первый, остальные два вылезали к
оркестратору поштучно и стоили ручных перезапусков.

Поэтому предикат отвечает на вопрос волны, а не на вопрос про маршрут:
принимаем ли результат. Отказ гейта — законный повод повторить; вечно повторять
не даст `RETRIES`.

Код возврата: 0 — принимаем, 1 — повторить.
"""
from __future__ import annotations

import json
import sys


def route_started(result: dict) -> bool:
    usage = result.get("usage") or {}
    resolved = result.get("resolved") or {}
    stalled = resolved.get("provider") is None and (usage.get("api_calls") or 0) == 0
    return not stalled


def acceptable(result: dict) -> tuple[bool, str]:
    if not route_started(result):
        return False, "маршрут не стартовал"
    if not result.get("ok"):
        warnings = result.get("warnings") or []
        return False, (warnings[0] if warnings else "гейт не принял прогон")
    # Обёртка кладёт в пустой ответ строку-заглушку, и она не пуста как текст.
    # Проверка «непустой строки» на ней зеленеет — ровно тот случай, о котором
    # предупреждает сам скил: гейт выдаёт зелёное на пустом результате.
    body = (result.get("response") or "").strip()
    if not body or body in {"(empty)", "(пусто)"}:
        return False, "ответ пуст"
    return True, "принят"


if __name__ == "__main__":
    try:
        payload = json.load(open(sys.argv[1], encoding="utf-8"))
    except Exception:
        print("нет JSON")
        sys.exit(1)
    ok, why = acceptable(payload)
    if not ok:
        print(why)
    sys.exit(0 if ok else 1)
