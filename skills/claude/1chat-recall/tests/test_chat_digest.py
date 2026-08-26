"""Acceptance tests for lossless parsing and bounded hybrid recall retrieval."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
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
session-context: "chat recall retrieval; session files; BM25; карточечныймаршрут"
---

# Chat recall

* 2026-07-14T06:00:00+00:00 — "Канон живёт отдельно — с тире" — type: решение | topic: документация-и-знания | context-note: Речь о владельце канона, а не о BM25.
* 10:55 — "Субагенты работают параллельно
и сохраняют контекст" — type: предпочтение | topic: мой-workflow
* 2026-07-15 — "Выбрал: локальный путь" — kind: selection | type: решение | \
topic: работа-и-процессы | context-note: Выбор относится к режиму хранения канона. | \
source: repaired | precision: date | source-ref: transcript.jsonl
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
        self.write_file("recall.md", entries)

    def write_file(
        self,
        name: str,
        entries: list[str],
        *,
        session: str = SESSION,
        session_context: str | None = None,
    ) -> None:
        context_line = (
            f"session-context: {json.dumps(session_context, ensure_ascii=False)}\n"
            if session_context
            else ""
        )
        content = (
            "---\n"
            "project: demo\n"
            "date: 2026-07-01\n"
            "agent: codex\n"
            "model: gpt-5.6\n"
            f"session: {session}\n"
            + context_line
            + "---\n\n"
            "# Chat recall\n\n"
            + "\n".join(entries)
            + "\n"
        )
        (self.corpus / name).write_text(content, encoding="utf-8")

    def write_topic(self, topic: str, description: str) -> None:
        layer = self.corpus / "topics"
        layer.mkdir(exist_ok=True)
        (layer / f"{topic}.md").write_text(
            "---\n"
            f"topic: {topic}\n"
            f"title: {description}\n"
            "sources: 0\n"
            "---\n"
            f"# {description}\n",
            encoding="utf-8",
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
        self.assertEqual(records[1]["topic"], "мой-workflow")
        self.assertIsNone(records[1]["topic_raw"])
        self.assertNotIn("invalid-topic", records[1]["diagnostics"])
        self.assertEqual(records[2]["kind"], "selection")
        self.assertEqual(records[2]["precision"], "date")
        self.assertEqual(records[2]["source_ref"], "transcript.jsonl")
        self.assertEqual(records[3]["kind"], "note")
        self.assertEqual(records[3]["type"], "неопределено")

    def test_record_id_ignores_file_date_classification_and_context_note(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        original = records[0]["record_id"]
        changed = FILE.replace("date: 2026-07-14", "date: 2025-01-01").replace(
            "type: решение | topic: документация-и-знания",
            "type: факт | topic: архитектура-и-модель",
            1,
        )
        changed = changed.replace(
            "Речь о владельце канона, а не о BM25.",
            "Другое пояснение того же тезиса.",
        )
        (self.corpus / "recall.md").unlink()
        (self.corpus / "renamed.md").write_text(
            changed.replace("# Chat recall", "\n\n# Chat recall"),
            encoding="utf-8",
        )
        changed_records, _ = DIGEST.load(self.corpus)
        self.assertEqual(original, changed_records[0]["record_id"])

    def test_context_note_is_searchable_but_shown_only_on_show(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        record = records[0]
        record_id = record["record_id"]
        self.assertEqual(
            record["context_note"],
            "Речь о владельце канона, а не о BM25.",
        )

        compact_query = self.call("--query", "канон")
        self.assertNotIn("владельце канона", compact_query.stdout)
        query_json = json.loads(self.call("--query", "канон", "--json").stdout)
        self.assertNotIn("context_note", query_json["holders"][0])
        self.assertEqual(
            query_json["holders"][0]["session_context"],
            "chat recall retrieval; session files; BM25; карточечныймаршрут",
        )
        note_match = json.loads(
            self.call("--query", "BM25", "--json").stdout
        )
        self.assertNotEqual(note_match["selection"], "none")
        self.assertEqual(
            note_match["holders"][0]["strongest_quote"]["address"],
            record["address"],
        )

        shown = self.call("--show", record_id)
        self.assertIn(
            "context-note: Речь о владельце канона, а не о BM25.",
            shown.stdout,
        )
        shown_json = json.loads(self.call("--show", record_id, "--json").stdout)
        self.assertEqual(
            shown_json["records"][0]["context_note"],
            "Речь о владельце канона, а не о BM25.",
        )

    def test_session_context_is_the_only_searchable_source_for_task_wording(self) -> None:
        data = json.loads(
            self.call("--query", "карточечныймаршрут", "--json").stdout
        )

        self.assertEqual(data["matched"], 1)
        self.assertEqual(data["selection"], "holders")
        self.assertEqual(data["card_route"], "open: lexical")
        self.assertEqual(data["holders"][0]["session_context"], (
            "chat recall retrieval; session files; BM25; карточечныймаршрут"
        ))
        self.assertIsNone(data["holders"][0]["strongest_quote"])
        self.assertEqual(data["holders"][0]["admitted_by"], "card")
        self.assertNotIn("date", data["holders"][0])
        self.assertIn("age", data["holders"][0])

    def test_human_card_route_names_holder_without_representative_quote(self) -> None:
        result = self.call("--query", "карточечныймаршрут")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("holder=recall.md", result.stdout)
        self.assertIn("admitted_by=card", result.stdout)
        self.assertNotIn("Канон живёт отдельно", result.stdout)

    def test_topic_description_is_a_separate_query_route(self) -> None:
        self.write_topic(
            "topic-lifecycle",
            "Редактированиетематическихфактов после новых слов владельца",
        )

        result = self.call(
            "--query",
            "Редактированиетематическихфактов",
            "--json",
        )
        data = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["selection"], "topic_candidates")
        self.assertEqual(data["holders"], [])
        self.assertEqual(data["topic_candidate_count"], 1)
        self.assertEqual(data["topic_returned"], 1)
        self.assertEqual(
            data["topic_candidates"][0],
            {
                "topic": "topic-lifecycle",
                "description": (
                    "Редактированиетематическихфактов после новых слов владельца"
                ),
                "file": "topics/topic-lifecycle.md",
                "topic_rank": 1,
                "admitted_by": "lexical",
            },
        )

        human = self.call("--query", "Редактированиетематическихфактов")
        self.assertIn("topic-candidate=topic-lifecycle", human.stdout)
        self.assertIn("description: Редактированиетематическихфактов", human.stdout)

    def test_topic_and_quote_routes_remain_separate(self) -> None:
        self.write_topic("subagent-search", "Субагенты для дополнительного поиска")

        data = json.loads(
            self.call("--query", "субагент*", "--json").stdout
        )

        self.assertEqual(data["selection"], "holders+topic_candidates")
        self.assertEqual(data["topic_candidates"][0]["topic"], "subagent-search")
        self.assertEqual(data["topic_candidates"][0]["topic_rank"], 1)
        self.assertEqual(data["holders"][0]["file"], "recall.md")
        self.assertIn("Субагенты", data["holders"][0]["strongest_quote"]["text"])

    def test_topic_search_indexes_the_short_intro_without_exposing_it(self) -> None:
        layer = self.corpus / "topics"
        layer.mkdir()
        (layer / "capture-flow.md").write_text(
            "---\n"
            "topic: capture-flow\n"
            "title: Жизненный цикл записи\n"
            "sources: 0\n"
            "---\n"
            "# Жизненный цикл записи\n\n"
            "Уникальныймаршрут выбора и обновления тематического факта.\n",
            encoding="utf-8",
        )

        data = json.loads(
            self.call("--query", "Уникальныймаршрут", "--json").stdout
        )

        candidate = data["topic_candidates"][0]
        self.assertEqual(candidate["topic"], "capture-flow")
        self.assertEqual(candidate["description"], "Жизненный цикл записи")
        self.assertNotIn("search_text", candidate)

    def test_selected_holders_display_newest_first_with_semantic_rank_and_counts(
        self,
    ) -> None:
        self.write_file(
            "a-old.md",
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Needle old decision" '
                    '— type: решение | topic: архитектура-и-модель'
                ),
                (
                    '* 2026-07-01T11:00:00+00:00 — "Needle old idea" '
                    '— type: идея | topic: архитектура-и-модель'
                ),
            ],
            session="22222222-2222-4222-8222-222222222222",
            session_context="old needle session",
        )
        self.write_file(
            "z-new.md",
            [
                (
                    '* 2026-07-03T10:00:00+00:00 — "Needle new decision" '
                    '— type: решение | topic: продукт-и-ценность'
                ),
            ],
            session="33333333-3333-4333-8333-333333333333",
            session_context="new needle session",
        )

        data = json.loads(
            self.call("--query", "Needle", "--limit", "2", "--json").stdout
        )

        self.assertEqual(
            [holder["file"] for holder in data["holders"]],
            ["z-new.md", "a-old.md"],
        )
        self.assertEqual(
            [holder["semantic_rank"] for holder in data["holders"]],
            [2, 1],
        )
        old = data["holders"][1]
        self.assertEqual(old["session_context"], "old needle session")
        self.assertEqual(old["types"], {"решение": 1, "идея": 1})
        self.assertEqual(old["topics"], {"архитектура-и-модель": 2})
        self.assertNotIn("date", old)

    def test_context_rescue_replaces_only_single_channel_quote_holder(self) -> None:
        quote_ranking = [
            {
                "file": "protected.md",
                "quote_channels": 2,
                "quote_evidence": [],
            },
            {
                "file": "replaceable.md",
                "quote_channels": 1,
                "quote_evidence": [],
            },
        ]
        card_ranking = [
            {
                "file": "card.md",
                "card_rank": 1,
                "card_evidence": ["bm25", "dense"],
            }
        ]

        selected, candidate_count = DIGEST._select_holders(
            quote_ranking,
            card_ranking,
            2,
        )

        self.assertEqual(candidate_count, 3)
        self.assertEqual(
            [record["file"] for record in selected],
            ["protected.md", "card.md"],
        )
        self.assertEqual(selected[1]["admitted_by"], "card")

    def test_novel_card_term_is_a_separate_route_when_common_text_matches(self) -> None:
        self.write_file(
            "base.md",
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Common route word" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ],
            session="22222222-2222-4222-8222-222222222222",
        )
        self.write_file(
            "card.md",
            [
                (
                    '* 2026-07-02T10:00:00+00:00 — "Unrelated quote" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ],
            session="33333333-3333-4333-8333-333333333333",
            session_context="rarecardterm",
        )

        data = json.loads(
            self.call(
                "--query",
                "rarecardterm common",
                "--json",
                "--limit",
                "5",
            ).stdout
        )

        by_file = {holder["file"]: holder for holder in data["holders"]}
        self.assertEqual(set(by_file), {"base.md", "card.md"})
        self.assertEqual(by_file["base.md"]["admitted_by"], "quote")
        self.assertEqual(by_file["card.md"]["admitted_by"], "card")
        self.assertEqual(data["candidate_count"], 2)

        bounded = json.loads(
            self.call(
                "--query",
                "rarecardterm common",
                "--json",
                "--max-chars",
                "512",
            ).stdout
        )
        self.assertEqual(bounded["candidate_count"], 2)
        self.assertEqual(bounded["returned"], len(bounded["holders"]))
        self.assertGreaterEqual(bounded["candidate_count"], bounded["returned"])

    def test_two_wildcard_roots_open_the_ordinary_card_route(self) -> None:
        self.write_file(
            "root-one.md",
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Корневой материал" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ],
            session="22222222-2222-4222-8222-222222222222",
        )
        self.write_file(
            "root-two.md",
            [
                (
                    '* 2026-07-01T11:00:00+00:00 — "Папочная инструкция" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ],
            session="33333333-3333-4333-8333-333333333333",
        )
        self.write_file(
            "card.md",
            [
                (
                    '* 2026-07-01T12:00:00+00:00 — "Другой текст" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ],
            session="44444444-4444-4444-8444-444444444444",
            session_context="корневой поиск; папочная инструкция",
        )

        opened = json.loads(
            self.call("--query", "корнев* папочн*", "--json").stdout
        )
        one_root = json.loads(
            self.call("--query", "корнев*", "--json").stdout
        )
        no_admission = json.loads(
            self.call("--query", "корнев* отсутствующ*", "--json").stdout
        )

        self.assertEqual(opened["card_route"], "open: lexical")
        self.assertIn("card.md", [holder["file"] for holder in opened["holders"]])
        self.assertEqual(
            one_root["card_route"],
            "closed: no context consensus or lexical novelty",
        )
        self.assertEqual(
            no_admission["card_route"],
            "no context consensus or lexical admission",
        )

    def test_opaque_selection_has_context_while_self_contained_quote_stays_bare(
        self,
    ) -> None:
        records, _ = DIGEST.load(self.corpus)
        self.assertNotIn("context_note", records[1])
        selection = records[2]
        self.assertEqual(selection["kind"], "selection")
        self.assertEqual(
            selection["context_note"],
            "Выбор относится к режиму хранения канона.",
        )
        shown = self.call("--show", selection["record_id"])
        self.assertIn(
            "context-note: Выбор относится к режиму хранения канона.",
            shown.stdout,
        )

    def test_bm25_prefix_filters_and_show_are_stable(self) -> None:
        query = self.call("--query", "субагент*", "--json")
        self.assertEqual(query.returncode, 0, query.stderr)
        self.assertEqual(query.stderr, "")
        envelope = json.loads(query.stdout)
        self.assertEqual(envelope["matched"], 1)
        self.assertEqual(envelope["retrieval"], "lexical")
        self.assertTrue(envelope["retrieval_complete"])
        self.assertEqual(envelope["candidate_count"], 1)
        address = envelope["holders"][0]["strongest_quote"]["address"]
        records, _ = DIGEST.load(self.corpus)
        record_id = next(
            record["record_id"] for record in records if record["address"] == address
        )
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
            "1/1 holders shown · 5 records · retrieval=lexical",
            compact.stdout,
        )
        self.assertRegex(compact.stdout, r"\d+ (день|дня|дней|месяц|месяца|месяцев) назад")
        self.assertNotIn("score=", compact.stdout)
        self.assertIn("recall.md:13", compact.stdout)
        self.assertEqual(compact.stderr, "")

        verbose = self.call("--query", "субагент*", "--verbose")
        self.assertEqual(verbose.returncode, 0, verbose.stderr)
        self.assertNotIn("score=", verbose.stdout)

    def test_human_show_is_compact_and_verbose_preserves_full_record(self) -> None:
        address = json.loads(self.call("--query", "канон", "--json").stdout)[
            "holders"
        ][0]["strongest_quote"]["address"]
        records, _ = DIGEST.load(self.corpus)
        record_id = next(
            record["record_id"] for record in records if record["address"] == address
        )

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

    def test_free_topic_is_native_and_searchable(self) -> None:
        check = self.call("--check")
        self.assertNotIn("invalid-topic", check.stdout)
        self.assertIn("missing-topic", check.stdout)
        found = json.loads(self.call("--query", "мой-workflow", "--json").stdout)
        self.assertEqual(found["matched"], 1)
        self.assertEqual(found["holders"][0]["topics"]["мой-workflow"], 1)
        self.assertEqual(found["holders"][0]["topics"]["без-темы"], 2)
        records, _ = DIGEST.load(self.corpus)
        free_topic = next(
            record for record in records if record["topic"] == "мой-workflow"
        )
        self.assertIsNone(free_topic["topic_raw"])
        shown_topic = self.call("--show", free_topic["record_id"])
        self.assertIn("topic=мой-workflow", shown_topic.stdout)

        invalid_type = next(
            record
            for record in records
            if record["type_raw"] and record["type_raw"] != record["type"]
        )
        shown_type = self.call("--show", invalid_type["record_id"])
        self.assertIn("type_raw=идея, коррекция", shown_type.stdout)

    def test_controlled_vocabulary_is_shared(self) -> None:
        self.assertEqual(len(DIGEST.TYPES), 9)
        self.assertIn("неопределено", DIGEST.TYPES)
        self.assertEqual(DIGEST.REPAIR_TOPIC, "без-темы")

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

    def test_truncated_result_preserves_returned_quote_evidence(self) -> None:
        for hour in range(3):
            self.write_file(
                f"evidence-{hour}.md",
                [
                    (
                        f'* 2026-07-01T{hour:02d}:00:00+00:00 — '
                        f'"EvidenceNeedle position {hour}" — type: решение | '
                        "topic: работа-и-процессы"
                    )
                ],
                session=f"00000000-0000-4000-8000-{hour:012d}",
            )

        data = json.loads(
            self.call(
                "--query",
                "EvidenceNeedle",
                "--limit",
                "1",
                "--json",
            ).stdout
        )

        self.assertTrue(data["truncated"])
        self.assertEqual(data["truncated_by"], "limit")
        self.assertEqual(data["returned"], 1)
        self.assertIsNotNone(data["holders"][0]["strongest_quote"])
        self.assertIn("EvidenceNeedle", data["holders"][0]["strongest_quote"]["text"])

    def test_default_query_keeps_all_ten_full_holder_cards(self) -> None:
        for hour in range(10):
            self.write_file(
                f"full-context-{hour}.md",
                [
                    (
                        f'* 2026-07-01T{hour:02d}:00:00+00:00 — '
                        f'"Needle holder {hour}" — type: решение | '
                        "topic: документация-и-знания"
                    )
                ],
                session=f"00000000-0000-4000-9000-{hour:012d}",
                session_context=f"Needle context {hour} " + "detail " * 180,
            )

        result = self.call("--query", "Needle", "--lexical", "--json")
        data = json.loads(result.stdout)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(len(result.stdout), DIGEST.DEFAULT_MAX_CHARS)
        self.assertEqual(data["returned"], 10)
        self.assertEqual(len(data["holders"]), 10)
        self.assertFalse(data["truncated"])

    def test_query_json_returns_snippet_in_strongest_quote(self) -> None:
        long_text = (
            "владелец объясняет длинную позицию про запись файлов " * 6
        ).strip()
        self.write_entries(
            [
                f'* 2026-07-01T10:00:00+00:00 — "{long_text}" — '
                "type: решение | topic: работа-и-процессы",
            ]
        )
        data = json.loads(self.call("--query", "запись файлов", "--json").stdout)
        self.assertEqual(data["returned"], 1)
        snippet = data["holders"][0]["strongest_quote"]["text"]
        self.assertTrue(snippet.endswith("…"))
        self.assertLessEqual(len(snippet), 111)
        timeline = json.loads(
            self.call("--query", "запись файлов", "--timeline", "--json").stdout
        )
        self.assertTrue(
            any(len(record["text"]) > 111 for record in timeline["records"])
        )

    def test_help_explains_limit_head_and_character_budget(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("maximum holders for a query", result.stdout)
        self.assertIn("excerpt length for human digest and strongest quote", result.stdout)
        self.assertIn("full query holder cards", result.stdout)

    def test_human_bound_uses_rendered_digest_not_full_json(self) -> None:
        for hour in range(5):
            self.write_file(
                f"needle-{hour}.md",
                [
                    (
                        f'* 2026-07-01T{hour:02d}:00:00+00:00 — '
                        f'"Needle {hour} {"detail " * 350}" '
                        "— type: решение | topic: документация-и-знания"
                    )
                ],
                session=f"00000000-0000-4000-8000-{hour:012d}",
            )

        human = self.call(
            "--query", "Needle", "--limit", "5", "--max-chars", "4000"
        )
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertTrue(human.stdout.startswith("5/5 holders shown · 10 records"))
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
        self.assertEqual(machine["returned"], 5)
        self.assertFalse(machine["truncated"])
        self.assertIsNone(machine["truncated_by"])

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
        self.assertIn("первая holder-card не помещается", result.stderr)
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

    def test_timeline_keeps_later_correction_with_the_earlier_decision(self) -> None:
        self.write_entries(
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Артефакты удалять локально" '
                    "— type: решение | topic: работа-и-процессы"
                ),
                (
                    '* 2026-07-02T10:00:00+00:00 — "Артефакты локально сохранять" '
                    "— type: коррекция | topic: работа-и-процессы"
                ),
            ]
        )

        records = json.loads(
            self.call(
                "--query",
                "Артефакты",
                "--timeline",
                "--json",
                "--limit",
                "5",
            ).stdout
        )["records"]

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["type"], "коррекция")
        self.assertEqual(records[1]["type"], "решение")

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

    def test_strict_check_reports_forbidden_topic_tombstone(self) -> None:
        self.write_entries(
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Clean record" '
                    '— type: решение | topic: работа-и-процессы'
                )
            ]
        )
        self.write_topic("topic-lifecycle", "Жизненный цикл темы")
        topic = self.corpus / "topics" / "topic-lifecycle.md"
        topic.write_text(
            topic.read_text(encoding="utf-8")
            + "\n## Отменено\n\n- Исторический claim.\n",
            encoding="utf-8",
        )

        strict = self.call("--check", "--strict")

        self.assertEqual(strict.returncode, 1)
        self.assertIn(
            "topics/topic-lifecycle.md: forbidden-topic-tombstone",
            strict.stdout,
        )

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

    def test_bounded_strict_check_keeps_topic_drift_visible(self) -> None:
        self.write_entries([f"* broken record {index:02d}" for index in range(20)])
        self.write_topic("topic-lifecycle", "Жизненный цикл темы")
        topic = self.corpus / "topics" / "topic-lifecycle.md"
        topic.write_text(
            topic.read_text(encoding="utf-8")
            + "\n## Отменено\n\n- Исторический claim.\n",
            encoding="utf-8",
        )

        strict = self.call("--check", "--strict", "--max-chars", "512")

        self.assertEqual(strict.returncode, 1)
        self.assertIn("corpus diagnostics (20 raw, 1 topic)", strict.stdout)
        self.assertIn(
            "topics/topic-lifecycle.md: forbidden-topic-tombstone",
            strict.stdout,
        )

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

    def test_hybrid_queue_serializes_processes_across_project_cwds(self) -> None:
        shared_cache = self.corpus / "shared-cache"
        other_project = self.corpus / "other-project"
        other_project.mkdir()
        ready = self.corpus / "queue-ready"
        environment = os.environ.copy()
        environment["CHAT_RECALL_CACHE_DIR"] = str(shared_cache)
        environment["CHAT_RECALL_QUEUE_READY"] = str(ready)
        probe = f"""
