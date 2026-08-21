from __future__ import annotations

import hashlib
import json
import random
import shutil
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT.parents[1]
SCRIPT_DIR = EXPERIMENT / "scripts"
RECORDS = EXPERIMENT / "artifacts/full-build/evidence/records.jsonl"
COVERAGE = EXPERIMENT / "artifacts/full-build/evidence/coverage-input.json"
OUTPUT = EXPERIMENT / "artifacts/full-build/clusters"

import sys

sys.path.insert(0, str(SCRIPT_DIR))
import build_cluster_proposals  # noqa: E402


class ClusterProposalTests(unittest.TestCase):
    @staticmethod
    def _json(path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _records(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    @staticmethod
    def _snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and not path.is_symlink()
        }

    @staticmethod
    def _copy_inputs(root: Path) -> tuple[Path, Path]:
        root.mkdir(parents=True, exist_ok=True)
        records = root / "records.jsonl"
        coverage = root / "coverage-input.json"
        shutil.copy2(RECORDS, records)
        shutil.copy2(COVERAGE, coverage)
        return records, coverage

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _build(self, root: Path) -> tuple[Path, dict]:
        records, coverage = self._copy_inputs(root)
        output = root / "clusters"
        result = build_cluster_proposals.build(
            repo_root=REPO_ROOT,
            records_path=records,
            coverage_path=coverage,
            output_dir=output,
        )
        return output, result

    def test_full_coverage_schema_rule_and_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output, result = self._build(Path(temp_dir))
            manifest = self._json(output / "partition-manifest.json")
            source_records = self._records(RECORDS)
            part_records = [
                record
                for part in manifest["parts"]
                for record in self._records(output / part["path"])
            ]

        self.assertEqual(result["part_count"], 8)
        self.assertEqual(result["record_count"], 1101)
        self.assertEqual(result["used_count"], 1067)
        self.assertEqual(result["rejected_count"], 34)
        self.assertEqual(result["min_part_records"], 135)
        self.assertEqual(result["max_part_records"], 141)
        self.assertEqual(result["median_part_records"], 137.5)
        self.assertEqual(manifest["schema"], build_cluster_proposals.MANIFEST_SCHEMA)
        self.assertEqual(manifest["input"]["records"]["sha256"], build_cluster_proposals.EXPECTED_RECORDS_SHA256)
        self.assertEqual(manifest["input"]["coverage"]["sha256"], build_cluster_proposals.EXPECTED_COVERAGE_SHA256)
        self.assertEqual(manifest["rule"]["config"]["part_count"], 8)
        self.assertEqual(manifest["rule"]["config"]["target_records_per_part"], 138)
        self.assertEqual(manifest["rule"]["oversized_topics"][0]["record_count"], 624)
        self.assertEqual(manifest["rule"]["oversized_topics"][0]["shard_count"], 5)
        self.assertEqual(manifest["coverage"]["part_record_count_sum"], 1101)
        self.assertEqual(manifest["coverage"]["unique_record_id_count"], 1101)
        self.assertEqual(manifest["coverage"]["disposition_counts"], {"rejected": 34, "skipped": 0, "used": 1067})
        self.assertEqual(len({record["record_id"] for record in part_records}), 1101)
        self.assertEqual({record["record_id"] for record in part_records}, {record["record_id"] for record in source_records})
        self.assertEqual(
            {record["disposition"] for record in part_records}, {"used", "rejected"}
        )
        self.assertEqual(
            sum(record["disposition"] == "rejected" for record in part_records), 34
        )
        self.assertTrue(all(record["disposition_reason"] for record in part_records if record["disposition"] == "rejected"))
        serialized = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
        self.assertNotIn(str(REPO_ROOT), serialized)
        self.assertNotIn("HEAD", serialized)
        self.assertNotIn("mtime", serialized)

    def test_part_rows_preserve_f2_evidence_objects_and_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output, _ = self._build(Path(temp_dir))
            manifest = self._json(output / "partition-manifest.json")
            source_by_id = {record["record_id"]: record for record in self._records(RECORDS)}
            for part in manifest["parts"]:
                rows = self._records(output / part["path"])
                self.assertEqual(rows, sorted(rows, key=build_cluster_proposals._partition_row_key))
                for row in rows:
                    self.assertEqual(row, source_by_id[row["record_id"]])
                self.assertEqual(
                    hashlib.sha256((output / part["path"]).read_bytes()).hexdigest(),
                    part["input_sha256"],
                )

    def test_topic_and_session_cohesion_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output, _ = self._build(Path(temp_dir))
            manifest = self._json(output / "partition-manifest.json")
            locations: dict[tuple[str, str], set[str]] = {}
            topic_locations: dict[str, set[str]] = {}
            for part in manifest["parts"]:
                for record in self._records(output / part["path"]):
                    topic = record["metadata"]["topic"]
                    session = record["metadata"]["session"]
                    locations.setdefault((topic, session), set()).add(part["part_id"])
                    topic_locations.setdefault(topic, set()).add(part["part_id"])
        self.assertTrue(all(len(parts) == 1 for parts in locations.values()))
        self.assertEqual(
            [topic for topic, parts in topic_locations.items() if len(parts) > 1],
            ["агенты-и-ии"],
        )
        self.assertEqual(len(topic_locations["агенты-и-ии"]), 5)

    def test_shuffled_input_order_has_identical_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            normal, _ = self._build(root / "normal")
            shuffled_root = root / "shuffled"
            shuffled_root.mkdir()
            records, coverage = self._copy_inputs(shuffled_root)
            record_lines = records.read_text(encoding="utf-8").splitlines()
            random.Random(17).shuffle(record_lines)
            records.write_text("\n".join(record_lines) + "\n", encoding="utf-8")
            coverage_value = self._json(coverage)
            random.Random(23).shuffle(coverage_value["records"])
            self._write_json(coverage, coverage_value)
            shuffled = shuffled_root / "clusters"
            build_cluster_proposals.build(
                repo_root=REPO_ROOT,
                records_path=records,
                coverage_path=coverage,
                output_dir=shuffled,
            )
            self.assertEqual(self._snapshot(normal), self._snapshot(shuffled))

    def test_two_fresh_builds_are_byte_identical_and_unrelated_survives(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first, _ = self._build(root / "first")
            second, _ = self._build(root / "second")
            self.assertEqual(self._snapshot(first), self._snapshot(second))
            unrelated = first / "keep-unrelated.txt"
            unrelated.write_text("preserve\n", encoding="utf-8")
            build_cluster_proposals.build(
                repo_root=REPO_ROOT,
                records_path=first.parent / "records.jsonl",
                coverage_path=first.parent / "coverage-input.json",
                output_dir=first,
            )
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "preserve\n")

    def test_committed_artifacts_match_current_writer(self) -> None:
        result = build_cluster_proposals.check(
            repo_root=REPO_ROOT,
            records_path=RECORDS,
            coverage_path=COVERAGE,
            output_dir=OUTPUT,
        )
        self.assertEqual(result["status"], "pass")

    def test_f2_record_and_coverage_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            records, coverage = self._copy_inputs(root)
            output = root / "clusters"
            output.mkdir()
            sentinel = output / "sentinel.txt"
            sentinel.write_text("preserve\n", encoding="utf-8")
            rows = self._records(records)
            rows[0]["quote"] += " drift"
            records.write_text(
                "".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                    for row in rows
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(build_cluster_proposals.ClusterError, "evidence"):
                build_cluster_proposals.build(
                    repo_root=REPO_ROOT,
                    records_path=records,
                    coverage_path=coverage,
                    output_dir=output,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve\n")

            records, coverage = self._copy_inputs(root)
            coverage_value = self._json(coverage)
            coverage_value["records"].pop()
            self._write_json(coverage, coverage_value)
            with self.assertRaisesRegex(build_cluster_proposals.ClusterError, "coverage"):
                build_cluster_proposals.build(
                    repo_root=REPO_ROOT,
                    records_path=records,
                    coverage_path=coverage,
                    output_dir=output,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve\n")

    def test_missing_live_holder_tree_does_not_change_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            normal, _ = self._build(root / "normal")
            isolated = root / "isolated"
            isolated.mkdir()
            records, coverage = self._copy_inputs(isolated)
            output = isolated / "clusters"
            build_cluster_proposals.build(
                repo_root=isolated,
                records_path=records,
                coverage_path=coverage,
                output_dir=output,
            )
            self.assertEqual(self._snapshot(normal), self._snapshot(output))

    def test_generated_root_and_part_escape_fail_without_touching_sentinel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            records, coverage = self._copy_inputs(root)
            target = root / "external"
            target.mkdir()
            sentinel = target / "sentinel.txt"
            sentinel.write_text("safe\n", encoding="utf-8")
            symlink_root = root / "clusters-link"
            symlink_root.symlink_to(target, target_is_directory=True)
            with self.assertRaises(build_cluster_proposals.ClusterError):
                build_cluster_proposals.build(
                    repo_root=REPO_ROOT,
                    records_path=records,
                    coverage_path=coverage,
                    output_dir=symlink_root,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "safe\n")

            output, _ = self._build(root / "clean")
            manifest_path = output / build_cluster_proposals.MANIFEST_NAME
            manifest = self._json(manifest_path)
            manifest["parts"][0]["path"] = "../external/sentinel.txt"
            self._write_json(manifest_path, manifest)
            with self.assertRaises(build_cluster_proposals.ClusterError):
                build_cluster_proposals.build(
                    repo_root=REPO_ROOT,
                    records_path=root / "clean/records.jsonl",
                    coverage_path=root / "clean/coverage-input.json",
                    output_dir=output,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "safe\n")

    def test_stale_owned_part_cleanup_requires_full_preflight_and_preserves_unrelated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output, _ = self._build(root)
            unrelated = output / "keep-unrelated.txt"
            unrelated.write_text("preserve\n", encoding="utf-8")
            manifest_path = output / build_cluster_proposals.MANIFEST_NAME
            manifest = self._json(manifest_path)
            stale_dir = output / "part-999"
            stale_dir.mkdir()
            stale_path = stale_dir / "input.jsonl"
            stale_path.write_bytes((output / manifest["parts"][0]["path"]).read_bytes())
            stale = dict(manifest["parts"][0])
            stale["part_id"] = "part-999"
            stale["path"] = "part-999/input.jsonl"
            manifest["parts"].append(stale)
            manifest["parts"].sort(key=lambda part: part["part_id"])
            manifest["outputs"]["parts_sha256"] = build_cluster_proposals._parts_digest(manifest["parts"])
            self._write_json(manifest_path, manifest)
            build_cluster_proposals.build(
                repo_root=REPO_ROOT,
                records_path=root / "records.jsonl",
                coverage_path=root / "coverage-input.json",
                output_dir=output,
            )
            self.assertFalse(stale_dir.exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "preserve\n")

    def test_part_directory_without_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            records, coverage = self._copy_inputs(root)
            output = root / "clusters"
            (output / "part-999").mkdir(parents=True)
            sentinel = output / "part-999/input.jsonl"
            sentinel.write_text("do not delete\n", encoding="utf-8")
            with self.assertRaises(build_cluster_proposals.ClusterError):
                build_cluster_proposals.build(
                    repo_root=REPO_ROOT,
                    records_path=records,
                    coverage_path=coverage,
                    output_dir=output,
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not delete\n")


if __name__ == "__main__":
    unittest.main()
