"""codex_sdk_compat: дрейф движка ChatGPT.app не должен ронять мост.

Регрессия 2026-07-24: движок начал слать reasoningEffort='max', закрытый enum
запиненного SDK его не знал, и pydantic-валидация ThreadStartResponse роняла
каждый запуск до старта Codex. Механизм проверяется на синтетических enum'ах
(без SDK в системном python), контракт с реальным SDK — интеграционными
тестами, активными при прогоне из .venv.
"""
from __future__ import annotations

import contextlib
import enum
import importlib.util
import io
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
# Wiring-тесты переиспользуют фейки соседних тестовых модулей; при запуске вне
# discovery (python -m unittest tests.test_codex_sdk_compat) tests/ нет в path.
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import codex_sdk_compat  # noqa: E402
from codex_sdk_compat import harden_sdk_enums  # noqa: E402

V2_MODULE = "openai_codex.generated.v2_all"


def _fake_sdk_modules(v2: types.ModuleType) -> dict[str, types.ModuleType]:
    """sys.modules-набор для `from openai_codex.generated import v2_all`."""
    mod = types.ModuleType("openai_codex")
    gen = types.ModuleType("openai_codex.generated")
    gen.v2_all = v2
    return {
        "openai_codex": mod,
        "openai_codex.generated": gen,
        V2_MODULE: v2,
    }


def _make_closed_enum(name: str, members: dict[str, str]) -> type[enum.Enum]:
    cls = enum.Enum(name, members)
    # harden берёт только классы, определённые в сгенерённом модуле схемы.
    cls.__module__ = V2_MODULE
    return cls


class HardenMechanismTest(unittest.TestCase):
    """Механизм open-enum на синтетической схеме — без установленного SDK."""

    def _harden_with(self, v2: types.ModuleType) -> list[str]:
        with mock.patch.dict(sys.modules, _fake_sdk_modules(v2)):
            with contextlib.redirect_stderr(io.StringIO()):
                return harden_sdk_enums()

    def test_unknown_string_value_admitted_and_cached(self) -> None:
        """Ядро регрессии 2026-07-24: неизвестное значение не роняет parse."""
        v2 = types.ModuleType(V2_MODULE)
        v2.ReasoningEffort = _make_closed_enum("ReasoningEffort", {"low": "low", "xhigh": "xhigh"})
        hardened = self._harden_with(v2)
        self.assertEqual(hardened, ["ReasoningEffort"])

        member = v2.ReasoningEffort("max")
        self.assertEqual(member.value, "max")
        self.assertEqual(member.name, "max")
        self.assertIsInstance(member, v2.ReasoningEffort)
        # Кэш членства: то же значение → тот же объект (identity-сравнения живы).
        self.assertIs(member, v2.ReasoningEffort("max"))

    def test_known_values_and_non_strings_untouched(self) -> None:
        v2 = types.ModuleType(V2_MODULE)
        v2.ReasoningEffort = _make_closed_enum("ReasoningEffort", {"low": "low"})
        self._harden_with(v2)
        self.assertIs(v2.ReasoningEffort("low"), v2.ReasoningEffort.low)
        with self.assertRaises(ValueError):
            v2.ReasoningEffort(42)

    def test_idempotent_second_call_is_noop(self) -> None:
        v2 = types.ModuleType(V2_MODULE)
        v2.Effort = _make_closed_enum("Effort", {"low": "low"})
        first = self._harden_with(v2)
        second = self._harden_with(v2)
        self.assertEqual(first, ["Effort"])
        self.assertEqual(second, [])

    def test_enum_with_own_missing_hook_kept(self) -> None:
        """Открытый SDK (>= 0.144.x) не перепатчивается — его хук остаётся."""
        sentinel = enum.Enum("Sentinel", {"a": "a"})

        class OpenEffort(enum.Enum):
            low = "low"

            @classmethod
            def _missing_(cls, value):  # noqa: ANN001
                return cls.low

        OpenEffort.__module__ = V2_MODULE
        own_hook = OpenEffort._missing_.__func__
        v2 = types.ModuleType(V2_MODULE)
        v2.OpenEffort = OpenEffort
        v2.Sentinel = sentinel  # __module__ чужой — тоже должен быть пропущен
        hardened = self._harden_with(v2)
        self.assertEqual(hardened, [])
        self.assertIs(OpenEffort._missing_.__func__, own_hook)

    def test_warns_once_per_enum_value(self) -> None:
        v2 = types.ModuleType(V2_MODULE)
        v2.Effort = _make_closed_enum("Effort", {"low": "low"})
        saved_warned = set(codex_sdk_compat._warned)
        try:
            with mock.patch.dict(sys.modules, _fake_sdk_modules(v2)):
                with contextlib.redirect_stderr(io.StringIO()):
                    harden_sdk_enums()
                buf = io.StringIO()
                with contextlib.redirect_stderr(buf):
                    v2.Effort("brand-new")
                    v2.Effort("brand-new")
                self.assertEqual(buf.getvalue().count("brand-new"), 1)
        finally:
            codex_sdk_compat._warned.clear()
            codex_sdk_compat._warned.update(saved_warned)

    def test_stub_module_without_enums_is_noop(self) -> None:
        """Паттерн существующих тестов моста: v2_all-стаб с lambda вместо enum."""
        v2 = types.ModuleType(V2_MODULE)
        v2.ReasoningEffort = lambda value: value
        self.assertEqual(self._harden_with(v2), [])

    def test_partial_sdk_without_generated_is_noop(self) -> None:
        """Стаб только openai_codex (как в test_codex_threads) — не падает.
        None в sys.modules даёт детерминированный ImportError для подмодуля."""
        mod = types.ModuleType("openai_codex")
        with mock.patch.dict(
            sys.modules,
            {"openai_codex": mod, "openai_codex.generated": None, V2_MODULE: None},
        ):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(harden_sdk_enums(), [])


