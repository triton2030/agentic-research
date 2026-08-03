"""Acceptance tests for lossless parsing and bounded hybrid recall retrieval."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "chat_digest.py"
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
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

* 2026-07-14T06:00:00+00:00 — "Канон живёт отдельно — с тире" — type: решение | topic: документация-и-знания
* 10:55 — "Субагенты работают параллельно
и сохраняют контекст" — type: предпочтение | topic: мой-workflow
* 2026-07-15 — "Выбрал: локальный путь" — kind: selection | type: решение | \
topic: работа-и-процессы | source: repaired | precision: date | source-ref: transcript.jsonl
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
        command = list(args)
        if "--query" in command and "--lexical" not in command:
            command.append("--lexical")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.corpus), *command],
            capture_output=True,
            text=True,
            check=False,
        )

    def call_default(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.corpus), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def write_entries(self, entries: list[str]) -> None:
        content = (
            "---\n"
            "project: demo\n"
            "date: 2026-07-01\n"
            "agent: codex\n"
            "model: gpt-5.6\n"
            f"session: {SESSION}\n"
            "---\n\n"
            "# Chat recall\n\n"
            + "\n".join(entries)
            + "\n"
        )
        (self.corpus / "recall.md").write_text(content, encoding="utf-8")

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
        self.assertEqual(records[1]["topic"], "без-темы")
        self.assertEqual(records[1]["topic_raw"], "мой-workflow")
        self.assertIn("invalid-topic", records[1]["diagnostics"])
        self.assertEqual(records[2]["kind"], "selection")
        self.assertEqual(records[2]["precision"], "date")
        self.assertEqual(records[2]["source_ref"], "transcript.jsonl")
        self.assertEqual(records[3]["kind"], "note")
        self.assertEqual(records[3]["type"], "неопределено")

    def test_record_id_ignores_file_date_line_and_classification(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        original = records[0]["record_id"]
        changed = FILE.replace("date: 2026-07-14", "date: 2025-01-01").replace(
            "type: решение | topic: документация-и-знания",
            "type: факт | topic: архитектура-и-модель",
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
        self.assertEqual(query.stderr, "")
        envelope = json.loads(query.stdout)
        self.assertEqual(envelope["matched"], 1)
        self.assertEqual(envelope["retrieval"], "lexical")
        self.assertTrue(envelope["retrieval_complete"])
        self.assertEqual(envelope["candidate_count"], 1)
        record_id = envelope["records"][0]["record_id"]
        shown = self.call("--show", record_id, "--json")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout)["records"][0]["record_id"], record_id)
        filtered = self.call(
            "--query",
            "канон субагент*",
            "--topic",
            "документация-и-знания",
            "--json",
        )
        self.assertEqual(json.loads(filtered.stdout)["matched"], 1)

    def test_human_query_hides_score_unless_verbose(self) -> None:
        compact = self.call("--query", "субагент*")
        self.assertEqual(compact.returncode, 0, compact.stderr)
        self.assertIn(
            "1/1 candidates shown · 5 records · retrieval=lexical",
            compact.stdout,
        )
        self.assertIn("2026-07-14", compact.stdout)
        self.assertNotIn("score=", compact.stdout)
        self.assertNotIn("recall.md:", compact.stdout)
        self.assertEqual(compact.stderr, "")

        verbose = self.call("--query", "субагент*", "--verbose")
        self.assertEqual(verbose.returncode, 0, verbose.stderr)
        self.assertIn("score=", verbose.stdout)

    def test_human_show_is_compact_and_verbose_preserves_full_record(self) -> None:
        record_id = json.loads(self.call("--query", "канон", "--json").stdout)[
            "records"
        ][0]["record_id"]

        compact = self.call("--show", record_id)
        self.assertEqual(compact.returncode, 0, compact.stderr)
        self.assertEqual(compact.stdout.count("Канон живёт отдельно"), 1)
        self.assertIn(f"record={record_id}", compact.stdout)
        self.assertIn("diagnostics=none", compact.stdout)
        self.assertNotIn('"quote"', compact.stdout)
        self.assertNotIn("type_raw=", compact.stdout)
        self.assertNotIn("topic_raw=", compact.stdout)
        self.assertEqual(compact.stderr, "")

        verbose = self.call("--show", record_id, "--verbose")
        self.assertEqual(verbose.returncode, 0, verbose.stderr)
        full_record = json.loads(verbose.stdout)
        self.assertEqual(full_record["record_id"], record_id)
        self.assertIn("quote", full_record)

    def test_invalid_topic_is_visible_and_searchable(self) -> None:
        check = self.call("--check")
        self.assertIn("invalid-topic", check.stdout)
        found = json.loads(self.call("--query", "мой-workflow", "--json").stdout)
        self.assertEqual(found["matched"], 1)
        self.assertEqual(found["records"][0]["topic"], "без-темы")
        self.assertEqual(found["records"][0]["topic_raw"], "мой-workflow")
        shown_topic = self.call("--show", found["records"][0]["record_id"])
        self.assertIn("topic_raw=мой-workflow", shown_topic.stdout)

        invalid_type = json.loads(
            self.call("--query", "Позднее", "--json").stdout
        )["records"][0]
        shown_type = self.call("--show", invalid_type["record_id"])
        self.assertIn("type_raw=идея, коррекция", shown_type.stdout)

    def test_controlled_vocabulary_is_shared(self) -> None:
        self.assertEqual(len(DIGEST.TYPES), 9)
        self.assertEqual(len(DIGEST.TOPICS), 21)
        self.assertIn("неопределено", DIGEST.TYPES)
        self.assertIn("без-темы", DIGEST.TOPICS)

    def test_bounded_json_and_zero_result(self) -> None:
        bounded = json.loads(self.call("--digest", "--limit", "2", "--json").stdout)
        self.assertEqual(bounded["total"], 5)
        self.assertEqual(bounded["returned"], 2)
        self.assertTrue(bounded["truncated"])
        self.assertEqual(bounded["truncated_by"], "limit")
        self.assertIn("quality", bounded)
        human_limited = self.call("--digest", "--limit", "2")
        self.assertTrue(
            human_limited.stdout.startswith(
                "2/5 records shown · 5 records · truncated by --limit"
            )
        )
        tiny = self.call("--query", "субагент*", "--max-chars", "512", "--json")
        self.assertEqual(tiny.returncode, 0, tiny.stderr)
        self.assertLessEqual(len(tiny.stdout.rstrip("\n")), 512)
        tiny_payload = json.loads(tiny.stdout)
        self.assertTrue(tiny_payload["truncated"])
        self.assertEqual(tiny_payload["truncated_by"], "max_chars")
        none_result = self.call_default("--query", "несуществующее", "--json")
        self.assertEqual(none_result.returncode, 0, none_result.stderr)
        none = json.loads(none_result.stdout)
        self.assertEqual(none["selection"], "none")
        self.assertEqual(none["returned"], 0)
        self.assertIsNone(none["truncated_by"])
        self.assertEqual(none["retrieval"], "hybrid")

    def test_help_explains_limit_head_and_character_budget(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("maximum records", result.stdout)
        self.assertIn("human-readable excerpt", result.stdout)
        self.assertIn("ignored with --json", result.stdout)
        self.assertIn("may return fewer records than --limit", result.stdout)

    def test_human_bound_uses_rendered_digest_not_full_json(self) -> None:
        self.write_entries(
            [
                (
                    f'* 2026-07-01T{hour:02d}:00:00+00:00 — '
                    f'"Needle {hour} {"detail " * 350}" '
                    "— type: решение | topic: документация-и-знания"
                )
                for hour in range(5)
            ]
        )

        human = self.call(
            "--query", "Needle", "--limit", "5", "--max-chars", "4000"
        )
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertTrue(human.stdout.startswith("5/5 candidates shown · 5 records"))
        self.assertLessEqual(len(human.stdout.rstrip("\n")), 4000)

        character_limited = self.call(
            "--query", "Needle", "--limit", "5", "--max-chars", "512"
        )
        self.assertEqual(character_limited.returncode, 0, character_limited.stderr)
        self.assertIn(
            "truncated by --max-chars",
            character_limited.stdout.splitlines()[0],
        )

        machine = json.loads(
            self.call(
                "--query",
                "Needle",
                "--limit",
                "5",
                "--max-chars",
                "4000",
                "--json",
            ).stdout
        )
        self.assertLess(machine["returned"], 5)
        self.assertTrue(machine["truncated"])
        self.assertEqual(machine["truncated_by"], "max_chars")

    def test_human_bound_never_turns_matches_into_abstention(self) -> None:
        self.write_entries(
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — '
                    f'"Needle {"detail " * 500}" '
                    "— type: решение | topic: документация-и-знания"
                )
            ]
        )

        result = self.call(
            "--query",
            "Needle",
            "--head",
            "10000",
            "--max-chars",
            "512",
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("первая запись не помещается", result.stderr)
        self.assertNotIn("selection=none", result.stderr)

    def test_timeline_puts_unknown_last(self) -> None:
        data = json.loads(self.call("--timeline", "--json", "--limit", "20").stdout)
        self.assertEqual(data["order"], "newest-first")
        self.assertEqual(data["records"][0]["timestamp"], "2026-07-15")
        self.assertEqual(data["records"][-1]["precision"], "unknown")

    def test_timeline_limit_keeps_newest_query_matches(self) -> None:
        self.write_entries(
            [
                (
                    f'* 2026-07-01T{hour:02d}:00:00+00:00 — "Position {hour:02d}" '
                    "— type: решение | topic: работа-и-процессы"
                )
                for hour in range(15)
            ]
        )

        data = json.loads(
            self.call(
                "--query",
                "Position",
                "--timeline",
                "--limit",
                "12",
                "--max-chars",
                "20000",
                "--json",
            ).stdout
        )

        self.assertEqual(data["matched"], 15)
        self.assertEqual(data["returned"], 12)
        self.assertTrue(data["truncated"])
        self.assertEqual(data["truncated_by"], "limit")
        self.assertEqual(data["records"][0]["text"], "Position 14")
        self.assertEqual(data["records"][-1]["text"], "Position 03")

    def test_timeline_ties_are_stable_and_unknown_is_not_duplicated(self) -> None:
        self.write_entries(
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Earlier line" '
                    "— type: решение | topic: работа-и-процессы"
                ),
                (
                    '* 2026-07-01T10:00:00+00:00 — "Later line" '
                    "— type: коррекция | topic: работа-и-процессы"
                ),
                (
                    '* 2026-07-02T10:00:00+00:00 — "Unknown precision" '
                    "— type: факт | topic: работа-и-процессы | "
                    "source: repaired | precision: unknown"
                ),
                (
                    '* unknown — "Unknown timestamp" — kind: note | '
                    "type: идея | topic: работа-и-процессы | "
                    "source: unknown | precision: unknown"
                ),
            ]
        )

        records = json.loads(
            self.call("--timeline", "--json", "--limit", "20").stdout
        )["records"]
        texts = [record["text"] for record in records]

        self.assertEqual(texts[:2], ["Later line", "Earlier line"])
        self.assertEqual(texts.count("Unknown precision"), 1)
        self.assertEqual(
            [record["precision"] for record in records[-2:]],
            ["unknown", "unknown"],
        )

    def test_timeline_character_bound_keeps_newest_match(self) -> None:
        self.write_entries(
            [
                (
                    f'* 2026-07-{day:02d}T10:00:00+00:00 — '
                    f'"Память {day:02d} {"деталь " * 14}" '
                    "— type: решение | topic: документация-и-знания"
                )
                for day in range(1, 9)
            ]
        )

        data = json.loads(
            self.call(
                "--query",
                "Память",
                "--timeline",
                "--limit",
                "20",
                "--max-chars",
                "900",
                "--json",
            ).stdout
        )

        self.assertEqual(data["matched"], 8)
        self.assertTrue(data["truncated"])
        self.assertEqual(data["truncated_by"], "max_chars")
        self.assertTrue(data["records"][0]["text"].startswith("Память 08"))

    def test_check_is_readable_and_strict_blocks_validation(self) -> None:
        check = self.call("--check")
        self.assertEqual(check.returncode, 0)
        records, diagnostic_count = DIGEST.load(self.corpus)
        self.assertTrue(
            check.stdout.startswith(
                f"{diagnostic_count} records with diagnostics · "
                f"{len(records)} records"
            )
        )
        self.assertIn("recall.md:", check.stdout)
        self.assertNotIn("returned/matched/total", check.stdout + check.stderr)
        bounded = self.call("--check", "--max-chars", "512")
        self.assertLessEqual(len(bounded.stdout.rstrip("\n")), 512)
        strict = self.call("--check", "--strict")
        self.assertEqual(strict.returncode, 1)

    def test_check_truncation_counts_visible_diagnostics(self) -> None:
        self.write_entries([f"* broken record {index:02d}" for index in range(20)])

        check = self.call("--check", "--max-chars", "512")
        self.assertEqual(check.returncode, 0, check.stderr)
        lines = check.stdout.splitlines()
        self.assertRegex(
            lines[0],
            r"^\d+/20 records with diagnostics shown · 20 records · truncated$",
        )
        shown = int(lines[0].split("/", 1)[0])
        self.assertEqual(len(lines) - 1, shown)

    def test_global_bounds_validate_check_and_inventory(self) -> None:
        for args in (("--check", "--max-chars", "511"), ("--limit", "0")):
            with self.subTest(args=args):
                result = self.call(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")

    def test_query_defaults_to_hybrid_and_lexical_is_explicit(self) -> None:
        default = DIGEST.build_parser().parse_args(
            [str(self.corpus), "--query", "канон"]
        )
        lexical = DIGEST.build_parser().parse_args(
            [str(self.corpus), "--query", "канон", "--lexical"]
        )

        self.assertFalse(default.lexical)
        self.assertTrue(lexical.lexical)

    def test_hybrid_abstains_before_loading_dense_model(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        with mock.patch.object(DIGEST, "search_dense") as dense:
            result = DIGEST.search_hybrid(records, "несуществующее")

        self.assertEqual(result, [])
        dense.assert_not_called()

    def test_hybrid_rrf_uses_addresses_not_duplicate_record_ids(self) -> None:
        records = [
            {"address": "a.md:1", "record_id": "duplicate"},
            {"address": "b.md:1", "record_id": "duplicate"},
            {"address": "c.md:1", "record_id": "unique"},
        ]
        lexical = [dict(records[0]), dict(records[1])]
        dense = [dict(records[1]), dict(records[2])]
        with (
            mock.patch.object(DIGEST, "search_bm25", return_value=lexical),
            mock.patch.object(DIGEST, "search_dense", return_value=dense),
        ):
            result = DIGEST.search_hybrid(records, "query")

        self.assertEqual(
            [record["address"] for record in result],
            ["b.md:1", "a.md:1", "c.md:1"],
        )
        self.assertEqual(
            [record["record_id"] for record in result].count("duplicate"),
            2,
        )

    def test_filters_run_before_hybrid_ranking(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        args = DIGEST.build_parser().parse_args(
            [
                str(self.corpus),
                "--query",
                "канон",
                "--topic",
                "документация-и-знания",
            ]
        )
        with mock.patch.object(DIGEST, "search_hybrid", return_value=[]) as hybrid:
            _, retrieval = DIGEST._retrieve(records, args)

        ranked_records = hybrid.call_args.args[0]
        self.assertEqual(retrieval, "hybrid")
        self.assertTrue(ranked_records)
        self.assertTrue(
            all(
                record["topic"] == "документация-и-знания"
                for record in ranked_records
            )
        )

    def test_embedding_cache_contains_hashes_and_vectors_not_quote_text(self) -> None:
        path = self.corpus / "cache" / "embeddings.sqlite3"
        secret = "Точный приватный текст цитаты"
        content_hash = DIGEST._content_hash(secret)
        vector = [0.125] * DIGEST.EMBEDDING_DIMENSION

        DIGEST._store_vectors(path, {content_hash: vector})
        loaded = DIGEST._cached_vectors(path, [content_hash])

        self.assertEqual(loaded[content_hash], vector)
        self.assertNotIn(secret.encode("utf-8"), path.read_bytes())
        with mock.patch.object(DIGEST, "EMBEDDING_PROFILE", "another-profile"):
            self.assertEqual(DIGEST._cached_vectors(path, [content_hash]), {})

    def test_prepare_is_standalone_and_lexical_requires_query(self) -> None:
        prepare_with_corpus = self.call("--prepare")
        self.assertEqual(prepare_with_corpus.returncode, 2)
        self.assertIn("--prepare запускается отдельно", prepare_with_corpus.stderr)

        lexical_without_query = self.call("--lexical")
        self.assertEqual(lexical_without_query.returncode, 2)
        self.assertIn("только вместе с --query", lexical_without_query.stderr)

    def test_cli_errors_are_short_without_traceback(self) -> None:
        for args in (
            ("--grep", "["),
            ("--since", "yesterday"),
            ("--head", "0", "--digest"),
        ):
            result = self.call(*args)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
