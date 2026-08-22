from __future__ import annotations

import json
import random
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import build_chronological_batch as builder  # noqa: E402


FROZEN = EXPERIMENT / "artifacts/full-build/frozen/source-manifest.json"
RECORDS = EXPERIMENT / "artifacts/full-build/evidence/records.jsonl"
BATCH1 = EXPERIMENT / "artifacts/chronological-pilot/batch-001-input.json"
BATCH2 = EXPERIMENT / "artifacts/chronological-pilot/batch-002-input.json"
RECEIPT2 = EXPERIMENT / "artifacts/chronological-pilot/batch-002/receipt.json"
ACCEPTED_BATCH2_COMMIT = "ade7d0583930495479f3739a6db54cb47003b7fb"


class BuildChronologicalBatchTests(unittest.TestCase):
    def test_reproduces_batch1_batch2_and_exact_batch3(self) -> None:
        ordered, no_records, metadata = builder.load_ordered_inventory(FROZEN, RECORDS)
        historical1 = json.loads(BATCH1.read_text(encoding="utf-8"))
        historical2 = json.loads(BATCH2.read_text(encoding="utf-8"))

        self.assertEqual(
            [item["source_path"] for item in ordered[:10]],
            [item["source_path"] for item in historical1["holders"]],
        )
        self.assertEqual(
            [item["source_path"] for item in ordered[10:20]],
            [item["source_path"] for item in historical2["holders"]],
        )

        value = builder.build_manifest(
            repo_root=REPO,
            batch_number=3,
            frozen_manifest_path=FROZEN,
            records_path=RECORDS,
            previous_manifest_path=BATCH2,
            previous_receipt_path=RECEIPT2,
            accepted_prior_commit=ACCEPTED_BATCH2_COMMIT,
        )
        self.assertEqual(
            [item["source_path"] for item in value["holders"]],
            [
                "_ops/chat-recall/2026-07-30-131107-codex-019fb213.md",
                "_ops/chat-recall/2026-07-29-201927-codex-019fadc9.md",
                "_ops/chat-recall/2026-07-31-005511-codex-019fb495.md",
                "_ops/chat-recall/2026-07-29-201852-codex-019fada0.md",
                "_ops/chat-recall/2026-07-31-200328-codex-019fb8b3.md",
                "_ops/chat-recall/2026-08-01-122733-claude-188605a7.md",
                "_ops/chat-recall/2026-08-01-122602-claude-5db612ad.md",
                "_ops/chat-recall/2026-08-01-145225-claude-444200aa.md",
                "_ops/chat-recall/2026-08-01-164842-claude-d2c4b3e7.md",
                "_ops/chat-recall/2026-08-01-172241-codex-019fbd46.md",
            ],
        )
        self.assertEqual(
            value["counts"],
            {
                "holder_count": 10,
                "record_count": 38,
                "diagnostic_record_count": 0,
                "source_quote_chars": 8606,
                "source_quote_utf8_bytes": 15596,
                "cumulative_holder_count": 30,
                "cumulative_record_count": 90,
                "cumulative_diagnostic_record_count": 0,
                "cumulative_source_quote_chars": 19410,
                "cumulative_source_quote_utf8_bytes": 35208,
            },
        )
        self.assertEqual(value["time_boundary_utc"], "2026-08-01T12:22:41.874000+00:00")
        self.assertEqual(metadata["frozen_holder_count"], 184)
        self.assertEqual(metadata["record_bearing_holder_count"], 183)
        self.assertEqual(
            no_records,
            ["_ops/chat-recall/2026-08-11-000000-claude-1ae24acb.md"],
        )
        self.assertEqual(
            value["run_state"]["terminal_coverage_equation"],
            "183 record-bearing + 1 no-record = 184 frozen",
        )

    def test_record_file_order_does_not_change_holder_order(self) -> None:
        expected, expected_no_records, expected_metadata = builder.load_ordered_inventory(
            FROZEN, RECORDS
        )
        lines = RECORDS.read_bytes().splitlines()
        random.Random(1729).shuffle(lines)
        with tempfile.TemporaryDirectory() as temp_dir:
            shuffled = Path(temp_dir) / "records.jsonl"
            shuffled.write_bytes(b"\n".join(lines) + b"\n")
            actual, actual_no_records, actual_metadata = builder.load_ordered_inventory(
                FROZEN, shuffled
            )
        self.assertEqual(
            [(item["source_path"], item["record_ids"]) for item in actual],
            [(item["source_path"], item["record_ids"]) for item in expected],
        )
        self.assertEqual(actual_no_records, expected_no_records)
        self.assertEqual(
            actual_metadata["record_count"], expected_metadata["record_count"]
        )

    def test_naive_and_date_only_timestamps_use_almaty(self) -> None:
        self.assertEqual(
            builder._utc_text(builder._utc_timestamp("2026-07-29", "cr-date")),
            "2026-07-28T19:00:00+00:00",
        )
        self.assertEqual(
            builder._utc_text(
                builder._utc_timestamp("2026-07-29T12:00:00", "cr-naive")
            ),
            "2026-07-29T07:00:00+00:00",
        )

    def test_duplicate_record_and_unknown_holder_fail(self) -> None:
        original = RECORDS.read_bytes().splitlines()
        cases: list[tuple[bytes, str]] = []
        cases.append((b"\n".join(original + [original[0]]) + b"\n", "duplicate"))
        unknown = json.loads(original[0])
        unknown["source_path"] = "_ops/chat-recall/not-frozen.md"
        unknown["source_address"] = "_ops/chat-recall/not-frozen.md:1"
        unknown["source_line"] = 1
        mutated = [json.dumps(unknown, ensure_ascii=False, sort_keys=True).encode("utf-8")]
        mutated.extend(original[1:])
        cases.append((b"\n".join(mutated) + b"\n", "source fields"))

        for raw, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp_dir:
                path = Path(temp_dir) / "records.jsonl"
                path.write_bytes(raw)
                with self.assertRaisesRegex(builder.BatchBuildError, message):
                    builder.load_ordered_inventory(FROZEN, path)

    def test_prior_commit_and_check_mode_are_frozen(self) -> None:
        with self.assertRaisesRegex(builder.BatchBuildError, "full 40-character SHA"):
            builder.build_manifest(
                repo_root=REPO,
                batch_number=3,
                frozen_manifest_path=FROZEN,
                records_path=RECORDS,
                previous_manifest_path=BATCH2,
                previous_receipt_path=RECEIPT2,
                accepted_prior_commit="ade7d05",
                verify_git=False,
            )

        value = builder.build_manifest(
            repo_root=REPO,
            batch_number=3,
            frozen_manifest_path=FROZEN,
            records_path=RECORDS,
            previous_manifest_path=BATCH2,
            previous_receipt_path=RECEIPT2,
            accepted_prior_commit=ACCEPTED_BATCH2_COMMIT,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "batch-003-input.json"
            builder.write_manifest(output, value, check=False)
            builder.write_manifest(output, value, check=True)
            output.write_bytes(output.read_bytes() + b" ")
            with self.assertRaisesRegex(builder.BatchBuildError, "stale"):
                builder.write_manifest(output, value, check=True)


if __name__ == "__main__":
    unittest.main()