class EntrypointWiringTest(unittest.TestCase):
    """Codex-ревью P2: удаление вызова harden_sdk_enums() из входа не ловилось
    ни одним тестом — механизм работал, но wiring был не защищён."""

    def _run_entrypoint_capturing_order(self, module_name: str, argv: list[str]) -> None:
        """Прогон main() со стабом SDK: harden обязан быть вызван, и вызван
        ДО thread_start (иначе первый же ответ движка минует hardening)."""
        import importlib

        entry = importlib.import_module(module_name)
        if module_name == "codex_review":
            from test_codex_review import _install_fake_openai_codex
        else:
            from test_codex_investigate import _install_fake_openai_codex

        captured: dict = {}
        fake_names = _install_fake_openai_codex(captured)
        saved_argv = sys.argv[:]
        billing_keys = ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL")
        saved_env = {key: os.environ.get(key) for key in billing_keys}

        def _harden_spy() -> list[str]:
            self.assertEqual(
                captured, {},
                "harden_sdk_enums() вызван ПОСЛЕ первого SDK-вызова — "
                "ответ движка минует hardening",
            )
            return []

        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                sys.argv = [f"{module_name}.py", *argv, "--project", str(root)]
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), mock.patch.object(
                    entry, "harden_sdk_enums", side_effect=_harden_spy
                ) as harden_mock, mock.patch.object(
                    entry, "resolve_codex_bin", return_value="/sentinel/chatgpt/codex"
                ):
                    rc = entry.main()
            self.assertEqual(rc, 0)
            self.assertTrue(harden_mock.called, f"{module_name}.main() не вызвал harden_sdk_enums()")
            self.assertIn("run_kwargs", captured)  # SDK-путь дошёл до thread.run
        finally:
            sys.argv = saved_argv
            for name in fake_names:
                sys.modules.pop(name, None)
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_review_main_calls_harden_before_thread_start(self) -> None:
        self._run_entrypoint_capturing_order(
            "codex_review", ["--task", "посмотри на codex_review.py"]
        )

    def test_investigate_main_calls_harden_before_thread_start(self) -> None:
        self._run_entrypoint_capturing_order(
            "codex_investigate", ["--task", "изучи проект", "--heartbeat-sec", "0"]
        )

    def test_all_entrypoints_wire_harden_in_source(self) -> None:
        """Инвариант AGENTS «каждый вход зовёт harden_sdk_enums()» — страховка
        для orchestrate/threads, где полный runtime-прогон требует git/archive
        скаффолдинга."""
        for entry in ("codex_review", "codex_investigate", "codex_orchestrate", "codex_threads"):
            source = (BACKEND / f"{entry}.py").read_text(encoding="utf-8")
            self.assertIn(
                "harden_sdk_enums()", source,
                f"{entry}.py не вызывает harden_sdk_enums() — инвариант AGENTS нарушен",
            )


@unittest.skipUnless(
    importlib.util.find_spec("openai_codex") is not None,
    "openai-codex SDK не установлен (прогони тесты интерпретатором .venv)",
)
class HardenRealSdkTest(unittest.TestCase):
    """Контракт с реальным запиненным SDK — активен из .venv."""

    def test_reasoning_effort_option_parses_unknown_value(self) -> None:
        """Точный слой падения 2026-07-24: pydantic-модель с ReasoningEffort
        принимает значение, которого нет в enum, и сохраняет его дословно."""
        from openai_codex.generated.v2_all import ReasoningEffort, ReasoningEffortOption

        with contextlib.redirect_stderr(io.StringIO()):
            harden_sdk_enums()
            parsed = ReasoningEffortOption.model_validate(
                {"description": "d", "reasoningEffort": "zz-unknown-effort-probe"}
            )
        self.assertEqual(parsed.reasoning_effort.value, "zz-unknown-effort-probe")
        self.assertIsInstance(parsed.reasoning_effort, ReasoningEffort)

    def test_bridge_effort_ceiling_survives_sdk_reinstall(self) -> None:
        """--effort ultra не должен зависеть от ручного патча venv: после
        hardening ReasoningEffort('ultra') работает и на pristine SDK."""
        from openai_codex.generated.v2_all import ReasoningEffort

        from codex_defaults import REASONING_EFFORTS

        with contextlib.redirect_stderr(io.StringIO()):
            harden_sdk_enums()
            for effort in REASONING_EFFORTS:
                self.assertEqual(ReasoningEffort(effort).value, effort)


if __name__ == "__main__":
    unittest.main()
