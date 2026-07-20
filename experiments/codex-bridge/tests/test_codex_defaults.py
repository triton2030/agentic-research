from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

import codex_defaults


class ResolveCodexBinTests(unittest.TestCase):
    def test_prefers_chatgpt_app_binary_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = Path(tmp) / "codex"
            fake_bin.write_bytes(b"")
            with mock.patch.object(codex_defaults, "CHATGPT_APP_CODEX_BIN", str(fake_bin)):
                self.assertEqual(codex_defaults.resolve_codex_bin(), str(fake_bin))

    def test_falls_back_to_sdk_bundle_when_app_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "codex"
            with mock.patch.object(codex_defaults, "CHATGPT_APP_CODEX_BIN", str(missing)):
                self.assertIsNone(codex_defaults.resolve_codex_bin())

    def test_directory_at_binary_path_is_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(codex_defaults, "CHATGPT_APP_CODEX_BIN", tmp):
                self.assertIsNone(codex_defaults.resolve_codex_bin())

    def test_binary_source_labels(self) -> None:
        self.assertEqual(codex_defaults.codex_bin_source("/x/codex"), "chatgpt-app")
        self.assertEqual(codex_defaults.codex_bin_source(None), "sdk-bundle")


class ServiceTierDefaultTests(unittest.TestCase):
    def test_default_service_tier_is_priority(self) -> None:
        # The bridge must ALWAYS run fast; a drift of this default silently slows
        # every background run. "priority" = how the current engine encodes fast.
        self.assertEqual(codex_defaults.DEFAULT_CODEX_SERVICE_TIER, "priority")

    def test_fast_mode_feature_gate_forced(self) -> None:
        # Tier alone is a no-op unless features.fast_mode is on; the bridge must
        # force the gate so "always fast" does not depend on the user's config.
        self.assertIn(
            "features.fast_mode=true", codex_defaults.FAST_MODE_CONFIG_OVERRIDES
        )


if __name__ == "__main__":
    unittest.main()
