#!/usr/bin/env python3
"""Behavioral tests for prepared max-review packets and report checking."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "portable/scripts/max_review.py"
SCHEMA = ROOT / "portable/assets/report.schema.json"


class PacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source_one = self.root / "rules-one.md"
        self.source_one.write_text("first rule\n\nsecond rule\n", encoding="utf-8")
        self.source_two = self.root / "rules-two.md"
        self.source_two.write_text("private other rule\n", encoding="utf-8")
        self.target_one = self.root / "target-one.md"
        self.target_one.write_text("outside\nassigned target one\nend\n", encoding="utf-8")
        self.target_two = self.root / "target-two.md"
        self.target_two.write_text("assigned target two\n", encoding="utf-8")
        self.context = self.root / "context.txt"
        self.context.write_text("context fact\n", encoding="utf-8")
        self.plan_path = self.root / "plan.json"
        self.prepared = self.root / "prepared"
        self.run_dir = self.root / "run"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def plan(self) -> dict:
        return {
            "targets": [
                {"id": "T1", "path": str(self.target_one), "lines": [2, 2]},
                {"id": "T2", "path": str(self.target_two)},
            ],
            "sources": [
                {"id": "S1", "path": str(self.source_one), "targets": ["T1"]},
                {"id": "S2", "path": str(self.source_two), "targets": ["T2"]},
            ],
            "packets": [
                {
                    "id": "P1",
                    "targets": ["T1"],
                    "rules": [{"source": "S1", "lines": [1, 3]}],
                    "context": [{"path": str(self.context)}],
                },
                {"id": "P2", "targets": ["T2"], "rules": [{"source": "S2", "lines": [1, 1]}]},
            ],
            "excluded": [],
            "gaps": [],
        }

    def cli(self, *arguments: object) -> tuple[subprocess.CompletedProcess[str], dict]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *(str(item) for item in arguments), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )
        return process, json.loads(process.stdout)

    def prepare(self, plan: dict | None = None) -> dict:
        self.plan_path.write_text(json.dumps(plan or self.plan()), encoding="utf-8")
        process, payload = self.cli("prepare", "--plan", self.plan_path, "--out", self.prepared)
        self.assertEqual(process.returncode, 0, process.stderr)
        return payload

    def make_run(self, reports: dict[str, dict] | None = None, statuses: dict[str, str] | None = None) -> None:
        reports = reports or {
            "P1": {"packet": "P1", "status": "clean", "findings": [], "gaps": []},
            "P2": {"packet": "P2", "status": "clean", "findings": [], "gaps": []},
        }
        statuses = statuses or {}
        ledger = json.loads((self.prepared / "coverage.json").read_text())
        self.run_dir.mkdir()
        inputs = self.run_dir / "inputs"
        inputs.mkdir()
        (inputs / "output-schema.json").write_bytes((self.prepared / "report.schema.json").read_bytes())
        tasks = {}
        for packet in ledger["packets"]:
            packet_id = packet["id"]
            prompt = self.prepared / packet["prompt"]
            prompt_copy = inputs / f"{packet_id}.txt"
            prompt_copy.write_bytes(prompt.read_bytes())
            attempt_dir = self.run_dir / "attempts" / packet_id / "0001"
            attempt_dir.mkdir(parents=True)
            report_path = attempt_dir / "report.txt"
            if packet_id in reports:
                report_path.write_text(json.dumps(reports[packet_id]), encoding="utf-8")
            status = statuses.get(packet_id, "succeeded")
            tasks[packet_id] = {
                "prompt_source": str(prompt),
                "prompt_sha256": packet["prompt_sha256"],
                "prompt_copy": str(prompt_copy.relative_to(self.run_dir)),
                "status": status,
                "attempts": [{"number": 1, "status": status, "report": str(report_path.relative_to(self.run_dir))}],
            }
        state = {
            "tasks_source": str(self.prepared / "tasks.jsonl"),
            "output_schema": {
                "source": str(self.prepared / "report.schema.json"),
                "copy": "inputs/output-schema.json",
                "sha256": ledger["schema"]["sha256"],
            },
            "tasks": tasks,
        }
        (self.run_dir / "run.json").write_text(json.dumps(state), encoding="utf-8")

    def test_prepare_writes_bounded_self_contained_prompts_without_cross_packet_text(self) -> None:
        payload = self.prepare()
        self.assertEqual(payload["status"], "prepared")
        self.assertEqual([item["id"] for item in payload["packet_words"]], ["P1", "P2"])
        self.assertTrue(all(item["words"] > 0 for item in payload["packet_words"]))
        first = (self.prepared / "prompts/P1.md").read_text()
        second = (self.prepared / "prompts/P2.md").read_text()
        reviewer = (ROOT / "portable/references/reviewer.md").read_text()
        self.assertIn("PACKET P1", first)
        self.assertIn("first rule", first)
        self.assertIn("second rule", first)
        self.assertIn("assigned target one", first)
        self.assertIn("TARGET T1 lines 2-2 of 3 (excerpt)", first)
        self.assertIn("context fact", first)
        self.assertIn(reviewer, first)
        self.assertNotIn("private other rule", first)
        self.assertNotIn("assigned target two", first)
        self.assertNotIn("first rule", second)
        self.assertNotIn("context fact", second)
        self.assertNotIn("outside", first)
        self.assertNotIn("end", first)
        tasks = [json.loads(line) for line in (self.prepared / "tasks.jsonl").read_text().splitlines()]
        self.assertEqual({row["id"] for row in tasks}, {"P1", "P2"})
        self.assertTrue(all(row["cwd"] == str(Path(tempfile.gettempdir()).resolve()) for row in tasks))
        self.assertEqual((self.prepared / "report.schema.json").read_bytes(), SCHEMA.read_bytes())
        ledger = json.loads((self.prepared / "coverage.json").read_text())
        self.assertTrue(all(packet["prompt_words"] > 0 for packet in ledger["packets"]))

    def test_prepare_rejects_coverage_holes_before_writing_output(self) -> None:
        plan = self.plan()
        plan["packets"][0]["rules"][0]["lines"] = [1, 1]
        self.plan_path.write_text(json.dumps(plan), encoding="utf-8")
        process, payload = self.cli("prepare", "--plan", self.plan_path, "--out", self.prepared)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(payload["status"], "error")
        self.assertIn("uncovered source lines", payload["error"])
        self.assertFalse(self.prepared.exists())

    def test_exclusion_can_cover_a_source_range_for_one_applicable_target(self) -> None:
        plan = self.plan()
        plan["packets"][0]["rules"][0]["lines"] = [1, 1]
        plan["excluded"] = [
            {"source": "S1", "lines": [2, 3], "targets": ["T1"], "reason": "blank and unrelated"}
        ]
        payload = self.prepare(plan)
        self.assertEqual(payload["counts"]["packets"], 2)

    def test_prepare_rejects_unknown_ids_out_of_range_and_silent_targets(self) -> None:
        cases = []
        unknown = self.plan()
        unknown["packets"][0]["rules"][0]["source"] = "missing"
        cases.append(unknown)
        out_of_range = self.plan()
        out_of_range["targets"][0]["lines"] = [2, 8]
        cases.append(out_of_range)
        unassigned = self.plan()
        unassigned["packets"] = unassigned["packets"][:1]
        unassigned["sources"] = unassigned["sources"][:1]
        cases.append(unassigned)
        for index, plan in enumerate(cases):
            with self.subTest(index=index):
                plan_path = self.root / f"bad-{index}.json"
                out = self.root / f"bad-out-{index}"
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                process, payload = self.cli("prepare", "--plan", plan_path, "--out", out)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(payload["status"], "error")
                self.assertFalse(out.exists())

    def test_clean_reports_pass_and_findings_are_saved_out_of_band(self) -> None:
        self.prepare()
        reports = {
            "P1": {
                "packet": "P1",
                "status": "findings",
                "findings": [{"rule": "S1:3", "at": "T1:2", "defect": "second rule is absent"}],
                "gaps": [],
            },
            "P2": {"packet": "P2", "status": "clean", "findings": [], "gaps": []},
        }
        self.make_run(reports)
        process, payload = self.cli("check", "--prepared", self.prepared, "--run-dir", self.run_dir)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(payload["status"], "findings")
        self.assertEqual(payload["counts"]["finding_items"], 1)
        self.assertNotIn("findings", payload)
        details = json.loads(Path(payload["check_path"]).read_text())
        self.assertEqual(details["findings"][0]["defect"], "second rule is absent")

    def test_missing_unknown_malformed_and_transport_failure_are_incomplete(self) -> None:
        variants = [
            ({"P1": {"packet": "P1", "status": "clean", "findings": [], "gaps": []}}, {}),
            ({
                "P1": {"packet": "P1", "status": "unknown", "findings": [], "gaps": ["cannot inspect"]},
                "P2": {"packet": "P2", "status": "clean", "findings": [], "gaps": []},
            }, {}),
            ({
                "P1": {"packet": "wrong", "status": "clean", "findings": [], "gaps": []},
                "P2": {"packet": "P2", "status": "clean", "findings": [], "gaps": []},
            }, {}),
            ({
                "P1": {"packet": "P1", "status": "clean", "findings": [], "gaps": []},
                "P2": {"packet": "P2", "status": "clean", "findings": [], "gaps": []},
            }, {"P1": "failed"}),
        ]
        for index, (reports, statuses) in enumerate(variants):
            with self.subTest(index=index):
                self.prepared = self.root / f"prepared-{index}"
                self.run_dir = self.root / f"run-{index}"
                self.prepare()
                self.make_run(reports, statuses)
                process, payload = self.cli(
                    "check", "--prepared", self.prepared, "--run-dir", self.run_dir
                )
                self.assertEqual(process.returncode, 1)
                self.assertEqual(payload["status"], "incomplete")

    def test_check_rejects_stale_source_mismatched_prompt_and_bad_addresses(self) -> None:
        variants = ("source", "prompt", "address")
        for index, variant in enumerate(variants):
            with self.subTest(variant=variant):
                self.prepared = self.root / f"prepared-stale-{index}"
                self.run_dir = self.root / f"run-stale-{index}"
                self.prepare()
                reports = None
                if variant == "address":
                    reports = {
                        "P1": {
                            "packet": "P1", "status": "findings", "gaps": [],
                            "findings": [{"rule": "S2:1", "at": "T1:1", "defect": "bad"}],
                        },
                        "P2": {"packet": "P2", "status": "clean", "findings": [], "gaps": []},
                    }
                self.make_run(reports)
                if variant == "source":
                    self.source_one.write_text("changed\n", encoding="utf-8")
                elif variant == "prompt":
                    state_path = self.run_dir / "run.json"
                    state = json.loads(state_path.read_text())
                    state["tasks"]["P1"]["prompt_sha256"] = "0" * 64
                    state_path.write_text(json.dumps(state), encoding="utf-8")
                process, payload = self.cli(
                    "check", "--prepared", self.prepared, "--run-dir", self.run_dir
                )
                self.assertEqual(process.returncode, 1)
                self.assertEqual(payload["status"], "incomplete")
                details = json.loads(Path(payload["check_path"]).read_text())
                self.assertTrue(details["problems"])
                if variant == "source":
                    self.source_one.write_text("first rule\n\nsecond rule\n", encoding="utf-8")

    def test_explicit_plan_gap_blocks_clean(self) -> None:
        plan = self.plan()
        plan["gaps"] = ["Applicable remote policy could not be fetched"]
        self.prepare(plan)
        self.make_run()
        process, payload = self.cli("check", "--prepared", self.prepared, "--run-dir", self.run_dir)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(payload["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
