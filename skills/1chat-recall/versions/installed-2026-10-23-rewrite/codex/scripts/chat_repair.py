#!/usr/bin/env python3
"""Plan then apply stable headings for explicitly verified legacy records.

Dry-run: --address '<file>.md:<line> sha:<known-hash>' --plan-out plan.json
Apply: --apply-plan plan.json (refuses if any planned file changed).
This does not infer what a stale document link originally meant or rewrite it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import uuid

from chat_capture import CaptureError, default_project, restore_files, snapshot_files, write_atomic
from record_identity import corpus_lock, HEADING_RE, record_hash, resolve_record


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_plan(log_dir, addresses):
    mapping = []
    seen = set()
    for address in addresses:
        path, number, raw, identity = resolve_record(log_dir, address)
        if (path.name, number) in seen:
            continue
        seen.add((path.name, number))
        identity = identity or "recall-" + uuid.uuid4().hex
        mapping.append({"file": path.name, "file_sha256": file_hash(path),
                        "line": number, "record_sha256": record_hash(raw),
                        "old_address": f"{path.name}#L{number}",
                        "anchor": f"{path.name}#{identity}", "record_id": identity})
    return {"version": 1, "corpus": str(log_dir.resolve()), "mapping": mapping,
            "warning": "Headings shift legacy line links. Verify and update document references from source evidence; this plan does not infer their original targets."}


def apply_plan(log_dir, plan):
    if plan.get("version") != 1 or plan.get("corpus") != str(log_dir.resolve()):
        raise ValueError("plan belongs to another corpus or unsupported version")
    grouped = {}
    seen = set()
    targets = set()
    for item in plan["mapping"]:
        identity = item["record_id"]
        if not HEADING_RE.fullmatch("### " + identity):
            raise ValueError("invalid record identity in plan")
        if identity in seen:
            raise ValueError("duplicate record identity in plan")
        seen.add(identity)
        address = f"{item['file']}:{item['line']} sha:{item['record_sha256']}"
        path, number, raw, existing = resolve_record(log_dir, address)
        if file_hash(path) != item["file_sha256"] or number != item["line"]:
            raise ValueError(f"{path.name} changed since plan; regenerate mapping before apply")
        if item["anchor"] != f"{path.name}#{identity}" or (existing and existing != identity):
            raise ValueError("plan disagrees with existing identity")
        if (path, number) in targets:
            raise ValueError("duplicate planned target")
        targets.add((path, number))
        if not existing:
            grouped.setdefault(path, []).append((number, identity))
    before = snapshot_files(set(grouped))
    try:
        for path, insertions in grouped.items():
            # keepends preserves every original byte, including CRLF and an absent final newline.
            lines = path.read_bytes().decode("utf-8").splitlines(keepends=True)
            for number, identity in sorted(insertions, reverse=True):
                lines.insert(number - 1, f"### {identity}\n\n")
            write_atomic(path, "".join(lines))
    except (OSError, CaptureError):
        restore_files(before)
        raise
    return {"status": "applied", "mapping": plan["mapping"], "changed_files": len(grouped)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=default_project())
    parser.add_argument("--address", action="append", help="verified record address; repeat for several records")
    parser.add_argument("--plan-out", type=Path)
    parser.add_argument("--apply-plan", type=Path)
    args = parser.parse_args()
    try:
        root = Path(args.project).resolve()
        log_dir = root / "_ops/chat-recall"
        if not log_dir.is_dir():
            raise ValueError("corpus directory does not exist")
        if bool(args.address) == bool(args.apply_plan):
            raise ValueError("choose --address (dry-run) or --apply-plan")
        with corpus_lock(log_dir):
            if args.apply_plan:
                if args.plan_out:
                    raise ValueError("--plan-out belongs to the dry-run")
                result = apply_plan(log_dir, json.loads(args.apply_plan.read_text()))
            else:
                result = make_plan(log_dir, args.address)
                if args.plan_out:
                    plan_path = args.plan_out.resolve()
                    if plan_path.parent == log_dir:
                        raise ValueError("save migration plans outside the corpus")
                    write_atomic(plan_path, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, CaptureError) as error:
        print(f"chat-repair: error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
