#!/usr/bin/env python3
"""Seal and check MaxRevie coverage manifests and packet reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


DISPOSITIONS = {"check", "not_applicable", "superseded"}
STATUSES = {"pass", "fail", "unknown"}
SEVERITIES = {"high", "medium", "low"}
HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in HEX_DIGITS for character in value
    )


def _safe_basename(value: str) -> bool:
    return value not in {".", ".."} and "/" not in value and "\\" not in value


def _unique_strings(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not _text(item):
            errors.append(f"{label} contains a non-empty string requirement")
            continue
        if item in seen:
            errors.append(f"{label} contains duplicate id {item!r}")
        else:
            seen.add(item)
            result.append(item)
    return result


def _load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"cannot read JSON {path}: {exc}"
    return value, None


def _validate_manifest(
    value: Any, *, require_hashes: bool, require_plan_hash: bool = False
) -> tuple[dict[str, Any], list[str]]:
    """Return normalized lookup maps and all structural manifest errors."""

    errors: list[str] = []
    if not isinstance(value, dict):
        return {}, ["manifest must be a JSON object"]

    if require_plan_hash and not _sha(value.get("plan_hash")):
        errors.append("manifest.plan_hash must be a 64-character hexadecimal digest")

    raw_inputs = value.get("inputs")
    raw_rules = value.get("rules")
    raw_units = value.get("units")
    raw_packets = value.get("packets")
    collections = {
        "inputs": raw_inputs,
        "rules": raw_rules,
        "units": raw_units,
        "packets": raw_packets,
    }
    for name, entries in collections.items():
        if not isinstance(entries, list):
            errors.append(f"{name} must be a list")
        elif name in {"inputs", "rules"} and not entries:
            errors.append(f"{name} must not be empty")

    raw_inputs = raw_inputs if isinstance(raw_inputs, list) else []
    raw_rules = raw_rules if isinstance(raw_rules, list) else []
    raw_units = raw_units if isinstance(raw_units, list) else []
    raw_packets = raw_packets if isinstance(raw_packets, list) else []

    inputs: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw_inputs):
        label = f"inputs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = item.get("id")
        if not _text(identifier):
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if identifier in inputs:
            errors.append(f"duplicate input id {identifier!r}")
        else:
            inputs[identifier] = item
        path = item.get("path")
        if not isinstance(path, str) or not os.path.isabs(path):
            errors.append(f"{label}.path must be an absolute path")
        digest = item.get("sha256")
        if "sha256" in item:
            if not _sha(digest):
                errors.append(f"{label}.sha256 must be a 64-character hexadecimal digest")
        elif require_hashes:
            errors.append(f"{label}.sha256 is missing")

    rules: dict[str, dict[str, Any]] = {}
    rule_targets: dict[str, list[str]] = {}
    check_rules: set[str] = set()
    exceptions: list[dict[str, str]] = []
    for index, item in enumerate(raw_rules):
        label = f"rules[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = item.get("id")
        if not _text(identifier):
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if identifier in rules:
            errors.append(f"duplicate rule id {identifier!r}")
        else:
            rules[identifier] = item
        source = item.get("source")
        if not _text(source) or source not in inputs:
            errors.append(f"{label}.source must name an input")
        targets = _unique_strings(item.get("targets"), f"{label}.targets", errors)
        unknown_targets = [target for target in targets if target not in inputs]
        for target in unknown_targets:
            errors.append(f"{label}.targets names unknown input {target!r}")
        disposition = item.get("disposition")
        if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
            errors.append(f"{label}.disposition must be one of {sorted(DISPOSITIONS)}")
        elif disposition == "check":
            check_rules.add(identifier)
        else:
            reason = item.get("reason")
            if not _text(reason):
                errors.append(f"{label} exception requires a non-empty reason")
            else:
                exceptions.append(
                    {"rule": identifier, "disposition": disposition, "reason": reason}
                )
        rule_targets[identifier] = targets

    units: dict[str, dict[str, Any]] = {}
    unit_rules: dict[str, list[str]] = {}
    unit_targets: dict[str, list[str]] = {}
    for index, item in enumerate(raw_units):
        label = f"units[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = item.get("id")
        if not _text(identifier):
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if identifier in units:
            errors.append(f"duplicate unit id {identifier!r}")
        else:
            units[identifier] = item
        referenced_rules = _unique_strings(item.get("rules"), f"{label}.rules", errors)
        targets = _unique_strings(item.get("targets"), f"{label}.targets", errors)
        unit_rules[identifier] = referenced_rules
        unit_targets[identifier] = targets
        for rule in referenced_rules:
            if rule not in rules:
                errors.append(f"{label}.rules names unknown rule {rule!r}")
            elif rule not in check_rules:
                errors.append(f"{label} includes non-check rule {rule!r}")
        for target in targets:
            if target not in inputs:
                errors.append(f"{label}.targets names unknown input {target!r}")
        for rule in referenced_rules:
            allowed = set(rule_targets.get(rule, ()))
            for target in targets:
                if target not in allowed:
                    errors.append(
                        f"{label} target {target!r} is outside rule {rule!r} scope"
                    )

    packets: dict[str, list[str]] = {}
    unit_packet: dict[str, str] = {}
    for index, item in enumerate(raw_packets):
        label = f"packets[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        identifier = item.get("id")
        if not _text(identifier):
            errors.append(f"{label}.id must be a non-empty string")
            continue
        if not _safe_basename(identifier):
            errors.append(f"{label}.id must be a safe basename")
        if identifier in packets:
            errors.append(f"duplicate packet id {identifier!r}")
        units_in_packet = _unique_strings(item.get("units"), f"{label}.units", errors)
        packets[identifier] = units_in_packet
        for unit in units_in_packet:
            if unit not in units:
                errors.append(f"{label}.units names unknown unit {unit!r}")
            elif unit in unit_packet:
                errors.append(
                    f"unit {unit!r} is assigned to packets {unit_packet[unit]!r} and {identifier!r}"
                )
            else:
                unit_packet[unit] = identifier

    for unit in units:
        if unit not in unit_packet:
            errors.append(f"unit {unit!r} is unassigned to a packet")

    assigned_pairs: set[tuple[str, str]] = set()
    for unit, referenced_rules in unit_rules.items():
        for rule in referenced_rules:
            for target in unit_targets.get(unit, ()):
                # Independent rechecks and joint checks may overlap in scope.
                # Each unit still needs its own unique assignment and report.
                assigned_pairs.add((rule, target))

    for rule in check_rules:
        for target in rule_targets.get(rule, ()):
            if (rule, target) not in assigned_pairs:
                errors.append(f"rule-target {rule!r}/{target!r} has no unit coverage")

    return {
        "manifest": value,
        "inputs": inputs,
        "rules": rules,
        "units": units,
        "packets": packets,
        "unit_rules": unit_rules,
        "unit_targets": unit_targets,
        "unit_packet": unit_packet,
        "exceptions": exceptions,
        "plan_hash": value.get("plan_hash"),
    }, errors


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _plan_hash(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("plan_hash", None)
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _check_hashes(plan: dict[str, Any], *, fill_missing: bool) -> tuple[dict[str, str], list[str]]:
    computed: dict[str, str] = {}
    errors: list[str] = []
    for identifier, item in plan["inputs"].items():
        path = Path(item.get("path", ""))
        if not path.is_file():
            errors.append(f"input {identifier!r} is not a readable file: {path}")
            continue
        try:
            actual = _hash_file(path)
        except OSError as exc:
            errors.append(f"cannot hash input {identifier!r} at {path}: {exc}")
            continue
        computed[identifier] = actual
        expected = item.get("sha256")
        if expected is None and fill_missing:
            continue
        if not isinstance(expected, str) or expected.lower() != actual:
            errors.append(f"stale input {identifier!r}: sha256 does not match {path}")
    return computed, errors


def _base_result(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = plan or {}
    return {
        "status": "invalid",
        "rules": len(plan.get("rules", {})),
        "units": len(plan.get("units", {})),
        "pass": 0,
        "fail": 0,
        "unknown": 0,
        "missing": 0,
        "exceptions": list(plan.get("exceptions", [])),
        "errors": [],
        "findings": [],
    }


def _finding(value: Any, unit_rules: list[str], label: str) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(value, dict):
        return None, f"{label} must be an object"
    rule = value.get("rule")
    if rule not in unit_rules:
        return None, f"{label}.rule names a rule outside its unit: {rule!r}"
    address = value.get("at")
    if not _text(address):
        return None, f"{label}.at must be a non-empty address"
    defect = value.get("defect")
    if not _text(defect):
        return None, f"{label}.defect must be a non-empty string"
    severity = value.get("severity")
    if not isinstance(severity, str) or severity not in SEVERITIES:
        return None, f"{label}.severity must be one of {sorted(SEVERITIES)}"
    return value, None


def _validate_check(
    value: Any, expected_unit: str, plan: dict[str, Any]
) -> tuple[str | None, list[dict[str, Any]], list[str]]:
    label = f"unit {expected_unit!r} check"
    if not isinstance(value, dict):
        return None, [], [f"{label} must be an object"]
    unit = value.get("unit")
    if unit != expected_unit:
        return None, [], [f"{label} has mismatched unit id {unit!r}"]
    status = value.get("status")
    if not isinstance(status, str) or status not in STATUSES:
        return None, [], [f"{label}.status must be one of {sorted(STATUSES)}"]

    errors: list[str] = []
    evidence = value.get("evidence")
    if evidence is None and status == "unknown":
        evidence_values: list[Any] = []
    elif not isinstance(evidence, list):
        errors.append(f"{label}.evidence must be a list")
        evidence_values = []
    else:
        evidence_values = evidence
    if any(not _text(address) for address in evidence_values):
        errors.append(f"{label}.evidence entries must be non-empty addresses")
    if status in {"pass", "fail"} and not evidence_values:
        errors.append(f"{label} {status} requires evidence")

    raw_findings = value.get("findings")
    if raw_findings is None and status == "unknown":
        raw_findings = []
    if not isinstance(raw_findings, list):
        errors.append(f"{label}.findings must be a list")
        raw_findings = []
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(raw_findings):
        parsed, error = _finding(item, plan["unit_rules"].get(expected_unit, []), f"{label}.findings[{index}]")
        if error:
            errors.append(error)
        elif parsed is not None:
            findings.append(parsed)
    if status == "pass" and findings:
        errors.append(f"{label} pass requires empty findings")
    if status == "fail" and not findings:
        errors.append(f"{label} fail requires findings")
    if status == "unknown" and not _text(value.get("reason")):
        errors.append(f"{label} unknown requires a non-empty reason")
    return status, findings, errors


def _check_reports(plan: dict[str, Any], reports_dir: Path) -> dict[str, Any]:
    result = _base_result(plan)
    packets: dict[str, list[str]] = plan["packets"]
    expected_names = {f"{packet}.json" for packet in packets}
    if not reports_dir.exists():
        result["missing"] = len(plan["units"])
        result["status"] = "incomplete"
        return result
    if not reports_dir.is_dir():
        result["errors"].append(f"reports path is not a directory: {reports_dir}")
        return result

    try:
        report_files = {
            path.name: path
            for path in reports_dir.iterdir()
            if path.is_file() and path.suffix == ".json"
        }
    except OSError as exc:
        result["errors"].append(f"cannot list reports directory {reports_dir}: {exc}")
        return result
    for name in sorted(set(report_files) - expected_names):
        result["errors"].append(f"unexpected packet report {name!r}")

    for packet, expected_units in packets.items():
        report_path = reports_dir / f"{packet}.json"
        if not report_path.is_file():
            result["missing"] += len(expected_units)
            continue
        report, error = _load_json(report_path)
        if error:
            result["errors"].append(error)
            continue
        if not isinstance(report, dict):
            result["errors"].append(f"report {report_path} must be a JSON object")
            continue
        if report.get("packet") != packet:
            result["errors"].append(
                f"report {report_path} has packet {report.get('packet')!r}, expected {packet!r}"
            )
            continue
        if report.get("plan_hash") != plan["plan_hash"]:
            result["errors"].append(
                f"report {report_path} has a plan_hash different from the manifest"
            )
            continue
        checks = report.get("checks")
        if not isinstance(checks, list):
            result["errors"].append(f"report {report_path}.checks must be a list")
            continue
        expected_set = set(expected_units)
        seen: set[str] = set()
        for index, entry in enumerate(checks):
            label = f"report {report_path} checks[{index}]"
            unit = entry.get("unit") if isinstance(entry, dict) else None
            if not isinstance(unit, str) or unit not in expected_set:
                result["errors"].append(f"{label} names an extra or unknown unit {unit!r}")
                continue
            if unit in seen:
                result["errors"].append(f"{label} repeats unit {unit!r}")
                continue
            seen.add(unit)
            status, findings, errors = _validate_check(entry, unit, plan)
            result["errors"].extend(errors)
            if errors or status is None:
                continue
            if status == "pass":
                result["pass"] += 1
            elif status == "fail":
                result["fail"] += 1
            else:
                result["unknown"] += 1
            result["findings"].extend(findings)
        result["missing"] += len(expected_set - seen)

    if result["errors"]:
        result["status"] = "invalid"
    elif result["unknown"] or result["missing"]:
        result["status"] = "incomplete"
    elif result["fail"]:
        result["status"] = "findings"
    else:
        result["status"] = "clean"
    return result


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def seal(manifest_path: Path) -> int:
    value, error = _load_json(manifest_path)
    if error:
        _emit({"status": "invalid", "errors": [error]})
        return 2
    plan, errors = _validate_manifest(value, require_hashes=False)
    if errors:
        result = _base_result(plan)
        result["errors"] = errors
        _emit(result)
        return 2
    computed, errors = _check_hashes(plan, fill_missing=True)
    if errors:
        result = _base_result(plan)
        result["errors"] = errors
        _emit(result)
        return 2
    assert isinstance(value, dict)
    filled = 0
    for identifier, digest in computed.items():
        if "sha256" not in plan["inputs"][identifier]:
            plan["inputs"][identifier]["sha256"] = digest
            filled += 1
    value["plan_hash"] = _plan_hash(value)
    try:
        manifest_path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        _emit({"status": "invalid", "errors": [f"cannot write manifest {manifest_path}: {exc}"]})
        return 2
    _emit(
        {
            "status": "sealed",
            "manifest": str(manifest_path),
            "filled": filled,
            "plan_hash": value["plan_hash"],
        }
    )
    return 0


def check(manifest_path: Path, reports_dir: Path) -> int:
    value, error = _load_json(manifest_path)
    if error:
        result = _base_result()
        result["errors"] = [error]
        _emit(result)
        return 2
    plan, errors = _validate_manifest(value, require_hashes=True, require_plan_hash=True)
    if errors:
        result = _base_result(plan)
        result["errors"] = errors
        _emit(result)
        return 2
    assert isinstance(value, dict)
    actual_plan_hash = _plan_hash(value)
    if actual_plan_hash != plan["plan_hash"]:
        result = _base_result(plan)
        result["errors"] = ["manifest.plan_hash does not match the sealed manifest"]
        _emit(result)
        return 2
    _, errors = _check_hashes(plan, fill_missing=False)
    if errors:
        result = _base_result(plan)
        result["errors"] = errors
        _emit(result)
        return 2
    result = _check_reports(plan, reports_dir)
    _emit(result)
    return {"clean": 0, "findings": 1, "incomplete": 1, "invalid": 2}[result["status"]]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    seal_parser = commands.add_parser("seal", help="validate and fill missing input hashes")
    seal_parser.add_argument("manifest", type=Path)
    check_parser = commands.add_parser("check", help="validate hashes, plan coverage, and reports")
    check_parser.add_argument("manifest", type=Path)
    check_parser.add_argument("reports_dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "seal":
        return seal(args.manifest.expanduser())
    return check(args.manifest.expanduser(), args.reports_dir.expanduser())


if __name__ == "__main__":
    raise SystemExit(main())
