from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = EXPERIMENT / "artifacts/typed-gold-manifest.json"
SCRIPT_DIR = EXPERIMENT / "scripts"

import sys

sys.path.insert(0, str(SCRIPT_DIR))
import build_typed_probe  # noqa: E402


class TypedProbeTests(unittest.TestCase):
    def test_frozen_git_sources_and_exact_membership(self) -> None:
        manifest = build_typed_probe.load_manifest(MANIFEST_PATH)
        results = [
            build_typed_probe.validate_cluster(
                cluster, EXPERIMENT.parents[1]
            )
            for cluster in manifest["clusters"]
        ]
        self.assertEqual([len(result["records"]) for result in results], [4, 5])
        self.assertEqual(
            [result["first"] for result in results],
            [
                "2026-08-14T07:45:46.732000+00:00",
                "2026-08-21T13:31:52+05:00",
            ],
        )
        self.assertEqual(
            [result["latest"] for result in results],
            [
                "2026-08-17T17:46:29+05:00",
                "2026-08-21T14:44:26+05:00",
            ],
        )

    def test_sha_drift_fails_closed(self) -> None:
        manifest = build_typed_probe.load_manifest(MANIFEST_PATH)
        drifted = copy.deepcopy(manifest["clusters"][1])
        drifted["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(build_typed_probe.ProbeError, "SHA mismatch"):
            build_typed_probe.validate_cluster(drifted, EXPERIMENT.parents[1])

    def test_record_membership_drift_fails_closed(self) -> None:
        manifest = build_typed_probe.load_manifest(MANIFEST_PATH)
        drifted = copy.deepcopy(manifest["clusters"][0])
        drifted["records"][0]["quote"] += " drift"
        with self.assertRaisesRegex(build_typed_probe.ProbeError, "quote differs"):
            build_typed_probe.validate_cluster(drifted, EXPERIMENT.parents[1])

    def test_output_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = build_typed_probe.build(
                MANIFEST_PATH, Path(first_dir), EXPERIMENT.parents[1]
            )
            second = build_typed_probe.build(
                MANIFEST_PATH, Path(second_dir), EXPERIMENT.parents[1]
            )
            self.assertEqual(first["clusters"], second["clusters"])
            names = sorted(path.name for path in Path(first_dir).glob("*.md"))
            self.assertEqual(names, sorted(path.name for path in Path(second_dir).glob("*.md")))
            for name in names:
                self.assertEqual(
                    (Path(first_dir) / name).read_bytes(),
                    (Path(second_dir) / name).read_bytes(),
                )

    def test_manifest_is_json_and_has_both_provenance_refs(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        refs = [cluster["source"]["provenance_ref"] for cluster in manifest["clusters"]]
        self.assertEqual(
            refs,
            [
                "6d392ae^:_ops/chat-recall/2026-08-14-124028-codex-019fff2e.md",
                "6d392ae^:_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()
