#!/usr/bin/env python3
"""Read-only local hashing and comparison with supplied Drive metadata."""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys


class VerificationError(Exception):
    """Only fixed, non-sensitive reason codes cross the CLI boundary."""


STAT_KEYS = {"device", "inode", "size", "mtime_ns", "ctime_ns"}
REMOTE_KEYS = {
    "schemaVersion", "checkedAt", "accountKey", "fileId", "size",
    "sha256Checksum", "md5Checksum", "version", "trashed", "binaryFile",
    "canDownload", "ownedByMe",
}
LOCAL_KEYS = {
    "schemaVersion", "kind", "status", "startedAt", "finishedAt", "sourcePath",
    "fstatBefore", "fstatAfter", "pathBefore", "pathAfter", "bytesRead",
    "sha256", "md5", "deleteAllowed",
}
UTC_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)\Z")
OPAQUE_ID = re.compile(r"[A-Za-z0-9_-]{1,256}\Z")
DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,24})\Z")
CLI_REASON_CODES = frozenset({
    "ARGUMENT_ERROR", "OUTPUT_IS_INPUT", "OUTPUT_EXISTS", "OUTPUT_PARENT_CHANGED",
    "SOURCE_SYMLINK", "SOURCE_NOT_REGULAR", "SOURCE_EMPTY", "LOCAL_CHANGED_DURING_READ",
})


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def timestamp(value):
    if not isinstance(value, str) or not UTC_TIME.fullmatch(value):
        raise ValueError("timestamp")
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def fingerprint(info):
    return {"device": info.st_dev, "inode": info.st_ino, "size": info.st_size,
            "mtime_ns": info.st_mtime_ns, "ctime_ns": info.st_ctime_ns}


def path_snapshot(path):
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode):
        raise VerificationError("SOURCE_SYMLINK")
    if not stat.S_ISREG(info.st_mode):
        raise VerificationError("SOURCE_NOT_REGULAR")
    return {**fingerprint(info), "realPath": os.path.realpath(path)}


def _read_chunk(fd):
    # A small seam lets tests mutate/replace a synthetic file during a real read.
    return os.read(fd, 1024 * 1024)


