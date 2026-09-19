#!/usr/bin/env python3
"""Behavioral tests for the narrow MaxRevie coverage helper."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "portable/scripts/coverage.py"


class CoverageHelperTests(unittest.TestCase):
    def test_empty_audit_cannot_be_sealed(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(json.dumps({"inputs": [], "rules": [], "units": [], "packets": []}))
            process, result = self.run_cli("seal", manifest)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(result["status"], "invalid")

    def test_independent_recheck_requires_its_own_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path, manifest = self.make_manifest(root)
            manifest["units"].append({"id": "unit-2", "rules": ["rule-1"], "targets": ["target1"]})
            manifest["packets"].append({"id": "packet-2", "units": ["unit-2"]})
            path.write_text(json.dumps(manifest))
            process, _ = self.run_cli("seal", path)
            self.assertEqual(process.returncode, 0, process.stdout)
            manifest = json.loads(path.read_text())
            reports = self.write_report(root, manifest, [self.passing_check()])
            process, result = self.run_cli("check", path, reports)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["missing"], 1)
            second = {**self.passing_check(), "unit": "unit-2"}
            self.write_report(root, manifest, [second], "packet-2")
            process, result = self.run_cli("check", path, reports)
            self.assertEqual(process.returncode, 0, process.stdout)
            self.assertEqual(result["pass"], 2)

    def run_cli(self, *arguments: str | Path) -> tuple[subprocess.CompletedProcess[str], dict]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *(str(argument) for argument in arguments)],
            text=True,
            capture_output=True,
            check=False,
        )
        payload = json.loads(process.stdout)
        return process, payload

    def make_manifest(self, root: Path, target_count: int = 1) -> tuple[Path, dict]:
        source = root / "source.md"
        source.write_text("normative source\n", encoding="utf-8")
        inputs = [{"id": "source", "path": str(source)}]
        targets: list[str] = []
        for index in range(target_count):
            target_id = f"target{index + 1}"
            target = root / f"{target_id}.md"
            target.write_text(f"target {index + 1}\n", encoding="utf-8")
            inputs.append({"id": target_id, "path": str(target)})
            targets.append(target_id)
        manifest = {
            "inputs": inputs,
            "rules": [
                {
                    "id": "rule-1",
                    "source": "source",
                    "targets": targets,
                    "disposition": "check",
                }
            ],
            "units": [{"id": "unit-1", "rules": ["rule-1"], "targets": targets}],
            "packets": [{"id": "packet-1", "units": ["unit-1"]}],
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        process, payload = self.run_cli("seal", manifest_path)
        self.assertEqual(process.returncode, 0, process.stderr)
        return manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))

    def write_report(
        self,
        root: Path,
        manifest: dict,
        checks: list[dict],
        packet: str = "packet-1",
    ) -> Path:
        reports = root / "reports"
        reports.mkdir(exist_ok=True)
        report = {"packet": packet, "plan_hash": manifest["plan_hash"], "checks": checks}
        report_path = reports / f"{packet}.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return reports

    @staticmethod
    def passing_check() -> dict:
        return {"unit": "unit-1", "status": "pass", "evidence": ["target1:1"], "findings": []}

    @staticmethod
    def failing_check() -> dict:
        return {
            "unit": "unit-1",
            "status": "fail",
            "evidence": ["target1:1"],
            "findings": [
                {
                    "rule": "rule-1",
                    "at": "target1:1",
                    "defect": "required statement is absent",
                    "severity": "high",
                }
            ],
        }

    def test_seal_records_input_hashes_and_plan_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest_path, manifest = self.make_manifest(Path(directory))
            self.assertTrue(all("sha256" in item for item in manifest["inputs"]))
            self.assertRegex(manifest["plan_hash"], r"^[0-9a-f]{64}$")
            self.assertEqual(json.loads(manifest_path.read_text())["plan_hash"], manifest["plan_hash"])

    def test_clean_pass_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            reports = self.write_report(root, manifest, [self.passing_check()])
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(result["status"], "clean")
            self.assertEqual(result["pass"], 1)

    def test_fail_report_keeps_all_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            reports = self.write_report(root, manifest, [self.failing_check()])
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 1, process.stderr)
            self.assertEqual(result["status"], "findings")
            self.assertEqual(result["fail"], 1)
            self.assertEqual(result["findings"][0]["defect"], "required statement is absent")

    def test_missing_report_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, _ = self.make_manifest(root)
            reports = root / "reports"
            reports.mkdir()
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 1, process.stderr)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["missing"], 1)

    def test_unknown_check_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            reports = self.write_report(
                root,
                manifest,
                [{"unit": "unit-1", "status": "unknown", "reason": "reader unavailable"}],
            )
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 1, process.stderr)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(result["unknown"], 1)

    def test_invalid_pass_requires_evidence_and_empty_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            bad = {"unit": "unit-1", "status": "pass", "evidence": [], "findings": []}
            reports = self.write_report(root, manifest, [bad])
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 2, process.stderr)
            self.assertEqual(result["status"], "invalid")

    def test_unknown_rule_in_finding_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            bad = self.failing_check()
            bad["findings"][0]["rule"] = "rule-does-not-exist"
            reports = self.write_report(root, manifest, [bad])
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 2, process.stderr)
            self.assertEqual(result["status"], "invalid")

    def test_unhashable_report_unit_is_invalid_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            reports = self.write_report(
                root,
                manifest,
                [{"unit": [], "status": "unknown", "reason": "malformed"}],
            )
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 2, process.stderr)
            self.assertEqual(result["status"], "invalid")

    def test_lost_rule_target_pair_invalidates_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, _ = self.make_manifest(root, target_count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["units"][0]["targets"] = ["target1"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            process, result = self.run_cli("seal", manifest_path)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any("no unit coverage" in error for error in result["errors"]))

    def test_same_unit_cannot_be_assigned_to_two_packets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, _ = self.make_manifest(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["packets"].append({"id": "packet-2", "units": ["unit-1"]})
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            process, result = self.run_cli("seal", manifest_path)
            self.assertEqual(process.returncode, 2)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any("assigned to packets" in error for error in result["errors"]))

    def test_stale_source_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, manifest = self.make_manifest(root)
            (root / "source.md").write_text("changed source\n", encoding="utf-8")
            reports = self.write_report(root, manifest, [self.passing_check()])
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 2, process.stderr)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any("stale input" in error for error in result["errors"]))

    def test_report_from_prior_sealed_plan_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path, old_manifest = self.make_manifest(root)
            reports = self.write_report(root, old_manifest, [self.passing_check()])
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            target2 = root / "target2.md"
            target2.write_text("new target\n", encoding="utf-8")
            manifest["inputs"].append({"id": "target2", "path": str(target2)})
            manifest["rules"][0]["targets"].append("target2")
            manifest["units"][0]["targets"].append("target2")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            process, _ = self.run_cli("seal", manifest_path)
            self.assertEqual(process.returncode, 0, process.stderr)
            process, result = self.run_cli("check", manifest_path, reports)
            self.assertEqual(process.returncode, 2, process.stderr)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any("plan_hash" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
