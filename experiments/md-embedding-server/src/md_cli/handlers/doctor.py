from __future__ import annotations

import importlib.metadata
import os
import shutil
import sys
from pathlib import Path

from md_cli import __version__
from md_cli.cost_ledger import cache_root
from md_cli.result import ToolResult


def run(args) -> ToolResult:
    checks = [
        _version_check(),
        _python_check(),
        *_dependency_checks(),
        _cache_check(),
        _path_check(),
        _openrouter_key_check(),
        _skill_path_check("claude", Path.home() / ".claude/skills/1md-navigator"),
        _skill_path_check("codex", Path.home() / ".codex/skills/1md-navigator"),
        _mcp_registration_check(),
    ]
    fail_count = sum(1 for check in checks if check["status"] == "FAIL")
    payload = {"checks": checks, "summary": {"fail": fail_count, "total": len(checks)}}
    if getattr(args, "json", False):
        return ToolResult(payload, 0 if fail_count == 0 else 1)
    lines = ["Check                         Status  Message"]
    for check in checks:
        lines.append(f"{check['name']:<30} {check['status']:<6} {check['message']}")
    return ToolResult({"_human": "\n".join(lines), **payload}, 0 if fail_count == 0 else 1)


def _version_check() -> dict[str, str]:
    return {"name": "md-tools version", "status": "OK", "message": __version__}


def _python_check() -> dict[str, str]:
    ok = sys.version_info >= (3, 11)
    return {"name": "python >=3.11", "status": "OK" if ok else "FAIL", "message": sys.version.split()[0]}


def _dependency_checks() -> list[dict[str, str]]:
    checks = []
    for dep in ["networkx", "numpy", "pymorphy3", "pyyaml", "scipy", "sqlite-vec"]:
        package = "PyYAML" if dep == "pyyaml" else dep
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            checks.append({"name": f"dep {dep}", "status": "FAIL", "message": "missing"})
        else:
            checks.append({"name": f"dep {dep}", "status": "OK", "message": version})
    return checks


def _cache_check() -> dict[str, str]:
    root = cache_root()
    try:
        root.mkdir(parents=True, exist_ok=True)
        test = root / ".write-test"
        test.write_text("ok", encoding="utf-8")
        test.unlink()
    except OSError as exc:
        return {"name": "cache writable", "status": "FAIL", "message": str(exc)}
    return {"name": "cache writable", "status": "OK", "message": str(root)}


def _path_check() -> dict[str, str]:
    found = shutil.which("md")
    return {"name": "md on PATH", "status": "OK" if found else "FAIL", "message": found or "not found"}


def _openrouter_key_check() -> dict[str, str]:
    if os.environ.get("OPENROUTER_API_KEY"):
        return {"name": "OpenRouter key", "status": "OK", "message": "env"}
    candidates = [Path.cwd() / ".openrouter.key", Path.home() / ".openrouter.key"]
    found = next((path for path in candidates if path.exists()), None)
    return {"name": "OpenRouter key", "status": "OK" if found else "WARN", "message": str(found) if found else "not found"}


def _skill_path_check(label: str, path: Path) -> dict[str, str]:
    return {"name": f"{label} skill path", "status": "OK" if path.exists() else "WARN", "message": str(path)}


def _mcp_registration_check() -> dict[str, str]:
    config = Path.home() / ".codex/config.toml"
    try:
        text = config.read_text(encoding="utf-8")
    except OSError:
        return {"name": "legacy md-mcp registration", "status": "OK", "message": "not found"}
    if "[mcp_servers.md-mcp]" in text:
        return {"name": "legacy md-mcp registration", "status": "WARN", "message": str(config)}
    return {"name": "legacy md-mcp registration", "status": "OK", "message": "not configured"}
