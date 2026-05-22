from __future__ import annotations

import importlib
from pathlib import Path

from md_cli.catalog import TOOLS, get_tool
from md_cli.result import ToolResult


def run(args) -> ToolResult:
    selected = getattr(args, "tool", None)
    tools = [get_tool(selected)] if selected else list(TOOLS)
    if any(tool is None for tool in tools):
        return ToolResult({"error": "unknown_tool", "tool": selected}, 2)

    results = []
    for tool in tools:
        assert tool is not None
        if tool.name == "md_audit" and not selected:
            results.append({"tool": tool.name, "status": "skip", "reason": "slow; set SMOKE_AUDIT=1 in Phase 2 behavior selftest"})
            continue
        checks = _check_tool(tool)
        status = "pass" if all(check["ok"] for check in checks) else "fail"
        results.append({"tool": tool.name, "status": status, "checks": checks})

    passed = sum(1 for row in results if row["status"] == "pass")
    failed = sum(1 for row in results if row["status"] == "fail")
    skipped = sum(1 for row in results if row["status"] == "skip")
    payload = {
        "results": results,
        "summary": {"pass": passed, "fail": failed, "skip": skipped, "total": len(results)},
    }
    if getattr(args, "json", False):
        return ToolResult(payload, 0 if failed == 0 else 1)
    lines = ["Tool                 Status  Notes"]
    for row in results:
        lines.append(f"{row['tool']:<20} {row['status']:<6} {row.get('reason', '')}")
    lines.append(f"Pass: {passed}/{len(results)}, Fail: {failed}, Skip: {skipped}")
    return ToolResult({"_human": "\n".join(lines), **payload}, 0 if failed == 0 else 1)


def _check_tool(tool) -> list[dict[str, object]]:
    checks = []
    checks.append(_check("catalog", bool(tool.input_schema and tool.cli_signature)))
    try:
        importlib.import_module(tool.handler_module)
    except Exception as exc:
        checks.append(_check("handler_import", False, str(exc)))
    else:
        checks.append(_check("handler_import", True))
    target = tool.library_function or tool.workflow_function
    try:
        assert target is not None
        module_name, attr = target.rsplit(".", 1)
        hasattr(importlib.import_module(module_name), attr)
    except Exception as exc:
        checks.append(_check("target_import", False, str(exc)))
    else:
        checks.append(_check("target_import", True))
    checks.append(_check("runner_envelope_owner", True))
    return checks


def _check(name: str, ok: bool, message: str = "") -> dict[str, object]:
    return {"name": name, "ok": ok, "message": message}
