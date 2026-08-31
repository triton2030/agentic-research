"""Open-enum hardening поверх запиненного openai-codex SDK.

ChatGPT.app авто-обновляет движок, а requirements.txt пинит SDK (0.144.4), так
что wire-протокол дрейфует под замороженной схемой: движок начинает слать
enum-значения, которых сгенерённые pydantic-модели не знают ('ultra' — 07.2026,
'max' — 2026-07-24), и валидация ThreadStartResponse роняла мост до старта
Codex. Этот модуль в рантайме делает строковые enum'ы схемы открытыми
(`_missing_`), чтобы устойчивость жила в репо, а не в ручных правках
.venv/site-packages (любой reinstall их стирает).

Апгрейд SDK этот модуль НЕ отменяет: upstream открывает enum'ы поштучно —
2 класса из 104 в `0.144.4` (`ReasoningEffort`, `ThreadSource`), 3 из 109 в
`0.147.0` (+`PlanType`). Живой дрейф на 2026-09-01: движок `0.151.0-alpha.7.2`
шлёт `SubAgentActivityKind='completed'`, которого не знает ни одна из этих
версий. Пока `openai/codex#21871` открыт, класс-за-классом остаётся правилом.

Модуль SDK-free на верхнем уровне: импортировать можно до scrub_billing_env,
сам SDK подтягивается только внутри harden_sdk_enums().
"""
from __future__ import annotations

import enum
import sys

# (имя enum-класса, значение) — warning печатается один раз на процесс.
_warned: set[tuple[str, str]] = set()


def _open_enum_missing(cls, value):  # noqa: ANN001
    """`_missing_`-хук: принять неизвестную строку как pseudo-member."""
    if not isinstance(value, str):
        return None
    member = object.__new__(cls)
    member._name_ = value
    member._value_ = value
    # Кэш членства: повторный parse того же значения вернёт тот же объект.
    cls._value2member_map_[value] = member
    key = (cls.__name__, value)
    if key not in _warned:
        _warned.add(key)
        print(
            f"[codex-bridge] SDK enum {cls.__name__} не знает значения {value!r} — "
            "принято терпимо (дрейф движка ChatGPT.app под запиненным SDK; "
            "см. codex_sdk_compat.py).",
            file=sys.stderr,
        )
    return member


def _has_custom_missing(cls: type[enum.Enum]) -> bool:
    """True, если у enum уже есть свой `_missing_` (открытый SDK или наш хук)."""
    return cls._missing_.__func__ is not enum.Enum._missing_.__func__  # type: ignore[attr-defined]


def harden_sdk_enums() -> list[str]:
    """Сделать все строковые enum'ы сгенерённой SDK-схемы открытыми.

    Идемпотентно (повторный вызов — no-op) и безопасно под тестовыми стабами:
    модуль без Enum-классов или без generated-схемы — no-op. Возвращает имена
    классов, которым хук навешен этим вызовом.
    """
    try:
        from openai_codex.generated import v2_all
    except ImportError as exc:
        # Частичный SDK (или стаб) — парсить ответы всё равно будет нечем;
        # hardening здесь best-effort слой, не гейт запуска.
        print(f"[codex-bridge] enum hardening пропущен: {exc}", file=sys.stderr)
        return []

    hardened: list[str] = []
    for name, obj in vars(v2_all).items():
        if not (isinstance(obj, type) and issubclass(obj, enum.Enum)):
            continue
        if getattr(obj, "__module__", None) != v2_all.__name__:
            continue  # импортированные в модуль классы (сам enum.Enum и пр.)
        if not all(isinstance(member.value, str) for member in obj):
            continue
        if _has_custom_missing(obj):
            continue  # уже открытый (SDK >= 0.144.x) или уже hardened
        obj._missing_ = classmethod(_open_enum_missing)  # type: ignore[method-assign]
        hardened.append(name)
    return sorted(hardened)
