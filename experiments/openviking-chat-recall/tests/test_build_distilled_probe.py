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
    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    @staticmethod
    def _write_manifest(path: Path, manifest: dict) -> None:
        path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

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
        self.assertEqual(len(bundle["claims"]), 6)
        subagent_claim = next(
            claim
            for claim in bundle["claims"]
            if claim["id"] == "subagents-read-and-summarize"
        )
        self.assertEqual(
            subagent_claim["title"], "Earlier broad subagent reading proposal"
        )
        self.assertNotIn("should read and summarize", subagent_claim["title"])
        self.assertEqual(bundle["no_gold_controls"][0]["status"], "abstain")
        self.assertEqual(bundle["no_gold_controls"][0]["resolution"], "unknown")
        self.assertTrue(bundle["no_gold_controls"][0]["coverage_gap"])
        self.assertEqual(
            bundle["no_gold_controls"][0]["coverage_gap"],
            "No supporting record for this universal replacement claim was found at the checked frozen addresses; this route does not establish that no such claim exists elsewhere in _ops/chat-recall/**.",
        )
        self.assertEqual(
            bundle["no_gold_controls"][0]["checked_addresses"],
            [
                "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:25",
                "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:33",
            ],
        )

    def test_supersession_and_scope_status_filter_default_wiki(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        claims = {claim["id"]: claim for claim in manifest["claims"]}
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
        self.assertNotIn(claims["wiki-language-route"]["statement"], body)
        self.assertNotIn(claims["historical-wiki-evolution"]["statement"], body)
        self.assertNotIn(claims["subagents-read-and-summarize"]["statement"], body)
        self.assertNotIn(
            "The distilled Wiki can replace source-holder reads for every question",
            body,
        )
        self.assertNotIn("wiki-language-route", payload["evidence"]["rendered_claim_ids"])
        self.assertEqual(
            payload["evidence"]["suppressed_claim_ids"],
            [
                "wiki-language-route",
                "historical-wiki-evolution",
                "subagents-read-and-summarize",
            ],
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

        drifted_line = copy.deepcopy(manifest)
        drifted_line["sources"][0]["records"][0]["line"] = 20
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError, "record id does not match source address"
        ):
            build_distilled_probe.validate_manifest(drifted_line, EXPERIMENT.parents[1])

        drifted_timestamp = copy.deepcopy(manifest)
        drifted_timestamp["sources"][0]["records"][0]["timestamp"] = (
            "2020-01-01T00:00:00+00:00"
        )
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError, "timestamp differs from frozen source"
        ):
            build_distilled_probe.validate_manifest(
                drifted_timestamp, EXPERIMENT.parents[1]
            )

        drifted_record_id = copy.deepcopy(manifest)
        drifted_record_id["sources"][0]["records"][0]["record_id"] = (
            "_ops/chat-recall/2026-08-20-181330-claude-a7539038.md:999"
        )
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError, "record id does not match source address"
        ):
            build_distilled_probe.validate_manifest(
                drifted_record_id, EXPERIMENT.parents[1]
            )

        unknown_record = copy.deepcopy(manifest)
        unknown_record["claims"][0]["source_record_ids"] = ["missing.md:1"]
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "unknown source record"):
            build_distilled_probe.validate_manifest(unknown_record, EXPERIMENT.parents[1])

        unknown_status = copy.deepcopy(manifest)
        unknown_status["claims"][0]["lifecycle_status"] = "latest"
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "unknown lifecycle status"):
            build_distilled_probe.validate_manifest(unknown_status, EXPERIMENT.parents[1])

        dangling = copy.deepcopy(manifest)
        historical_claim = next(
            claim
            for claim in dangling["claims"]
            if claim["id"] == "historical-wiki-evolution"
        )
        historical_claim["superseded_by"] = "missing-claim"
        with self.assertRaisesRegex(build_distilled_probe.ProbeError, "dangling superseded_by"):
            build_distilled_probe.validate_manifest(dangling, EXPERIMENT.parents[1])

    def test_contested_membership_contract_fails_closed(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)

        def contested_manifest() -> tuple[dict, dict]:
            candidate = copy.deepcopy(manifest)
            claim = next(
                item
                for item in candidate["claims"]
                if item["id"] == "wiki-language-route"
            )
            claim["lifecycle_status"] = "contested"
            return candidate, claim

        missing_conflicts, _ = contested_manifest()
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError,
            "contested claim requires conflict_source_record_ids",
        ):
            build_distilled_probe.validate_manifest(
                missing_conflicts, EXPERIMENT.parents[1]
            )

        one_sided, one_sided_claim = contested_manifest()
        one_sided_claim["conflict_source_record_ids"] = [
            one_sided_claim["source_record_ids"][0]
        ]
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError,
            "at least two distinct conflict source record IDs",
        ):
            build_distilled_probe.validate_manifest(one_sided, EXPERIMENT.parents[1])

        out_of_claim, out_of_claim_item = contested_manifest()
        out_of_claim_item["conflict_source_record_ids"] = [
            out_of_claim_item["source_record_ids"][0],
            "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:33",
        ]
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError,
            "must be included in source_record_ids",
        ):
            build_distilled_probe.validate_manifest(
                out_of_claim, EXPERIMENT.parents[1]
            )

        dangling, dangling_claim = contested_manifest()
        dangling_claim["source_record_ids"] = [
            "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:25",
            "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:33",
        ]
        dangling_claim["conflict_source_record_ids"] = [
            dangling_claim["source_record_ids"][0],
            "missing.md:1",
        ]
        with self.assertRaisesRegex(
            build_distilled_probe.ProbeError,
            "unknown conflict source record id",
        ):
            build_distilled_probe.validate_manifest(dangling, EXPERIMENT.parents[1])

    def test_structural_contested_fixture_stays_candidate(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        candidate = copy.deepcopy(manifest)
        claim = next(
            item
            for item in candidate["claims"]
            if item["id"] == "wiki-language-route"
        )
        conflict_ids = [
            "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:25",
            "_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:33",
        ]
        claim["lifecycle_status"] = "contested"
        claim["source_record_ids"] = conflict_ids
        claim["conflict_source_record_ids"] = conflict_ids

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            fixture_path = root / "manifest.json"
            self._write_manifest(fixture_path, candidate)
            payload = build_distilled_probe.build(
                fixture_path,
                root / "input",
                root / "wiki",
                EXPERIMENT.parents[1],
                root / "receipt.json",
                root / "receipt.md",
            )
            body = "\n".join(
                path.read_text(encoding="utf-8")
                for path in (root / "wiki").rglob("*.md")
            )

        self.assertEqual(payload["semantic_boundary"]["status"], "candidate")
        self.assertIn(
            "semantic opposition between contested source records",
            payload["semantic_boundary"]["not_proven"],
        )
        self.assertIn(
            "contested-membership-structure",
            [
                check["id"]
                for check in payload["deterministic_validation"]["checks"]
            ],
        )
        self.assertEqual(
            payload["evidence"]["contested_membership"],
            [
                {
                    "claim_id": "wiki-language-route",
                    "source_record_ids": conflict_ids,
                    "conflict_source_record_ids": conflict_ids,
                }
            ],
        )
        self.assertIn(claim["statement"], body)

    def test_no_gold_and_default_body_do_not_leak_source_history(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        bundle = build_distilled_probe.validate_manifest(manifest, EXPERIMENT.parents[1])
        control = bundle["no_gold_controls"][0]
        self.assertEqual(control["status"], "abstain")
        self.assertEqual(control["resolution"], "unknown")
        self.assertTrue(control["coverage_gap"])
        self.assertTrue(control["checked_addresses"])
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
            first_files = self._snapshot(first)
            second_files = self._snapshot(second)
        self.assertEqual(first_files, second_files)

    def test_same_directory_rebuild_removes_stale_generated_pages_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_distilled_probe.build(
                MANIFEST_PATH,
                root / "input",
                root / "wiki",
                EXPERIMENT.parents[1],
            )
            stale_page = root / "wiki/concept/static-derived-library.md"
            self.assertTrue(stale_page.exists())
            unrelated_page = root / "wiki/keep-unrelated.md"
            unrelated_page.write_text("unrelated\n", encoding="utf-8")

            manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
            static_claim = next(
                claim
                for claim in manifest["claims"]
                if claim["id"] == "static-derived-library"
            )
            static_claim["lifecycle_status"] = "non-current"
            mutated_manifest = root / "mutated-manifest.json"
            self._write_manifest(mutated_manifest, manifest)
            build_distilled_probe.build(
                mutated_manifest,
                root / "input",
                root / "wiki",
                EXPERIMENT.parents[1],
            )

            self.assertFalse(stale_page.exists())
            self.assertEqual(unrelated_page.read_text(encoding="utf-8"), "unrelated\n")
            self.assertTrue((root / "wiki/concept/retrieval-scout-boundary.md").exists())

    def test_generated_root_symlink_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki_dir = root / "wiki"
            wiki_dir.mkdir(parents=True)
            outside_dir = root / "outside"
            outside_dir.mkdir()
            sentinel = outside_dir / "sentinel.txt"
            sentinel.write_text("must survive\n", encoding="utf-8")
            (wiki_dir / "link").symlink_to(outside_dir, target_is_directory=True)
            (wiki_dir / "keep-unrelated.md").write_text(
                "unrelated\n", encoding="utf-8"
            )
            (wiki_dir / build_distilled_probe.GENERATED_ROOT_MARKER).write_text(
                json.dumps(
                    {
                        "schema": build_distilled_probe.GENERATED_ROOT_SCHEMA,
                        "files": ["link/sentinel.txt"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                build_distilled_probe.ProbeError,
                "owned destination escapes generated root through a symlink",
            ):
                build_distilled_probe.build(
                    MANIFEST_PATH,
                    root / "input",
                    wiki_dir,
                    EXPERIMENT.parents[1],
                )

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "must survive\n")
            self.assertEqual(
                (wiki_dir / "keep-unrelated.md").read_text(encoding="utf-8"),
                "unrelated\n",
            )

    def test_projection_includes_current_and_suppresses_uncertain_or_non_current(self) -> None:
        manifest = build_distilled_probe.load_manifest(MANIFEST_PATH)
        claims = {claim["id"]: claim for claim in manifest["claims"]}
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
        self.assertIn(claims["static-derived-library"]["statement"], body)
        for claim_id in (
            "wiki-language-route",
            "historical-wiki-evolution",
            "subagents-read-and-summarize",
        ):
            self.assertNotIn(claims[claim_id]["statement"], body)
            self.assertIn(claim_id, payload["evidence"]["suppressed_claim_ids"])

    def test_committed_generated_outputs_match_current_writer(self) -> None:
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
            self.assertEqual(
                self._snapshot(root / "input"),
                self._snapshot(EXPERIMENT / "artifacts/distilled-input"),
            )
            self.assertEqual(
                self._snapshot(root / "wiki"),
                self._snapshot(EXPERIMENT / "artifacts/distilled-wiki"),
            )
            self.assertEqual(
                (root / "receipt.json").read_bytes(),
                (EXPERIMENT / "artifacts/distilled-probe-receipt.json").read_bytes(),
            )
            self.assertEqual(
                (root / "receipt.md").read_bytes(),
                (EXPERIMENT / "artifacts/distilled-probe-receipt.md").read_bytes(),
            )
            receipt = json.loads((root / "receipt.json").read_text(encoding="utf-8"))
            receipt_md = (root / "receipt.md").read_text(encoding="utf-8")
        self.assertEqual(receipt["deterministic_validation"]["status"], "pass")
        self.assertEqual(receipt["semantic_boundary"]["status"], "candidate")
        self.assertIn("semantic acceptance is external", receipt_md)
        self.assertEqual(
            receipt["provenance_commit"], manifest["frozen_provenance_commit"]
        )
        self.assertNotIn("nested_agent_receipts", receipt)
        self.assertNotIn("01a024c8", receipt_md)


if __name__ == "__main__":
    unittest.main()
