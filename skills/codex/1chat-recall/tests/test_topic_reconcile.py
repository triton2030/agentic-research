"""Tests for guarded same-turn topic reconciliation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "topic_reconcile.py"


class TopicReconcileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.topic = "chat-recall-corpus"
        self.session = str(uuid.uuid4())
        self.topic_file = (
            self.root / "_ops" / "chat-recall" / "topics" / f"{self.topic}.md"
        )
        self.raw_dir = self.root / "_ops" / "chat-recall" / "raw"
        self.topic_file.parent.mkdir(parents=True)
        self.raw_dir.mkdir(parents=True)
        self.topic_file.write_text(
            f"---\ntopic: {self.topic}\ntitle: Recall\nsources: 0\n---\n"
            "# Recall\n\nПрежняя граница темы.\n\n## Current\n\n- Прежний claim. "
            "[2026-08-20-120000-Codex-OLD.md#L10]\n\n## Отменено\n",
            encoding="utf-8",
        )
        self.holder = self.raw_dir / "2026-08-24-120000-codex-12345678.md"
        self.record_line = (
            '* 2026-08-24T12:00:00+00:00 — "Новая позиция" '
            f"— type: решение | topic: {self.topic}"
        )
        self.holder.write_text(
            "---\nproject: test\ndate: 2026-08-24\nagent: codex\n"
            f"session: {self.session}\ntypes:\n  - решение\ntopics:\n"
            f"  - {self.topic}\n---\n\n# Holder\n\n{self.record_line}\n",
            encoding="utf-8",
        )
        self.source_anchor = self.current_anchor()
        self.record_sha256 = hashlib.sha256(
            self.record_line.encode("utf-8")
        ).hexdigest()
        self.patch = self.root / "patch.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def current_anchor(self) -> str:
        line_number = next(
            number
            for number, line in enumerate(
                self.holder.read_text(encoding="utf-8").splitlines(), start=1
            )
            if '"Новая позиция"' in line
        )
        return f"{self.holder.name}#L{line_number}"

    def run_command(self, *arguments: str, expect_ok: bool = True) -> dict[str, str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
        if expect_ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        return {"stderr": result.stderr}

    def prepare(self) -> dict[str, str]:
        return self.run_command(
            "prepare",
            "--project",
            str(self.root),
            "--topic",
            self.topic,
            "--patch",
            str(self.patch),
        )

    def apply(self, expected: str, expect_ok: bool = True) -> dict[str, str]:
        return self.run_command(
            "apply",
            "--project",
            str(self.root),
            "--topic",
            self.topic,
            "--patch",
            str(self.patch),
            "--expected-sha256",
            expected,
            "--session",
            self.session,
            "--record-sha256",
            self.record_sha256,
            "--source-anchor",
            self.source_anchor,
            expect_ok=expect_ok,
        )

    def acknowledge_noop(self) -> dict[str, str]:
        return self.run_command(
            "acknowledge-noop",
            "--project",
            str(self.root),
            "--topic",
            self.topic,
            "--session",
            self.session,
            "--record-sha256",
            self.record_sha256,
            "--source-anchor",
            self.source_anchor,
        )

    def set_operations(self, operations: list[dict[str, str]]) -> None:
        self.patch.write_text(
            json.dumps(
                {"version": 1, "topic": self.topic, "operations": operations},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def insert_operation(self, text: str, anchor: str | None = None) -> dict[str, str]:
        return {
            "kind": "insert",
            "section": "## Current",
            "claim": f"- {text} [{anchor or self.source_anchor}]",
        }

    def test_prepare_and_apply_guarded_patch(self) -> None:
        receipt = self.prepare()
        schema = json.loads(self.patch.read_text(encoding="utf-8"))["operation_schema"]
        self.assertEqual(schema["replace"]["kind"], "replace")
        self.assertIn("section", schema["move"])
        self.set_operations([self.insert_operation("Владелец задал новую позицию.")])

        result = self.apply(receipt["expected_sha256"])

        rendered = self.topic_file.read_text(encoding="utf-8")
        self.assertEqual(result["status"], "applied")
        self.assertIn(f"[{self.current_anchor()}]", rendered)
        self.assertIn("sources: 2", rendered)

    def test_concurrent_topic_change_refuses_without_mutation(self) -> None:
        receipt = self.prepare()
        self.set_operations([self.insert_operation("Владелец задал новую позицию.")])
        concurrent = self.topic_file.read_text(encoding="utf-8") + "Concurrent\n"
        self.topic_file.write_text(concurrent, encoding="utf-8")

        result = self.apply(receipt["expected_sha256"], expect_ok=False)

        self.assertIn("topic changed after prepare", result["stderr"])
        self.assertEqual(self.topic_file.read_text(encoding="utf-8"), concurrent)

    def test_raw_line_shift_reanchors_the_patch(self) -> None:
        receipt = self.prepare()
        self.set_operations([self.insert_operation("Владелец задал новую позицию.")])
        text = self.holder.read_text(encoding="utf-8")
        self.holder.write_text(
            text.replace("types:\n", "model: gpt-test\ntypes:\n"),
            encoding="utf-8",
        )
        self.assertNotEqual(self.source_anchor, self.current_anchor())

        result = self.apply(receipt["expected_sha256"])

        rendered = self.topic_file.read_text(encoding="utf-8")
        self.assertEqual(result["anchor"], self.current_anchor())
        self.assertIn(f"[{self.current_anchor()}]", rendered)
        self.assertNotIn(f"[{self.source_anchor}]", rendered)

    def test_wrong_record_topic_refuses_without_mutation(self) -> None:
        receipt = self.prepare()
        self.set_operations([self.insert_operation("Владелец задал новую позицию.")])
        self.holder.write_text(
            self.holder.read_text(encoding="utf-8").replace(
                f"topic: {self.topic}", "topic: another-topic"
            ),
            encoding="utf-8",
        )
        changed_line = next(
            line
            for line in self.holder.read_text(encoding="utf-8").splitlines()
            if '"Новая позиция"' in line
        )
        self.record_sha256 = hashlib.sha256(changed_line.encode("utf-8")).hexdigest()
        before = self.topic_file.read_text(encoding="utf-8")

        result = self.apply(receipt["expected_sha256"], expect_ok=False)

        self.assertIn("does not belong to topic", result["stderr"])
        self.assertEqual(self.topic_file.read_text(encoding="utf-8"), before)

    def test_each_changed_claim_must_cite_the_new_record_once(self) -> None:
        receipt = self.prepare()
        self.set_operations(
            [
                {
                    "kind": "insert",
                    "section": "## Current",
                    "claim": "- Claim without evidence.",
                }
            ]
        )
        before = self.topic_file.read_text(encoding="utf-8")

        result = self.apply(receipt["expected_sha256"], expect_ok=False)

        self.assertIn("exactly once", result["stderr"])
        self.assertEqual(self.topic_file.read_text(encoding="utf-8"), before)

    def test_patch_cannot_alias_the_shared_topic(self) -> None:
        result = self.run_command(
            "prepare",
            "--project",
            str(self.root),
            "--topic",
            self.topic,
            "--patch",
            str(self.topic_file),
            expect_ok=False,
        )

        self.assertIn("must not be the shared topic file", result["stderr"])

    def test_patch_cannot_replace_the_whole_topic(self) -> None:
        receipt = self.prepare()
        before = self.topic_file.read_text(encoding="utf-8")
        self.patch.write_text(
            json.dumps(
                {
                    "version": 1,
                    "topic": self.topic,
                    "operations": [self.insert_operation("Новый claim.")],
                    "content": "- Удалить всё прежнее.",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        result = self.apply(receipt["expected_sha256"], expect_ok=False)

        self.assertIn("must contain version", result["stderr"])
        self.assertEqual(self.topic_file.read_text(encoding="utf-8"), before)

    def test_one_record_can_update_multiple_claims(self) -> None:
        receipt = self.prepare()
        self.set_operations(
            [
                self.insert_operation("Первое следствие."),
                self.insert_operation("Второе следствие."),
            ]
        )

        result = self.apply(receipt["expected_sha256"])

        rendered = self.topic_file.read_text(encoding="utf-8")
        self.assertEqual(result["status"], "applied")
        self.assertEqual(rendered.count(f"[{self.current_anchor()}]"), 2)

    def test_replace_targets_exactly_one_existing_claim(self) -> None:
        receipt = self.prepare()
        before_claim = "- Прежний claim. [2026-08-20-120000-Codex-OLD.md#L10]"
        self.set_operations(
            [
                {
                    "kind": "replace",
                    "before": before_claim,
                    "after": (
                        "- Уточнённый claim. "
                        f"[2026-08-20-120000-Codex-OLD.md#L10, {self.source_anchor}]"
                    ),
                }
            ]
        )

        result = self.apply(receipt["expected_sha256"])

        rendered = self.topic_file.read_text(encoding="utf-8")
        self.assertEqual(result["status"], "applied")
        self.assertNotIn(before_claim, rendered)
        self.assertIn("- Уточнённый claim.", rendered)
        self.assertIn("sources: 2", rendered)

    def test_boundary_replace_is_limited_to_intro_paragraph(self) -> None:
        receipt = self.prepare()
        self.set_operations(
            [
                {
                    "kind": "replace-boundary",
                    "before": "Прежняя граница темы.",
                    "after": f"Уточнённая граница темы. [{self.source_anchor}]",
                }
            ]
        )

        result = self.apply(receipt["expected_sha256"])

        rendered = self.topic_file.read_text(encoding="utf-8")
        self.assertEqual(result["status"], "applied")
        self.assertIn("Уточнённая граница темы.", rendered)
        self.assertNotIn("Прежняя граница темы.", rendered)

    def test_boundary_replace_refuses_other_prose(self) -> None:
        self.topic_file.write_text(
            self.topic_file.read_text(encoding="utf-8") + "\nПосторонний абзац.\n",
            encoding="utf-8",
        )
        receipt = self.prepare()
        self.set_operations(
            [
                {
                    "kind": "replace-boundary",
                    "before": "Посторонний абзац.",
                    "after": f"Подмена. [{self.source_anchor}]",
                }
            ]
        )
        before = self.topic_file.read_text(encoding="utf-8")

        result = self.apply(receipt["expected_sha256"], expect_ok=False)

        self.assertIn("not the topic-boundary paragraph", result["stderr"])
        self.assertEqual(self.topic_file.read_text(encoding="utf-8"), before)

    def test_move_cancels_one_claim_into_exact_section(self) -> None:
        receipt = self.prepare()
        before_claim = "- Прежний claim. [2026-08-20-120000-Codex-OLD.md#L10]"
        cancelled = (
            "- Прежний claim отменён владельцем. "
            f"[2026-08-20-120000-Codex-OLD.md#L10, {self.source_anchor}]"
        )
        self.set_operations(
            [
                {
                    "kind": "move",
                    "before": before_claim,
                    "section": "## Отменено",
                    "after": cancelled,
                }
            ]
        )

        result = self.apply(receipt["expected_sha256"])

        rendered = self.topic_file.read_text(encoding="utf-8")
        current, cancelled_section = rendered.split("## Отменено", 1)
        self.assertEqual(result["status"], "applied")
        self.assertNotIn(before_claim, current)
        self.assertIn(cancelled, cancelled_section)
        self.assertIn("## Отменено\n\n- ", rendered)
        self.assertNotIn("\n\n\n## Отменено", rendered)

    def test_noop_receipt_is_idempotent_and_does_not_edit_topic(self) -> None:
        before = self.topic_file.read_bytes()

        first = self.acknowledge_noop()
        second = self.acknowledge_noop()

        ledger_path = (
            self.root / "_ops" / "chat-recall" / "topics" / "reconcile-noops.json"
        )
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(first["status"], "noop-acknowledged")
        self.assertEqual(second["status"], "noop-already-acknowledged")
        self.assertEqual(len(ledger["records"]), 1)
        self.assertEqual(ledger["records"][0]["record_sha256"], self.record_sha256)
        self.assertEqual(self.topic_file.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