def hash_file(path):
    source = os.path.abspath(path)
    started = now()
    path_before = path_snapshot(source)
    if path_before["size"] <= 0:
        raise VerificationError("SOURCE_EMPTY")
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    fd = os.open(source, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise VerificationError("SOURCE_NOT_REGULAR")
        before = fingerprint(info)
        if before != {key: path_before[key] for key in STAT_KEYS}:
            raise VerificationError("LOCAL_CHANGED_DURING_READ")
        sha256 = hashlib.sha256()
        md5 = hashlib.md5(usedforsecurity=False)
        count = 0
        while chunk := _read_chunk(fd):
            count += len(chunk)
            sha256.update(chunk)
            md5.update(chunk)
        after = fingerprint(os.fstat(fd))
        path_after = path_snapshot(source)
        if (before != after or path_before != path_after or count != before["size"]
                or after != {key: path_after[key] for key in STAT_KEYS}):
            raise VerificationError("LOCAL_CHANGED_DURING_READ")
    finally:
        os.close(fd)
    return {
        "schemaVersion": 1, "kind": "local-hash", "status": "LOCAL_HASHED",
        "startedAt": started, "finishedAt": now(), "sourcePath": source,
        "fstatBefore": before, "fstatAfter": after,
        "pathBefore": path_before, "pathAfter": path_after, "bytesRead": count,
        "sha256": sha256.hexdigest(), "md5": md5.hexdigest(), "deleteAllowed": False,
    }


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _invalid_constant(_value):
    raise ValueError("non-JSON constant")


def load_record(path):
    source = os.path.abspath(path)
    before = path_snapshot(source)
    fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        first = fingerprint(info)
        if not stat.S_ISREG(info.st_mode) or first != {key: before[key] for key in STAT_KEYS}:
            raise ValueError("unstable input")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("oversized input")
        if first != fingerprint(os.fstat(fd)) or before != path_snapshot(source):
            raise ValueError("unstable input")
    finally:
        os.close(fd)
    return json.loads(raw, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)


def checksum(value, length, nullable=False):
    return (nullable and value is None) or (
        isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{" + str(length) + r"}", value) is not None
    )


def valid_remote(record):
    if not isinstance(record, dict) or set(record) != REMOTE_KEYS:
        return False
    try:
        timestamp(record["checkedAt"])
    except (ValueError, TypeError):
        return False
    return (
        type(record["schemaVersion"]) is int and record["schemaVersion"] == 1
        and all(isinstance(record[key], str) and OPAQUE_ID.fullmatch(record[key])
                for key in ("accountKey", "fileId"))
        and isinstance(record["size"], str) and DECIMAL.fullmatch(record["size"]) is not None
        and checksum(record["sha256Checksum"], 64, nullable=True)
        and checksum(record["md5Checksum"], 32, nullable=True)
        and (record["version"] is None or (
            isinstance(record["version"], str) and DECIMAL.fullmatch(record["version"]) is not None))
        and type(record["binaryFile"]) is bool
        and all(record[key] is None or type(record[key]) is bool
                for key in ("trashed", "canDownload", "ownedByMe"))
    )


def valid_stat(value, with_path=False):
    keys = STAT_KEYS | ({"realPath"} if with_path else set())
    return (isinstance(value, dict) and set(value) == keys
            and all(type(value[key]) is int and value[key] >= 0 for key in STAT_KEYS)
            and (not with_path or (isinstance(value["realPath"], str)
                                  and os.path.isabs(value["realPath"]))))


def valid_local(record):
    if not isinstance(record, dict) or set(record) != LOCAL_KEYS:
        return False
    try:
        start, finish = timestamp(record["startedAt"]), timestamp(record["finishedAt"])
    except (ValueError, TypeError):
        return False
    return (
        type(record["schemaVersion"]) is int and record["schemaVersion"] == 1
        and record["kind"] == "local-hash" and record["status"] == "LOCAL_HASHED"
        and record["deleteAllowed"] is False and start <= finish
        and isinstance(record["sourcePath"], str) and os.path.isabs(record["sourcePath"])
        and all(valid_stat(record[key]) for key in ("fstatBefore", "fstatAfter"))
        and all(valid_stat(record[key], with_path=True) for key in ("pathBefore", "pathAfter"))
        and type(record["bytesRead"]) is int and record["bytesRead"] > 0
        and checksum(record["sha256"], 64) and checksum(record["md5"], 32)
    )


def compare_records(local, before, after):
    local_valid = valid_local(local)
    before_valid, after_valid = valid_remote(before), valid_remote(after)
    evidence = {
        "local": ({key: local[key] for key in ("startedAt", "finishedAt", "bytesRead", "sha256", "md5")}
                  if local_valid else None),
        "before": dict(before) if before_valid else None,
        "after": dict(after) if after_valid else None,
    }
    report = {"schemaVersion": 1, "kind": "archive-comparison", "evaluatedAt": now(),
              "evidenceCheckedAt": after["checkedAt"] if after_valid else None,
              "evidence": evidence,
              "status": "UNVERIFIED", "reason": "INVALID_LOCAL_RECORD",
              "deleteAllowed": False, "restoreAccessConfirmed": False}

    def result(status, reason):
        report.update(status=status, reason=reason)
        return report

    if not local_valid:
        return report
    if not before_valid:
        return result("UNVERIFIED", "INVALID_REMOTE_BEFORE")
    if not after_valid:
        return result("UNVERIFIED", "INVALID_REMOTE_AFTER")
    if before["accountKey"] != after["accountKey"]:
        return result("UNVERIFIED", "REMOTE_ACCOUNT_CHANGED")
    if before["fileId"] != after["fileId"]:
        return result("UNVERIFIED", "REMOTE_ID_CHANGED")
    start, finish = timestamp(local["startedAt"]), timestamp(local["finishedAt"])
    if not timestamp(before["checkedAt"]) < start <= finish < timestamp(after["checkedAt"]):
        return result("UNVERIFIED", "TIMESTAMP_ORDER_INVALID")
    first = local["fstatBefore"]
    if (first != local["fstatAfter"] or local["pathBefore"] != local["pathAfter"]
            or first != {key: local["pathBefore"][key] for key in STAT_KEYS}
            or first["size"] != local["bytesRead"]):
        return result("UNVERIFIED", "LOCAL_READING_UNSTABLE")
    if not before["binaryFile"] or not after["binaryFile"]:
        return result("UNVERIFIED", "REMOTE_NOT_BINARY")
    if before["trashed"] is not False or after["trashed"] is not False:
        return result("UNVERIFIED", "REMOTE_TRASH_STATE_UNCONFIRMED")
    if before["version"] is None or after["version"] is None:
        return result("UNVERIFIED", "REMOTE_VERSION_UNAVAILABLE")
    if before["version"] != after["version"]:
        return result("UNVERIFIED", "REMOTE_VERSION_CHANGED")
    if before["size"] != after["size"]:
        return result("UNVERIFIED", "REMOTE_SIZE_CHANGED")
    if before["sha256Checksum"] is None or after["sha256Checksum"] is None:
        return result("UNVERIFIED", "REMOTE_SHA256_UNAVAILABLE")
    if before["sha256Checksum"].lower() != after["sha256Checksum"].lower():
        return result("UNVERIFIED", "REMOTE_SHA256_CHANGED")
    if int(before["size"]) != local["bytesRead"]:
        return result("CANDIDATE_DIFFERS", "SIZE_MISMATCH")
    if local["sha256"].lower() != before["sha256Checksum"].lower():
        return result("CANDIDATE_DIFFERS", "SHA256_MISMATCH")
    if any(item["md5Checksum"] is not None and item["md5Checksum"].lower() != local["md5"].lower()
           for item in (before, after)):
        return result("UNVERIFIED", "MD5_METADATA_CONFLICT")
    report["restoreAccessConfirmed"] = all(
        item[key] is True for item in (before, after) for key in ("canDownload", "ownedByMe")
    )
    return result("MATCH_SHA256", "SHA256_SIZE_VERSION_CONFIRMED")


def validate_output(path, inputs):
    target = os.path.abspath(path)
    if any(target == os.path.abspath(item) or os.path.realpath(target) == os.path.realpath(item)
           for item in inputs):
        raise VerificationError("OUTPUT_IS_INPUT")
    if os.path.lexists(target):
        raise VerificationError("OUTPUT_EXISTS")


def write_atomic(path, record, inputs):
    """Publish once with link(2); an existing name is never replaced."""
    validate_output(path, inputs)
    target = Path(os.path.abspath(path))
    parent_real = os.path.realpath(target.parent)
    directory = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    temp_name = ".archive-verify-" + secrets.token_hex(16) + ".tmp"
    created = False
    try:
        fd = os.open(temp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
        created = True
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=True, sort_keys=True, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        live = os.stat(target.parent)
        pinned = os.fstat(directory)
        if (live.st_dev, live.st_ino) != (pinned.st_dev, pinned.st_ino) or os.path.realpath(target.parent) != parent_real:
            raise VerificationError("OUTPUT_PARENT_CHANGED")
        os.link(temp_name, target.name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
    finally:
        if created:
            os.unlink(temp_name, dir_fd=directory)  # Only this operation's private temporary file.
        os.close(directory)


class QuietParser(argparse.ArgumentParser):
    def error(self, _message):
        raise VerificationError("ARGUMENT_ERROR")


def main(argv=None):
    parser = QuietParser(prog="archive_verify.py", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=QuietParser)
    hash_parser = commands.add_parser("hash", help="Hash one nonempty regular local file.")
    hash_parser.add_argument("--path", required=True)
    hash_parser.add_argument("--out", required=True, help="New JSON report path; must not exist.")
    compare_parser = commands.add_parser("compare", help="Compare local record and two supplied metadata probes.")
    for name in ("local", "before", "after", "out"):
        compare_parser.add_argument("--" + name, required=True)
    try:
        args = parser.parse_args(argv)
        if args.command == "hash":
            inputs = [args.path]
            validate_output(args.out, inputs)
            record = hash_file(args.path)
        else:
            inputs = [args.local, args.before, args.after]
            validate_output(args.out, inputs)
            records = []
            for path in inputs:
                try:
                    records.append(load_record(path))
                except (OSError, ValueError, RecursionError, VerificationError):
                    records.append(None)
            record = compare_records(*records)
        write_atomic(args.out, record, inputs)
        return 0 if record["status"] in ("LOCAL_HASHED", "MATCH_SHA256") else 2
    except VerificationError as error:
        reason = str(error)
        print(reason if reason in CLI_REASON_CODES else "INTERNAL_ERROR", file=sys.stderr)
        return 2
    except OSError:
        print("IO_ERROR", file=sys.stderr)
        return 2
    except Exception:
        print("INTERNAL_ERROR", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
