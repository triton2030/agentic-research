from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = EXPERIMENT / "artifacts/distilled-gold-manifest.json"
SCRIPT_DIR = EXPERIMENT / "scripts"

import sys

sys.path.insert(0, str(SCRIPT_DIR))
import build_distilled_probe  # noqa: E402


class DistilledProbeTests(unittest.TestCase):
    def test_frozen_membership_and_claim_contract(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        bundle = build_distilled_probe.validate_manifest(manifest, EXPERIMENT.parents[1])
        self.assertEqual(
            bundle["frozen_provenance_commit"],
            "09d2a48b2a82ff4b35ffb739a11b5721351d7dd6",
        )
        self.assertEqual(len(bundle["sources"]), 2)
        self.assertEqual(len(bundle["records"]), 7)
        self.assertEqual(
            {claim["lifecycle_status"] for claim in bundle["claims"]},
            {"current", "non-current", "uncertain"},
        )

    def test_supersession_and_scope_status_filter_default_wiki(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            payload = build_distilled_probe.build(
                MANIFEST_PATH,
                root / "input",
                root / "wiki",
                EXPERIMENT.parents[1],
            )
            body = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / "wiki").rglob("*.md")
            )
        self.assertEqual(payload["deterministic_validation"]["status"], "pass")
        self.assertIn("static-derived-library", body)
        self.assertIn("retrieval-scout-boundary", body)
        self.assertIn("distilled-facts-not-history", body)
        self.assertNotIn(
            manifest["claims"][3]["statement"],
            body,
        )
        self.assertNotIn(
            manifest["claims"][4]["statement"],
            body,
        )
        self.assertNotIn(
            manifest["claims"][5]["statement"],
            body,
        )

    def test_drift_and_unknown_contracts_fail_closed(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)

        drifted_blob = copy.deepcopy(manifest)
        drifted_blob["sources"][0]["blob_sha256"] = "0" * 64
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "frozen blob mismatch"):
            build_distilled_probe.validate_manifest(drifted_blob, EXPERIMENT.parents[1])

        drifted_quote = copy.deepcopy(manifest)
        drifted_quote["sources"][0]["records"][0]["quote_sha256"] = "0" * 64
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "quote digest differs"):
            build_distilled_probe.validate_manifest(drifted_quote, EXPERIMENT.parents[1])

        unknown_record = copy.deepcopy(manifest)
        unknown_record["claims"][0]["source_record_ids"] = ["missing.md:1"]
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "unknown source record"):
            build_distilled_probe.validate_manifest(unknown_record, EXPERIMENT.parents[1])

        unknown_status = copy.deepcopy(manifest)
        unknown_status["claims"][0]["lifecycle_status"] = "latest"
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "unknown lifecycle status"):
            build_distilled_probe.validate_manifest(unknown_status, EXPERIMENT.parents[1])

        dangling = copy.deepcopy(manifest)
        dangling["claims"][3]["superseded_by"] = "missing-claim"
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "dangling superseded_by"):
            build_distilled_probe.validate_manifest(dangling, EXPERIMENT.parents[1])

    def test_no_gold_and_default_body_do_not_leak_source_history(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        bundle = build_distilled_probe.validate_manifest(manifest, EXPERIMENT.parents[1])
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_distilled_probe.build(
                MANIFEST_PATH,
                root / "input",
                root / "wiki",
                EXPERIMENT.parents[1],
            )
            body = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / "wiki").rglob("*.md")
            )
        for record in bundle["records"].values():
            self.assertNotIn(record["quote"], body)
        for marker in build_distilled_probe.FORBIDDEN_DEFAULT_MARKERS:
            self.assertNotIn(marker, body)
        for control in bundle["no_gold_controls"]:
            self.assertNotIn(control["statement"], body)

    def test_rebuild_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            build_distilled_probe.build(
                MANIFEST_PATH, first / "input", first / "wiki", EXPERIMENT.parents[1]
            )
            build_distilled_probe.build(
                MANIFEST_PATH, second / "input", second / "wiki", EXPERIMENT.parents[1]
            )
            first_files = {
                path.relative_to(first).as_posix(): path.read_bytes()
                for path in first.rglob("*.md")
            }
            second_files = {
                path.relative_to(second).as_posix(): path.read_bytes()
                for path in second.rglob("*.md")
            }
        self.assertEqual(first_files, second_files)

    def test_receipt_separates_deterministic_and_semantic_status(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_distilled_probe.build(
                MANIFEST_PATH,
                root / "input",
                root / "wiki",
                EXPERIMENT.parents[1],
                root / "receipt.json",
                root / "receipt.md",
            )
            receipt = json.loads((root / "receipt.json").read_text(encoding="utf-8"))
            receipt_md = (root / "receipt.md").read_text(encoding="utf-8")
        self.assertEqual(receipt["deterministic_validation"]["status"], "pass")
        self.assertEqual(receipt["semantic_boundary"]["status"], "candidate")
        self.assertIn("semantic acceptance is external", receipt_md)
        self.assertEqual(
            receipt["provenance_commit"], manifest["frozen_provenance_commit"]
        )


if __name__ == "__main__":
    unittest.main()
