"""Preflight: разбор ответов движка и вердикт.

`interpret` — чистая функция, поэтому проверяется без движка и без кредитов.
Предмет тестов: живая форма ответа (замер 2026-07-28), отсутствие ложных
тревог и — главное — что НЕИЗВЕСТНАЯ форма становится видимым отказом, а не
тихим «все поля None, но ok».
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from codex_preflight import interpret, render  # noqa: E402

LIVE_ACCOUNT = {
    "account": {"type": "chatgpt", "email": "user@example.com", "planType": "plus"},
    "requiresOpenaiAuth": True,
}
LIVE_CONFIG = {
    "config": {
        "model": "gpt-5.6-sol",
        "model_reasoning_effort": "xhigh",
        "service_tier": None,
        "sandbox_mode": "danger-full-access",
        "approval_policy": "never",
    }
}


class PreflightInterpretTests(unittest.TestCase):
    def test_live_shape_is_ok_without_false_alarms(self) -> None:
        r = interpret(LIVE_ACCOUNT, LIVE_CONFIG)
        self.assertTrue(r["ok"])
        self.assertEqual(r["auth"]["mode"], "chatgpt")
        self.assertEqual(r["auth"]["plan"], "plus")
        self.assertEqual(r["config"]["model"], "gpt-5.6-sol")
        self.assertIsNone(r["config"]["inherited_service_tier"])
        # requiresOpenaiAuth=true — норма движка; предупреждать на неё нельзя.
        self.assertEqual(r["warnings"], [])

    def test_non_chatgpt_auth_is_blocking(self) -> None:
        """Инвариант биллинга: любой не-chatgpt режим обязан валить вердикт."""
        r = interpret({"account": {"type": "apikey"}}, LIVE_CONFIG)
        self.assertFalse(r["ok"])
        self.assertTrue(any("биллинг" in w for w in r["warnings"]))

    def test_missing_account_is_blocking(self) -> None:
        r = interpret({}, LIVE_CONFIG)
        self.assertFalse(r["ok"])
        self.assertTrue(any("аккаунт не прочитан" in w for w in r["warnings"]))

    def test_unknown_config_shape_fails_loudly(self) -> None:
        """Дрейф схемы не должен превращаться в тихое зелёное."""
        for broken in (["not", "a", "dict"], "строка", 42):
            with self.subTest(broken=broken):
                r = interpret(LIVE_ACCOUNT, broken)
                self.assertFalse(r["ok"], broken)
                self.assertTrue(
                    any("config/read" in w for w in r["warnings"]), r["warnings"]
                )

    def test_unknown_account_shape_does_not_crash(self) -> None:
        r = interpret({"account": ["сюрприз"]}, LIVE_CONFIG)
        self.assertFalse(r["ok"])
        self.assertTrue(any("account/read" in w for w in r["warnings"]))

    def test_non_standard_inherited_tier_warns_but_does_not_block(self) -> None:
        cfg = {"config": dict(LIVE_CONFIG["config"], service_tier="priority")}
        r = interpret(LIVE_ACCOUNT, cfg)
        self.assertTrue(r["ok"])
        self.assertTrue(any("service_tier" in w for w in r["warnings"]))

    def test_render_survives_error_report(self) -> None:
        text = render({"engine": {"binary_source": "chatgpt-app"}, "error": "нет связи"})
        self.assertIn("ОШИБКА", text)
        self.assertIn("ТРЕБУЕТ ВНИМАНИЯ", text)


if __name__ == "__main__":
    unittest.main()
