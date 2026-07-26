"""Tests for chat_digest.py: parsing, inventory, digest filters, addresses."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
MODULE_SPEC = importlib.util.spec_from_file_location("chat_digest_under_test", SCRIPT)
if MODULE_SPEC is None or MODULE_SPEC.loader is None:
    raise RuntimeError("cannot load chat_digest.py")
CHAT_DIGEST = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(CHAT_DIGEST)

FILE_A = """---
project: demo
date: 2026-07-14
types:
  - решение
topics:
  - Канон
---

# Chat recall — 2026-07-14 — claude aaaa1111

* 2026-07-14T06:00:00.000000+00:00 — "Канон живёт отдельно — с тире внутри цитаты" — type: решение | topic: Канон
* 2026-07-14T07:00:00.000000+00:00 — "запускай много агентов параллельно" — type: предпочтение | topic: мой-workflow
"""

FILE_B = """---
project: demo
date: 2026-07-20
---

# Chat recall — 2026-07-20 — codex bbbb2222

* 2026-07-20T10:00:00.000000+00:00 — "проекции канона не вторая истина" — type: правило-кандидат | topic: Канон
* сломанная строка без формата
"""


class ChatDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.corpus = Path(self.temp.name)
        (self.corpus / "2026-07-14-060000-claude-aaaa1111.md").write_text(FILE_A)
        (self.corpus / "2026-07-20-100000-codex-bbbb2222.md").write_text(FILE_B)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.corpus), *args],
            capture_output=True,
            text=True,
        )

    def test_load_parses_quotes_and_counts_unparsed(self) -> None:
        rows, unparsed = CHAT_DIGEST.load(self.corpus)
        self.assertEqual(len(rows), 3)
        self.assertEqual(unparsed, 1)
        first = rows[0]
        self.assertEqual(first["topic"], "Канон")
        self.assertEqual(first["line"], 12)
        # тире внутри цитаты не рвёт парсинг
        self.assertIn("с тире внутри цитаты", first["quote"])

    def test_inventory_is_default_and_reports_drift_surface(self) -> None:
        result = self.run_script()
        self.assertEqual(result.returncode, 0)
        self.assertIn("Канон", result.stdout)
        self.assertIn("всего 3 цитат / 2 topics", result.stdout)
        self.assertIn("1 строк не распарсено", result.stdout)

    def test_type_filter_implies_digest_with_addresses(self) -> None:
        result = self.run_script("--type", "правило-кандидат,предпочтение")
        self.assertEqual(result.returncode, 0)
        self.assertIn("=== 2026-07-14-060000-claude-aaaa1111.md", result.stdout)
        self.assertIn("L13", result.stdout)  # адрес строки предпочтения
        self.assertNotIn("решение", result.stdout)
        self.assertIn("2/3 цитат", result.stderr)

    def test_grep_filter_and_head_clipping(self) -> None:
        result = self.run_script("--grep", "канон", "--head", "10")
        self.assertEqual(result.returncode, 0)
        self.assertIn("проекции к…", result.stdout)
        self.assertNotIn("агентов", result.stdout)

    def test_since_filter(self) -> None:
        result = self.run_script("--since", "2026-07-20")
        self.assertIn("правило-кандидат"[:4], result.stdout)
        self.assertNotIn("07-14", result.stdout)

    def test_empty_corpus_fails_loud(self) -> None:
        empty = self.corpus / "sub"
        empty.mkdir()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(empty)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("нет распознанных цитат", result.stderr)


if __name__ == "__main__":
    unittest.main()
