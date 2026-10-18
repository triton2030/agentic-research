"""Synthetic-only tests; no network, credentials, media, or cloud calls."""

import contextlib
import copy
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "shared/1google-drive-archive/portable/scripts"))
import archive_verify as verifier


class ArchiveVerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "synthetic.bin"
        self.content = b"synthetic test content\x00\xff" * 31
        self.source.write_bytes(self.content)
        self.local = verifier.hash_file(self.source)
        self.before = self.remote(verifier.timestamp(self.local["startedAt"]) - dt.timedelta(seconds=1))
        self.after = self.remote(verifier.timestamp(self.local["finishedAt"]) + dt.timedelta(seconds=1))

    def remote(self, checked):
        return {
            "schemaVersion": 1, "checkedAt": checked.isoformat().replace("+00:00", "Z"),
            "accountKey": "opaquePermission_123", "fileId": "opaque-file_456",
            "size": str(len(self.content)), "sha256Checksum": hashlib.sha256(self.content).hexdigest(),
            "md5Checksum": hashlib.md5(self.content, usedforsecurity=False).hexdigest(),
            "version": "101", "trashed": False, "binaryFile": True,
            "canDownload": True, "ownedByMe": True,
        }

    def compare(self, reason, status="UNVERIFIED"):
        result = verifier.compare_records(self.local, self.before, self.after)
        self.assertEqual((result["status"], result["reason"]), (status, reason))
        self.assertIs(result["deleteAllowed"], False)
        return result

    def write_json(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = verifier.main([str(arg) for arg in args])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_stable_hash_and_match(self):
        self.assertEqual(self.local["sha256"], hashlib.sha256(self.content).hexdigest())
        self.assertEqual(self.local["md5"], hashlib.md5(self.content, usedforsecurity=False).hexdigest())
        self.assertEqual(self.local["bytesRead"], len(self.content))
        result = self.compare("SHA256_SIZE_VERSION_CONFIRMED", "MATCH_SHA256")
        self.assertIs(result["restoreAccessConfirmed"], True)

    def test_cli_hash_then_compare_writes_private_reports_silently(self):
        local_path = self.root / "local.json"
        self.assertEqual(self.run_cli("hash", "--path", self.source, "--out", local_path), (0, "", ""))
        self.assertEqual(local_path.stat().st_mode & 0o777, 0o600)
        local = json.loads(local_path.read_text())
        self.before = self.remote(verifier.timestamp(local["startedAt"]) - dt.timedelta(seconds=1))
        self.after = self.remote(verifier.timestamp(local["finishedAt"]) + dt.timedelta(seconds=1))
        before_path = self.write_json("before.json", self.before)
        after_path = self.write_json("after.json", self.after)
        output = self.root / "comparison.json"
        self.assertEqual(self.run_cli("compare", "--local", local_path, "--before", before_path,
                                     "--after", after_path, "--out", output), (0, "", ""))
        result = json.loads(output.read_text())
        self.assertEqual(result["status"], "MATCH_SHA256")
        self.assertIs(result["deleteAllowed"], False)
        self.assertEqual(list(self.root.glob(".archive-verify-*")), [])

    def test_missing_or_malformed_remote_fields(self):
        for key in verifier.REMOTE_KEYS:
            with self.subTest(missing=key):
                before = copy.deepcopy(self.before)
                del before[key]
                self.assertEqual(verifier.compare_records(self.local, before, self.after)["reason"],
                                 "INVALID_REMOTE_BEFORE")
        for key, value in (("schemaVersion", True), ("size", 1), ("size", "-1"),
                           ("sha256Checksum", "bad"), ("version", ""), ("accountKey", "person@example.com"),
                           ("fileId", ""), ("canDownload", "yes"), ("binaryFile", None),
                           ("checkedAt", "2026-01-01T00:00:00+01:00")):
            with self.subTest(key=key, value=value):
                before = {**self.before, key: value}
                self.assertEqual(verifier.compare_records(self.local, before, self.after)["reason"],
                                 "INVALID_REMOTE_BEFORE")

    def test_malformed_after(self):
        self.after["extra"] = "arbitrary-private-value"
        self.compare("INVALID_REMOTE_AFTER")

    def test_missing_sha_is_never_md5_match(self):
        for side in (self.before, self.after):
            side["sha256Checksum"] = None
        self.compare("REMOTE_SHA256_UNAVAILABLE")

    def test_sha_mismatch_despite_identical_md5(self):
        self.before["sha256Checksum"] = self.after["sha256Checksum"] = "0" * 64
        self.compare("SHA256_MISMATCH", "CANDIDATE_DIFFERS")

    def test_remote_sha_changes(self):
        self.after["sha256Checksum"] = "0" * 64
        self.compare("REMOTE_SHA256_CHANGED")

    def test_version_change(self):
        self.after["version"] = "102"
        self.compare("REMOTE_VERSION_CHANGED")

    def test_unknown_version(self):
        self.before["version"] = None
        self.compare("REMOTE_VERSION_UNAVAILABLE")

    def test_remote_identity_must_match(self):
        for key, reason in (("fileId", "REMOTE_ID_CHANGED"), ("accountKey", "REMOTE_ACCOUNT_CHANGED")):
            with self.subTest(key=key):
                after = {**self.after, key: "different_opaque"}
                self.assertEqual(verifier.compare_records(self.local, self.before, after)["reason"], reason)

    def test_unknown_access_still_proves_sha_but_not_restore_access(self):
        for key in ("canDownload", "ownedByMe"):
            with self.subTest(key=key):
                after = {**self.after, key: None}
                result = verifier.compare_records(self.local, self.before, after)
                self.assertEqual(result["status"], "MATCH_SHA256")
                self.assertIs(result["restoreAccessConfirmed"], False)
                self.assertIs(result["deleteAllowed"], False)

    def test_size_change_and_local_size_mismatch(self):
        self.after["size"] = str(len(self.content) + 1)
        self.compare("REMOTE_SIZE_CHANGED")
        self.before["size"] = self.after["size"]
        self.compare("SIZE_MISMATCH", "CANDIDATE_DIFFERS")

    def test_unstable_or_missing_remote_sha_prevents_candidate_difference(self):
        self.before["size"] = self.after["size"] = str(len(self.content) + 1)
        self.after["sha256Checksum"] = "0" * 64
        self.compare("REMOTE_SHA256_CHANGED")
        self.after["sha256Checksum"] = None
        self.compare("REMOTE_SHA256_UNAVAILABLE")

    def test_not_binary_and_trashed_metadata(self):
        self.before["binaryFile"] = False
        self.compare("REMOTE_NOT_BINARY")
        self.before["binaryFile"] = True
        self.after["trashed"] = None
        self.compare("REMOTE_TRASH_STATE_UNCONFIRMED")

    def test_md5_conflict_and_absence(self):
        self.after["md5Checksum"] = "0" * 32
        self.compare("MD5_METADATA_CONFLICT")
        self.after["md5Checksum"] = self.before["md5Checksum"] = None
        self.compare("SHA256_SIZE_VERSION_CONFIRMED", "MATCH_SHA256")

    def test_timestamp_strict_bracketing(self):
        for side, value in (("before", self.local["startedAt"]), ("after", self.local["finishedAt"]),
                            ("before", self.after["checkedAt"]), ("after", self.before["checkedAt"])):
            with self.subTest(side=side):
                before, after = dict(self.before), dict(self.after)
                (before if side == "before" else after)["checkedAt"] = value
                self.assertEqual(verifier.compare_records(self.local, before, after)["reason"],
                                 "TIMESTAMP_ORDER_INVALID")
        self.local["finishedAt"] = self.local["startedAt"]
        self.compare("SHA256_SIZE_VERSION_CONFIRMED", "MATCH_SHA256")

    def test_report_binds_historical_evidence_without_relabeling_cloud_time(self):
        evaluated = "2030-01-01T00:00:00.000000Z"
        with patch.object(verifier, "now", return_value=evaluated):
            report = self.compare("SHA256_SIZE_VERSION_CONFIRMED", "MATCH_SHA256")
        self.assertEqual(report["evaluatedAt"], evaluated)
        self.assertEqual(report["evidenceCheckedAt"], self.after["checkedAt"])
        self.assertEqual(report["evidence"]["before"], self.before)
        self.assertEqual(report["evidence"]["after"], self.after)
        self.assertEqual(report["evidence"]["local"]["sha256"], self.local["sha256"])
        self.assertEqual(report["evidence"]["local"]["startedAt"], self.local["startedAt"])
        self.assertNotIn("sourcePath", json.dumps(report))
        self.assertNotIn("realPath", json.dumps(report))

    def test_invalid_local_and_unstable_record(self):
        malformed = copy.deepcopy(self.local)
        del malformed["pathBefore"]
        self.assertEqual(verifier.compare_records(malformed, self.before, self.after)["reason"],
                         "INVALID_LOCAL_RECORD")
        for field in ("inode", "size", "mtime_ns", "ctime_ns", "device"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.local)
                changed["fstatAfter"][field] += 1
                self.assertEqual(verifier.compare_records(changed, self.before, self.after)["reason"],
                                 "LOCAL_READING_UNSTABLE")
        self.local["pathAfter"]["realPath"] += "-replacement"
        self.compare("LOCAL_READING_UNSTABLE")

    def test_rejects_empty_directory_and_symlink(self):
        empty = self.root / "empty"
        empty.touch()
        link = self.root / "link"
        link.symlink_to(self.source)
        for source, reason in ((empty, "SOURCE_EMPTY"), (self.root, "SOURCE_NOT_REGULAR"),
                               (link, "SOURCE_SYMLINK")):
            with self.subTest(source=source.name):
                with self.assertRaisesRegex(verifier.VerificationError, reason):
                    verifier.hash_file(source)

    def test_controlled_mutation_during_read(self):
        original = verifier._read_chunk
        mutated = False

        def mutate(fd):
            nonlocal mutated
            chunk = original(fd)
            if not mutated:
                mutated = True
                with self.source.open("ab") as stream:
                    stream.write(b"mutation")
            return chunk

        with patch.object(verifier, "_read_chunk", side_effect=mutate):
            with self.assertRaisesRegex(verifier.VerificationError, "LOCAL_CHANGED_DURING_READ"):
                verifier.hash_file(self.source)

    def test_replaced_path_with_identical_bytes_during_read(self):
        original = verifier._read_chunk
        replacement = self.root / "replacement"
        replacement.write_bytes(self.content)
        replaced = False

        def replace(fd):
            nonlocal replaced
            chunk = original(fd)
            if not replaced:
                replaced = True
                os.replace(replacement, self.source)
            return chunk

        with patch.object(verifier, "_read_chunk", side_effect=replace):
            with self.assertRaisesRegex(verifier.VerificationError, "LOCAL_CHANGED_DURING_READ"):
                verifier.hash_file(self.source)

    def test_symlink_replaces_path_during_read(self):
        original = verifier._read_chunk
        other = self.root / "other"
        other.write_bytes(self.content)
        replacement = self.root / "replacement-link"
        replacement.symlink_to(other)
        replaced = False

        def replace(fd):
            nonlocal replaced
            chunk = original(fd)
            if not replaced:
                replaced = True
                os.replace(replacement, self.source)
            return chunk

        with patch.object(verifier, "_read_chunk", side_effect=replace):
            with self.assertRaisesRegex(verifier.VerificationError, "SOURCE_SYMLINK"):
                verifier.hash_file(self.source)

    def test_output_cannot_clobber_source_or_existing_file(self):
        code, stdout, stderr = self.run_cli("hash", "--path", self.source, "--out", self.source)
        self.assertEqual((code, stdout, stderr), (2, "", "OUTPUT_IS_INPUT\n"))
        self.assertEqual(self.source.read_bytes(), self.content)
        output = self.root / "existing"
        output.write_bytes(b"keep")
        self.assertEqual(self.run_cli("hash", "--path", self.source, "--out", output),
                         (2, "", "OUTPUT_EXISTS\n"))
        self.assertEqual(output.read_bytes(), b"keep")
        alias = self.root / "source-alias"
        os.link(self.source, alias)
        self.assertEqual(self.run_cli("hash", "--path", self.source, "--out", alias),
                         (2, "", "OUTPUT_EXISTS\n"))
        self.assertEqual(self.source.read_bytes(), self.content)

    def test_compare_cannot_clobber_any_input(self):
        paths = [self.write_json(name, record) for name, record in (
            ("local.json", self.local), ("before.json", self.before), ("after.json", self.after))]
        for path in paths:
            with self.subTest(path=path.name):
                content = path.read_bytes()
                self.assertEqual(self.run_cli("compare", "--local", paths[0], "--before", paths[1],
                                             "--after", paths[2], "--out", path),
                                 (2, "", "OUTPUT_IS_INPUT\n"))
                self.assertEqual(path.read_bytes(), content)

    def test_atomic_publication_never_overwrites_racing_file(self):
        target = self.root / "raced.json"
        original = os.link

        def race(*args, **kwargs):
            target.write_bytes(b"concurrent writer")
            return original(*args, **kwargs)

        with patch.object(verifier.os, "link", side_effect=race):
            self.assertEqual(self.run_cli("hash", "--path", self.source, "--out", target),
                             (2, "", "IO_ERROR\n"))
        self.assertEqual(target.read_bytes(), b"concurrent writer")
        self.assertEqual(list(self.root.glob(".archive-verify-*")), [])

    def test_missing_malformed_duplicate_and_nan_inputs_produce_fixed_report(self):
        local_path = self.write_json("local.json", self.local)
        after_path = self.write_json("after.json", self.after)
        for index, raw in enumerate((None, "{broken", '{"size":"1","size":"2"}', '{"size":NaN}',
                                     "[" * 2000 + "]" * 2000, " " * (1024 * 1024 + 1))):
            with self.subTest(raw=raw):
                before_path = self.root / f"before-{index}.json"
                if raw is not None:
                    before_path.write_text(raw)
                output = self.root / f"result-{index}.json"
                self.assertEqual(self.run_cli("compare", "--local", local_path, "--before", before_path,
                                             "--after", after_path, "--out", output), (2, "", ""))
                result = json.loads(output.read_text())
                self.assertEqual(result["reason"], "INVALID_REMOTE_BEFORE")
                self.assertIs(result["deleteAllowed"], False)

    def test_synthetic_secret_redaction(self):
        secret = "SYNTHETIC_SECRET_DO_NOT_EXPOSE_928417"
        missing = self.root / secret
        code, stdout, stderr = self.run_cli("hash", "--path", missing, "--out", self.root / "result.json")
        self.assertEqual((code, stdout, stderr), (2, "", "IO_ERROR\n"))
        self.assertEqual(self.run_cli("hash", "--unknown", secret), (2, "", "ARGUMENT_ERROR\n"))
        local_path = self.write_json("local.json", self.local)
        before_path = self.write_json("before.json", {**self.before, "secret": secret})
        after_path = self.write_json("after.json", self.after)
        output = self.root / "comparison.json"
        response = self.run_cli("compare", "--local", local_path, "--before", before_path,
                                "--after", after_path, "--out", output)
        self.assertEqual(response, (2, "", ""))
        self.assertNotIn(secret, output.read_text())
        with patch.object(verifier, "hash_file", side_effect=OSError(secret)):
            self.assertEqual(self.run_cli("hash", "--path", self.source, "--out", self.root / "io.json"),
                             (2, "", "IO_ERROR\n"))
        for failure in (ValueError(secret), verifier.VerificationError(secret)):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(verifier, "hash_file", side_effect=failure):
                    self.assertEqual(self.run_cli("hash", "--path", self.source,
                                                 "--out", self.root / "exception.json"),
                                     (2, "", "INTERNAL_ERROR\n"))

    def test_help_is_available(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), self.assertRaises(SystemExit) as caught:
            verifier.main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertIn("hash", stdout.getvalue())
        self.assertIn("compare", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
