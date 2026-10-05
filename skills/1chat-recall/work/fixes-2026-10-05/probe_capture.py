#!/usr/bin/env python3
"""Exercise delivered CLI interfaces only against an OS temporary corpus."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid


def probe(package):
    calls = []
    checks = {}
    with tempfile.TemporaryDirectory(prefix="recall-cli-probe-") as temporary:
        root = Path(temporary)
        session = str(uuid.uuid4())

        def capture(quote, *options, agent="claude", type_="решение", relation=True):
            command = [sys.executable, str(package / "scripts/chat_capture.py"),
                       "--project", str(root), "--session", session, "--agent", agent,
                       "--quote", quote, "--type", type_, "--topic", "probe",
                       "--context-note", "Временная проба; помощник Capture", "--json"]
            if relation:
                command.append("--supersedes-none")
            command += options
            result = subprocess.run(command, text=True, capture_output=True,
                                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            calls.append({"command": command, "exit_code": result.returncode,
                          "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode:
                raise RuntimeError(result.stderr)
            return json.loads(result.stdout)

        first = capture("Тест: запись в текущем ходе", "--new-topic", "Временные CLI-пробы",
                        "--session-context", "помощник Capture; прежний предмет", agent="Claude")
        old_a = capture("Тест: прежнее решение А", "--source-timestamp", "2026-10-01T12:00:00.123456Z")
        old_b = capture("Тест: прежнее решение Б", "--source-timestamp", "2026-10-02T12:00:00Z", agent="CLAUDE")
        checks["case_insensitive_same_holder"] = first["path"] == old_a["path"] == old_b["path"]
        checks["same_turn_no_timestamp_or_ref"] = first["deduplication"] == "none" and "warning" in first
        path = Path(first["path"])
        earlier_body = path.read_text().split("### ", 1)[1].rstrip()
        replacement = capture("Тест: новое решение", "--source-timestamp", "2026-10-03T12:00:00Z",
                              "--supersedes", old_a["anchor"], old_b["anchor"], relation=False)
        contested = capture("Тест: спорная позиция", "--contested", old_a["anchor"],
                            "--contested", old_b["anchor"], relation=False)
        permission = capture("Тест: согласие архивировать указанную папку", "--add-subjects", "новый предмет; синоним",
                             type_="разрешение", relation=False)
        script = '''import json,sys
sys.path.insert(0,sys.argv[1])
import chat_digest as digest
from pathlib import Path
records,_ = digest.load(Path(sys.argv[2]))
digest.link_supersessions(records)
print(json.dumps(records,ensure_ascii=False))
'''
        read = subprocess.run([sys.executable, "-c", script, str(package / "scripts"), str(root / "_ops/chat-recall")],
                              capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if read.returncode:
            raise RuntimeError(read.stderr)
        records = json.loads(read.stdout)
        previous = [record for record in records if record["address"] in {old_a["anchor"], old_b["anchor"]}]
        checks["multiple_supersedes_linked"] = len(previous) == 2 and all(record["superseded_by"] == [replacement["anchor"]] for record in previous)
        checks["multiple_contested_linked"] = all(record["contested_by"] == [contested["anchor"]] for record in previous)
        checks["add_subjects_preserved_card"] = all(record["session_context"] == "помощник Capture; прежний предмет; новый предмет; синоним" for record in records)
        checks["earlier_quotes_unchanged"] = earlier_body + "\n" in path.read_text()
        checks["permission_roundtrip"] = any(record["address"] == permission["anchor"] and record["type"] == "разрешение" and not record["diagnostics"] for record in records)
        checks["fractional_timestamp_preserved"] = any(record["timestamp"] == "2026-10-01T12:00:00.123456+00:00" for record in records)
        checks["all_calls_exit_zero"] = all(call["exit_code"] == 0 for call in calls)
        return {"package": str(package), "temporary_root": str(root),
                "checks": checks, "calls": calls, "records": records,
                "holder": path.read_text(), "passed": all(checks.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = probe(args.package.resolve())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"package": result["package"], "checks": result["checks"]}, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
