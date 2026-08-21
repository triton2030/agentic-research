from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT.parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
FROZEN_DIR = EXPERIMENT / "artifacts/full-build/frozen"
SNAPSHOT_COMMIT = "6f98fcccdbf4b4de45ef787239ad101f70d106e2"
EXPECTED_DIAGNOSTIC_ADDRESSES = {
    "duplicate-session-holder": [
        "_ops/chat-recall/2026-08-09-165734-codex-019fe662.md:16",
        "_ops/chat-recall/2026-08-09-165734-codex-019fe662.md:17",
        "_ops/chat-recall/2026-08-09-165734-codex-019fe662.md:18",
        "_ops/chat-recall/2026-08-09-165734-codex-019fe662.md:19",
        "_ops/chat-recall/2026-08-09-171636-Codex-019fe662.md:19",
        "_ops/chat-recall/2026-08-09-171636-Codex-019fe662.md:20",
        "_ops/chat-recall/2026-08-09-171636-Codex-019fe662.md:21",
        "_ops/chat-recall/2026-08-09-171636-Codex-019fe662.md:22",
        "_ops/chat-recall/2026-08-09-171636-Codex-019fe662.md:23",
        "_ops/chat-recall/2026-08-14-120225-codex-019ffae9.md:16",
        "_ops/chat-recall/2026-08-14-120225-codex-019ffae9.md:17",
        "_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:19",
        "_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:20",
        "_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:21",
        "_ops/chat-recall/2026-08-14-135604-Codex-019ffae9.md:22",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:19",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:20",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:21",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:22",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:23",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:24",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:25",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:26",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:27",
        "_ops/chat-recall/2026-08-15-134233-codex-01a00494.md:28",
        "_ops/chat-recall/2026-08-16-063500-Codex-01a00494.md:15",
        "_ops/chat-recall/2026-08-19-023138-codex-01a016c7.md:17",
        "_ops/chat-recall/2026-08-19-023138-codex-01a016c7.md:18",
        "_ops/chat-recall/2026-08-19-122330-claude-01a016c7.md:15",
    ],
    "invalid-type": [
        "_ops/chat-recall/2026-08-20-222832-codex-01a02036.md:29",
    ],
    "unmarked-approximate": [
        "_ops/chat-recall/2026-08-12-000000-claude-2649459a.md:19",
        "_ops/chat-recall/2026-08-12-000000-claude-2649459a.md:20",
        "_ops/chat-recall/2026-08-12-000000-claude-2649459a.md:21",
        "_ops/chat-recall/2026-08-12-000000-claude-2649459a.md:22",
    ],
}

sys.path.insert(0, str(SCRIPT_DIR))
import build_evidence_layer  # noqa: E402


