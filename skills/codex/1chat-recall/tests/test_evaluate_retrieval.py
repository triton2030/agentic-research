"""Acceptance tests for corpus-bound retrieval regression fixtures."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("evaluate_retrieval.py")
SPEC = importlib.util.spec_from_file_location("retrieval_eval_under_test", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import evaluate_retrieval.py")
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)

SESSION = "11111111-1111-4111-8111-111111111111"


class RetrievalEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.corpus = self.root / "corpus"
        self.corpus.mkdir()
        self.fixture = self.root / "cases.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_record(self, project: str, text: str, filename: str = "recall.md") -> str:
        (self.corpus / filename).write_text(
            (
                "---\n"
                f"project: {project}\n"
                "date: 2026-08-04\n"
                "agent: codex\n"
                f"session: {SESSION}\n"
                "---\n\n"
                "# Chat recall\n\n"
                f'* 2026-08-04T10:00:00+00:00 — "{text}" '
                "— type: решение | topic: работа-и-процессы\n"
            ),
            encoding="utf-8",
        )
        records, _ = EVALUATOR.DIGEST.load(self.corpus)
        return next(record["record_id"] for record in records if record["text"] == text)

    def write_fixture(self, project: str, relevant: list[str]) -> None:
        self.fixture.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "corpus": {"project": project},
                    "cases": [
                        {"id": "example", "query": "пример", "relevant": relevant}
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def call_main(self) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with (
            mock.patch.object(
                sys,
                "argv",
                [str(SCRIPT), str(self.corpus), "--cases", str(self.fixture)],
            ),
            redirect_stdout(output),
        ):
            code = EVALUATOR.main()
        return code, json.loads(output.getvalue())

    def test_fixture_requires_one_self_describing_schema(self) -> None:
        self.write_fixture("demo", ["cr-example"])
        project, cases = EVALUATOR._load_fixture(self.fixture)
        self.assertEqual(project, "demo")
        self.assertEqual(cases[0]["relevant"], ["cr-example"])

        self.fixture.write_text("[]", encoding="utf-8")
        code, payload = self.call_main()
        self.assertEqual(code, 2)
        self.assertEqual(payload["error"], "cases-schema")

    def test_corpus_mismatch_precedes_missing_target_ids(self) -> None:
        self.write_record("mavo-short2", "Тестовая запись")
        self.write_fixture("agentic-research", ["cr-does-not-exist"])

        code, payload = self.call_main()

        self.assertEqual(code, 2)
        self.assertEqual(payload["error"], "corpus-mismatch")
        self.assertEqual(payload["expected"], {"project": "agentic-research"})
        self.assertEqual(payload["found"], {"projects": ["mavo-short2"]})

    def test_correct_corpus_reports_genuinely_missing_targets(self) -> None:
        self.write_record("agentic-research", "Тестовая запись")
        self.write_fixture("agentic-research", ["cr-does-not-exist"])

        code, payload = self.call_main()

        self.assertEqual(code, 2)
        self.assertEqual(payload["error"], "missing-targets")

    def test_every_target_must_belong_to_the_declared_project(self) -> None:
        expected_id = self.write_record("agentic-research", "Нужный проект")
        records, _ = EVALUATOR.DIGEST.load(self.corpus)
        foreign = dict(records[0], project="codex-bridge")
        error = EVALUATOR._fixture_corpus_error(
            [records[0], foreign],
            "agentic-research",
            [{"id": "example", "query": "проект", "relevant": [expected_id]}],
        )

        self.assertIsNotNone(error)
        assert error is not None
        self.assertEqual(error["error"], "target-project-mismatch")


if __name__ == "__main__":
    unittest.main()