import importlib.util
import os
import sys
import time
from pathlib import Path

script = Path({str(SCRIPT)!r})
sys.path.insert(0, str(script.parent))
spec = importlib.util.spec_from_file_location("chat_digest_queue_probe", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Path(os.environ["CHAT_RECALL_QUEUE_READY"]).write_text("ready", encoding="utf-8")
started = time.monotonic()
with module._hybrid_queue():
    print(time.monotonic() - started, flush=True)
"""
        process: subprocess.Popen[str] | None = None
        try:
            with mock.patch.dict(
                os.environ,
                {"CHAT_RECALL_CACHE_DIR": str(shared_cache)},
            ):
                with DIGEST._hybrid_queue():
                    process = subprocess.Popen(
                        [sys.executable, "-c", probe],
                        cwd=other_project,
                        env=environment,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    deadline = time.monotonic() + 3
                    while not ready.exists() and time.monotonic() < deadline:
                        time.sleep(0.01)
                    self.assertTrue(ready.exists(), "probe did not reach queue")
                    time.sleep(0.2)
                    self.assertIsNone(process.poll(), "probe bypassed held queue")
                stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertGreaterEqual(float(stdout.strip()), 0.18)
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait()

    def test_hybrid_abstains_before_loading_dense_model(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        with mock.patch.object(DIGEST, "search_dense") as dense:
            result = DIGEST.search_hybrid(records, "несуществующее")

        self.assertEqual(result, [])
        dense.assert_not_called()

    def test_session_card_fallback_does_not_displace_quote_hybrid(self) -> None:
        records = [
            {"file": "quote.md", "address": "quote.md:1", "record_id": "quote"},
            {"file": "card.md", "address": "card.md:1", "record_id": "card"},
        ]
        with (
            mock.patch.object(DIGEST, "search_bm25", return_value=[records[0]]),
            mock.patch.object(DIGEST, "search_dense", return_value=records),
            mock.patch.object(
                DIGEST,
                "search_session_context_bm25",
                return_value=[records[1]],
            ) as cards,
        ):
            result = DIGEST.search_hybrid(records, "query", collapse_files=True)

        cards.assert_not_called()
        self.assertEqual(result[0]["file"], "quote.md")

    def test_context_consensus_requires_top_five_bm25_and_dense_agreement(
        self,
    ) -> None:
        records = [
            {
                "file": "agreed.md",
                "address": "agreed.md:1",
                "record_id": "agreed",
            },
            {
                "file": "lexical-only.md",
                "address": "lexical-only.md:1",
                "record_id": "lexical-only",
            },
            {
                "file": "dense-only.md",
                "address": "dense-only.md:1",
                "record_id": "dense-only",
            },
        ]
        with (
            mock.patch.object(DIGEST, "search_bm25", return_value=[records[0]]),
            mock.patch.object(
                DIGEST,
                "search_session_context_bm25",
                return_value=[records[1], records[0]],
            ),
            mock.patch.object(
                DIGEST,
                "search_session_context_dense",
                return_value=[records[2], records[0]],
            ),
        ):
            result, route = DIGEST.search_session_routes(
                records,
                "query",
                hybrid=True,
            )

        self.assertEqual([record["file"] for record in result], ["agreed.md"])
        self.assertEqual(result[0]["card_evidence"], ["bm25", "dense"])
        self.assertEqual(route, "open: consensus")

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

    def test_hybrid_collapses_files_before_depth_and_rrf(self) -> None:
        records = [
            {
                "file": "long.md",
                "address": f"long.md:{index}",
                "record_id": f"long-{index}",
            }
            for index in range(DIGEST.HYBRID_DEPTH + 1)
        ]
        records.append(
            {"file": "other.md", "address": "other.md:1", "record_id": "other"}
        )
        lexical = [dict(record) for record in records]
        dense = [dict(record) for record in records]
        with (
            mock.patch.object(DIGEST, "search_bm25", return_value=lexical),
            mock.patch.object(DIGEST, "search_dense", return_value=dense),
        ):
            result = DIGEST.search_hybrid(
                records,
                "query",
                collapse_files=True,
            )

        self.assertEqual([record["file"] for record in result], ["long.md", "other.md"])
        self.assertAlmostEqual(
            result[0]["score"],
            (1 + DIGEST.FILE_SUPPORT_WEIGHT) * 2 / (DIGEST.RRF_CONSTANT + 1),
        )
        self.assertEqual(len(result[0]["quote_evidence"]), 1)
        self.assertAlmostEqual(
            result[1]["score"],
            DIGEST.FILE_SUPPORT_WEIGHT * 2 / (DIGEST.RRF_CONSTANT + 2),
        )

    def test_file_rrf_uses_each_channels_best_quote_without_raw_count_bonus(self) -> None:
        records = [
            {"file": "a.md", "address": "a.md:1", "record_id": "a1"},
            {"file": "a.md", "address": "a.md:2", "record_id": "a2"},
            {"file": "b.md", "address": "b.md:1", "record_id": "b1"},
        ]
        lexical = [dict(records[0]), dict(records[2]), dict(records[1])]
        dense = [dict(records[1]), dict(records[2]), dict(records[0])]

        result = DIGEST._merge_file_rankings(records, (lexical, dense))

        self.assertEqual([record["file"] for record in result], ["a.md", "b.md"])
        self.assertEqual(result[0]["address"], "a.md:1")
        self.assertAlmostEqual(
            result[0]["score"],
            1 / (DIGEST.RRF_CONSTANT + 1)
            + 1 / (DIGEST.RRF_CONSTANT + 3)
            + DIGEST.FILE_SUPPORT_WEIGHT * 2 / (DIGEST.RRF_CONSTANT + 1),
        )
        self.assertAlmostEqual(
            result[1]["score"],
            (1 + DIGEST.FILE_SUPPORT_WEIGHT) * 2 / (DIGEST.RRF_CONSTANT + 2),
        )
        self.assertEqual(
            [record["address"] for record in result[0]["quote_evidence"]],
            ["a.md:1", "a.md:2"],
        )

    def test_default_query_returns_one_candidate_per_file_and_timeline_keeps_all(
        self,
    ) -> None:
        long_entries = [
            (
                f'* 2026-07-01T{index % 24:02d}:{index:02d}:00+00:00 — '
                f'"Needle long {index}" — type: факт | topic: работа-и-процессы'
            )
            for index in range(DIGEST.HYBRID_DEPTH + 1)
        ]
        self.write_file("long.md", long_entries)
        self.write_file(
            "other.md",
            [
                (
                    '* 2026-07-02T10:00:00+00:00 — "Needle other" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ],
            session="22222222-2222-4222-8222-222222222222",
        )

        compact = json.loads(
            self.call("--query", "Needle", "--limit", "2", "--json").stdout
        )
        timeline = json.loads(
            self.call(
                "--query",
                "Needle",
                "--timeline",
                "--limit",
                "100",
                "--max-chars",
                "200000",
                "--json",
            ).stdout
        )

        self.assertEqual(
            {holder["file"] for holder in compact["holders"]},
            {"long.md", "other.md"},
        )
        self.assertEqual(timeline["matched"], DIGEST.HYBRID_DEPTH + 2)

    def test_session_card_is_indexed_once_and_timeline_expands_its_file(self) -> None:
        entries = [
            (
                f'* 2026-07-01T{index % 24:02d}:{index % 60:02d}:00+00:00 — '
                f'"Record without route word {index}" '
                '— type: факт | topic: работа-и-процессы'
            )
            for index in range(DIGEST.HYBRID_DEPTH + 12)
        ]
        self.write_file(
            "card-only.md",
            entries,
            session_context="уникальныйкарточныймаршрут",
        )

        compact = json.loads(
            self.call(
                "--query",
                "уникальныйкарточныймаршрут",
                "--json",
            ).stdout
        )
        timeline = json.loads(
            self.call(
                "--query",
                "уникальныйкарточныймаршрут",
                "--timeline",
                "--limit",
                "100",
                "--max-chars",
                "200000",
                "--json",
            ).stdout
        )

        self.assertEqual(compact["matched"], 1)
        self.assertEqual(compact["selection"], "holders")
        self.assertEqual(compact["card_route"], "open: lexical")
        self.assertEqual(compact["holders"][0]["file"], "card-only.md")
        self.assertEqual(timeline["matched"], len(entries))
        self.assertEqual(
            {record["address"].split(":", 1)[0] for record in timeline["records"]},
            {"card-only.md"},
        )

    def test_legacy_file_without_session_context_remains_valid(self) -> None:
        self.write_entries(
            [
                (
                    '* 2026-07-01T10:00:00+00:00 — "Legacy holder" '
                    '— type: факт | topic: работа-и-процессы'
                )
            ]
        )

        records, diagnostics = DIGEST.load(self.corpus)

        self.assertEqual(diagnostics, 0)
        self.assertNotIn("session_context", records[0])

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
            _, retrieval, _, _ = DIGEST._retrieve(records, args)

        ranked_records = hybrid.call_args.args[0]
        self.assertEqual(retrieval, "hybrid")
        self.assertTrue(ranked_records)
        self.assertTrue(
            all(
                record["topic"] == "документация-и-знания"
                for record in ranked_records
            )
        )

    def test_dense_query_strips_wildcard_markers(self) -> None:
        records, _ = DIGEST.load(self.corpus)
        record = records[0]
        vector = [0.0] * DIGEST.EMBEDDING_DIMENSION
        content_hash = DIGEST._content_hash(DIGEST._dense_text(record))
        backend = object()
        with (
            mock.patch.object(DIGEST, "_embedding_backend", return_value=backend),
            mock.patch.object(
                DIGEST,
                "_cached_vectors",
                return_value={content_hash: vector},
            ),
            mock.patch.object(DIGEST, "_embed", return_value=[vector]) as embed,
        ):
            DIGEST.search_dense([record], "корнев* папочн*")

        embed.assert_called_once_with(
            backend,
            [DIGEST.QUERY_PREFIX + "корнев папочн"],
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