class EvidenceLayerTests(unittest.TestCase):
    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and not path.is_symlink()
        }

    @staticmethod
    def _json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _records(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    @staticmethod
    def _copy_frozen(root: Path) -> Path:
        frozen = root / "frozen"
        shutil.copytree(FROZEN_DIR, frozen)
        return frozen

    def test_exact_snapshot_schema_counts_and_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evidence"
            summary = build_evidence_layer.build(
                REPO_ROOT, SNAPSHOT_COMMIT, output, FROZEN_DIR
            )
            records = self._records(output / "records.jsonl")
            coverage = self._json(output / "coverage-input.json")

        self.assertEqual(summary["holder_count"], 184)
        self.assertEqual(summary["record_count"], 1101)
        self.assertEqual(summary["diagnostic_record_count"], 34)
        self.assertEqual(
            summary["diagnostic_counts"],
            {
                "duplicate-session-holder": 29,
                "invalid-type": 1,
                "unmarked-approximate": 4,
            },
        )
        diagnostic_addresses = {
            diagnostic: [
                record["source_address"]
                for record in records
                if diagnostic in record["diagnostics"]
            ]
            for diagnostic in EXPECTED_DIAGNOSTIC_ADDRESSES
        }
        self.assertEqual(diagnostic_addresses, EXPECTED_DIAGNOSTIC_ADDRESSES)
        self.assertEqual(len(records), 1101)
        self.assertEqual(len({record["record_id"] for record in records}), 1101)
        self.assertEqual(coverage["schema"], "openviking-chat-recall/coverage-input.v1")
        self.assertEqual(len(coverage["records"]), 1101)
        self.assertEqual(
            len({item["record_id"] for item in coverage["records"]}), 1101
        )
        self.assertEqual(coverage["source"]["diagnostic_record_count"], 34)
        self.assertEqual(
            sum(bool(item["diagnostics"]) for item in coverage["records"]),
            34,
        )
        coverage_diagnostic_addresses = {
            diagnostic: [
                item["source_address"]
                for item in coverage["records"]
                if diagnostic in item["diagnostics"]
            ]
            for diagnostic in EXPECTED_DIAGNOSTIC_ADDRESSES
        }
        self.assertEqual(
            coverage_diagnostic_addresses,
            EXPECTED_DIAGNOSTIC_ADDRESSES,
        )
        self.assertEqual(
            {item["disposition"] for item in records}, {"used", "rejected"}
        )
        rejected = [record for record in records if record["disposition"] == "rejected"]
        self.assertEqual(len(rejected), 34)
        self.assertTrue(all(record["disposition_reason"] for record in rejected))
        self.assertTrue(all(record["diagnostics"] for record in rejected))
        self.assertTrue(all(record["source_address"].startswith("_ops/chat-recall/") for record in records))
        self.assertTrue(all("/Users/triton/.codex/worktrees/" not in json.dumps(record) for record in records))
        self.assertTrue(
            all(
                record["content_sha256"]
                == hashlib.sha256(record["quote"].encode("utf-8")).hexdigest()
                for record in records
            )
        )

    def test_two_fresh_builds_are_identical_and_unrelated_file_survives(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, first, FROZEN_DIR)
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, second, FROZEN_DIR)
            self.assertEqual(self._snapshot(first), self._snapshot(second))

            unrelated = first / "keep-unrelated.txt"
            unrelated.write_text("must survive\n", encoding="utf-8")
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, first, FROZEN_DIR)
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "must survive\n")

    def test_check_matches_generated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evidence"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, output, FROZEN_DIR)
            result = build_evidence_layer.check(REPO_ROOT, SNAPSHOT_COMMIT, output, FROZEN_DIR)
        self.assertEqual(result["status"], "pass")

    def test_committed_artifacts_match_current_writer(self) -> None:
        result = build_evidence_layer.check(
            REPO_ROOT,
            SNAPSHOT_COMMIT,
            EXPERIMENT / "artifacts/full-build/evidence",
            FROZEN_DIR,
        )
        self.assertEqual(result["status"], "pass")

    def test_output_record_and_coverage_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evidence"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, output, FROZEN_DIR)

            records_path = output / "records.jsonl"
            records = self._records(records_path)
            records[0]["source_line"] += 1
            records_path.write_text(
                "".join(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for record in records),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(build_evidence_layer.EvidenceError, "records.jsonl differs"):
                build_evidence_layer.check(REPO_ROOT, SNAPSHOT_COMMIT, output, FROZEN_DIR)

            clean_output = Path(temp_dir) / "clean-evidence"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, clean_output, FROZEN_DIR)
            coverage_path = clean_output / "coverage-input.json"
            coverage = self._json(coverage_path)
            coverage["records"].pop()
            coverage_path.write_text(
                json.dumps(coverage, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(build_evidence_layer.EvidenceError, "coverage-input.json differs"):
                build_evidence_layer.check(REPO_ROOT, SNAPSHOT_COMMIT, clean_output, FROZEN_DIR)

            missing_output = Path(temp_dir) / "missing-record-evidence"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, missing_output, FROZEN_DIR)
            missing_records = self._records(missing_output / "records.jsonl")[:-1]
            (missing_output / "records.jsonl").write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    + "\n"
                    for record in missing_records
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(build_evidence_layer.EvidenceError, "records.jsonl differs"):
                build_evidence_layer.check(REPO_ROOT, SNAPSHOT_COMMIT, missing_output, FROZEN_DIR)

            duplicate_output = Path(temp_dir) / "duplicate-record-evidence"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, duplicate_output, FROZEN_DIR)
            duplicate_records = self._records(duplicate_output / "records.jsonl")
            duplicate_records[-1] = duplicate_records[0]
            (duplicate_output / "records.jsonl").write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    + "\n"
                    for record in duplicate_records
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(build_evidence_layer.EvidenceError, "records.jsonl differs"):
                build_evidence_layer.check(REPO_ROOT, SNAPSHOT_COMMIT, duplicate_output, FROZEN_DIR)

    def test_invalid_commit_and_frozen_input_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            frozen = self._copy_frozen(root)
            with self.assertRaises(build_evidence_layer.EvidenceError):
                build_evidence_layer.build(REPO_ROOT, "HEAD", root / "head", frozen)
            with self.assertRaises(build_evidence_layer.EvidenceError):
                build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT[:7], root / "short", frozen)

            manifest = self._json(frozen / "source-manifest.json")
            manifest["files"][0]["sha256"] = "0" * 64
            (frozen / "source-manifest.json").write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(build_evidence_layer.EvidenceError, "manifest digest drift"):
                build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, root / "manifest", frozen)

    def test_symlink_owned_output_fails_without_touching_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "evidence"
            output.mkdir()
            sentinel = root / "sentinel.txt"
            sentinel.write_text("preserve\n", encoding="utf-8")
            (output / "records.jsonl").symlink_to(sentinel)
            with self.assertRaises(build_evidence_layer.EvidenceError):
                build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, output, FROZEN_DIR)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve\n")

    def test_live_dirty_holder_does_not_change_git_object_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            clone = root / "clone"
            subprocess.run(
                ["git", "clone", "--quiet", "--no-hardlinks", str(REPO_ROOT), str(clone)],
                check=True,
                capture_output=True,
            )
            frozen = clone / "experiments/openviking-chat-recall/artifacts/full-build/frozen"
            dirty_holder = clone / "_ops/chat-recall/2026-04-28-111714-claude-74356077.md"
            dirty_holder.write_text("* 2099-01-01 — \"dirty\" — kind: quote | type: факт | topic: факт\n", encoding="utf-8")
            clean_output = root / "clean"
            dirty_output = root / "dirty"
            build_evidence_layer.build(REPO_ROOT, SNAPSHOT_COMMIT, clean_output, FROZEN_DIR)
            build_evidence_layer.build(clone, SNAPSHOT_COMMIT, dirty_output, frozen)
            self.assertEqual(self._snapshot(clean_output), self._snapshot(dirty_output))


if __name__ == "__main__":
    unittest.main()
