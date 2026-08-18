"""Проверка здоровья движка без единого оплаченного turn-а.

Зачем. Мост наследует часть runtime не из своего кода, а из общего `~/.codex`,
который делит с Codex Desktop: авторизацию, эффективный конфиг и — что важнее
всего — `service_tier`, потому что его мы намеренно НЕ шлём. Ledger фиксирует
запрошенное, а не применённое, поэтому вопрос «на каком тире и под каким
аккаунтом мы сейчас работаем» до этого модуля не имел ответа вообще.

Оба вызова (`account/read`, `config/read`) — служебные RPC, кредиты не тратят.

Сюда же приклеен локальный скан следа моста СНАРУЖИ (`codex_footprint.py`):
он не требует движка и печатается даже тогда, когда RPC не ответили.

Ответы читаются СЫРЫМИ (`_request_raw`), без pydantic-моделей: движок
ChatGPT.app опережает запиненную схему (см. `codex_sdk_compat.py`), и
диагностика обязана переживать дрейф, а не падать на нём первой.
"""
from __future__ import annotations

from typing import Any

from codex_defaults import (
    DEFAULT_CODEX_MODEL,
    codex_bin_source,
    resolve_codex_bin,
)
from codex_footprint import scan as scan_footprint


def _dig(node: Any, *path: str) -> Any:
    """Достать вложенное поле, не веря в форму ответа."""
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def check(*, cwd: str, codex_bin: str | None = None) -> dict[str, Any]:
    """Снимок runtime: авторизация, эффективный конфиг, движок, предупреждения."""
    from openai_codex import Codex, CodexConfig  # импорт после scrub_billing_env

    from codex_sdk_compat import harden_sdk_enums

    harden_sdk_enums()

    if codex_bin is None:
        codex_bin = resolve_codex_bin()

    # След — локальный скан диска: он обязан дожить до вывода даже тогда, когда
    # движок молчит, потому что именно эту грязь наши тесты не видят вообще.
    footprint = scan_footprint()

    report: dict[str, Any] = {
        "engine": {"codex_bin": codex_bin, "binary_source": codex_bin_source(codex_bin)},
        "auth": {},
        "config": {},
        "footprint": footprint,
        "warnings": [],
        "ok": False,
    }

    try:
        with Codex(CodexConfig(cwd=cwd, codex_bin=codex_bin)) as codex:
            client = codex._client  # noqa: SLF001 — сырой RPC нужен ради дрейфа схемы
            account = client._request_raw("account/read", {"refreshToken": False})  # noqa: SLF001
            config = client._request_raw(  # noqa: SLF001
                "config/read", {"cwd": cwd, "includeLayers": False}
            )
    except Exception as exc:  # noqa: BLE001 — диагностика не имеет права падать
        report["error"] = str(exc)
        report["warnings"].append(
            "движок не ответил на служебные RPC — до платного прогона дело не дойдёт"
        )
        return report

    report.update(interpret(account, config))
    report["footprint"] = footprint
    return report


def interpret(account: Any, config: Any) -> dict[str, Any]:
    """Разбор ответов в вердикт. Чистая функция — тестируется без движка.

    Форма ответа движка дрейфует, поэтому НИ ОДНО поле не считается словарём
    без проверки: неизвестная форма обязана стать видимым warning, а не тихим
    «всё None, но ok».
    """
    result: dict[str, Any] = {"auth": {}, "config": {}, "warnings": [], "ok": False}
    warnings: list[str] = result["warnings"]

    acc = _dig(account, "account")
    if acc is not None and not isinstance(acc, dict):
        warnings.append("account/read вернул неизвестную форму — разбор невозможен")
        acc = None
    acc = acc or {}
    result["auth"] = {
        # Живая форма (замер 2026-07-28): {"account": {"type": "chatgpt",
        # "email": …, "planType": "plus"}, "requiresOpenaiAuth": true}.
        # `requiresOpenaiAuth` — норма, НЕ повод для предупреждения.
        "present": bool(acc),
        "mode": acc.get("type") or acc.get("authMode"),
        "plan": acc.get("planType") or acc.get("plan_type"),
        "email": acc.get("email"),
    }

    cfg = _dig(config, "config")
    if cfg is None:
        cfg = config
    config_unknown = not isinstance(cfg, dict)
    if config_unknown:
        warnings.append("config/read вернул неизвестную форму — эффективный конфиг не прочитан")
        cfg = {}
    effective_tier = cfg.get("serviceTier") or cfg.get("service_tier")
    result["config"] = {
        "model": cfg.get("model"),
        "effort": cfg.get("modelReasoningEffort") or cfg.get("model_reasoning_effort"),
        # Единственное поле, которое мост реально НАСЛЕДУЕТ, а не задаёт сам.
        "inherited_service_tier": effective_tier,
        "sandbox_mode": cfg.get("sandboxMode") or cfg.get("sandbox_mode"),
        "approval_policy": cfg.get("approvalPolicy") or cfg.get("approval_policy"),
    }

    blocking = config_unknown
    mode = result["auth"]["mode"]
    if not result["auth"]["present"]:
        warnings.append("аккаунт не прочитан — вероятно, требуется вход в Codex")
        blocking = True
    elif mode != "chatgpt":
        warnings.append(
            f"account.type={mode!r}, а не 'chatgpt' — инвариант биллинга под угрозой: "
            "прогоны могут уйти на платный API"
        )
        blocking = True
    if effective_tier and effective_tier not in {"default", "standard"}:
        warnings.append(
            f"наследуемый service_tier={effective_tier!r} — прогоны пойдут не на "
            "стандартном тире (мост тир не шлёт, он берётся отсюда)"
        )

    result["ok"] = not blocking
    return result



def render(report: dict[str, Any]) -> str:
    """Человекочитаемая сводка: несколько строк, не дамп."""
    lines = []
    auth = report.get("auth", {})
    cfg = report.get("config", {})
    engine = report.get("engine", {})

    lines.append(f"движок: {engine.get('binary_source')} ({engine.get('codex_bin') or 'бандл SDK'})")
    if report.get("error"):
        lines.append(f"ОШИБКА: {report['error']}")
    else:
        lines.append(
            f"аккаунт: mode={auth.get('mode')} plan={auth.get('plan')} "
            f"{auth.get('email') or ''}".rstrip()
        )
        lines.append(
            f"конфиг: model={cfg.get('model')} effort={cfg.get('effort')} "
            f"sandbox={cfg.get('sandbox_mode')} approval={cfg.get('approval_policy')}"
        )
        lines.append(
            f"наследуемый service_tier: {cfg.get('inherited_service_tier') or '—'} "
            f"(мост его не шлёт; модель мост задаёт сам: {DEFAULT_CODEX_MODEL})"
        )
    foot = report.get("footprint") or {}
    orphans, dead = foot.get("orphan_threads", 0), foot.get("dead_project_entries", 0)
    lines.append(
        f"след моста снаружи: тредов на удалённых папках — {orphans}; "
        f"мёртвых записей в config.toml — {dead} (косметика, не чиним)"
    )
    if orphans:
        # Каждый такой тред — карточка проекта в Codex, ведущая в никуда.
        lines.append(f"  ↳ пример: {(foot.get('orphan_thread_samples') or ['—'])[0]}")
        lines.append("  ↳ убрать: codex_threads.py archive --orphaned --project \"$PWD\"")
    for warning in report.get("warnings", []):
        lines.append(f"  ⚠ {warning}")
    lines.append(f"итог: {'ok' if report.get('ok') else 'ТРЕБУЕТ ВНИМАНИЯ'}")
    return "\n".join(lines)
