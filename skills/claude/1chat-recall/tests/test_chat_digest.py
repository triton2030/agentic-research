"""Acceptance tests for lossless recall parsing and bounded BM25 retrieval."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
SPEC = importlib.util.spec_from_file_location("chat_digest_under_test", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import chat_digest.py")
DIGEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIGEST)

SESSION = "11111111-1111-4111-8111-111111111111"
FILE = f"""---
project: demo
date: 2026-07-14
agent: claude
model: claude-opus-5
session: {SESSION}
---

# Chat recall

* 2026-07-14T06:00:00+00:00 — "Канон живёт отдельно — с тире" — type: решение | topic: канон
* 10:55 — "Субагенты работают параллельно
и сохраняют контекст" — type: предпочтение | topic: мой-workflow
* 2026-07-15 — "Выбрал: локальный путь" — kind: selection | type: решение | topic: агентная-память | source: repaired | precision: date | source-ref: transcript.jsonl
* unknown — "Позднее пояснение" — kind: note | type: идея, коррекция | topic:  | source: unknown | precision: unknown
* сломанная строка, но она ценна
"""


class ChatDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.corpus = Path(self.temp.name)
        (self.corpus / "recall.md").write_text(FILE, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def call(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.corpus), *args],
            capture_output=True,
            text=True,
        )

    def test_every_star_block_is_a_record(self) -> None:
        records, diagnostics = DIGEST.load(self.corpus)
        self.assertEqual(len(records), FILE.count("\n* "))
        self.assertGreater(diagnostics, 0)
        self.assertEqual(records[-1]["kind"], "raw")
        self.assertIn("сломанная строка", records[-1]["text"])
        self.assertEqual(records[-1]["type"], "неопределено")
        self.assertEqual(records[-1]["topic"], "без-темы")

    def test_multiline_kinds_and_approximate_provenance(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        self.assertIn("параллельно\nи сохраняют", records[1]["text"])
        self.assertEqual(records[1]["precision"], "minute")
        self.assertIn("unmarked-approximate", records[1]["diagnostics"])
        self.assertEqual(records[2]["kind"], "selection")
        self.assertEqual(records[2]["precision"], "date")
        self.assertEqual(records[2]["source_ref"], "transcript.jsonl")
        self.assertEqual(records[3]["kind"], "note")
        self.assertEqual(records[3]["type"], "неопределено")

    def test_record_id_ignores_file_date_line_and_classification(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        original = records[0]["record_id"]
        changed = FILE.replace("date: 2026-07-14", "date: 2025-01-01").replace(
            "type: решение | topic: канон",
            "type: факт | topic: другое",
            1,
        )
        (self.corpus / "recall.md").unlink()
        (self.corpus / "renamed.md").write_text(
            changed.replace("# Chat recall", "\n\n# Chat recall"),
            encoding="utf-8",
        )
        changed_records, _ = DIGEST.load(self.corpus)
        self.assertEqual(original, changed_records[0]["record_id"])

    def test_bm25_prefix_filters_and_show_are_stable(self) -> None:
        query = self.call("--query", "субагент*", "--json")
        self.assertEqual(query.returncode, 0, query.stderr)
        envelope = json.loads(query.stdout)
        self.assertEqual(envelope["matched"], 1)
        record_id = envelope["records"][0]["record_id"]
        shown = self.call("--show", record_id, "--json")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout)["records"][0]["record_id"], record_id)
        filtered = self.call(
            "--query", "канон субагент*", "--topic", "канон", "--json"
        )
        self.assertEqual(json.loads(filtered.stdout)["matched"], 1)

    def test_bounded_json_and_zero_result(self) -> None:
        bounded = json.loads(self.call("--digest", "--limit", "2", "--json").stdout)
        self.assertEqual(bounded["total"], 5)
        self.assertEqual(bounded["returned"], 2)
        self.assertTrue(bounded["truncated"])
        self.assertIn("quality", bounded)
        tiny = self.call("--query", "субагент*", "--max-chars", "512", "--json")
        self.assertEqual(tiny.returncode, 0, tiny.stderr)
        self.assertLessEqual(len(tiny.stdout.rstrip("\n")), 512)
        self.assertTrue(json.loads(tiny.stdout)["truncated"])
        none = json.loads(self.call("--query", "несуществующее", "--json").stdout)
        self.assertEqual(none["selection"], "none")
        self.assertEqual(none["returned"], 0)

    def test_timeline_puts_unknown_last(self) -> None:
        data = json.loads(self.call("--timeline", "--json", "--limit", "20").stdout)
        self.assertEqual(data["records"][-1]["precision"], "unknown")

    def test_check_is_readable_and_strict_blocks_validation(self) -> None:
        check = self.call("--check")
        self.assertEqual(check.returncode, 0)
        self.assertIn("recall.md:", check.stdout)
        bounded = self.call("--check", "--max-chars", "512")
        self.assertLessEqual(len(bounded.stdout.rstrip("\n")), 512)
        strict = self.call("--check", "--strict")
        self.assertEqual(strict.returncode, 1)

    def test_cli_errors_are_short_without_traceback(self) -> None:
        for args in (
            ("--grep", "["),
            ("--since", "yesterday"),
            ("--head", "0", "--digest"),
        ):
            result = self.call(*args)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
