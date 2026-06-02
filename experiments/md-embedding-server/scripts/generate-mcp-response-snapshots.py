#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "tests/golden/mcp-responses"
DOC = ROOT / "docs/mcp-response-snapshots.md"
FIXTURE = ROOT / "tests/fixtures/sample-corpus"

sys.path.insert(0, str(ROOT / "src"))

from md_cli.catalog import TOOLS_BY_ID  # noqa: E402


CANONICAL_OVERRIDES: dict[str, dict[str, Any]] = {
    "md_cluster": {"corpus": str(FIXTURE)},
    "md_coherence_audit": {"path": str(ROOT / "README.md"), "scan": str(FIXTURE)},
    "md_extract": {"map_data": {"root": str(FIXTURE), "files": []}},
    "md_search_read": {"corpus": str(FIXTURE), "query": "sample"},
}


VOLATILE_KEYS = {
    "expires_at",
    "fingerprint",
    "last_touched",
    "session_usd",
    "transaction_id",
    "turn_usd",
}


def main() -> int:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, bool]] = []
    for tool_id in sorted(TOOLS_BY_ID):
        args = canonical_args(tool_id)
        payload = run_tool(tool_id, args)
        payload = scrub_volatile(payload)
        wrapped = {
            "tool": tool_id,
            "canonical_args": args,
            "is_error": bool(payload.get("error")),
            "payload": payload,
        }
        write_json(SNAPSHOT_DIR / f"{tool_id}.json", wrapped)
        rows.append((tool_id, bool(payload.get("error"))))
    write_doc(rows)
    return 0


def canonical_args(tool_id: str) -> dict[str, Any]:
    if tool_id in CANONICAL_OVERRIDES:
        return CANONICAL_OVERRIDES[tool_id]
    path = SNAPSHOT_DIR / f"{tool_id}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data.get("canonical_args"), dict):
            return data["canonical_args"]
    return {}


def run_tool(tool_id: str, args: dict[str, Any]) -> dict[str, Any]:
    spec = TOOLS_BY_ID[tool_id]
    argv = [sys.executable, "-m", "md_cli", spec.subcommand]
    used: set[str] = set()
    for key in spec.positional_args:
        if key not in args:
            continue
        value = args[key]
        if isinstance(value, list):
            argv.extend(str(item) for item in value)
        else:
            argv.append(str(value))
        used.add(key)
    for key, value in args.items():
        if key in used or value in (None, False):
            continue
        flag = "--" + key.replace("_", "-")
        if value is True:
            argv.append(flag)
        elif isinstance(value, list):
            for item in value:
                argv.extend([flag, str(item)])
        elif isinstance(value, dict):
            argv.extend([flag, json.dumps(value, ensure_ascii=False)])
        else:
            argv.extend([flag, str(value)])
    argv.append("--json")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        argv,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=90,
    )
    if not result.stdout.strip():
        raise RuntimeError(
            f"{tool_id} produced no JSON (exit {result.returncode}): {result.stderr}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{tool_id} produced invalid JSON (exit {result.returncode}): "
            f"{result.stdout[:500]} {result.stderr[:500]}"
        ) from exc


def scrub_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if key in VOLATILE_KEYS and item is not None:
                out[key] = "__VOLATILE__"
            else:
                out[key] = scrub_volatile(item)
        return out
    if isinstance(value, list):
        return [scrub_volatile(item) for item in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.move(str(tmp), path)


def write_doc(rows: list[tuple[str, bool]]) -> None:
    lines = [
        "---",
        'description: "Generated index of MCP response golden snapshots."',
        "read-before-edit: []",
        "edit-after-edit: []",
        "---",
        "# MCP Response Snapshots",
        "",
        f"Generated {date.today().isoformat()} from live CLI. Count: {len(rows)}.",
        "",
        "| Tool | File | is_error |",
        "|---|---|---|",
    ]
    for tool_id, is_error in rows:
        lines.append(f"| {tool_id} | tests/golden/mcp-responses/{tool_id}.json | {str(is_error).lower()} |")
    lines.append("")
    tmp = DOC.with_suffix(".tmp")
    tmp.write_text("\n".join(lines), encoding="utf-8")
    shutil.move(str(tmp), DOC)


if __name__ == "__main__":
    raise SystemExit(main())
